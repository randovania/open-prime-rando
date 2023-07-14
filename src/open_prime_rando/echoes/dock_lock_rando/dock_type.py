import dataclasses

from retro_data_structures.asset_manager import NameOrAssetId
from retro_data_structures.base_resource import AssetId
from retro_data_structures.enums.echoes import Message, State, VisorFlags
from retro_data_structures.formats.mapa import Mapa
from retro_data_structures.formats.mrea import Area
from retro_data_structures.formats.scan import Scan
from retro_data_structures.formats.script_object import ScriptInstance
from retro_data_structures.formats.strg import Strg
from retro_data_structures.properties.base_property import BaseObjectType
from retro_data_structures.properties.echoes.archetypes.ActorParameters import ActorParameters
from retro_data_structures.properties.echoes.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.HealthInfo import HealthInfo
from retro_data_structures.properties.echoes.archetypes.ScannableParameters import ScannableParameters
from retro_data_structures.properties.echoes.archetypes.SurroundPan import SurroundPan
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.archetypes.VisorParameters import VisorParameters
from retro_data_structures.properties.echoes.archetypes.WeaponVulnerability import WeaponVulnerability
from retro_data_structures.properties.echoes.core.Color import Color
from retro_data_structures.properties.echoes.core.Spline import Spline
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects.Actor import Actor
from retro_data_structures.properties.echoes.objects.CameraShaker import CameraShaker
from retro_data_structures.properties.echoes.objects.Counter import Counter
from retro_data_structures.properties.echoes.objects.DamageableTrigger import DamageableTrigger
from retro_data_structures.properties.echoes.objects.DamageableTriggerOrientated import DamageableTriggerOrientated
from retro_data_structures.properties.echoes.objects.Dock import Dock
from retro_data_structures.properties.echoes.objects.Door import Door
from retro_data_structures.properties.echoes.objects.Effect import Effect
from retro_data_structures.properties.echoes.objects.HUDHint import HUDHint
from retro_data_structures.properties.echoes.objects.MemoryRelay import MemoryRelay
from retro_data_structures.properties.echoes.objects.PlayerController import PlayerController
from retro_data_structures.properties.echoes.objects.Relay import Relay
from retro_data_structures.properties.echoes.objects.ScannableObjectInfo import ScannableObjectInfo
from retro_data_structures.properties.echoes.objects.Sound import Sound
from retro_data_structures.properties.echoes.objects.StreamedAudio import StreamedAudio
from retro_data_structures.properties.echoes.objects.Timer import Timer

from open_prime_rando.echoes.asset_ids import world
from open_prime_rando.echoes.dock_lock_rando.map_icons import DoorMapIcon
from open_prime_rando.echoes.vulnerabilities import resist_all_vuln
from open_prime_rando.patcher_editor import PatcherEditor


