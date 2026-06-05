from __future__ import annotations

import colorsys
import dataclasses
import typing

import pydantic
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.echoes.core import Color
from retro_data_structures.properties.echoes.objects import TweakGuiColors

from open_prime_rando.echoes.pydantic_models import PydanticColor

if typing.TYPE_CHECKING:
    from collections.abc import Callable

    from retro_data_structures.properties.field_reflection import FieldReflection

    from open_prime_rando.patcher_editor import PatcherEditor


def _frozen_color(color: Color) -> tuple[float, float, float, float]:
    """Turns a Color into a tuple so it's hashable"""
    return (color.r, color.g, color.b, color.a)


def _to_hsv(color: Color) -> tuple[float, float, float]:
    """Converts a Color to an HSV tuple"""
    return colorsys.rgb_to_hsv(*_frozen_color(color)[:3])


def _from_hsv(color: tuple[float, float, float], alpha: float = 1.0) -> Color:
    """Converts an HSV tuple to a Color"""
    rgb = colorsys.hsv_to_rgb(*color)
    return Color(*rgb, alpha)


def _new_color(
    main: tuple[float, float, float], other: tuple[float, float, float], change: Callable[[float, float], float]
) -> tuple[float, float, float]:
    """Applies a change to a color based on another. This shouldn't be necessary but ty doesn't like zip() i guess"""
    result = tuple(change(main_c, other_c) for main_c, other_c in zip(main, other, strict=True))
    return typing.cast("tuple[float, float, float]", result)


def _adjust_color(old_other: Color, old_main: Color, new_main: Color) -> Color:
    """
    Generates a new Color, relative to the main color.
    Uses the ratio between the old color and the old main color to
    produce a color that is different from the new main color in the same way.
    """
    main_hsv = _to_hsv(old_main)
    other_hsv = _to_hsv(old_other)

    ratio = _new_color(main_hsv, other_hsv, lambda main, other: other / main)

    new_main_hsv = _to_hsv(new_main)
    new_other = _new_color(new_main_hsv, ratio, lambda main, other: max(0.0, min(1.0, main * other)))

    return _from_hsv(new_other, old_other.a)


def _update_colors(
    tweak: BaseProperty,
    color_mapping: dict[tuple[float, float, float, float], Color],
    excluded_properties: set[int],
) -> None:
    """
    Recursively iterates the fields in the tweak, changing colors
    according to the color mapping as it comes across them.
    Can optionally provide a set of property IDs to never change.
    """
    for tweak_field in dataclasses.fields(tweak):
        if "reflection" not in tweak_field.metadata:
            continue

        reflection: FieldReflection = tweak_field.metadata["reflection"]

        if reflection.id in excluded_properties:
            continue

        if reflection.type == Color:
            field_color: Color = getattr(tweak, tweak_field.name)

            for old_color, new_color in color_mapping.items():
                if _frozen_color(field_color) == old_color:
                    setattr(tweak, tweak_field.name, new_color)
                    break

        elif issubclass(reflection.type, BaseProperty):
            _update_colors(
                getattr(tweak, tweak_field.name),
                color_mapping,
                excluded_properties,
            )


class HudColorConfiguration(pydantic.BaseModel):
    main_color: PydanticColor = (0.5372549891471863, 0.8392159938812256, 1.0)
    """
    The primary color of the HUD's color scheme. Various HUD elements use slightly
    darker versions of this color - those colors get generated automatically based
    on this color.
    """

    change_text_color: bool = True
    """Whether to change the color of text in HUD memos."""

    change_beam_visor_select_color: bool = True
    """Whether to change the color of the beam and visor selection icons."""


def edit_hud_color(editor: PatcherEditor, color_config: HudColorConfiguration) -> None:
    """
    Edits TweakGuiColors to change the HUD colors according to the configuration.
    """

    main_color = Color(*color_config.main_color, 1.0)
    with editor.edit_tweak(TweakGuiColors) as tweak:
        old_main_color = tweak.combat_hud_color_scheme.hud_hue

        excluded_properties: set[int] = set()
        colors_to_change: list[Color] = [
            old_main_color,
            tweak.ball_hud.energy_bar_filled_color,
            tweak.ball_hud.energy_bar_shadow_color,
            tweak.misc.energy_bar_low_empty_color,
        ]

        if not color_config.change_text_color:
            excluded_properties.add(0x2DF1EB03)  # hud_memo_text_foreground_color
        else:
            colors_to_change.extend(
                [
                    tweak.misc.hud_memo_text_outline_color,
                ]
            )

        if color_config.change_beam_visor_select_color:
            colors_to_change.extend(
                [
                    tweak.misc.unknown_0x59e416aa,
                    tweak.misc.selected_visor_beam_color,
                    tweak.misc.unselected_visor_beam_color,
                ]
            )

        color_map = {
            _frozen_color(color): _adjust_color(color, old_main_color, main_color) for color in colors_to_change
        }

        _update_colors(tweak, color_map, excluded_properties)
