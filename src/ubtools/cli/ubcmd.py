__all__ = ["main"]

import argparse
import sys

from typing import Sequence

import ubtools

from .utils import *


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ubcmd",
        description="Send a command to U-Boot via the serial console and print the output",
        add_help=False
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-n", "--no-reply", action="store_true",
                        help="do not retrieve output nor exit code")
    group.add_argument("-q", "--quiet", action="store_true",
                        help="do not show non-zero exit code")

    parser.add_argument("command", metavar="COMMAND",
                        help="command to send")
    parser.add_argument("args", nargs=argparse.REMAINDER, metavar="ARGS",
                        help="arguments")

    add_parser_args(parser)
    args = parser.parse_args(argv)
    config = create_config_for_ubtools(args)

    cmd_list = [args.command] + args.args
    cmd = " ".join(cmd_list)

    code = 0
    with ubtools.UBoot(config) as uboot:
        uboot.send_command(cmd)
        if not args.no_reply:
            for line in uboot.stream_output():
                print(line)
            code = uboot.get_exit_code()
            if not args.quiet and code != 0:
                print(f"Exit code: {code}", file=sys.stderr)

    return code


if __name__ == "__main__":
    sys.exit(main())

