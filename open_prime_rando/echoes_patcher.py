import json
import logging
from pathlib import Path

from retro_data_structures.asset_manager import FileProvider
from retro_data_structures.formats.mlvl import AreaWrapper
from retro_data_structures.game_check import Game

from open_prime_rando import dynamic_schema
from open_prime_rando.echoes import specific_area_patches, asset_ids
from open_prime_rando.echoes.inverted import apply_inverted
from open_prime_rando.echoes.small_randomizations import apply_small_randomizations
from open_prime_rando.patcher_editor import PatcherEditor
from open_prime_rando.validator_with_default import DefaultValidatingDraft7Validator
from retro_data_structures.properties.shared_objects import Dock

LOG = logging.getLogger("echoes_patcher")


def _read_schema():
    with Path(__file__).parent.joinpath("echoes", "schema.json").open() as f:
        return json.load(f)


def apply_area_modifications(editor: PatcherEditor, configuration: dict[str, dict]):
    for world_name, world_config in configuration.items():
        world_meta = asset_ids.world.load_dedicated_file(world_name)
        mlvl = editor.get_mlvl(asset_ids.world.NAME_TO_ID[world_name])

        areas_by_name: dict[str, AreaWrapper] = {
            area.name: area
            for area in mlvl.areas
        }

        for area_name, area in areas_by_name.items():
            if area_name not in world_config["areas"]:
                continue

            area_config = world_config["areas"][area_name]

            for dock_name, dock_config in area_config["docks"].items():
                dock_number = world_meta.DOCK_NAMES[area_name][dock_name]
                if "connect_to" in dock_config:
                    dock_target = dock_config["connect_to"]
                    LOG.debug("Connecting dock %s of %s - %s to %s - %s",
                              dock_name, world_name, area_name, dock_target["area"], dock_target["dock"])
                    area.connect_dock_to(dock_number, areas_by_name[dock_target["area"]],
                                         world_meta.DOCK_NAMES[dock_target["area"]][dock_target["dock"]])

            for layer_name, layer_state in area_config["layers"].items():
                LOG.debug("Setting layer %s of %s - %s to %s", layer_name, world_name, area_name, str(layer_state))
                area.get_layer(layer_name).active = layer_state


def patch_paks(file_provider: FileProvider, output_path: Path, configuration: dict):
    LOG.info("Will patch files at %s", file_provider)

    editor = PatcherEditor(file_provider, Game.ECHOES)

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
