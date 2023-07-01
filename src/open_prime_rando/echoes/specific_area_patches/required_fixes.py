import logging
from collections.abc import Iterable

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats.mrea import Area
from retro_data_structures.formats.script_object import InstanceIdRef
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import (
    HUDMemo,
    Pickup,
    Relay,
    SpawnPoint,
    Switch,
    Timer,
    Trigger,
)

from open_prime_rando.echoes.asset_ids import agon_wastes, sanctuary_fortress, temple_grounds, torvus_bog
from open_prime_rando.echoes.asset_ids.world import (
    AGON_WASTES_MLVL,
    SANCTUARY_FORTRESS_MLVL,
    TEMPLE_GROUNDS_MLVL,
    TORVUS_BOG_MLVL,
)
from open_prime_rando.patcher_editor import PatcherEditor

LOG = logging.getLogger("echoes_patcher")


def required_fixes(editor: PatcherEditor):
    """
    Applies changes necessary for the game to function properly.
    """
    mining_station_b(editor)
    undertemple_access(editor)
    main_reactor(editor)
    sacrificial_chamber(editor)
    aerie(editor)
    main_research(editor)
    hive_chamber_b(editor)
    gfmc_compound(editor)
    torvus_temple(editor)


def mining_station_b(editor: PatcherEditor):
    """
    Normally this relay is activated by the cutscene, but has an incoming connection from the pickup.
    Activating it like this means the pickup will trigger the relay without the cutscene
    """
    area = editor.get_area(AGON_WASTES_MLVL, agon_wastes.MINING_STATION_B_MREA)
    with area.get_instance(0x80121).edit_properties(Relay) as post_pickup_relay:
        post_pickup_relay.editor_properties.active = True


def undertemple_access(editor: PatcherEditor):
    """
    Move the default spawn point in-bounds.
    """
    area = editor.get_area(TORVUS_BOG_MLVL, torvus_bog.UNDERTEMPLE_ACCESS_MREA)

    with area.get_instance("Spawn point 001").edit_properties(SpawnPoint) as spawn:
        spawn.editor_properties.transform.position.x = -149.25


def main_reactor(editor: PatcherEditor):
    """
    Save some memory during DS1 fight.
    """
    area = editor.get_area(AGON_WASTES_MLVL, agon_wastes.MAIN_REACTOR_MREA)

    unload_relay = area.get_instance("Unload dock when door closed")
    trigger = area.get_instance("Trigger Start DS Intro")
    trigger.add_connection(State.Entered, Message.SetToZero, unload_relay)


def sacrificial_chamber(editor: PatcherEditor):
    """
    Unknown purpose.
    """
    area = editor.get_area(TORVUS_BOG_MLVL, torvus_bog.SACRIFICIAL_CHAMBER_MREA)

    with area.get_instance("If grapple attainment is loaded, then end battle").edit_properties(Switch) as switch:
        switch.is_open = True


def _patch_echo_gate_softlock(
        area: Area,
        counter: InstanceIdRef,
        relays: Iterable[tuple[InstanceIdRef, InstanceIdRef]]
        ):
    for shot_relay_id, memory_relay_id in relays:
        shot_relay = area.get_instance(shot_relay_id)
        memory_relay = area.get_instance(memory_relay_id)

        shot_relay.remove_connections_from(counter)
        memory_relay.add_connection(State.Active, Message.Increment, counter)


def aerie(editor: PatcherEditor):
    """
    Patches an echo gate softlock.
    """
    area = editor.get_area(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.AERIE_MREA)

    relays = (
        (0x410094, 0x41008D),
        (0x410077, 0x41007F),
        (0x4100B5, 0x4100B6)
    )
    _patch_echo_gate_softlock(area, 0x4100BE, relays)


def main_research(editor: PatcherEditor):
    "Patches an echo gate softlock."
    area = editor.get_area(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.MAIN_RESEARCH_MREA)

    relays = (
        (0x0B02E6, 0x0B02DE),
        (0x0B0303, 0x0B030D),
        (0x0B02F6, 0x0B02FA)
    )
    _patch_echo_gate_softlock(area, 0x0B0315, relays)


def hive_chamber_b(editor: PatcherEditor):
    """
    Removes item loss sequence.
    """
    area = editor.get_area(TEMPLE_GROUNDS_MLVL, temple_grounds.HIVE_CHAMBER_B_MREA)

    # FIXME: use layers API
    area.get_layer("DS Appears Part1").active = False
    area.get_layer("Pre Dark Samus Music").active = False

    area.get_layer("Pickup").active = True
    area.get_layer("Post Dark Samus Music").active = True


def gfmc_compound(editor: PatcherEditor):
    """
    Add a HUDMemo for the ship missile.
    """
    area = editor.get_area(TEMPLE_GROUNDS_MLVL, temple_grounds.GFMC_COMPOUND_MREA)

    pickup_xfm = area.get_instance(0x2B0324).get_properties_as(Pickup).editor_properties.transform
    ship_trigger = area.get_layer("Default").add_instance_with(Trigger(
        editor_properties=EditorProperties(
            name="Show Ship Missile HudMemo",
            transform=Transform(
                position=pickup_xfm.position,
                rotation=Vector(0.0, 0.0, 45.0),
                scale=Vector(50.0, 50.0, 10.0)
            )
        ),
        deactivate_on_enter=True
    ))
    strg_id, _ = editor.create_strg(
        "gfmc_jump_hudmemo.STRG",
        ["Defeating Jump Guardian is required for this item to appear."]
    )
    hud_memo = area.get_layer("Default").add_instance_with(HUDMemo(
        editor_properties=EditorProperties(
            name="Ship Missile HudMemo",
            transform=pickup_xfm
        ),
        display_time=6.0,
        display_type=0,
        string=strg_id
    ))
    ship_trigger.add_connection(State.Entered, Message.SetToZero, hud_memo)

    timer = area.get_layer("Space Jump").add_instance_with(Timer(
        editor_properties=EditorProperties(
            name="Disable Ship Missile Trigger",
            transform=pickup_xfm
        ),
        time=0.1,
        auto_start=True
    ))
    timer.add_connection(State.Zero, Message.Deactivate, ship_trigger)


def torvus_temple(editor: PatcherEditor):
    """
    Remove cosmetic objects from Torvus Temple to minimize the chance of crash via alloc failure
    """
    area = editor.get_area(TORVUS_BOG_MLVL, torvus_bog.TORVUS_TEMPLE_MREA)

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

