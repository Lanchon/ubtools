__all__ = ["main"]

import argparse
import time
import sys

from typing import Sequence

import ubtools


def main(argv: Sequence[str] | None = None) -> None:
	parser = argparse.ArgumentParser(
		prog="ubint",
		description="Interrupt U-Boot autoboot via the serial console"
	)

	# Current implementations of ubdriver.UBoot() and  ubdriver.UBoot.detect()
	# already send Return and Ctrl-C characters during inital synchronization,
	# making specific options for these characters unnecessary.

	parser.add_argument("-s", "--string", metavar="XXX",
	                    help="interrupt using custom string")

	ubtools.UBootConfig.add_parser_arguments(parser)
	args = parser.parse_args(argv)
	config = ubtools.UBootConfig.from_parser_namespace(args)

	cmd = args.string.encode(config.encoding) if args.string is not None else b' '

	if not ubtools.UBoot.detect(config):
		print("Trying to interrupt U-Boot autoboot...")
		while True:
			with config.open_serial() as serial:
				serial.write(cmd)
				time.sleep(serial.timeout)
			if ubtools.UBoot.detect(config):
				break

	print("U-Boot is ready")


if __name__ == "__main__":
	sys.exit(main())

