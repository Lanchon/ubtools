__all__ = ["main"]

import argparse
import os
import sys

from typing import Sequence

import ubtools

from .utils import *


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="ubread",
        description="Read from U-Boot memory via the serial console",
        add_help=False
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

    add_parser_args(parser)
    args = parser.parse_args(argv)
    config = create_config_for_ubtools(args)

    do_read(config, args.file, args.address, args.length, quiet=args.quiet, bit_width=args.word)

def do_read(config: ubtools.UBootConfig, file: str | os.PathLike[str], address: int, length: int,
            quiet: bool = False, bit_width: int | None = None) -> None:
    progress_file = None if quiet else sys.stderr
    with ubtools.UBoot(config) as uboot:
        data = uboot.read(address, length, bit_width=bit_width, progress_file=progress_file)
    if file == "-":
        sys.stdout.buffer.write(data)
    else:
        with open(file, "wb") as f:
            f.write(data)


if __name__ == "__main__":
    sys.exit(main())

