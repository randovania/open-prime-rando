import copy

import open_prime_rando.echoes.asset_ids.world
from open_prime_rando.patcher_editor import PatcherEditor


def expand_schema(base_schema: dict, editor: PatcherEditor) -> dict:
    schema = copy.deepcopy(base_schema)

    world_props = schema["properties"]["worlds"]["properties"] = {}
    for world, mlvl_id in open_prime_rando.echoes.asset_ids.world.NAME_TO_ID_MLVL.items():
        world_def = copy.deepcopy(schema["$defs"]["world"])
        world_props[world] = world_def

        mlvl = editor.get_mlvl(mlvl_id)
        area_props = {}
        world_def["properties"]["areas"] = {"type": "object", "additionalProperties": False, "properties": area_props}

        world_details = open_prime_rando.echoes.asset_ids.world.load_dedicated_file(world)
        mrea_to_name: dict[int, str] = {
            mrea: name
            for name, mrea in world_details.NAME_TO_ID_MREA.items()
        }

        for area in mlvl.areas:
            area_name = mrea_to_name[area.mrea_asset_id]
            area_def = copy.deepcopy(schema["$defs"]["area"])
            area_props[area_name] = area_def

            area_def["properties"]["docks"] = {
                "type": "object",
                "properties": {
                    dock_name: {"$ref": "#/$defs/dock"}
                    for dock_name in world_details.DOCK_NAMES.get(area_name, {}).keys()
                },
                "default": {},
                "additionalProperties": False,
            }

            area_def["properties"]["layers"] = {
                "type": "object",
                "properties": {
                    layer.name: {"type": "boolean"}
                    for layer in area.layers
                },
                "default": {},
                "additionalProperties": False,
            }

    return schema
