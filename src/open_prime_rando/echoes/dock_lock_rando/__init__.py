from pathlib import Path

from construct import Container
from retro_data_structures.base_resource import AssetId, RawResource
from retro_data_structures.formats.cmdl import Cmdl
from retro_data_structures.game_check import Game

from open_prime_rando.echoes.dock_lock_rando import dock_type
from open_prime_rando.echoes.dock_lock_rando.dock_type_database import DOCK_TYPES
from open_prime_rando.patcher_editor import PatcherEditor


def add_custom_models(editor: PatcherEditor):
    assets = Path(__file__).parent.parent.joinpath("custom_assets", "doors")
    def get_txtr(n: str, must_exist: bool = True) -> AssetId:
        f = assets.joinpath(n)
        if not must_exist and not f.exists():
            return None
        res = RawResource(
            type="TXTR",
            data=f.read_bytes()
        )
        return editor.add_file(n, res)

    greyscale_emissive = get_txtr("custom_door_lock_greyscale_emissive.TXTR")
    template = editor.get_parsed_asset(0xF115F575, type_hint=Cmdl)

    for door_type in DOCK_TYPES.values():
        if not (
            isinstance(door_type, dock_type.BlastShieldDoorType)
            and isinstance(door_type.shield_model, str)
        ):
            continue
        name = door_type.shield_model
        txtr = get_txtr(f"custom_door_lock_{name}.TXTR")
        emissive = get_txtr(f"custom_door_lock_{name}_emissive.TXTR", must_exist=False)
        if emissive is None:
            emissive = greyscale_emissive

        cmdl = Container(template.raw)
        cmdl.material_sets[0].texture_file_ids[0] = txtr
        cmdl.material_sets[0].texture_file_ids[1] = emissive
        editor.add_file(f"custom_door_lock_{name}.CMDL", Cmdl(cmdl, Game.ECHOES, editor))


def apply_door_rando(editor: PatcherEditor, world_name: str, area_name: str, dock_name: str,
                     new_door_type: str, old_door_type: str | None, low_memory: bool):
    if old_door_type is not None:
        old_door = DOCK_TYPES[old_door_type]

        if isinstance(old_door, dock_type.VanillaBlastShieldDoorType):
            old_door.remove_blast_shield(editor, world_name, area_name, dock_name)

    new_door = DOCK_TYPES[new_door_type]
    new_door.patch_door(editor, world_name, area_name, dock_name, low_memory)
