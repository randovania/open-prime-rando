from __future__ import annotations

import collections
import functools
from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, PlayerItemEnum, State
from retro_data_structures.properties.base_property import BaseObjectType, ObjectWithEditorProperties
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.LayerSwitch import LayerSwitch
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.core.Color import Color
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import (
    Actor,
    DamageableTrigger,
    DamageableTriggerOrientated,
    DynamicLight,
    MemoryRelay,
    Platform,
    ScriptLayerController,
    SequenceTimer,
    Sound,
    SpawnPoint,
    Timer,
    Trigger,
    TriggerEllipsoid,
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
from open_prime_rando.echoes.pickups.pickup_editing import add_conditional_relay

if TYPE_CHECKING:
    from collections.abc import Iterable

    from retro_data_structures.formats.mlvl import Mlvl
    from retro_data_structures.formats.mrea import Area
    from retro_data_structures.formats.script_object import InstanceId, InstanceRef

    from open_prime_rando.patcher_editor import PatcherEditor


def register_all(area_patcher: AreaPatcher) -> None:
    """
    Applies patches that rebalance aspects of the game for a better rando experience.
    """
    register_barrier_removals(area_patcher)
    register_gate_key_scans(area_patcher)

    for func in [
        landing_site_remove_intro,
        hive_access_tunnel_translator_gate,
        bionergy_production_pirates_trigger,
        hive_tunnel_webbing,
        agon_temple_door_locks,
        temple_sanctuary_emerald_gate,
        main_reactor_post_ds_layer_changes,
        torvus_temple_barrier,
        torvus_temple_translator_gate,
        torvus_energy_controller_fight_layers,
        gfmc_compound_gate,
        sanctuary_entrance_keybearer,
        main_reactor_keybearer,
        gfmc_compound_ship_pickup,
        judgment_pit_gfmc_layer,
        hive_chamber_a_dmt_active,
        agon_temple_dmt_layer,
        dark_oasis_ing_cache,
        security_station_b_activate_gates,
        dynamo_chamber_non_dangerous,
        trooper_security_station_non_dangerous,
        sacred_bridge_non_dangerous,
        transport_c_access_crystal,
        grand_abyss_robots,
    ]:
        area_patcher.add_function(func)


def _disable_layer_controllers(editor: PatcherEditor, mlvl: Mlvl, area: Area, layer_controllers: Iterable[InstanceRef]):
    for inst in layer_controllers:
        with area.get_instance(inst).edit_properties(ScriptLayerController) as controller:
            controller.editor_properties.active = False


def register_barrier_removals(area_patcher: AreaPatcher) -> None:
    """
    Removes Luminoth barriers.
    """
    barriers_to_remove = {
        (AGON_WASTES_MLVL, agon_wastes.AGON_ENERGY_CONTROLLER_MREA): [
            "Increment - 07_Temple - Luminoth Barrier Swamp",
        ],
        (AGON_WASTES_MLVL, agon_wastes.DARK_AGON_ENERGY_CONTROLLER_MREA): [
            "Increment - 0A_Sand_Hall - Luminoth Barriers",
        ],
        (TORVUS_BOG_MLVL, torvus_bog.TORVUS_ENERGY_CONTROLLER_MREA): [
            "Increment - 07_Temple - Luminoth Barrier Cliffs",
        ],
        (TORVUS_BOG_MLVL, torvus_bog.DARK_TORVUS_ENERGY_CONTROLLER_MREA): [
            "Increment - 0A_Swamp - Luminoth Barriers",
            "Increment - 04_Swamp - Luminoth Barriers",
        ],
        (SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.HIVE_ENERGY_CONTROLLER_MREA): [
            "Increment - 0P_Cliff - Luminoth Barriers",
            "Increment - 0A_Cliff - Luminoth Barriers",
            "Increment - 0Q_Cliff - Luminoth Barriers",
        ],
    }

    for (mlvl_id, mrea_id), layer_controllers in barriers_to_remove.items():
        area_patcher.add_raw_function(
            mlvl_id,
            mrea_id,
            functools.partial(
                _disable_layer_controllers,
                layer_controllers=layer_controllers,
            ),
        )


def register_gate_key_scans(area_patcher: AreaPatcher) -> None:
    """
    Remove all the gate key scans except for the "No Keys" variant,
    in all three areas with a dark temple gate.
    """
    areas = [
        (AGON_WASTES_MLVL, agon_wastes.DARK_AGON_TEMPLE_MREA),
        (TORVUS_BOG_MLVL, torvus_bog.DARK_TORVUS_TEMPLE_MREA),
        (SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.HIVE_TEMPLE_ACCESS_MREA),
    ]

    for mlvl_id, mrea_id in areas:

        @decorate_patcher(mlvl_id, mrea_id)
        def remove_gate_key_scans(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
            pois = [
                area.get_instance(poi_name)
                for poi_name in ("POI - No Keys", "POI - 1 Key", "POI - 2 Keys", "POI - 3 Keys")
            ]
            for counter_name in ("1 Key", "2 Key", "3 Key"):
                counter = area.get_instance(counter_name)
                for poi in pois:
                    counter.remove_all_connections_to(poi)

        area_patcher.add_function(remove_gate_key_scans)


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.LANDING_SITE_MREA)
def landing_site_remove_intro(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Removes the intro cinematic.
    """
    area.get_layer("1st Pass - Intro Cinematic").active = False
    for layer_name in ("Save Station Load", "Ship Repair", "Luminoth Key Bearer", "WAR CHEST"):
        area.get_layer(layer_name).active = True

    spawn = area.get_instance("E3 Spawn Point")
    with spawn.edit_properties(SpawnPoint) as props:
        props.editor_properties.active = False

    timer = area.get_layer("Default").add_instance_with(Timer(time=0.01, auto_start=True))
    for inst in ("Keep Samus Ship", "Savestation Recharge Always Plays", "Ambient Music Memory Relay"):
        timer.add_connection(State.Zero, Message.Activate, area.get_instance(inst))


def get_all_ids_related_to(area: Area, target: InstanceId) -> set[InstanceId]:
    """
    Gets all object ids that send a message to, or receives a message from the target object, or any object involved.
    """

    obj_conn_to: dict[InstanceId, set[InstanceId]] = collections.defaultdict(set)

    for instance in area.all_instances:
        for conn in instance.connections:
            obj_conn_to[conn.target].add(instance.id)

    related_objects = set()

    def add_related_objs(t_id: InstanceId) -> None:
        if t_id in related_objects:
            return

        related_objects.add(t_id)

        obj = area.get_instance(t_id)
        for c in obj.connections:
            add_related_objs(c.target)
        for c in obj_conn_to[t_id]:
            add_related_objs(c)

    add_related_objs(target)

    return related_objects


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.HIVE_ACCESS_TUNNEL_MREA)
def hive_access_tunnel_translator_gate(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Moves the translator gate to be in front of the drop to Hive Chamber A.
    """
    gate = area.get_instance("Luminoth Gate")

    target_position = Vector(32, -207, -45)
    rotation = Vector(0, 0, -60)

    root_transform = gate.get_properties_as(Platform).editor_properties.transform
    delta = target_position - root_transform.position

    for obj_id in get_all_ids_related_to(area, gate.id):
        instance = area.get_instance(obj_id)

        with instance.edit_properties(BaseObjectType) as props:
            assert isinstance(props, ObjectWithEditorProperties)
            assert isinstance(props.editor_properties, EditorProperties)
            if obj_id != gate.id:
                props.editor_properties.transform.position = (
                    props.editor_properties.transform.position.rotate(rotation, root_transform.position) + delta
                )
                props.editor_properties.transform.rotation += rotation
            else:
                props.editor_properties.transform.position = target_position
                props.editor_properties.transform.rotation = rotation


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.BIOENERGY_PRODUCTION_MREA)
def bionergy_production_pirates_trigger(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Deactivate the trigger for flying pirates after killing them all.
    """
    counter = area.get_instance("Dead Pirates")
    counter.add_connection(State.MaxReached, Message.Deactivate, area.get_instance("Turn On Flying Pirates"))


@decorate_patcher(TORVUS_BOG_MLVL, torvus_bog.TORVUS_ENERGY_CONTROLLER_MREA)
def torvus_energy_controller_fight_layers(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Don't remove the Torvus Temple fight.
    """

    _disable_layer_controllers(
        editor,
        mlvl,
        area,
        (
            "DECREMENT 04_Swamp_Temple 1st Pass",
            "Decrement - 04_Swamp_Temple - 1st Pass",
            "Increment - 04_Swamp_Temple - 2ndPass",
        ),
    )


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.HIVE_TUNNEL_MREA)
def hive_tunnel_webbing(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Immediately decrement the Webbing layer after destroying the web,
    but not dynamically, so it doesn't unload until you leave.
    """
    with area.get_instance("Timer 001").edit_properties(Timer) as timer:
        timer.time = 0.02
    with area.get_instance("Decrement - Webbing").edit_properties(ScriptLayerController) as controller:
        controller.is_dynamic = False


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.AGON_TEMPLE_MREA)
def agon_temple_door_locks(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    No longer locks the doors after the Bomb Guardian fight.
    """
    area.get_layer("Lock Doors").active = False


@decorate_patcher(GREAT_TEMPLE_MLVL, great_temple.TEMPLE_SANCTUARY_MREA)
def temple_sanctuary_emerald_gate(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Keep the Emerald gate active from the beginning.
    """
    area.remove_instance("Activate Gate ")  # Intentional

    instances_to_activate = [
        0x200A5,  # Glow For Holo 2
        0x200C4,  # Gate Holo 1
        0x200C5,  # Luminoth Gate
        0x200C9,  # Gate Holo 2
        0x200FB,  # Glow For Holo 1
    ]

    for instance_id in instances_to_activate:
        with area.get_instance(instance_id).edit_properties(BaseObjectType) as props:
            assert isinstance(props, ObjectWithEditorProperties)
            props.editor_properties.active = True

    # Sound - Translator Gate Idle
    with area.get_instance(0x200AB).edit_properties(Sound) as sound_props:
        sound_props.auto_start = True

    # Don't make trigger also activate the gate
    fight_trigger = area.get_instance(0x2000D)
    fight_start_relay = area.get_instance("Cinema Start - Splinter Snatch Cinematic")
    fight_trigger_connections = list(fight_trigger.connections)
    for connection in fight_trigger_connections[:8]:
        fight_trigger.remove_connection(connection)
    fight_trigger.add_connection(State.Entered, Message.SetToZero, fight_start_relay)

    with fight_trigger.edit_properties(TriggerEllipsoid) as trigger_props:
        trigger_props.deactivate_on_enter = True


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.MAIN_REACTOR_MREA)
def main_reactor_post_ds_layer_changes(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Change layers properly after DS1's death.
    """
    layer_switcher = area.get_instance("Switch Layers To Post-Dark Samus")
    layer_controller = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Decrement Biostorage Station 1st Pass",
                transform=Transform(
                    position=Vector(436.5, 71.5, 4.3),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            layer=LayerSwitch(
                area_id=agon_wastes.BIOSTORAGE_STATION_INTERNAL_ID,
                layer_number=3,  # 1st Pass
            ),
        )
    )
    layer_switcher.add_connection(State.Zero, Message.Decrement, layer_controller)


@decorate_patcher(TORVUS_BOG_MLVL, torvus_bog.TORVUS_TEMPLE_MREA)
def torvus_temple_barrier(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Replace the Barrier's collision model with a
    smaller one to allow access to/from Lower Torvus.
    """
    # https://i.ibb.co/W4L49TDj/torvus-temple-barrier.jpg
    barrier = area.get_instance("Laser Barrier Blocking Volume")
    with barrier.edit_properties(Actor) as barrier_props:
        barrier_props.editor_properties.transform.position = Vector(-212.0, -118.0, 43.0)
        barrier_props.editor_properties.transform.rotation = Vector(90.093697, -39.95039, 0.0)
        barrier_props.collision_model = 0x3356D256

    memory_relay = area.get_instance("Remember Beams Off")
    barrier_extension = area.get_layer("Default").add_instance_with(
        Actor(
            editor_properties=EditorProperties(
                name="Barrier Extendo",
                transform=Transform(
                    position=Vector(-217.484482, -118.0, 49.528767),
                    rotation=Vector(90.093712, -39.727413, 0.0),
                ),
            ),
            model=0x3801DE98,
            collision_model=0x3356D256,
        )
    )
    memory_relay.add_connection(State.Active, Message.Deactivate, barrier_extension)
    barrier.add_connection(State.Inactive, Message.Deactivate, barrier_extension)


@decorate_patcher(TORVUS_BOG_MLVL, torvus_bog.TORVUS_TEMPLE_MREA)
def torvus_temple_translator_gate(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Make the translator gate always active.
    """
    area.get_layer("Load After 1st Pass").active = True


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.GFMC_COMPOUND_MREA)
def gfmc_compound_gate(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Move the gate to the Default layer.
    """
    gate_instances = (
        0x2B00DB,
        0x2B00DC,
        0x2B00FF,
        0x2B0101,
        0x2B013C,
        0x2B0238,
        0x2B0288,
        0x2B02E9,
    )
    gate_instances += tuple(range(0x2B0277, 0x2B0287))

    for instance_id in gate_instances:
        area.move_instance(instance_id, "Default")


@decorate_patcher(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.SANCTUARY_ENTRANCE_MREA)
def sanctuary_entrance_keybearer(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Change the Keybearer to spawn on the Default layer, removing the Spider Guardian requirement.
    """
    area.move_instance("Dead Luminoth 4 KeyBearer", "Default")
    area.move_instance("Luminoth Light Support", "Default")


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.MAIN_REACTOR_MREA)
def main_reactor_keybearer(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Change the Keybearer to spawn on the Default layer, removing the Dark Samus 1 requirement.
    """
    area.move_instance("Dead Luminoth 3 KeyBearer ", "Default")
    area.move_instance("Luminoth Light Support", "Default")


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.GFMC_COMPOUND_MREA)
def gfmc_compound_ship_pickup(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Activate the ship pickup when the player has Space Jump,
    rather than when they defeat Jump Guardian.
    """

    default = area.get_layer("Default")
    pickup_layer = area.get_layer("Space Jump")

    # create layer controllers
    def get_controller(prefix: str) -> ScriptLayerController:
        return ScriptLayerController(
            editor_properties=EditorProperties(
                name=f"{prefix} - Space Jump (Dynamic)",
            ),
            layer=LayerSwitch(
                area_id=temple_grounds.GFMC_COMPOUND_INTERNAL_ID,
                layer_number=pickup_layer.index,
            ),
            is_dynamic=True,
        )

    decrement_controller = area.get_layer("GFT Flashback Intro").add_instance_with(get_controller("Decrement"))
    increment_controller = area.get_layer("Default").add_instance_with(get_controller("Increment"))
    increment_controller.add_connection(State.Arrived, Message.Play, increment_controller)

    # conditional relay with looping timer
    conditional = add_conditional_relay(
        item=PlayerItemEnum.SpaceJumpBoots,
        immediate=False,
        layer=default,
        name="Check for Space Jump",
    )
    timer = default.add_instance_with(
        Timer(
            editor_properties=EditorProperties(name="Looping Timer"),
            # slightly slower than usual, so there's time for the
            # memory relay to deactivate the conditional on room load
            time=0.1,
            auto_reset=True,
            auto_start=True,
        )
    )
    timer.add_connection(State.Zero, Message.SetToZero, conditional)
    conditional.add_connection(State.Open, Message.Deactivate, timer)

    # load the layer when the conditional relay fires
    conditional.add_connection(State.Open, Message.Increment, increment_controller)

    # unload the layer temporarily during the movie to save on memory
    cinema_start = area.get_instance("Cinema Start - Intro")
    cinema_start.add_connection(State.Zero, Message.Decrement, decrement_controller)

    # deactivate the looping timer at the same time so it doesn't reload the layer
    cinema_start.add_connection(State.Zero, Message.Deactivate, timer)

    # reactivate the looping timer when the Dump During Movie layer activates
    area.get_instance("Increment Dump During Movie (Dynamic)").add_connection(State.Arrived, Message.Activate, timer)

    # deactivate the conditional relay via the memory relay, to prevent duping
    memory_relay = pickup_layer.get_instance("Deactivate Pickup")
    memory_relay.add_connection(State.Active, Message.Deactivate, conditional)
    memory_relay.add_connection(State.Active, Message.Deactivate, timer)


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.JUDGMENT_PIT_MREA)
def judgment_pit_gfmc_layer(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Don't reactivate the GFMC ship pickup after Jump Guardian.
    """

    _disable_layer_controllers(editor, mlvl, area, ["Increment - 05_Temple - Space Jump"])


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.HIVE_CHAMBER_A_MREA)
def hive_chamber_a_dmt_active(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Makes the Dark Missile Trooper layers active by default, removing the Bomb Guardian requirement.
    """

    area.get_layer("Missile Trooper").active = True
    area.get_layer("Missile trooper gate").active = True


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.AGON_TEMPLE_MREA)
def agon_temple_dmt_layer(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Don't reactivate the Dark Missile Trooper layers after Bomb Guardian.
    """

    _disable_layer_controllers(
        editor,
        mlvl,
        area,
        [
            "Increment -  01_Temple_Hive01 - Missile Trooper Gate",  # [sic]
            "Increment - 01_Temple_Hive01 - Missile Trooper",
        ],
    )


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.DARK_OASIS_MREA)
def dark_oasis_ing_cache(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Activate 2nd Pass layer by default.
    """
    area.get_layer("2nd pass").active = True


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.SECURITY_STATION_B_MREA)
def security_station_b_activate_gates(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Deactivate 1st Pass and activate 2nd Pass layer by default.
    This removes the Dark Samus cutscene and makes the gates always active.
    """
    area.get_layer("1st Pass").active = False
    area.get_layer("2nd Pass").active = True


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.DYNAMO_CHAMBER_MREA)
def dynamo_chamber_non_dangerous(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Make the tunnel gates in Dynamo Chamber not close when the door gate opens.
    """
    first_pass = area.get_layer("1st Pass Scripting")

    # don't move the tunnel gates during the cutscene
    gate_sequence = area.get_instance("Gate Switch Sequence")
    gates_to_leave_up = [
        first_pass.get_instance("Platform_Gate 2"),
        first_pass.get_instance("Platform_Gate 3"),
    ]

    connections_to_skip = {
        i
        for i, conn in enumerate(gate_sequence.connections)
        if any(conn.target.matches(gate.id) for gate in gates_to_leave_up)
    }

    with gate_sequence.edit_properties(SequenceTimer) as sequence:
        sequence.sequence_connections = [
            connection
            for connection in sequence.sequence_connections
            if connection.connection_index not in connections_to_skip
        ]

    # move the door gate to dedicated layers
    gate_closed = area.add_layer("Door Gate Closed", active=True)
    gate_open = area.add_layer("Door Gate Open", active=False)

    move_to_gate_closed = [
        "Platform_Gate 1",
        "Gate 1 DOWN",
        "Gate 1 UP",
        "Gate 1 Stop Event Control",
        "Closed Gate Scan",
        "Gate Stop",
        "Sound_Open",
    ]
    move_to_gate_open = [
        0x1F00DE,  # Platform_Gate
    ]

    for inst in move_to_gate_closed:
        area.move_instance(inst, gate_closed.name)
    for inst in move_to_gate_open:
        area.move_instance(inst, gate_open.name)

    # change the layer controllers to (de)activate the new layers
    decrement_1st_pass = area.get_instance("1st pass_Decrement")
    increment_2nd_pass = area.get_instance("2nd pass_Increment")

    with decrement_1st_pass.edit_properties(ScriptLayerController) as layer_controller:
        layer_controller.layer.layer_number = gate_closed.index
    with increment_2nd_pass.edit_properties(ScriptLayerController) as layer_controller:
        layer_controller.layer.layer_number = gate_open.index


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.TROOPER_SECURITY_STATION_MREA)
def trooper_security_station_non_dangerous(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Make the gate in Trooper Security Station no longer close permanently after going through it.
    Also makes it destructible on the 1st Pass layer.
    """
    first_pass = area.get_layer("1st Pass")
    second_pass = area.get_layer("2nd Pass")

    # move gate destruction objects to first pass
    move_to_first_pass = [
        "turn off Gate for good",
        "Camera Shaker_Harsh_Short",
        "Blow up grating",
        "Broken Gate Scan",
        "Generator 003",
        "Sound 002",
    ]
    for inst in move_to_first_pass:
        area.move_instance(second_pass.get_instance(inst), first_pass.name)

    area.move_instance(second_pass.get_instance("Gate Destroyed (Switch Scan Hints)"), "Default")

    # edit 1st pass gate to be destructible
    main_gate = area.get_instance("Gate")
    main_gate.add_connection(State.Dead, Message.Action, area.get_instance("Camera Shaker_Harsh_Short"))
    main_gate.add_connection(State.Dead, Message.SetToZero, area.get_instance("Blow up grating"))
    main_gate.add_connection(State.Dead, Message.Activate, area.get_instance("Gate Destroyed (Switch Scan Hints)"))
    main_gate.add_connection(State.Dead, Message.Deactivate, main_gate)

    with main_gate.edit_properties(Platform) as gate:
        gate.vulnerability = area.get_instance("Gate Down - Locked").get_properties_as(Actor).vulnerability

    gate_destroyed_mem_relay = area.get_instance("turn off Gate for good")
    gate_destroyed_mem_relay.add_connection(State.Active, Message.Deactivate, main_gate)

    # keep the gate movement active after first time scanning it
    puzzle_active_mem_relay = first_pass.add_instance_with(
        MemoryRelay(
            editor_properties=EditorProperties(
                name="Keep Puzzle Active",
                active=False,
            ),
            delayed_action=True,
        )
    )
    gate_scan_poi = area.get_instance("Gate Control Panel Scan (1st Pass)")
    start_puzzle_relay = area.get_instance("Begin Puzzle")

    # activate memory relay when scan post is scanned
    gate_scan_poi.add_connection(State.ScanDone, Message.Activate, puzzle_active_mem_relay)
    # deactivate memory relay when gate is destroyed
    main_gate.add_connection(State.Dead, Message.Deactivate, puzzle_active_mem_relay)

    puzzle_active_mem_relay.add_connection(State.Active, Message.SetToZero, start_puzzle_relay)

    # change the layers when the gate is destroyed,
    # rather than when the puzzle is solved
    puzzle_solve_trigger = area.get_instance("Lower Gate for good")
    with puzzle_solve_trigger.edit_properties(Trigger) as trigger:
        trigger.editor_properties.active = False

    main_gate.add_connection(State.Dead, Message.Decrement, area.get_instance("Decrement 1st Pass"))
    main_gate.add_connection(State.Dead, Message.Increment, area.get_instance("Increment 2nd Pass"))

    # delete second pass gate, since second pass now activates on destruction
    area.remove_instance("Gate Down - Locked")


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.SACRED_BRIDGE_MREA)
def sacred_bridge_non_dangerous(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Open the gate in Sacred Bridge if you reach the other side after entering from GFMC.
    """
    platform_up = area.get_layer("Platform Up")

    # add a trigger at the other side of the room to lower the bridge
    show_samus_trigger = area.get_instance("Show Samus")
    show_samus_props = show_samus_trigger.get_properties_as(Trigger)
    # this trigger aligns perfectly with where we want the new one to be
    lower_bridge_trigger = platform_up.add_instance_with(show_samus_props)
    with lower_bridge_trigger.edit_properties(Trigger) as trigger:
        trigger.editor_properties.name = "Lower Bridge Automatically"
        trigger.editor_properties.active = False

        trigger.deactivate_on_enter = True

    # only activate the new trigger after entering one at the GFMC door
    gfmc_door_trigger = area.get_instance(0x310099)
    prepare_bridge_trigger = platform_up.add_instance_with(gfmc_door_trigger.get_properties())
    prepare_bridge_trigger.name = "Prepare to lower bridge automatically"
    prepare_bridge_trigger.add_connection(State.Entered, Message.Activate, lower_bridge_trigger)

    # deactivate new triggers after bridge is lowered
    bridge_relay = area.get_instance("Bridge Operation Control")
    bridge_relay.add_connection(State.Zero, Message.Deactivate, prepare_bridge_trigger)
    bridge_relay.add_connection(State.Zero, Message.Deactivate, lower_bridge_trigger)

    # make a new sequence timer that doesn't start a cutscene
    cutscene_sequence = area.get_instance("Bridge Down Control")
    no_cutscene_sequence = platform_up.add_instance_with(cutscene_sequence.get_properties())
    no_cutscene_sequence.name = "Bridge Down Control (No cutscene)"
    no_cutscene_sequence.connections = cutscene_sequence.connections

    connections_to_skip = {
        0,  # decrement cinematic bars
        1,  # increment cinematic bars
        2,  # reposition
        3,  # activate cinematic
        4,  # deactivate cinematic
        9,  # force combat visor
        11,  # show samus relay
        12,  # show samus trigger
    }
    with no_cutscene_sequence.edit_properties(SequenceTimer) as sequence:
        sequence.sequence_connections = [
            connection
            for connection in sequence.sequence_connections
            if connection.connection_index not in connections_to_skip
        ]

    # start the new sequence timer when entering the new trigger
    lower_bridge_trigger.add_connection(State.Entered, Message.Start, no_cutscene_sequence)


@decorate_patcher(GREAT_TEMPLE_MLVL, great_temple.TRANSPORT_C_ACCESS_MREA)
def transport_c_access_crystal(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Make the Dark Crystal platform in
    Transport C Access be movable in both sides.
    """
    default = area.get_layer("Default")

    # Add objects

    # Ever so slightly bigger than dark crystal
    # for fade effect to avoid Z-Fighting
    light_crystal = default.add_instance_with(
        Actor(
            editor_properties=EditorProperties(
                name="[LIGHT] Crystal",
                transform=Transform(
                    position=Vector(-92.548386, -62.062748, -18.448999),
                    rotation=Vector(90.0, 0.0, -45.0),
                    scale=Vector(2.501, 2.501, 2.501),
                ),
                active=False,
            ),
            model=0xD03EAF48,
            is_solid=False,
        )
    )

    dark_crystal = default.add_instance_with(
        Actor(
            editor_properties=EditorProperties(
                name="[DARK] Crystal",
                transform=Transform(
                    position=Vector(-92.548386, -62.062748, -18.448999),
                    rotation=Vector(90.0, 0.0, -45.0),
                    scale=Vector(2.5, 2.5, 2.5),
                ),
            ),
            model=0xACB98F54,
            is_solid=False,
        )
    )

    new_dtrigger = default.add_instance_with(
        DamageableTriggerOrientated(
            editor_properties=EditorProperties(
                name="DamageableTriggerOrientated",
                transform=Transform(
                    position=Vector(-93.116074, -62.668762, -18.448999),
                    rotation=Vector(0.0, 0.0, -45.0),
                    scale=Vector(2.0, 1.349, 2.0),
                ),
            ),
        )
    )

    # Add a light to spotlight the crystal
    light_copy_source_room = editor.get_area(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.DYNAMO_WORKS_MREA)
    dynamic_light = default.add_instance_with(
        light_copy_source_room.get_instance("Luminoth Light Support").get_properties()
    )
    with dynamic_light.edit_properties(DynamicLight) as light:
        light.editor_properties.transform.position = Vector(-98.0, -61.7, -18.0)
        light.color = Color(0.858824, 0.729412, 0.584314, 0.0)

    # Add og trigger connections and vulnerabilities to new one
    og_dtrigger = area.get_instance("DamageableTrigger 001")
    new_dtrigger.connections = og_dtrigger.connections
    with new_dtrigger.edit_properties(DamageableTriggerOrientated) as dtrigger:
        dtrigger.vulnerability = og_dtrigger.get_properties_as(DamageableTrigger).vulnerability

    # Define objects
    platform = area.get_instance("Red Eye Statue Initial Position")
    memory_relay = area.get_instance("Keep Statue in Last Position")

    # Add new connections

    # Dynamic Light
    dynamic_light.add_connection(State.Play, Message.Activate, platform)
    dynamic_light.add_connection(State.Play, Message.Activate, light_crystal)
    dynamic_light.add_connection(State.Play, Message.Activate, dark_crystal)

    # Platform connections to Crystals and Light
    platform.add_connection(State.Play, Message.Activate, light_crystal)
    platform.add_connection(State.Play, Message.Activate, dark_crystal)
    platform.add_connection(State.Play, Message.Activate, dynamic_light)

    # Make it so shooting either dtrigger deactivates the other one, and
    # make the og dtrigger fade the crystal on the other side
    new_dtrigger.add_connection(State.Dead, Message.Deactivate, og_dtrigger)
    og_dtrigger.add_connection(State.Dead, Message.Deactivate, new_dtrigger)
    new_dtrigger.add_connection(State.Dead, Message.Increment, light_crystal)
    og_dtrigger.add_connection(State.Dead, Message.Increment, light_crystal)

    # New memory relay connections
    memory_relay.add_connection(State.Active, Message.Deactivate, light_crystal)
    memory_relay.add_connection(State.Active, Message.Deactivate, dark_crystal)
    memory_relay.add_connection(State.Active, Message.Deactivate, new_dtrigger)
    memory_relay.add_connection(State.Active, Message.Deactivate, dynamic_light)


@decorate_patcher(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.GRAND_ABYSS_MREA)
def grand_abyss_robots(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Remove the ScriptLayerController that deactivates the 1st Pass.
    This makes the bots always active.
    """
    area.remove_instance("Decrement 1st Pass")
