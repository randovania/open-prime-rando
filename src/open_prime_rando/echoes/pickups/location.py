from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Annotated, Literal, NamedTuple

import pydantic
from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats.script_object import ScriptInstance
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


@dataclasses.dataclass(frozen=True)
class PickupInstances:
    pickup: ScriptInstance
    hud_memo: ScriptInstance
    streamed_audio: ScriptInstance
    sound: ScriptInstance
    audio_fade: ScriptInstance
    post_pickup_relay: ScriptInstance
    mappable_object: ScriptInstance


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

    # TODO: add to db
    # dark torvus arena 0x200543, "Stage 2 -> Post Battle Cinematic"
    # main gyro chamber 0x240111, "Cannon"

    def get_instances(self, area: Area) -> PickupInstances:
        raise NotImplementedError

    def get_layer_name(self, area: Area) -> str:
        raise NotImplementedError

    def _add_mappable_obj(self, area: Area, relay: ScriptInstance) -> ScriptInstance:
        layer = area.get_layer(self.get_layer_name(area))

        mappable = layer.add_instance_with(
            SpecialFunction(
                editor_properties=EditorProperties(name="Pickup Map Icon"),
                function=Function.TranslatorDoorLocation,
                sound1=-1,
                sound2=-1,
                sound3=-1,
            )
        )

        relay.add_connection(State.Zero, Message.Decrement, mappable)
        return mappable


class StandardPickupLocation(BasePickupLocation):
    type: Literal["standard"]
    pickup: PydanticInstanceId
    hud_memo: PydanticInstanceId
    streamed_audio: PydanticInstanceId
    sound: PydanticInstanceId
    audio_fade: PydanticInstanceId

    def get_instances(self, area: Area) -> PickupInstances:
        inst = area.get_instance

        layer = area.get_layer(self.get_layer_name(area))
        relay = layer.add_instance_with(
            Relay(
                editor_properties=EditorProperties(name="Post-Pickup Relay"),
                one_shot=False,
            )
        )
        pickup = inst(self.pickup)
        pickup.add_connection(State.Arrived, Message.SetToZero, relay)

        return PickupInstances(
            pickup=pickup,
            hud_memo=inst(self.hud_memo),
            streamed_audio=inst(self.streamed_audio),
            sound=inst(self.sound),
            audio_fade=inst(self.audio_fade),
            post_pickup_relay=relay,
            mappable_object=self._add_mappable_obj(area, relay),
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

    def get_instances(self, area: Area) -> PickupInstances:
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

        # Add connections
        pickup.add_connection(State.Arrived, Message.SetToZero, hud_memo)
        pickup.add_connection(State.Arrived, Message.Play, streamed)
        pickup.add_connection(State.Arrived, Message.Play, sound)
        pickup.add_connection(State.Arrived, Message.Decrement, audio_fade)
        pickup.add_connection(State.Arrived, Message.ResetAndStart, timer)
        timer.add_connection(State.Zero, Message.Increment, audio_fade)
        pickup.add_connection(State.Arrived, Message.Activate, mem_relay)
        mem_relay.add_connection(State.Active, Message.Deactivate, pickup)
        pickup.add_connection(State.Arrived, Message.SetToZero, relay)

        return PickupInstances(
            pickup,
            hud_memo,
            streamed,
            sound,
            audio_fade,
            relay,
            self._add_mappable_obj(area, relay),
        )

    def get_layer_name(self, area: Area) -> str:
        return self.layer


PickupLocation = Annotated[StandardPickupLocation | CustomPickupLocation, pydantic.Field(discriminator="type")]
