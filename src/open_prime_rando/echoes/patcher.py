from __future__ import annotations

import logging
import struct
import uuid
from typing import TYPE_CHECKING

from ppc_asm.assembler import ppc
from retro_data_structures.asset_manager import IsoFileProvider, PathFileWriter
from retro_data_structures.exceptions import UnknownAssetId
from retro_data_structures.game_check import Game
from retro_data_structures.properties.echoes.objects import WorldTeleporter

from open_prime_rando.dol_patching.echoes import dol_patcher
from open_prime_rando.dol_patching.echoes.beam_configuration import BeamAmmoConfiguration
from open_prime_rando.dol_patching.echoes.user_preferences import OprEchoesUserPreferences
from open_prime_rando.echoes import custom_assets, frontend_asset_ids, inverted
from open_prime_rando.echoes.elevators import auto_enabled_elevator_patches
from open_prime_rando.patcher_editor import PatcherEditor

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from open_prime_rando.dol_patching.echoes.dol_patches import EchoesDolVersion
    from open_prime_rando.echoes.rando_configuration import AreaReference, RandoConfiguration

LOG = logging.getLogger("echoes_patcher")


def _default_dol_patches() -> dol_patcher.EchoesDolPatchesData:
    return dol_patcher.EchoesDolPatchesData(
        world_uuid=uuid.UUID("00000000-0000-1111-0000-000000000000"),
        energy_per_tank=100,
        beam_configurations=[
            BeamAmmoConfiguration.from_json(it)
            for it in [
                {
                    "item_index": 0,
                    "ammo_a": -1,
                    "ammo_b": -1,
                    "uncharged_cost": 0,
                    "charged_cost": 0,
                    "combo_missile_cost": 5,
                    "combo_ammo_cost": 0,
                },
                {
                    "item_index": 1,
                    "ammo_a": 45,
                    "ammo_b": -1,
                    "uncharged_cost": 1,
                    "charged_cost": 5,
                    "combo_missile_cost": 5,
                    "combo_ammo_cost": 30,
                },
                {
                    "item_index": 2,
                    "ammo_a": 46,
                    "ammo_b": -1,
                    "uncharged_cost": 1,
                    "charged_cost": 5,
                    "combo_missile_cost": 5,
                    "combo_ammo_cost": 30,
                },
                {
                    "item_index": 3,
                    "ammo_a": 46,
                    "ammo_b": 45,
                    "uncharged_cost": 1,
                    "charged_cost": 5,
                    "combo_missile_cost": 5,
                    "combo_ammo_cost": 30,
                },
            ]
        ],
        safe_zone_heal_per_second=1.0,
        user_preferences=OprEchoesUserPreferences(),
        default_items={"visor": "Combat Visor", "beam": "Power Beam"},
        unvisited_room_names=True,
        teleporter_sounds=True,
        dangerous_energy_tank=False,
    )


_ALL_FEATURES = False


def edit_starting_area_dol(editor: PatcherEditor, version: EchoesDolVersion, starting_area: AreaReference) -> None:
    function_address = version.starting_area_serialize_clean_slot_address  # CGameState::SerializeNewForCleanSlot

    def split_int(value: int) -> tuple[int, int]:
        high = value >> 16
        low = struct.unpack("h", struct.pack("H", value & 0xFFFF))[0]

        if low < 0:
            # When low_value is considered negative, adding it will subtract the overflow bit
            # Add one to high_value to fix it
            high += 1

        return high, low

    world_high, world_low = split_int(starting_area.mlvl_id)
    area_high, area_low = split_int(starting_area.mrea_id)

    # SetMLvlId argument
    editor.dol.write_instructions(function_address + 12 * 4, [ppc.lis(ppc.r4, world_high)])
    editor.dol.write_instructions(function_address + 14 * 4, [ppc.addi(ppc.r4, ppc.r4, world_low)])

    # StateForWorld argument
    editor.dol.write_instructions(function_address + 16 * 4, [ppc.lis(ppc.r4, world_high)])
    editor.dol.write_instructions(function_address + 18 * 4, [ppc.addi(ppc.r4, ppc.r4, world_low)])

    # SetDesiredAreaAssetId
    editor.dol.write_instructions(function_address + 20 * 4, [ppc.lis(ppc.r4, area_high)])
    editor.dol.write_instructions(function_address + 21 * 4, [ppc.addi(ppc.r4, ppc.r4, area_low)])


def edit_starting_area_teleporter(editor: PatcherEditor, starting_area: AreaReference) -> None:
    try:
        area = editor.get_area(frontend_asset_ids.FRONTEND_PAL_MLVL, frontend_asset_ids.FRONTEND_PAL_MREA)
    except UnknownAssetId:
        area = editor.get_area(frontend_asset_ids.FRONTEND_NTSC_MLVL, frontend_asset_ids.FRONTEND_NTSC_MREA)

    elevator = area.get_instance("StartNewSinglePlayerGame")
    with elevator.edit_properties(WorldTeleporter) as teleporter:
        teleporter.world = starting_area.mlvl_id
        teleporter.area = starting_area.mrea_id


def edit_starting_area(editor: PatcherEditor, version: EchoesDolVersion, starting_area: AreaReference) -> None:
    edit_starting_area_dol(editor, version, starting_area)
    edit_starting_area_teleporter(editor, starting_area)


def patch_iso(
    input_iso: Path,
    output_iso: Path,
    configuration: RandoConfiguration,
    status_update: Callable[[str, float], None] = lambda s, _: LOG.info(s),
) -> None:
    """

    :param input_iso:
    :param output_iso:
    :param configuration:
    :param status_update:
    :return:
    """
    file_provider = IsoFileProvider(input_iso)
    output = PathFileWriter(output_iso)  # TODO: IsoFileWriter

    editor = PatcherEditor(file_provider, Game.ECHOES)

    custom_assets.create_custom_assets(editor)
    version = dol_patcher.apply_patches(editor.dol, _default_dol_patches())

    if configuration.starting_area is not None:
        edit_starting_area(editor, version, configuration.starting_area)

    if _ALL_FEATURES:
        auto_enabled_elevator_patches.apply_auto_enabled_elevators_patch(editor)
        inverted.apply_inverted(editor)

    # Save our changes
    editor.build_modified_files()
    editor.save_modifications(output)
