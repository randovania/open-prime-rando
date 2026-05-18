from __future__ import annotations

from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.LayerSwitch import LayerSwitch
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import (
    ScriptLayerController,
    StreamedAudio,
    Trigger,
)

from open_prime_rando.area_patcher import decorate_patcher
from open_prime_rando.echoes.asset_ids import sanctuary_fortress
from open_prime_rando.echoes.asset_ids.world import (
    SANCTUARY_FORTRESS_MLVL,
)

if TYPE_CHECKING:
    from retro_data_structures.formats.mlvl import Mlvl
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.patcher_editor import PatcherEditor


@decorate_patcher(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.MAIN_RESEARCH_MREA)
def main_research_dynamic_layer_loading(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Disables the Contraption layer by default, activating it dynamically when exiting the lower portal.
    This hopefully prevents OOM/object list full crashes.
    """
    # Make layer be inactive by default
    area.get_layer("Contraption").active = False

    # Rename this existing object
    contraption_layer_switch = area.get_instance("DYNAMIC Decrement Contraption")
    contraption_layer_switch.name = "DYNAMIC Increment / Decrement Contraption"

    # Add new Controller for the Spider Ball stuff, this layer
    # gets incremented in Staging Area already but for room
    # rando purposes, dynamically increment here as well
    spider_controller = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Dynamic Increment Column Spiderball",
                transform=Transform(position=Vector(-18.5, 150.6, -134.7), scale=Vector(2.0, 2.0, 2.0)),
            ),
            layer=LayerSwitch(
                area_id=sanctuary_fortress.MAIN_RESEARCH_INTERNAL_ID,
                layer_number=area.get_layer("Column Spiderball").index,
            ),
            is_dynamic=True,
        )
    )

    # Same issue as previous layer controller
    first_pass_controller = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Dynamic Decrement 1st Pass Enemies",
                transform=Transform(position=Vector(-20, 150.6, -134.7), scale=Vector(2.0, 2.0, 2.0)),
            ),
            layer=LayerSwitch(
                area_id=sanctuary_fortress.MAIN_RESEARCH_INTERNAL_ID,
                layer_number=area.get_layer("1st Pass Enemies").index,
            ),
            is_dynamic=True,
        )
    )

    # Define objects
    portal_spawn = area.get_instance(0xB0056)
    initial_spiderball_trigger = area.get_instance(0xB015B)
    short_battle_sAudio = area.get_instance("Short Battle (INACTIVE)")
    demo_contraption_trigger = area.get_instance("Start Demo Contraption")
    contraption_encounter_trigger = area.get_instance("Start Contraption Encounter")
    memory_relay = area.get_instance("Unlock 0l")

    # These objects get activated/deactivated upon lower portal spawn
    # arrival, but since the layer they're from gets incremented dynamically
    # upon spawn they won't receive said messages, so we're updating their
    # default status from the start
    with initial_spiderball_trigger.edit_properties(Trigger) as trigger1:
        trigger1.editor_properties.active = True
    with short_battle_sAudio.edit_properties(StreamedAudio) as sAudio:
        sAudio.editor_properties.active = True
    with demo_contraption_trigger.edit_properties(Trigger) as trigger2:
        trigger2.editor_properties.active = False
    with contraption_encounter_trigger.edit_properties(Trigger) as trigger3:
        trigger3.editor_properties.active = True

    # Activate/Deactivate layers upon lower portal arrival
    portal_spawn.add_connection(State.Zero, Message.Decrement, first_pass_controller)
    portal_spawn.add_connection(State.Zero, Message.Increment, spider_controller)
    portal_spawn.add_connection(State.Zero, Message.Increment, contraption_layer_switch)
    spider_controller.add_connection(State.Arrived, Message.Play, spider_controller)
    contraption_layer_switch.add_connection(State.Arrived, Message.Play, contraption_layer_switch)

    # Make memory relay deactivate controller objects
    # so the caretaker stuff doesn't load again
    memory_relay.add_connection(State.Active, Message.Deactivate, contraption_layer_switch)
    memory_relay.add_connection(State.Active, Message.Deactivate, spider_controller)
    memory_relay.add_connection(State.Active, Message.Deactivate, first_pass_controller)
