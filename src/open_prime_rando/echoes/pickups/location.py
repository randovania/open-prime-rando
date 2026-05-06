from __future__ import annotations

import dataclasses
import typing
from typing import TYPE_CHECKING, Annotated, Literal, NamedTuple

import pydantic
from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats.script_object import Connection, ScriptInstance
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.SurroundPan import SurroundPan
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.objects import (
    HUDMemo,
    MemoryRelay,
    Pickup,
    Relay,
    Sound,
    SpecialFunction,
    StreamedAudio,
    Timer,
)
from retro_data_structures.properties.echoes.objects.SpecialFunction import Function

from open_prime_rando.echoes.pickups.model_database import PickupModelByName
from open_prime_rando.echoes.pydantic_models import PydanticConnection, PydanticInstanceId, PydanticVector

if TYPE_CHECKING:
    from retro_data_structures.formats.mlvl import Area
    from retro_data_structures.formats.script_layer import ScriptLayer


@dataclasses.dataclass(frozen=True, kw_only=True)
class PickupInstances:
    pickup: Annotated[ScriptInstance, Pickup]
    hud_memo: Annotated[ScriptInstance, HUDMemo]
    streamed_audio: Annotated[ScriptInstance, StreamedAudio]
    sound: Annotated[ScriptInstance, Sound]
    audio_fade: Annotated[ScriptInstance, StreamedAudio]
    fade_timer: Annotated[ScriptInstance, Timer]
    post_pickup_relay: Annotated[ScriptInstance, Relay]
    mappable_object: Annotated[ScriptInstance, SpecialFunction]
    memory_relay: Annotated[ScriptInstance, MemoryRelay]

    def new_stage(self, layer: ScriptLayer) -> PickupInstances:
        """
        Create copies of any instances that change between pickup stages,
        set up their connections, and return a new PickupInstances with the new instances.
        """

        def copy_inst(instance: ScriptInstance) -> ScriptInstance:
            return layer.add_instance_with(instance.get_properties())

        pickup = copy_inst(self.pickup)
        with pickup.edit_properties(Pickup) as pickup_props:
            pickup_props.editor_properties.active = False

        stage = PickupInstances(
            pickup=pickup,
            hud_memo=copy_inst(self.hud_memo),
            streamed_audio=copy_inst(self.streamed_audio),
            sound=copy_inst(self.sound),
            audio_fade=copy_inst(self.audio_fade),
            fade_timer=copy_inst(self.fade_timer),
            post_pickup_relay=copy_inst(self.post_pickup_relay),
            mappable_object=self.mappable_object,
            memory_relay=self.memory_relay,
        )
        stage.add_connections()
        return stage

    def add_connections(self) -> None:
        """
        Set up the connections between the instances. Use when the instances are first created.
        """

        self.pickup.add_connection(State.Arrived, Message.SetToZero, self.hud_memo)
        self.pickup.add_connection(State.Arrived, Message.Play, self.streamed_audio)
        self.pickup.add_connection(State.Arrived, Message.Play, self.sound)
        self.pickup.add_connection(State.Arrived, Message.Decrement, self.audio_fade)
        self.pickup.add_connection(State.Arrived, Message.ResetAndStart, self.fade_timer)
        self.fade_timer.add_connection(State.Zero, Message.Increment, self.audio_fade)
        self.pickup.add_connection(State.Arrived, Message.Activate, self.memory_relay)
        self.memory_relay.add_connection(State.Active, Message.Deactivate, self.pickup)
        self.pickup.add_connection(State.Arrived, Message.SetToZero, self.post_pickup_relay)
        self.post_pickup_relay.add_connection(State.Zero, Message.Decrement, self.mappable_object)


class CutsceneModel(NamedTuple):
    instance: PydanticInstanceId
    layer: str


class BasePickupLocation(pydantic.BaseModel):
    exclude_memo_from_removal: bool
    original_model: PickupModelByName
    connections: list[PydanticConnection]
    removals: list[PydanticInstanceId]
    collision_offset: PydanticVector
    cutscene_model: CutsceneModel | None = None

    _instances: PickupInstances | None = None

    # TODO: add to db
    # dark torvus arena 0x200543, "Stage 2 -> Post Battle Cinematic"
    # main gyro chamber 0x240111, "Cannon"

    def _prepare_instances(self, area: Area) -> PickupInstances:
        raise NotImplementedError

    def prepare_instances(self, area: Area) -> PickupInstances:
        """
        When first called, prepares and returns the instances for this location,
        creating new ones and adding connections as needed.
        On subsequent calls, the existing instances are returned directly.
        """

        if self._instances is None:
            self._instances = self._prepare_instances(area)
        return self._instances

    def get_layer_name(self, area: Area) -> str:
        raise NotImplementedError

    def get_layer(self, area: Area) -> ScriptLayer:
        return area.get_layer(self.get_layer_name(area))

    def _add_mappable_obj(self, area: Area) -> ScriptInstance:
        layer = self.get_layer(area)

        return layer.add_instance_with(
            SpecialFunction(
                editor_properties=EditorProperties(name="Pickup Map Icon"),
                function=Function.TranslatorDoorLocation,
                sound1=-1,
                sound2=-1,
                sound3=-1,
            )
        )


