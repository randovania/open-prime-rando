import logging

from construct import Container
from retro_data_structures.formats.script_object import ScriptInstanceHelper
from retro_data_structures.game_check import Game
from retro_data_structures.properties.echoes.objects.Relay import Relay
from retro_data_structures.properties.echoes.objects.ScriptLayerController import ScriptLayerController

from open_prime_rando.echoes.asset_ids.agon_wastes import MINING_STATION_B_MREA
from open_prime_rando.echoes.asset_ids.torvus_bog import TORVUS_ENERGY_CONTROLLER_MREA
from open_prime_rando.patcher_editor import PatcherEditor

LOG = logging.getLogger("echoes_patcher")


def specific_patches(editor: PatcherEditor):
    sand_mining(editor)
    torvus_generator(editor)


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
    obj.add_connection("Zero", "Increment", layer_cont1)
    obj.add_connection("Zero", "Increment", layer_cont2)
