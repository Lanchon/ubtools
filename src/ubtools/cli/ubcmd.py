__all__ = ["main"]

import argparse
import sys

from typing import Sequence

import ubtools


def main(argv: Sequence[str] | None = None) -> int:
	parser = argparse.ArgumentParser(
		prog="ubcmd",
		description="Send a command to U-Boot via the serial console and print the output"
	)

	parser.add_argument("-q", "--quiet", action="store_true",
	                    help="do not show exit code")

	parser.add_argument("command", metavar="COMMAND",
	                    help="command to send"
	                    )
	parser.add_argument("args", nargs=argparse.REMAINDER, metavar="ARGS",
	                    help="arguments"
	                    )

	ubtools.UBootConfig.add_parser_arguments(parser)
	args = parser.parse_args(argv)
	config = ubtools.UBootConfig.from_parser_namespace(args)

	cmd_list = [args.command] + args.args
	cmd = " ".join(cmd_list)

	with ubtools.UBoot(config) as uboot:
		uboot.send_command(cmd)
		for line in uboot.stream_output():
			print(line)
		code = uboot.get_exit_code()
		if not args.quiet and code != 0:
			print(f"Exit code: {code}", file=sys.stderr)
		return code


if __name__ == "__main__":
	sys.exit(main())

