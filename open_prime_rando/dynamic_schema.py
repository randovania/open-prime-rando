import copy

from open_prime_rando.patcher_editor import PatcherEditor
import open_prime_rando.echoes.asset_ids.world


def expand_schema(base_schema: dict, editor: PatcherEditor) -> dict:
    schema = copy.deepcopy(base_schema)

    world_props = schema["properties"]["worlds"]["properties"] = {}
    for world, mlvl_id in open_prime_rando.echoes.asset_ids.world.NAME_TO_ID.items():
        world_def = copy.deepcopy(schema["$defs"]["world"])
        world_props[world] = world_def

        mlvl = editor.get_mlvl(mlvl_id)
        area_props = {}
        world_def["properties"]["areas"] = {"type": "object", "additionalProperties": False, "properties": area_props}

        for area in mlvl.areas:
            area_def = copy.deepcopy(schema["$defs"]["area"])
            area_props[area.name] = area_def

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
