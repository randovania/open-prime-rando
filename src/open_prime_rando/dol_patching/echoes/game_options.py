from enum import Enum
from typing import Annotated

import pydantic
from annotated_types import Interval
from ppc_asm.assembler.ppc import addi, li, nop, or_, r0, r1, r3, r31, stb, stw
from ppc_asm.dol_file import DolEditor


class SoundMode(Enum):
    MONO = 0
    STEREO = 1
    SURROUND = 2


type ScreenOffset = Annotated[int, Interval(ge=-0x1E, le=0x1F)]
type Volume = Annotated[int, Interval(ge=0x00, le=0x69)]
type Alpha = Annotated[int, Interval(ge=0x00, le=0xFF)]


class GameOptionsDefaults(pydantic.BaseModel):
    """"""

    sound_mode: SoundMode = SoundMode.STEREO
    screen_brightness: Annotated[int, Interval(ge=0, le=8)] = 4
    screen_x_offset: ScreenOffset = 0
    screen_y_offset: ScreenOffset = 0
    screen_stretch: Annotated[int, Interval(ge=-10, le=10)] = 0
    sfx_volume: Volume = 0x69
    music_volume: Volume = 0x4F
    hud_alpha: Alpha = 0xFF
    helmet_alpha: Alpha = 0xFF
    hud_lag: bool = True
    invert_y_axis: bool = False
    rumble: bool = True
    hint_system: bool = False


_PREFERENCES_ORDER = (
    "sound_mode",
    "screen_brightness",
    "screen_x_offset",
    "screen_y_offset",
    "screen_stretch",
    "sfx_volume",
    "music_volume",
    "hud_alpha",
    "helmet_alpha",
)

_FLAGS_ORDER = (
    "hud_lag",
    "invert_y_axis",
    "rumble",
    None,  # crashes, maybe swapBeamsControls
    "hint_system",
    None,  # 5: doesn't crash, unknown
    None,  # 6: doesn't crash, unknown
    None,  # 7: doesn't crash, unknown
)


def apply_patch(
    game_options_constructor_offset: int,
    dol_editor: DolEditor,
    game_options_defaults: GameOptionsDefaults,
) -> None:
    """
    Patches the CGameOptions constructor to use a different set of default values.

    With this, the user can set their options before even opening the game.
    """
    patch = [
        # Unknown purpose, but keep for safety
        stw(r31, 0x1C, r1),
        or_(r31, r3, r3),
        # For a later function call we don't touch
        addi(r3, r1, 0x8),
    ]

    for i, preference_name in enumerate(_PREFERENCES_ORDER):
        value = getattr(game_options_defaults, preference_name)
        if isinstance(value, Enum):
            value = value.value
        patch.extend(
            [
                li(r0, value),
                stw(r0, (0x04 * i), r31),
            ]
        )

    flag_values = [
        getattr(game_options_defaults, flag_name) if flag_name is not None else False for flag_name in _FLAGS_ORDER
    ]
    bit_mask = int("".join(str(int(flag)) for flag in flag_values), 2)
    patch.extend(
        [
            li(r0, bit_mask),
            stb(r0, 0x04 * len(_PREFERENCES_ORDER), r31),
            li(r0, 0),
            stw(r0, 0x2C, r31),
            stw(r0, 0x30, r31),
            stw(r0, 0x34, r31),
        ]
    )

    instructions_space = 34
    instructions_to_fill = instructions_space - len(patch)

    if instructions_to_fill < 0:
        raise RuntimeError(f"Our patch ({len(patch)}) is bigger than the space we have ({instructions_space}).")

    for i in range(instructions_to_fill):
        patch.append(nop())
    dol_editor.write_instructions(game_options_constructor_offset + 8 * 4, patch)
