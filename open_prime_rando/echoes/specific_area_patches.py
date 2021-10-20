import logging
from pathlib import Path
from typing import Container

from retro_data_structures.asset_provider import AssetProvider
from retro_data_structures.formats.mrea import Mrea
from retro_data_structures.formats.script_object import ScriptInstanceHelper
from retro_data_structures.game_check import Game

LOG = logging.getLogger("echoes_patcher")

def specific_patches(asset_provider: AssetProvider, output_path: Path):
    def get_mrea(asset_id) -> Mrea:
        with asset_provider:
            return asset_provider.get_asset(asset_id)
    
    def write_file(area: Mrea, path):
        LOG.info(f"Writing MREA: {path}...")
        output_path.joinpath(path).write_bytes(area.build())
    
    write_file(*sand_mining(get_mrea(0xDB7B2CED)))
    write_file(*torvus_generator(get_mrea(0x133BF5B8)))

def sand_mining(area: Mrea):
    post_pickup_relay = area.get_instance(0x80121)

    properties = post_pickup_relay.get_properties()
    properties.EditorProperties.Active = True
    post_pickup_relay.set_properties(properties)

    return area, "04_sand_mining.MREA"

def create_layer_controller(area_id: int, layer: int, dynamic: bool = False) -> ScriptInstanceHelper:
    layer_controller = ScriptInstanceHelper.new_instance(Game.ECHOES, "SLCT")
    props = layer_controller.get_properties()

    props.EditorProperties.Name = "Layer Controller"
    props.EditorProperties.Transform.Scale = Container({"X": 1.0, "Y": 1.0, "Z": 1.0})
    props.EditorProperties.Active = True
    props.EditorProperties.Unknown = 3

    props.Layer["Area ID"] = area_id
    props.Layer["Layer #"] = layer
    props.IsDynamic = dynamic

    layer_controller.set_properties(props)
    return layer_controller

def torvus_generator(area: Mrea):
    layer_controller_ids = [2687307, 2687027, 2687028, 2687029]

    for _id in layer_controller_ids:
        layer_controller = area.get_instance(_id)
        props = layer_controller.get_properties()
        props.EditorProperties.Active = True
        layer_controller.set_properties(props)
    
    # TODO: generate new instance IDs
    layer_cont1 = create_layer_controller(0x9A2ACAFD, 3)
    layer_cont2 = create_layer_controller(0x9A2ACAFD, 3)

    # TODO: add new layers
    # TODO: add new objects to new layers

    obj = area.get_instance(2686994)
    obj.add_connection("Zero", "Increment", layer_cont1)
    obj.add_connection("Zero", "Increment", layer_cont2)

    return area, "00_swamp_generator.MREA"