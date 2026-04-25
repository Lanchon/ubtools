__all__ = ["main"]

import argparse
import sys

from typing import Sequence

import ubtools


def nonnegative_int(arg: str) -> int:
	try:
		value = int(arg, 0)
	except ValueError:
		raise argparse.ArgumentTypeError(f"invalid integer value: {arg}")
	if value < 0:
		raise argparse.ArgumentTypeError(f"value cannot be negative: {arg}")
	return value

def main(argv: Sequence[str] | None = None) -> None:
	parser = argparse.ArgumentParser(
		prog="ubread",
		description="Read from U-Boot memory via the serial console"
	)

	parser.add_argument("-q", "--quiet", action="store_true",
	                    help="do not show progress")
	parser.add_argument("-w", "--word", metavar="BITS", type=int, choices=[8, 16, 32, 64],
	                    help="use reads of specified bit width")

	parser.add_argument("file", metavar="FILE",
	                    help="Output file (use '-' for stdout)")
	parser.add_argument("address", metavar="ADDRESS", type=nonnegative_int,
	                    help="memory address (decimal or hex)")
	parser.add_argument("length", metavar="LENGTH", type=nonnegative_int,
	                    help="number of bytes (decimal or hex)")

	ubtools.UBootConfig.add_parser_arguments(parser)
	args = parser.parse_args(argv)
	config = ubtools.UBootConfig.from_parser_namespace(args)

	progress_file = sys.stderr if not args.quiet else None

	with ubtools.UBoot(config) as uboot:
		data = uboot.read(args.address, args.length, bit_width=args.word, progress_file=progress_file)

	if args.file == "-":
		sys.stdout.buffer.write(data)
	else:
		with open(args.file, "wb") as file:
			file.write(data)


if __name__ == "__main__":
	sys.exit(main())

