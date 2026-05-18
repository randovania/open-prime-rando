from __future__ import annotations

from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats.script_object import Connection
from retro_data_structures.properties.echoes.archetypes.Connection import Connection as SequenceConnection
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.LayerSwitch import LayerSwitch
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import (
    Camera,
    Counter,
    IngSpiderballGuardian,
    MemoryRelay,
    Relay,
    ScriptLayerController,
    SequenceTimer,
    Switch,
    Timer,
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


@decorate_patcher(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.DYNAMO_WORKS_MREA)
def dynamo_works_dynamic_layer_loading(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Dynamically loads/unloads layers so Spider Guardian
    can always be accessible, separate a huge amount of
    objects to a dedicated layer to be unloaded during the
    fight to save memory, then adjust scripting accordingly
    to compensate for the changes.
    """
    # Add new layer to separate "Default" layer objects from
    dump_during_battle = area.add_layer("Dump During Battle")

    # Add new layer for the inner CameraHint objects
    # to only load when player is inside arena
    tunnel_hints = area.add_layer("Tunnel Hints", active=False)

    # Remove Spider Guardian entrance blocker
    area.remove_instance("1st Pass Spiderball Guardian Blocker")

    # List of objects to separate from "Default" layer
    for dumpInstances in _MOVE_TO_DUMP_DURING_BATTLE:
        area.move_instance(dumpInstances, "Dump During Battle")

    # CameraHint objects
    for camerahint_instances in _MOVE_TO_TUNNEL_HINTS:
        area.move_instance(camerahint_instances, "Tunnel Hints")

    # Objects that belong in Spider Guardian layer that are on Default
    for sgInstances in _MOVE_TO_SPIDER_GUARDIAN:
        area.move_instance(sgInstances, "Spiderball Guardian (Dynamic unload)")

    # Move BLOW CRATE Generator to Default so Spider Guardian
    # crates have Debris when destroyed
    area.move_instance("BLOW CRATE", "Default")

    # Make Boss Intro Cinematic layer active by default so that
    # Spider Guardian can always be fought
    area.get_layer("Boss Intro Cinematic").active = True

    # Make Spider Guardian be active by default since layer now
    # gets Dynamically loaded, also change it's initial position
    # to match it's unedited final position with these new changes
    spider_guardian = area.get_instance("IngSpiderballGuardian 001")
    with spider_guardian.edit_properties(IngSpiderballGuardian) as spider_guardian_props:
        spider_guardian_props.editor_properties.active = True
        spider_guardian_props.editor_properties.transform.position.y += 3.0
        spider_guardian_props.editor_properties.transform.position.z += 2.0
        spider_guardian_props.editor_properties.transform.rotation = Vector(0.0, 90.0, 0.0)

    # Define Objects
    boss_dead_relay = area.get_instance("Boss Dead")
    boss_intro_relay = area.get_instance("[IN] Start Boss Intro Cinematic")
    layer_swap_trigger = area.get_instance("Layer Swap - 1st Pass to Spiderball Guardian")
    tunnel_in_entrance = area.get_instance("Camera Tunnel In Enter Master")
    tunnel_in_portal = area.get_instance("Camera To Pickup Enter")
    intro_sequence_timer = area.get_instance("Boss Intro Cinematic Sequence")
    spider_guardian_controller1 = area.get_instance("06_Cliff - Increment Spiderball Guardian (Dynamic Unload)")
    spider_guardian_controller2 = area.get_instance(
        "06_Cliff - Spiderball Guardian"
    )  # Spiderball Guardian (Nondynamic Decrement)
    spider_guardian_gone_controller = area.get_instance("Increment  - 06_Cliff - Spiderball Guardian Gone")
    boss_intro_controller = area.get_instance("06_Cliff - Boss Intro Cinematic")
    sg_intro_camera = area.get_instance("BI - CameraShot 001")
    ing_music = area.get_instance("Ing Large")
    sanc_music = area.get_instance("Cliffside Two")
    music_player = area.get_instance("Music Player For Area")
    boss_intro_camera = area.get_instance("BI - CameraShot 001")
    spider_new_patrol_waypoint = area.get_instance(0x140069)

    # Make the Intro Camera not immediately look near the
    # arena to hide the layer objects popping into existance
    with boss_intro_camera.edit_properties(Camera) as camera:
        knot = camera.motion_control_spline.knots[1]
        knot.amplitude = 0.17

    # Change Spider Guardian's initial starting
    # AIWaypoint to fit it's new position
    spider_connections = list(spider_guardian.connections)
    spider_connections[1] = Connection(State.Patrol, Message.Follow, spider_new_patrol_waypoint.id)
    spider_guardian.connections = spider_connections

    # Make the following Layer Controllers be Dynamic
    for layer_controller in (
        boss_intro_controller,
        spider_guardian_controller1,
        spider_guardian_controller2,
        spider_guardian_gone_controller,
    ):
        with layer_controller.edit_properties(ScriptLayerController) as layer_controller_props:
            layer_controller_props.is_dynamic = True
    # Add new Objects

    # This will be used to load or unload the Quads layer
    # when activating / clearing Spider Guardian
    quads_dynamic_controller = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Increment / Decrement 1st Pass (Dynamic)",
                transform=Transform(position=Vector(165.0, 228.0, -18.0), scale=Vector(2.0, 2.0, 2.0)),
            ),
            is_dynamic=True,
            layer=LayerSwitch(
                area_id=sanctuary_fortress.DYNAMO_WORKS_INTERNAL_ID, layer_number=area.get_layer("1st Pass").index
            ),
        )
    )

    # Controller for getting rid of Unnecesary Objects during the Spider Guardian fight
    dump_during_battle_controller = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Increment / Decrement Dump During Battle (Dynamic)",
                transform=Transform(position=Vector(173.0, 228.3, -19.3), scale=Vector(2.0, 2.0, 2.0)),
            ),
            is_dynamic=True,
            layer=LayerSwitch(
                area_id=sanctuary_fortress.DYNAMO_WORKS_INTERNAL_ID, layer_number=dump_during_battle.index
            ),
        )
    )

    # Controller for Camera Hint objects layer, only
    # active when inside Spider Guardian arena
    tunnel_hints_controller = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Increment / Decrement Tunnel Hints (Dynamic)",
                transform=Transform(position=Vector(174.5, 228.3, -19.3), scale=Vector(2.0, 2.0, 2.0)),
            ),
            is_dynamic=True,
            layer=LayerSwitch(area_id=sanctuary_fortress.DYNAMO_WORKS_INTERNAL_ID, layer_number=tunnel_hints.index),
        )
    )

    # Counter for checking the intro related Layers that finished loading
    sg_layer_loading_counter = area.get_layer("Default").add_instance_with(
        Counter(
            editor_properties=EditorProperties(
                name="Spider Guardian Layer Count",
                transform=Transform(position=Vector(177.0, 228.3, -18.3), scale=Vector(2.0, 2.0, 2.0)),
            ),
            initial_count=0,
            max_count=3,
        )
    )

    # Counter for checking the post Spider Guardian related Layers that finished loading
    post_sg_layer_loading_counter = area.get_layer("Default").add_instance_with(
        Counter(
            editor_properties=EditorProperties(
                name="Post Spider Guardian Layer Count",
                transform=Transform(position=Vector(177.0, 228.3, -17.0), scale=Vector(2.0, 2.0, 2.0)),
            ),
            initial_count=0,
            max_count=3,
            auto_reset=True,
        )
    )

    # Load checker, once counter is Max, this opens and resumes the fight Intro
    sg_layer_loading_switch = area.get_layer("Default").add_instance_with(
        Switch(
            editor_properties=EditorProperties(
                name="Load Check",
                transform=Transform(position=Vector(177.0, 228.3, -19.3), scale=Vector(2.0, 2.0, 2.0)),
            )
        )
    )

    # Retry timer for if the load check fails
    layer_check_retry_timer = area.get_layer("Default").add_instance_with(
        Timer(
            editor_properties=EditorProperties(
                name="Try again", transform=Transform(position=Vector(178.0, 228.3, -19.3), scale=Vector(2.0, 2.0, 2.0))
            ),
            time=0.02,
        )
    )
    # Triggers for Incrementing/Decrementing Tunnel Hints layer controller
    tunnel_out_entrance = area.get_layer("Default").add_instance_with(
        Trigger(
            editor_properties=EditorProperties(
                name="Tunnel Exit Entrance (For Controller)",
                transform=Transform(position=Vector(198.6, 161.0, -6.8), scale=Vector(13.0, 1.0, 7.0)),
            )
        )
    )

    tunnel_in_tube = area.get_layer("Default").add_instance_with(
        Trigger(
            editor_properties=EditorProperties(
                name="Tunnel Entry Tube (For Controller)",
                transform=Transform(position=Vector(251.4, 226.0), scale=Vector(1.5, 0.5, 1.5)),
            )
        )
    )

    tunnel_out_tube1 = area.get_layer("Default").add_instance_with(
        Trigger(
            editor_properties=EditorProperties(
                name="Tunnel Exit Tube Master (For Controller)",
                transform=Transform(position=Vector(252.0, 226.0, -3.0), scale=Vector(5.0, 23.5, 1.0)),
            )
        )
    )

    tunnel_out_tube2 = area.get_layer("Default").add_instance_with(
        Trigger(
            editor_properties=EditorProperties(
                name="Tunnel Exit Tube Slave (For Controller)",
                transform=Transform(position=Vector(254.0, 226.0, 1.1), scale=Vector(1.0, 23.0, 7.0)),
            )
        )
    )

    # Relay that allows the 1st Pass layer (Quads) to be activated if room
    # has not been traversed yet, controlled by a MemoryRelay
    quads_layer_change_check = area.get_layer("Default").add_instance_with(
        Relay(
            editor_properties=EditorProperties(
                name="Allow 1st Pass",
                transform=Transform(position=Vector(165.0, 228.0, -17.0), scale=Vector(2.0, 2.0, 2.0)),
            )
        )
    )

    # Memory Relay that is activated after touched the layer change Trigger
    # next to the quads, once active it will deny other layer loads from
    # Incrementing this layer controller again
    layer_switch_memory_relay = area.get_layer("Default").add_instance_with(
        MemoryRelay(
            editor_properties=EditorProperties(
                name="1st Pass Deactivated",
                transform=Transform(position=Vector(164.0, 228.0, -17.0), scale=Vector(2.0, 2.0, 2.0)),
            )
        )
    )

    # Make Intro stop music instead of playing Ing music (It
    # will now play Ing Battle when the load checker passes)
    relay_connections = list(boss_intro_relay.connections)
    relay_connections[5] = Connection(State.Zero, Message.Stop, sanc_music.id)
    boss_intro_relay.connections = relay_connections

    # Remove Spider Guardian layer switch trigger connections
    trigger_connections = list(layer_swap_trigger.connections)
    layer_swap_trigger.remove_connection(trigger_connections[0])  # Increment -> Spider Guardian Controller (Dynamic)
    layer_swap_trigger.remove_connection(trigger_connections[3])  # Increment -> Boss Intro Cinematic
    layer_swap_trigger.remove_connection(trigger_connections[4])  # Increment -> Spider Guardian (Nondynamic)

    # Tunnel Hints Layer Loading
    tunnel_in_entrance.add_connection(State.Entered, Message.Increment, tunnel_hints_controller)
    tunnel_out_entrance.add_connection(State.Entered, Message.Decrement, tunnel_hints_controller)
    tunnel_in_portal.add_connection(State.Entered, Message.Increment, tunnel_hints_controller)
    tunnel_in_tube.add_connection(State.Entered, Message.Increment, tunnel_hints_controller)
    tunnel_out_tube1.add_connection(State.Entered, Message.Decrement, tunnel_hints_controller)
    tunnel_out_tube2.add_connection(State.Connect, Message.Attach, tunnel_out_tube1)
    music_player.add_connection(State.Exited, Message.Decrement, tunnel_hints_controller)
    tunnel_hints_controller.add_connection(State.Arrived, Message.Play, tunnel_hints_controller)

    # Make Quads layer not get Incremented dynamically after Spider Guardian
    # If already went through the room normally on the 1st Pass
    layer_swap_trigger.add_connection(State.Entered, Message.Activate, layer_switch_memory_relay)
    layer_switch_memory_relay.add_connection(State.Active, Message.Deactivate, quads_layer_change_check)
    layer_switch_memory_relay.add_connection(State.Active, Message.Increment, post_sg_layer_loading_counter)
    quads_layer_change_check.add_connection(State.Zero, Message.Increment, quads_dynamic_controller)

    # Toggle necesary layers once Spider Guardian is activated
    boss_intro_relay.add_connection(State.Zero, Message.Decrement, quads_dynamic_controller)
    boss_intro_relay.add_connection(State.Zero, Message.Decrement, dump_during_battle_controller)
    boss_intro_relay.add_connection(State.Zero, Message.Increment, spider_guardian_controller1)
    boss_intro_relay.add_connection(State.Zero, Message.Increment, spider_guardian_controller2)

    # Layer loads check for Intro

    # Layers Increment counter once finished loading
    tunnel_hints_controller.add_connection(State.Arrived, Message.Increment, sg_layer_loading_counter)
    spider_guardian_controller1.add_connection(State.Arrived, Message.Increment, sg_layer_loading_counter)
    spider_guardian_controller2.add_connection(State.Arrived, Message.Increment, sg_layer_loading_counter)

    # Sequence connection to fire the Spider Guardian related layers check during Intro
    with intro_sequence_timer.edit_properties(SequenceTimer) as sequence_timer:
        sequence_timer.sequence_connections.append(
            SequenceConnection(
                connection_index=4,
                activation_times=[1.0],
            )
        )
    intro_sequence_timer.add_connection(State.Sequence, Message.SetToZero, sg_layer_loading_switch)

    # Load Check Switch, once all layers are loaded
    # it's opened and resumes the Intro / Starts the fight
    sg_layer_loading_switch.add_connection(State.Closed, Message.ResetAndStart, layer_check_retry_timer)
    sg_layer_loading_switch.add_connection(State.Closed, Message.Stop, intro_sequence_timer)
    sg_layer_loading_switch.add_connection(State.Closed, Message.Stop, sg_intro_camera)
    layer_check_retry_timer.add_connection(State.Zero, Message.SetToZero, sg_layer_loading_switch)
    sg_layer_loading_counter.add_connection(State.MaxReached, Message.Open, sg_layer_loading_switch)
    sg_layer_loading_switch.add_connection(State.Open, Message.Play, spider_guardian_controller1)
    sg_layer_loading_switch.add_connection(State.Open, Message.Play, spider_guardian_controller2)
    sg_layer_loading_switch.add_connection(State.Open, Message.Play, intro_sequence_timer)
    sg_layer_loading_switch.add_connection(State.Open, Message.Play, ing_music)
    sg_layer_loading_switch.add_connection(State.Open, Message.Start, sg_intro_camera)

    # Load target layers once Spider Guardian is dead
    boss_dead_relay.add_connection(State.Zero, Message.Increment, dump_during_battle_controller)
    boss_dead_relay.add_connection(State.Zero, Message.SetToZero, quads_layer_change_check)

    # Controller connections to Counter
    spider_guardian_gone_controller.add_connection(State.Arrived, Message.Increment, post_sg_layer_loading_counter)
    quads_dynamic_controller.add_connection(State.Arrived, Message.Increment, post_sg_layer_loading_counter)
    dump_during_battle_controller.add_connection(State.Arrived, Message.Increment, post_sg_layer_loading_counter)

    # Once all layers are done loading, send Play via Counter
    post_sg_layer_loading_counter.add_connection(State.MaxReached, Message.Play, spider_guardian_gone_controller)
    post_sg_layer_loading_counter.add_connection(State.MaxReached, Message.Play, quads_dynamic_controller)
    post_sg_layer_loading_counter.add_connection(State.MaxReached, Message.Play, dump_during_battle_controller)


_MOVE_TO_DUMP_DURING_BATTLE = [
    "Magnet (Left)",
    "Magnet (Right)",
    "Magnet (Right)",
    "Does Player Have Spiderball?",
    "Inactive Spiderball Track",
    "Active Spiderball Track",
    "Ring Sound Volumetric North 1",
    "Ring Sound Volumetric North 2",
    "Ring Sound Volumetric South 1",
    "Ring Sound Volumetric South 2",
    "Big Rings South",
    "Big Rings North",
    0x1403C9,  # RoomAcoustic Trigger
    "Effect Light Rays",
    "Enter Portal",
    "Active Portal Scan Target",
    "Rift Portal Scan Target",
    "WARP OUT",
    0x1400DA,  # SHOCK
    "Force Player Away",
    "Render Bounds for Rift",
    "Look at Rift Sounds",
    "Sound - Dark Rift Creak, Big",
    "Sound - Rumble",
    "Dark Portal Open",
    "Sound - Dark Rift Close",
    "PORTAL TO RIFT ",
    "RIFT ",
    "Shoot to activate PORTAL",
    "RIFT TO PORTAL",
    "Portal Map Location",
    "Dark Portal",
    "RIFT Portal Scan",
    "ACTIVE Portal Scan",
    "Sound - Dark Rift Base",
    "Sound - Dark Rift Voices (ViewFrustum)",
    "Sound - Dark Rift Open",
    "Sound - Dark Rift Creak, Small 2",
    "Sound - Dark Rift Creak, Small",
    "Sound - Dark Portal",
    "To DarkWorld",
    "Arrival",
    "Player Control Disable Length",
    "Portal Arrival Effect",
    0x1400C5,
    "Portal Arrival Sound",
    0x140277,
    "[IN] Begin Transition",
    "[OUT] Perform Transition",
    "Stop Dark Rift Sounds",
    "Start Dark Rift Sounds",
    "Dark Rift Creak Sounds",
    "Timer - Play Creak Big (ViewFrustum)",
    0x1400C0,  # Cinematic Camera 001
    0x1400AB,  # c1 path1
    "c1 path2",
    "c1 path3",
    "c1 path4",
    "c1 path5",
    "c1 path6",
    "c1 path7",
    0x1400B7,  # PlayerActor Samus
    0x1400B6,  # c1 target1
    "RadialDamage 001",
    0x1400DB,  # SHOCK
    "PORTAL DUST",
    "Effect Tunnel Clouds",
    "PORTAL TO RIFT CONTROLLER",
    "Camera Tunnel Out Enter Master",
    "Camera Tunnel Out Exit Master",
    "Tunnel Out",
    "Path Camera 002",
    "Tunnel Out Path 001",
    "Tunnel Out Path 002",
    "Tunnel Out Path 003",
    "Tunnel Out Path 005",
    "Tunnel Out Path 006",
    "Tunnel Out Path 007",
    "Tunnel Out Player 009",
    "Tunnel Out Player 007",
    "Tunnel Out Player 006",
    "Tunnel Out Player 005",
    "Tunnel Out Player 004",
    "Tunnel Out Player 003",
    "Tunnel Out Player 002",
    "Tunnel Out Player 001",
    0x140107,  # Camera Tunnel Out Exit Slave 001
    0x140112,  # Camera Tunnel Out Exit Slave 002
    "Camera Show Pickup",
    "Show Pickup",
    "Tunnel In",
    "Camera Tunnel In Enter Master",
    "Camera Tunnel In Exit Master",
    "Path Camera 001",
    "Path Camera 004",
    "CameraWaypoint 017",
    "CameraWaypoint 018",
    "CameraWaypoint 019",
    "CameraWaypoint 020",
    "CameraWaypoint 021",
    "CameraWaypoint 022",
    "CameraWaypoint 023",
    "CameraWaypoint 024",
    0x140379,  # Cliff Crate
    0x14037A,  # Cliff Crate
    0x14037B,  # Cliff Crate
    "Pickup Generator High",
]

_MOVE_TO_TUNNEL_HINTS = [
    "Camera Tunnel In Exit Slave 001",
    "Camera Tunnel In Enter Slave 001",
    "Camera Tunnel In Enter Slave 002",
    "Camera Tunnel In Exit Slave 002",
    "Spiderball Guardian Battle",
    "Inside Puzzle 1",
    "Camera Puzzle 1 Enter",
    "Camera Puzzle 1 Exit",
    "Camera Puzzle 1 to Puzzle 2 Exit",
    "Camera Puzzle 1 to Puzzle 2 Enter",
    "Camera Puzzle 2 Enter",
    "Camera Puzzle 2 Exit",
    "Camera Puzzle 2 Right Drop in Enter",
    "Camera Puzzle 2 Right Drop in Exit",
    "Inside Puzzle 2 & 3",
    "Camera Puzzle 2 to Puzzle 3 Enter",
    "Camera Puzzle 2 to Puzzle 3 Exit",
    0x140236,  # Camera Halfpipe Exit
    0x140235,  # Camera Halfpipe Enter
    0x14023D,  # Lookat Spline North 001
    0x14022E,  # Lookat Spline North 002
    0x14023E,  # Lookat Spline North 003
    0x140231,  # Lookat Spline South 001
    0x140229,  # Lookat Spline South 002
    0x140233,  # Lookat Spline South 001
    0x140237,  # Lookat Spline Base
    0x14023B,  # Player Spline 001
    0x14022D,  # Player Spline 002
    0x14023A,  # Player Spline 003
    0x140232,  # Player Spline 004
    0x140238,  # Player Spline 005
    0x14022B,  # Player Spline 006
    0x14023C,  # Player Spline 007
    0x140258,  # Player Spline 001
    0x140248,  # Player Spline 002
    0x140254,  # Player Spline 003
    0x140247,  # Player Spline 004
    0x140245,  # Player Spline 005
    0x140251,  # Player Spline 006
    0x14025A,  # Player Spline 007
    "Camera Puzzle 3 Exit",
    "Camera Puzzle 3 Enter",
    0x140255,  # Camera Halfpipe Exit
    0x140257,  # Camera Halfpipe Enter
    0x14024B,  # Lookat Spline North 001
    0x140259,  # Lookat Spline North 002
    0x14024A,  # Lookat Spline North 003
    0x14024F,  # Lookat Spline Base
    0x140250,  # Lookat Spline South 003
    0x14024E,  # Lookat Spline South 002
    0x140244,  # Lookat Spline South 001
    "Camera Spiderball Exit Slave 001",
    "Camera Spiderball Enter Slave 001",
    "Camera Spiderball Exit Master",
    "Camera Spiderball Enter Master",
    "Inside Puzzle 4, 5, & 6",
    0x1400E8,  # Puzzle 1
    0x1400AE,  # Puzzle 1
    0x14023F,  # West
    0x14022C,  # West Path
    "Puzzle 2",
    0x140126,  # Puzzle 1 to Puzzle 2
    "Enter Puzzle 1",
    "Halfpipe 2 Drop in",
    0x1403A9,  # Puzzle 2 to 3
    0x140106,  # Puzzle 2 to 3
    "Surface Camera 004",
    "Spiderball Out",
    "Surface Camera 005",
    "Puzzle 3",
    0x14024C,  # West
    0x140256,  # West Path
    "Surface Camera 006",
    "Spiderball Out Fixed",
    0x14022A,  # Halfpipe West
    0x140253,  # Halfpipe West
    0x14022F,  # Halfpipe East
    0x140239,  # East
    0x140230,  # East Path
    0x14024D,  # East
    0x140252,  # Halfpipe East
    0x140249,  # East Path
    0x140246,  # Player Has Boost
    0x140234,  # Player Has Boost
]

_MOVE_TO_SPIDER_GUARDIAN = [
    "Area 1-001",
    "Area 1-002",
    "Area 1-003",
    "Area 1-004",
    "Area 1-005",
    "Area 1-Damage",
    "Area 2-001",
    "Area 2-002",
    "Area 2-003",
    "Area 2-004",
    "Area 2-005",
    "Area 2-006",
    "Area 2-007",
    "Area 2-008",
    "Area 2-009",
    "Area 2-010",
    "Area 2-Damage",
    "Area 3-001",
    "Area 3-002",
    "Area 3-003",
    "Area 3-004",
    "Area 3-005",
    "Area 3-006",
    "Area 3-007",
    "Area 3-008",
    "Area 3-009",
    "Area 3-Damage",
    "Area 4-001",
    "Area 4-002",
    "Area 4-003",
    "Area 4-004",
    "Area 4-005",
    "Area 4-006",
    "Area 4-007",
    "Area 4-008",
    "Area 4-009",
    "Area 4-010",
    "Area 4-011",
    "Area 4-012",
    "Area 4-043",
    "Area 4-044",
    "Area 4-025",
    "Area 4-042",
    "Area 4-024",
    "Area 4-021",
    "Area 4-022",
    "Area 4-013",
    "Area 4-014",
    "Area 4-015",
    "Area 4-016",
    "Area 4-017",
    "Area 4-018",
    "Area 4-019",
    "Area 4-020",
    "Area 4-045",
    "Area 4-034",
    "Area 4-033",
    "Area 4-032",
    "Area 4-026",
    "Area 4-027",
    "Area 4-028",
    "Area 4-029",
    "Area 4-030",
    "Area 4-031",
    "Area 4-035",
    "Area 4-036",
    "Area 4-037",
    "Area 4-038",
    "Area 4-039",
    "Area 4-040",
    "Area 4-041",
]
