from __future__ import annotations

from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats.script_object import Connection
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.LayerSwitch import LayerSwitch
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import (
    Counter,
    ScriptLayerController,
    Switch,
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


@decorate_patcher(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.AERIE_MREA)
def aerie_dynamic_layer_loading(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Dynamically loads/unloads layers so a room reload is
    not necesary after battling Dark Samus 2, then adjust
    scripting accordingly to compensate for the changes.
    """
    # Move some "Default" layer objects that belong in "Elevator" layer
    for default_instances in _MOVE_TO_ELEVATOR:
        area.move_instance(default_instances, "Elevator")

    # Move "Keep Elevator Activated" MemoryRelay to Default layer
    area.move_instance(0x4100B9, "Default")

    # Define Objects
    ds2_intro_layer_switch = area.get_instance("Decrement Dark Samus Intro")
    echo_visor_layer_switch = area.get_instance("Increment - Echo Visor Attainment Cinematic")
    echo_puzzle_nondynamic_layer_switch = area.get_instance("Increment Echo Puzzle")
    elevator_layer_switch = area.get_instance("Increment Elevator")
    echo_visor_attainment_end_relay = area.get_instance("Relay Cinema End")
    ds2_intro_start_relay = area.get_instance("Relay- Start Cinema")
    ds2_intro_end_relay = area.get_instance("Relay- End Cinema")
    ds2_death_loading_control_relay = area.get_instance("Dark Samus Battle 2 Death Loading Control")
    ds2_death_end_relay = area.get_instance("Cinema - End DS Death")
    dark_samus_intro = area.get_instance("Dark Samus Intro")
    fade_in_music_timer = area.get_instance("Fade In Music")
    echo_puzzle_counter = area.get_instance("All Targets Hit")
    elevator_departure_relay = area.get_instance("[IN] Elevator Leave")
    elevator_active_memory_relay = area.get_instance("Keep Elevator Activated")
    puzzle_music_memory_relay = area.get_instance("Set Puzzle Music As Active Music")
    boss_go = area.get_instance("Boss Go")
    puzzle_music = area.get_instance("Puzzle")
    sanc_music = area.get_instance("Cliffside Two INACTIVE BY DEFAULT")

    # Delete duplicate ScriptLayerController
    area.remove_instance("Decrement - Echo Visor Attainment Cinematic")

    # Add Objects

    # Layer Loading Check
    post_ds2_layer_loading_counter = area.get_layer("Default").add_instance_with(
        Counter(
            editor_properties=EditorProperties(
                name="Layer Load Count",
                transform=Transform(position=Vector(72.0, 475.0, 183.3), scale=Vector(2.0, 2.0, 2.0)),
            ),
            initial_count=0,
            max_count=2,
        )
    )

    # Echo Puzzle layer controller for Dynamic Increment
    echo_puzzle_layer_switch = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Increment Echo Puzzle (Dynamic)",
                transform=Transform(position=Vector(75.0, 473.0, 183.5), scale=Vector(2.0, 2.0, 2.0)),
            ),
            layer=LayerSwitch(
                area_id=sanctuary_fortress.AERIE_INTERNAL_ID, layer_number=area.get_layer("Echo Visor Puzzle").index
            ),
            is_dynamic=True,
        )
    )

    # Rename the existing non-dynamic controller
    echo_puzzle_nondynamic_layer_switch.name = "Decrement Echo Visor Puzzle"

    # Music change check in case player solves puzzle before
    # getting pickup but then grabbing pickup afterwards
    echo_puzzle_music_switch = area.get_layer("Default").add_instance_with(
        Switch(
            editor_properties=EditorProperties(
                name="CLOSED: Puzzle / OPEN: Cliffside Two",
                transform=Transform(position=Vector(100.8, 430.5, 181.0), scale=Vector(2.0, 2.0, 2.0)),
            )
        )
    )

    # Make the following ScriptLayerController objects be Dynamic
    for layer_switch in (ds2_intro_layer_switch, elevator_layer_switch):
        with layer_switch.edit_properties(ScriptLayerController) as layer_switches:
            layer_switches.editor_properties.name += " (Dynamic)"
            layer_switches.is_dynamic = True

    with echo_visor_layer_switch.edit_properties(ScriptLayerController) as layer_switches2:
        layer_switches2.editor_properties.name = "Increment/Decrement Echo Visor Attainment Cinematic (Dynamic)"
        layer_switches2.is_dynamic = True

    # Make the Echo Visor Attainment Cinema End relay Decrement
    # the same layer controller instead of the duplicate one
    echo_visor_attainment_end_relay.add_connection(State.Zero, Message.Decrement, echo_visor_layer_switch)

    # Make Death End Relay stop music instead of playing Boss Go otherwise sounds won't play
    ds2_death_end_relay_connections = list(ds2_death_end_relay.connections)
    ds2_death_end_relay_connections[2] = Connection(State.Zero, Message.Stop, dark_samus_intro.id)
    ds2_death_end_relay.connections = ds2_death_end_relay_connections

    # Load/Play Elevator load on Intro Start/End
    ds2_intro_start_relay.add_connection(State.Zero, Message.Increment, elevator_layer_switch)
    ds2_intro_end_relay.add_connection(State.Zero, Message.Play, elevator_layer_switch)

    # Remove layer control connections...
    death_control_connections = list(ds2_death_loading_control_relay.connections)
    ds2_death_loading_control_relay.remove_connection(
        death_control_connections[2]
    )  # Increment/Decrement Echo Visor Attainment Cinematic (Dynamic)
    ds2_death_loading_control_relay.remove_connection(death_control_connections[5])  # Increment Echo Puzzle
    ds2_death_loading_control_relay.remove_connection(death_control_connections[6])  # Increment Elevator (Dynamic)

    # ...and add to DS Death End instead...
    ds2_death_end_relay.add_connection(State.Zero, Message.Increment, echo_visor_layer_switch)
    ds2_death_end_relay.add_connection(State.Zero, Message.Increment, echo_puzzle_layer_switch)

    # ... then Play when all loaded
    echo_visor_layer_switch.add_connection(State.Arrived, Message.Increment, post_ds2_layer_loading_counter)
    echo_puzzle_layer_switch.add_connection(State.Arrived, Message.Increment, post_ds2_layer_loading_counter)
    post_ds2_layer_loading_counter.add_connection(State.MaxReached, Message.Play, echo_puzzle_layer_switch)
    post_ds2_layer_loading_counter.add_connection(State.MaxReached, Message.Play, echo_visor_layer_switch)
    post_ds2_layer_loading_counter.add_connection(State.MaxReached, Message.Play, boss_go)

    # Remove Puzzle music activation and playing connections
    # from Fade In Music timer since now it goes to Switch
    fade_in_music_timer_connections = list(fade_in_music_timer.connections)
    fade_in_music_timer.remove_connection(fade_in_music_timer_connections[3])
    fade_in_music_timer.remove_connection(fade_in_music_timer_connections[4])

    # Music Status check connections
    echo_puzzle_music_switch.add_connection(State.Closed, Message.Activate, puzzle_music_memory_relay)
    echo_puzzle_music_switch.add_connection(State.Closed, Message.Activate, puzzle_music)
    echo_puzzle_music_switch.add_connection(State.Closed, Message.Play, puzzle_music)
    echo_puzzle_music_switch.add_connection(State.Open, Message.Play, sanc_music)

    # Connections to Music Status check
    fade_in_music_timer.add_connection(State.Zero, Message.SetToZero, echo_puzzle_music_switch)
    echo_puzzle_counter.add_connection(State.MaxReached, Message.Open, echo_puzzle_music_switch)
    elevator_active_memory_relay.add_connection(State.Active, Message.Open, echo_puzzle_music_switch)

    # Make Elevator Departure play Sanc music
    # again in case Dark Commandos were active
    elevator_departure_relay.add_connection(State.Zero, Message.Play, sanc_music)


_MOVE_TO_ELEVATOR = [
    0x4100FB,  # [SequenceTimer] Departure Cine
    0x4100F5,  # [PlayerActor] Samus
    0x4100FC,  # [Camera] Departure
    0x410116,  # [CameraWaypoint] Waypoint 003
    0x410117,  # [CameraWaypoint] Waypoint 004
]
