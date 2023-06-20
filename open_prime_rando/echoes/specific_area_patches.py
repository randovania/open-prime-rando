import logging

from construct import Container

from open_prime_rando.echoes.asset_ids.agon_wastes import MINING_STATION_B_MREA, PORTAL_TERMINAL_MREA
from open_prime_rando.echoes.asset_ids.torvus_bog import TORVUS_ENERGY_CONTROLLER_MREA, TORVUS_TEMPLE_MREA
from open_prime_rando.echoes.asset_ids.world import TORVUS_BOG_MLVL
from open_prime_rando.patcher_editor import PatcherEditor
from retro_data_structures.formats.script_object import ScriptInstanceHelper
from retro_data_structures.game_check import Game
from retro_data_structures.properties.echoes.objects.Counter import Counter
from retro_data_structures.properties.echoes.objects.Relay import Relay
from retro_data_structures.properties.echoes.objects.ScriptLayerController import ScriptLayerController
from retro_data_structures.enums.echoes import State, Message

LOG = logging.getLogger("echoes_patcher")


def specific_patches(editor: PatcherEditor, area_patches: dict):
    # sand_mining(editor)
    # torvus_generator(editor)
    if area_patches["torvus_temple"]:
        torvus_temple_crash(editor)


def sand_mining(editor: PatcherEditor):
    area = editor.get_mrea(MINING_STATION_B_MREA)
    post_pickup_relay = area.get_instance(0x80121)

    properties = post_pickup_relay.get_properties()
    assert isinstance(properties, Relay)
    properties.editor_properties.active = True
    post_pickup_relay.set_properties(properties)


def create_layer_controller(area_id: int, layer: int, dynamic: bool = False) -> ScriptInstanceHelper:
    layer_controller = ScriptInstanceHelper.new_instance(Game.ECHOES, "SLCT")
    props = layer_controller.get_properties()
    assert isinstance(props, ScriptLayerController)

    props.editor_properties.name = "Layer Controller"
    props.editor_properties.transform.Scale = Container({"X": 1.0, "Y": 1.0, "Z": 1.0})
    props.editor_properties.active = True
    props.editor_properties.unknown = 3

    props.layer.area_id = area_id
    props.layer.layer_number = layer
    props.IsDynamic = dynamic

    layer_controller.set_properties(props)
    return layer_controller


def torvus_generator(editor: PatcherEditor):
    area = editor.get_mrea(TORVUS_ENERGY_CONTROLLER_MREA)
    layer_controller_ids = [2687307, 2687027, 2687028, 2687029]

    for _id in layer_controller_ids:
        layer_controller = area.get_instance(_id)
        props = layer_controller.get_properties()
        assert isinstance(props, ScriptLayerController)
        props.editor_properties.active = True
        layer_controller.set_properties(props)

    # TODO: generate new instance IDs
    layer_cont1 = create_layer_controller(0x9A2ACAFD, 3)
    layer_cont2 = create_layer_controller(0x9A2ACAFD, 3)

    # TODO: add new layers
    # TODO: add new objects to new layers

    obj = area.get_instance(2686994)
    obj.add_connection(State.Zero, Message.Increment, layer_cont1)
    obj.add_connection(State.Zero, Message.Increment, layer_cont2)


def torvus_temple_crash(editor: PatcherEditor):
    """
    Remove cosmetic objects from Torvus Temple to minimize the chance of chance via alloc failure
    """
    world = editor.get_mlvl(TORVUS_BOG_MLVL)
    area = world.get_area(TORVUS_TEMPLE_MREA)

    default = area.get_layer("Default")
    first_pass = area.get_layer("1st Pass")
    second_pass = area.get_layer("2nd PAss")

    for obj in ["Thrust1", "Thrust1", "Thrust2", "Thrust2", "Looping Thrust w/Doppler", "Looping Thrust w/Doppler"]:
        first_pass.remove_instance(obj)

    for obj in ["GENERATE GIBS"]:
        second_pass.remove_instance(obj)

    # These are generated objects, so to remove these we need to change the generated objects layer
    # Since that isn't properly exposed by RDS, let's skip for now
    # debris = ["SwampCrateDebris"] * 7
    # for obj in ["GibFlash", "Sound - Swamp Crate Gib"] + debris:
    #     default.remove_instance(obj)


def agon_wastes_portal_terminal_puzzle_patch(editor: PatcherEditor):
    """
    Patches Agon Wastes - Portal Terminal to behave like in GC NTSC-U/PAL
    In GC NTSC-J version a counter was added to check for each cork to be broken
    """
    area = editor.get_mrea(PORTAL_TERMINAL_MREA)

    """
    Remove counter increment on the 2 first corks to destroy
    """
    relay_ids = [0x12033A, 0x120343]  # 0x120307 is the last cork to destroy
    for relay_id in relay_ids:
        relay = area.get_instance(relay_id)

        properties = relay.get_properties()
        assert isinstance(properties, Relay)
        relay.remove_connections([0x12044E])
        relay.set_properties(properties)

    """
    Set the destroyed cork counter to expect only one cork to be destroyed
    """
    counter = area.get_instance(0x12044E)

    with counter.edit_properties(Counter) as props:
        props.editor_properties.unknown = 1
        props.max_count = 1
