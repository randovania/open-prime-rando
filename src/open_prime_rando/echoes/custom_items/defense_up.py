import struct
from typing import Annotated

import pydantic
from annotated_types import Interval
from ppc_asm.assembler import BaseInstruction
from ppc_asm.assembler.ppc import (
    bl,
    f1,
    f2,
    f3,
    f30,
    fmuls,
    fsubs,
    lfd,
    li,
    lis,
    mr,
    r0,
    r1,
    r2,
    r3,
    r4,
    r5,
    r26,
    r27,
    stw,
)
from retro_data_structures.enums.echoes import PlayerItemEnum
from retro_data_structures.properties.echoes.objects import TweakPlayer

from open_prime_rando.dol_patching.all_prime_dol_patches import FloatRegister, GeneralRegister
from open_prime_rando.dol_patching.echoes.dol_patches import EchoesDolVersion
from open_prime_rando.patcher_editor import PatcherEditor


class DefenseUpConfig(pydantic.BaseModel):
    """Control how strong Massive Damage is and how many copies you can have."""

    damage_reduction_multiplier: float = 0.0
    """By how much damage reduction each copy of the item gives."""

    max_count: Annotated[int, Interval(ge=1, le=255)] = 1
    """How many copies of the item you're allowed to have."""


def _convert_int_to_float_using_stack(
    version: EchoesDolVersion,
    input_register: GeneralRegister,
    output_register: FloatRegister,
    bias_register: FloatRegister,
) -> list[BaseInstruction]:
    # this conversion must involve the memory, so we use the stack below r1 since we're not calling anything
    return [
        lis(r0, 0x4330),  # load upper half of double constant
        stw(r0, -0x8, r1),
        stw(input_register, -0x4, r1),
        lfd(output_register, -0x8, r1),  # load as double
        lfd(bias_register, (version.fp_unsigned_bias - version.sda2_base), r2),  # load the bias constant
        fsubs(output_register, output_register, bias_register),  # subtract bias constant
    ]


def apply_dol_patches(version: EchoesDolVersion, editor: PatcherEditor, config: DefenseUpConfig) -> None:
    cave = editor.code_cave

    with editor.edit_tweak(TweakPlayer) as tweak:
        tweak.suit_damage_reduction.varia = config.damage_reduction_multiplier

    # Adjust the max capacity of Massive Damage
    cave.dol_editor.write(version.powerup_max + PlayerItemEnum.VariaSuit.value * 4, struct.pack(">l", config.max_count))

    start_offset = 476
    instruction_count = 312

    cave.replace_instructions(
        address=cave.dol_editor.symbols["CDamageInfo::ApplyDoubleDamage"] + start_offset,
        instruction_count=instruction_count,
        instructions=[
            mr(r3, r26),  # put the CPlayer pointer in r3
            bl("CPlayer::GetTweakPlayer"),
            bl("CTweakPlayer::GetVariaSuitDamageReduction"),
            # f1 has the reduction
            mr(r3, r27),  # put the CPlayerState pointer in r3
            li(r4, PlayerItemEnum.VariaSuit.value),
            li(r5, True),
            bl("CPlayerState::GetItemAmount"),
            # Convert the item count (at r3) to a float at f1
            *_convert_int_to_float_using_stack(
                version,
                r3,
                f2,
                f3,
            ),
            # Multiply the reduction by the item count and put the result at f30
            fmuls(f30, f1, f2),
        ],
        add_jump_at_end=True,
    )
