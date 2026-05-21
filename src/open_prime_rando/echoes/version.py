from __future__ import annotations

from enum import Enum


class EchoesVersion(float, Enum):
    NTSC_U = 1.028
    PAL = 1.035
    NTSC_J = 1.036
    NEW_PLAY_CONTROL = 3.561
    TRILOGY_NTSC = 3.593
    TRILOGY_PAL = 3.629
