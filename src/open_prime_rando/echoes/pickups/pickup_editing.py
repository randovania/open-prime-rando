import dataclasses
from typing import NamedTuple, Self

from retro_data_structures.enums.echoes import Message, PlayerItemEnum, State
from retro_data_structures.formats.mapa import Mapa, ObjectTypeMP2, ObjectVisibility
from retro_data_structures.formats.mrea import Area
from retro_data_structures.formats.script_layer import ScriptLayer
from retro_data_structures.formats.script_object import ScriptInstance
from retro_data_structures.properties.echoes.archetypes.ConditionalTest import (
    AmountOrCapacity,
    Condition,
    ConditionalTest,
)
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.core.Spline import Spline
from retro_data_structures.properties.echoes.objects import (
    ConditionalRelay,
    Effect,
    HUDMemo,
    Relay,
    Sound,
    SpecialFunction,
    StreamedAudio,
)
from retro_data_structures.properties.echoes.objects.Pickup import Pickup as RDSPickup
from retro_data_structures.properties.echoes.objects.SpecialFunction import Function

from open_prime_rando.echoes.pickups.location import PickupInstances, PickupLocation
from open_prime_rando.echoes.pickups.model_database import PICKUP_MODELS
from open_prime_rando.echoes.pickups.models import ETM_MODEL, PickupModel
from open_prime_rando.patcher_editor import PatcherEditor


class Jingle(NamedTuple):
    file_name: str
    volume: float


@dataclasses.dataclass(frozen=True)
class PickupAppearance:
    model_data: PickupModel
    sound: int
    jingle: Jingle
    hud_text: str
    scan: str

    @classmethod
    def from_json(cls, data: dict) -> Self:
        return cls(
            model_data=PICKUP_MODELS[data["model"]],
            sound=data["sound"],
            jingle=Jingle(
                data["jingle"]["file"],
                data["jingle"]["volume"],
            ),
            hud_text=data["hud_text"],
            scan=data["scan"],
        )


class ResourceGain(NamedTuple):
    item: int
    amount: int


class ResourceConversion(NamedTuple):
    from_item: int
    to_item: int


@dataclasses.dataclass(frozen=True)
class PickupStage:
    required_item: int | None
    resources: list[ResourceGain]
    appearance: PickupAppearance
    conversion: list[ResourceConversion]

    @classmethod
    def from_json(cls, data: dict) -> Self:
        return cls(
            required_item=data["required_item"],
            resources=[ResourceGain(gain["item"], gain["amount"]) for gain in data["resources"]],
            appearance=PickupAppearance.from_json(data["appearance"]),
            conversion=[
                ResourceConversion(
                    conversion["from_item"],
                    conversion["to_item"],
                )
                for conversion in data["converted"]
            ],
        )


