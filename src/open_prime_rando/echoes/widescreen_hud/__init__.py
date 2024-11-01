from retro_data_structures.base_resource import RawResource

from open_prime_rando.echoes.custom_assets import custom_asset_path
from open_prime_rando.echoes.widescreen_hud.asset_map import WIDESCREEN_HUD_ASSETS
from open_prime_rando.patcher_editor import PatcherEditor


def apply_widescreen_hud(editor: PatcherEditor):
    """
    Replaces certain FRME files to adjust HUD/Visor widgets to better fit a 16:9 screen aspect ratio
    """
    for asset_id, filename in WIDESCREEN_HUD_ASSETS.items():
        widescreen_assets = custom_asset_path().joinpath("widescreen_hud")
        asset = widescreen_assets.joinpath(filename)
        if not editor.does_asset_exists(asset_id):
            continue
        res = RawResource(type="FRME", data=asset.read_bytes())
        editor.replace_asset(asset_id, res)
