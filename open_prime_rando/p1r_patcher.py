import collections
import itertools
import json
import logging
import pprint
import uuid
from pathlib import Path

from open_prime_rando.patcher_editor import PatcherEditor
from open_prime_rando.prime_remastered.string_editor import StringEditor
from open_prime_rando.validator_with_default import DefaultValidatingDraft7Validator
from retro_data_structures.asset_manager import FileProvider
from retro_data_structures.formats import Room
from retro_data_structures.game_check import Game
from retro_data_structures.properties.prime_remastered.archetypes.AnimSetMP1 import AnimSetMP1
from retro_data_structures.properties.prime_remastered.core.PooledString import PooledString
from retro_data_structures.properties.prime_remastered.objects import WorldTeleporterTooMP1, PickupMP1, HUDMemoMP1
import retro_data_structures.enums.prime_remastered

LOG = logging.getLogger("p1r_patcher")

end_cinema = uuid.UUID('ce44a797-c442-4128-8372-694626a83722')

all_rooms_with_teleporters = [
    uuid.UUID("6929c583-d47a-407c-8014-586c7769395c"),  # 00_crater_over_elev_J
    uuid.UUID("a103fb3c-0be0-428b-83c6-c69fa31b883f"),  # 03f_Crater
    uuid.UUID("b035c80a-afbf-4ed5-b5e9-592c5a7c0ff6"),  # 00_ice_elev_lava_C
    uuid.UUID("1686a3ef-f84d-4195-a989-cee3078817a5"),  # 00_ice_elev_lava_D
    # uuid.UUID("a8444ff6-e4a4-4183-bfec-73d6d6407fa5"),  # 01_intro_hanger
    uuid.UUID("38a2b289-d65e-4c05-a8f9-82ecb8e5e511"),  # 00_lava_elev_ice_C
    uuid.UUID("ac0cf9d6-744f-4a6b-a90a-070c002462a1"),  # 00_Lava_Elev_Ice_D
    uuid.UUID("eb1b3a53-e103-4047-90dc-00dcb753f34d"),  # 00_lava_elev_over_L
    uuid.UUID("c6075efb-d0e2-46af-956b-cb7c1e2d28c8"),  # 00_Lava_elev_Ruins_B
    uuid.UUID("617c984a-7a0e-4816-abfe-f2a0798ade61"),  # 00_Lava_Mines_Elev_H
    uuid.UUID("47e79ddd-b62f-455f-9d0d-56a69f2a8555"),  # 00_mines_lava_elev_H
    uuid.UUID("27dd7619-bf41-487d-9086-de942c66d632"),  # 00_Mine_lava_elev_G
    uuid.UUID("fa869fe6-c689-4461-bea7-7d87364abb10"),  # 00_over_elev_lava_L
    uuid.UUID("54be5fd1-916a-4523-82a6-72d335c868a5"),  # 00_over_elev_mines_G
    uuid.UUID("863591c2-2ebb-47d5-9650-c033f715ddf2"),  # 00_over_elev_ruins_A
    uuid.UUID("8e47d4ba-2c40-4389-804a-8b041dae8062"),  # 00_over_elev_ruins_E
    uuid.UUID("e3f5266d-4404-41bc-8281-05e002c86925"),  # 00_over_elev_ruins_F
    uuid.UUID("5722350a-e985-4ae3-b96b-36322622b93f"),  # 07_Over_Stonehenge
    uuid.UUID("fb28a118-3189-4b24-b212-b93369c45ec7"),  # 0_Elev_Lava_B
    uuid.UUID("92f21343-0369-42d3-90ca-98396710725e"),  # 0_Elev_Over_A
    uuid.UUID("8de242c2-a4d0-44b0-9d48-0b5b35f1c982"),  # 0_Elev_Over_E
    uuid.UUID("2d6fcf34-f7ba-4383-a0df-660fe25b1c6d"),  # 0_Elev_Over_F
]

rooms_with_pickups = [
    uuid.UUID('d674e2b2-fb22-49d5-a6bd-50d31cfde414'),  # Alcove - 01_over_pickup_spacejump
    uuid.UUID('65f989f3-1dd2-4cec-b379-75244367ee33'),  # Plasma Processing - 13_Lava_Pickup
]


def _read_schema():
    with Path(__file__).parent.joinpath("prime_remastered", "schema.json").open() as f:
        return json.load(f)


def patch_paks(file_provider: FileProvider, output_path: Path, configuration: dict):
    LOG.info("Will patch files at %s", file_provider)
    editor = PatcherEditor(file_provider, Game.PRIME_REMASTER)

    LOG.info("Validating schema")
    DefaultValidatingDraft7Validator(_read_schema()).validate(configuration)

    string_editor = StringEditor(editor)

    results = collections.defaultdict(list)

    name_for_ids = {
        asset_id: list(editor.find_paks(asset_id))[0].split("/")[-1].split(".")[0]
        for asset_id in editor.all_asset_ids()
        if editor.get_asset_type(asset_id) == "ROOM"
    }

    # for asset_id in rooms_with_pickups:
    #     room = editor.get_file(asset_id, Room)
    #     for pickup in room.properties_of_type(PickupMP1):
    #         print(room.get_pooled_string(pickup.animation_parameters.str1))
    #         print(room.get_pooled_string(pickup.animation_parameters.str2))

    for asset_id in [rooms_with_pickups[0]]:
        # Space Jump
        room = editor.get_file(asset_id, Room)
        for memo in room.properties_of_type(HUDMemoMP1):
            print(memo)
            # memo.memo_type = retro_data_structures.enums.prime_remastered.MemoType.StatusMessage
            break
            # for i in itertools.count():
            #     s = string_editor.get_string(memo.guid_1, i)
            #     if s is None:
            #         break
            #     print(s)
            #     print(repr(s))

        for pickup in room.properties_of_type(PickupMP1):
            pickup.item = retro_data_structures.enums.prime_remastered.PlayerItem.PlasmaBeam
            # pickup.animation_parameters = AnimSetMP1(
            #     id=uuid.UUID('10000000-0000-f000-f000-00006397cc1b'),
            #     str1=PooledString(-1, b'Node1'),
            #     str2=PooledString(-1, b'PlasmaBeam_ready'),
            # )
            # pickup.actor_info.unk_bool_4 = True
            pickup.actor_info.scannable.scan_file = uuid.UUID('10000000-0000-f000-f000-0000f576ec35')
            # pickup.actor_info.unk_bool_6 = False
            # pickup.unk_bool_1 = False

    #
    # for asset_id in all_rooms_with_teleporters:
    #     room = editor.get_file(asset_id, Room)
    #     for teleporter in room.properties_of_type(WorldTeleporterTooMP1):
    #         teleporter.world = end_cinema
    #         teleporter.area = end_cinema
            # results[asset_id].append((teleporter.world, teleporter.area))

    # for room, destinations in results.items():
    #     print(f"> From {name_for_ids[room]}")
    #     for dest in destinations:
    #         print(dest)
    #         print(name_for_ids[dest[0]], name_for_ids[dest[1]])

    # Save our changes
    editor.flush_modified_assets()

    editor.save_modifications(output_path)
    LOG.info("Finished.")
