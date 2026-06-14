from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from retro_data_structures.formats import Mapu
from retro_data_structures.transform import Transform

if TYPE_CHECKING:
    from retro_data_structures.base_resource import AssetId

    from open_prime_rando.patcher_editor import PatcherEditor


def get_original_mapu_transforms(editor: PatcherEditor) -> dict[AssetId, Transform]:
    mapu = editor.get_file(0xA2D85F5B, Mapu)
    return {world.mlvl: world.transform for world in mapu.worlds}


def move_world_in_mapu(
    editor: PatcherEditor,
    mlvl_id: AssetId,
    world_to_copy: AssetId,
    original_transforms: dict[AssetId, Transform],
) -> None:
    """
    Moves a world in the MAPU from its original transform,
    to the original transform of another world in the MAPU.
    """
    mapu = editor.get_file(0xA2D85F5B, Mapu)

    world = next(world for world in mapu.worlds if world.mlvl == mlvl_id)
    world.transform = original_transforms[world_to_copy]

    world_z_offset: float = (original_transforms[mlvl_id] / original_transforms[world_to_copy])._data[2, 3]

    def without_z_translation(trans: Transform) -> Transform:
        arr = np.asarray(trans, copy=True)
        arr[2, 3] = 0.0
        return Transform(arr)

    def adjust_hexagon(hexagon: Transform) -> Transform:
        old_trans = without_z_translation(original_transforms[mlvl_id])
        new_trans = without_z_translation(original_transforms[world_to_copy])

        zscale: float = hexagon._data[2, 2]
        z_translation = Transform.translation(0.0, 0.0, -world_z_offset / zscale)

        return hexagon / old_trans @ new_trans @ z_translation

    world.hexagon_transforms = [adjust_hexagon(hexagon) for hexagon in world.hexagon_transforms]
