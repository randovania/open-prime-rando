from __future__ import annotations

import dataclasses
import struct
from typing import TYPE_CHECKING, Annotated

import pydantic
from annotated_types import Interval
from ppc_asm.assembler import BaseInstruction, Instruction, custom_ppc
from ppc_asm.assembler.ppc import (
    CTR,
    LR,
    addi,
    b,
    bdnz,
    bge,
    bl,
    blr,
    cmpw,
    li,
    lwz,
    lwzx,
    mfspr,
    mtspr,
    or_,
    r0,
    r1,
    r3,
    r4,
    r5,
    r9,
    r10,
    r25,
    r27,
    r28,
    r29,
    r30,
    r31,
    rlwinm,
    stw,
    stwu,
)
from pydantic import Field
from retro_data_structures.enums.echoes import PlayerItemEnum

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ppc_asm.dol_file import DolEditor

    from open_prime_rando.dol_patching.code_cave_tracker import CodeCaveTracker


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

    def register_symbols_to(self, cave: CodeCaveTracker) -> None:
        symbols = cave.dol_editor.symbols
        symbols["g_ChargeComboMissileCosts"] = self.charge_combo_missile_cost
        symbols["BeamIdToUnchargedShotAmmoCost"] = self.uncharged_cost
        symbols["BeamIdToChargedShotAmmoCost"] = self.charged_cost
        symbols["BeamIdToChargeComboAmmoCost"] = self.charge_combo_ammo_cost

        symbols["CPlayerGun::GetPlayer"] = self.gun_get_player
        symbols["CPlayerGun::IsOutOfAmmoToShoot"] = self.is_out_of_ammo_to_shoot
        symbols["CPlayerState::GetItemAmount"] = self.get_item_amount
        symbols["CSamusGun::GetBeamAmmoTypeAndCosts"] = self.get_beam_ammo_type_and_costs


def _get_ammo_index(item: PlayerItemEnum | None) -> int:
    if item is not None:
        return item.value
    else:
        return -1


class BeamAmmoConfiguration(pydantic.BaseModel):
    """Ammo overrides for a single beam. Can have up to 2 ammo type costs."""

    ammo_a: PlayerItemEnum | None
    ammo_b: PlayerItemEnum | None = None
    uncharged_cost: Annotated[int, Interval(ge=0, le=250)] = 1
    charged_cost: Annotated[int, Interval(ge=0, le=250)] = 5
    combo_missile_cost: Annotated[int, Interval(ge=1, le=250)] = 5
    combo_ammo_cost: Annotated[int, Interval(ge=0, le=250)] = 30

    def ammo_types(self) -> tuple[int, int]:
        """Indices of the two beams, as used by the dol patch."""
        return _get_ammo_index(self.ammo_a), _get_ammo_index(self.ammo_b)


class BeamConfiguration(pydantic.BaseModel):
    """Ammo overrides for all beams. Defaults to vanilla configuration."""

    power: BeamAmmoConfiguration = Field(default_factory=lambda: BeamAmmoConfiguration(ammo_a=None))
    dark: BeamAmmoConfiguration = Field(default_factory=lambda: BeamAmmoConfiguration(ammo_a=PlayerItemEnum.DarkAmmo))
    light: BeamAmmoConfiguration = Field(default_factory=lambda: BeamAmmoConfiguration(ammo_a=PlayerItemEnum.LightAmmo))
    annihilator: BeamAmmoConfiguration = Field(
        default_factory=lambda: BeamAmmoConfiguration(ammo_a=PlayerItemEnum.DarkAmmo, ammo_b=PlayerItemEnum.LightAmmo)
    )

    def beams(
        self,
    ) -> tuple[BeamAmmoConfiguration, BeamAmmoConfiguration, BeamAmmoConfiguration, BeamAmmoConfiguration]:
        """Returns all the beams in the order needed by apply_patch"""
        return self.power, self.dark, self.light, self.annihilator


