import dataclasses
import struct
from collections.abc import Iterable
from enum import Enum
from typing import NamedTuple

from ppc_asm.assembler import custom_ppc
from ppc_asm.assembler.ppc import *  # noqa: F403
from ppc_asm.dol_file import DolFile

# ruff: noqa: F405
from open_prime_rando.dol_patching.all_prime_dol_patches import (
    BasePrimeDolVersion,
    DangerousEnergyTankAddresses,
    HealthCapacityAddresses,
)
from open_prime_rando.dol_patching.echoes.beam_configuration import BeamAmmoConfiguration
from open_prime_rando.dol_patching.echoes.user_preferences import OprEchoesUserPreferences

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
    def register(self) -> Register:
        return Register(self.register_num)


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
class BeamCostAddresses:
    uncharged_cost: int
    charged_cost: int
    charge_combo_ammo_cost: int
    charge_combo_missile_cost: int
    get_beam_ammo_type_and_costs: int
    is_out_of_ammo_to_shoot: int
    gun_get_player: int
    get_item_amount: int


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


_PREFERENCES_ORDER = (
    "sound_mode",
    "screen_brightness",
    "screen_x_offset",
    "screen_y_offset",
    "screen_stretch",
    "sfx_volume",
    "music_volume",
    "hud_alpha",
    "helmet_alpha",
)
_FLAGS_ORDER = (
    "hud_lag",
    "invert_y_axis",
    "rumble",
    None,  # crashes, maybe swapBeamsControls
    "hint_system",
    None,  # 5: doesn't crash, unknown
    None,  # 6: doesn't crash, unknown
    None,  # 7: doesn't crash, unknown
)


def apply_game_options_patch(game_options_constructor_offset: int, user_preferences: OprEchoesUserPreferences,
                             dol_file: DolFile):
    patch = [
        # Unknown purpose, but keep for safety
        stw(r31, 0x1c, r1),
        or_(r31, r3, r3),

        # For a later function call we don't touch
        addi(r3, r1, 0x8),
    ]

    for i, preference_name in enumerate(_PREFERENCES_ORDER):
        value = getattr(user_preferences, preference_name)
        if isinstance(value, Enum):
            value = value.value
        patch.extend([
            li(r0, value),
            stw(r0, (0x04 * i), r31),
        ])

    flag_values = [
        getattr(user_preferences, flag_name)
        if flag_name is not None else False
        for flag_name in _FLAGS_ORDER
    ]
    bit_mask = int("".join(str(int(flag)) for flag in flag_values), 2)
    patch.extend([
        li(r0, bit_mask),
        stb(r0, 0x04 * len(_PREFERENCES_ORDER), r31),
        li(r0, 0),
        stw(r0, 0x2c, r31),
        stw(r0, 0x30, r31),
        stw(r0, 0x34, r31),
    ])

    instructions_space = 34
    instructions_to_fill = instructions_space - len(patch)

    if instructions_to_fill < 0:
        raise RuntimeError(f"Our patch ({len(patch)}) is bigger than the space we have ({instructions_space}).")

    for i in range(instructions_to_fill):
        patch.append(nop())
    dol_file.write_instructions(game_options_constructor_offset + 8 * 4, patch)