@dataclasses.dataclass(frozen=True)
class Pickup:
    location: PickupLocation
    stages: list[PickupStage]

    @classmethod
    def from_json(cls, data: dict) -> Self:
        return cls(
            location=PickupLocation.from_json(data["location"]),
            stages=[PickupStage.from_json(stage) for stage in data["stages"]],
        )

    def patch_pickup(self, editor: PatcherEditor, area: Area, mapa: Mapa):
        if len(self.stages > 1):
            self._patch_complex_pickup(editor, area)
        else:
            self._patch_simple_pickup(editor, area)

    def _attach_etm_particle(self, target: ScriptInstance, layer: ScriptLayer):
        with target.edit_properties(target.type) as props:
            target_editor_properties: EditorProperties = props.editor_properties

        particle = layer.add_instance_with(Effect())
        with particle.edit_properties(Effect) as etm:
            etm.editor_properties.active = target_editor_properties.active
            etm.editor_properties.transform = target_editor_properties.transform
            etm.particle_effect = 0x95C37749
            etm.restart_on_activate = True
            etm.unknown_0xbe931927 = True
            etm.motion_spline_duration = 5.0
            etm.motion_control_spline = Spline(
                bytes.fromhex(
                    "00 00 00 00 00 03 00 00"
                    "00 00 00 00 00 00 01 01"
                    "3f 80 00 00 3c cb 9c b7"
                    "05 05 40 3f ab 94 3e 33"
                    "f9 65 40 3f ab 94 3e 33"
                    "f9 65 40 a0 00 00 3f 80"
                    "00 00 05 05 40 29 1f 0d"
                    "3f b5 ca 7c 40 29 1f 0d"
                    "3f b5 ca 7c 01 00 00 00"
                    "00 3f 80 00 00"
                )
            )
        target.add_connection(State.Active, Message.Activate, particle)
        target.add_connection(State.Inactive, Message.Deactivate, particle)
        target.add_connection(State.Arrived, Message.Deactivate, particle)

        follow_sf = layer.add_instance_with(
            SpecialFunction(
                editor_properties=EditorProperties(
                    name="ETM Follow Pickup",
                    transform=target_editor_properties.transform,
                ),
                function=Function.ObjectFollowObject,
                sound1=-1,
                sound2=-1,
                sound3=-1,
            )
        )
        follow_sf.add_connection(State.Play, Message.Deactivate, particle)
        follow_sf.add_connection(State.Play, Message.Activate, target)

    def _add_modify_inventory_sf(self, item: int, amount: int, layer: ScriptLayer) -> ScriptInstance:
        return layer.add_instance_with(
            SpecialFunction(
                editor_properties=EditorProperties(name="Modify Item Amount"),
                function=Function.InventoryThing1,
                int_parm2=amount,
                inventory_item_parm=item,
                sound1=-1,
                sound2=-1,
                sound3=-1,
            )
        )

    def _add_relay(self, layer: ScriptLayer) -> ScriptInstance:
        return layer.add_instance_with(
            Relay(
                editor_properties=EditorProperties(name="Relay"),
                one_shot=False,
            )
        )

    def _add_conditional_relay(self, item: int, immediate: bool, layer: ScriptLayer) -> ScriptInstance:
        return layer.add_instance_with(
            ConditionalRelay(
                editor_properties=EditorProperties(name="Conditional Relay"),
                trigger_on_first_think=immediate,
                conditional1=ConditionalTest(
                    player_item=item,
                    amount_or_capacity=AmountOrCapacity.Capacity,
                    condition=Condition.GreaterThan,
                    value=0,
                ),
            )
        )

    def _patch_single_pickup_stage_appearance(
        self, editor: PatcherEditor, area: Area, stage: PickupStage, instances: PickupInstances, disable_hud_popup: bool
    ):
        model_data = stage.appearance.model_data

        # pickup
        with instances.pickup.edit_properties(RDSPickup) as pickup:
            # basics
            pickup.model = model_data.model
            pickup.auto_spin = model_data.auto_spin

            # transform
            old_pos = self.location.original_model.get_position(editor)
            new_pos = stage.appearance.model_data.get_position(editor)

            offset = old_pos - new_pos
            pickup.editor_properties.transform.position += offset
            pickup.collision_offset -= offset

            pickup.editor_properties.transform.rotation = model_data.transform.rotation
            pickup.editor_properties.transform.scale = model_data.transform.scale
            pickup.orbit_offset = model_data.transform.orbit_offset

            # animation
            pickup.animation_information = model_data.animation.get_animation_parameters(editor)

            # lighting
            lighting = pickup.actor_information.lighting
            lighting.cast_shadow = model_data.lighting.cast_shadow
            lighting.unknown_0xa71810e9 = model_data.lighting.unk_bool
            lighting.world_lighting_options = model_data.lighting.use_world_lighting
            lighting.use_old_lighting = model_data.lighting.use_old_lighting
            lighting.ambient_color = model_data.lighting.ambient_color

            # scan
            pickup.actor_information.scannable.scannable_info0 = editor.get_pickup_scan(
                stage.appearance.scan, model_data.scan_model
            )
            area._parent_mlvl.savw.raw.scannable_objects.append(
                {
                    "scan_asset_id": pickup.actor_information.scannable.scannable_info0,
                    "logbook_category": 0,
                }
            )

        # ETM particle
        if model_data.model == ETM_MODEL:
            layer = area.get_layer(self.location.get_layer_name(area))
            self._attach_etm_particle(instances.pickup, layer)

        # cutscene model
        if self.location.cutscene_model is not None:
            inst = area.get_instance(self.location.cutscene_model.instance)

            # FIXME: this does not account for progressive item models
            with inst.edit_properties(inst.type) as cutscene_model:
                cutscene_model.model = model_data.model
                cutscene_model.animation_information.ancs = model_data.animation.get_animation_parameters(editor)

            if model_data.model == ETM_MODEL:
                layer = area.get_layer(self.location.cutscene_model.layer)
                self._attach_etm_particle(inst, layer)

        # sound
        with instances.sound.edit_properties(Sound) as sound:
            sound.sound = stage.appearance.sound

        # jingle
        with instances.streamed_audio.edit_properties(StreamedAudio) as streamed:
            streamed.song_file = stage.appearance.jingle.file_name
            streamed.volume = stage.appearance.jingle.volume

        # hud memo
        with instances.hud_memo.edit_properties(HUDMemo) as hud_memo:
            scan_string = stage.appearance.scan
            hud_memo.string, _ = editor.create_strg(f"Pickup{scan_string}.STRG", scan_string)

            if not disable_hud_popup:
                hud_memo.display_time = 2.5
                hud_memo.display_type = 1
            elif self.location.exclude_memo_from_removal:
                hud_memo.display_time = 0.1
                hud_memo.display_type = 1
            else:
                hud_memo.display_type = 4.0
                hud_memo.display_type = 0

    def _patch_single_pickup_stage_basic_resources(
        self,
        editor: PatcherEditor,
        area: Area,
        stage: PickupStage,
        instances: PickupInstances,
    ):
        instances.pickup.add_connection(State.Arrived, Message.SetToZero, instances.post_pickup_relay)

        percentage = next((item for item in stage.resources if item.item == PlayerItemEnum.ItemPercentage), None)
        first = next((item for item in stage.resources if item.item != percentage), None)
        remaining = [item for item in stage.resources if item not in (percentage, first)]

        with instances.pickup.edit_properties(RDSPickup) as pickup:
            if percentage is not None:
                pickup.item_percentage_increase = percentage.amount
            else:
                pickup.item_percentage_increase = 0

            if first is not None:
                pickup.item_to_give = first.item
                pickup.amount = first.amount
                pickup.capacity_increase = first.amount
            else:
                pickup.item_to_give = PlayerItemEnum.PowerBeam
                pickup.amount = 0
                pickup.capacity_increase = 0

        layer = area.get_layer(self.location.get_layer_name(area))
        for item in remaining:
            sf = self._add_modify_inventory_sf(item.item, item.amount, layer)
            instances.post_pickup_relay.add_connection(State.Zero, Message.Action, sf)

    def _patch_single_pickup_stage_converted_resources(
        self,
        editor: PatcherEditor,
        area: Area,
        stage: PickupStage,
        instances: PickupInstances,
    ):
        layer = area.get_layer(self.location.get_layer_name(area))
        for from_item, to_item in stage.conversion:
            relay = self._add_relay(layer)
            conditional = self._add_conditional_relay(from_item, False, layer)

            subtract_from = self._add_modify_inventory_sf(from_item, -1, layer)
            add_to = self._add_modify_inventory_sf(to_item, 1, layer)

            # after collecting the pickup, check the conditional relay
            instances.post_pickup_relay.add_connection(State.Zero, Message.SetToZero, conditional)

            # if from_item > 0, trigger the relay a single time
            conditional.add_connection(State.Open, Message.SetToZero, relay)

            # subtract 1 from from_item, add 1 to to_item, and checks the conditional relay again
            # this will loop until from_item == 0
            relay.add_connection(State.Zero, Message.Action, subtract_from)
            relay.add_connection(State.Zero, Message.Action, add_to)
            relay.add_connection(State.Zero, Message.SetToZero, conditional)

    def _patch_single_pickup_stage(
        self, editor: PatcherEditor, area: Area, stage: PickupStage, instances: PickupInstances, disable_hud_popup: bool
    ):
        self._patch_single_pickup_stage_appearance(
            editor,
            area,
            stage,
            instances,
            disable_hud_popup,
        )

        self._patch_single_pickup_stage_basic_resources(
            editor,
            area,
            stage,
            instances,
        )

        self._patch_single_pickup_stage_converted_resources(
            editor,
            area,
            stage,
            instances,
        )

        for connection in self.location.connections:
            instances.post_pickup_relay.add_connection(
                connection.state,
                connection.message,
                connection.target,
            )

    def _add_map_icon(self, mapa: Mapa, instances: PickupInstances):
        mappable_id = instances.mappable_object.id
        with instances.pickup.edit_properties(RDSPickup) as pickup:
            pos = pickup.editor_properties.transform.position
        padding = 0xFFFFFFFF

        mapa.raw.mappable_objects.append(
            {
                "type": ObjectTypeMP2.TranslatorGate,
                "visibility_mode": ObjectVisibility,
                "editor_id": mappable_id,
                "unk1": padding,
                "transform": [
                    1.0,
                    0.0,
                    0.0,
                    pos.x,
                    0.0,
                    1.0,
                    0.0,
                    pos.y,
                    0.0,
                    0.0,
                    1.0,
                    pos.z,
                ],
                "unk2": [padding] * 4,
            }
        )

    def _patch_simple_pickup(self, editor: PatcherEditor, area: Area, mapa: Mapa, disable_hud_popup: bool):
        instances = self.location.get_instances(area)

        self._patch_single_pickup_stage(editor, area, self.stages[0], instances, disable_hud_popup)
        self._add_map_icon(mapa, instances)

        for removal in self.location.removals:
            area.remove_instance(removal)

    def _patch_complex_pickup(self, editor: PatcherEditor, area: Area, mapa: Mapa, disable_hud_popup: bool):
        pass
