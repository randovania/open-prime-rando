from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.LayerSwitch import LayerSwitch
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.archetypes.TriggerInfo import FlagsTrigger
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import (
    CameraFilterKeyframe,
    CameraHint,
    CameraShaker,
    HUDMemo,
    Pickup,
    Relay,
    ScriptLayerController,
    SpawnPoint,
    Switch,
    Timer,
    Trigger,
    TriggerOrientated,
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
    from retro_data_structures.formats.script_object import InstanceIdRef

    from open_prime_rando.patcher_editor import PatcherEditor

LOG = logging.getLogger("echoes_patcher")


def register_all(area_patcher: AreaPatcher) -> None:
    """
    Applies changes necessary for the game to function properly.
    """

    for func in [
        mining_station_b,
        undertemple_access,
        main_reactor,
        sacrificial_chamber,
        aerie,
        main_research,
        hive_chamber_b,
        gfmc_compound,
        torvus_temple,
        command_center_door,
        landing_site_load_black_bars,
        temple_transport_c_black_bars,
        temple_sanctuary,
        minigyro_terminal_fall,
    ]:
        area_patcher.add_function(func)


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.MINING_STATION_B_MREA)
def mining_station_b(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Normally this relay is activated by the cutscene, but has an incoming connection from the pickup.
    Activating it like this means the pickup will trigger the relay without the cutscene
    """
    with area.get_instance(0x80121).edit_properties(Relay) as post_pickup_relay:
        post_pickup_relay.editor_properties.active = True


@decorate_patcher(TORVUS_BOG_MLVL, torvus_bog.UNDERTEMPLE_ACCESS_MREA)
def undertemple_access(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Move the default spawn point in-bounds.
    """
    with area.get_instance("Spawn point 001").edit_properties(SpawnPoint) as spawn:
        spawn.editor_properties.transform.position.x = -149.25


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.MAIN_REACTOR_MREA)
def main_reactor(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Save some memory during DS1 fight.
    """
    unload_relay = area.get_instance("Unload dock when door closed")
    trigger = area.get_instance("Trigger Start DS Intro")
    trigger.add_connection(State.Entered, Message.SetToZero, unload_relay)


@decorate_patcher(TORVUS_BOG_MLVL, torvus_bog.SACRIFICIAL_CHAMBER_MREA)
def sacrificial_chamber(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
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
def aerie(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Patches an echo gate softlock.
    """
    relays = ((0x410094, 0x41008D), (0x410077, 0x41007F), (0x4100B5, 0x4100B6))
    _patch_echo_gate_softlock(area, 0x4100BE, relays)


@decorate_patcher(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.MAIN_RESEARCH_MREA)
def main_research(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Patches an echo gate softlock.
    Disables the Contraption layer by default, activating it dynamically when exiting the lower portal.
    This hopefully prevents OOM/object list full crashes.
    """
    relays = ((0x0B02E6, 0x0B02DE), (0x0B0303, 0x0B030D), (0x0B02F6, 0x0B02FA))
    _patch_echo_gate_softlock(area, 0x0B0315, relays)

    area.get_layer("Contraption").active = False
    portal_spawn = area.get_instance(0x0B0056)
    spawn_xfm = portal_spawn.get_properties_as(SpawnPoint).editor_properties.transform

    contraption_controller = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(name="Dynamic Increment Contraption", transform=spawn_xfm),
            layer=LayerSwitch(
                area_id=sanctuary_fortress.MAIN_RESEARCH_INTERNAL_ID, layer_number=area.get_layer("Contraption").index
            ),
            is_dynamic=True,
        )
    )
    spider_controller = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(name="Dynamic Increment Column Spiderball", transform=spawn_xfm),
            layer=LayerSwitch(
                area_id=sanctuary_fortress.MAIN_RESEARCH_INTERNAL_ID,
                layer_number=area.get_layer("Column Spiderball").index,
            ),
            is_dynamic=True,
        )
    )

    for controller in (contraption_controller, spider_controller):
        portal_spawn.add_connection(State.Arrived, Message.Load, controller)
        controller.add_connection(State.Arrived, Message.Play, controller)


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.HIVE_CHAMBER_B_MREA)
def hive_chamber_b(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Removes item loss sequence.
    """
    # FIXME: use layers API
    area.get_layer("DS Appears Part1").active = False
    area.get_layer("Pre Dark Samus Music").active = False

    area.get_layer("Pickup").active = True
    area.get_layer("Post Dark Samus Music").active = True


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.GFMC_COMPOUND_MREA)
def gfmc_compound(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Add a HUDMemo for the ship missile.
    """
    pickup_xfm = area.get_instance(0x2B0324).get_properties_as(Pickup).editor_properties.transform
    ship_trigger = area.get_layer("Default").add_instance_with(
        Trigger(
            editor_properties=EditorProperties(
                name="Show Ship Missile HudMemo",
                transform=Transform(
                    position=pickup_xfm.position, rotation=Vector(0.0, 0.0, 45.0), scale=Vector(50.0, 50.0, 10.0)
                ),
            ),
            deactivate_on_enter=True,
        )
    )
    strg_id, _ = editor.create_strg(
        "gfmc_jump_hudmemo.STRG", ["Defeating Jump Guardian is required for this item to appear."]
    )
    hud_memo = area.get_layer("Default").add_instance_with(
        HUDMemo(
            editor_properties=EditorProperties(name="Ship Missile HudMemo", transform=pickup_xfm),
            display_time=6.0,
            display_type=0,
            string=strg_id,
        )
    )
    ship_trigger.add_connection(State.Entered, Message.SetToZero, hud_memo)

    timer = area.get_layer("Space Jump").add_instance_with(
        Timer(
            editor_properties=EditorProperties(name="Disable Ship Missile Trigger", transform=pickup_xfm),
            time=0.1,
            auto_start=True,
        )
    )
    timer.add_connection(State.Zero, Message.Deactivate, ship_trigger)


@decorate_patcher(TORVUS_BOG_MLVL, torvus_bog.TORVUS_TEMPLE_MREA)
def torvus_temple(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Remove cosmetic objects from Torvus Temple to minimize the chance of crash via alloc failure
    """
    to_remove = [
        "Thrust1",
        "Thrust1",
        "Thrust2",
        "Thrust2",
        "Looping Thrust w/Doppler",
        "Looping Thrust w/Doppler",
        "GENERATE GIBS",
    ]
    to_remove.extend(["SwampCrateDebris"] * 7)

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


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.LANDING_SITE_MREA)
def landing_site_load_black_bars(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Makes the "Load In" cutscene have cinematic black bars appear, this
    CameraFilterKeyframe object is wrongfully sharing the same FilterIndex
    value as the PlayerActor load wait black screen filter.
    """
    with area.get_instance(0x102).edit_properties(CameraFilterKeyframe) as blackbars:
        blackbars.filter_stage = 1


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.TEMPLE_TRANSPORT_C_MREA)
def temple_transport_c_black_bars(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Makes the Departure cutscene black bars not hide if being hit by the light rays filter, this
    CameraFilterKeyframe object is wrongfully sharing the same FilterIndex value as the Black Bars screen filter.
    """
    with area.get_instance(0x90010).edit_properties(CameraFilterKeyframe) as sunlight_filter:
        sunlight_filter.filter_stage = 0


@decorate_patcher(GREAT_TEMPLE_MLVL, great_temple.TEMPLE_SANCTUARY_MREA)
def temple_sanctuary(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Makes Ing Battle music play even when other music layers are active
    """
    # Move StreamedAudio to "1st Pass Enemy" layer where all the Dark Splinters are
    area.move_instance("Ing Encounter", "1st Pass Enemy")
    # Make the "Cinema End" Relay also send a `Play` message to the StreamedAudios from other layers
    boss_death_cinema_end_relay = area.get_instance("Cinema End")
    for instance in (0x20115, 0x20006, 0x2013E):
        boss_death_cinema_end_relay.add_connection(
            State.Zero,
            Message.Play,
            instance,
        )


@decorate_patcher(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.MINIGYRO_CHAMBER_MREA)
def minigyro_terminal_fall(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Adds a Terminal Fall in Minigyro Chamber to prevent oblivious players from accidentally
    going out of bounds if traversing through opposite side or have Cannon Ball on the
    intended side (The out of bounds is still possible if the player unmorphs early, and
    there is a failsafe reposition in case the oblivious player also happens to unmorph early.)
    """
    # Copying objects from Unseen Way
    other_area = editor.get_area(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.UNSEEN_WAY_MREA)

    # And placing them in Minigyro Chamber
    filter_blur = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Camera Blur").get_properties()
    )

    filter_flash = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance(0x170021).get_properties()
    )

    camera_hint_frozen = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Frozen").get_properties()
    )

    camera_hint_morph_ball = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Morph Fall").get_properties()
    )

    camera_hint_prevent_ledge_avoidance = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Prevent Ledge Avoidance").get_properties()
    )

    camera_shaker = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Camera Shaker_HArsh_Short").get_properties()
    )
    with camera_shaker.edit_properties(CameraShaker) as shaker:
        shaker.editor_properties = EditorProperties(transform=Transform(position=Vector(170.0, 182.0, -114.0)))

    no_morph_control_hint = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Disable Morph").get_properties()
    )

    radial_damage = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Hurt Player").get_properties()
    )

    originator_relay = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Set Player Originator for Hurt").get_properties()
    )

    flash_controls_relay = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance(0x17001D).get_properties()
    )

    rumble_effect = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Fall Rumble").get_properties()
    )

    sequence_timer = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Fall to Death").get_properties()
    )

    sound_into_hud = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Sound - Into Hud").get_properties()
    )

    east_spawnpoint = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Fall to Death Return").get_properties()
    )
    with east_spawnpoint.edit_properties(SpawnPoint) as east_spawn:
        east_spawn.editor_properties = EditorProperties(
            transform=Transform(
                position=Vector(150.665604, 130.681992, -116.36132),
                rotation=Vector(0.0, 0.0, 0.0),
                scale=Vector(1.799, 1.799, 1.799),
            )
        )
        east_spawn.morphed = True

    west_spawnpoint = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance(0x170022).get_properties()
    )
    with west_spawnpoint.edit_properties(SpawnPoint) as west_spawn:
        west_spawn.editor_properties = EditorProperties(
            transform=Transform(
                position=Vector(150.683228, 161.135986, -116.07415),
                rotation=Vector(0.0, 0.0, 90.0),
                scale=Vector(1.799, 1.799, 1.799),
            )
        )
        west_spawn.morphed = True

    player_in_area_special_function = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Death Fall Player In Area").get_properties()
    )

    flash_timer = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Timer White Flash Duration").get_properties()
    )

    west_spawnpoint_trigger = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance(0x170004).get_properties()
    )
    with west_spawnpoint_trigger.edit_properties(Trigger) as west_spawn_trigger:
        west_spawn_trigger.editor_properties = EditorProperties(
            transform=Transform(position=Vector(120.773407, 149.127029, -106.985382), scale=Vector(10.0, 10.0, 10.0))
        )

    east_spawnpoint_trigger = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Fall Trigger_Platform").get_properties()
    )
    with east_spawnpoint_trigger.edit_properties(TriggerOrientated) as east_spawn_trigger:
        east_spawn_trigger.editor_properties = EditorProperties(
            transform=Transform(position=Vector(182.771896, 142.353943, -107.949036), scale=Vector(10.0, 10.0, 10.0))
        )

    fall_Trigger = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Fall Trigger").get_properties()
    )
    with fall_Trigger.edit_properties(TriggerOrientated) as falling_trigger:
        falling_trigger.editor_properties = EditorProperties(
            transform=Transform(position=Vector(151.665604, 144.968307, -124.108681), scale=Vector(50.0, 50.0, 3.0))
        )
        falling_trigger.trigger.flags_trigger &= ~FlagsTrigger.DetectUnmorphedPlayer

    # Additional Extra Objects
    camera_teleport = area.get_layer("Gyroscope puzzle").add_instance_with(
        CameraHint(
            editor_properties=EditorProperties(
                name="Teleport Player Camera",
                transform=Transform(
                    position=Vector(151.658524, 145.002243, -120.17498),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            priority=1,
            timer=0.02,
            flags_camera_hint=262462,
        )
    )
    east_side_camerahint_reset_trigger = area.get_layer("Gyroscope puzzle").add_instance_with(
        Trigger(
            editor_properties=EditorProperties(
                name="Onto gyro platforms (tunnel) 2nd Trigger",
                transform=Transform(
                    position=Vector(150.885666, 130.688904, -116.225525),
                    scale=Vector(2.983, 1.44, 5.068),
                ),
            )
        )
    )
    reset_camerahints_trigger = area.get_layer("Gyroscope puzzle").add_instance_with(
        Trigger(
            editor_properties=EditorProperties(
                name="Reset CameraHints",
                transform=Transform(
                    position=Vector(151.665604, 144.968307, -124.108681),
                    scale=Vector(50.0, 50.0, 3.0),
                ),
            )
        )
    )
    fall_failsafe_trigger = area.get_layer("Gyroscope puzzle").add_instance_with(
        Trigger(
            editor_properties=EditorProperties(
                name="Catch Player Failsafe",
                transform=Transform(position=Vector(151.665604, 144.968307, -300), scale=Vector(1000.0, 1000.0, 3.0)),
            )
        )
    )

    # Define some existing objects
    gyro_camera_hint = area.get_instance("Gyro Outer Ring")
    tunnels_camera_hint = area.get_instance("Tunnels")
    supertrigger = area.get_instance("Supertrigger enter tunnel")

    # Terminal Fall Connections
    originator_relay.add_connection(State.Zero, Message.Action, radial_damage)
    flash_controls_relay.add_connection(State.Zero, Message.ResetAndStart, flash_timer)
    flash_controls_relay.add_connection(State.Zero, Message.Increment, filter_blur)
    flash_controls_relay.add_connection(State.Zero, Message.Increment, filter_flash)
    for target, message in [
        (flash_controls_relay, Message.SetToZero),
        (sound_into_hud, Message.Play),
        (no_morph_control_hint, Message.Decrement),
        (no_morph_control_hint, Message.Increment),
        (west_spawnpoint, Message.SetToZero),
        (camera_hint_prevent_ledge_avoidance, Message.Decrement),
        (camera_hint_morph_ball, Message.Increment),
        (camera_hint_frozen, Message.Increment),
        (originator_relay, Message.SetToZero),
        (camera_hint_frozen, Message.Decrement),
        (rumble_effect, Message.Action),
        (east_spawnpoint, Message.SetToZero),
        (camera_shaker, Message.Action),
        (fall_Trigger, Message.Activate),
    ]:
        sequence_timer.add_connection(State.Sequence, message, target)
    player_in_area_special_function.add_connection(State.Entered, Message.Activate, fall_Trigger)
    player_in_area_special_function.add_connection(State.Exited, Message.Deactivate, fall_Trigger)
    player_in_area_special_function.add_connection(State.Entered, Message.Activate, fall_failsafe_trigger)
    player_in_area_special_function.add_connection(State.Exited, Message.Deactivate, fall_failsafe_trigger)
    flash_timer.add_connection(State.Zero, Message.Decrement, filter_blur)
    flash_timer.add_connection(State.Zero, Message.Decrement, filter_flash)
    west_spawnpoint_trigger.add_connection(State.Entered, Message.Deactivate, east_spawnpoint)
    west_spawnpoint_trigger.add_connection(State.Entered, Message.Activate, west_spawnpoint)
    fall_Trigger.add_connection(State.Entered, Message.SetOriginator, originator_relay)
    fall_Trigger.add_connection(State.Entered, Message.Start, sequence_timer)
    east_spawnpoint_trigger.add_connection(State.Entered, Message.Increment, camera_hint_prevent_ledge_avoidance)
    east_spawnpoint_trigger.add_connection(State.Exited, Message.Decrement, camera_hint_prevent_ledge_avoidance)
    east_spawnpoint_trigger.add_connection(State.Entered, Message.Activate, east_spawnpoint)
    east_spawnpoint_trigger.add_connection(State.Entered, Message.Deactivate, west_spawnpoint)
    # CameraHint related connections
    reset_camerahints_trigger.add_connection(State.Entered, Message.Decrement, gyro_camera_hint)
    reset_camerahints_trigger.add_connection(State.Entered, Message.Decrement, tunnels_camera_hint)
    reset_camerahints_trigger.add_connection(State.Entered, Message.Increment, camera_teleport)
    east_side_camerahint_reset_trigger.add_connection(State.Connect, Message.Attach, supertrigger)
    # Failsafe Reposition connections
    fall_failsafe_trigger.add_connection(State.Entered, Message.SetOriginator, originator_relay)
    fall_failsafe_trigger.add_connection(State.Entered, Message.Start, sequence_timer)
