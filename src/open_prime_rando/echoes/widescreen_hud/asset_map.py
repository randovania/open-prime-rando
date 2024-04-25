# https://github.com/Nystrata/EchoesWidescreenHUD/wiki#gguisyspak
from retro_data_structures.base_resource import AssetId

WIDESCREEN_ASSETS: dict[str, dict[AssetId, str]] = {
    "ntsc": {
        0xE6F37215: "helmet.FRME",
        0x88738D60: "samushudball.FRME",
        0xEEF43AA1: "samushudcombat.FRME",
        0xF7EC0850: "scanhudflat.FRME"
    },
    "pal": {
        0xE6F37215: "helmet.FRME",
        0x88738D60: "samushudball.FRME",
        0xB5CF0C19: "samushudcombat.FRME",
        0xD9D58FA5: "scanhudflat.FRME"
    }
}
