import dataclasses
import functools
import logging
from open_prime_rando.echoes.dock_lock_rando.map_icons import DoorMapIcon
from open_prime_rando.patcher_editor import PatcherEditor
from open_prime_rando.echoes.asset_ids import *

from retro_data_structures.base_resource import AssetId
from retro_data_structures.properties.echoes.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.echoes.archetypes.WeaponVulnerability import WeaponVulnerability
from retro_data_structures.properties.echoes.core.Color import Color
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects.Dock import Dock
from retro_data_structures.properties.echoes.objects.Door import Door
from retro_data_structures.properties.echoes.objects.Actor import Actor
from retro_data_structures.properties.echoes.objects.MemoryRelay import MemoryRelay
from retro_data_structures.properties.echoes.objects.ScannableObjectInfo import ScannableObjectInfo
from retro_data_structures.formats.mapa import Mapa
from retro_data_structures.formats.mlvl import AreaWrapper
from retro_data_structures.formats.scan import Scan
from retro_data_structures.formats.strg import Strg
from retro_data_structures.formats.script_object import ScriptInstanceHelper, InstanceId


@dataclasses.dataclass(frozen=True)
class DoorType:
    name: str

    vulnerability: DamageVulnerability

    shell_model: AssetId
    shell_color: Color

    scan_text: tuple[str, ...] | None

    map_icon: DoorMapIcon

    def get_files(self, editor: PatcherEditor, world_name: str, area_name: str) -> tuple[AreaWrapper, Mapa]:
        world_file = world.load_dedicated_file(world_name)
        mrea = editor.get_area_helper(world.NAME_TO_ID_MLVL[world_name], world_file.NAME_TO_ID_MREA[area_name])
        mapa = editor.get_file(world_file.NAME_TO_ID_MAPA[area_name], type_hint=Mapa)
        return mrea, mapa
    
    def get_dock_index(self, world_name: str, area_name: str, dock_name: str) -> int:
        world_file = world.load_dedicated_file(world_name)
        return world_file.DOCK_NAMES[area_name][dock_name]
    
    def get_mrea(self, editor: PatcherEditor, world_name: str, area_name: str) -> AreaWrapper:
        return self.get_files(editor, world_name, area_name)[0]
    
    def get_door_from_dock_index(self, mrea: AreaWrapper, dock_index: int) -> ScriptInstanceHelper:
        dock = next(
            inst for inst in mrea.mrea.all_instances
            if (
                inst.type == Dock and
                inst.get_properties_as(Dock).dock_number == dock_index
            )
        )
        for instance in mrea.mrea.all_instances:
            if instance.type != Door:
                continue
            for connection in instance.connections:
                if dock.id_matches(connection.target):
                    return instance
        raise KeyError(f"no door found with a connection to {dock} in {mrea.name}")

    def patch_map_icon(self, mapa: Mapa, door: ScriptInstanceHelper):
        for obj in mapa.raw.mappable_objects:
            if door.id_matches(obj.editor_id):
                obj.type = self.map_icon.value
                return
    
    @staticmethod
    def get_scan_templates(editor: PatcherEditor) -> tuple[Scan, Strg]:
        scan = editor.get_parsed_asset(0x36DE1342, type_hint=Scan)
        strg = editor.get_parsed_asset(0x49DF4448, type_hint=Strg)
        return scan, strg

    def get_patched_scan(self, editor: PatcherEditor) -> AssetId:
        if (scan_id := editor.get_custom_asset(f"custom_door_{self.name}.SCAN")) is not None:
            return scan_id

        scan, strg = DoorType.get_scan_templates(editor)
        for i, text in enumerate(self.scan_text):
            strg.set_string(i, text)
        
        # TODO: choose paks dynamically
        strg_id = editor.add_file(f"custom_door_{self.name}.STRG", strg, editor.all_paks)
        
        scan_info = scan.scannable_object_info.get_properties_as(ScannableObjectInfo)
        scan_info.string = strg_id
        scan.scannable_object_info.set_properties(scan_info)

        # TODO: choose paks dynamically
        return editor.add_file(f"custom_door_{self.name}.SCAN", scan, editor.all_paks)

    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        mrea, mapa = self.get_files(editor, world_name, area_name)
        door = self.get_door_from_dock_index(mrea, self.get_dock_index(world_name, area_name, dock_name))
        self.patch_map_icon(mapa, door)

        door_props = door.get_properties_as(Door)
        door_props.shell_model = self.shell_model
        door_props.shell_color = self.shell_color
        door.set_properties(door_props)


