from retro_data_structures.base_resource import RawResource

from open_prime_rando.echoes.custom_assets import custom_asset_path
from open_prime_rando.echoes.suit_cosmetics.asset_map import SUIT_ASSETS
from open_prime_rando.patcher_editor import PatcherEditor


def apply_custom_suits(editor: PatcherEditor, configuration: dict):
    for suit, assets in SUIT_ASSETS.items():
        skin = configuration[suit]
        if skin == "player1":
            continue
        custom_suit_assets = custom_asset_path().joinpath("suits", skin, suit)
        for asset_id, filename in assets.items():
            asset = custom_suit_assets.joinpath(filename)
            if not asset.exists():
                continue  # some skins leave a few assets vanilla

            res = RawResource(
                type="TXTR",
                data=asset.read_bytes(),
            )
            editor.replace_asset(asset_id, res)
