import logging
from collections.abc import Iterable

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats.mrea import Area
from retro_data_structures.formats.script_object import InstanceId, InstanceRef
from retro_data_structures.properties.echoes.archetypes.LayerSwitch import LayerSwitch
from retro_data_structures.properties.echoes.objects import (
    Actor,
    IngSpiderballGuardian,
    MemoryRelay,
    Pickup,
    ScriptLayerController,
    Splinter,
    Timer,
)

from open_prime_rando.echoes.asset_ids import agon_wastes, great_temple, sanctuary_fortress, temple_grounds, torvus_bog
from open_prime_rando.echoes.asset_ids.world import (
    AGON_WASTES_MLVL,
    GREAT_TEMPLE_MLVL,
    SANCTUARY_FORTRESS_MLVL,
    TEMPLE_GROUNDS_MLVL,
    TORVUS_BOG_MLVL,
)
from open_prime_rando.patcher_editor import PatcherEditor

LOG = logging.getLogger("echoes_patcher")


def apply_all(editor: PatcherEditor):
    """
    Applies patches that rebalance aspects of the game for a better rando experience.
    """
    landing_site(editor)
    bionergy_production(editor)
    remove_luminoth_barriers(editor)
    torvus_energy_controller(editor)
    hive_tunnel(editor)
    agon_temple(editor)
    temple_sanctuary(editor)
    main_reactor(editor)
    dynamo_works(editor)
    torvus_temple(editor)
    gfmc_compound(editor)


def landing_site(editor: PatcherEditor):
    """
    Removes the intro cinematic.
    """
    area = editor.get_area(TEMPLE_GROUNDS_MLVL, temple_grounds.LANDING_SITE_MREA)

    remove_intro = True

    # FIXME: use layers API
    area.get_layer("1st Pass - Intro Cinematic").active = not remove_intro
    for layer_name in ("Save Station Load", "Ship Repair", "Luminoth Key Bearer", "WAR CHEST"):
        area.get_layer(layer_name).active = remove_intro

    if remove_intro:
        timer = area.get_layer("Default").add_instance_with(Timer(time=0.01, auto_start=True))
        for inst in ("Keep Samus Ship", "Savestation Recharge Always Plays", "Ambient Music Memory Relay"):
            # TODO: unclear whether the timer is necessary, or if we can just activate these immediately
            timer.add_connection(State.Zero, Message.Activate, area.get_instance(inst))


def bionergy_production(editor: PatcherEditor):
    """
    Deactivate the trigger for flying pirates after killing them all.
    """
    area = editor.get_area(AGON_WASTES_MLVL, agon_wastes.BIOENERGY_PRODUCTION_MREA)

    counter = area.get_instance("Dead Pirates")
    counter.add_connection(State.MaxReached, Message.Deactivate, area.get_instance("Turn On Flying Pirates"))


def _disable_layer_controllers(area: Area, layer_controllers: Iterable[InstanceRef]):
    for inst in layer_controllers:
        with area.get_instance(inst).edit_properties(ScriptLayerController) as controller:
            controller.editor_properties.active = False


def remove_luminoth_barriers(editor: PatcherEditor):
    """
    Remove Luminoth barriers throughout the game.
    """
    # Agon Energy Controller
    agon = editor.get_area(AGON_WASTES_MLVL, agon_wastes.AGON_ENERGY_CONTROLLER_MREA)
    _disable_layer_controllers(agon, ["Increment - 07_Temple - Luminoth Barrier Swamp"])

    # Torvus Energy Controller
    torvus = editor.get_area(TORVUS_BOG_MLVL, torvus_bog.TORVUS_ENERGY_CONTROLLER_MREA)
    _disable_layer_controllers(torvus, ["Increment - 07_Temple - Luminoth Barrier Cliffs"])

    # Dark Agon Energy Controller
    dark_agon = editor.get_area(AGON_WASTES_MLVL, agon_wastes.DARK_AGON_ENERGY_CONTROLLER_MREA)
    _disable_layer_controllers(dark_agon, ["Increment - 0A_Sand_Hall - Luminoth Barriers"])

    # Dark Torvus Energy Controller
    dark_torvus = editor.get_area(TORVUS_BOG_MLVL, torvus_bog.DARK_TORVUS_ENERGY_CONTROLLER_MREA)
    _disable_layer_controllers(
        dark_torvus, ("Increment - 0A_Swamp - Luminoth Barriers", "Increment - 04_Swamp - Luminoth Barriers")
    )

    # Hive Energy Controller
    hive = editor.get_area(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.HIVE_ENERGY_CONTROLLER_MREA)
    _disable_layer_controllers(
        hive,
        (
            "Increment - 0P_Cliff - Luminoth Barriers",
            "Increment - 0A_Cliff - Luminoth Barriers",
            "Increment - 0Q_Cliff - Luminoth Barriers",
        ),
    )