def _is_out_of_ammo_patch(symbols: dict[str, int], ammo_types: list[tuple[int, int]]):
    def get_beam_ammo_amount(index: int):
        label = f"_after_get_ammo_type_{index}"

        body = [
            lwz(r5, 0x774, r30),  # r5 = get current beam
            addi(r5, r5, 0x1),  # current_beam += 1
            mtspr(CTR, r5),  # count_register = current_beam
        ]

        for beam_index, beam_ammo_types in enumerate(ammo_types):
            instructions = []
            if beam_index + 1 < len(ammo_types):
                instructions.append(bdnz(f"_before_get_ammo_type_{beam_index + 1}_{index}"))

            if beam_ammo_types[index] == -1:
                instructions.extend([
                    li(r3, 0),  # No ammo type, so load result
                    b("_end"),  # and return
                ])
            else:
                instructions.extend([
                    li(r4, beam_ammo_types[index]),
                    b(label),
                ])

            instructions[0].with_label(f"_before_get_ammo_type_{beam_index}_{index}")
            body.extend(instructions)

        body.extend([
            or_(r3, r31, r31).with_label(label),  # arg1 = playerState, arg2 is already there
            li(r5, 1),  # arg3 = true, allow multiplayer ammo stuff
            bl("CPlayerState::GetItemAmount"),  # r3 = ammoCount
        ])

        return body

    get_uncharged_cost = [
        custom_ppc.load_unsigned_32bit(r4, symbols["BeamIdToChargedShotAmmoCost"]),
        lwz(r5, 0x774, r30),  # r5 = get current beam
        rlwinm(r5, r5, 0x2, 0x0, 0x1d),  # r5 *= 4
        lwzx(r4, r4, r5),  # ammoCost_r4 = UnchargedCosts_r4[currentBeam]
    ]
    compare_count_to_cost = [
        cmpw(0, r3, r4),
        bge(3 * 4, relative=True),  # if ammoCount_3 >= ammoCost_r4, goto
        li(r3, 1),  # Not enough ammo, load true
        b("_end"),  # and return
    ]

    return [
        # Save stack
        stwu(r1, -0x10, r1),
        mfspr(r0, LR),
        stw(r0, 0x14, r1),

        # Save r31 and r30
        stw(r31, 0xc, r1),
        stw(r30, 0x8, r1),

        # Save a pointer to CPlayerGun
        or_(r30, r3, r3),
        bl("CPlayerGun::GetPlayer"),

        # Get and save a pointer to CPlayerState
        lwz(r31, 0x1314, r3),

        # check ammo type 1
        *get_beam_ammo_amount(0),  # r3 = ammo amount
        *get_uncharged_cost,  # r4 = uncharged_cost
        *compare_count_to_cost,

        # check ammo type 2
        *get_beam_ammo_amount(1),  # r3 = ammo amount
        *get_uncharged_cost,  # r4 = uncharged_cost
        *compare_count_to_cost,

        # All ammo types for this beam are fine!
        li(r3, 0),
        b("_end"),  # and return

        # end
        lwz(r0, 0x14, r1).with_label("_end"),
        lwz(r31, 0xc, r1),
        lwz(r30, 0x8, r1),
        mtspr(LR, r0),
        addi(r1, r1, 0x10),
        blr(),
    ]


