from enum import Enum
from typing import Annotated

from annotated_types import Interval
from pydantic import BaseModel

AssetId = Annotated[int, Interval(ge=0, le=0xFFFFFFFF)]


class AreaReference(BaseModel):
    mlvl_id: AssetId
    mrea_id: AssetId


class PracticeModMode(str, Enum):
    disabled = "disabled"
    full = "full"


class RandoConfiguration(BaseModel):
    """
    Configuration for randomizing Metroid Prime 2: Echoes.
    """

    starting_area: AreaReference | None = None
    """The game will start at the given area. When not set, starts at Landing Site."""

    practice_mod: PracticeModMode = PracticeModMode.disabled
    """How accessible is the Practice Mod."""
