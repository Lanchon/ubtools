__all__ = [
    "nonnegative_int",
    "add_parser_args",
    "add_config_parser_args",
    "add_version_parser_arg",
    "set_config_from_parser_args",
    "set_config_from_env_vars",
    "set_config_from_toml_file",
    "set_config_from_field_getter",
    "parse_locking_mode",
    "create_config",
    "create_config_for_tool",
    "create_config_for_ubtools",
]

import argparse
import os
import platformdirs
import tomllib

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
                        help="serial port baud rate")
    parser.add_argument("--timeout", metavar="SECONDS", type=float,
                        help="serial port receive timeout")
    parser.add_argument("--mode", choices=["shared", "exclusive", "none"],
                        help="serial port locking mode")

def add_version_parser_arg(parser) -> None:
    parser.add_argument("-h", "--help", action="help",
                        help="show help message and exit")
    parser.add_argument("--version", action="version", version=ubtools.__version__,
                        help="show version number and exit")

def set_config_from_parser_args(config: ubtools.UBootConfig, args) -> None:
    set_config_from_field_getter(config, lambda field: getattr(args, field))

def set_config_from_env_vars(config: ubtools.UBootConfig, env_var_prefix: str) -> None:
    set_config_from_field_getter(config, lambda field: os.getenv(f"{env_var_prefix}_{field.upper()}"))

def set_config_from_toml_file(config: ubtools.UBootConfig, toml_file: str | os.PathLike[str],
                              toml_section: str | None) -> None:
    with open(toml_file, "rb") as file:
        data = tomllib.load(file)
    if toml_section is not None:
        data = data.get(toml_section, {})
    set_config_from_field_getter(config, lambda field: data.get(field))

def set_config_from_field_getter(config: ubtools.UBootConfig, get) -> None:
    port = get("port")
    baud = get("baud")
    timeout = get("timeout")
    mode = get("mode")
    if port is not None:
        config.port = str(port)
    if baud is not None:
        config.baudrate = int(baud)
    if timeout is not None:
        config.timeout = float(timeout)
    if mode is not None:
        config.exclusive = parse_locking_mode(mode)

def parse_locking_mode(mode: str) -> bool | None:
    match mode:
        case "shared":
            return False
        case "exclusive":
            return True
        case "none":
            return None
        case _:
            raise ValueError(f"Invalid locking mode: {mode}")

ConfigT = TypeVar("ConfigT", bound=ubtools.UBootConfig)

def create_config(args = None,
                  env_var_prefix: str | None = None,
                  toml_file: str | os.PathLike[str] | None = None, toml_section: str | None = None,
                  cls: Type[ConfigT] = ubtools.UBootConfig) -> ConfigT:
    config = cls()
    if toml_file is not None:
        set_config_from_toml_file(config, toml_file, toml_section)
    if env_var_prefix is not None:
        set_config_from_env_vars(config, env_var_prefix)
    if args is not None:
        set_config_from_parser_args(config, args)
    return config

def create_config_for_tool(tool_name: str,
                           args = None,
                           toml_filename: str | None = "config.toml", toml_section: str | None  = "serial",
                           cls: Type[ConfigT] = ubtools.UBootConfig) -> ConfigT:
    toml_file = None
    if toml_filename is not None:
        file = platformdirs.user_config_path(tool_name) / toml_filename
        if file.exists():
            toml_file = file
    return create_config(args=args,
                         env_var_prefix=tool_name.upper(),
                         toml_file=toml_file, toml_section=toml_section,
                         cls=cls)

def create_config_for_ubtools(args,
                              cls: Type[ConfigT] = ubtools.UBootConfig) -> ConfigT:
    return create_config_for_tool("ubtools", args=args, cls=cls)

