import logging
from pathlib import Path

from retro_data_structures.asset_manager import FileProvider

from open_prime_rando.echoes import custom_assets
from open_prime_rando.echoes.asset_ids.temple_grounds import HIVE_ACCESS_TUNNEL_MREA
from open_prime_rando.echoes.specific_area_patches import specific_patches
from open_prime_rando.patcher_editor import PatcherEditor

LOG = logging.getLogger("echoes_patcher")


def patch_paks(file_provider: FileProvider, output_path: Path, configuration: dict):
    LOG.info("Will patch files at %s", file_provider)

    editor = PatcherEditor(file_provider)

    custom_assets.create_custom_assets(editor)
    specific_patches(editor)
    access_tunnel = editor.get_mrea(HIVE_ACCESS_TUNNEL_MREA)

    docks = {}
    doors = {}

    for script_layer in access_tunnel.script_layers:
        for instance in script_layer.instances:
            try:
                print("{}: {}".format(instance, instance.name))
                # print(instance.get_properties())
            except Exception as e:
                print("{}: {} --- {}".format(instance, e, instance._raw.instance.base_property.hex()))
                continue

            if instance.type == "DOCK":
                docks[instance.id] = instance

            if instance.type == "DOOR":
                doors[instance.id] = instance

    for door in doors.values():
        print(door.name)
        x = door.get_properties()
        print(x)
        x.ShellColor.R = 1.0
        v = x.Vulnerability
        types = ["Power", "Dark", "Annihilator", "Bomb", "PowerBomb", "Missile", "PowerCharge", "Entangler",
                 "SonicBoom", "SuperMissle", "BlackHole", "Imploder"]
        for t in types:
            v[t].DamageMultiplier = 0.0
        print(x)
        door.set_properties(x)

    Path("lol.txt").write_text(str(access_tunnel))
    # print(access_tunnel)

    LOG.info("Writing MREA...")
    output_path.joinpath("0a_temple_hall.MREA").write_bytes(access_tunnel.build())
    LOG.info("Finished.")
