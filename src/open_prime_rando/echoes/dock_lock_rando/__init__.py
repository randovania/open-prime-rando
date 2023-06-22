from pathlib import Path

from construct import Container
from open_prime_rando.echoes.dock_lock_rando import dock_type
from open_prime_rando.echoes.dock_lock_rando.dock_type_database import DOCK_TYPES
from open_prime_rando.patcher_editor import PatcherEditor
from retro_data_structures.base_resource import AssetId, RawResource
from retro_data_structures.formats.cmdl import Cmdl
from retro_data_structures.game_check import Game


def add_custom_models(editor: PatcherEditor):
    assets = Path(__file__).parent.parent.joinpath("custom_assets", "doors")
    def get_txtr(n: str) -> AssetId:
        res = RawResource(
            type="TXTR",
            data=assets.joinpath(f"{n}.TXTR").read_bytes()
        )
        return editor.add_file(f"{n}.TXTR", res, [])

    emissive = get_txtr("custom_door_lock_greyscale_emissive")
    template = editor.get_parsed_asset(0xF115F575, type_hint=Cmdl)

    for name in ("darkburst", "sunburst", "sonicboom"):
        txtr = get_txtr(f"custom_door_lock_{name}")
        cmdl = Container(template.raw)
        cmdl.material_sets[0].texture_file_ids[0] = txtr
        cmdl.material_sets[0].texture_file_ids[1] = emissive
        editor.add_file(f"custom_door_lock_{name}.CMDL", Cmdl(cmdl, Game.ECHOES, editor), [])


def apply_door_rando(editor: PatcherEditor, world_name: str, area_name: str, dock_name: str,
                     new_door_type: str, old_door_type: str | None, low_memory: bool):
    if old_door_type is not None:
        old_door = DOCK_TYPES[old_door_type]

        if isinstance(old_door, dock_type.VanillaBlastShieldDoorType):
            old_door.remove_blast_shield(editor, world_name, area_name, dock_name)

    new_door = DOCK_TYPES[new_door_type]
    new_door.patch_door(editor, world_name, area_name, dock_name, low_memory)
