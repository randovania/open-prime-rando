import json
import logging
from pathlib import Path

from retro_data_structures.asset_manager import FileProvider
from retro_data_structures.formats.mlvl import AreaWrapper
from retro_data_structures.enums.echoes import Effect
from retro_data_structures.properties.echoes.objects.DamageableTrigger import DamageableTrigger
from retro_data_structures.game_check import Game

from open_prime_rando import dynamic_schema
from open_prime_rando.echoes import auto_enabled_elevator_patches, specific_area_patches, asset_ids, dock_lock_rando
from open_prime_rando.echoes.inverted import apply_inverted
from open_prime_rando.echoes.small_randomizations import apply_small_randomizations
from open_prime_rando.patcher_editor import PatcherEditor
from open_prime_rando.unique_area_name import get_name_for_area
from open_prime_rando.validator_with_default import DefaultValidatingDraft7Validator

LOG = logging.getLogger("echoes_patcher")


def _read_schema():
    with Path(__file__).parent.joinpath("echoes", "schema.json").open() as f:
        return json.load(f)


def _change_portals_to_all_beams(area: AreaWrapper) -> None:
    def fix_vuln(vuln):
        vuln.damage_multiplier = 100.0
        vuln.effect = Effect.Normal

    for layer in area.layers:
        for obj in layer.instances:
            if obj.type == DamageableTrigger:
                properties = obj.get_properties_as(DamageableTrigger)
                if properties.get_name() == "Shoot to activate PORTAL":
                    fix_vuln(properties.vulnerability.power)
                    fix_vuln(properties.vulnerability.dark)
                    fix_vuln(properties.vulnerability.light)
                    fix_vuln(properties.vulnerability.annihilator)
                    fix_vuln(properties.vulnerability.power_charge)
                    fix_vuln(properties.vulnerability.entangler)
                    fix_vuln(properties.vulnerability.light_blast)
                    fix_vuln(properties.vulnerability.sonic_boom)
                    fix_vuln(properties.vulnerability.super_missle)
                    fix_vuln(properties.vulnerability.black_hole)
                    fix_vuln(properties.vulnerability.sunburst)
                    fix_vuln(properties.vulnerability.imploder)
                    obj.set_properties(properties)


def apply_area_modifications(editor: PatcherEditor, configuration: dict[str, dict]):
    for world_name, world_config in configuration.items():
        world_meta = asset_ids.world.load_dedicated_file(world_name)
        mlvl = editor.get_mlvl(asset_ids.world.NAME_TO_ID_MLVL[world_name])

        areas_by_name: dict[str, AreaWrapper] = {
            get_name_for_area(area): area
            for area in mlvl.areas
        }

        for i, (area_name, area) in enumerate(areas_by_name.items()):
            if area_name not in world_config["areas"]:
                continue
            
            LOG.info(f"[{100*i/len(areas_by_name)}%] Processing {area_name}...")

            area_config = world_config["areas"][area_name]
            low_memory = area_config["low_memory_mode"]

            for dock_name, dock_config in area_config["docks"].items():
                dock_number = world_meta.DOCK_NAMES[area_name][dock_name]

                if "new_door_type" in dock_config:
                    dock_lock_rando.apply_door_rando(
                        editor,
                        world_name,
                        area_name,
                        dock_name,
                        dock_config["new_door_type"],
                        dock_config.get("old_door_type"),
                        low_memory
                    )
                
                if "connect_to" in dock_config:
                    dock_target = dock_config["connect_to"]
                    LOG.debug("Connecting dock %s of %s - %s to %s - %s",
                              dock_name, world_name, area_name, dock_target["area"], dock_target["dock"])
                    area.connect_dock_to(dock_number, areas_by_name[dock_target["area"]],
                                         world_meta.DOCK_NAMES[dock_target["area"]][dock_target["dock"]])

            if area_config["portals_with_any_beams"]:
                _change_portals_to_all_beams(area)

            for layer_name, layer_state in area_config["layers"].items():
                LOG.debug("Setting layer %s of %s - %s to %s", layer_name, world_name, area_name, str(layer_state))
                area.get_layer(layer_name).active = layer_state
        
            area.build_mlvl_dependencies(only_modified=True)


def patch_paks(file_provider: FileProvider, output_path: Path, configuration: dict):
    LOG.info("Will patch files at %s", file_provider)

    editor = PatcherEditor(file_provider, Game.ECHOES)

    LOG.info("Preparing schema")
    schema = dynamic_schema.expand_schema(_read_schema(), editor)

    LOG.info("Validating schema")
    DefaultValidatingDraft7Validator(schema).validate(configuration)

    # custom_assets.create_custom_assets(editor)
    dock_lock_rando.add_custom_models(editor)
    if configuration["auto_enabled_elevators"]:
        auto_enabled_elevator_patches.apply_auto_enabled_elevators_patch(editor)
    specific_area_patches.specific_patches(editor, configuration["area_patches"])
    apply_area_modifications(editor, configuration["worlds"])
    apply_small_randomizations(editor, configuration["small_randomizations"])


    if configuration["inverted"]:
        apply_inverted(editor)

    # Save our changes
    editor.flush_modified_assets()

    editor.save_modifications(output_path)
    LOG.info("Finished.")
