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
    'custom_door_lock_screwattack.CMDL': 1232841653,
    'custom_door_lock_screwattack.TXTR': 781552186,
    'custom_door_lock_screwattack_emissive.TXTR': 1230915219,
    'custom_door_lock_sonicboom.CMDL': 1368621368,
    'custom_door_lock_sonicboom.TXTR': 914202807,
    'custom_door_lock_sunburst.CMDL': 987291923,
    'custom_door_lock_sunburst.TXTR': 1563869340,
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
