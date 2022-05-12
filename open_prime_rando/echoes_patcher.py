import logging
from pathlib import Path

from retro_data_structures.file_tree_editor import PathFileProvider
from retro_data_structures.formats import Mrea

from open_prime_rando.echoes.asset_ids.great_temple import MAIN_ENERGY_CONTROLLER_MREA
from open_prime_rando.patcher_editor import PatcherEditor

LOG = logging.getLogger("echoes_patcher")


def patch_doors_in_area(area: Mrea):
    doors = {}

    for script_layer in area.script_layers:
        for instance in script_layer.instances:
            if instance.type == "DOOR":
                doors[instance.id] = instance

    dock_number_to_door = {}

    for instance_id, door in doors.items():
        for connection in door.connections:
            if (connection.state, connection.message) == ("OPEN", "INCR"):
                connected_dock = area.get_instance(connection.target)
                dock_number_to_door[connected_dock.get_properties().DockNumber] = door

    for dock_number, door in dock_number_to_door.items():
        x = door.get_properties()
        x.ShellColor.R = 1.0
        v = x.Vulnerability

        # TODO: scan text

        types = ["Power", "Dark", "Annihilator", "Bomb", "PowerBomb", "Missile", "PowerCharge", "Entangler",
                 "SonicBoom", "SuperMissle", "BlackHole", "Imploder"]
        for t in types:
            v[t].DamageMultiplier = 0.0
            v[t].Effect = 1  # Reflect
        for t in ["Light", "LightBlast", "Sunburst"]:
            v[t].DamageMultiplier = 100.0
            v[t].Effect = 0  # Normal
        door.set_properties(x)


def patch_paks(paks_path: Path, output_path: Path, configuration: dict):
    LOG.info("Will patch files at %s", paks_path)

    editor = PatcherEditor(PathFileProvider(paks_path))
    # specific_patches(editor)
    patch_doors_in_area(editor.get_mrea(MAIN_ENERGY_CONTROLLER_MREA))

    LOG.info("Writing changes...")
    output_path.mkdir(parents=True, exist_ok=True)
    editor.flush_modified_assets()
    editor.save_modifications(output_path)
    LOG.info("Finished.")
