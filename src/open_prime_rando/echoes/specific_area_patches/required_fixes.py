from __future__ import annotations

import dataclasses
import logging
from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats.script_object import Connection
from retro_data_structures.properties.echoes.archetypes.Connection import Connection as SequenceConnection
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.LayerSwitch import LayerSwitch
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import (
    IngSpiderballGuardian,
    MemoryRelay,
    Pickup,
    Relay,
    ScriptLayerController,
    SequenceTimer,
    SpawnPoint,
    SpiderBallWaypoint,
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
        aerie_echo_gate,
        main_research_echo_gate,
        hive_chamber_b_remove_item_loss,
        torvus_temple_remove_effects,
        command_center_door,
        alpha_splinter_pb_response,
        dynamo_works_sg_pb_response,
        sacrificial_chamber_persist_pickup,
        undertemple_persist_pickup,
        temple_sanctuary_persist_pickup,
        agon_temple_move_pickup,
        hive_temple_persist_pickup,
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


@decorate_patcher(TORVUS_BOG_MLVL, torvus_bog.UNDERTEMPLE_MREA)
def undertemple_persist_pickup(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Makes the pickup persistent, even if you exit the area and reload.
    """
    pickup_active = area.get_layer("Ingsporb battle").add_instance_with(
        MemoryRelay(
            editor_properties=EditorProperties(
                active=False,
                name="Keep Pickup Active",
                transform=Transform(
                    position=Vector(-159.0, -126.0, -110.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            delayed_action=True,
        )
    )
    pickup = area.get_instance(0x3C0217)
    fight_trigger = area.get_instance(0x3C0234)

    # Setup stuff for if Player left room then came back
    music_player = area.get_instance("Music Player For Area")
    dark_torvus_music = area.get_instance("Swamp Chika Dark")
    boss_go_music = area.get_instance("Boss Go")
    sporb_base = area.get_instance("SporbBase - MegaIng")
    sporb_top = area.get_instance("SporbTop - MegaIng")
    ingsporb_complete_memory_relay = area.get_instance("Ingsporb battle completed")
    death_cinema_end = area.get_instance("[OUT] End Ingsporb Death Cinema")
    post_pickup_relay = area.get_instance(0x3C021E)
    ingsporb_layer_switch_relay = area.get_instance("Handle Timer Actions")
    ingsporb_layer_switch = area.get_instance(0x3C01EC)
    release_ball_relay1 = area.get_instance(0x3C01FF)
    release_ball_relay2 = area.get_instance(0x3C01E5)
    release_ball_relay3 = area.get_instance(0x3C0209)
    release_ball_relay4 = area.get_instance(0x3C01DB)

    music_status = area.get_layer("Default").add_instance_with(
        Switch(
            editor_properties=EditorProperties(
                name="CLOSED: Swamp Chika Dark / OPEN: Boss Go",
                transform=Transform(
                    position=Vector(-154.0, -51.0, -117.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
        )
    )

    # Don't Decrement Ingsporb battle when Dead
    ingsporb_layer_switch_relay.remove_connection(ingsporb_layer_switch_relay.connections[1])

    # Decrement on Post Pickup instead
    post_pickup_relay.add_connection(State.Zero, Message.Decrement, ingsporb_layer_switch)

    # Activate MemoryRelay when dead
    death_cinema_end.add_connection(State.Zero, Message.Activate, pickup_active)

    # Activate Pickup, setup music
    pickup_active.add_connection(State.Active, Message.Activate, pickup)
    death_cinema_end.add_connection(State.Zero, Message.Open, music_status)
    pickup_active.add_connection(State.Active, Message.Open, music_status)
    post_pickup_relay.add_connection(State.Zero, Message.Close, music_status)

    # Deactivate Fight stuff
    ingsporb_complete_memory_relay.add_connection(State.Active, Message.Deactivate, sporb_base)
    ingsporb_complete_memory_relay.add_connection(State.Active, Message.Deactivate, sporb_top)
    ingsporb_complete_memory_relay.add_connection(State.Active, Message.Deactivate, fight_trigger)
    ingsporb_complete_memory_relay.add_connection(State.Active, Message.SetToZero, release_ball_relay1)
    ingsporb_complete_memory_relay.add_connection(State.Active, Message.SetToZero, release_ball_relay2)
    ingsporb_complete_memory_relay.add_connection(State.Active, Message.SetToZero, release_ball_relay3)
    ingsporb_complete_memory_relay.add_connection(State.Active, Message.SetToZero, release_ball_relay4)

    # Move Slider platforms to retracted position
    for sliders in (0x3C035B, 0x3C035E, 0x3C035D, 0x3C035C):
        ingsporb_complete_memory_relay.add_connection(State.Active, Message.Next, sliders)

    # Keep Boss Go music if player hasn't collected Pickup
    music_player.remove_connection(music_player.connections[0])
    music_player.add_connection(State.Entered, Message.SetToZero, music_status)
    music_status.add_connection(State.Closed, Message.Play, dark_torvus_music)
    music_status.add_connection(State.Open, Message.Play, boss_go_music)


@decorate_patcher(GREAT_TEMPLE_MLVL, great_temple.TEMPLE_SANCTUARY_MREA)
def temple_sanctuary_persist_pickup(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Makes the pickup persistent once spawned, even if you
    exit the area and reload. This also makes it so the fight
    can be activated again if reloaded room and returned.
    """
    pickup = area.get_instance(0x20127)
    sequence_timer1 = area.get_instance("Unload Splinter Snatch / Load Boss Snatch (Dynamic)")
    sequence_timer2 = area.get_instance("Unload Boss Snatch / Load Boss Death (Dynamic)")
    turn_on_walls_relay = area.get_instance(0x2006A)
    with turn_on_walls_relay.edit_properties(Relay) as old_relay_props:
        old_relay_pos = old_relay_props.editor_properties.transform.position
    cinema_start_relay = area.get_instance(0x201AF)
    cinema_end_relay = area.get_instance(0x20198)

    # MemoryRelay for Pickup
    pickup_active = area.get_layer("Default").add_instance_with(
        MemoryRelay(
            editor_properties=EditorProperties(
                active=False,
                name="Keep Pickup Active",
                transform=Transform(
                    position=Vector(0.970526, -44.557369, -14.398048),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            delayed_action=True,
        )
    )

    # non-dynamic layer controllers for room reload purposes
    splinter_snatch_controller = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Increment Splinter Snatch Cinematic",
                transform=Transform(position=Vector(-66.4, -42.0, -17.0), scale=Vector(2.0, 2.0, 2.0)),
            ),
            layer=LayerSwitch(
                area_id=great_temple.TEMPLE_SANCTUARY_INTERNAL_ID,
                layer_number=area.get_layer("Splinter Snatch Cinematic").index,
            ),
        )
    )

    boss_snatch_controller = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Decrement Boss Snatch Cinematic",
                transform=Transform(position=Vector(-69.3, -43.8, -17.3), scale=Vector(2.0, 2.0, 2.0)),
            ),
            layer=LayerSwitch(
                area_id=great_temple.TEMPLE_SANCTUARY_INTERNAL_ID,
                layer_number=area.get_layer("Boss Snatch Cinematic").index,
            ),
        )
    )

    boss_dead_controller = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Decrement Boss Death Cinematic",
                transform=Transform(position=Vector(-66.4, -46.0, -17.0), scale=Vector(2.0, 2.0, 2.0)),
            ),
            layer=LayerSwitch(
                area_id=great_temple.TEMPLE_SANCTUARY_INTERNAL_ID,
                layer_number=area.get_layer("Boss Death Cinematic").index,
            ),
        )
    )

    # Activate/Deactivate Pickup MemoryRelay
    cinema_start_relay.add_connection(State.Zero, Message.Activate, pickup_active)
    cinema_end_relay.add_connection(State.Zero, Message.Deactivate, pickup_active)

    # MemoryRelay connections
    pickup_active.add_connection(State.Active, Message.Activate, pickup)

    # Setup Stuff for when player leaves mid fight / post fight:

    # Toggle layers non-dynamically after they're (un)loaded
    with sequence_timer1.edit_properties(SequenceTimer) as timer1:
        timer1.editor_properties.name = (
            "Unload Splinter Snatch / Load Boss Snatch (Dynamic) / Decrement Boss Snatch / Increment Splinter Snatch"
        )
        timer1.sequence_connections.extend(
            [
                SequenceConnection(
                    connection_index=2,
                    activation_times=[3.0],
                ),
                SequenceConnection(
                    connection_index=3,
                    activation_times=[3.0],
                ),
            ]
        )
    sequence_timer1.add_connection(State.Sequence, Message.Decrement, boss_snatch_controller)
    sequence_timer1.add_connection(State.Sequence, Message.Increment, splinter_snatch_controller)

    with sequence_timer2.edit_properties(SequenceTimer) as timer2:
        timer2.editor_properties.name = "Unload Boss Snatch / Load Boss Death (Dynamic) / Decrement Boss Death"
        timer2.sequence_connections.append(
            SequenceConnection(
                connection_index=2,
                activation_times=[3.0],
            ),
        )
    sequence_timer2.add_connection(State.Sequence, Message.Decrement, boss_dead_controller)

    # Setup layers again if killed Dark Alpha Splinter
    cinema_start_relay.add_connection(State.Zero, Message.Increment, boss_dead_controller)
    cinema_start_relay.add_connection(State.Zero, Message.Decrement, boss_snatch_controller)
    cinema_start_relay.add_connection(State.Zero, Message.Decrement, splinter_snatch_controller)

    # Activate wall barriers instead of Fade them in by copying the
    # existing connections of the wall fader relay, and replacing
    # "Increment" message with "Activate"
    new_turn_on_walls_relay = area.get_layer("Default").add_instance_with(
        Relay(
            editor_properties=EditorProperties(
                name="Activate Walls for Room Reload",
                transform=Transform(position=old_relay_pos + Vector(1.0, 0.0, 0.0), scale=Vector(2.0, 2.0, 2.0)),
            )
        )
    )
    new_walls_relay_connections = list(turn_on_walls_relay.connections)
    new_walls_relay_connections[0:8] = [
        dataclasses.replace(conn, message=Message.Activate) for conn in new_walls_relay_connections[0:8]
    ]
    new_turn_on_walls_relay.connections = new_walls_relay_connections
    pickup_active.add_connection(State.Active, Message.SetToZero, new_turn_on_walls_relay)


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

    # Removing this object will cause the env var to be removed from the SAVW, which causes
    # CPersistentOptions::FindEnvironmentVariable to return NULL, which is handled by the game as show the button.
    area.remove_instance("Enable Darkworld Automapper button")


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
def alpha_splinter_pb_response(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
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


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.AGON_TEMPLE_MREA)
def agon_temple_move_pickup(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Move the Bomb Guardian pickup off of the generated objects layer.
    Being on this layer causes unpredictable behavior when patching the pickup.
    """
    first_pass = area.get_layer("1st pass enemy_Bomb Boss")

    # we have to move it to Default first, to change the layer ID.
    # instances on SCGN have the same ID as they would if they were on
    # another layer, and in this case that's the layer we're moving to.
    # without this extra move, the instance doesn't actually get moved
    area.move_instance("Morph Ball Bomb", "Default")
    area.move_instance("Morph Ball Bomb", first_pass.name)

    pickup = area.get_instance("Morph Ball Bomb")

    relay = first_pass.add_instance_with(
        Relay(
            editor_properties=EditorProperties(name="Activate Bomb Pickup"),
            one_shot=False,
        )
    )
    relay.add_connection(State.Zero, Message.Activate, pickup)

    generator = area.get_instance("Generate Bomb Pickup")
    unswarm_effects = area.get_instance("Unswarm Effects")

    unswarm_effects.replace_connections_to(generator, relay)
    area.remove_instance(generator)


@decorate_patcher(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.HIVE_TEMPLE_MREA)
def hive_temple_persist_pickup(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Makes the pickup persistent, even if you exit the area and reload.
    """
    # Define objects
    quadraxis = area.get_instance("DigitalGuardianHead 001")
    pickup = area.get_instance("Annihilator Beam")
    post_pickup = area.get_instance("Post Pickup")
    spiderball_platform_end_relay = area.get_instance("[OUT] End Spiderball Platform Activation")

    # Move crippled body actor to a dedicated layer
    # so there's no need to have everything related
    # to quad loaded for the pickup to be active
    # thus making the room load be shorter
    boss_body_layer = area.add_layer("Boss Body")

    boss_body_controller_dynamic = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Unload Boss Body",
                transform=Transform(position=Vector(239.8, 30.6, -32.7), scale=Vector(2.0, 2.0, 2.0)),
            ),
            layer=LayerSwitch(
                area_id=sanctuary_fortress.HIVE_TEMPLE_INTERNAL_ID,
                layer_number=boss_body_layer.index,
            ),
            is_dynamic=True,
        )
    )
    area.move_instance("Crippled Body", "Boss Body")

    # And the SpiderBallWaypoints
    boss_layer = area.get_layer("CliffsideBoss")
    for instance in list(boss_layer.instances):
        if instance.script_type == SpiderBallWaypoint:
            area.move_instance(instance, "Boss Body")

    # Unload Layer after getting pickup
    spiderball_platform_end_relay.add_connection(State.Zero, Message.Decrement, boss_body_controller_dynamic)

    # Undo boss state from Persistent Boss patch
    # (works independantly, without the other patch this does nothing)
    boss_death_controller = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Increment/Decrement Boss Death (For Persistent Pickup)",
                transform=Transform(position=Vector(251.5, 28.0, -32.7), scale=Vector(2.0, 2.0, 2.0)),
            ),
            layer=LayerSwitch(
                area_id=sanctuary_fortress.HIVE_TEMPLE_INTERNAL_ID,
                layer_number=area.get_layer("Boss Death").index,
            ),
        )
    )
    quadraxis.add_connection(State.Dead, Message.Increment, boss_death_controller)
    quadraxis.add_connection(State.Dead, Message.Increment, area.get_instance("Decrement - Boss Music"))
    quadraxis.add_connection(State.Dead, Message.Decrement, area.get_instance("Dump Digital Guardian body"))
    quadraxis.add_connection(State.Dead, Message.Decrement, area.get_instance("DYNAMIC Dump Intro Cinematic Actors"))
    quadraxis.add_connection(
        State.Dead, Message.Decrement, area.get_instance("Decrement - 09_Cliff - CliffsideBoss (Dynamic)")
    )

    # Make Pickup persistent
    pickup_active = area.get_layer("Boss Death").add_instance_with(
        MemoryRelay(
            editor_properties=EditorProperties(
                active=False,
                name="Keep Pickup Active",
                transform=Transform(
                    position=Vector(41.758938, 66.569855, -28.637785),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            delayed_action=True,
        )
    )
    quadraxis.add_connection(State.Dead, Message.Activate, pickup_active)
    pickup_active.add_connection(State.Active, Message.Lock, area.get_instance(0x35000C))
    pickup_active.add_connection(State.Active, Message.Activate, pickup)
    pickup_active.add_connection(State.Active, Message.Activate, area.get_instance("Crippled Body"))
    pickup_active.add_connection(State.Active, Message.Deactivate, area.get_instance("Start Boss Encounter"))
    post_pickup.add_connection(State.Zero, Message.Deactivate, pickup_active)
    post_pickup.add_connection(State.Zero, Message.Decrement, area.get_instance("Decrement - Boss Music"))
    post_pickup.add_connection(State.Zero, Message.Increment, area.get_instance("Increment - Post Boss Music"))

    # Keep Boss Go music if player hasn't collected Pickup
    music_player = area.get_instance(0x350254)
    boss_prelude = area.get_instance("Swamp Mae")
    boss_go_music = area.get_instance("Boss Go")
    music_status = area.get_layer("Boss Music").add_instance_with(
        Switch(
            editor_properties=EditorProperties(
                name="CLOSED: Swamp Mae / OPEN: Boss Go",
                transform=Transform(
                    position=Vector(75.5, 130.2, -6.3),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
        )
    )
    quadraxis.add_connection(State.Dead, Message.Open, music_status)
    pickup_active.add_connection(State.Active, Message.Open, music_status)
    post_pickup.add_connection(State.Zero, Message.Close, music_status)
    music_player.remove_connection(music_player.connections[0])
    music_player.add_connection(State.Entered, Message.SetToZero, music_status)
    music_status.add_connection(State.Closed, Message.Play, boss_prelude)
    music_status.add_connection(State.Open, Message.Play, boss_go_music)
