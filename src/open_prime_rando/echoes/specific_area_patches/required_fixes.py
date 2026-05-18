from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats.script_object import Connection
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.LayerSwitch import LayerSwitch
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import (
    IngSpiderballGuardian,
    Pickup,
    Relay,
    ScriptLayerController,
    SequenceTimer,
    SpawnPoint,
    Splinter,
    Switch,
    Timer,
)

from open_prime_rando.area_patcher import AreaPatcher, decorate_patcher
from open_prime_rando.echoes.asset_ids import agon_wastes, great_temple, sanctuary_fortress, temple_grounds, torvus_bog
from open_prime_rando.echoes.asset_ids.world import (
    AGON_WASTES_MLVL,
    GREAT_TEMPLE_MLVL,
    SANCTUARY_FORTRESS_MLVL,
    TEMPLE_GROUNDS_MLVL,
    TORVUS_BOG_MLVL,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from retro_data_structures.formats.mlvl import Mlvl
    from retro_data_structures.formats.mrea import Area
    from retro_data_structures.formats.script_object import InstanceIdRef, InstanceRef

    from open_prime_rando.patcher_editor import PatcherEditor

LOG = logging.getLogger("echoes_patcher")


def register_all(area_patcher: AreaPatcher) -> None:
    """
    Applies changes necessary for the game to function properly.
    """

    for func in [
        mining_station_b_post_pickup_relay,
        undertemple_access_spawn_point,
        main_reactor_flashbang,
        main_reactor_stop_loads,
        sacrificial_chamber_persist_pickup,
        aerie_echo_gate,
        main_research_echo_gate,
        hive_chamber_b_remove_item_loss,
        torvus_temple_remove_effects,
        command_center_door,
        alpha_splinter,
        dynamo_works_sg_pb_response,
    ]:
        area_patcher.add_function(func)


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.MINING_STATION_B_MREA)
def mining_station_b_post_pickup_relay(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Normally this relay is activated by the cutscene, but has an incoming connection from the pickup.
    Activating it like this means the pickup will trigger the relay without the cutscene
    """
    with area.get_instance(0x80121).edit_properties(Relay) as post_pickup_relay:
        post_pickup_relay.editor_properties.active = True


@decorate_patcher(TORVUS_BOG_MLVL, torvus_bog.UNDERTEMPLE_ACCESS_MREA)
def undertemple_access_spawn_point(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Move the default spawn point in-bounds.
    """
    with area.get_instance("Spawn point 001").edit_properties(SpawnPoint) as spawn:
        spawn.editor_properties.transform.position.x = -149.25


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.MAIN_REACTOR_MREA)
def main_reactor_stop_loads(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Fixes crashes related to loading rooms before
    or during the Dark Samus 1 fight.
    """

    # Define Objects
    unload_relay = area.get_instance("Unload dock when door closed")
    spawn_point = area.get_instance("Spawn point Start DS Battle")
    intro_sequence_timer = area.get_instance("SequenceTimer Dark Samus Intro")

    # When player is in room, stop all room loading
    spawn_point.add_connection(State.Zero, Message.SetToZero, unload_relay)

    # Make SequenceTimer reposition you immediately, so triggering the fight
    # in wrong room will still properly stop room loading via AreaAutoLoadController
    with intro_sequence_timer.edit_properties(SequenceTimer) as sequence_timer:
        sequence_timer.sequence_connections[43].activation_times = [0.0]


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.MAIN_REACTOR_MREA)
def main_reactor_flashbang(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Fixes Dark Samus flashbang softlock.
    """

    # Define Objects
    ds_death_stimer = area.get_instance("Dark Samus Death Sequence Transition")
    start_death_cinema_relay = area.get_instance("[IN] Start Death Cinema")

    # Add a Looping Timer that always tries to start the Death Cinema
    # cutscene, so if Dark Samus dies before the layer is finished loading
    # it will start it when it does
    death_cutscene_load_timer = area.get_layer("Dark Samus").add_instance_with(
        Timer(
            editor_properties=EditorProperties(
                active=False,
                name="Try to start Death Cinema",
                transform=Transform(
                    position=Vector(400.0, 92.0, 4.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            time=0.02,
            auto_reset=True,
            auto_start=True,
        )
    )

    # Replace the Death Cinema start relay connection with the retry timer
    sequence_connections = list(ds_death_stimer.connections)
    sequence_connections[0] = Connection(State.Sequence, Message.Activate, death_cutscene_load_timer.id)
    ds_death_stimer.connections = sequence_connections

    # Make looping timer start the death cinema, then make death cinema deactivate timer
    death_cutscene_load_timer.add_connection(State.Zero, Message.SetToZero, start_death_cinema_relay)
    start_death_cinema_relay.add_connection(State.Zero, Message.Deactivate, death_cutscene_load_timer)


@decorate_patcher(TORVUS_BOG_MLVL, torvus_bog.SACRIFICIAL_CHAMBER_MREA)
def sacrificial_chamber_persist_pickup(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Makes the pickup persistent, even if you exit the area and reload.
    """
    with area.get_instance("If grapple attainment is loaded, then end battle").edit_properties(Switch) as switch:
        switch.is_open = True


def _patch_echo_gate_softlock(
    area: Area, counter: InstanceIdRef, relays: Iterable[tuple[InstanceIdRef, InstanceIdRef]]
):
    for shot_relay_id, memory_relay_id in relays:
        shot_relay = area.get_instance(shot_relay_id)
        memory_relay = area.get_instance(memory_relay_id)

        shot_relay.remove_all_connections_to(counter)
        memory_relay.add_connection(State.Active, Message.Increment, counter)


@decorate_patcher(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.AERIE_MREA)
def aerie_echo_gate(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Patches an echo gate softlock.
    """
    relays = ((0x410094, 0x41008D), (0x410077, 0x41007F), (0x4100B5, 0x4100B6))
    _patch_echo_gate_softlock(area, 0x4100BE, relays)

    # Decrement the Puzzle Layer once it's complete
    puzzle_controller = area.get_instance(0x410419)
    puzzle_counter = area.get_instance(0x4100BE)
    puzzle_counter.add_connection(State.MaxReached, Message.Decrement, puzzle_controller)


@decorate_patcher(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.MAIN_RESEARCH_MREA)
def main_research_echo_gate(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Patches an echo gate softlock.
    """
    relays = ((0x0B02E6, 0x0B02DE), (0x0B0303, 0x0B030D), (0x0B02F6, 0x0B02FA))
    _patch_echo_gate_softlock(area, 0x0B0315, relays)


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.HIVE_CHAMBER_B_MREA)
def hive_chamber_b_remove_item_loss(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Removes item loss sequence.
    """
    area.get_layer("DS Appears Part1").active = False
    area.get_layer("Pre Dark Samus Music").active = False

    area.get_layer("Pickup").active = True
    area.get_layer("Post Dark Samus Music").active = True


@decorate_patcher(TORVUS_BOG_MLVL, torvus_bog.TORVUS_TEMPLE_MREA)
def torvus_temple_remove_effects(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Remove cosmetic objects from Torvus Temple to minimize the chance of crash via alloc failure
    """
    to_remove: list[InstanceRef] = []

    for name in (
        "Thrust1",
        "Thrust2",
        "Looping Thrust w/Doppler",
        "SwampCrateDebris",
        "GENERATE GIBS",
    ):
        for layer in area.all_layers:
            to_remove.extend(layer.get_all_instances_with_name(name))

    for obj in to_remove:
        area.remove_instance(obj)


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.COMMAND_CENTER_MREA)
def command_center_door(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Opening the blast door normally requires a room reload after they've been closed.
    The DS cutscene in Security Station B reloads the room, but that cutscene has been removed.
    """
    default = area.get_layer("Default")

    poi = default.get_instance("Blast Door Activation")

    # Deactivate layers
    for layer in ("1st Pass Scripting", "1st pass parts"):
        controller = default.add_instance_with(
            ScriptLayerController(
                editor_properties=EditorProperties(
                    name=f"DYNAMIC Decrement {layer}",
                ),
                layer=LayerSwitch(
                    area_id=0xAA657163,
                    layer_number=area.get_layer(layer).index,
                ),
                is_dynamic=True,
            )
        )
        poi.add_connection(State.ScanDone, Message.Decrement, controller)

    # Ensure the blast door instances are active for the cutscene
    for instance in ("Upper Blast Door", "Lower Blast Door"):
        poi.add_connection(
            State.ScanDone,
            Message.Activate,
            default.get_instance(instance),
        )


@decorate_patcher(GREAT_TEMPLE_MLVL, great_temple.TEMPLE_SANCTUARY_MREA)
def alpha_splinter(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Patches Alpha Splinter to take damage properly from Power Bombs.
    Also makes the Pickup fade in, rather than pop in.
    """
    with area.get_instance("MEGA Splinter Light").edit_properties(Splinter) as alpha:
        custom_rule = editor.get_custom_asset("custom_knockback.RULE")
        assert custom_rule is not None
        alpha.patterned.knockback_rules = custom_rule
        alpha.ing_possession_data.ing_vulnerability.power_bomb.damage_multiplier = 3000.0

    with area.get_instance("Pickup Object").edit_properties(Pickup) as pickup:
        pickup.fadetime = 1.0


@decorate_patcher(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.DYNAMO_WORKS_MREA)
def dynamo_works_sg_pb_response(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Fix Spider Guardian's response to PBs.
    """
    with area.get_instance("IngSpiderballGuardian 001").edit_properties(IngSpiderballGuardian) as spider:
        custom_rule = editor.get_custom_asset("custom_knockback.RULE")
        assert custom_rule is not None
        spider.patterned.knockback_rules = custom_rule
