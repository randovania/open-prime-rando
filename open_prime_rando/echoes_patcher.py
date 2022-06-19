import json
import logging
from pathlib import Path

from retro_data_structures.asset_manager import FileProvider

from open_prime_rando.echoes.inverted import apply_inverted
from open_prime_rando.echoes.small_randomizations import apply_small_randomizations
from open_prime_rando.patcher_editor import PatcherEditor
from open_prime_rando.validator_with_default import DefaultValidatingDraft7Validator

LOG = logging.getLogger("echoes_patcher")


def _read_schema():
    with Path(__file__).parent.joinpath("echoes", "schema.json").open() as f:
        return json.load(f)


def patch_paks(file_provider: FileProvider, output_path: Path, configuration: dict):
    LOG.info("Will patch files at %s", file_provider)

    DefaultValidatingDraft7Validator(_read_schema()).validate(configuration)

    editor = PatcherEditor(file_provider)

    # custom_assets.create_custom_assets(editor)
    # specific_patches(editor)
    apply_small_randomizations(editor, configuration["small_randomizations"])
    # apply_door_rando(editor, [])

    if configuration["inverted"]:
        apply_inverted(editor)

    # Save our changes
    editor.flush_modified_assets()

    editor.save_modifications(output_path)
    LOG.info("Finished.")
