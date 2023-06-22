import dataclasses

import construct
from retro_data_structures.base_resource import Dependency, RawResource
from retro_data_structures.dependencies import recursive_dependencies_for_editor
from retro_data_structures.formats import Mlvl
from retro_data_structures.properties.echoes.objects.AreaAttributes import AreaAttributes
from retro_data_structures.properties.echoes.objects.SafeZone import SafeZone
from retro_data_structures.properties.echoes.objects.SafeZoneCrystal import SafeZoneCrystal

from open_prime_rando.echoes.asset_ids import world as world_ids
from open_prime_rando.echoes.inverted.area_pairs import TG_PAIRS, AGON_PAIRS
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


def collect_dependencies(obj):
    for field in dataclasses.fields(obj):
        if "asset_types" in field.metadata:
            yield getattr(obj, field.name)


_all_deps_cache: dict[frozenset[int], set[Dependency]] = {}


def _swap_dark_world(editor: PatcherEditor):
    for world_id in _WORLDS:
        world = editor.get_mlvl(world_id)

        for area in world.areas:
            if area.id in _AREAS_TO_SKIP:
                continue

            is_dark_world = area.internal_name.endswith("_dark")

            for layer in area.layers:
                for instance in layer.instances:
                    if instance.type == AreaAttributes:
                        prop = instance.get_properties()
                        assert isinstance(prop, AreaAttributes)
                        if prop.dark_world != is_dark_world:
                            print(area.name, is_dark_world, "found", prop.dark_world)
                        prop.dark_world = not is_dark_world
                        instance.set_properties(prop)

            mapa_id = world.mapw.get_mapa_id(area.index)
            mapa = bytearray(editor.get_raw_asset(mapa_id).data)
            mapa[8:12] = construct.Int32ub.build(not is_dark_world)
            editor.replace_asset(
                mapa_id,
                RawResource("MAPA", bytes(mapa))
            )


def _move_safe_zones(world: Mlvl, pairs: list[tuple[int, int]]):
    for pair in pairs:
        light = world.get_area(pair[0])
        dark = world.get_area(pair[1])

        light_layer = light.get_layer("Default")
        dark_layer = dark.get_layer("Default")

        assert light_layer.index == 0

        new_dependencies = set()  # asset ids that must be added to the mlvl dependency list
        special_ids = set()  # ids for objects that have extra functionality and we want to keep
        copied_safe_zones = {}

        # Copy the safe zones
        for instance in list(dark_layer.instances):
            if instance.type == SafeZone:
                copied_safe_zones[instance.id] = light_layer.add_instance_with(props := instance.get_properties())
                assert isinstance(props, SafeZone)
                new_dependencies.add(props.impact_effect)

                ids = {conn.target for conn in instance.connections}
                for target in ids:
                    target_name = dark.get_instance(target).name
                    if "ENTERED Safezone" not in target_name and "EXITED Safezone" not in target_name:
                        special_ids.add(instance.id)

                if instance.id not in special_ids:
                    dark_layer.remove_instance(instance)

        # Copy the safe zone crystals
        for instance in list(dark_layer.instances):
            if instance.type == SafeZoneCrystal:
                copied_crystal = light_layer.add_instance_with(props := instance.get_properties())
                new_dependencies.update(collect_dependencies(props))

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
                            f"Crystal {instance.name} at {dark.name} has unexpected connections to {weird_target} ({weird_target.name})")
                        continue
                    copied_crystal.add_connection(conn.state, conn.message, target)

                if not targets_special:
                    dark_layer.remove_instance(instance)

        assert 0xffffffff not in new_dependencies

        # Update dependencies

        # Add assets used by safe zones
        new_dependencies = frozenset(new_dependencies)
        if new_dependencies not in _all_deps_cache:
            _all_deps_cache[new_dependencies] = recursive_dependencies_for_editor(
                world.asset_manager, list(new_dependencies)
            )

        dependencies = light._raw.dependencies
        assert isinstance(dependencies.dependencies_b, list)
        for dep in _all_deps_cache[new_dependencies]:
            dependencies.dependencies_b.append(construct.Container(
                asset_id=dep.id,
                asset_type=dep.type,
            ))

        for i in range(1, len(dependencies.dependencies_offset)):
            dependencies.dependencies_offset[i] += len(new_dependencies)

        # Add Safe Zone's module dep
        module_dependencies = light._raw.module_dependencies
        for module_dep in set(SafeZone.modules() + SafeZoneCrystal.modules()):
            if module_dep not in module_dependencies.rel_module:
                module_dependencies.rel_module.insert(0, module_dep)
                for i in range(1, len(module_dependencies.rel_offset)):
                    module_dependencies.rel_offset[i] += 1


def apply_inverted(editor: PatcherEditor):
    _swap_dark_world(editor)

    _move_safe_zones(editor.get_mlvl(world_ids.TEMPLE_GROUNDS_MLVL), area_pairs.TG_PAIRS)
    _move_safe_zones(editor.get_mlvl(world_ids.AGON_WASTES_MLVL), area_pairs.AGON_PAIRS)
    _move_safe_zones(editor.get_mlvl(world_ids.TORVUS_BOG_MLVL), area_pairs.TORVUS_PAIRS)
    _move_safe_zones(editor.get_mlvl(world_ids.SANCTUARY_FORTRESS_MLVL), area_pairs.SANCTUARY_PAIRS)
    _move_safe_zones(editor.get_mlvl(world_ids.GREAT_TEMPLE_MLVL), area_pairs.GREAT_TEMPLE_PAIRS)