@dataclasses.dataclass(kw_only=True)
class DoorType:
    name: str

    vulnerability: DamageVulnerability

    shell_model: NameOrAssetId = 0x6B78FD92  # normal door model
    shell_color: Color

    scan_text: tuple[str, ...] | None = None

    map_icon: DoorMapIcon

    patched_scan: AssetId | None = None

    def get_files(self, editor: PatcherEditor, world_name: str, area_name: str) -> tuple[Area, Mapa]:
        world_file = world.load_dedicated_file(world_name)
        area = editor.get_area(world.NAME_TO_ID_MLVL[world_name], world_file.NAME_TO_ID_MREA[area_name])
        mapa = editor.get_file(world_file.NAME_TO_ID_MAPA[area_name], type_hint=Mapa)
        return area, mapa

    def get_dock_index(self, world_name: str, area_name: str, dock_name: str) -> int:
        world_file = world.load_dedicated_file(world_name)
        return world_file.DOCK_NAMES[area_name][dock_name]

    def get_area(self, editor: PatcherEditor, world_name: str, area_name: str) -> Area:
        return self.get_files(editor, world_name, area_name)[0]

    def get_door_from_dock_index(self, area: Area, dock_index: int) -> ScriptInstance:
        dock = next(
            inst for inst in area.all_instances
            if (
                    inst.type == Dock and
                    inst.get_properties_as(Dock).dock_number == dock_index
            )
        )
        for instance in area.all_instances:
            if instance.type != Door:
                continue
            for connection in instance.connections:
                if dock.id_matches(connection.target):
                    return instance
        raise KeyError(f"no door found with a connection to {dock} in {area.name}")

    def patch_map_icon(self, mapa: Mapa, door: ScriptInstance):
        for obj in mapa.raw.mappable_objects:
            if door.id_matches(obj.editor_id):
                obj.type = self.map_icon.value
                return

    @staticmethod
    def get_scan_templates(editor: PatcherEditor) -> tuple[Scan, Strg]:
        # Uncategorized/There is a Blast Shield on the door blocking acces_0.SCAN
        scan = editor.get_parsed_asset(0x36DE1342, type_hint=Scan)
        # Strings/Uncategorized/There is a Blast Shield on the door blocking acces_0_0.STRG
        strg = editor.get_parsed_asset(0x49DF4448, type_hint=Strg)
        return scan, strg

    def get_patched_scan(self, editor: PatcherEditor, world_name: str, area_name: str) -> AssetId:
        if self.patched_scan is None or not editor.does_asset_exists(self.patched_scan):
            scan, strg = DoorType.get_scan_templates(editor)
            for i, text in enumerate(self.scan_text):
                strg.set_string(i, text)

            strg_id = editor.add_or_replace_custom_asset(f"custom_door_{self.name}.STRG", strg)

            with scan.scannable_object_info.edit_properties(ScannableObjectInfo) as scan_info:
                scan_info.string = strg_id

            scan_id = editor.add_or_replace_custom_asset(f"custom_door_{self.name}.SCAN", scan)
            self.patched_scan = scan_id

        return self.patched_scan

    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str, low_memory: bool):
        area, mapa = self.get_files(editor, world_name, area_name)
        door = self.get_door_from_dock_index(area, self.get_dock_index(world_name, area_name, dock_name))
        self.patch_map_icon(mapa, door)

        shell_model = editor._resolve_asset_id(self.shell_model)

        with door.edit_properties(Door) as door_props:
            door_props.shell_model = shell_model
            door_props.shell_color = self.shell_color
            if self.scan_text is not None:
                door_props.alt_scannable.scannable_info0 = self.get_patched_scan(editor, world_name, area_name)
            else:
                door_props.alt_scannable.scannable_info0 = 0xFFFFFFFF


@dataclasses.dataclass(kw_only=True)
class NormalDoorType(DoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str, low_memory: bool):
        super().patch_door(editor, world_name, area_name, dock_name, low_memory)
        area = self.get_area(editor, world_name, area_name)
        door = self.get_door_from_dock_index(area, self.get_dock_index(world_name, area_name, dock_name))

        with door.edit_properties(Door) as door_props:
            door_props.vulnerability = self.vulnerability

@dataclasses.dataclass
class BlastShieldActors:
    door: ScriptInstance
    sound: ScriptInstance | None
    streamed: ScriptInstance | None
    lock: ScriptInstance
    relay: ScriptInstance
    gibs: ScriptInstance | None


