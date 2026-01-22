import argparse
from pathlib import Path

from open_prime_rando.echoes import patcher
from open_prime_rando.echoes.rando_configuration import RandoConfiguration


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-iso", required=True, type=Path, help="Path to a ISO to randomize")
    parser.add_argument("--output-iso", required=True, type=Path, help="Path to write the modified ISO.")

    subparser = parser.add_subparsers(dest="command")
    rando = subparser.add_parser("randomizer")
    rando.add_argument("--input-json", type=Path, required=True, help="Path to the configuration json.")
    return parser


def main(argv: list[str]) -> None:
    parser = create_parser()
    args = parser.parse_args(argv)

    print(args)

    if args.command == "randomizer":
        configuration_path: Path = args.input_json
        configuration = RandoConfiguration.model_validate_json(
            configuration_path.read_text(),
            strict=True,
        )

        patcher.patch_iso(
            args.input_iso,
            args.output_iso,
            configuration,
        )
    else:
        parser.print_help()
        raise SystemExit(1)
