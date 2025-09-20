import json
import logging
import typing
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

from retro_data_structures.asset_manager import FileProvider, PathFileWriter
from retro_data_structures.formats.strg import Strg
from retro_data_structures.game_check import Game

from open_prime_rando.echoes import (
    asset_ids,
    dock_lock_rando,
    legacy_dynamic_schema,
)
from open_prime_rando.echoes.elevators.elevator_rando import patch_elevator
from open_prime_rando.echoes.general_changes import apply_corrupted_memory_card_change
from open_prime_rando.echoes.small_randomizations import apply_small_randomizations
from open_prime_rando.echoes.specific_area_patches import required_fixes
from open_prime_rando.echoes.suit_cosmetics import apply_custom_suits
from open_prime_rando.patcher_editor import PatcherEditor
from open_prime_rando.validator_with_default import DefaultValidatingDraft7Validator

if TYPE_CHECKING:
    from retro_data_structures.formats.mrea import Area

LOG = logging.getLogger("echoes_patcher")


def _read_legacy_schema():
    with Path(__file__).parent.joinpath("legacy_schema.json").open() as f:
        return json.load(f)


def apply_area_modifications(
    editor: PatcherEditor, configuration: dict[str, dict], status_update: Callable[[str, float], None]
):
    num_areas = sum(len(world_config["areas"]) for world_config in configuration.values())
    areas_processed = 0.0

    for world_name, world_config in configuration.items():
        world_meta = asset_ids.world.load_dedicated_file(world_name)
        mlvl = editor.get_mlvl(asset_ids.world.NAME_TO_ID_MLVL[world_name])

        mrea_to_name: dict[int, str] = {mrea: name for name, mrea in world_meta.NAME_TO_ID_MREA.items()}

        areas_by_name: dict[str, Area] = {mrea_to_name[area.mrea_asset_id]: area for area in mlvl.areas}

        for i, (area_name, area) in enumerate(areas_by_name.items()):
            if area_name not in world_config["areas"]:
                continue

            status_update(f"Processing {world_name} - {area_name}...", areas_processed / num_areas)
            areas_processed += 1

            area_config = world_config["areas"][area_name]
            low_memory = area_config["low_memory_mode"]

            for dock_name, dock_config in area_config["docks"].items():
                if "new_door_type" in dock_config:
                    dock_lock_rando.apply_door_rando(
                        editor,
                        world_name,
                        area_name,
                        dock_name,
                        dock_config["new_door_type"],
                        dock_config.get("old_door_type"),
                        low_memory,
                    )

            for layer_name, layer_state in area_config["layers"].items():
                LOG.debug("Setting layer %s of %s - %s to %s", layer_name, world_name, area_name, str(layer_state))
                area.get_layer(layer_name).active = layer_state

            for elevator in area_config["elevators"]:
                patch_elevator(
                    editor,
                    area,
                    elevator["instance_id"],
                    elevator["target_assets"]["world_asset_id"],
                    elevator["target_assets"]["area_asset_id"],
                    elevator["target_strg"],
                    elevator["target_name"],
                )

            if area_config["new_name"] is not None:
                old_strg = area._raw.area_name_id
                new_strg_id = editor.duplicate_asset(old_strg, f"custom_name_for_{area.internal_name}.STRG")
                strg = editor.get_file(new_strg_id, Strg)
                strg.set_single_string(0, area_config["new_name"])
                area._raw.area_name_id = new_strg_id

            area.update_all_dependencies(only_modified=True)


def apply_tweak_edits(editor: PatcherEditor, tweak_edits: dict[str, dict[str, typing.Any]]) -> None:
    """
    Edits the tweaks based on the generic schema api
    :param editor:
    :param tweak_edits:
    :return:
    """
    for instance in editor.tweaks.instances:
        properties = instance.get_properties().to_json()
        if properties["instance_name"] in tweak_edits:
            logging.debug("Editing %s", properties["instance_name"])

            for name, value in tweak_edits[properties["instance_name"]].items():
                parent = properties
                spit_name = name.split(".")

                for part in spit_name[:-1]:
                    parent = parent[part]

                parent[spit_name[-1]] = value

            instance.set_properties(instance.type.from_json(properties))


def patch_paks(
    file_provider: FileProvider,
    output_path: Path,
    configuration: dict,
    status_update: Callable[[str, float], None] = lambda s, _: LOG.info(s),
):
    """Applies the legacy patches, intended to be used alongside Claris' patcher."""
    status_update(f"Will patch files at {file_provider}", 0)
    output_path.joinpath("files").mkdir(parents=True, exist_ok=True)
    output_path.joinpath("files", "opr_patcher_data.json").write_text(json.dumps(configuration))

    editor = PatcherEditor(file_provider, Game.ECHOES)

    status_update("Preparing schema", 0)
    schema = legacy_dynamic_schema.expand_schema(_read_legacy_schema(), editor)

    status_update("Validating schema", 0)
    DefaultValidatingDraft7Validator(schema).validate(configuration)

    status_update("Applying small patches", 0)
    dock_lock_rando.add_custom_models(editor)
    required_fixes.torvus_temple(editor)
    required_fixes.command_center_door(editor)
    apply_small_randomizations(editor, configuration["small_randomizations"])
    apply_corrupted_memory_card_change(editor)

    if "tweaks" in configuration:
        status_update("Modifying tweaks", 0)
        apply_tweak_edits(editor, configuration["tweaks"])

    status_update("Modifying areas", 0)
    apply_area_modifications(editor, configuration["worlds"], status_update)
    apply_custom_suits(editor, configuration["cosmetics"]["suits"])

    # Save our changes
    editor.build_modified_files()

    editor.save_modifications(PathFileWriter(output_path))
    status_update("Finished", 1.0)