@dataclasses.dataclass(kw_only=True)
class BlastShieldDoorType(DoorType):
    shield_model: NameOrAssetId
    shield_collision_box: Vector = dataclasses.field(default_factory=lambda: Vector(0.35, 5.0, 4.0))
    shield_collision_offset: Vector = dataclasses.field(default_factory=lambda: Vector(-2 / 3, 0, 2.0))

    def find_attached_instance(
            self, area: Area, source: ScriptInstance, state: State, message: Message,
            target_type: type[BaseObjectType], target_name: str | None = None
    ) -> ScriptInstance:
        for connection in source.connections:
            if connection.state == state and connection.message == message:
                target = area.get_instance(connection.target)
                if target.type == target_type and (target_name is None or target.name == target_name):
                    return target
        name = f"{target_type} named {target_name}" if target_name is not None else str(target_type)
        raise TypeError(f"No {name} connected to {source}")

    def get_spline(self) -> Spline:
        return Spline(
            data=b'\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x02'
                 b'\x02A \x00\x00?\x80\x00\x00\x02\x02\x01\x00\x00\x00\x00?\x80\x00\x00'
        )

    def create_trigger(self,
                       name: str,
                       door_xfm: Transform,
                       health: float,
                       visor_flags: VisorFlags = VisorFlags.Combat | VisorFlags.Dark,
                       active: bool = True,
                       seeker_lock_on: bool = True,
                       orbitable: bool = False,
    ):
        pos = Vector(
            door_xfm.position.x,
            door_xfm.position.y,
            door_xfm.position.z + 1.8
        )

        return DamageableTriggerOrientated(
            editor_properties=EditorProperties(
                name=name,
                transform=Transform(
                    position=pos,
                    rotation=door_xfm.rotation,
                    scale=Vector(4.0, 4.0, 1.5)
                ),
                active=active
            ),
            health=HealthInfo(health=health),
            vulnerability=self.vulnerability,
            enable_seeker_lock_on=seeker_lock_on,
            orbitable=orbitable,
            visor=VisorParameters(
                visor_flags=visor_flags
            )
        )

    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str, low_memory: bool):
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
        super().patch_door(editor, world_name, area_name, dock_name, low_memory)
        area = self.get_area(editor, world_name, area_name)
        door = self.get_door_from_dock_index(area, self.get_dock_index(world_name, area_name, dock_name))

        with door.edit_properties(Door) as _door:
            door_transform = _door.editor_properties.transform
            _door.vulnerability = resist_all_vuln

        default = area.get_layer("Default")

        shield_model = self.shield_model
        if isinstance(shield_model, str):
            shield_model = f"custom_door_lock_{shield_model}.CMDL"
        model = editor._resolve_asset_id(shield_model)

        lock = default.add_instance_with(Actor(
            editor_properties=EditorProperties(
                name=f"{self.name} Blast Shield Lock",
                transform=door_transform
            ),
            collision_box=self.shield_collision_box,
            collision_offset=self.shield_collision_offset,
            vulnerability=self.vulnerability,
            model=model,
            actor_information=ActorParameters(
                scannable=ScannableParameters(
                    scannable_info0=self.get_patched_scan(editor, world_name, area_name)
                )
            )
        ))

        relay = default.add_memory_relay("Lock Cleared")
        with relay.edit_properties(MemoryRelay) as _relay:
            _relay.editor_properties.transform = door_transform
            _relay.editor_properties.active = False

        lock.add_connection(State.Dead, Message.Activate, relay)

        relay.add_connection(State.Active, Message.Deactivate, lock)
        relay.add_connection(State.Active, Message.Reset, door)

        door.add_connection(State.Open, Message.Activate, relay)

        gibs = None
        sound = None
        streamed = None

        if not low_memory:
            particle = 0xCDCBDF04

            gibs = default.add_instance_with(Effect(
                editor_properties=EditorProperties(
                    transform=door_transform,
                    active=False
                ),
                particle_effect=particle,
                restart_on_activate=True,
                motion_control_spline=self.get_spline(),
            ))

            sound = default.add_instance_with(Sound(
                editor_properties=EditorProperties(
                    name="Metal Door Lock Breaking",
                    transform=door_transform
                ),
                sound=948,
                max_audible_distance=150.0,
                surround_pan=SurroundPan(surround_pan=1.0)
            ))

            streamed = default.add_instance_with(StreamedAudio(
                editor_properties=EditorProperties(
                    name="StreamedAudio - Event Jingle",
                    transform=door_transform
                ),
                song_file="/audio/evt_x_event_00.dsp",
                fade_in_time=0.01,
                volume=65,
                software_channel=1,
                unknown=False
            ))

            lock.add_connection(State.Dead, Message.Play, sound)
            lock.add_connection(State.Dead, Message.Play, streamed)
            lock.add_connection(State.Dead, Message.Activate, gibs)

        return BlastShieldActors(door, sound, streamed, lock, relay, gibs)


