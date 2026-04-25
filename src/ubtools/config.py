__all__ = ["UBootConfig"]

import serial

from dataclasses import dataclass


@dataclass
class UBootConfig:
    port: str = "/dev/ttyUSB0"
    baudrate: int = 115200
    bytesize: int = serial.EIGHTBITS
    parity: str = serial.PARITY_NONE
    stopbits: float = serial.STOPBITS_ONE
    timeout: float = 0.1
    write_timeout: float | None = None
    inter_byte_timeout: float | None = None
    exclusive: bool | None = True

    encoding: str = "latin-1"

    def open_serial(self) -> serial.Serial:
        return serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=self.bytesize,
            parity=self.parity,
            stopbits=self.stopbits,
            timeout=self.timeout,
            write_timeout=self.write_timeout,
            inter_byte_timeout=self.inter_byte_timeout,
            exclusive=self.exclusive
        )