def apply_beam_cost_patch(patch_addresses: BeamCostAddresses,
                          beam_configurations: Iterable[BeamAmmoConfiguration],
                          dol_file: DolFile):
    uncharged_costs = []
    charged_costs = []
    combo_costs = []
    missile_costs = []
    ammo_types = []

    for beam_config in beam_configurations:
        uncharged_costs.append(beam_config.uncharged_cost)
        charged_costs.append(beam_config.charged_cost)
        combo_costs.append(beam_config.combo_ammo_cost)
        missile_costs.append(beam_config.combo_missile_cost)
        ammo_types.append((
            beam_config.ammo_a,
            beam_config.ammo_b,
        ))

    # The following patch also changes the fact that the game doesn't check if there's enough ammo for Power Beam
    # we start our patch right after the `addi r3,r31,0x0`
    ammo_type_patch_offset = 0x40
    offset_to_body_end = 0xB4
    ammo_type_patch = [
        lwz(r10, 0x774, r25),  # r10 = get current beam
        rlwinm(r10, r10, 0x2, 0x0, 0x1d),  # r10 *= 4

        lwzx(r0, r3, r10),  # r0 = BeamIdToUnchargedShotAmmoCost[currentBeam]
        stw(r0, 0x0, r29),  # *outBeamAmmoCost = r0

        lwz(r10, 0x774, r25),  # r10 = get current beam
        addi(r10, r10, 0x1),  # r10 = r10 + 1
        mtspr(CTR, r10),  # count_register = r10

        # Power Beam
        bdnz("dark_beam"),  # if (--count_register > 0) goto
        li(r3, ammo_types[0][0]),
        li(r9, ammo_types[0][1]),
        b("update_out_beam_type"),

        # Dark Beam
        bdnz("light_beam").with_label("dark_beam"),  # if (--count_register > 0) goto
        li(r3, ammo_types[1][0]),
        li(r9, ammo_types[1][1]),
        b("update_out_beam_type"),

        # Light Beam
        bdnz("annihilator_beam").with_label("light_beam"),  # if (--count_register > 0) goto
        li(r3, ammo_types[2][0]),
        li(r9, ammo_types[2][1]),
        b("update_out_beam_type"),

        # Annihilator Beam
        li(r3, ammo_types[3][0]).with_label("annihilator_beam"),
        li(r9, ammo_types[3][1]),

        # update_out_beam_type
        stw(r3, 0x0, r27).with_label("update_out_beam_type"),  # *outBeamAmmoTypeA = r3
        stw(r9, 0x0, r28),  # *outBeamAmmoTypeB = r9

        b(patch_addresses.get_beam_ammo_type_and_costs + offset_to_body_end),
        # jump to the code for getting the charged/combo costs and then check if has ammo
        # The address in question is at 0x801ccd64 for NTSC
    ]

    # FIXME: depend on version
    dol_file.symbols["BeamIdToChargedShotAmmoCost"] = patch_addresses.uncharged_cost
    dol_file.symbols["BeamIdToUnchargedShotAmmoCost"] = patch_addresses.charged_cost
    dol_file.symbols["BeamIdToChargeComboAmmoCost"] = patch_addresses.charge_combo_ammo_cost
    dol_file.symbols["g_ChargeComboMissileCosts"] = patch_addresses.charge_combo_missile_cost
    dol_file.symbols["CPlayerGun::IsOutOfAmmoToShoot"] = patch_addresses.is_out_of_ammo_to_shoot
    dol_file.symbols["CPlayerGun::GetPlayer"] = patch_addresses.gun_get_player
    dol_file.symbols["CPlayerState::GetItemAmount"] = patch_addresses.get_item_amount

    uncharged_costs_patch = struct.pack(">llll", *uncharged_costs)
    charged_costs_patch = struct.pack(">llll", *charged_costs)
    combo_costs_patch = struct.pack(">llll", *combo_costs)
    missile_costs_patch = struct.pack(">llll", *missile_costs)

    dol_file.write("BeamIdToChargedShotAmmoCost", uncharged_costs_patch)
    dol_file.write("BeamIdToUnchargedShotAmmoCost", charged_costs_patch)
    dol_file.write("BeamIdToChargeComboAmmoCost", combo_costs_patch)
    dol_file.write("g_ChargeComboMissileCosts", missile_costs_patch)
    dol_file.write_instructions(patch_addresses.get_beam_ammo_type_and_costs + ammo_type_patch_offset,
                                ammo_type_patch)
    dol_file.write_instructions("CPlayerGun::IsOutOfAmmoToShoot", _is_out_of_ammo_patch(dol_file.symbols, ammo_types))


def apply_safe_zone_heal_patch(patch_addresses: SafeZoneAddresses,
                               sda2_base: int,
                               heal_per_second: float,
                               dol_file: DolFile):
    offset = patch_addresses.heal_per_frame_constant - sda2_base

    dol_file.write(patch_addresses.heal_per_frame_constant, struct.pack(">f", heal_per_second / 60))
    dol_file.write_instructions(patch_addresses.increment_health_fmr, [lfs(f1, offset, r2)])


