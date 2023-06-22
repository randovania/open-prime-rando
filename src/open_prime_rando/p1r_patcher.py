import json
import logging
from pathlib import Path

from retro_data_structures.asset_manager import FileProvider
from retro_data_structures.game_check import Game

from open_prime_rando.patcher_editor import PatcherEditor
from open_prime_rando.validator_with_default import DefaultValidatingDraft7Validator

LOG = logging.getLogger("p1r_patcher")


def _read_schema():
    with Path(__file__).parent.joinpath("prime_remastered", "schema.json").open() as f:
        return json.load(f)


def patch_paks(file_provider: FileProvider, output_path: Path, configuration: dict):
    LOG.info("Will patch files at %s", file_provider)
    editor = PatcherEditor(file_provider, Game.PRIME_REMASTER)

    LOG.info("Validating schema")
    DefaultValidatingDraft7Validator(_read_schema()).validate(configuration)

    # Save our changes
    editor.flush_modified_assets()

    editor.save_modifications(output_path)
    LOG.info("Finished.")
