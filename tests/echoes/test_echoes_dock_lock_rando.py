import contextlib
from unittest.mock import MagicMock

import pytest

from open_prime_rando.echoes import dock_lock_rando
from open_prime_rando.echoes.dock_lock_rando import DOCK_TYPES
from open_prime_rando.patcher_editor import PatcherEditor

_custom_asset_ids = {
    'custom_door_lock_darkburst.CMDL': 3171862285,
    'custom_door_lock_darkburst.TXTR': 3672172162,
    'custom_door_lock_darkburst_emissive.TXTR': 234173793,
    'custom_door_lock_echo_visor.CMDL': 2853277507,
    'custom_door_lock_echo_visor.TXTR': 3456085708,
    'custom_door_lock_echo_visor_emissive.TXTR': 1855515304,
    'custom_door_lock_greyscale_emissive.TXTR': 3597936245,
    'custom_door_lock_boost_ball.CMDL': 3448653349,
    'custom_door_lock_boost_ball.TXTR': 2858444714,
    'custom_door_lock_boost_ball_emissive.TXTR': 679049133,
    'custom_door_lock_cannon_ball.CMDL': 3063077393,
    'custom_door_lock_cannon_ball.TXTR': 3514629022,
    'custom_door_lock_cannon_ball_emissive.TXTR': 3792718965,
    'custom_door_lock_charge_beam.CMDL': 3005557644,
    'custom_door_lock_charge_beam.TXTR': 3570076163,
    'custom_door_lock_charge_beam_emissive.TXTR': 1595153749,
    'custom_door_lock_dark_visor.CMDL': 2145020805,
    'custom_door_lock_dark_visor.TXTR': 406080010,
    'custom_door_lock_dark_visor_emissive.TXTR': 775355676,
    'custom_door_lock_morph_ball_bombs.CMDL': 3083075990,
    'custom_door_lock_morph_ball_bombs.TXTR': 3492421657,
    'custom_door_lock_morph_ball_bombs_emissive.TXTR': 805979281,
    'custom_door_lock_screw_attack.CMDL': 1760304179,
    'custom_door_lock_screw_attack.TXTR': 251805116,
    'custom_door_lock_screw_attack_emissive.TXTR': 1723694793,
    'custom_door_lock_sonic_boom.CMDL': 1667093720,
    'custom_door_lock_sonic_boom.TXTR': 78902615,
    'custom_door_lock_sonic_boom_emissive.TXTR': 2606270890,
    'custom_door_lock_sunburst.CMDL': 987291923,
    'custom_door_lock_sunburst.TXTR': 1563869340,
    'custom_door_lock_sunburst_emissive.TXTR': 2638796108,
}


def test_add_custom_models(prime2_editor: PatcherEditor):
    dock_lock_rando.add_custom_models(prime2_editor)

    assert prime2_editor._custom_asset_ids == _custom_asset_ids


vanilla_doors = {
    "Normal": ("Torvus Bog", "Gathering Hall", "North"),
    "Dark": ("Torvus Bog", "Torvus Temple", "EastTop"),
    "Light": ("Torvus Bog", "Underground Tunnel", "North"),
    "Annihilator": ("Torvus Bog", "Gathering Hall", "East_0P"),

    "Missile": ("Temple Grounds", "GFMC Compound", "WestTop"),
    "SuperMissile": ("Torvus Bog", "Torvus Temple", "WestGenerator"),
    "SeekerMissile": ("Temple Grounds", "Path of Honor", "North"),
    "PowerBomb": ("Temple Grounds", "GFMC Compound", "West"),
}


@pytest.mark.parametrize("new_door_type", DOCK_TYPES.keys())
@pytest.mark.parametrize("old_door_type", vanilla_doors.keys())
@pytest.mark.parametrize("low_memory", [False])  # too slow to run twice for now
def test_apply_door_rando(prime2_editor, new_door_type, old_door_type, low_memory):
    prime2_editor.ensure_present = MagicMock()

    if new_door_type in {"Grapple", "AgonEnergy", "TorvusEnergy", "SanctuaryEnergy"}:
        expectation = pytest.raises(NotImplementedError)
    else:
        expectation = contextlib.nullcontext()

    world_name, area_name, dock_name = vanilla_doors[old_door_type]
    with expectation:
        dock_lock_rando.apply_door_rando(prime2_editor, world_name, area_name, dock_name,
                                         new_door_type, old_door_type, low_memory)
