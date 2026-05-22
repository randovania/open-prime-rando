import contextlib
from unittest.mock import MagicMock

import pytest

from open_prime_rando.echoes import dock_lock_rando
from open_prime_rando.echoes.asset_ids.temple_grounds import GFMC_COMPOUND_MREA, PATH_OF_HONOR_MREA
from open_prime_rando.echoes.asset_ids.torvus_bog import (
    GATHERING_HALL_MREA,
    TORVUS_TEMPLE_MREA,
    UNDERGROUND_TUNNEL_MREA,
)
from open_prime_rando.echoes.asset_ids.world import TEMPLE_GROUNDS_MLVL, TORVUS_BOG_MLVL
from open_prime_rando.echoes.dock_lock_rando import DOCK_TYPES, DockTypeChange
from open_prime_rando.patcher_editor import PatcherEditor

_custom_asset_ids = {
    "custom_door_lock_darkburst.CMDL": 3171862285,
    "custom_door_lock_darkburst.TXTR": 3672172162,
    "custom_door_lock_darkburst_emissive.TXTR": 234173793,
    "custom_door_lock_echo_visor.CMDL": 2853277507,
    "custom_door_lock_echo_visor.TXTR": 3456085708,
    "custom_door_lock_echo_visor_emissive.TXTR": 1855515304,
    "custom_door_lock_greyscale_emissive.TXTR": 3597936245,
    "custom_door_lock_boost_ball.CMDL": 3448653349,
    "custom_door_lock_boost_ball.TXTR": 2858444714,
    "custom_door_lock_boost_ball_emissive.TXTR": 679049133,
    "custom_door_lock_cannon_ball.CMDL": 3063077393,
    "custom_door_lock_cannon_ball.TXTR": 3514629022,
    "custom_door_lock_cannon_ball_emissive.TXTR": 3792718965,
    "custom_door_lock_charge_beam.CMDL": 3005557644,
    "custom_door_lock_charge_beam.TXTR": 3570076163,
    "custom_door_lock_charge_beam_emissive.TXTR": 1595153749,
    "custom_door_lock_dark_visor.CMDL": 2145020805,
    "custom_door_lock_dark_visor.TXTR": 406080010,
    "custom_door_lock_dark_visor_emissive.TXTR": 775355676,
    "custom_door_lock_morph_ball_bombs.CMDL": 3083075990,
    "custom_door_lock_morph_ball_bombs.TXTR": 3492421657,
    "custom_door_lock_morph_ball_bombs_emissive.TXTR": 805979281,
    "custom_door_lock_screw_attack.CMDL": 1760304179,
    "custom_door_lock_screw_attack.TXTR": 251805116,
    "custom_door_lock_screw_attack_emissive.TXTR": 1723694793,
    "custom_door_lock_sonic_boom.CMDL": 1667093720,
    "custom_door_lock_sonic_boom.TXTR": 78902615,
    "custom_door_lock_sonic_boom_emissive.TXTR": 2606270890,
    "custom_door_lock_sunburst.CMDL": 987291923,
    "custom_door_lock_sunburst.TXTR": 1563869340,
    "custom_door_lock_sunburst_emissive.TXTR": 2638796108,
}


def test_add_custom_models(prime2_editor: PatcherEditor):
    dock_lock_rando.add_custom_models(prime2_editor)

    assert prime2_editor._custom_asset_ids == _custom_asset_ids


vanilla_doors = {
    "Normal": (TORVUS_BOG_MLVL, GATHERING_HALL_MREA, "North"),
    "Dark": (TORVUS_BOG_MLVL, TORVUS_TEMPLE_MREA, "EastTop"),
    "Light": (TORVUS_BOG_MLVL, UNDERGROUND_TUNNEL_MREA, "North"),
    "Annihilator": (TORVUS_BOG_MLVL, GATHERING_HALL_MREA, "East_0P"),
    "Missile": (TEMPLE_GROUNDS_MLVL, GFMC_COMPOUND_MREA, "WestTop"),
    "SuperMissile": (TORVUS_BOG_MLVL, TORVUS_TEMPLE_MREA, "WestGenerator"),
    "SeekerMissile": (TEMPLE_GROUNDS_MLVL, PATH_OF_HONOR_MREA, "North"),
    "PowerBomb": (TEMPLE_GROUNDS_MLVL, GFMC_COMPOUND_MREA, "West"),
}


@pytest.mark.parametrize("new_door_type", DOCK_TYPES.keys())
@pytest.mark.parametrize("old_door_type", vanilla_doors.keys())
def test_apply_door_rando(prime2_editor, new_door_type, old_door_type):
    prime2_editor.ensure_present = MagicMock()

    if new_door_type in {"Grapple", "AgonEnergy", "TorvusEnergy", "SanctuaryEnergy"}:
        expectation = pytest.raises(NotImplementedError)
    else:
        expectation = contextlib.nullcontext()

    world_id, area_id, dock_name = vanilla_doors[old_door_type]
    area = prime2_editor.get_area(world_id, area_id)
    mlvl = area.parent_mlvl

    change = DockTypeChange(
        dock_name=dock_name,
        old_door_type=DOCK_TYPES[old_door_type],
        new_door_type=DOCK_TYPES[new_door_type],
    )

    with expectation:
        dock_lock_rando.apply_door_rando(prime2_editor, mlvl, area, change)