@dataclasses.dataclass(frozen=True)
class NormalDoorType(DoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        super().patch_door(editor, world_name, area_name, dock_name)
        mrea = self.get_mrea(editor, world_name, area_name)
        door = self.get_door_from_dock_index(mrea, self.get_dock_index(world_name, area_name, dock_name))
        
        door_props = door.get_properties_as(Door)
        door_props.vulnerability = self.vulnerability

        # if self.scan_text is not None:
        #     door_props.alt_scannable.scannable_info0 = self.get_patched_scan(editor)
        
        door.set_properties(door_props)
    

@dataclasses.dataclass(frozen=True)
class BlastShieldDoorType(DoorType):
    shield_model: AssetId
    shield_collision_box: Vector
    shield_collision_offset: Vector
    
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        """
        blast shield connections:
            DEAD -> lock cleared MemoryRelay, ACTV
            DEAD -> lock breaking SoundEffect, PLAY
            DEAD -> lock explosion gibs, ACTV
            DEAD -> jingle streamedaudio, PLAY
        
        door connections:
            OPEN -> lock cleared MemoryRelay, ACTV
        
        memory relay connections:
            ACTV -> door, RSET
            ACTV -> blast shield, DCTV
        """
        raise NotImplementedError()
    

@dataclasses.dataclass(frozen=True)
class VanillaBlastShieldDoorType(BlastShieldDoorType):
    def remove_blast_shield(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        mrea = self.get_mrea(editor, world_name, area_name)
        door = self.get_door_from_dock_index(mrea, self.get_dock_index(world_name, area_name, dock_name))

        relay = None
        for connection in door.connections:
            if connection.state == "OPEN" and connection.message == "ACTV":
                target = mrea.get_instance(connection.target)
                if target.type != MemoryRelay:
                    continue
                relay = target
                break
        
        if relay is None:
            logging.warn(f"No MemoryRelay connected to {door} in {world_name}/{area_name}")
            return
        
        lock = None
        for connection in relay.connections:
            if connection.state == "ACTV" and connection.message == "DCTV":
                target = mrea.get_instance(connection.target)
                if target.type != Actor:
                    continue
                lock = target
                break
        
        if lock is None:
            logging.warn(f"No lock Actor connected to {relay} in {world_name}/{area_name}")
            return
        
        for connection in lock.connections:
            mrea.mrea.remove_instance(connection.target)
        mrea.mrea.remove_instance(lock)


@dataclasses.dataclass(frozen=True)
class SeekerBlastShieldDoorType(VanillaBlastShieldDoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        raise NotImplementedError()
    
    def remove_blast_shield(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        raise NotImplementedError()


@dataclasses.dataclass(frozen=True)
class PlanetaryEnergyDoorType(DoorType):
    planetary_energy_item_id: int

    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        raise NotImplementedError()


@dataclasses.dataclass(frozen=True)
class GrappleDoorType(BlastShieldDoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        raise NotImplementedError()


@dataclasses.dataclass(frozen=True)
class DarkVisorDoorType(BlastShieldDoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        raise NotImplementedError()


@dataclasses.dataclass(frozen=True)
class EchoVisorDoorType(BlastShieldDoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        raise NotImplementedError()


@dataclasses.dataclass(frozen=True)
class ScanVisorDoorType(BlastShieldDoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        raise NotImplementedError()


@dataclasses.dataclass(frozen=True)
class TranslatorDoorType(ScanVisorDoorType):
    translator_item_id: int

    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        raise NotImplementedError()
    