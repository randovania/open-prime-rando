from __future__ import annotations

import dataclasses
import struct
from typing import TYPE_CHECKING, NamedTuple

import open_prime_rando_practice_mod
from ppc_asm.assembler import custom_ppc
from ppc_asm.assembler.ppc import *  # noqa: F403

# ruff: noqa: F405
from open_prime_rando.dol_patching.all_prime_dol_patches import (
    BasePrimeDolVersion,
    DangerousEnergyTankAddresses,
    HealthCapacityAddresses,
)
from open_prime_rando.dol_patching.echoes.beam_cost import BeamCostAddresses
from open_prime_rando.dol_patching.echoes.stk_on_map import StkMapIconSymbols
from open_prime_rando.echoes.version import EchoesVersion

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ppc_asm.dol_file import DolEditor

    from open_prime_rando.dol_patching.code_cave_tracker import CodeCaveTracker

POWERUP_TO_INDEX = {
    "Double Damage": 58,
    "Unlimited Missiles": 81,
    "Unlimited Beam Ammo": 82,
}


class IsDoorAddr(NamedTuple):
    low: int
    high: int
    register_num: int

    @property
    def register(self) -> GeneralRegister:
        return GeneralRegister(self.register_num)


@dataclasses.dataclass(frozen=True)
class MapDoorTypeAddresses:
    get_correct_transform: IsDoorAddr
    map_obj_draw: IsDoorAddr
    is_visible_to_automapper: IsDoorAddr
    map_world_draw_areas: IsDoorAddr
    map_area_commit_resources1: IsDoorAddr
    map_area_commit_resources2: IsDoorAddr
    get_door_color: int
    map_icon_jumptable: int


@dataclasses.dataclass(frozen=True)
class SafeZoneAddresses:
    heal_per_frame_constant: int
    increment_health_fmr: int


@dataclasses.dataclass(frozen=True)
class StartingBeamVisorAddresses:
    player_state_constructor_clean: int
    player_state_constructor_decode: int
    health_info_constructor: int
    enter_morph_ball_state: int
    start_transition_to_visor: int
    reset_visor: int


def apply_safe_zone_heal_patch(
    patch_addresses: SafeZoneAddresses, sda2_base: int, heal_per_second: float, dol_editor: DolEditor
) -> None:
    """Changes safe zones to heal the given amount instead of 1/s."""
    offset = patch_addresses.heal_per_frame_constant - sda2_base

    # Patches some unused float constant with our new per-tick amount
    # Then changes the code to use that float instead of the dt argument.
    # (which is fine because the dt argument is always 1/60)
    dol_editor.write(patch_addresses.heal_per_frame_constant, struct.pack(">f", heal_per_second / 60))
    dol_editor.write_instructions(patch_addresses.increment_health_fmr, [lfs(f1, offset, r2)])


def apply_starting_visor_patch(
    addresses: StartingBeamVisorAddresses, default_items: dict, dol_editor: DolEditor
) -> None:
    visor_order = ["Combat Visor", "Echo Visor", "Scan Visor", "Dark Visor"]
    beam_order = ["Power Beam", "Dark Beam", "Light Beam", "Annihilator Beam"]

    default_visor = visor_order.index(default_items["visor"])
    default_beam = beam_order.index(default_items["beam"])

    # Patch CPlayerState constructor with default values
    dol_editor.write_instructions(
        addresses.player_state_constructor_clean + 0x54,
        [
            bl(addresses.health_info_constructor),
            li(r0, default_beam),
            stw(r0, 0xC, r30),  # xc_currentBeam
            li(r0, default_visor),
            stw(r0, 0x30, r30),  # x30_currentVisor
            stw(r0, 0x34, r30),  # x34_transitioningVisor
            li(r3, 0),
        ],
    )

    # Patch CPlayerState constructor for loading save files
    dol_editor.write_instructions(
        addresses.player_state_constructor_decode + 0x5C,
        [
            li(r0, default_visor),
            stw(r0, 0x30, r30),
            stw(r0, 0x34, r30),
        ],
    )

    # Patch EnterMorphBallState's call for StartTransitionToVisor to use the new default visor
    dol_editor.write_instructions(
        addresses.enter_morph_ball_state + 0xE8,
        [
            li(r4, default_visor),
        ],
    )

    # Patch CPlayerState::ResetVisor so elevators use the new default visor
    dol_editor.write_instructions(
        addresses.reset_visor,
        [
            li(r0, default_visor),
        ],
    )


@dataclasses.dataclass(frozen=True)
class EchoesDolVersion(BasePrimeDolVersion):
    echoes_version: EchoesVersion
    practice_mod_version: open_prime_rando_practice_mod.GameVersion
    fp_unsigned_bias: int
    health_capacity: HealthCapacityAddresses
    dangerous_energy_tank: DangerousEnergyTankAddresses
    game_options_constructor_address: int
    beam_cost_addresses: BeamCostAddresses
    safe_zone: SafeZoneAddresses
    starting_beam_visor: StartingBeamVisorAddresses
    anything_set_start_address: int
    anything_set_end_address: int
    error_handler_start_address: int
    unvisited_room_names_address: int
    cworldtransmanager_sfxstart: int
    powerup_should_persist: int
    powerup_max: int
    map_door_types: MapDoorTypeAddresses
    massive_damage_vfx: int
    starting_area_serialize_clean_slot_address: int
    inventory_slot_to_item_id_address: int
    stk_map_icon: StkMapIconSymbols
    apply_double_damage_address: int
    apply_double_damage_float: int


