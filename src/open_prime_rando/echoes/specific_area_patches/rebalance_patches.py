from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.properties.echoes.archetypes.LayerSwitch import LayerSwitch
from retro_data_structures.properties.echoes.objects import (
    Actor,
    IngSpiderballGuardian,
    MemoryRelay,
    Pickup,
    ScriptLayerController,
    SpawnPoint,
    Splinter,
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