def apply_starting_visor_patch(addresses: StartingBeamVisorAddresses, default_items: dict, dol_file: DolFile):
    visor_order = ["Combat Visor", "Echo Visor", "Scan Visor", "Dark Visor"]
    beam_order = ["Power Beam", "Dark Beam", "Light Beam", "Annihilator Beam"]

    default_visor = visor_order.index(default_items["visor"])
    default_beam = beam_order.index(default_items["beam"])

    # Patch CPlayerState constructor with default values
    dol_file.write_instructions(addresses.player_state_constructor_clean + 0x54, [
        bl(addresses.health_info_constructor),

        li(r0, default_beam),
        stw(r0, 0xc, r30),  # xc_currentBeam

        li(r0, default_visor),
        stw(r0, 0x30, r30),  # x30_currentVisor
        stw(r0, 0x34, r30),  # x34_transitioningVisor

        li(r3, 0),
    ])

    # Patch CPlayerState constructor for loading save files
    dol_file.write_instructions(addresses.player_state_constructor_decode + 0x5C, [
        li(r0, default_visor),
        stw(r0, 0x30, r30),
        stw(r0, 0x34, r30),
    ])

    # Patch EnterMorphBallState's call for StartTransitionToVisor to use the new default visor
    dol_file.write_instructions(addresses.enter_morph_ball_state + 0xE8, [
        li(r4, default_visor),
    ])

    # Patch CPlayerState::ResetVisor so elevators use the new default visor
    dol_file.write_instructions(addresses.reset_visor, [
        li(r0, default_visor),
    ])


@dataclasses.dataclass(frozen=True)
class EchoesDolVersion(BasePrimeDolVersion):
    health_capacity: HealthCapacityAddresses
    dangerous_energy_tank: DangerousEnergyTankAddresses
    game_options_constructor_address: int
    beam_cost_addresses: BeamCostAddresses
    safe_zone: SafeZoneAddresses
    starting_beam_visor: StartingBeamVisorAddresses
    anything_set_address: int
    rs_debugger_printf_loop_address: int
    unvisited_room_names_address: int
    cworldtransmanager_sfxstart: int
    powerup_should_persist: int
    map_door_types: MapDoorTypeAddresses
    double_damage_vfx: int


def apply_fixes(version: EchoesDolVersion, dol_file: DolFile):
    dol_file.symbols["CMapWorldInfo::IsAnythingSet"] = version.anything_set_address

    dol_file.write_instructions("CMapWorldInfo::IsAnythingSet", [
        li(r3, 1),
        blr(),
    ])

    dol_file.write_instructions(version.rs_debugger_printf_loop_address, [
        nop(),
    ])

    # Disable Double Damage VFX by checking for an invalid item id
    dol_file.write_instructions(version.double_damage_vfx, [
        li(r4, 999),
    ])


def change_powerup_should_persist(version: EchoesDolVersion, dol_file: DolFile, powerups: list[str]):
    for item in powerups:
        index = POWERUP_TO_INDEX[item]
        dol_file.write(version.powerup_should_persist + index, b"\x01")


def apply_unvisited_room_names(version: EchoesDolVersion, dol_file: DolFile, enabled: bool):
    # In CAutoMapper::Update, the function checks for `mwInfo.IsMapped` then `mwInfo.IsAreaVisited` and if both are
    # false, sets a variable to false. This variable indicates if the room name is displayed used.
    dol_file.write_instructions(version.unvisited_room_names_address, [
        li(r28, 1 if enabled else 0),
    ])


def apply_teleporter_sounds(version: EchoesDolVersion, dol_file: DolFile, enabled: bool):
    dol_file.symbols["CWorldTransManager::SfxStart"] = version.cworldtransmanager_sfxstart

    if enabled:
        inst = stwu(r1, -0x20, r1)
    else:
        inst = blr()

    dol_file.write_instructions("CWorldTransManager::SfxStart", [
        inst
    ])


def freeze_player():
    return [
        lfs(f1, -0x707c, r2),  # timeout = 5.0f
        lwz(r3, 0x14fc, r31),  # player = manager->players[0]
        lhz(r6, -0x40da, r2),  # sfxId = kInvalidSoundId
        or_(r4, r31, r31),  # mgr
        li(r5, -0x1),  # steamTextureId
        li(r7, -0x1),  # iceTextureId
        bl("CPlayer::Freeze"),
    ]


