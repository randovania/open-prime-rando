
from retro_data_structures.formats import Mapa, Mlvl
from retro_data_structures.formats.mrea import Area
from retro_data_structures.formats.script_layer import ScriptLayer
from retro_data_structures.formats.script_object import InstanceId, ScriptInstance
from retro_data_structures.properties.echoes.objects.AreaAttributes import AreaAttributes
from retro_data_structures.properties.echoes.objects.SafeZone import SafeZone
from retro_data_structures.properties.echoes.objects.SafeZoneCrystal import SafeZoneCrystal

from open_prime_rando.echoes.asset_ids import world as world_ids
from open_prime_rando.echoes.inverted import area_pairs
from open_prime_rando.patcher_editor import PatcherEditor

_WORLDS = [
    world_ids.TEMPLE_GROUNDS_MLVL, world_ids.AGON_WASTES_MLVL, world_ids.TORVUS_BOG_MLVL,
    world_ids.SANCTUARY_FORTRESS_MLVL, world_ids.GREAT_TEMPLE_MLVL,
]
_AREAS_TO_SKIP = {
    0x775664a5,  # 00_scandummy
    0x752b2850,  # game_end_part1
    0x9d221f4a,  # game_end_part2
    0xc5250dbc,  # game_end_part3
    0x9641773f,  # game_end_part4
    0xce4665c9,  # game_end_part5
    0x4d4e5400,  # Menu
}


def _swap_dark_world(editor: PatcherEditor):
    for world_id in _WORLDS:
        world = editor.get_mlvl(world_id)

        for area in world.areas:
            if area.id in _AREAS_TO_SKIP:
                continue

            is_dark_world = area.internal_name.endswith("_dark")

            for instance in area.all_instances:
                if instance.type == AreaAttributes:
                    with instance.edit_properties(AreaAttributes) as prop:
                        if prop.dark_world != is_dark_world:
                            print(area.name, is_dark_world, "found", prop.dark_world)
                        prop.dark_world = not is_dark_world

            mapa_id = world.mapw.get_mapa_id(area.index)
            mapa = editor.get_file(mapa_id, Mapa)
            mapa.raw.type = not is_dark_world


def _copy_safe_zones(dark: Area, dark_layer: ScriptLayer, light_layer: ScriptLayer,
                     special_ids: set):
    copied_safe_zones = {}

    for instance in list(dark_layer.instances):
        if instance.type == SafeZone:
            copied_safe_zones[instance.id] = light_layer.add_instance_with(instance.get_properties_as(SafeZone))

            ids = {conn.target for conn in instance.connections}
            for target in ids:
                target_name = dark.get_instance(target).name
                if "ENTERED Safezone" not in target_name and "EXITED Safezone" not in target_name:
                    special_ids.add(instance.id)

            if instance.id not in special_ids:
                dark_layer.remove_instance(instance)

    return copied_safe_zones


def _copy_safe_zone_crystal(copied_crystal: ScriptInstance,
                            instance: ScriptInstance,
                            copied_safe_zones: dict[InstanceId, ScriptInstance],
                            dark: Area, special_ids: set[int],
                            ):
    targets_special = False

    for conn in instance.connections:
        if conn.target == instance.id:
            target = copied_crystal
        elif conn.target in copied_safe_zones:
            targets_special = targets_special or conn.target in special_ids
            target = copied_safe_zones[conn.target]
        else:
            targets_special = True
            weird_target = dark.get_instance(conn.target)
            print(
                f"Crystal {instance.name} at {dark.name} has unexpected connections "
                f"to {weird_target} ({weird_target.name})")
            continue
        copied_crystal.add_connection(conn.state, conn.message, target)

    return targets_special


def _move_safe_zones(world: Mlvl, pairs: list[tuple[int, int]]):
    for light_id, dark_id in pairs:
        light = world.get_area(light_id)
        dark = world.get_area(dark_id)

        light_layer = light.get_layer("Default")
        dark_layer = dark.get_layer("Default")

        assert light_layer.index == 0

        special_ids = set()  # ids for objects that have extra functionality and we want to keep

        # Copy the safe zones
        copied_safe_zones = _copy_safe_zones(dark, dark_layer, light_layer, special_ids)

        # Copy the safe zone crystals
        for instance in list(dark_layer.instances):
            if instance.type == SafeZoneCrystal:
                copied_crystal = light_layer.add_instance_with(instance.get_properties_as(SafeZoneCrystal))

                targets_special = _copy_safe_zone_crystal(
                    copied_crystal, instance, copied_safe_zones, dark, special_ids
                )
                if not targets_special:
                    dark_layer.remove_instance(instance)


def apply_inverted(editor: PatcherEditor):
    _swap_dark_world(editor)

    _move_safe_zones(editor.get_mlvl(world_ids.TEMPLE_GROUNDS_MLVL), area_pairs.TG_PAIRS)
    _move_safe_zones(editor.get_mlvl(world_ids.AGON_WASTES_MLVL), area_pairs.AGON_PAIRS)
    _move_safe_zones(editor.get_mlvl(world_ids.TORVUS_BOG_MLVL), area_pairs.TORVUS_PAIRS)
    _move_safe_zones(editor.get_mlvl(world_ids.SANCTUARY_FORTRESS_MLVL), area_pairs.SANCTUARY_PAIRS)
    _move_safe_zones(editor.get_mlvl(world_ids.GREAT_TEMPLE_MLVL), area_pairs.GREAT_TEMPLE_PAIRS)