class StandardPickupLocation(BasePickupLocation):
    type: Literal["standard"]
    pickup: PydanticInstanceId
    hud_memo: PydanticInstanceId
    streamed_audio: PydanticInstanceId
    sound: PydanticInstanceId
    audio_fade: PydanticInstanceId

    @typing.override
    def _prepare_instances(self, area: Area) -> PickupInstances:
        get_inst = area.get_instance

        layer = area.get_layer(self.get_layer_name(area))
        relay = layer.add_instance_with(
            Relay(
                editor_properties=EditorProperties(name="Post-Pickup Relay"),
                one_shot=False,
            )
        )
        pickup = get_inst(self.pickup)
        pickup.add_connection(State.Arrived, Message.SetToZero, relay)

        # find the MemoryRelay that the pickup sends an Activate message to on its Arrived state
        mem_relay = next(
            inst
            for conn in pickup.connections
            if conn.state == State.Arrived
            and conn.message == Message.Activate
            and (inst := get_inst(conn.target)).script_type == MemoryRelay
        )

        desired_connection = Connection(State.Zero, Message.Increment, self.audio_fade)
        fade_timer = next(inst for inst in area.all_instances if desired_connection in inst.connections)

        mappable_object = self._add_mappable_obj(area)
        relay.add_connection(State.Zero, Message.Decrement, mappable_object)

        return PickupInstances(
            pickup=pickup,
            hud_memo=get_inst(self.hud_memo),
            streamed_audio=get_inst(self.streamed_audio),
            sound=get_inst(self.sound),
            audio_fade=get_inst(self.audio_fade),
            fade_timer=fade_timer,
            post_pickup_relay=relay,
            mappable_object=mappable_object,
            memory_relay=mem_relay,
        )

    def get_layer_name(self, area: Area) -> str:
        for layer in area.layers:
            try:
                layer.get_instance(self.pickup)
            except KeyError:
                continue
            return layer.name
        raise KeyError(f"Unknown pickup: {self.pickup}")


class CustomPickupLocation(BasePickupLocation):
    type: Literal["custom"]
    position: PydanticVector
    collision_size: PydanticVector
    layer: str

    @typing.override
    def _prepare_instances(self, area: Area) -> PickupInstances:
        layer = area.get_layer(self.layer)

        # Create instances
        pickup = layer.add_instance_with(
            Pickup(
                editor_properties=EditorProperties(
                    transform=Transform(
                        position=self.position,
                    ),
                    name="Pickup",
                ),
                collision_offset=self.collision_offset,
                collision_size=self.collision_size,
            )
        )

        hud_memo = layer.add_instance_with(
            HUDMemo(
                editor_properties=EditorProperties(
                    transform=Transform(
                        position=self.position,
                    ),
                    name="Pickup Acquired",
                ),
            )
        )

        streamed = layer.add_instance_with(
            StreamedAudio(
                editor_properties=EditorProperties(
                    transform=Transform(
                        position=self.position,
                    ),
                    name="Pickup Jingle",
                ),
                fade_in_time=0.01,
                software_channel=1,
            )
        )

        sound = layer.add_instance_with(
            Sound(
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
            )
        )

        audio_fade = layer.add_instance_with(
            StreamedAudio(
                editor_properties=EditorProperties(
                    transform=Transform(
                        position=self.position,
                    ),
                    name="FadeIn/Out Long",
                ),
                song_file="sw",
                fade_in_time=2.0,
                fade_out_time=2.0,
            )
        )

        timer = layer.add_instance_with(
            Timer(
                editor_properties=EditorProperties(
                    transform=Transform(
                        position=self.position,
                    ),
                    name="Fade In Music",
                ),
                time=1.0,
            )
        )

        mem_relay = layer.add_memory_relay("Deactivate Pickup")
        with mem_relay.edit_properties(MemoryRelay) as _mem_relay:
            _mem_relay.editor_properties.transform.position = self.position
            _mem_relay.editor_properties.active = False

        relay = layer.add_instance_with(
            Relay(
                editor_properties=EditorProperties(name="Post-Pickup Relay"),
                one_shot=False,
            )
        )

        instances = PickupInstances(
            pickup=pickup,
            hud_memo=hud_memo,
            streamed_audio=streamed,
            sound=sound,
            audio_fade=audio_fade,
            fade_timer=timer,
            post_pickup_relay=relay,
            mappable_object=self._add_mappable_obj(area),
            memory_relay=mem_relay,
        )
        instances.add_connections()
        return instances

    def get_layer_name(self, area: Area) -> str:
        return self.layer


PickupLocation = Annotated[StandardPickupLocation | CustomPickupLocation, pydantic.Field(discriminator="type")]
