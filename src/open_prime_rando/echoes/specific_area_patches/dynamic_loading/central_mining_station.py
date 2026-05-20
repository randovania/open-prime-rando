from __future__ import annotations

from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import (
    Actor,
    ScriptLayerController,
    SequenceTimer,
    SpecialFunction,
)
from retro_data_structures.properties.echoes.objects.SpecialFunction import Function

from open_prime_rando.area_patcher import decorate_patcher
from open_prime_rando.echoes.asset_ids import agon_wastes
from open_prime_rando.echoes.asset_ids.world import (
    AGON_WASTES_MLVL,
)

if TYPE_CHECKING:
    from retro_data_structures.formats.mlvl import Mlvl
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.patcher_editor import PatcherEditor


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.CENTRAL_MINING_STATION_MREA)
def central_mining_station_dynamic_layer_loading(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Dynamically loads/unloads layers so a room reload
    is not necesary after the pirate fight, then adjust
    scripting accordingly to compensate for the changes.
    Additionally, move certain objects to the Default layer.
    (Like the Luminoth Keybearer corpse and Turret crates)
    """

    # Move 2nd Pass objects to 1st Pass
    for instances in _MOVE_TO_DEFAULT:
        area.move_instance(instances, "Default")

    # Make upper 1st Pass Scripting Turret Holograms
    # be inactive by default, activated later on during the fight
    wave2_pirates_counter = area.get_instance("Dead Pirates All Wave 2")
    for holograms in (0x1D0246, 0x1D0247, 0x1D0052, 0x1D0056):
        wave2_pirates_counter.add_connection(State.MaxReached, Message.Increment, holograms)
        with area.get_instance(holograms).edit_properties(Actor) as hologram_props:
            hologram_props.editor_properties.active = False

    # This SequenceTimer connections changes the layers, adjust it's timing
    # so it matches the cutscene end time to then start loading layer dynamically
    barrier_down_sequence_timer = area.get_instance("LASER FENCE OFF")
    with barrier_down_sequence_timer.edit_properties(SequenceTimer) as sequence_timer:
        sequence_timer.sequence_connections[5].activation_times = [2.5]

    # Make the following layer controllers be dynamic
    first_pass_controller = area.get_instance("Decrement - 06_Sand - 1st Pass Scripting")
    second_pass_controller = area.get_instance("Increment - 06_Sand - 2nd Pass Scripting")
    for layer_switch in (first_pass_controller, second_pass_controller):
        with layer_switch.edit_properties(ScriptLayerController) as layer_switch_props:
            layer_switch_props.editor_properties.name += " (Dynamic)"
            layer_switch_props.is_dynamic = True

    # Activate layer when 2nd Pass loaded
    second_pass_controller.add_connection(State.Arrived, Message.Play, second_pass_controller)

    # Stop room loading during the fight as to not make dynamic
    # layer loading stagger, resume once 2nd Pass is loaded

    # Load stopper SpecialFunction
    stop_room_loading_sf = area.get_layer("Default").add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(
                name="AreaAutoLoadController",
                transform=Transform(
                    position=Vector(160.0, -100.0, 10.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            function=Function.AreaAutoLoadController,
        )
    )

    # Force player Inbounds on the 1st frame, then stop loading, for oob purposes
    intro_sequence_timer = area.get_instance("Start Skiff cinematic")
    with intro_sequence_timer.edit_properties(SequenceTimer) as sequence_timer:
        sequence_timer.sequence_connections[0].activation_times = [0.0]

    post_intro_spawn = area.get_instance(0x1D02B0)
    post_intro_spawn.add_connection(State.Zero, Message.Stop, stop_room_loading_sf)

    # Resume room loading when 2nd Pass is finished loading
    second_pass_controller.add_connection(State.Arrived, Message.Start, stop_room_loading_sf)

    # Remove layer change relay forcing a room reload on Central Station Access
    # since the AreaAutoLoadController is now stopping room loading
    layer_change_relay = area.get_instance("Set up post-pirate battle layers")
    layer_change_relay.remove_connection(layer_change_relay.connections[4])


_MOVE_TO_DEFAULT = [
    "Falling Skiff",
    "Destructible Rack",
    "Destructible Tank 1",
    "Destructible Tank 2",
    "Destructible Tank 3",
    "Destructible blast door",
    "Dead Luminoth 2 KeyBearer",
    "Destructible tank destroyed",
    "Destructible tank destroyed; blast door destroyed",
    "Destructible tank destroyed; destructible rack destroyed; skiff on ground",
    0x1D0354,  # blocker
    0x1D02DA,  # Waypoint 003
    0x1D0022,  # Waypoint 003
]
