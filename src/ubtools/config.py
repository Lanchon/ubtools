__all__ = ["UBootConfig"]

import serial

from dataclasses import dataclass
from typing import Self


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

	@staticmethod
	def add_parser_arguments(parser) -> None:
		parser.add_argument("-p", "--port",
		                    help="serial port device")
		parser.add_argument("-b", "--baud", type=int,
		                    help="baud rate")
		parser.add_argument("--timeout", metavar="SECONDS", type=float,
		                    help="timeout for read operations")
		parser.add_argument("--shared", action="store_true",
		                    help="open serial port in shared mode")

	@classmethod
	def from_parser_namespace(cls, args) -> Self:
		config = cls()
		if args.port is not None:
			config.port = args.port
		if args.baud is not None:
			config.baudrate = args.baud
		if args.timeout is not None:
			config.timeout = args.timeout
		if args.shared:
			config.exclusive = False
		return config