def torvus_energy_controller(editor: PatcherEditor):
    """
    Don't remove the Torvus Temple fight.
    """
    area = editor.get_area(TORVUS_BOG_MLVL, torvus_bog.TORVUS_ENERGY_CONTROLLER_MREA)
    _disable_layer_controllers(
        area,
        (
            "DECREMENT 04_Swamp_Temple 1st Pass",
            "Decrement - 04_Swamp_Temple - 1st Pass",
            "Increment - 04_Swamp_Temple - 2ndPass",
        ),
    )


def hive_tunnel(editor: PatcherEditor):
    """
    Unknown purpose.
    """
    area = editor.get_area(TEMPLE_GROUNDS_MLVL, temple_grounds.HIVE_TUNNEL_MREA)

    with area.get_instance("Timer 001").edit_properties(Timer) as timer:
        timer.time = 0.02
    with area.get_instance("Decrement - Webbing").edit_properties(ScriptLayerController) as controller:
        controller.is_dynamic = False


def agon_temple(editor: PatcherEditor):
    """
    No longer locks the doors after the Bomb Guardian fight.
    """
    area = editor.get_area(AGON_WASTES_MLVL, agon_wastes.AGON_TEMPLE_MREA)

    area.get_layer("Lock Doors").active = False  # FIXME: use layers API


def temple_sanctuary(editor: PatcherEditor):
    """
    Patches Alpha Splinter to take damage properly from Power Bombs.
    Keep the Emerald gate active from the beginning.
    Fade in the Pickup.
    """
    area = editor.get_area(GREAT_TEMPLE_MLVL, great_temple.TEMPLE_SANCTUARY_MREA)

    with area.get_instance("MEGA Splinter Light").edit_properties(Splinter) as alpha:
        custom_rule = editor._resolve_asset_id("custom_knockback.RULE")
        alpha.patterned.knockback_rules = custom_rule
        alpha.ing_possession_data.ing_vulnerability.power_bomb.damage_multiplier = 3000.0

    with area.get_instance(0x0200B0).edit_properties(MemoryRelay) as relay:
        relay.editor_properties.active = True

    with area.get_instance("Pickup Object").edit_properties(Pickup) as pickup:
        pickup.fadetime = 1.0


def main_reactor(editor: PatcherEditor):
    """
    Change layers properly after DS1's death.
    """
    area = editor.get_area(AGON_WASTES_MLVL, agon_wastes.MAIN_REACTOR_MREA)

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


def dynamo_works(editor: PatcherEditor):
    """
    Fix Spider Guardian's response to PBs.
    """
    area = editor.get_area(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.DYNAMO_WORKS_MREA)

    with area.get_instance("IngSpiderballGuardian 001").edit_properties(IngSpiderballGuardian) as spider:
        custom_rule = editor._resolve_asset_id("custom_knockback.RULE")
        spider.patterned.knockback_rules = custom_rule


def torvus_temple(editor: PatcherEditor):
    """
    Reduce the size of the barrier such that it doesn't block the path to lower Torvus.
    """
    area = editor.get_area(TORVUS_BOG_MLVL, torvus_bog.TORVUS_TEMPLE_MREA)
    with area.get_instance(0x1B00E0).edit_properties(Actor) as barrier:
        barrier.editor_properties.transform.position.x = -226.4198
        barrier.editor_properties.transform.position.z = 58.7156
        barrier.editor_properties.transform.scale.y = 2.019


def gfmc_compound(editor: PatcherEditor):
    """
    Move the gate to the Default layer.
    """
    area = editor.get_area(TEMPLE_GROUNDS_MLVL, temple_grounds.GFMC_COMPOUND_MREA)

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
    for raw_id in gate_instances:
        # TODO: implement a function to move an instance from one layer to another in RDS
        inst_id = InstanceId(raw_id)
        old_inst = area.get_instance(inst_id)
        new_inst = area.get_layer("Default").add_instance_with(old_inst.get_properties())
        area.remove_instance(old_inst)
        new_inst.id = InstanceId.new(new_inst.id.layer, new_inst.id.area, inst_id.instance)
