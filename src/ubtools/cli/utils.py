__all__ = [
    "nonnegative_int",
    "add_parser_args",
    "add_config_parser_args",
    "add_version_parser_arg",
    "set_config_from_parser_args",
    "config_from_parser_args",
]

import argparse

from typing import Type, TypeVar

import ubtools


def nonnegative_int(arg: str) -> int:
    try:
        value = int(arg, 0)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid integer value: {arg}")
    if value < 0:
        raise argparse.ArgumentTypeError(f"value cannot be negative: {arg}")
    return value

def add_parser_args(parser) -> None:
    add_config_parser_args(parser)
    add_version_parser_arg(parser)
    #parser.epilog = f"ubtools version: {ubtools.__version__}"

def add_config_parser_args(parser) -> None:
    parser.add_argument("-p", "--port",
                        help="serial port device")
    parser.add_argument("-b", "--baud", type=int,
                        help="baud rate")
    parser.add_argument("--timeout", metavar="SECONDS", type=float,
                        help="timeout for read operations")
    parser.add_argument("--shared", action="store_true",
                        help="open serial port in shared mode")

def add_version_parser_arg(parser) -> None:
    parser.add_argument("-h", "--help", action="help",
                        help="show help message and exit")
    parser.add_argument("--version", action="version", version=ubtools.__version__,
                        help="show version number and exit")

def set_config_from_parser_args(config: ubtools.UBootConfig, args) -> None:
    if args.port is not None:
        config.port = args.port
    if args.baud is not None:
        config.baudrate = args.baud
    if args.timeout is not None:
        config.timeout = args.timeout
    if args.shared:
        config.exclusive = False

ConfigT = TypeVar("ConfigT", bound=ubtools.UBootConfig)

def config_from_parser_args(args, cls: Type[ConfigT] = ubtools.UBootConfig) -> ConfigT:
    config = ubtools.UBootConfig()
    set_config_from_parser_args(config, args)
    return config

