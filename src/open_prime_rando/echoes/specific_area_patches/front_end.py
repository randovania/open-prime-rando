from __future__ import annotations

from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.exceptions import UnknownAssetId
from retro_data_structures.formats import Strg
from retro_data_structures.properties.echoes.archetypes import EditorProperties, TextProperties, Transform
from retro_data_structures.properties.echoes.core import Color, Vector
from retro_data_structures.properties.echoes.objects import (
    Relay,
    SequenceTimer,
    SpecialFunction,
    TextPane,
    Timer,
    WorldTeleporter,
)
from retro_data_structures.properties.echoes.objects.SpecialFunction import Function

from open_prime_rando.echoes import frontend_asset_ids

if TYPE_CHECKING:
    from retro_data_structures.formats.mlvl import Mlvl
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.echoes.pydantic_models import AreaReference
    from open_prime_rando.patcher_editor import PatcherEditor


def get_front_end_area(editor: PatcherEditor) -> Area:
    """
    Get the correct FrontEnd Area for this version of the game.
    """
    try:
        return editor.get_area(frontend_asset_ids.FRONTEND_PAL_MLVL, frontend_asset_ids.FRONTEND_PAL_MREA)
    except UnknownAssetId:
        return editor.get_area(frontend_asset_ids.FRONTEND_NTSC_MLVL, frontend_asset_ids.FRONTEND_NTSC_MREA)


def edit_front_end(editor: PatcherEditor, mlvl: Mlvl, area: Area, title_screen_text: str) -> None:
    layer = area.add_layer("Randomizer Instant Unlocks")

    sys_vars_timer = layer.add_instance_with(
        Timer(
            editor_properties=EditorProperties(name="Instant Unlocks Timer"),
            time=0.1,
            auto_reset=False,
            auto_start=True,
        )
    )
    for env_var in ["NormalModeCompleted", "SeenIntroText"]:
        sys_var_func = layer.add_instance_with(
            SpecialFunction(
                editor_properties=EditorProperties(name=f"Unlock {env_var}"),
                function=Function.GameStateSysVar,
                string_parm=env_var,
            )
        )
        sys_vars_timer.add_connection(State.Zero, Message.Increment, sys_var_func)

    # Timeout to next attract movie
    with area.get_instance(0x132).edit_properties(SequenceTimer) as sequence_timer:
        sequence_timer.editor_properties.active = False

    # Remove the Multiplayer entry in the main menu
    area.get_instance("Main").remove_all_connections_to(
        area.get_instance("Multiplayer"),  # The DataNetwork
    )
    area.remove_instance("MultiPlayer")  # The TextPane

    # Remove the Multiplayer entry in the Options menu
    area.get_instance(0x00000201).remove_all_connections_to(  # DataNetwork WhichOptions
        area.get_instance(0x0000020B),  # DataNetwork MultiplayerOptions
    )
    area.remove_instance(0x000001FB)  # TextPane MultiplayerOptions

    # Remove the options entry for activating the Hint System
    area.get_instance(0x00000202).remove_all_connections_to(  # DataNetwork VisorOptions
        area.get_instance(0x000002D5),  # The DataNetwork RHSOption
    )
    area.remove_instance(0x000002D1)  # TextPane RHSOption

    main_menu_strg_id = 0x98E7E268
    main_menu_strg = editor.get_file(main_menu_strg_id, Strg)
    main_menu_strg.append_string(title_screen_text, name="RandomizerString")

    main_menu_text_pane = layer.add_instance_with(
        TextPane(
            editor_properties=EditorProperties(
                name="Randomizer Menu",
                transform=Transform(
                    position=Vector(0.0, -4.0, 8.0),
                    scale=Vector(8.0, 1.0, 1.0),
                ),
                active=False,
            ),
            text_properties=TextProperties(
                text_bounding_width=160,
                text_bounding_height=20,
                foreground_color=Color(1.0, 1.0, 1.0, 1.0),
                outline_color=Color(0.0, 0.0, 0.0, 1.0),
                geometry_color=Color(1.0, 1.0, 1.0, 1.0),
                default_font=0x93E909C1,  # Deface_2
                unknown_0x18dd95cd=1,
                unknown_0x42091548=1,
                wrap_text=False,
            ),
            pivot_offset=Vector(4.0, 0.0, 0.5),
            default_string=main_menu_strg_id,
            default_string_name="RandomizerString",
        )
    )

    # Relay: Back out of Main Menu
    area.get_instance(0x30).add_connection(State.Zero, Message.Deactivate, main_menu_text_pane)
    # Relay: Transition to begin single player game
    area.get_instance(0x3C).add_connection(State.Zero, Message.Deactivate, main_menu_text_pane)
    # Relay: Fade in main menu
    area.get_instance(0x2C).add_connection(State.Zero, Message.Activate, main_menu_text_pane)

    # A timer that when complete, will start the game
    start_game_timer = layer.add_instance_with(
        Timer(
            time=0.03,
            auto_reset=False,
            auto_start=False,
        )
    )
    start_game_timer.add_connection(State.Zero, Message.Action, 0)  # FrontEndScreen

    #
    start_game_relay = layer.add_instance_with(Relay())
    start_game_relay.add_connection(State.Zero, Message.ResetAndStart, start_game_timer)

    # Hijack the existing confirmations from going directly to ingame, to instead firing our relay
    # GuiMenu: Difficulty 3, GuiMenu: Difficulty 1, GuiMenu: Difficulty 2
    for instance_id in (0x245, 0x44D, 0x42C):
        instance = area.get_instance(instance_id)
        instance.remove_all_connections_to(0)
        instance.add_connection(State.PressA, Message.SetToZero, start_game_relay)

    # TODO: starting popup


def edit_starting_area_teleporter(editor: PatcherEditor, mlvl: Mlvl, area: Area, starting_area: AreaReference) -> None:
    elevator = area.get_instance("StartNewSinglePlayerGame")
    with elevator.edit_properties(WorldTeleporter) as teleporter:
        teleporter.world = starting_area.mlvl_id
        teleporter.area = starting_area.mrea_id
