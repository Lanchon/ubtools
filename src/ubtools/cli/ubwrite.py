__all__ = ["main"]

import argparse
import sys

from typing import Sequence

import ubtools

from .utils import *


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="ubwrite",
        description="Write to U-Boot memory via the serial console",
        add_help=False
    )

    parser.add_argument("-q", "--quiet", action="store_true",
                        help="do not show progress")
    parser.add_argument("-w", "--word", metavar="BITS", type=int, choices=[8, 16, 32, 64],
                        help="use writes of specified bit width")

    parser.add_argument("file", metavar="FILE",
                        help="input file (use '-' for stdin)")
    parser.add_argument("address", metavar="ADDRESS", type=nonnegative_int,
                        help="memory address (decimal or hex)")

    add_parser_args(parser)
    args = parser.parse_args(argv)
    config = create_config_for_ubtools(args)

    if args.file == "-":
        data = sys.stdin.buffer.read()
    else:
        with open(args.file, "rb") as file:
            data = file.read()

    progress_file = sys.stderr if not args.quiet else None

    with ubtools.UBoot(config) as uboot:
        uboot.write(data, args.address, bit_width=args.word, progress_file=progress_file)


if __name__ == "__main__":
    sys.exit(main())

