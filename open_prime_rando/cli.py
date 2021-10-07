import argparse
import logging
import logging.config
from pathlib import Path

from open_prime_rando import echoes_patcher


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", required=True, choices=["echoes"])
    parser.add_argument("--input-paks", required=True, type=Path,
                        help="Path to where the paks to randomizer can be found.")
    parser.add_argument("--output-paks", required=True, type=Path,
                        help="Path to where the modified paks will be written to.")
    parser.add_argument("--input-json", type=Path,
                        help="Path to the configuration json. If missing, it's read from standard input")
    return parser


def setup_logging():
    handlers = {
        'default': {
            'level': 'DEBUG',
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
    }
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] [%(levelname)s] [%(name)s] %(funcName)s: %(message)s',
            }
        },
        'handlers': handlers,
        'disable_existing_loggers': False,
        'loggers': {
            'default': {
                'level': 'DEBUG',
            },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': list(handlers.keys()),
        },
    })
    logging.info("Hello world.")


def main():
    setup_logging()
    parser = create_parser()
    args = parser.parse_args()
    print(args)

    echoes_patcher.patch_paks(
        args.input_paks,
        args.output_paks,
        {},
    )
