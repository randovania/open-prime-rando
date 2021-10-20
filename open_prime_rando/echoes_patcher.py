import logging
from pathlib import Path

from retro_data_structures.asset_provider import AssetProvider
from retro_data_structures.formats.mrea import Mrea
from retro_data_structures.game_check import Game

from open_prime_rando.echoes.specific_area_patches import specific_patches

LOG = logging.getLogger("echoes_patcher")

hive_access_tunnel_id = 0xB1140C24


def patch_paks(paks_path: Path, output_path: Path, configuration: dict):
    LOG.info("Will patch files at %s", paks_path)

    asset_provider = AssetProvider(Game.ECHOES, list(paks_path.glob("*.pak")))
    specific_patches(asset_provider, output_path)

    with asset_provider:
        access_tunnel: Mrea = asset_provider.get_asset(hive_access_tunnel_id)

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
            types = ["Power", "Dark", "Annihilator", "Bomb", "PowerBomb", "Missile", "PowerCharge", "Entangler", "SonicBoom", "SuperMissle", "BlackHole", "Imploder"]
            for t in types:
                v[t].DamageMultiplier = 0.0
            print(x)
            door.set_properties(x)

        Path("lol.txt").write_text(str(access_tunnel))
        # print(access_tunnel)

        LOG.info("Writing MREA...")
        output_path.joinpath("0a_temple_hall.MREA").write_bytes(access_tunnel.build())
        LOG.info("Finished.")
