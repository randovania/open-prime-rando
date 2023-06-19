import dataclasses
import functools
import logging
from open_prime_rando.echoes.dock_lock_rando.map_icons import DoorMapIcon
from open_prime_rando.patcher_editor import PatcherEditor
from open_prime_rando.echoes.asset_ids import *

from retro_data_structures.base_resource import AssetId
from retro_data_structures.asset_manager import NameOrAssetId
from retro_data_structures.properties.echoes.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.echoes.archetypes.WeaponVulnerability import WeaponVulnerability
from retro_data_structures.properties.echoes.core.Color import Color
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects.Dock import Dock
from retro_data_structures.properties.echoes.objects.Door import Door
from retro_data_structures.properties.echoes.objects.Actor import Actor
from retro_data_structures.properties.echoes.objects.MemoryRelay import MemoryRelay
from retro_data_structures.properties.echoes.objects.ScannableObjectInfo import ScannableObjectInfo
from retro_data_structures.properties.echoes.objects.Sound import Sound
from retro_data_structures.properties.echoes.objects.StreamedAudio import StreamedAudio
from retro_data_structures.properties.echoes.objects.MemoryRelay import MemoryRelay
from retro_data_structures.properties.echoes.objects.Effect import Effect
from retro_data_structures.properties.echoes.core.Spline import Spline
from retro_data_structures.formats.mapa import Mapa
from retro_data_structures.formats.mlvl import AreaWrapper
from retro_data_structures.formats.scan import Scan
from retro_data_structures.formats.strg import Strg
from retro_data_structures.formats.script_object import ScriptInstanceHelper, InstanceId


@dataclasses.dataclass(kw_only=True)
class DoorType:
    name: str

    vulnerability: DamageVulnerability

    shell_model: NameOrAssetId = 0x6B78FD92
    shell_color: Color

    scan_text: tuple[str, ...] | None = None

    map_icon: DoorMapIcon

    patched_scan: AssetId | None = None

    def get_paks(self, editor: PatcherEditor, world_name: str, area_name: str):
        world_file = world.load_dedicated_file(world_name)
        return editor.find_paks(world_file.NAME_TO_ID_MREA[area_name])

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

    def get_patched_scan(self, editor: PatcherEditor, world_name: str, area_name: str) -> AssetId:
        paks = self.get_paks(editor, world_name, area_name)
        if self.patched_scan is None or not editor.does_asset_exists(self.patched_scan):
            scan, strg = DoorType.get_scan_templates(editor)
            for i, text in enumerate(self.scan_text):
                strg.set_string(i, text)
            
            strg_id = editor.add_or_replace_custom_asset(f"custom_door_{self.name}.STRG", strg, paks)

            scan_info = scan.scannable_object_info.get_properties_as(ScannableObjectInfo)
            scan_info.string = strg_id
            scan.scannable_object_info.set_properties(scan_info)

            scan_id = editor.add_or_replace_custom_asset(f"custom_door_{self.name}.SCAN", scan, paks)
            self.patched_scan = scan_id
        
        for pak in paks:
            editor.ensure_present(pak, self.patched_scan)
        return self.patched_scan

    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        mrea, mapa = self.get_files(editor, world_name, area_name)
        door = self.get_door_from_dock_index(mrea, self.get_dock_index(world_name, area_name, dock_name))
        self.patch_map_icon(mapa, door)

        shell_model = editor._resolve_asset_id(self.shell_model)

        door_props = door.get_properties_as(Door)
        door_props.shell_model = shell_model
        door_props.shell_color = self.shell_color
        door.set_properties(door_props)

        for pak in self.get_paks(editor, world_name, area_name):
            editor.ensure_present(pak, shell_model)


