from retro_data_structures.enums import echoes
from retro_data_structures.formats import Mlvl
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.objects.AreaAttributes import AreaAttributes
from retro_data_structures.properties.echoes.objects.SafeZone import SafeZone
from retro_data_structures.properties.echoes.objects.SafeZoneCrystal import SafeZoneCrystal
from retro_data_structures.properties.echoes.objects.SpecialFunction import SpecialFunction
from retro_data_structures.properties.echoes.objects.Timer import Timer

from open_prime_rando.echoes.asset_ids import world as world_ids
from open_prime_rando.echoes.inverted.area_pairs import TG_PAIRS, AGON_PAIRS
from open_prime_rando.patcher_editor import PatcherEditor


def _modify_world(world: Mlvl, pairs: list[tuple[int, int]]):
    for pair in pairs:
        light = world.get_area(pair[0])
        dark = world.get_area(pair[1])

        module_dependencies = light._raw.module_dependencies
        if "ScriptSafeZone.rel" not in module_dependencies.rel_module:
            module_dependencies.rel_module.insert(0, "ScriptSafeZone.rel")
            for i in range(1, len(module_dependencies.rel_offset)):
                module_dependencies.rel_offset[i] += 1

        light_layer = light.get_layer("Default")
        dark_layer = dark.get_layer("Default")

        special_ids = set()

        copied_safe_zones = {}
        for instance in list(dark_layer.instances):
            if instance.type == SafeZone:
                copied_safe_zones[instance.id] = light_layer.add_instance_with(instance.get_properties())

                ids = {conn.target for conn in instance.connections}
                for target in ids:
                    target_name = dark.get_instance(target).name
                    if "ENTERED Safezone" not in target_name and "EXITED Safezone" not in target_name:
                        special_ids.add(instance.id)

                if instance.id not in special_ids:
                    dark_layer.remove_instance(instance)

        for instance in list(dark_layer.instances):
            if instance.type == SafeZoneCrystal:
                copied_crystal = light_layer.add_instance_with(instance.get_properties())

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
                        print(f"Crystal {instance.name} at {dark.name} has unexpected connections to {weird_target} ({weird_target.name})")
                        continue
                    copied_crystal.add_connection(conn.state, conn.message, target)

                if not targets_special:
                    dark_layer.remove_instance(instance)

        # Area Attributes
        for a, new_value in zip([light, dark], [True, False]):
            for layer in a.layers:
                for instance in layer.instances:
                    if instance.type == AreaAttributes:
                        prop = instance.get_properties()
                        assert isinstance(prop, AreaAttributes)
                        prop.dark_world = new_value
                        instance.set_properties(prop)

        # Timer Stuff
        try:
            dark.get_layer("Default").remove_instance("Timer_Start Dark")
            dark.get_layer("Default").remove_instance("SpecialFunction_Darkworld")
        except KeyError:
            pass

        light_timer = light.get_layer("Default").add_instance_with(Timer(
            editor_properties=EditorProperties(name="Timer_Start InvertedDark"),
            time=0.001,
            auto_start=True,
        ))
        light_function = light.get_layer("Default").add_instance_with(SpecialFunction(
            editor_properties=EditorProperties(name="SpecialFunction_Darkworld Inverted"),
            function=echoes.Function.Darkworld,
        ))
        light_timer.add_connection('ZERO', 'ACTN', light_function)
        light_timer.add_connection('ZERO', 'DECR', light_function)


def apply_inverted(editor: PatcherEditor):
    _modify_world(editor.get_mlvl(world_ids.TEMPLE_GROUNDS_MLVL), area_pairs.TG_PAIRS)
    _modify_world(editor.get_mlvl(world_ids.AGON_WASTES_MLVL), area_pairs.AGON_PAIRS)
    _modify_world(editor.get_mlvl(world_ids.TORVUS_BOG_MLVL), area_pairs.TORVUS_PAIRS)
    _modify_world(editor.get_mlvl(world_ids.SANCTUARY_FORTRESS_MLVL), area_pairs.SANCTUARY_PAIRS)
    _modify_world(editor.get_mlvl(world_ids.GREAT_TEMPLE_MLVL), area_pairs.GREAT_TEMPLE_PAIRS)
