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
    Actor,
    CameraHint,
    CameraShaker,
    IngSpiderballGuardian,
    MemoryRelay,
    Pickup,
    ScriptLayerController,
    SpawnPoint,
    Splinter,
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
    from retro_data_structures.formats.script_object import InstanceRef

    from open_prime_rando.patcher_editor import PatcherEditor

LOG = logging.getLogger("echoes_patcher")


def register_all(area_patcher: AreaPatcher) -> None:
    """
    Applies patches that rebalance aspects of the game for a better rando experience.
    """
    for func in [
        landing_site,
        bionergy_production,
        agon_energy_controller,
        dark_agon_energy_controller,
        torvus_energy_controller,
        dark_torvus_energy_controller,
        hive_energy_controller,
        hive_tunnel,
        agon_temple,
        temple_sanctuary,
        main_reactor,
        dynamo_works,
        torvus_temple,
        gfmc_compound,
        sanctuary_entrance,
        minigyro_terminal_fall,
    ]:
        area_patcher.add_function(func)


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.LANDING_SITE_MREA)
def landing_site(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Removes the intro cinematic.
    """
    remove_intro = True

    # FIXME: use layers API
    area.get_layer("1st Pass - Intro Cinematic").active = not remove_intro
    for layer_name in ("Save Station Load", "Ship Repair", "Luminoth Key Bearer", "WAR CHEST"):
        area.get_layer(layer_name).active = remove_intro

    spawn = area.get_instance("E3 Spawn Point")
    with spawn.edit_properties(SpawnPoint) as props:
        props.editor_properties.active = not remove_intro

    if remove_intro:
        timer = area.get_layer("Default").add_instance_with(Timer(time=0.01, auto_start=True))
        for inst in ("Keep Samus Ship", "Savestation Recharge Always Plays", "Ambient Music Memory Relay"):
            # TODO: unclear whether the timer is necessary, or if we can just activate these immediately
            timer.add_connection(State.Zero, Message.Activate, area.get_instance(inst))


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.BIOENERGY_PRODUCTION_MREA)
def bionergy_production(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Deactivate the trigger for flying pirates after killing them all.
    """
    counter = area.get_instance("Dead Pirates")
    counter.add_connection(State.MaxReached, Message.Deactivate, area.get_instance("Turn On Flying Pirates"))


def _disable_layer_controllers(area: Area, layer_controllers: Iterable[InstanceRef]):
    for inst in layer_controllers:
        with area.get_instance(inst).edit_properties(ScriptLayerController) as controller:
            controller.editor_properties.active = False


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.AGON_ENERGY_CONTROLLER_MREA)
def agon_energy_controller(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Remove Luminoth barriers.
    """
    _disable_layer_controllers(area, ["Increment - 07_Temple - Luminoth Barrier Swamp"])


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.DARK_AGON_ENERGY_CONTROLLER_MREA)
def dark_agon_energy_controller(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Remove Luminoth barriers.
    """
    _disable_layer_controllers(area, ["Increment - 0A_Sand_Hall - Luminoth Barriers"])


@decorate_patcher(TORVUS_BOG_MLVL, torvus_bog.TORVUS_ENERGY_CONTROLLER_MREA)
def torvus_energy_controller(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Don't remove the Torvus Temple fight, and remove luminoth barriers.
    """

    # Luminoth Barriers
    _disable_layer_controllers(area, ["Increment - 07_Temple - Luminoth Barrier Cliffs"])

    # Don't remove the Torvus Temple fight.
    _disable_layer_controllers(
        area,
        (
            "DECREMENT 04_Swamp_Temple 1st Pass",
            "Decrement - 04_Swamp_Temple - 1st Pass",
            "Increment - 04_Swamp_Temple - 2ndPass",
        ),
    )


@decorate_patcher(TORVUS_BOG_MLVL, torvus_bog.DARK_TORVUS_ENERGY_CONTROLLER_MREA)
def dark_torvus_energy_controller(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Remove Luminoth barriers.
    """
    _disable_layer_controllers(
        area, ("Increment - 0A_Swamp - Luminoth Barriers", "Increment - 04_Swamp - Luminoth Barriers")
    )


@decorate_patcher(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.HIVE_ENERGY_CONTROLLER_MREA)
def hive_energy_controller(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Remove Luminoth barriers.
    """
    _disable_layer_controllers(
        area,
        (
            "Increment - 0P_Cliff - Luminoth Barriers",
            "Increment - 0A_Cliff - Luminoth Barriers",
            "Increment - 0Q_Cliff - Luminoth Barriers",
        ),
    )


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.HIVE_TUNNEL_MREA)
def hive_tunnel(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Unknown purpose.
    """
    with area.get_instance("Timer 001").edit_properties(Timer) as timer:
        timer.time = 0.02
    with area.get_instance("Decrement - Webbing").edit_properties(ScriptLayerController) as controller:
        controller.is_dynamic = False


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.AGON_TEMPLE_MREA)
def agon_temple(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    No longer locks the doors after the Bomb Guardian fight.
    """
    area.get_layer("Lock Doors").active = False  # FIXME: use layers API


@decorate_patcher(GREAT_TEMPLE_MLVL, great_temple.TEMPLE_SANCTUARY_MREA)
def temple_sanctuary(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Patches Alpha Splinter to take damage properly from Power Bombs.
    Keep the Emerald gate active from the beginning.
    Fade in the Pickup.
    """
    with area.get_instance("MEGA Splinter Light").edit_properties(Splinter) as alpha:
        custom_rule = editor.get_custom_asset("custom_knockback.RULE")
        assert custom_rule is not None
        alpha.patterned.knockback_rules = custom_rule
        alpha.ing_possession_data.ing_vulnerability.power_bomb.damage_multiplier = 3000.0

    with area.get_instance(0x0200B0).edit_properties(MemoryRelay) as relay:
        relay.editor_properties.active = True

    with area.get_instance("Pickup Object").edit_properties(Pickup) as pickup:
        pickup.fadetime = 1.0


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.MAIN_REACTOR_MREA)
def main_reactor(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Change layers properly after DS1's death.
    """
    layer_switcher = area.get_instance("Switch Layers To Post-Dark Samus")
    layer_controller = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            layer=LayerSwitch(
                area_id=agon_wastes.BIOSTORAGE_STATION_INTERNAL_ID,
                layer_number=3,  # 1st Pass
            )
        )
    )
    layer_switcher.add_connection(State.Zero, Message.Decrement, layer_controller)


@decorate_patcher(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.DYNAMO_WORKS_MREA)
def dynamo_works(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Fix Spider Guardian's response to PBs.
    """
    with area.get_instance("IngSpiderballGuardian 001").edit_properties(IngSpiderballGuardian) as spider:
        custom_rule = editor.get_custom_asset("custom_knockback.RULE")
        assert custom_rule is not None
        spider.patterned.knockback_rules = custom_rule


@decorate_patcher(TORVUS_BOG_MLVL, torvus_bog.TORVUS_TEMPLE_MREA)
def torvus_temple(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Reduce the size of the barrier such that it doesn't block the path to lower Torvus.
    """
    with area.get_instance(0x1B00E0).edit_properties(Actor) as barrier:
        barrier.editor_properties.transform.position.x = -226.4198
        barrier.editor_properties.transform.position.z = 58.7156
        barrier.editor_properties.transform.scale.y = 2.019


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.GFMC_COMPOUND_MREA)
def gfmc_compound(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
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
def sanctuary_entrance(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Change the Keybearer to spawn on the Default layer, removing the Spider Guardian requirement.
    """
    area.move_instance("Dead Luminoth 4 KeyBearer", "Default")
    area.move_instance("Luminoth Light Support", "Default")


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
        west_spawn_trigger.editor_properties.transform.scale = Vector(10.0, 10.0, 10.0)

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