@dataclasses.dataclass(kw_only=True)
class NormalDoorType(DoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        super().patch_door(editor, world_name, area_name, dock_name)
        mrea = self.get_mrea(editor, world_name, area_name)
        door = self.get_door_from_dock_index(mrea, self.get_dock_index(world_name, area_name, dock_name))
        
        door_props = door.get_properties_as(Door)
        door_props.vulnerability = self.vulnerability

        if self.scan_text is not None:
            door_props.alt_scannable.scannable_info0 = self.get_patched_scan(editor, world_name, area_name)
        
        door.set_properties(door_props)
    

@dataclasses.dataclass(kw_only=True)
class BlastShieldDoorType(DoorType):
    shield_model: NameOrAssetId
    shield_collision_box: Vector = dataclasses.field(default_factory=lambda: Vector(0.35, 5.0, 4.0))
    shield_collision_offset: Vector = dataclasses.field(default_factory=lambda: Vector(-2/3, 0, 2.0))
    
    def get_spline(editor: PatcherEditor) -> Spline:
        return Spline(data=b'\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x02\x02A \x00\x00?\x80\x00\x00\x02\x02\x01\x00\x00\x00\x00?\x80\x00\x00')

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
        super().patch_door(editor, world_name, area_name, dock_name)
        mrea = self.get_mrea(editor, world_name, area_name)
        _door = self.get_door_from_dock_index(mrea, self.get_dock_index(world_name, area_name, dock_name))
        door = _door.get_properties_as(Door)

        default = mrea.get_layer("Default")
        
        _sound = default.add_instance("SOND", "Metal Door Lock Breaking")
        sound = _sound.get_properties_as(Sound)
        sound.editor_properties.transform = door.editor_properties.transform
        sound.sound = 948
        sound.max_audible_distance = 150.0
        sound.surround_pan.surround_pan = 1.0
        _sound.set_properties(sound)

        _streamed = default.add_instance("STAU", "StreamedAudio - Event Jingle")
        streamed = _streamed.get_properties_as(StreamedAudio)
        streamed.editor_properties.transform = door.editor_properties.transform
        streamed.song_file = "/audio/evt_x_event_00.dsp"
        streamed.fade_in_time = 0.01
        streamed.volume = 65
        streamed.software_channel = 1
        streamed.unknown = False
        _streamed.set_properties(streamed)

        _relay = default.add_memory_relay("Lock Cleared")
        relay = _relay.get_properties_as(MemoryRelay)
        relay.editor_properties.transform = door.editor_properties.transform
        relay.editor_properties.active = False
        _relay.set_properties(relay)

        _gibs = default.add_instance("EFCT", "Missile Lock Explosion Gibs")
        gibs = _gibs.get_properties_as(Effect)
        gibs.editor_properties.transform = door.editor_properties.transform
        gibs.editor_properties.active = False
        gibs.particle_effect = 0xCDCBDF04
        gibs.restart_on_activate = True
        gibs.motion_control_spline = BlastShieldDoorType.get_spline(editor)
        _gibs.set_properties(gibs)

        model = editor._resolve_asset_id(self.shield_model)

        _lock = default.add_instance("ACTR", "Blast Shield Lock")
        lock = _lock.get_properties_as(Actor)
        lock.editor_properties.transform = door.editor_properties.transform
        lock.collision_box = self.shield_collision_box
        lock.collision_offset = self.shield_collision_offset
        lock.vulnerability = self.vulnerability
        lock.model = model
        lock.actor_information.scannable.scannable_info0 = self.get_patched_scan(editor, world_name, area_name)
        _lock.set_properties(lock)

        _lock.add_connection("DEAD", "PLAY", _sound)
        _lock.add_connection("DEAD", "PLAY", _streamed)
        # _lock.add_connection("DEAD", "ACTV", _gibs)
        _lock.add_connection("DEAD", "ACTV", _relay)

        _relay.add_connection("ACTV", "DCTV", _lock)
        _relay.add_connection("ACTV", "RSET", _door)

        _door.add_connection("OPEN", "ACTV", _relay)

        for pak in self.get_paks(editor, world_name, area_name):
            for asset in (
                model,
                0x8B4CD966, # MetalDoorLockBreak AGSC
                0xCDCBDF04  # gibs PART
            ):
                editor.ensure_present(pak, asset)

    

@dataclasses.dataclass(kw_only=True)
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


@dataclasses.dataclass(kw_only=True)
class SeekerBlastShieldDoorType(VanillaBlastShieldDoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        raise NotImplementedError()
    
    def remove_blast_shield(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        raise NotImplementedError()


@dataclasses.dataclass(kw_only=True)
class PlanetaryEnergyDoorType(DoorType):
    planetary_energy_item_id: int

    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        raise NotImplementedError()


@dataclasses.dataclass(kw_only=True)
class GrappleDoorType(BlastShieldDoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        raise NotImplementedError()


@dataclasses.dataclass(kw_only=True)
class DarkVisorDoorType(BlastShieldDoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        raise NotImplementedError()


@dataclasses.dataclass(kw_only=True)
class EchoVisorDoorType(BlastShieldDoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        raise NotImplementedError()


@dataclasses.dataclass(kw_only=True)
class ScanVisorDoorType(BlastShieldDoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        raise NotImplementedError()


@dataclasses.dataclass(kw_only=True)
class TranslatorDoorType(ScanVisorDoorType):
    translator_item_id: int

    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        raise NotImplementedError()
    