import logging
from pathlib import Path

from retro_data_structures.asset_provider import AssetProvider
from retro_data_structures.formats import Mrea
from retro_data_structures.game_check import Game

LOG = logging.getLogger("echoes_patcher")

hive_access_tunnel_id = 0xB1140C24


def patch_paks(paks_path: Path, output_path: Path, configuration: dict):
    LOG.info("Will patch files at %s", paks_path)

    asset_provider = AssetProvider(Game.ECHOES, list(paks_path.glob("*.pak")))
    with asset_provider:
        access_tunnel: Mrea = asset_provider.get_asset(hive_access_tunnel_id)

        docks = {}
        doors = {}

        for script_layer in access_tunnel.script_layers:
            for instance in script_layer.instances:
                try:
                    print("{}: {}".format(instance, instance.name))
                except Exception as e:
                    print("{}: {} --- {}".format(instance, e, instance._raw.instance.base_property))
                    continue

                if instance.type == "DOCK":
                    docks[instance.id] = instance

                if instance.type == "DOOR":
                    doors[instance.id] = instance

        # for door in doors.values():
        #     print(door.name)
            # x = door.get_properties()
            # print(x)
            # break

        Path("lol.txt").write_text(str(access_tunnel))
        # print(access_tunnel)
