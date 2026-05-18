from __future__ import annotations

from typing import TYPE_CHECKING

import pydantic
from retro_data_structures.properties.echoes.objects import TweakPlayer

from open_prime_rando.dol_patching import all_prime_dol_patches
from open_prime_rando.dol_patching.echoes import dol_patches

if TYPE_CHECKING:
    from open_prime_rando.dol_patching.echoes.dol_patches import EchoesDolVersion
    from open_prime_rando.patcher_editor import PatcherEditor


class DamageChanges(pydantic.BaseModel):
    """Set of changes related to damage and health."""

    energy_per_tank: int = 100
    """How much energy you get per energy tank. Also controls starting energy."""

    safe_zone_heal_per_second: float = 1.0
    """How much energy a safe zone heals per second."""

    dangerous_energy_tanks: bool = False
    """When enabled, collecting an energy tank leaves you at 1 energy instead of healing."""

    dark_world_damage: float = 6.0
    """How much damage Dark Aether causes per second."""

    dark_suit_protection: float = 0.2
    """With Dark Suit, take only this percentage of the dark world damage."""


def apply_damage_changes(editor: PatcherEditor, damage_changes: DamageChanges, version: EchoesDolVersion) -> None:
    """Applies all changes related to damage and health."""

    all_prime_dol_patches.apply_energy_tank_capacity_patch(
        version.health_capacity,
        damage_changes.energy_per_tank,
        editor.dol,
    )
    dol_patches.apply_safe_zone_heal_patch(
        version.safe_zone,
        version.sda2_base,
        damage_changes.safe_zone_heal_per_second,
        editor.dol,
    )
    all_prime_dol_patches.apply_reverse_energy_tank_heal_patch(
        version.sda2_base,
        version.dangerous_energy_tank,
        damage_changes.dangerous_energy_tanks,
        version.game,
        editor.dol,
    )

    with editor.edit_tweak(TweakPlayer) as tweak:
        tweak.dark_world.damage_per_second.di_damage = damage_changes.dark_world_damage / 60.0
        tweak.dark_world.dark_suit_damage_reduction = damage_changes.dark_suit_protection
