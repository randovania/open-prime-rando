from __future__ import annotations

import copy
import typing
from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, PlayerItemEnum, State
from retro_data_structures.formats.mapa import Mapa, MappableObject, ObjectVisibility
from retro_data_structures.properties.echoes.archetypes.ConditionalTest import (
    AmountOrCapacity,
    Boolean,
    Condition,
    ConditionalTest,
)
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.core.Spline import Spline
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import (
    ConditionalRelay,
    Effect,
    HUDMemo,
    Relay,
    Sound,
    SpecialFunction,
    StreamedAudio,
    Timer,
)
from retro_data_structures.properties.echoes.objects.Pickup import Pickup as RDSPickup
from retro_data_structures.properties.echoes.objects.SpecialFunction import Function

from open_prime_rando.echoes.pickups.models import ETM_MODEL

if TYPE_CHECKING:
    from retro_data_structures.base_resource import AssetId
    from retro_data_structures.formats import Mlvl
    from retro_data_structures.formats.mrea import Area
    from retro_data_structures.formats.script_layer import ScriptLayer
    from retro_data_structures.formats.script_object import ScriptInstance
    from retro_data_structures.properties.echoes.core import AnimationParameters

    from open_prime_rando.echoes.pickups.location import PickupInstances, PickupLocation
    from open_prime_rando.echoes.pickups.schema import PickupModification, PickupStage
    from open_prime_rando.patcher_editor import PatcherEditor


@typing.runtime_checkable
class ObjectWithModel(typing.Protocol):
    model: AssetId
    animation_information: AnimationParameters


def _attach_etm_particle_and_sound(target: ScriptInstance, layer: ScriptLayer) -> None:
    target_editor_properties: EditorProperties = getattr(target.get_properties(), "editor_properties")

    sound = layer.add_instance_with(Sound())
    with sound.edit_properties(Sound) as etm_sound:
        etm_sound.editor_properties.transform = target_editor_properties.transform
        etm_sound.editor_properties.active = False
        etm_sound.sound = 215
        etm_sound.surround_pan.surround_pan = 1.0
        etm_sound.loop = True
        etm_sound.auto_start = True
    target.add_connection(State.Active, Message.Activate, sound)
    target.add_connection(State.Inactive, Message.Deactivate, sound)
    target.add_connection(State.Arrived, Message.Deactivate, sound)

    particle = layer.add_instance_with(Effect())
    with particle.edit_properties(Effect) as etm_particle:
        etm_particle.editor_properties.active = target_editor_properties.active
        etm_particle.editor_properties.transform.scale = Vector(3.0, 3.0, 3.0)
        etm_particle.particle_effect = 0x95C37749
        etm_particle.restart_on_activate = True
        etm_particle.unknown_0xbe931927 = True
        etm_particle.motion_spline_duration = 5.0
        etm_particle.motion_control_spline = Spline.from_bytes(
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

    effect_follow_sf = layer.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(
                name="Effect Follow Pickup",
                transform=target_editor_properties.transform,
            ),
            function=Function.ObjectFollowObject,
            sound1=-1,
            sound2=-1,
            sound3=-1,
        )
    )

    sound_follow_sf = layer.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(
                name="Sound Follow Pickup",
                transform=target_editor_properties.transform,
            ),
            function=Function.ObjectFollowObject,
            sound1=-1,
            sound2=-1,
            sound3=-1,
        )
    )
    effect_follow_sf.add_connection(State.Play, Message.Deactivate, particle)
    effect_follow_sf.add_connection(State.Play, Message.Activate, target)
    sound_follow_sf.add_connection(State.Play, Message.Deactivate, sound)
    sound_follow_sf.add_connection(State.Play, Message.Activate, target)


def _add_modify_inventory_sf(item: PlayerItemEnum, amount: int, layer: ScriptLayer) -> ScriptInstance:
    return layer.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(name="Modify Item Amount"),
            function=Function.SetInventoryAmount,
            int_parm2=amount,
            inventory_item_parm=item,
            sound1=-1,
            sound2=-1,
            sound3=-1,
        )
    )


def _add_relay(layer: ScriptLayer) -> ScriptInstance:
    return layer.add_instance_with(
        Relay(
            editor_properties=EditorProperties(name="Relay"),
            one_shot=False,
        )
    )


def add_conditional_relay(
    item: PlayerItemEnum,
    immediate: bool,
    layer: ScriptLayer,
    *,
    name: str = "Conditional Relay",
    active: bool = True,
) -> ScriptInstance:
    empty_test = ConditionalTest(
        boolean=Boolean.Unknown,  # this enum value means that the conditional isn't checked by the relay's logic
    )
    return layer.add_instance_with(
        ConditionalRelay(
            editor_properties=EditorProperties(
                name=name,
                active=active,
            ),
            trigger_on_first_think=immediate,
            conditional1=ConditionalTest(
                player_item=item,
                amount_or_capacity=AmountOrCapacity.Capacity,
                condition=Condition.GreaterThan,
                value=0,
            ),
            conditional2=empty_test,
            conditional3=empty_test,
            conditional4=empty_test,
        )
    )


