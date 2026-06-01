from __future__ import annotations

from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.properties.echoes.archetypes.Connection import Connection as SequenceConnection
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.archetypes.TriggerInfo import FlagsTrigger
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import (
    CameraFilterKeyframe,
    CameraHint,
    CameraShaker,
    SequenceTimer,
    SpawnPoint,
    Trigger,
    TriggerOrientated,
)

from open_prime_rando.area_patcher import AreaPatcher, decorate_patcher
from open_prime_rando.echoes.asset_ids import great_temple, sanctuary_fortress, temple_grounds, torvus_bog
from open_prime_rando.echoes.asset_ids.world import (
    GREAT_TEMPLE_MLVL,
    SANCTUARY_FORTRESS_MLVL,
    TEMPLE_GROUNDS_MLVL,
    TORVUS_BOG_MLVL,
)

if TYPE_CHECKING:
    from retro_data_structures.formats.mlvl import Mlvl
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.patcher_editor import PatcherEditor


def register_all(area_patcher: AreaPatcher) -> None:
    """
    Applies quality of life changes.
    """

    for func in [
        landing_site_load_black_bars,
        temple_transport_c_black_bars,
        temple_sanctuary_music,
        minigyro_terminal_fall,
        sacred_bridge_platform_scan,
        torvus_temple_cutscene_skips_length,
    ]:
        area_patcher.add_function(func)


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
def temple_sanctuary_music(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
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
        shaker.editor_properties.transform.position = Vector(170.0, 182.0, -114.0)

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
        east_spawn.editor_properties.transform.position = Vector(150.665604, 130.681992, -116.36132)
        east_spawn.morphed = True

    west_spawnpoint = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance(0x170022).get_properties()
    )
    with west_spawnpoint.edit_properties(SpawnPoint) as west_spawn:
        west_spawn.editor_properties.transform.position = Vector(150.683228, 161.135986, -116.07415)
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
        west_spawn_trigger.editor_properties.transform.position = Vector(120.773407, 149.127029, -106.985382)
        west_spawn_trigger.editor_properties.transform.scale = Vector(10.0, 15.0, 10.0)

    east_spawnpoint_trigger = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Fall Trigger_Platform").get_properties()
    )
    with east_spawnpoint_trigger.edit_properties(TriggerOrientated) as east_spawn_trigger:
        east_spawn_trigger.editor_properties.transform.position = Vector(182.771896, 142.353943, -107.949036)
        east_spawn_trigger.editor_properties.transform.scale = Vector(10.0, 10.0, 10.0)

    fall_Trigger = area.get_layer("Gyroscope puzzle").add_instance_with(
        other_area.get_instance("Fall Trigger").get_properties()
    )
    with fall_Trigger.edit_properties(TriggerOrientated) as falling_trigger:
        falling_trigger.editor_properties.transform.position = Vector(151.665604, 144.968307, -124.108681)
        falling_trigger.editor_properties.transform.scale = Vector(50.0, 50.0, 3.0)
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

    # Adding connections from terminal fall related objects that Retro added on every room
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
    # Attach failsafe Trigger to main Fall Trigger
    fall_failsafe_trigger.add_connection(State.Connect, Message.Attach, fall_Trigger)


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.SACRED_BRIDGE_MREA)
def sacred_bridge_platform_scan(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Add a Trigger on the Sacred Path side that
    activates the Kinetic Orb Cannon scan panel.
    """
    primary_scan_trigger = area.get_instance("Activate MB Control Scan")
    secondary_scan_trigger = area.get_layer("Default").add_instance_with(
        Trigger(
            editor_properties=EditorProperties(
                name="Activate MB Control Scan (Extension)",
                transform=Transform(
                    position=Vector(-8.0, 290.0, -36.0),
                    scale=Vector(10.0, 10.0, 10.0),
                ),
            )
        )
    )
    secondary_scan_trigger.add_connection(State.Connect, Message.Attach, primary_scan_trigger)


@decorate_patcher(TORVUS_BOG_MLVL, torvus_bog.TORVUS_TEMPLE_MREA)
def torvus_temple_cutscene_skips_length(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Temporarely stop room loading during the 2nd wave so
    cutscene skips don't take a long time in a black screen.
    """
    stop_loading_relay = area.get_instance("Unload all adjacent areas, disable scripted loading")
    resume_loading_relay = area.get_instance("re-enable scripted loading")
    wave2_pirates_sequence_timer = area.get_instance("Pirate Skiff 2 Cinematic Sequence")
    supermissile_cinematic_controller = area.get_instance("Increment - 04_Swamp - Supermissile Cinematic (Dynamic)")

    # Add new connection to Wave 2 Cutscene SequenceTimer
    with wave2_pirates_sequence_timer.edit_properties(SequenceTimer) as stimer_props:
        stimer_props.sequence_connections.append(
            SequenceConnection(
                connection_index=27,
                activation_times=[0.0],
            ),
        )
    wave2_pirates_sequence_timer.add_connection(State.Sequence, Message.SetToZero, stop_loading_relay)

    # Resume room loading once the barrier is gone
    supermissile_cinematic_controller.add_connection(State.Arrived, Message.SetToZero, resume_loading_relay)
