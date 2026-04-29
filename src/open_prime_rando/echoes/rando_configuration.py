from typing import Annotated

from annotated_types import Interval
from open_prime_rando_practice_mod import PracticeModMode
from pydantic import BaseModel, StringConstraints

AssetId = Annotated[int, Interval(ge=0, le=0xFFFFFFFF)]


class AreaReference(BaseModel):
    mlvl_id: AssetId
    mrea_id: AssetId


class AreaChange(BaseModel):
    """Contains changes for a given MREA."""

    mrea_id: AssetId
    """The asset id of the MREA for this change."""


class WorldChange(BaseModel):
    """Contains changes for a given MLVL."""

    mlvl_id: AssetId
    """The asset id of the MLVL for this change."""

    area_changes: list[AreaChange]
    """The changes to apply to a MREA that belongs to this MLVL."""


class RandoConfiguration(BaseModel):
    """
    Configuration for randomizing Metroid Prime 2: Echoes.
    """

    game_title: Annotated[str, StringConstraints(max_length=64)]
    """The new title of the game, listed in the ISO/Banner."""

    title_screen_text: str
    """Text to be displayed in the title screen."""

    starting_area: AreaReference | None = None
    """The game will start at the given area. When not set, starts at Landing Site."""

    practice_mod: PracticeModMode = PracticeModMode.disabled
    """How accessible is the Practice Mod."""

    world_changes: list[WorldChange]
    """"""
