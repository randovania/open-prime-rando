from typing import Annotated

from annotated_types import Interval
from open_prime_rando_practice_mod import PracticeModMode
from pydantic import BaseModel

AssetId = Annotated[int, Interval(ge=0, le=0xFFFFFFFF)]


class AreaReference(BaseModel):
    mlvl_id: AssetId
    mrea_id: AssetId


class RandoConfiguration(BaseModel):
    """
    Configuration for randomizing Metroid Prime 2: Echoes.
    """

    starting_area: AreaReference | None = None
    """The game will start at the given area. When not set, starts at Landing Site."""

    practice_mod: PracticeModMode = PracticeModMode.disabled
    """How accessible is the Practice Mod."""
