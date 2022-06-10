import logging
from pathlib import Path

from retro_data_structures.asset_manager import FileProvider

from open_prime_rando.echoes import custom_assets
from open_prime_rando.echoes.dock_lock_rando import apply_door_rando
from open_prime_rando.echoes.small_randomizations import apply_small_randomizations
from open_prime_rando.echoes.specific_area_patches import specific_patches
from open_prime_rando.patcher_editor import PatcherEditor

LOG = logging.getLogger("echoes_patcher")


def patch_paks(file_provider: FileProvider, output_path: Path, configuration: dict):
    LOG.info("Will patch files at %s", file_provider)

    editor = PatcherEditor(file_provider)

    # custom_assets.create_custom_assets(editor)
    # specific_patches(editor)
    apply_small_randomizations(editor, configuration["small_randomizations"])
    # apply_door_rando(editor, [])

    # Save our changes
    editor.flush_modified_assets()

    editor.save_modifications(output_path)
    LOG.info("Finished.")
