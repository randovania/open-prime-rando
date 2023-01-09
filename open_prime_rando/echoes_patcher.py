import json
import logging
from pathlib import Path

from retro_data_structures.asset_manager import FileProvider

from open_prime_rando import dynamic_schema
from open_prime_rando.echoes.inverted import apply_inverted
from open_prime_rando.echoes.small_randomizations import apply_small_randomizations
from open_prime_rando.patcher_editor import PatcherEditor
from open_prime_rando.validator_with_default import DefaultValidatingDraft7Validator
import open_prime_rando.echoes.asset_ids.world

LOG = logging.getLogger("echoes_patcher")


def _read_schema():
    with Path(__file__).parent.joinpath("echoes", "schema.json").open() as f:
        return json.load(f)


def apply_area_modifications(editor: PatcherEditor, configuration: dict[str, dict]):
    for world_name, world_config in configuration.items():
        mlvl = editor.get_mlvl(open_prime_rando.echoes.asset_ids.world.NAME_TO_ID[world_name])

        for area in mlvl.areas:
            area_name = area.name
            if area_name not in world_config["areas"]:
                continue

            area_config = world_config["areas"][area_name]
            for layer_name, layer_state in area_config["layers"].items():
                LOG.debug("Setting layer %s of %s - %s to %s", layer_name, world_name, area_name, str(layer_state))
                area.get_layer(layer_name).active = layer_state


def patch_paks(file_provider: FileProvider, output_path: Path, configuration: dict):
    LOG.info("Will patch files at %s", file_provider)

    editor = PatcherEditor(file_provider)

    LOG.info("Preparing schema")
    schema = dynamic_schema.expand_schema(_read_schema(), editor)

    LOG.info("Validating schema")
    DefaultValidatingDraft7Validator(schema).validate(configuration)

    # custom_assets.create_custom_assets(editor)
    # specific_patches(editor)
    apply_area_modifications(editor, configuration["worlds"])
    apply_small_randomizations(editor, configuration["small_randomizations"])
    # apply_door_rando(editor, [])

    if configuration["inverted"]:
        apply_inverted(editor)

    # Save our changes
    editor.flush_modified_assets()

    editor.save_modifications(output_path)
    LOG.info("Finished.")
