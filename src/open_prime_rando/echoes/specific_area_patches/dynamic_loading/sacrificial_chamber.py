from __future__ import annotations

from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats.script_object import Connection
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.LayerSwitch import LayerSwitch
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import (
    CameraShaker,
    Relay,
    ScriptLayerController,
    Trigger,
)

from open_prime_rando.area_patcher import decorate_patcher
from open_prime_rando.echoes.asset_ids import torvus_bog
from open_prime_rando.echoes.asset_ids.world import (
    TORVUS_BOG_MLVL,
)

if TYPE_CHECKING:
    from retro_data_structures.formats.mlvl import Mlvl
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.patcher_editor import PatcherEditor


@decorate_patcher(TORVUS_BOG_MLVL, torvus_bog.SACRIFICIAL_CHAMBER_MREA)
def sacrificial_chamber_static_floor(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Remove fake Grapple Guardian and prevent floor from lowering.
    """
    # Define objects
    raise_gates_relay = area.get_instance("Raise gates")
    entered_from_top_relay = area.get_instance("Entered from top floor")
    fight_trigger = area.get_instance("Begin battle")
    # Remove 2nd Pass
    area.remove_instance("2nd pass cage down")

    # Move 1st Pass floor stuff to Default
    for move in _TO_DEFAULT:
        area.move_instance(move, "Default")

    # Make "Entered from Top/Bottom" stuff active by
    # Default (Hunter Ing, Grapple Guardian trigger)
    with area.get_instance("Spawn Pool Ings").edit_properties(Relay) as hunter_ings_relay:
        hunter_ings_relay.editor_properties.active = True

    with fight_trigger.edit_properties(Trigger) as trigger_props:
        trigger_props.editor_properties.active = True

    # Remove fight trigger deactivation connection, deactivate top Ing Trigger
    entered_from_top_relay.remove_connection(entered_from_top_relay.connections[1])
    spawn_ings_top = area.get_instance("Spawn Medium Ings - South")
    entered_from_top_relay.add_connection(State.Entered, Message.Deactivate, spawn_ings_top)

    # Delete Ing if touched Fight Trigger
    first_pass_ing = area.add_layer("1st Pass Hunter Ing")
    area.move_instance("MediumIng 1st Pass", "1st Pass Hunter Ing")

    lower_ing_controller = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Unload 1st Pass Hunter Ing",
                transform=Transform(
                    position=Vector(-204.0, 88.5, -25.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            layer=LayerSwitch(area_id=torvus_bog.SACRIFICIAL_CHAMBER_INTERNAL_ID, layer_number=first_pass_ing.index),
            is_dynamic=True,
        )
    )
    fight_trigger.add_connection(State.Entered, Message.Decrement, lower_ing_controller)

    # Make south gate opening have shake and rumble
    shaker = area.get_instance("rumble of cage lowering")
    with shaker.edit_properties(CameraShaker) as shaker_props:
        shaker_props.shaker_data.duration = 1.3
    raise_gates_relay.add_connection(State.Zero, Message.Action, shaker)

    # Raise gates instead of Cage lower sequence
    cage_lowering_sequence = area.get_instance("Cage Lowering Cinema")
    sequence_connections = list(cage_lowering_sequence.connections)
    sequence_connections[2] = Connection(State.Sequence, Message.SetToZero, raise_gates_relay.id)
    cage_lowering_sequence.connections = sequence_connections

    # Delete instances, including fake Grapple Guardian
    # and elements related to floor moving
    for obj in _TO_REMOVE:
        area.remove_instance(obj)


_TO_DEFAULT = [
    "floor",
    "ledge",
    "gateNorth",
    "northFrame",
    "southFrame",
    "doorBlockEast",
    "doorBlockWest",
    0x3B0203,  # East gibs top
    0x3B0211,  # East gibs middle
    0x3B0214,  # East gibs left
    0x3B0210,  # East gibs right
    0x3B01F8,  # West gibs top
    0x3B01F9,  # West gibs middle
    0x3B01D2,  # West gibs left
    0x3B01D5,  # West gibs right
]

_TO_REMOVE = [
    "Entered from bottom floor",
    "Fake Patrolling GrappleGuardian",
    "Chance to play an animation",
    "Choose animation to play",
    "Fake Grenchler Sniff",
    "Fake Grenchler Shake",
    "Fake Grenchler Alert",
    "Waypoint 042",
    "Waypoint 043",
    "Waypoint 044",
    "Waypoint 045",
    "Waypoint 046",
    "Waypoint 047",
    "Waypoint 048",
    "Waypoint 049",
    "Waypoint 050",
    "Waypoint 051",
    "Waypoint 052",
    "Waypoint 053",
    "Waypoint 054",
    "Waypointcc 042",
    "Waypointcc 043",
    "Waypointcc 044",
    "Waypointcc 045",
    "Waypointcc 046",
    "Waypointcc 047",
    "Waypointcc 048",
    "Waypointcc 049",
    "Waypointcc 050",
    "Waypointcc 051",
    "Waypointcc 052",
    "Waypointcc 053",
    "Waypointcc 054",
    "GateNorth high",
    "Gate Stop North",
    "Gates Moving Loop North",
    "gateNorth atFloor",
    "gateNorth under",
    "North Gate Stop Timer",
    "Ledge low",
    "Ledge high",
    "Cage mid",
    "Cage low",
    "southFrame_after",
    "ledge_after",
    "northFrame_after",
    "floor_after",
    "doorBlockWest_after",
    "doorBlockEast_after",
    0x3B0213,  # East gibs top
    0x3B0219,  # East gibs middle
    0x3B0217,  # East gibs left
    0x3B0204,  # East gibs right
    0x3B01D8,  # West gibs top
    0x3B01D3,  # West gibs middle
    0x3B01CF,  # West gibs left
    0x3B01FF,  # West gibs right
    0x3B0083,  # Camera Shaker 001
    0x3B022A,  # Rotating Blockade Loop
    0x3B0232,  # Rotating Blockade Loop
]