@dataclasses.dataclass(kw_only=True)
class VanillaBlastShieldDoorType(BlastShieldDoorType):
    def remove_blast_shield(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        area = self.get_area(editor, world_name, area_name)
        door = self.get_door_from_dock_index(area, self.get_dock_index(world_name, area_name, dock_name))

        relay = self.find_attached_instance(area, door, State.Open, Message.Activate, MemoryRelay)
        lock = self.find_attached_instance(area, relay, State.Active, Message.Deactivate, Actor)

        for connection in lock.connections:
            area.remove_instance(connection.target)
        area.remove_instance(lock)


@dataclasses.dataclass(kw_only=True)
class SeekerBlastShieldDoorType(VanillaBlastShieldDoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str, low_memory: bool):
        actors = super().patch_door(editor, world_name, area_name, dock_name, low_memory)
        area = self.get_area(editor, world_name, area_name)
        default = area.get_layer("Default")

        # immune instead of reflect so that it explodes on the lock
        missile_immune = dataclasses.replace(resist_all_vuln, missile=WeaponVulnerability(damage_multiplier=0.0))
        with actors.lock.edit_properties(Actor) as lock:
            lock.vulnerability = missile_immune
        with actors.door.edit_properties(Door) as door:
            door.vulnerability = missile_immune

        door_transform = actors.door.get_properties_as(Door).editor_properties.transform

        # TODO: try using a sequencetimer to squeeze one fewer instance out of this
        timer = default.add_instance_with(Timer(
            editor_properties=EditorProperties(
                name="Button Control",
                transform=door_transform
            ),
            time=0.75
        ))

        timer_reset = default.add_instance_with(Timer(
            editor_properties=EditorProperties(
                name="Button Reset",
                transform=door_transform
            ),
            time=0.01
        ))

        # create 5 triggers so that you can have 5 lock-ons
        # TODO: only use 2 triggers in low memory mode and just accept it being more jank?
        # 30.01 health because splash damage is inconsistent. missiles do 30 damage
        # so this guarantees you need at least 2 missiles at once to break it
        triggers = [
            default.add_instance_with(self.create_trigger(
                f"Bridge Button {i}",
                door_transform, 30.01)
            ) for i in range(5)
        ]
        main_trigger = triggers[0]
        # TODO: repurpose one of the big triggers for this to save an instance
        mini_trigger = default.add_instance_with(self.create_trigger(
            "Bridge Button Mini",
            door_transform,
            1.0,
            seeker_lock_on=False
        ))

        # start a timer when the tiny trigger dies. stop it if the main trigger dies
        mini_trigger.add_connection(State.Dead, Message.ResetAndStart, timer)
        main_trigger.add_connection(State.Dead, Message.Stop, timer)
        for trigger in triggers:
            timer.add_connection(State.Zero, Message.Deactivate, trigger)

        # if the timer counts all the way down, reset the triggers
        timer.add_connection(State.Zero, Message.ResetAndStart, timer_reset)
        timer_reset.add_connection(State.Zero, Message.Activate, mini_trigger)
        for trigger in triggers:
            timer_reset.add_connection(State.Zero, Message.Activate, trigger)

        # move the lock's connections to the trigger, since it's the thing that dies now
        for connection in actors.lock.connections:
            actors.lock.remove_connection(connection)
            main_trigger.add_connection(
                connection.state,
                connection.message,
                connection.target
            )

        for trigger in triggers:
            actors.relay.add_connection(State.Active, Message.Deactivate, trigger)
        actors.relay.add_connection(State.Active, Message.Deactivate, mini_trigger)
        actors.relay.add_connection(State.Active, Message.Deactivate, timer)
        actors.relay.add_connection(State.Active, Message.Deactivate, timer_reset)

    def remove_blast_shield(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str):
        area = self.get_area(editor, world_name, area_name)
        door = self.get_door_from_dock_index(area, self.get_dock_index(world_name, area_name, dock_name))

        memory_relay = self.find_attached_instance(area, door, State.Open, Message.Activate, MemoryRelay)
        trigger = self.find_attached_instance(area, memory_relay, State.Active, Message.Deactivate, DamageableTrigger)
        shaker = self.find_attached_instance(area, trigger, State.Dead, Message.Action, CameraShaker)
        counter = self.find_attached_instance(area, trigger, State.Dead, Message.Increment, Counter)
        complete_relay = self.find_attached_instance(area, counter, State.MaxReached, Message.SetToZero, Relay)

        area.remove_instance(shaker)
        for connection in complete_relay.connections:
            area.remove_instance(connection.target)
        area.remove_instance(complete_relay)
        area.remove_instance(counter)


@dataclasses.dataclass(kw_only=True)
class PlanetaryEnergyDoorType(DoorType):
    planetary_energy_item_id: int

    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str, low_memory: bool):
        raise NotImplementedError()


@dataclasses.dataclass(kw_only=True)
class GrappleDoorType(BlastShieldDoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str, low_memory: bool):
        raise NotImplementedError()


@dataclasses.dataclass
class VisorBlastShieldActors(BlastShieldActors):
    trigger: ScriptInstance
    visor_detector: ScriptInstance


@dataclasses.dataclass(kw_only=True)
class VisorDoorType(BlastShieldDoorType):
    visor_flags: VisorFlags
    player_controller_proxy: int

    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str, low_memory: bool):
        actors = super().patch_door(editor, world_name, area_name, dock_name, low_memory)
        area = self.get_area(editor, world_name, area_name)
        default = area.get_layer("Default")

        with actors.door.edit_properties(Door) as door:
            door.vulnerability = resist_all_vuln
            door_xfm = door.editor_properties.transform


        with actors.lock.edit_properties(Actor) as lock:
            lock.vulnerability = resist_all_vuln

        trigger = default.add_instance_with(self.create_trigger(
            "Door Button", door_xfm, 1.0, self.visor_flags,
            active=False, seeker_lock_on=False, orbitable=True
        ))

        visor_detector = default.add_instance_with(PlayerController(
            editor_properties=EditorProperties(
                name="Detect Visor",
                transform=door_xfm
            ),
            unknown_0xe71de331=1,
            proxy_type=self.player_controller_proxy
        ))

        visor_detector.add_connection(State.Entered, Message.Activate, trigger)
        visor_detector.add_connection(State.Exited, Message.Deactivate, trigger)

        for connection in actors.lock.connections:
            actors.lock.remove_connection(connection)
            trigger.add_connection(
                connection.state,
                connection.message,
                connection.target
            )

        actors.relay.add_connection(State.Active, Message.Deactivate, trigger)
        actors.relay.add_connection(State.Active, Message.Deactivate, visor_detector)

        return VisorBlastShieldActors(
            actors.door, actors.sound, actors.streamed,
            actors.lock, actors.relay, actors.gibs,
            trigger, visor_detector
        )


