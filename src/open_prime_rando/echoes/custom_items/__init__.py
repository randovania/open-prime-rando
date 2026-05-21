from __future__ import annotations

from typing import TYPE_CHECKING

import pydantic
from pydantic import Field

from open_prime_rando.echoes.custom_items import massive_damage

if TYPE_CHECKING:
    from open_prime_rando.dol_patching.code_cave_tracker import CodeCaveTracker
    from open_prime_rando.dol_patching.echoes.dol_patches import EchoesDolVersion


class CustomItemsConfig(pydantic.BaseModel):
    """
    Parameters for fine adjustments of our custom items.
    """

    massive_damage_config: massive_damage.MassiveDamageConfig = Field(
        default_factory=massive_damage.MassiveDamageConfig
    )


def apply_changes(version: EchoesDolVersion, cave: CodeCaveTracker, config: CustomItemsConfig) -> None:
    """
    Makes the necessary changes for our custom items to work.
    """
    cave.add_task(massive_damage.apply_dol_patches(version, cave, config.massive_damage_config))
