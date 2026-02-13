from __future__ import annotations

from typing import TYPE_CHECKING

from open_prime_rando.echoes.pickups import pickup_editing

if TYPE_CHECKING:
    from retro_data_structures.formats import Mapa
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.echoes.pickups.schema import PickupModification
    from open_prime_rando.patcher_editor import PatcherEditor


def patch_pickup(
    editor: PatcherEditor, modification: PickupModification, area: Area, mapa: Mapa, disable_hud_popup: bool
) -> None:
    if len(modification.stages) > 1:
        pickup_editing.patch_complex_pickup(modification, editor, area, mapa, disable_hud_popup)
    else:
        pickup_editing.patch_simple_pickup(modification, editor, area, mapa, disable_hud_popup)
