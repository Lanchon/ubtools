__all__ = ["main"]

import argparse
import time
import sys

from typing import Sequence

import ubtools

from .utils import *


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="ubint",
        description="Interrupt U-Boot autoboot via the serial console",
        add_help=False
    )

    # Current implementations of ubtools.UBoot() and  ubtools.UBoot.detect()
    # already send Return and Ctrl-C characters during initial synchronization,
    # making specific options for these characters unnecessary.

    parser.add_argument("-q", "--quiet", action="store_true",
                        help="do not show progress")
    parser.add_argument("-r", "--reset", action="store_true",
                        help="send reset command first")
    parser.add_argument("-s", "--string", metavar="STR",
                        help="interrupt using custom string")

    add_parser_args(parser)
    args = parser.parse_args(argv)
    config = create_config_for_ubtools(args)

    interrupt = b' '
    if args.string is not None:
        interrupt = args.string.encode(config.encoding)

    if args.reset:
        if not args.quiet:
            print("Sending reset command...", file=sys.stderr)
        with ubtools.UBoot(config) as uboot:
            uboot.send_command(b'reset')

    prompt = ubtools.UBoot.detect(config)
    if prompt is None:
        if not args.quiet:
            print("Trying to interrupt U-Boot autoboot...", file=sys.stderr)
        while True:
            with config.open_serial() as serial:
                serial.write(interrupt)
                time.sleep(serial.timeout)
            prompt = ubtools.UBoot.detect(config)
            if prompt is not None:
                break
    prompt = prompt.strip()

    if not args.quiet:
        print(f"Prompt: {prompt}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())

