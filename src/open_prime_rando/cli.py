import argparse
import importlib
import logging
import logging.config
import sys

_game_to_patcher = {
    "echoes": "open_prime_rando.echoes.cli",
}


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("game", choices=sorted(_game_to_patcher.keys()))
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


def main():
    setup_logging()
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:2])

    patcher_module = importlib.import_module(_game_to_patcher[args.game])
    patcher_module.main(sys.argv[2:])
