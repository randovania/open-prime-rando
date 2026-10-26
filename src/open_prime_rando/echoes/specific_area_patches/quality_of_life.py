from __future__ import annotations

from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, PlayerItemEnum, State
from retro_data_structures.properties.echoes.archetypes.Connection import Connection as SequenceConnection
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.LayerSwitch import LayerSwitch
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.archetypes.TriggerInfo import FlagsTrigger
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import (
    Camera,
    CameraFilterKeyframe,
    CameraHint,
    CameraShaker,
    ScriptLayerController,
    SequenceTimer,
    SpawnPoint,
    SpecialFunction,
    StreamedAudio,
    Trigger,
    TriggerOrientated,
    WorldTeleporter,
)
from retro_data_structures.properties.echoes.objects.Camera import FlagsCinematicCamera
from retro_data_structures.properties.echoes.objects.SpecialFunction import Function

from open_prime_rando.area_patcher import AreaPatcher, decorate_patcher
from open_prime_rando.echoes.asset_ids import great_temple, sanctuary_fortress, temple_grounds
from open_prime_rando.echoes.asset_ids.world import (
    GREAT_TEMPLE_MLVL,
    SANCTUARY_FORTRESS_MLVL,
    TEMPLE_GROUNDS_MLVL,
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
        sky_temple_gateway_cinematic_skips,
        game_end_part1_cinematic_skips,
        game_end_part2_cinematic_skips,
        game_end_part3_cinematic_skips,
        game_end_part4_cinematic_skips,
        game_end_part5_cinematic_skips,
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
    Prevent lower reposition if Samus is above area.
    """
    primary_scan_trigger = area.get_instance("Activate MB Control Scan")

    lower_spawn = area.get_instance("Spawn Here After Cinematic")
    with lower_spawn.edit_properties(SpawnPoint) as spawn_props:
        spawn_props.editor_properties.active = False

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
    tertiary_scan_trigger = area.get_layer("Platform Down").add_instance_with(
        Trigger(
            editor_properties=EditorProperties(
                name="Activate MB Control Scan (Bridge Down Extension)",
                transform=Transform(
                    position=Vector(35.0, 333.0, -34.0),
                    scale=Vector(10.0, 10.0, 10.0),
                ),
            )
        )
    )
    reposition_trigger = area.get_layer("Default").add_instance_with(
        TriggerOrientated(
            editor_properties=EditorProperties(
                name="Allow Reposition",
                transform=Transform(
                    position=Vector(7.6, 318.0, -44.0),
                    rotation=Vector(0.0, 0.0, 140.0),
                    scale=Vector(17.0, 40.0, 8.0),
                ),
            )
        )
    )
    secondary_scan_trigger.add_connection(State.Connect, Message.Attach, primary_scan_trigger)
    tertiary_scan_trigger.add_connection(State.Connect, Message.Attach, primary_scan_trigger)
    reposition_trigger.add_connection(State.Entered, Message.Activate, lower_spawn)
    reposition_trigger.add_connection(State.Exited, Message.Deactivate, lower_spawn)


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.SKY_TEMPLE_GATEWAY_MREA)
def sky_temple_gateway_cinematic_skips(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Makes the Ending Cutscenes in Sky Temple Gateway
    be skippable and warp to credits room if done so.
    """
    default = area.get_layer("Default")

    # Add a new layer just for the teleporters, otherwise
    # room takes a little longer to load into
    warps_layer = area.add_layer("Ending Teleporters", active=False)
    ds_death_start = area.get_instance("DS Death Cinema Start")
    game_end_part1_end = area.get_instance(0x2A036B)

    # Required Objects
    teleporters_controller = default.add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Load Ending Teleporters",
                transform=Transform(position=Vector(-9.0, -61.5, -27.2), scale=Vector(2.0, 2.0, 2.0)),
            ),
            layer=LayerSwitch(
                area_id=temple_grounds.SKY_TEMPLE_GATEWAY_INTERNAL_ID,
                layer_number=warps_layer.index,
            ),
            is_dynamic=True,
        )
    )

    # Using a CinematicSkip Function allows for things to
    # happen only if you skipped a cutscene
    cinematic_skip = default.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(
                name="CinematicSkipSignal - Warp to Credits",
                transform=Transform(
                    position=Vector(17.30558, 76.674892, -30.408634),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            function=Function.CinematicSkipSignal,
        )
    )

    # Less than 75% items check
    ending_check1 = default.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(
                name="Ending 1 Check",
                transform=Transform(
                    position=Vector(15.0, 70.0, -30.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            function=Function.Ending,
        )
    )

    # Greater than 75% items check
    ending_check2 = default.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(
                name="Ending 2 Check",
                transform=Transform(
                    position=Vector(15.0, 69.0, -30.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            function=Function.Ending,
            value_parm=1.0,
        )
    )

    # If over 75%, take away Dark Suit for ZSS cutscene
    take_away_dark_suit = default.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(
                name="Take Away Dark Suit",
                transform=Transform(
                    position=Vector(16.0, 69.0, -30.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            # FIXME Update templates. Real name is "ModifyInventoryCapacity"
            function=Function.IncrementDecrementPlayersJoinedCount,
            inventory_item_parm=PlayerItemEnum.DarkSuit,
            int_parm2=-1,
        )
    )

    # If over 75%, take away Light Suit for ZSS cutscene
    take_away_light_suit = default.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(
                name="Take Away Light Suit",
                transform=Transform(
                    position=Vector(17.0, 69.0, -30.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            function=Function.IncrementDecrementPlayersJoinedCount,
            inventory_item_parm=PlayerItemEnum.LightSuit,
            int_parm2=-1,
        )
    )

    # Teleporter to Credits room
    credits_warp = warps_layer.add_instance_with(
        WorldTeleporter(
            editor_properties=EditorProperties(
                name="Warp to game_end_part5",
                transform=Transform(
                    position=Vector(14.0, 70.0, -30.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            world=TEMPLE_GROUNDS_MLVL,
            area=temple_grounds.GAME_END_PART5_MREA,
            elevator=-1,  # FIXME Default Value for this property should be -1 for [None] as 0 is INVALID
        )
    )

    # Teleporter to ZSS Cutscene room
    bad_ending_warp = warps_layer.add_instance_with(
        WorldTeleporter(
            editor_properties=EditorProperties(
                name="Warp to game_end_part3",
                transform=Transform(
                    position=Vector(14.0, 69.0, -30.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            world=TEMPLE_GROUNDS_MLVL,
            area=temple_grounds.GAME_END_PART3_MREA,
            elevator=-1,
        )
    )

    # Make the following cameras be skippable
    cameras = [
        "DS_3_Death_01",
        "DS_3_Death_02",
        "DS_3_Death_03",
        "DS_3_Death_04",
        "DS_3_Death_05",
        "DS_3_Death_06",
        "DS_3_Death_08",
        "DS_3_Death_09",
        "DS_3_Death_10",
        "DS_3_Death_11",
        "DS_3_Death_12",
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "C6",
        "C7",
        "C8",
        "C9",
        "C10",
        "C11",
        "C12",
        "C13",
        "C14",
        "C15",
        "C16",
        "C17",
    ]

    for camera_ids in cameras:
        with area.get_instance(camera_ids).edit_properties(Camera) as camera_props:
            camera_props.flags_cinematic_camera &= ~FlagsCinematicCamera.FinishCineSkip
            camera_props.flags_cinematic_camera |= FlagsCinematicCamera.CinematicSkip

    # Load Teleporters layer once death cutscene is done loading
    area.get_instance("Load Dark Samus 3 Battle Death").add_connection(
        State.Arrived, Message.Increment, teleporters_controller
    )
    area.get_instance("Begin Dark Samus Battle3 Death").add_connection(State.Open, Message.Play, teleporters_controller)

    # Increment/Decrement Cinematic Skip on cutscene start/end
    ds_death_start.add_connection(State.Zero, Message.Increment, cinematic_skip)
    game_end_part1_end.add_connection(State.Zero, Message.Decrement, cinematic_skip)

    # Fire % Checks when skipped cutscenes
    cinematic_skip.add_connection(State.Zero, Message.Action, ending_check1)
    cinematic_skip.add_connection(State.Zero, Message.Action, ending_check2)

    # Warp to Credits if below 75% on cutscene skip
    ending_check1.add_connection(State.Zero, Message.SetToZero, credits_warp)

    # Warp to ZSS Cutscene if or above 75% on cutscene skip
    ending_check2.add_connection(State.Zero, Message.Action, take_away_dark_suit)
    ending_check2.add_connection(State.Zero, Message.Action, take_away_light_suit)
    ending_check2.add_connection(State.Zero, Message.SetToZero, bad_ending_warp)


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.GAME_END_PART1_MREA)
def game_end_part1_cinematic_skips(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Makes the Ending Cutscenes in game_end_part1 be
    skippable and warp to credits room if done so
    """
    default = area.get_layer("Default")
    cinema_start = area.get_instance("Cinema Start")
    cinema_end = area.get_instance("Cinema End")

    cinematic_skip = default.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(
                name="CinematicSkipSignal - Warp to Credits",
                transform=Transform(
                    position=Vector(948.0, -350.0, 7.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            function=Function.CinematicSkipSignal,
        )
    )

    ending_check1 = default.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(
                name="Ending 1 Check",
                transform=Transform(
                    position=Vector(948.0, -351.0, 7.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            function=Function.Ending,
        )
    )

    ending_check2 = default.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(
                name="Ending 2 Check",
                transform=Transform(
                    position=Vector(949.0, -351.0, 7.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            function=Function.Ending,
            value_parm=1.0,
        )
    )

    credits_warp = default.add_instance_with(
        WorldTeleporter(
            editor_properties=EditorProperties(
                name="Warp to game_end_part5",
                transform=Transform(
                    position=Vector(948.0, -352.0, 7.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            world=TEMPLE_GROUNDS_MLVL,
            area=temple_grounds.GAME_END_PART5_MREA,
            elevator=-1,
        )
    )

    bad_ending_warp = default.add_instance_with(
        WorldTeleporter(
            editor_properties=EditorProperties(
                name="Warp to game_end_part3",
                transform=Transform(
                    position=Vector(949.0, -352.0, 7.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            world=TEMPLE_GROUNDS_MLVL,
            area=temple_grounds.GAME_END_PART3_MREA,
            elevator=-1,
        )
    )

    cameras = ["Camera 19", "Camera 20", "Camera 21", "Camera 22", "Camera 23"]

    for camera_ids in cameras:
        with area.get_instance(camera_ids).edit_properties(Camera) as camera_props:
            camera_props.flags_cinematic_camera |= FlagsCinematicCamera.CinematicSkip

    cinema_start.add_connection(State.Zero, Message.Increment, cinematic_skip)
    cinema_end.add_connection(State.Zero, Message.Decrement, cinematic_skip)
    cinematic_skip.add_connection(State.Zero, Message.Action, ending_check1)
    cinematic_skip.add_connection(State.Zero, Message.Action, ending_check2)
    ending_check1.add_connection(State.Zero, Message.SetToZero, credits_warp)
    ending_check2.add_connection(State.Zero, Message.Action, area.get_instance(0x2F013B))
    ending_check2.add_connection(State.Zero, Message.Action, area.get_instance(0x2F013A))
    ending_check2.add_connection(State.Zero, Message.SetToZero, bad_ending_warp)


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.GAME_END_PART2_MREA)
def game_end_part2_cinematic_skips(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Makes the Ending Cutscenes in game_end_part2 be
    skippable and warp to credits room if done so
    """
    default = area.get_layer("Default")
    cinema_start = area.get_instance("Enter Room")
    cinema_end = area.get_instance("Cinema End")
    aether_movie = area.get_instance("StreamedMovie 001")

    cinematic_skip = default.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(
                name="CinematicSkipSignal - Warp to Credits",
                transform=Transform(
                    position=Vector(1019.0, 157.0, 9.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            function=Function.CinematicSkipSignal,
        )
    )

    ending_check1 = default.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(
                name="Ending 1 Check",
                transform=Transform(
                    position=Vector(1019.0, 156.0, 9.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            function=Function.Ending,
        )
    )

    ending_check2 = default.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(
                name="Ending 2 Check",
                transform=Transform(
                    position=Vector(1020.0, 156.0, 9.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            function=Function.Ending,
            value_parm=1.0,
        )
    )

    loading_camera = default.add_instance_with(
        Camera(
            editor_properties=EditorProperties(
                name="Hold",
                transform=Transform(
                    position=Vector(0.0, 0.0, -1000.0),
                    rotation=Vector(-90.0, 0.0, 0.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            flags_cinematic_camera=(FlagsCinematicCamera(176)),
        )
    )

    credits_warp = default.add_instance_with(
        WorldTeleporter(
            editor_properties=EditorProperties(
                name="Warp to game_end_part5",
                transform=Transform(
                    position=Vector(1019.0, 155.0, 9.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            world=TEMPLE_GROUNDS_MLVL,
            area=temple_grounds.GAME_END_PART5_MREA,
            elevator=-1,
        )
    )

    cameras = [
        "Camera_1",
        "Camera_2",
        "Camera_3",
        "Camera_4",
        "Camera_5",
        "Camera_6",
        "Camera_7",
        "Camera_8",
        "Camera_9",
        "Camera_10",
        "Cinematic Camera 001",
    ]

    for camera_ids in cameras:
        with area.get_instance(camera_ids).edit_properties(Camera) as camera_props:
            camera_props.flags_cinematic_camera |= FlagsCinematicCamera.CinematicSkip

    cinema_start.add_connection(State.Zero, Message.Increment, cinematic_skip)
    cinema_end.add_connection(State.Zero, Message.Decrement, cinematic_skip)
    cinematic_skip.add_connection(State.Zero, Message.Action, ending_check1)
    cinematic_skip.add_connection(State.Zero, Message.Action, ending_check2)
    ending_check1.add_connection(State.Zero, Message.SetToZero, credits_warp)

    # Deactivate all the cameras upon skip otherwise music stays playing
    for cameras_deactivate in cameras:
        ending_check2.add_connection(State.Zero, Message.Deactivate, area.get_instance(cameras_deactivate))

    # Dump Cinema layer and start loading next room instead of warping if ending 2 passed
    ending_check2.add_connection(State.Zero, Message.Activate, loading_camera)
    ending_check2.add_connection(State.Zero, Message.Stop, loading_camera)
    ending_check2.add_connection(State.Zero, Message.Stop, aether_movie)
    ending_check2.add_connection(State.Zero, Message.Unload, aether_movie)
    ending_check2.add_connection(State.Zero, Message.SetToZero, area.get_instance("YellowTint"))
    ending_check2.add_connection(State.Zero, Message.SetToZero, area.get_instance("Cinema End"))
    ending_check2.add_connection(State.Zero, Message.Stop, area.get_instance("Game End Pages9_11"))
    ending_check2.add_connection(State.Zero, Message.Stop, area.get_instance("GameEnd 2 Music"))
    ending_check2.add_connection(State.Zero, Message.Stop, area.get_instance("GameEnd 2 SFX"))
    ending_check2.add_connection(State.Zero, Message.Decrement, area.get_instance("Unload Cinema"))


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.GAME_END_PART3_MREA)
def game_end_part3_cinematic_skips(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Makes the Ending Cutscenes in game_end_part3 be
    skippable and warp to credits room if done so
    """
    default = area.get_layer("Default")
    departure_sequence = area.get_instance("Game End_page14")
    cinema_end = area.get_instance(0x350077)

    cinematic_skip = default.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(
                name="CinematicSkipSignal - Warp to Credits",
                transform=Transform(
                    position=Vector(1025.6, -38.2, 7.4),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            function=Function.CinematicSkipSignal,
        )
    )

    credits_warp = default.add_instance_with(
        WorldTeleporter(
            editor_properties=EditorProperties(
                name="Warp to game_end_part5",
                transform=Transform(
                    position=Vector(1026.0, -36.0, 7.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            world=TEMPLE_GROUNDS_MLVL,
            area=temple_grounds.GAME_END_PART5_MREA,
            elevator=-1,
        )
    )

    cameras = [
        0x35001A,
        0x350070,
        0x350005,
        0x350065,
        "Camera 04",
        "Camera 05",
    ]

    for camera_ids in cameras:
        with area.get_instance(camera_ids).edit_properties(Camera) as camera_props:
            camera_props.flags_cinematic_camera |= FlagsCinematicCamera.CinematicSkip

    # If Ending 2 passed, make the starting cameras interrupt the cutscene skip
    for starting_cameras in (0x35005C, 0x350014):
        with area.get_instance(starting_cameras).edit_properties(Camera) as camera_flags:
            camera_flags.flags_cinematic_camera |= FlagsCinematicCamera.CinematicSkip
            camera_flags.flags_cinematic_camera |= FlagsCinematicCamera.FinishCineSkip

    # Delay Increment of CinematicSkip Function a little bit otherwise
    # it will fire before the cutscene skip can be interrupted
    with departure_sequence.edit_properties(SequenceTimer) as sequence_timer:
        sequence_timer.sequence_connections.append(
            SequenceConnection(
                connection_index=20,
                activation_times=[0.2],
            ),
        )

    departure_sequence.add_connection(State.Sequence, Message.Increment, cinematic_skip)
    cinema_end.add_connection(State.Zero, Message.Decrement, cinematic_skip)
    cinematic_skip.add_connection(State.Zero, Message.SetToZero, credits_warp)


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.GAME_END_PART4_MREA)
def game_end_part4_cinematic_skips(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Makes the Ending Cutscenes in game_end_part4 be skippable, also
    prevent the Credits Function from playing in this room.
    """
    default = area.get_layer("Default")
    credits = area.get_instance("Credits")
    cinema_start = area.get_instance("Cinema Start")
    cinema_end = area.get_instance("Cinema End")
    cine_sequence_timer = area.get_instance("End game Space")

    # Normally the Credits play in this room at the end of the cutscene, but
    # we want Credits to be able to play immediately if warped to this room, so
    # Credits is being changed from this cutscene's end to next room's cutscene start.
    with credits.edit_properties(SpecialFunction) as credits:
        credits.editor_properties.active = False

    cinematic_skip = default.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(
                name="Stop Everything, Proceed to Credits",
                transform=Transform(
                    position=Vector(827.792786, -33.837975, 7.045372),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            function=Function.CinematicSkipSignal,
        )
    )

    game_end_part4_music = default.add_instance_with(
        StreamedAudio(
            editor_properties=EditorProperties(
                name="GameEnd Part 4 Music",
                transform=Transform(
                    position=Vector(833.505005, -40.77496, 7.228385),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            song_file="/audio/ending-part3-3-32.dsp",
            fade_out_time=0.0,
        )
    )

    loading_camera = default.add_instance_with(
        Camera(
            editor_properties=EditorProperties(
                name="Hold",
                transform=Transform(
                    rotation=Vector(0.0, 0.0, 90.0),
                ),
            ),
            flags_cinematic_camera=(FlagsCinematicCamera(176)),
        )
    )

    # Start loading next room immediately instead of at
    # end, so Cinema layer can be dumped upon skip
    with cine_sequence_timer.edit_properties(SequenceTimer) as sequence_timer:
        sequence_timer.sequence_connections[15].activation_times = [0.0]

    cameras = [
        "Camera 04",
        "Camera 05",
    ]

    for camera_ids in cameras:
        with area.get_instance(camera_ids).edit_properties(Camera) as camera_flags:
            camera_flags.flags_cinematic_camera |= FlagsCinematicCamera.CinematicSkip

    cinema_start.add_connection(State.Zero, Message.Increment, cinematic_skip)
    cinema_end.add_connection(State.Zero, Message.Decrement, cinematic_skip)
    cinematic_skip.add_connection(State.Zero, Message.Activate, loading_camera)
    cinematic_skip.add_connection(State.Zero, Message.Stop, loading_camera)
    cinematic_skip.add_connection(State.Zero, Message.Deactivate, area.get_instance("Platform SpaceSky"))
    cinematic_skip.add_connection(State.Zero, Message.Deactivate, area.get_instance("Ship_s_4"))
    cinematic_skip.add_connection(State.Zero, Message.Deactivate, area.get_instance("Space_Only"))
    cinematic_skip.add_connection(State.Zero, Message.Deactivate, area.get_instance("Ship_s_5"))
    cinematic_skip.add_connection(State.Zero, Message.Deactivate, area.get_instance("Exit Plume"))
    cinematic_skip.add_connection(State.Zero, Message.Stop, area.get_instance("GameEnd part 4 SFX"))
    cinematic_skip.add_connection(State.Zero, Message.Stop, area.get_instance("End game Space"))
    cinematic_skip.add_connection(State.Zero, Message.Stop, game_end_part4_music)
    cinematic_skip.add_connection(State.Zero, Message.SetToZero, cinema_end)
    cinematic_skip.add_connection(State.Zero, Message.SetToZero, area.get_instance("Go To Next Area"))


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.GAME_END_PART5_MREA)
def game_end_part5_cinematic_skips(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Makes the Ending Cutscenes in game_end_part5 be skippable, also
    make Credits happen in this room on startup instead of at the end
    of the previous room's cutscene.
    """
    default = area.get_layer("Default")
    spawn = area.get_instance("Enter Room")

    credits = default.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(
                name="Credits",
                transform=Transform(
                    position=Vector(936.245789, -251.573517, 6.795353),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            function=Function.Credits,
        )
    )

    loading_camera = default.add_instance_with(
        Camera(
            editor_properties=EditorProperties(name="Hold"),
            animation_time=512,
            flags_cinematic_camera=(FlagsCinematicCamera(176)),
        )
    )

    # Upon room visible, fire Credits, then once those are done fire the ending checks.
    credits_and_endings_delay = default.add_instance_with(
        SequenceTimer(
            editor_properties=EditorProperties(
                name="Start Credits then Fire Game Endings",
                transform=Transform(
                    position=Vector(935.245789, -252.573517, 6.795353),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            sequence_connections=(
                [
                    SequenceConnection(
                        connection_index=0,
                        activation_times=[0.02],
                    ),
                    SequenceConnection(
                        connection_index=1,
                        activation_times=[0.03],
                    ),
                    SequenceConnection(
                        connection_index=2,
                        activation_times=[0.03],
                    ),
                    SequenceConnection(
                        connection_index=3,
                        activation_times=[0.03],
                    ),
                ]
            ),
        )
    )

    # Make camera be skippable
    with area.get_instance("Camera 001").edit_properties(Camera) as camera_props:
        camera_props.flags_cinematic_camera |= FlagsCinematicCamera.CinematicSkip

    # Remove Ending checks on player entering room
    # as those are now managed by the SequenceTimer
    spawn_connections = list(spawn.connections)
    spawn.remove_connection(spawn_connections[0])
    spawn.remove_connection(spawn_connections[1])
    spawn.remove_connection(spawn_connections[2])

    # Fire Credits and Ending timer on player entering room
    spawn.add_connection(State.Zero, Message.Activate, loading_camera)
    spawn.add_connection(State.Zero, Message.Start, credits_and_endings_delay)

    credits_and_endings_delay.add_connection(State.Sequence, Message.Action, credits)
    credits_and_endings_delay.add_connection(State.Sequence, Message.Action, area.get_instance("Normal Ending"))
    credits_and_endings_delay.add_connection(State.Sequence, Message.Action, area.get_instance("Good Ending"))
    credits_and_endings_delay.add_connection(State.Sequence, Message.Action, area.get_instance("Best Ending"))