def _all_worlds_visible(version: EchoesDolVersion, cave: CodeCaveTracker) -> None:
    """Makes it so that all worlds are always visible, even if you haven't visited them."""

    cave.register_symbol(
        "CMapWorldInfo::IsAnythingSet",
        version.anything_set_start_address,
        end=version.anything_set_end_address,
    )
    cave.replace_symbol(
        "CMapWorldInfo::IsAnythingSet",
        [
            li(r3, 1),
            blr(),
        ],
    )


def _error_screen_enabled(version: EchoesDolVersion, cave: CodeCaveTracker) -> None:
    """Makes all crashes automatically show the error screen, without checking for controller input."""

    # On NTSC,
    # 8028c3f4: start
    # 8028c4b8: bl OSGetTime
    # 8028c608: first instruction after

    get_time_call_address = (0x8028C4B8 - 0x8028C3F4) + version.error_handler_start_address
    end_block_address = (0x8028C608 - 0x8028C3F4) + version.error_handler_start_address

    cave.dol_editor.write_instructions(
        get_time_call_address,
        [
            b(end_block_address),
        ],
    )
    cave.add_empty_space(get_time_call_address + 4, end=end_block_address)


def _remove_massive_damage_vfx(version: EchoesDolVersion, dol_editor: DolEditor) -> None:
    """
    Disables the glowing red morph ball from when you have massive damage.

    This effect has a visual bug where it flashes very badly when in a safe zone.
    """

    # Change the item check for to an invalid item id
    dol_editor.write_instructions(
        version.massive_damage_vfx,
        [
            li(r4, 999),
        ],
    )


def apply_mandatory_fixes(version: EchoesDolVersion, cave: CodeCaveTracker) -> None:
    """Mandatory fixes that we want applied no matter what."""

    _all_worlds_visible(version, cave)
    _error_screen_enabled(version, cave)
    _remove_massive_damage_vfx(version, cave.dol_editor)


def change_powerup_should_persist(version: EchoesDolVersion, dol_editor: DolEditor, powerups: list[str]) -> None:
    for item in powerups:
        index = POWERUP_TO_INDEX[item]
        dol_editor.write(version.powerup_should_persist + index, b"\x01")


def apply_unvisited_room_names(version: EchoesDolVersion, dol_editor: DolEditor, enabled: bool) -> None:
    # In CAutoMapper::Update, the function checks for `mwInfo.IsMapped` then `mwInfo.IsAreaVisited` and if both are
    # false, sets a variable to false. This variable indicates if the room name is displayed used.
    dol_editor.write_instructions(
        version.unvisited_room_names_address,
        [
            li(r28, 1 if enabled else 0),
        ],
    )


def apply_teleporter_sounds(version: EchoesDolVersion, dol_editor: DolEditor, enabled: bool) -> None:
    dol_editor.symbols["CWorldTransManager::SfxStart"] = version.cworldtransmanager_sfxstart

    if enabled:
        inst = stwu(r1, -0x20, r1)
    else:
        inst = blr()

    dol_editor.write_instructions("CWorldTransManager::SfxStart", [inst])


def freeze_player() -> Sequence[BaseInstruction]:
    return [
        lfs(f1, -0x707C, r2),  # timeout = 5.0f
        lwz(r3, 0x14FC, r31),  # player = manager->players[0]
        lhz(r6, -0x40DA, r2),  # sfxId = kInvalidSoundId
        or_(r4, r31, r31),  # mgr
        li(r5, -0x1),  # steamTextureId
        li(r7, -0x1),  # iceTextureId
        bl("CPlayer::Freeze"),
    ]


def apply_map_door_changes(door_symbols: MapDoorTypeAddresses, dol_editor: DolEditor) -> None:
    """Adds support for additional door colors"""

    # This ends up being a slow import, don't do it early
    from open_prime_rando.echoes.dock_lock_rando.map_icons import DoorMapIcon

    door_min, door_max = DoorMapIcon.get_door_index_bounds()

    num_door_colors = 1 + door_max - door_min
    assert num_door_colors <= 32, "There's only enough space for 32 colors in the table!"

    is_door_symbols: list[IsDoorAddr] = [
        door_symbols.get_correct_transform,
        door_symbols.map_obj_draw,
        door_symbols.is_visible_to_automapper,
        door_symbols.map_world_draw_areas,
        door_symbols.map_area_commit_resources1,
        door_symbols.map_area_commit_resources2,
    ]
    for symbol in is_door_symbols:
        dol_editor.write_instructions(symbol.low, [cmpwi(symbol.register, door_min)])
        dol_editor.write_instructions(symbol.high, [cmpwi(symbol.register, door_max)])

    # TODO: add colors to GetDoorColor
    dol_editor.symbols["CTweakAutoMapper::GetDoorColor"] = door_symbols.get_door_color
    door_color_array = door_symbols.get_door_color + 32

    _colors = r6
    _type = r5
    _out_color = r3

    dol_editor.write_instructions(
        "CTweakAutoMapper::GetDoorColor",
        [
            custom_ppc.load_unsigned_32bit(_colors, door_color_array),
            addi(_type, _type, -door_min),
            mulli(_type, _type, 4),
            lwzx(r0, _colors, _type),
            stw(r0, 0, _out_color),
            blr(),
        ],
    )

    dol_editor.symbols["CTweakAutoMapper::GetDoorColor::DoorColorArray"] = door_color_array
    dol_editor.write("CTweakAutoMapper::GetDoorColor::DoorColorArray", DoorMapIcon.get_surface_colors_as_bytes())
