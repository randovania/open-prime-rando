from __future__ import annotations

from typing import TYPE_CHECKING

import pydantic
from pydantic import Field
from retro_data_structures.enums.echoes import PlayerItemEnum

from open_prime_rando.echoes.custom_items import defense_up, massive_damage

if TYPE_CHECKING:
    from collections.abc import Iterable

    from open_prime_rando.dol_patching.code_cave_tracker import CodeCaveTracker
    from open_prime_rando.dol_patching.echoes.dol_patches import EchoesDolVersion
    from open_prime_rando.patcher_editor import PatcherEditor


class CustomItemsConfig(pydantic.BaseModel):
    """
    Parameters for fine adjustments of our custom items.
    """

    massive_damage_config: massive_damage.MassiveDamageConfig = Field(
        default_factory=massive_damage.MassiveDamageConfig
    )

    defense_up_config: defense_up.DefenseUpConfig = Field(default_factory=defense_up.DefenseUpConfig)


def apply_changes(version: EchoesDolVersion, editor: PatcherEditor, config: CustomItemsConfig) -> None:
    """
    Makes the necessary changes for our custom items to work.
    """
    massive_damage.apply_dol_patches(version, editor.code_cave, config.massive_damage_config)
    defense_up.apply_patches(version, editor, config.defense_up_config)

    _persist_inventory_items(
        version,
        editor.code_cave,
        [
            PlayerItemEnum.PersistentCounter5,  # Temporary Missile
            PlayerItemEnum.PersistentCounter6,  # Temporary Power Bomb
            PlayerItemEnum.PersistentCounter7,  # Missile Launcher
            # PlayerItemEnum.PersistentCounter8, # Multiworld magic
            PlayerItemEnum.AmpDamage,
            PlayerItemEnum.UnlimitedBeamAmmo,
            PlayerItemEnum.UnlimitedMissiles,
        ],
    )


def _persist_inventory_items(
    version: EchoesDolVersion, cave: CodeCaveTracker, items_to_persist: Iterable[PlayerItemEnum]
) -> None:
    """
    Marks the provided items so that they're saved to the memory card.
    """
    for item in items_to_persist:
        cave.dol_editor.write(version.powerup_should_persist + item.value, b"\x01")
