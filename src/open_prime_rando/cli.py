import argparse
import importlib
import json
import logging
import logging.config
from pathlib import Path

from retro_data_structures.asset_manager import IsoFileProvider, PathFileProvider

_game_to_patcher = {
    "echoes": "open_prime_rando.echoes_patcher",
    "prime_remastered": "open_prime_rando.p1r_patcher",
}


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", required=True, choices=sorted(_game_to_patcher.keys()))
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--input-paks", type=Path, help="Path to where the paks to randomize")
    input_group.add_argument("--input-iso", type=Path, help="Path to a ISO to randomize")
    parser.add_argument(
        "--output-paks", required=True, type=Path, help="Path to where the modified paks will be written to."
    )
    parser.add_argument("--input-json", type=Path, required=True, help="Path to the configuration json.")
    return parser


def setup_logging():
    handlers = {
        "default": {
            "level": "DEBUG",
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    }
    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] [%(levelname)s] [%(name)s] %(funcName)s: %(message)s",
                }
            },
            "handlers": handlers,
            "disable_existing_loggers": False,
            "loggers": {
                "default": {
                    "level": "DEBUG",
                },
            },
            "root": {
                "level": "DEBUG",
                "handlers": list(handlers.keys()),
            },
        }
    )
    logging.info("Hello world.")


def main():
    setup_logging()
    parser = create_parser()
    args = parser.parse_args()
    print(args)

    with args.input_json.open() as f:
        configuration = json.load(f)

    if args.input_paks is not None:
        file_provider = PathFileProvider(args.input_paks)
    else:
        file_provider = IsoFileProvider(args.input_iso)

    patcher_module = importlib.import_module(_game_to_patcher[args.game])
    patcher_module.patch_paks(
        file_provider,
        args.output_paks,
        configuration,
    )
