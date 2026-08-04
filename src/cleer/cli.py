__all__ = []


import argparse
import importlib
import json
import os
import sys
from typing import List

from loguru import logger

from cleer import __version__ as cleer_version
from cleer.cleer import Cleer
from cleer.default import cleer_default_config


class FMT:
   purple = "\033[95m"
   cyan = "\033[96m"
   dark_cyan = "\033[36m"
   blue = "\033[94m"
   green = "\033[92m"
   yellow = "\033[93m"
   red = "\033[91m"
   bold = "\033[1m"
   underline = "\033[4m"
   end = "\033[0m"


def main(argv: List[str]=None) -> None:
    parser = argparse.ArgumentParser(
        prog="cleer",
        description="Inspect and format files with cleer!"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=cleer_version
    )
    sub_parsers = parser.add_subparsers(
        title="commands",
        dest="command"
    )

    command_args_parser = argparse.ArgumentParser(add_help=False)
    command_args_parser.add_argument(
        "-c",
        "--cleer",
        type=str,
        default=None,
        help=(
            f"{FMT.bold}[default: \"{FMT.end}{FMT.green}clr:clr{FMT.end}{FMT.bold}\"]{FMT.end} Cleer class instance to use as configuration. "
            "The default behavior is to look in the current dir for a clr.py file for a var named clr. "
            "If that doesn't exist then a default instance will be generated."
        )
    )
    command_args_parser.add_argument(
        "-l",
        "--log-level",
        type=str,
        default="ERROR",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=f"{FMT.bold}[default: \"{FMT.end}{FMT.green}CRITICAL{FMT.end}{FMT.bold}\"]{FMT.end} Set logging level."
    )
    command_args_parser.add_argument(
        "path",
        help="Path to file or directory."
    )

    inspect_parser = sub_parsers.add_parser(
        "inspect",
        help="Inspect a file or directory for formatting violations.",
        description="Inspect a file or directory for formatting violations.",
        parents=[command_args_parser]
    )
    format_parser = sub_parsers.add_parser(
        "format",
        help="Format a file or directory.",
        description="Format a file or directory.",
        parents=[command_args_parser]
    )

    if argv is None and len(sys.argv) < 2:
        logger.debug("No command detected, running help.")
        argv = ["--help"]

    args = parser.parse_args(argv)

    logger.enable("cleer")
    logger.remove()
    logger.add(sys.stderr, level=args.log_level)
    logger.info("Running cleer CLI. Logger configured.")

    clr_path: str | None = args.cleer
    logger.debug(f"Cleer instance path from args: {clr_path}")
    if clr_path is None:
        logger.debug("Setting Cleer instance path to default: 'clr:clr'.")
        clr_path = "clr:clr"

    sys.path.insert(0, os.getcwd())
    try:
        module_name, module_attr = clr_path.split(":")
        module = importlib.import_module(module_name)
        clr = getattr(module, module_attr)
        logger.info(f"Imported Cleer instance from '{clr_path}'.")
    except Exception as exc:
        if args.cleer is not None:
            logger.critical(f"Could not import Cleer instance from custom path: '{clr_path}'. [{type(exc).__name__}]: {exc}")
            exit(1)

        if isinstance(exc, ModuleNotFoundError) is True:
            logger.debug(
                (
                    f"Cleer instance path was not given, and the default path was not found. "
                    f"[{type(exc).__name__}]: {exc}"
                )
            )
        else:
            logger.critical(
                (
                    f"Found the default module, 'clr.py', "
                    f"but failed to import the Cleer instance from it. "
                    f"[{type(exc).__name__}]: {exc}"
                )
            )
            exit(1)

        clr = Cleer(cleer_default_config())
        logger.info("Default Cleer instance generated.")

    if args.command == "inspect":
        logger.info("Running inspect command...")
        print(
            json.dumps(
                clr.inspect(args.path),
                indent=4,
                default=str
            ),
            flush=True
        )
        logger.info("Inspect command complete!")
    elif args.command == "format":
        logger.info("Running format command...")
        print(
            json.dumps(
                clr.format(args.path),
                indent=4,
                default=str
            )
        )
        logger.info("Format command complete!")

    logger.info("Exiting.")
    exit(0)
