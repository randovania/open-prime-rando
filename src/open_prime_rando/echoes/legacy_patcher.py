import json
import logging
import typing
import uuid
from collections.abc import Callable
from pathlib import Path
from random import Random
from typing import TYPE_CHECKING

import pydantic
from ppc_asm.dol_file import DolEditor
from retro_data_structures.asset_manager import PathFileWriter
from retro_data_structures.file_provider import FileProvider
from retro_data_structures.game_check import Game

from open_prime_rando.area_patcher import AreaPatcher
from open_prime_rando.dol_patching import all_prime_dol_patches, dol_version
from open_prime_rando.dol_patching.code_cave_tracker import CodeCaveTracker
from open_prime_rando.dol_patching.echoes import beam_cost, dol_patches, dol_versions, game_options
from open_prime_rando.echoes import (
    asset_ids,
    dock_lock_rando,
    general_changes,
    legacy_dynamic_schema,
)
from open_prime_rando.echoes.asset_ids.world import (
    AGON_WASTES_MLVL,
    SANCTUARY_FORTRESS_MLVL,
    TEMPLE_GROUNDS_MLVL,
    TORVUS_BOG_MLVL,
)
from open_prime_rando.echoes.elevators.elevator_rando import ElevatorChange, patch_elevator
from open_prime_rando.echoes.general_changes import apply_corrupted_memory_card_change
from open_prime_rando.echoes.pydantic_models import AreaReference
from open_prime_rando.echoes.small_randomizations import register_small_randomizations
from open_prime_rando.echoes.specific_area_patches import required_fixes
from open_prime_rando.echoes.suit_cosmetics import SuitMapping, SuitSkin, apply_custom_suits
from open_prime_rando.patcher_editor import PatcherEditor
from open_prime_rando.validator_with_default import DefaultValidatingDraft7Validator

if TYPE_CHECKING:
    from retro_data_structures.formats.mrea import Area

LOG = logging.getLogger("echoes_patcher")


class DolPatchesData(pydantic.BaseModel):
    world_uuid: uuid.UUID
    energy_per_tank: int
    beam_configuration: beam_cost.BeamConfiguration
    safe_zone_heal_per_second: float
    game_options_defaults: game_options.GameOptionsDefaults
    default_items: dict
    unvisited_room_names: bool
    teleporter_sounds: bool
    dangerous_energy_tank: bool


def _read_legacy_schema():
    with Path(__file__).parent.joinpath("legacy_schema.json").open() as f:
        return json.load(f)


def apply_area_modifications(
    editor: PatcherEditor, configuration: dict[str, dict], status_update: Callable[[str, float], None]
) -> None:
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
                    dock_lock_rando.apply_door_rando_legacy(
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
                    mlvl,
                    area,
                    ElevatorChange(
                        elevator_id=elevator["instance_id"],
                        target=AreaReference(
                            mlvl_id=elevator["target_assets"]["world_asset_id"],
                            mrea_id=elevator["target_assets"]["area_asset_id"],
                        ),
                        scan_strg=elevator["target_strg"],
                        target_name=elevator["target_name"],
                    ),
                )

            if area_config["new_name"] is not None:
                general_changes.change_area_name(editor, mlvl, area, area_config["new_name"])

            area.update_all_dependencies(only_modified=True)


def apply_tweak_edits(editor: PatcherEditor, tweak_edits: dict[str, dict[str, typing.Any]]) -> None:
    """
    Edits the tweaks based on the generic schema api
    :param editor:
    :param tweak_edits:
    :return:
    """
    for instance in editor.tweaks.instances:
        properties = typing.cast("dict", instance.get_properties().to_json())

        if properties["instance_name"] in tweak_edits:
            logging.debug("Editing %s", properties["instance_name"])

            for name, value in tweak_edits[properties["instance_name"]].items():
                parent = typing.cast("dict", properties)
                spit_name = name.split(".")

                for part in spit_name[:-1]:
                    parent = parent[part]

                parent[spit_name[-1]] = value

            instance.set_properties(instance.script_type.from_json(properties))


def patch_paks(
    file_provider: FileProvider,
    output_path: Path,
    configuration: dict,
    status_update: Callable[[str, float], None] = lambda s, _: LOG.info(s),
) -> None:
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
    area_patcher = AreaPatcher(
        editor, [TEMPLE_GROUNDS_MLVL, AGON_WASTES_MLVL, TORVUS_BOG_MLVL, SANCTUARY_FORTRESS_MLVL], rebuild_savw=False
    )
    area_patcher.add_function(required_fixes.torvus_temple_remove_effects)
    area_patcher.add_function(required_fixes.command_center_door)
    register_small_randomizations(area_patcher, Random(configuration["small_randomizations"]["seed"]))
    area_patcher.perform_changes()
    apply_corrupted_memory_card_change(editor)

    if "tweaks" in configuration:
        status_update("Modifying tweaks", 0)
        apply_tweak_edits(editor, configuration["tweaks"])

    status_update("Modifying areas", 0)
    apply_area_modifications(editor, configuration["worlds"], status_update)
    apply_custom_suits(
        editor,
        SuitMapping(
            varia=SuitSkin(configuration["cosmetics"]["suits"]["varia"]),
            dark=SuitSkin(configuration["cosmetics"]["suits"]["dark"]),
            light=SuitSkin(configuration["cosmetics"]["suits"]["light"]),
        ),
    )

    # Save our changes
    editor.build_modified_files()

    editor.save_modifications(PathFileWriter(output_path))
    status_update("Finished", 1.0)


def patch_dol(dol_editor: DolEditor, patches_data: DolPatchesData) -> None:
    version = dol_version.find_version_for_dol(dol_editor, dol_versions.ALL_VERSIONS)
    assert isinstance(version, dol_patches.EchoesDolVersion)

    cave = CodeCaveTracker(dol_editor)

    dol_patches.apply_mandatory_fixes(version, cave)
    dol_patches.change_powerup_should_persist(
        version, dol_editor, ["Double Damage", "Unlimited Missiles", "Unlimited Beam Ammo"]
    )

    all_prime_dol_patches.apply_build_info_patch(version, dol_editor, patches_data.world_uuid)
    all_prime_dol_patches.apply_remote_execution_patch(version.game, version.string_display, dol_editor)
    all_prime_dol_patches.apply_energy_tank_capacity_patch(
        version.health_capacity, patches_data.energy_per_tank, dol_editor
    )
    all_prime_dol_patches.apply_reverse_energy_tank_heal_patch(
        version.sda2_base, version.dangerous_energy_tank, patches_data.dangerous_energy_tank, version.game, dol_editor
    )

    dol_patches.apply_unvisited_room_names(version, dol_editor, patches_data.unvisited_room_names)
    dol_patches.apply_teleporter_sounds(version, dol_editor, patches_data.teleporter_sounds)

    game_options.apply_patch(version.game_options_constructor_address, dol_editor, patches_data.game_options_defaults)
    beam_cost.apply_patch(version.beam_cost_addresses, dol_editor, patches_data.beam_configuration)
    dol_patches.apply_safe_zone_heal_patch(
        version.safe_zone, version.sda2_base, patches_data.safe_zone_heal_per_second, dol_editor
    )
    dol_patches.apply_starting_visor_patch(version.starting_beam_visor, patches_data.default_items, dol_editor)
    dol_patches.apply_map_door_changes(version.map_door_types, dol_editor)

    cave.fulfill_requests()
