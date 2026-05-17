from __future__ import annotations

import enum
import typing

import pydantic
from retro_data_structures.base_resource import RawResource

from open_prime_rando.echoes.custom_assets import custom_asset_path
from open_prime_rando.echoes.suit_cosmetics.asset_map import SUIT_ASSETS

if typing.TYPE_CHECKING:
    from pathlib import Path

    from open_prime_rando.patcher_editor import PatcherEditor

SuitKind = typing.Literal["varia", "dark", "light"]
_SUIT_LIST = ("varia", "dark", "light")


class SuitSkin(enum.Enum):
    """Which custom skin should be used for suit. Player_1 represents unchanged."""

    PLAYER_1 = "player1"
    PLAYER_2 = "player2"
    PLAYER_3 = "player3"
    PLAYER_4 = "player4"

    def get_asset_path(self, suit: SuitKind) -> Path:
        """Gets the folder where the assets for the given suit with this skin.."""
        return custom_asset_path().joinpath("suits", self.value, suit)


class SuitMapping(pydantic.BaseModel):
    """Determines which custom skin should be used for each of the three suits."""

    varia: SuitSkin = SuitSkin.PLAYER_1
    dark: SuitSkin = SuitSkin.PLAYER_1
    light: SuitSkin = SuitSkin.PLAYER_1

    def get_skin(self, suit: SuitKind) -> SuitSkin:
        """Gets the configured skin for the given suit."""
        match suit:
            case "varia":
                return self.varia
            case "dark":
                return self.dark
            case "light":
                return self.light


def apply_custom_suits(editor: PatcherEditor, mapping: SuitMapping) -> None:
    """
    Replaces the Suit assets with custom ones based on the given mapping.
    """
    for suit in _SUIT_LIST:
        skin = mapping.get_skin(suit)
        if skin == SuitSkin.PLAYER_1:
            continue

        custom_suit_assets = skin.get_asset_path(suit)
        for asset_id, filename in SUIT_ASSETS[suit].items():
            asset = custom_suit_assets.joinpath(filename)
            if not asset.exists():
                continue  # some skins leave a few assets vanilla

            res = RawResource(
                type="TXTR",
                data=asset.read_bytes(),
            )
            editor.replace_asset(asset_id, res)
