from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

from pydantic import BaseModel
from retro_data_structures.base_resource import AssetId, RawResource
from retro_data_structures.formats.mlvl import Mlvl

from open_prime_rando.echoes.asset_ids import world
from open_prime_rando.echoes.custom_assets import custom_asset_path
from open_prime_rando.echoes.dock_lock_rando import dock_type
from open_prime_rando.echoes.dock_lock_rando.dock_type_database import DOCK_TYPES, DockTypeByName

if TYPE_CHECKING:
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.patcher_editor import PatcherEditor


def add_custom_models(editor: PatcherEditor) -> None:
    assets = custom_asset_path().joinpath("doors")

    @overload
    def get_txtr(n: str, must_exist: Literal[True] = ...) -> AssetId: ...
    @overload
    def get_txtr(n: str, must_exist: Literal[False]) -> AssetId | None: ...
    def get_txtr(n: str, must_exist: bool = True) -> AssetId | None:
        f = assets.joinpath(n)
        if not must_exist and not f.exists():
            return None
        res = RawResource(type="TXTR", raw_data=f.read_bytes())
        return editor.add_new_asset(n, res)

    greyscale_emissive = get_txtr("custom_door_lock_greyscale_emissive.TXTR")

    for door_type in DOCK_TYPES.values():
        if not (isinstance(door_type, dock_type.BlastShieldDoorType) and isinstance(door_type.shield_model, str)):
            continue
        name = door_type.shield_model
        txtr = get_txtr(f"custom_door_lock_{name}.TXTR")
        emissive = get_txtr(f"custom_door_lock_{name}_emissive.TXTR", must_exist=False)
        if emissive is None:
            emissive = greyscale_emissive

        cmdl_id = editor.duplicate_asset(0xF115F575, f"custom_door_lock_{name}.CMDL")
        cmdl = editor.get_file(cmdl_id)

        cmdl.raw.material_sets[0].texture_file_ids[0] = txtr
        cmdl.raw.material_sets[0].texture_file_ids[1] = emissive


def apply_door_rando_legacy(
    editor: PatcherEditor,
    world_name: str,
    area_name: str,
    dock_name: str,
    new_door_type: str,
    old_door_type: str | None,
    low_memory: bool,
) -> None:
    """Change a door from having one lock type to another. Used by the legacy patcher."""

    world_file = world.load_dedicated_file(world_name)
    mlvl_id = world.NAME_TO_ID_MLVL[world_name]

    mlvl = editor.get_file(mlvl_id, Mlvl)
    area = editor.get_area(mlvl_id, world_file.NAME_TO_ID_MREA[area_name])

    if old_door_type is not None:
        old_door = DOCK_TYPES[old_door_type]

        if isinstance(old_door, dock_type.VanillaBlastShieldDoorType):
            old_door.remove_blast_shield(editor, mlvl, area, dock_name)

    new_door = DOCK_TYPES[new_door_type]
    new_door.patch_door(editor, mlvl, area, dock_name, low_memory)


def apply_door_rando(
    editor: PatcherEditor,
    mlvl: Mlvl,
    area: Area,
    change: DockTypeChange,
) -> None:
    """Change a door from having one lock type to another."""

    if isinstance(change.old_door_type, dock_type.VanillaBlastShieldDoorType):
        change.old_door_type.remove_blast_shield(editor, mlvl, area, change.dock_name)

    change.new_door_type.patch_door(editor, mlvl, area, change.dock_name, low_memory=False)


class DockTypeChange(BaseModel):
    """Contains changes for a dock type."""

    dock_name: str

    old_door_type: DockTypeByName
    new_door_type: DockTypeByName