@dataclasses.dataclass(kw_only=True)
class DarkVisorDoorType(VisorDoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str, low_memory: bool):
        actors = super().patch_door(editor, world_name, area_name, dock_name, low_memory)

        with actors.lock.edit_properties(Actor) as lock:
            # TODO: update the template
            # this property makes the actor appear red in dark visor
            lock.actor_information.unknown_0xcd4c81a1 = True


@dataclasses.dataclass(kw_only=True)
class EchoVisorDoorType(VisorDoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str, low_memory: bool):
        actors = super().patch_door(editor, world_name, area_name, dock_name, low_memory)
        area = self.get_area(editor, world_name, area_name)
        default = area.get_layer("Default")

        door_xfm = actors.door.get_properties_as(Door).editor_properties.transform

        center_pos = Vector(
            door_xfm.position.x,
            door_xfm.position.y,
            door_xfm.position.z + 1.8
        )

        hud_hint = default.add_instance_with(HUDHint(
            editor_properties=EditorProperties(
                name="Echo Target Icon",
                transform=Transform(
                    center_pos,
                    door_xfm.rotation,
                ),
                active=True
            ),
            hud_texture=0x36B1CB06,
            unknown_0x6078a651=24.0,
            unknown_0xf00bb6bb=128.0,
            animation_time=0.5,
            animation_frames=4,
            unknown_0xd993f97b=2
        ))

        with actors.lock.edit_properties(Actor) as lock:
            lock.echo_information.is_echo_emitter = True

        actors.relay.add_connection(State.Active, Message.Deactivate, hud_hint)


        if not low_memory:
            beacon_loop = default.add_instance_with(Sound(
                editor_properties=EditorProperties(
                    name="Echo Beacon Sound Loop",
                    transform=Transform(
                        position=center_pos
                    ),
                ),
                sound=1003,
                max_audible_distance=75.0,
                min_volume=0,
                max_volume=60,
                surround_pan=SurroundPan(
                    pan=0.0,
                    surround_pan=1.0
                ),
                loop=True,
                play_always=True,
                echo_visor_max_volume=127
            ))

            disrupted = default.add_instance_with(Sound(
                editor_properties=EditorProperties(
                    name="Echo Particle Disrupted",
                    transform=Transform(
                        position=center_pos
                    ),
                ),
                sound=1004,
                max_audible_distance=75.0,
                min_volume=20,
                max_volume=120,
                surround_pan=SurroundPan(
                    pan=0.0,
                    surround_pan=1.0
                ),
            ))

            timer = default.add_instance_with(Timer(
                editor_properties=EditorProperties(
                    name="Open Echo Door",
                    transform=door_xfm,
                ),
                time=1.0
            ))

            for connection in actors.trigger.connections:
                actors.trigger.remove_connection(connection)
                timer.add_connection(
                    State.Zero,
                    connection.message,
                    connection.target
                )

            actors.trigger.add_connection(State.Dead, Message.ResetAndStart, timer)
            actors.trigger.add_connection(State.Dead, Message.InternalMessage00, hud_hint)
            actors.trigger.add_connection(State.Dead, Message.Stop, beacon_loop)
            actors.trigger.add_connection(State.Dead, Message.Play, disrupted)

            actors.visor_detector.add_connection(State.Entered, Message.Play, beacon_loop)
            actors.visor_detector.add_connection(State.Exited, Message.Stop, beacon_loop)

            actors.relay.add_connection(State.Active, Message.Deactivate, beacon_loop)
            actors.relay.add_connection(State.Active, Message.Deactivate, timer)
            actors.relay.add_connection(State.Active, Message.Deactivate, disrupted)


@dataclasses.dataclass(kw_only=True)
class ScanVisorDoorType(BlastShieldDoorType):
    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str, low_memory: bool):
        raise NotImplementedError()


@dataclasses.dataclass(kw_only=True)
class TranslatorDoorType(ScanVisorDoorType):
    translator_item_id: int

    def patch_door(self, editor: PatcherEditor, world_name: str, area_name: str, dock_name: str, low_memory: bool):
        raise NotImplementedError()
