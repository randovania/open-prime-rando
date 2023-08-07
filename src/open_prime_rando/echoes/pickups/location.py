import dataclasses

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats.mlvl import Area
from retro_data_structures.formats.script_object import Connection, InstanceId, ScriptInstance
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.SurroundPan import SurroundPan
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import HUDMemo, MemoryRelay, Pickup, Sound, StreamedAudio, Timer
from typing_extensions import Self

from open_prime_rando.echoes.pickups.model_database import PICKUP_MODELS
from open_prime_rando.echoes.pickups.models import PickupModel


@dataclasses.dataclass(frozen=True)
class PickupInstances:
    pickup: ScriptInstance
    hud_memo: ScriptInstance
    streamed_audio: ScriptInstance
    sound: ScriptInstance
    audio_fade: ScriptInstance


@dataclasses.dataclass(frozen=True)
class PickupLocation:
    exclude_memo_from_removal: bool
    original_model: PickupModel
    connections: list[Connection]
    removals: list[InstanceId]

    @classmethod
    def from_json(cls, data: dict) -> Self:
        type_ = data.pop("type")
        if type_ == "standard":
            return StandardPickupLocation.from_json(data)
        if type_ == "custom":
            return CustomPickupLocation.from_json(data)
        raise ValueError(f"No such pickup location type: '{type_}'")

    def get_instances(self, area: Area) -> PickupInstances:
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class StandardPickupLocation(PickupLocation):
    pickup: InstanceId
    hud_memo: InstanceId
    streamed_audio: InstanceId
    sound: InstanceId
    audio_fade: InstanceId

    @classmethod
    def from_json(cls, data: dict) -> Self:
        instances = data["instances"]
        return StandardPickupLocation(
            exclude_memo_from_removal=data["exclude_memo_from_removal"],
            original_model=PICKUP_MODELS[data["original_model"]],
            connections=[Connection.from_construct(c) for c in data["connections"]],
            removals=[InstanceId(i) for i in data["removals"]],
            pickup=InstanceId(instances["pickup"]),
            hud_memo=InstanceId(instances["hud_memo"]),
            streamed_audio=InstanceId(instances["streamed_audio"]),
            sound=InstanceId(instances["sound"]),
            audio_fade=InstanceId(instances["audio_fade"]),
        )

    def get_instances(self, area: Area) -> PickupInstances:
        def inst(ref):
            return area.get_instance(ref)

        return PickupInstances(
            pickup=inst(self.pickup),
            hud_memo=inst(self.hud_memo),
            streamed_audio=inst(self.streamed_audio),
            sound=inst(self.sound),
            audio_fade=inst(self.audio_fade),
        )


@dataclasses.dataclass(frozen=True)
class CustomPickupLocation(PickupLocation):
    position: Vector
    collision_size: Vector
    collision_offset: Vector
    layer: str

    @classmethod
    def from_json(cls, data: dict) -> Self:
        return CustomPickupLocation(
            exclude_memo_from_removal=data["exclude_memo_from_removal"],
            original_model=PICKUP_MODELS[data["original_model"]],
            connections=[Connection.from_construct(c) for c in data["connections"]],
            removals=[InstanceId(i) for i in data["removals"]],
            position=Vector.from_json(data["position"]),
            collision_size=Vector.from_json(data["collision_size"]),
            collision_offset=Vector.from_json(data["collision_offset"]),
            layer=data["layer"],
        )

    def get_instances(self, area: Area) -> PickupInstances:
        layer = area.get_layer(self.layer)

        # Create instances
        pickup = layer.add_instance_with(Pickup(
            editor_properties=EditorProperties(
                transform=Transform(
                    position=self.position,
                ),
                name="Pickup",
            ),
            collision_offset=self.collision_offset,
            collision_size=self.collision_size,
        ))

        hud_memo = layer.add_instance_with(HUDMemo(
            editor_properties=EditorProperties(
                transform=Transform(
                    position=self.position,
                ),
                name="Pickup Acquired",
            ),
        ))

        streamed = layer.add_instance_with(StreamedAudio(
            editor_properties=EditorProperties(
                transform=Transform(
                    position=self.position,
                ),
                name="Pickup Jingle",
            ),
            fade_in_time=0.01,
            software_channel=1,
        ))

        sound = layer.add_instance_with(Sound(
            editor_properties=EditorProperties(
                transform=Transform(
                    position=self.position,
                ),
                name="Pickup Sound",
            ),
            surround_pan=SurroundPan(
                surround_pan=1.0,
            ),
            ambient=True,
            use_room_acoustics=False,
        ))

        audio_fade = layer.add_instance_with(StreamedAudio(
            editor_properties=EditorProperties(
                transform=Transform(
                    position=self.position,
                ),
                name="FadeIn/Out Long",
            ),
            song_file='sw',
            fade_in_time=2.0,
            fade_out_time=2.0,
        ))

        timer = layer.add_instance_with(Timer(
            editor_properties=EditorProperties(
                transform=Transform(
                    position=self.position,
                ),
                name="Fade In Music",
            ),
            time=1.0,
        ))

        relay = layer.add_memory_relay("Deactivate Pickup")
        with relay.edit_properties(MemoryRelay) as _relay:
            _relay.editor_properties.transform.position = self.position
            _relay.editor_properties.active = False

        # Add connections
        pickup.add_connection(State.Arrived, Message.SetToZero, hud_memo)
        pickup.add_connection(State.Arrived, Message.Play, streamed)
        pickup.add_connection(State.Arrived, Message.Play, sound)
        pickup.add_connection(State.Arrived, Message.Decrement, audio_fade)
        pickup.add_connection(State.Arrived, Message.ResetAndStart, timer)
        timer.add_connection(State.Zero, Message.Increment, audio_fade)
        pickup.add_connection(State.Arrived, Message.Activate, relay)
        relay.add_connection(State.Active, Message.Deactivate, pickup)

        return PickupInstances(
            pickup,
            hud_memo,
            streamed,
            sound,
            audio_fade,
        )
