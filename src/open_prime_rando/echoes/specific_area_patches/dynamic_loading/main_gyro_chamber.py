from __future__ import annotations

from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.properties.echoes.archetypes.Connection import Connection as SequenceConnection
from retro_data_structures.properties.echoes.objects import (
    ScriptLayerController,
    SequenceTimer,
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


@decorate_patcher(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.MAIN_GYRO_CHAMBER_MREA)
def main_gyro_chamber_dynamic_layer_loading(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Dynamically loads "Echo Door" layer after
    solving Puzzle 2, then adjust scripting
    accordingly to compensate for the changes.
    """
    # Make layer controller be dynamic
    puzzle_2_controller = area.get_instance("Decrement - 07_Cliff - Rubik's - Puzzle 2")
    with puzzle_2_controller.edit_properties(ScriptLayerController) as controller1_props:
        controller1_props.editor_properties.name += " (Dynamic)"
        controller1_props.is_dynamic = True

    # Remove immediate decrement of controllers
    puzzle_2_solved = area.get_instance("Puzzle 2 solved")
    puzzle_2_solved_connections = list(puzzle_2_solved.connections)
    puzzle_2_solved.remove_connection(puzzle_2_solved_connections[5])
    puzzle_2_solved.remove_connection(puzzle_2_solved_connections[8])

    # Add a layer load/unloading for Echo Door layer
    puzzle_2_sequence_timer = area.get_instance(0x2402AA)  # Close both doors
    echo_door_dynamic_controller = area.get_instance("Decrement - 07_Cliff - Echo Door puzzle layer (Dynamic)")
    puzzles_1_sequence_timer = area.get_instance("Unload Puzzle 1 / Load Puzzle 2 (Dynamic)")

    # Add sequence timer with existing's properties
    echo_door_sequence_timer = area.get_layer("Rubik's - Base Objects").add_instance_with(
        puzzles_1_sequence_timer.get_properties()
    )

    # Change it's name
    with echo_door_sequence_timer.edit_properties(SequenceTimer) as sequence_timer:
        sequence_timer.editor_properties.name = "Unload Puzzle 2 / Load Echo Lock"
        sequence_timer.editor_properties.transform.position.y -= 2.0

    # Add new sequence connection to load/unload layers
    with puzzle_2_sequence_timer.edit_properties(SequenceTimer) as sequence_timer2:
        sequence_timer2.sequence_connections.append(
            SequenceConnection(
                connection_index=20,
                activation_times=[6.0],
            ),
        )

    # Move Echo Door Platform waypoints to the door's origin layer so it actually moves
    area.move_instance("(Gate) Echo Gate Waypoint - UP", "Echo Door (Gate)")
    area.move_instance("(Gate) Echo Gate Waypoint - DOWN", "Echo Door (Gate)")

    # Connections
    puzzle_2_sequence_timer.add_connection(State.Sequence, Message.Start, echo_door_sequence_timer)
    echo_door_sequence_timer.add_connection(State.Sequence, Message.Increment, echo_door_dynamic_controller)
    echo_door_sequence_timer.add_connection(State.Sequence, Message.Decrement, puzzle_2_controller)
    echo_door_dynamic_controller.add_connection(State.Arrived, Message.Play, echo_door_dynamic_controller)
