from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from retro_data_structures.asset_manager import IsoFileProvider, PathFileWriter
from retro_data_structures.game_check import Game

from open_prime_rando.dol_patching.echoes import dol_patcher
from open_prime_rando.dol_patching.echoes.beam_configuration import BeamAmmoConfiguration
from open_prime_rando.dol_patching.echoes.user_preferences import OprEchoesUserPreferences
from open_prime_rando.echoes import inverted, menu_mod
from open_prime_rando.echoes.elevators import auto_enabled_elevator_patches
from open_prime_rando.patcher_editor import PatcherEditor

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

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


def patch_iso(
    input_iso: Path,
    output_iso: Path,
    configuration: dict,
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

    dol_patcher.apply_patches(editor.dol, _default_dol_patches())
    if _ALL_FEATURES:
        auto_enabled_elevator_patches.apply_auto_enabled_elevators_patch(editor)
        inverted.apply_inverted(editor)

    menu_mod.add_menu_mod(editor)

    # Save our changes
    editor.build_modified_files()
    editor.save_modifications(output)
