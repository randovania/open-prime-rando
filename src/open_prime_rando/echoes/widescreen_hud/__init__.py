from retro_data_structures.base_resource import RawResource
from open_prime_rando.echoes.custom_assets import custom_asset_path
from open_prime_rando.echoes.widescreen_hud.asset_map import WIDESCREEN_HUD_ASSETS
from open_prime_rando.patcher_editor import PatcherEditor


def apply_widescreen_hud(editor: PatcherEditor):
    if editor.does_asset_exists(0xEEF43AA1) and editor.does_asset_exists(0xF7EC0850):
        detectedversion = "ntscu"
    elif editor.does_asset_exists(0xB5CF0C19) and editor.does_asset_exists(0xD9D58FA5):
        detectedversion = "pal"
    else:
        raise NotImplementedError()

    for assetversion, assets in WIDESCREEN_HUD_ASSETS.items():
        if detectedversion == assetversion:
            widescreen_assets = custom_asset_path().joinpath("widescreen_hud", detectedversion)
            for asset_id, filename in assets.items():
                asset = widescreen_assets.joinpath(filename)
                if not asset.exists():
                    continue
                res = RawResource(
                    type="FRME",
                    data=asset.read_bytes(),
                )
                editor.replace_asset(asset_id, res)