def apply_map_door_changes(door_symbols: MapDoorTypeAddresses, dol_file: DolFile):
    # This ends up being a slow import, don't do it early
    from open_prime_rando.echoes.dock_lock_rando.map_icons import DoorMapIcon

    door_min, door_max = DoorMapIcon.get_door_index_bounds()

    num_door_colors = 1 + door_max - door_min
    assert num_door_colors <= 32, "There's only enough space for 32 colors in the table!"

    is_door_symbols = [
        door_symbols.get_correct_transform,
        door_symbols.map_obj_draw,
        door_symbols.is_visible_to_automapper,
        door_symbols.map_world_draw_areas,
        door_symbols.map_area_commit_resources1,
        door_symbols.map_area_commit_resources2,
    ]
    for symbol in is_door_symbols:
        dol_file.write_instructions(symbol.low, [cmpwi(symbol.register, door_min)])
        dol_file.write_instructions(symbol.high, [cmpwi(symbol.register, door_max)])

    # TODO: add colors to GetDoorColor
    dol_file.symbols["CTweakAutoMapper::GetDoorColor"] = door_symbols.get_door_color
    door_color_array = door_symbols.get_door_color + 32

    _colors = r6
    _type = r5
    _out_color = r3

    dol_file.write_instructions("CTweakAutoMapper::GetDoorColor", [
        custom_ppc.load_unsigned_32bit(_colors, door_color_array),
        addi(_type, _type, -door_min),
        mulli(_type, _type, 4),
        lwzx(r0, _colors, _type),
        stw(r0, 0, _out_color),
        blr()
    ])

    dol_file.symbols["CTweakAutoMapper::GetDoorColor::DoorColorArray"] = door_color_array
    dol_file.write("CTweakAutoMapper::GetDoorColor::DoorColorArray", DoorMapIcon.get_surface_colors_as_bytes())


def apply_widescreen_hack(version: EchoesDolVersion, dol_file: DolFile):
    description = str(version.description)
    if description == "Gamecube NTSC":
        apply_widescreen_hack_ntscu(dol_file)
    elif description == "Gamecube PAL":
        apply_widscreen_hack_pal(dol_file)
    else:
        raise NotImplementedError()


# ported from gamemasterplc's 16:9 gecko code
def apply_widescreen_hack_ntscu(dol_file: DolFile):
    print("Widescreen Hack: NTSC-U")
    culling_replacement = 0x8030256C
    culling_insertion = 0x80418E8C
    viewport_replacement = 0x8036D684
    viewport_insertion = 0x80003748

    dol_file.write_instructions(culling_replacement, [
        bl(culling_insertion, relative=False)
    ])

    dol_file.write_instructions(culling_insertion, [
        lis(r10, 0x4000),
        stw(r10, 0, r2),
        lfs(f26, 0, r2),
        blr()
    ])

    dol_file.write_instructions(viewport_replacement, [
        b(viewport_insertion, relative=False)
    ])

    dol_file.write_instructions(viewport_insertion, [
        lis(r10, 0x3FAA),
        ori(r10, r10, 0xAAAB),
        stw(r10, 0, r2),
        lfs(f19, 0, r2),
        fmuls(f9, f19, 0, f9),
        fdivs(f11,f10, f9, 0),
        b(viewport_replacement + 0x4, relative=False)
    ])


# ported from gamemasterplc's 16:9 gecko code
def apply_widscreen_hack_pal(dol_file: DolFile):
    print("Widescreen Hack: PAL")
    culling_replacement = 0x803029E0
    culling_insertion = 0x803c6c30
    viewport_replacement = 0x8036dA9C
    viewport_insertion = 0x803b1d60

    dol_file.write_instructions(culling_replacement, [
        bl(culling_insertion, relative=False)
    ])

    dol_file.write_instructions(culling_insertion, [
        lis(r9, 0x4000),
        stw(r9, 0, r2),
        lfs(f26, 0, r2),
        blr()
    ])

    dol_file.write_instructions(viewport_replacement, [
        b(viewport_insertion, relative=False)
    ])

    dol_file.write_instructions(viewport_insertion, [
        lis(r9, 0x3FAA),
        ori(r9, r9, 0xAAAB),
        stw(r9, 0, r2),
        lfs(f19, 0, r2),
        fmuls(f9, f19, 0, f9),
        fdivs(f11,f10, f9, 0),
        b(viewport_replacement + 0x4, relative=False)
    ])
