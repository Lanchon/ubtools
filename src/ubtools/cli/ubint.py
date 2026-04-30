__all__ = ["main"]

import argparse
import time
import sys

from typing import Sequence

import ubtools

from .utils import *


def main(argv: Sequence[str] | None = None) -> int:
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
    parser.add_argument("--prompt",
                        help="detected prompt must match this")
    parser.add_argument("-s", "--string", metavar="STR",
                        help="interrupt using custom string")

    add_parser_args(parser)
    args = parser.parse_args(argv)
    config = create_config_for_ubtools(args)

    return do_interrupt(config, quiet=args.quiet, reset=args.reset,
                        expected_prompt=args.prompt, int_string=args.string)

def do_interrupt(config: ubtools.UBootConfig, quiet: bool = False, reset: bool = False,
                 expected_prompt: str | None = None, int_string: str | None = None) -> int:
    if reset:
        if not quiet:
            print("Sending reset command...", file=sys.stderr)
        with ubtools.UBoot(config) as uboot:
            uboot.send_command("reset")

    prompt = ubtools.UBoot.detect(config)
    if prompt is None:
        if not quiet:
            print("Trying to interrupt U-Boot autoboot...", file=sys.stderr)
        if int_string is None:
            int_string = " "
        int_string = int_string.encode(config.encoding)
        while True:
            with config.open_serial() as serial:
                serial.write(int_string)
                time.sleep(serial.timeout)
            prompt = ubtools.UBoot.detect(config)
            if prompt is not None:
                break
    prompt = prompt.strip()

    if expected_prompt is not None and expected_prompt != prompt:
        print(f"Prompt mismatch (expected: {expected_prompt!r}, detected: {prompt!r})", file=sys.stderr)
        return 1

    if not quiet:
        print(f"Prompt: {prompt}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())

