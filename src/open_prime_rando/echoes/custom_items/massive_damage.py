from __future__ import annotations

import struct
from typing import TYPE_CHECKING, Annotated

import pydantic
from annotated_types import Interval
from ppc_asm.assembler.ppc import (
    b,
    f0,
    f1,
    f2,
    fadds,
    fmuls,
    fsubs,
    lfd,
    lfs,
    lis,
    r0,
    r1,
    r2,
    r3,
    stw,
)
from retro_data_structures.enums.echoes import PlayerItemEnum

from open_prime_rando.dol_patching.all_prime_dol_patches import r31

if TYPE_CHECKING:
    from open_prime_rando.dol_patching.code_cave_tracker import CodeCaveTracker
    from open_prime_rando.dol_patching.echoes.dol_patches import EchoesDolVersion


class MassiveDamageConfig(pydantic.BaseModel):
    """Control how strong Massive Damage is and how many copies you can have."""

    damage_multiplier: float = 1.0
    max_count: Annotated[int, Interval(ge=1, le=255)] = 1


def apply_dol_patches(version: EchoesDolVersion, cave: CodeCaveTracker, config: MassiveDamageConfig) -> None:
    """
    Patches Massive Damage to scale the damage multiplier by how many copies of it you have.
    Also changes how much each copy gives, allows you to have multiple and so it persists on save.
    """

    # it's the 15th instruction
    cave.dol_editor.symbols["CDamageInfo::ApplyDoubleDamage"] = version.apply_double_damage_address
    load_float_offset = 0x8018A0CC - 0x8018A098

    return_address = version.apply_double_damage_address + load_float_offset + 4

    # Change the 2.0 double with the requested multiplier
    cave.dol_editor.write(
        version.apply_double_damage_float,
        struct.pack(
            ">f",
            config.damage_multiplier,
        ),
    )

    # Mark Massive Damage as a pickup to persist
    cave.dol_editor.write(version.powerup_should_persist + PlayerItemEnum.AmpDamage.value, b"\x01")

    # Adjust the max capacity of Massive Damage
    cave.dol_editor.write(version.powerup_max + PlayerItemEnum.AmpDamage.value * 4, struct.pack(">l", config.max_count))

    def with_cave(code_cave_address: int) -> None:
        cave.dol_editor.write_instructions(
            ("CDamageInfo::ApplyDoubleDamage", load_float_offset),
            [
                b(code_cave_address),  # replace the load 2.0 with our code cave that puts the multiplier at f0
                lfs(f1, 0x4, r31),  # swap this instruction to come after, to not be clobbered
            ],
        )

    cave.request_cave_for(
        [
            # Convert the item count (at r3) to a float at f1
            # this conversion must involve the memory, so we use the stack below r1 since we're not calling anything
            lis(r0, 0x4330),  # load upper half of double constant
            stw(r0, -0x8, r1),
            stw(r3, -0x4, r1),
            lfd(f1, -0x8, r1),  # load as double
            lfd(f2, (version.fp_unsigned_bias - version.sda2_base), r2),  # load the bias constant
            fsubs(f1, f1, f2),  # subtract bias constant
            # Load the float with the per count multiplier
            lfs(f0, (version.apply_double_damage_float - version.sda2_base), r2),
            # Multiply the base multiplier by the item count and put the result at f0
            fmuls(f0, f0, f1),
            # Load 1.0 to f1. Conveniently it's just after our float!
            lfs(f1, (version.apply_double_damage_float + 4 - version.sda2_base), r2),
            fadds(f0, f0, f1),
            # Go back to ApplyDoubleDamage
            b(return_address),
        ],
        with_cave,
    )