def _patch_single_pickup_stage_appearance(
    editor: PatcherEditor,
    location: PickupLocation,
    area: Area,
    stage: PickupStage,
    instances: PickupInstances,
    disable_hud_popup: bool,
) -> None:
    model_data = stage.appearance.model_data

    # pickup
    with instances.pickup.edit_properties(RDSPickup) as pickup_e:
        pickup: RDSPickup = pickup_e
        assert isinstance(pickup, RDSPickup)

        # basics
        pickup.model = editor.resolve_asset_id(model_data.model)
        pickup.auto_spin = model_data.auto_spin

        # transform
        old_pos = location.original_model.get_position(editor)
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
        pickup.actor_information.scannable.scannable_info0 = editor.create_simple_scan(
            stage.appearance.scan, model=editor.resolve_asset_id(model_data.scan_model)
        )
        area._parent_mlvl.savw.raw.scannable_objects.append(
            {
                "scan_asset_id": pickup.actor_information.scannable.scannable_info0,
                "logbook_category": 0,
            }
        )

    # ETM particle
    if model_data.model == ETM_MODEL:
        layer = location.get_layer(area)
        _attach_etm_particle_and_sound(instances.pickup, layer)

    # cutscene model
    if location.cutscene_model is not None:
        inst = area.get_instance(location.cutscene_model.instance)

        # FIXME: this does not account for progressive item models
        with inst.edit_properties(inst.script_type) as cutscene_model:
            assert isinstance(cutscene_model, ObjectWithModel)
            cutscene_model.model = editor.resolve_asset_id(model_data.model)
            cutscene_model.animation_information.ancs = model_data.animation.get_animation_parameters(editor).ancs

        if model_data.model == ETM_MODEL:
            layer = area.get_layer(location.cutscene_model.layer)
            _attach_etm_particle_and_sound(inst, layer)

    # sound
    with instances.sound.edit_properties(Sound) as sound:
        sound.sound = stage.appearance.sound

    # jingle
    with instances.streamed_audio.edit_properties(StreamedAudio) as streamed:
        streamed.song_file = stage.appearance.jingle.file_name
        streamed.volume = stage.appearance.jingle.volume

    # hud memo
    with instances.hud_memo.edit_properties(HUDMemo) as hud_memo:
        collect_string = stage.appearance.hud_text
        hud_memo.string, _ = editor.create_strg(f"Pickup{collect_string}.STRG", collect_string)

        if not disable_hud_popup:
            hud_memo.display_time = 2.5
            hud_memo.display_type = 1
        elif location.exclude_memo_from_removal:
            hud_memo.display_time = 0.1
            hud_memo.display_type = 1
        else:
            hud_memo.display_time = 4.0
            hud_memo.display_type = 0


def _patch_single_pickup_stage_basic_resources(
    location: PickupLocation,
    area: Area,
    stage: PickupStage,
    instances: PickupInstances,
) -> None:
    remaining = list(stage.resources)
    if remaining:
        first = remaining.pop(0)
    else:
        first = None

    with instances.pickup.edit_properties(RDSPickup) as pickup:
        # Every pickup always increase the percentage by 1,
        # making the total percentage count match how many pickups there are
        pickup.item_percentage_increase = 1

        if first is not None:
            pickup.item_to_give = first.item
            pickup.amount = first.amount
            pickup.capacity_increase = first.amount
        else:
            pickup.item_to_give = PlayerItemEnum.PowerBeam
            pickup.amount = 0
            pickup.capacity_increase = 0

    layer = location.get_layer(area)
    for resource in remaining:
        sf = _add_modify_inventory_sf(resource.item, resource.amount, layer)
        instances.post_pickup_relay.add_connection(State.Zero, Message.Action, sf)


def _patch_single_pickup_stage_converted_resources(
    location: PickupLocation,
    area: Area,
    stage: PickupStage,
    instances: PickupInstances,
) -> None:
    layer = location.get_layer(area)

    conversion = [pair.as_tuple for pair in stage.conversion]

    for from_item, to_item in conversion:
        relay = _add_relay(layer)
        conditional = add_conditional_relay(from_item, False, layer)

        subtract_from = _add_modify_inventory_sf(from_item, -1, layer)
        add_to = _add_modify_inventory_sf(to_item, 1, layer)

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
    editor: PatcherEditor,
    location: PickupLocation,
    area: Area,
    stage: PickupStage,
    instances: PickupInstances,
    disable_hud_popup: bool,
) -> None:
    _patch_single_pickup_stage_appearance(
        editor,
        location,
        area,
        stage,
        instances,
        disable_hud_popup,
    )

    _patch_single_pickup_stage_basic_resources(
        location,
        area,
        stage,
        instances,
    )

    _patch_single_pickup_stage_converted_resources(
        location,
        area,
        stage,
        instances,
    )

    for connection in location.connections:
        instances.post_pickup_relay.add_connection(
            connection.state,
            connection.message,
            connection.target,
        )


