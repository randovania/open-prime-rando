# https://github.com/Nystrata/EchoesWidescreenHUD/wiki#gguisyspak
from retro_data_structures.base_resource import AssetId

WIDESCREEN_HUD_ASSETS: dict[str, dict[AssetId, str]] = {
    "ntscu": {
        0xE6F37215: "FRME_Helmet.FRME",
        0x88738D60: "FRME_SamusHud1Ball.FRME",
        0xEEF43AA1: "FRME_SamusHud1Combat.FRME",
        0xF7EC0850: "FRME_ScanHudFlat_0.FRME"
    },
    "pal": {
        0xE6F37215: "FRME_Helmet.FRME",
        0x88738D60: "FRME_SamusHud1Ball.FRME",
        0xB5CF0C19: "FRME_SamusHud1Combat_0.FRME",
        0xD9D58FA5: "FRME_ScanHudFlat_1.FRME"
    }
}
