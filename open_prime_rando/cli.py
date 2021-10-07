import argparse
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


def main():
    parser = create_parser()
    args = parser.parse_args()
    print(args)

    echoes_patcher.patch_paks(
        args.input_paks,
        args.output_paks,
        {},
    )
