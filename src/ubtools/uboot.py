__all__ = ["UBoot"]

import re
import serial
import struct

from typing import Callable, Iterator, Self

from .config import *
from .errors import *
from .types import *


class UBoot:
    @classmethod
    def detect(cls, config: UBootConfig | None = None) -> str | None:
        try:
            with cls(config) as uboot:
                return uboot.prompt.decode(uboot.encoding)
        except UBootCommunicationError:
            return None

    serial: serial.Serial
    encoding: str
    prompt: bytes

    # Initialization

    def __init__(self, config: UBootConfig | None = None) -> None:
        # WARNING: Ctrl-C is sent during initialization, which clears the previous exit code.
        if config is None:
            config = UBootConfig()
        self.serial = config.open_serial()
        self.encoding = config.encoding
        try:
            # Send Ctrl-C to purge command line buffer.
            self.serial.write(b'\x03')
            while self.serial.readline():
                pass

            # Establish sync.
            cmd = b'#TAG1'
            self.serial.write(cmd + b'\n')
            echo = self.serial.readline().strip(b'\r\n')
            if echo != cmd:
                raise UBootCommunicationError(f"Failed to establish sync (sent: {cmd!r}, received: {echo!r})")

            # Detect prompt.
            cmd = b'#TAG2'
            self.serial.write(cmd + b'\n')
            echo = self.serial.readline().strip(b'\r\n')
            if not echo.endswith(cmd):
                raise UBootCommunicationError(f"Failed to detect prompt (sent: {cmd!r}, received: {echo!r})")
            self.prompt = echo[:-len(cmd)]

            # Verify prompt detection.
            self.send_command(b'#TAG3')

            # Verify prompt content.
            ep = config.expected_prompt
            if ep is not None:
                ep = ep.encode(self.encoding).strip()
                rp = self.prompt.strip()
                if ep != rp:
                    ep = ep.decode(self.encoding)
                    rp = rp.decode(self.encoding)
                    raise UBootUnexpectedPromptError(f"Unexpected prompt (expected: {ep!r}, received: {rp!r})",
                                                     prompt=rp)
            else:
                if not self.prompt:
                    raise UBootUnexpectedPromptError("Empty prompt rejected (specify explicitly if expected)",
                                                     prompt="")
        except Exception:
            try:
                self.serial.close()
            except Exception:
                pass
            raise

    def close(self) -> None:
        self.serial.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> bool:
        self.close()
        return False

    # Command Execution

    def execute_command(self, cmd: str, restore: bool = False, expected_line_count: int | None = None) -> list[str]:
        out, code = self.execute_command_unchecked(cmd, restore=restore)
        if code != 0:
            raise UBootCommandExitCodeError(command=cmd, output=out, exit_code=code)
        if expected_line_count is not None and expected_line_count != len(out):
            raise UBootCommandOutputError(f"Unexpected command output line count "
                                          f"(expected: {expected_line_count}, received: {len(out)})",
                                          command=cmd, output=out, exit_code=code)
        return out

    def execute_command_unchecked(self, cmd: str, restore: bool = False) -> tuple[list[str], int]:
        self.send_command(cmd)
        out = self.receive_output()
        code = self.get_exit_code(restore=restore)
        return out, code

    def send_command(self, cmd: Buffer | str) -> None:
        # WARNING: after calling send_command() and before calling get_exit_code() or sending another command,
        # one of the output capture methods must be called if the invoked command does not finish instantaneously.
        if isinstance(cmd, str):
            cmd = cmd.encode(self.encoding)
        self.serial.write(b''.join((cmd, b'\n')))
        echo = self.serial.readline().strip(b'\r\n')
        expected = self.prompt + cmd
        if expected != echo:
            raise UBootCommunicationError(f"Unexpected command echo (expected: {expected!r}, received: {echo!r})")

    def receive_output(self) -> list[str]:
        return list(self.stream_output())

    def stream_output(self) -> Iterator[str]:
        return (line.strip(b'\r\n').decode(self.encoding) for line in self.stream_output_bytes())

    def stream_output_bytes(self) -> Iterator[bytes]:
        # Stream output until it stops at a prompt.
        while True:
            line = b''
            while not line.endswith((b'\n', self.prompt)):
                line += self.serial.readline()
            if line.endswith(self.prompt):
                line = line[:-len(self.prompt)]
                # Some U-Boot builds use "\r\n\r" for line termination.
                if line != b'' and line != b'\r':
                    yield line
                break
            yield line

        # Reestablish sync.
        cmd = b'#EOO_TAG'
        self.serial.write(cmd + b'\n')
        echo = self.serial.readline().strip(b'\r\n')
        if echo != cmd:
            raise UBootCommunicationError(f"Failed to detect end-of-output tag (expected: {cmd!r}, received: {echo!r})")

    def get_exit_code(self, restore: bool = False) -> int:
        # WARNING: reading the exit code necessarily clears it and in general there is no way to restore its value,
        # but at least its zero/non-zero status can be restored with an optional 'false' command.
        self.send_command(b'echo $?')
        code = int(self.serial.readline().strip(b'\r\n'))
        if code != 0 and restore:
            self.send_command(b'false')
        return code

    # Memory Access

    _TransferFn = Callable[[memoryview, int, int, object | None], None]

    def _transfer(self, transfer: _TransferFn, data: memoryview, adr: int, bit_width: int | None,
                  progress_file) -> None:
        if bit_width is not None:
            transfer(data, adr, bit_width, progress_file)
        else:
            self._adaptive_transfer(transfer, data, adr, progress_file)

    def _adaptive_transfer(self, transfer: _TransferFn, data: memoryview, adr: int, progress_file) -> None:
        length = len(data)
        index = 0
        step = 1

        # Do smallest possible alignment transfers as needed, staring with 8-bits and up to 32-bits or first failure.
        while length >= step and step < 8:
            if adr % (2 * step) != 0:
                if self._adaptive_transfer_try(transfer, data[index : index + step], adr, 8 * step, progress_file):
                    adr += step
                    length -= step
                    index += step
                else:
                    break
            step *= 2

        # Do eagerly large transfers as needed, staring with 64-bits if no previous failure or else a size step
        # downwards from the previous failure, and down to 8-bits.
        while step >= 1:
            chunk = length - (length % step)
            if chunk != 0:
                if self._adaptive_transfer_try(transfer, data[index : index + chunk], adr, 8 * step, progress_file):
                    adr += chunk
                    length -= chunk
                    index += chunk
            step //= 2

    def _adaptive_transfer_try(self, transfer: _TransferFn, data: memoryview, adr: int, bit_width: int,
                               progress_file) -> bool:
        try:
            transfer(data, adr, bit_width, progress_file)
            return True
        except UBootCommandExitCodeError:
            if progress_file is not None:
                print(f"{bit_width}-bit memory access to address {hex(adr)} failed", file=progress_file)
            if bit_width == 8:
                raise
            return False

    def _validate_transfer(self, data: memoryview, adr: int, bit_width: int) -> tuple[str, str]:
        match bit_width:
            case 64:
                pack_format = "<Q"
                size_modifier = ".q"
            case 32:
                pack_format = "<I"
                size_modifier = ".l"
            case 16:
                pack_format = "<H"
                size_modifier = ".w"
            case 8:
                pack_format = "<B"
                size_modifier = ".b"
            case _:
                raise ValueError(f"{bit_width}-bit memory access is not supported")

        step = bit_width // 8
        if adr % step != 0:
            raise ValueError(f"Address must be aligned to {bit_width} bits")
        if len(data) % step != 0:
            raise ValueError(f"Data size must be aligned to {bit_width} bits")

        return pack_format, size_modifier

    # Memory Read

    def read(self, adr: int, length: int, bit_width: int | None = None, progress_file=None) -> bytes:
        data = bytearray(length)
        self.read_into(data, adr, bit_width=bit_width, progress_file=progress_file)
        return bytes(data)

    def read_into(self, data: WritableBuffer, adr: int, bit_width: int | None = None, progress_file=None) -> None:
        self._transfer(self._read_raw, memoryview(data), adr, bit_width, progress_file)

    def _read_raw(self, data: memoryview, adr: int, bit_width: int, progress_file=None) -> None:
        pack_format, size_modifier = self._validate_transfer(data, adr, bit_width)
        length = len(data)
        step = bit_width // 8
        if length != 0:
            message = f"Reading {hex(length)} bytes from address {hex(adr)} using {bit_width}-bit reads..."
            cmd = f"md{size_modifier} {adr:x} {length // step:x}"
            index = 0
            first = True
            self.send_command(cmd)
            try:
                for line in self.stream_output():
                    chunk = self._read_md_line(cmd, line, adr + index, pack_format, step)
                    old_index = index
                    index += len(chunk)
                    if index > length:
                        raise UBootCommandOutputError("md: received too many words", command=cmd)
                    data[old_index:index] = chunk
                    first = False
                    if progress_file is not None:
                        percent = (index) * 100 // length
                        print(f"\r{message} {percent:3d}%", end="", flush=True, file=progress_file)
            finally:
                if progress_file is not None and not first:
                    print(file=progress_file)
            code = self.get_exit_code()
            if code != 0:
                raise UBootCommandExitCodeError(command=cmd, exit_code=code)
            if index < length:
                raise UBootCommandOutputError("md: received too few words", command=cmd)

    _MD_LINE_PATTERN = re.compile(r"^([0-9a-fA-F]+):\s*((?:[0-9a-fA-F]+\s)+)(.*$)")

    def _read_md_line(self, cmd: str, line: str, adr: int, pack_format: str, step: int) -> bytearray:
        match = self._MD_LINE_PATTERN.match(line)
        if not match:
            raise UBootCommandOutputError("md: unexpected line format", command=cmd, output=[line])
        try:
            line_adr = int(match.group(1), 16)
            words = list(int(word, 16) for word in match.group(2).split())
        except ValueError as e:
            raise UBootCommandOutputError("md: unexpected line format", command=cmd, output=[line]) from e

        if line_adr != adr:
            raise UBootCommandOutputError("md: unexpected line address", command=cmd, output=[line])

        size = len(words) * step
        chunk = bytearray(size)
        index = 0
        for word in words:
            struct.pack_into(pack_format, chunk, index, word)
            index += step

        chars = match.group(3)[-size:].encode(self.encoding)
        dot = ".".encode(self.encoding)[0]
        if len(chars) != size or any(a != c and a != dot for c, a in zip(chunk, chars)):
            raise UBootCommandOutputError(f"md: mismatch between hex and ascii data",
                                          command=cmd, output=[line])
        return chunk

    # Memory Write

    def write(self, data: Buffer, adr: int, bit_width: int | None = None, progress_file=None) -> None:
        self._transfer(self._write_raw, memoryview(data), adr, bit_width, progress_file)

    def _write_raw(self, data: memoryview, adr: int, bit_width: int, progress_file=None) -> None:
        pack_format, size_modifier = self._validate_transfer(data, adr, bit_width)
        length = len(data)
        step = bit_width // 8
        if length != 0:
            message = f"Writing {hex(length)} bytes to address {hex(adr)} using {bit_width}-bit writes..."
            index = 0
            first = True
            try:
                for (value, ) in struct.iter_unpack(pack_format, data):
                    cmd = f"mw{size_modifier} {adr + index:x} {value:x}"
                    self.send_command(cmd)
                    if first:
                        code = self.get_exit_code()
                        if code != 0:
                            raise UBootCommandExitCodeError(command=cmd, exit_code=code)
                        first = False
                    index += step
                    if progress_file is not None:
                        percent = index * 100 // length
                        print(f"\r{message} {percent:3d}%", end="", flush=True, file=progress_file)
            finally:
                if progress_file is not None and not first:
                    print(file=progress_file)