def _add_map_icon(editor: PatcherEditor, mlvl: Mlvl, area: Area, instances: PickupInstances) -> None:
    mapa_id = mlvl.mapw.get_mapa_id(area.index)
    mapa = editor.get_file(mapa_id, Mapa)

    mappable_id = instances.mappable_object.id
    with instances.pickup.edit_properties(RDSPickup) as pickup:
        pos = pickup.editor_properties.transform.position

    mapa.mappable_objects.append(
        MappableObject.create(
            object_type=0x12,  # custom icon type for pickups
            visibility_mode=ObjectVisibility.AreaVisitOrMapStation,
            editor_id=mappable_id,
            transform=[
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
        )
    )


def patch_simple_pickup(
    modification: PickupModification,
    editor: PatcherEditor,
    mlvl: Mlvl,
    area: Area,
    disable_hud_popup: bool,
) -> None:
    instances = modification.location.prepare_instances(area)

    _patch_single_pickup_stage(
        editor, modification.location, area, modification.primary_stage, instances, disable_hud_popup
    )
    _add_map_icon(editor, mlvl, area, instances)

    for removal in modification.location.removals:
        area.remove_instance(removal)


def patch_complex_pickup(
    modification: PickupModification,
    editor: PatcherEditor,
    mlvl: Mlvl,
    area: Area,
    disable_hud_popup: bool,
) -> None:
    instances = modification.location.prepare_instances(area)
    original_instances = instances

    original_pickup = copy.deepcopy(original_instances.pickup.get_properties_as(RDSPickup))

    # patch the first stage, as well as stage-agnostic changes like the map icon
    patch_simple_pickup(modification, editor, mlvl, area, disable_hud_popup)

    pickup_starts_active = original_instances.pickup.get_properties_as(RDSPickup).editor_properties.active

    layer = modification.location.get_layer(area)

    previous_conditional: ScriptInstance | None = None

    for i, stage in enumerate(modification.progressive_stages):
        # create new instances for this stage
        previous_instances = instances
        instances = original_instances.new_stage(layer, i + 1, original_pickup)

        # create the ConditionalRelay and looping Timer used to update to the correct stage
        conditional = add_conditional_relay(
            stage.required_item,
            False,
            layer,
            name=f"Check item requirement (stage {i + 1})",
            active=False,
        )
        looping_timer = layer.add_instance_with(
            Timer(
                editor_properties=EditorProperties(
                    name=f"Loop item requirement check (stage {i + 1})",
                ),
                time=0.01,
                auto_reset=True,
                auto_start=True,
            )
        )

        conditional.add_connection(State.Open, Message.Deactivate, previous_instances.pickup)
        conditional.add_connection(State.Open, Message.Activate, instances.pickup)
        conditional.add_connection(State.Open, Message.Deactivate, looping_timer)

        looping_timer.add_connection(State.Zero, Message.SetToZero, conditional)

        if previous_conditional is None:
            if pickup_starts_active:
                # first stage pickup is active at the start, so activate the conditionalrelay at the start too
                with conditional.edit_properties(ConditionalRelay) as relay:
                    relay.editor_properties.active = True
            else:
                # first stage pickup is inactive at the start, so make anything that activates it
                # also activate the conditional relay
                for inst in area.all_instances:
                    for connection in tuple(inst.connections):
                        if connection.target == previous_instances.pickup.id and connection.message == Message.Activate:
                            inst.add_connection(connection.state, Message.Activate, conditional)
        else:
            # subsequent stages should only begin checking after the previous stage activates
            previous_conditional.add_connection(State.Open, Message.Activate, conditional)

        # deactivate immediately to prevent you from picking up the next stage simultaneously
        previous_instances.pickup.add_connection(State.Arrived, Message.Deactivate, conditional)
        previous_instances.pickup.add_connection(State.Arrived, Message.Deactivate, looping_timer)

        # also deactivate via the memory relay, to preserve state
        instances.memory_relay.add_connection(State.Active, Message.Deactivate, conditional)
        instances.memory_relay.add_connection(State.Active, Message.Deactivate, looping_timer)

        _patch_single_pickup_stage(editor, modification.location, area, stage, instances, disable_hud_popup)

        previous_conditional = conditional
