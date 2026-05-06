from __future__ import annotations

from typing import TYPE_CHECKING

from open_prime_rando.echoes.pickups import pickup_editing

if TYPE_CHECKING:
    from retro_data_structures.formats import Mlvl
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.echoes.pickups.schema import PickupModification
    from open_prime_rando.patcher_editor import PatcherEditor


def patch_pickup(
    editor: PatcherEditor, mlvl: Mlvl, area: Area, modification: PickupModification, disable_hud_popup: bool
) -> None:
    if modification.progressive_stages:
        pickup_editing.patch_complex_pickup(modification, editor, mlvl, area, disable_hud_popup)
    else:
        pickup_editing.patch_simple_pickup(modification, editor, mlvl, area, disable_hud_popup)
