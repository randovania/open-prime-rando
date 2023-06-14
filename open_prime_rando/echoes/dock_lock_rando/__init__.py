from open_prime_rando.echoes.dock_lock_rando.dock_type import *
from open_prime_rando.echoes.dock_lock_rando.dock_type_database import DOCK_TYPES
from open_prime_rando.patcher_editor import PatcherEditor


def apply_door_rando(editor: PatcherEditor, world_name: str, area_name: str, dock_name: str, new_door_type: str, old_door_type: str | None):
    if old_door_type is not None:
        old_door = DOCK_TYPES[old_door_type]

        if isinstance(old_door, VanillaBlastShieldDoorType):
            old_door.remove_blast_shield(editor, world_name, area_name, dock_name)
    
    new_door = DOCK_TYPES[new_door_type]
    new_door.patch_door(editor, world_name, area_name, dock_name)