def _is_out_of_ammo_patch(symbols: dict[str, int], ammo_types: list[tuple[int, int]]):
    def get_beam_ammo_amount(index: int) -> Sequence[BaseInstruction]:
        label = f"_after_get_ammo_type_{index}"

        body: list[BaseInstruction | Instruction] = [
            lwz(r5, 0x774, r30),  # r5 = get current beam
            addi(r5, r5, 0x1),  # current_beam += 1
            mtspr(CTR, r5),  # count_register = current_beam
        ]

        for beam_index, beam_ammo_types in enumerate(ammo_types):
            instructions = []
            if beam_index + 1 < len(ammo_types):
                instructions.append(bdnz(f"_before_get_ammo_type_{beam_index + 1}_{index}"))

            if beam_ammo_types[index] == -1:
                instructions.extend(
                    [
                        li(r3, 0),  # No ammo type, so load result
                        b("_end"),  # and return
                    ]
                )
            else:
                instructions.extend(
                    [
                        li(r4, beam_ammo_types[index]),
                        b(label),
                    ]
                )

            instructions[0].with_label(f"_before_get_ammo_type_{beam_index}_{index}")
            body.extend(instructions)

        body.extend(
            [
                or_(r3, r31, r31).with_label(label),  # arg1 = playerState, arg2 is already there
                li(r5, 1),  # arg3 = true, allow multiplayer ammo stuff
                bl("CPlayerState::GetItemAmount"),  # r3 = ammoCount
            ]
        )

        return body

    get_uncharged_cost = [
        custom_ppc.load_unsigned_32bit(r4, symbols["BeamIdToUnchargedShotAmmoCost"]),
        lwz(r5, 0x774, r30),  # r5 = get current beam
        rlwinm(r5, r5, 0x2, 0x0, 0x1D),  # r5 *= 4
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
        stw(r31, 0xC, r1),
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
        lwz(r31, 0xC, r1),
        lwz(r30, 0x8, r1),
        mtspr(LR, r0),
        addi(r1, r1, 0x10),
        blr(),
    ]


def apply_patch(
    patch_addresses: BeamCostAddresses,
    dol_editor: DolEditor,
    beam_configurations: BeamConfiguration,
) -> None:
    """Patches the functions for checking ammo and consuming ammo to use different ammo requirements."""
    uncharged_costs: list[int] = []
    charged_costs: list[int] = []
    combo_costs: list[int] = []
    missile_costs: list[int] = []
    ammo_types: list[tuple[int, int]] = []

    for beam_config in beam_configurations.beams():
        uncharged_costs.append(beam_config.uncharged_cost)
        charged_costs.append(beam_config.charged_cost)
        combo_costs.append(beam_config.combo_ammo_cost)
        missile_costs.append(beam_config.combo_missile_cost)
        ammo_types.append(beam_config.ammo_types())

    # The following patch also changes the fact that the game doesn't check if there's enough ammo for Power Beam
    # we start our patch right after the `addi r3,r31,0x0`
    ammo_type_patch_offset = 0x40
    offset_to_body_end = 0xB4
    ammo_type_patch = [
        lwz(r10, 0x774, r25),  # r10 = get current beam
        rlwinm(r10, r10, 0x2, 0x0, 0x1D),  # r10 *= 4
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

    uncharged_costs_patch = struct.pack(">llll", *uncharged_costs)
    charged_costs_patch = struct.pack(">llll", *charged_costs)
    combo_costs_patch = struct.pack(">llll", *combo_costs)
    missile_costs_patch = struct.pack(">llll", *missile_costs)

    dol_editor.write("BeamIdToUnchargedShotAmmoCost", uncharged_costs_patch)
    dol_editor.write("BeamIdToChargedShotAmmoCost", charged_costs_patch)
    dol_editor.write("BeamIdToChargeComboAmmoCost", combo_costs_patch)
    dol_editor.write("g_ChargeComboMissileCosts", missile_costs_patch)
    dol_editor.write_instructions(("CSamusGun::GetBeamAmmoTypeAndCosts", ammo_type_patch_offset), ammo_type_patch)
    dol_editor.write_instructions(
        "CPlayerGun::IsOutOfAmmoToShoot", _is_out_of_ammo_patch(dol_editor.symbols, ammo_types)
    )
