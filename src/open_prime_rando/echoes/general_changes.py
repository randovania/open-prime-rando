from __future__ import annotations

import typing
from typing import TYPE_CHECKING, Final

from retro_data_structures.enums.echoes import Message, PlayerItemEnum, State
from retro_data_structures.formats.mapa import AreaVisibility, Mapa, ObjectTypeMP2, ObjectVisibility
from retro_data_structures.formats.strg import Strg
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.objects import Camera, ConditionalRelay, Timer
from retro_data_structures.properties.echoes.objects.Camera import FlagsCinematicCamera

from open_prime_rando.echoes.asset_ids import agon_wastes, great_temple, sanctuary_fortress, torvus_bog

if TYPE_CHECKING:
    from retro_data_structures.formats.mlvl import Mlvl
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.echoes.rando_configuration import MapVisibility
    from open_prime_rando.patcher_editor import PatcherEditor


def apply_corrupted_memory_card_change(editor: PatcherEditor) -> None:
    # STRG_MemoryCard_0
    table = editor.get_file(0x88E242D6, Strg)

    table.set_single_string(
        table.raw.name_table["CorruptedFile"],
        """The save file was created using a different
Randomizer ISO and must be deleted.""",
    )
    table.set_single_string(table.raw.name_table["ChoiceDeleteCorruptedFile"], "Delete Incompatible File")


def allow_skippable_cutscenes(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Edits all Camera objects that can be skipped to not require being watched first.
    """
    for instance in area.all_instances:
        if instance.script_type == Camera:
            prop = instance.get_properties_as(Camera)
            if prop.flags_cinematic_camera & FlagsCinematicCamera.CinematicSkip:
                prop.flags_cinematic_camera |= FlagsCinematicCamera.IgnoreWatchedCheck
                instance.set_properties(prop)


_TEMPLE_KEY_ITEMS: Final = {
    PlayerItemEnum.DarkAgonKey1,
    PlayerItemEnum.DarkAgonKey2,
    PlayerItemEnum.DarkAgonKey3,
    PlayerItemEnum.DarkTorvusKey1,
    PlayerItemEnum.DarkTorvusKey2,
    PlayerItemEnum.DarkTorvusKey3,
    PlayerItemEnum.IngHiveKey1,
    PlayerItemEnum.IngHiveKey2,
    PlayerItemEnum.IngHiveKey3,
    PlayerItemEnum.SkyTempleKey1,
    PlayerItemEnum.SkyTempleKey2,
    PlayerItemEnum.SkyTempleKey3,
    PlayerItemEnum.SkyTempleKey4,
    PlayerItemEnum.SkyTempleKey5,
    PlayerItemEnum.SkyTempleKey6,
    PlayerItemEnum.SkyTempleKey7,
    PlayerItemEnum.SkyTempleKey8,
    PlayerItemEnum.SkyTempleKey9,
}


def loop_conditional_relays(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Add looping timers to repeatedly trigger ConditionalRelays that are checking for specific items.
    This allows changes to happen instantly if other pickups are collected, or in multiworld.
    """

    for instance in area.all_instances:
        if instance.script_type != ConditionalRelay:
            continue

        conditional_relay = instance

        prop = conditional_relay.get_properties_as(ConditionalRelay)
        if not (prop.trigger_on_first_think or prop.editor_properties.name == "If player has Light Suit"):
            # we want the ones that trigger immediately. light suit checks are weird -
            # they have a timer that triggers after 0.1s. searching incoming connections is slow,
            # but conveniently these all have the same name so we can use it instead
            continue

        if prop.conditional1.player_item in _TEMPLE_KEY_ITEMS:
            # these conditional relays are more complicated and shouldn't just be looped carelessly
            continue

        layer = area.get_layer("Default")
        timer = layer.add_instance_with(
            Timer(
                editor_properties=EditorProperties(name="Looping pickup check"),
                time=0.01,
                auto_reset=True,
                auto_start=True,
            )
        )
        timer.add_connection(State.Zero, Message.SetToZero, conditional_relay)
        conditional_relay.add_connection(
            State.Open, Message.Deactivate, timer
        )  # prevents activating the relay multiple times


# Keep the energy controllers always visible on the map so we're always able to warp to that region.
_AREAS_THAT_ALWAYS_VISIBLE = {
    agon_wastes.AGON_ENERGY_CONTROLLER_MREA,
    torvus_bog.TORVUS_ENERGY_CONTROLLER_MREA,
    sanctuary_fortress.SANCTUARY_ENERGY_CONTROLLER_MREA,
    great_temple.MAIN_ENERGY_CONTROLLER_MREA,
}


def change_map_visibility(editor: PatcherEditor, mlvl: Mlvl, area: Area, map_visibility: MapVisibility) -> None:
    """
    Changes the visibility mode of the map for the given area to be always visible or require a visit.
    """

    mapa = typing.cast("Mapa[ObjectTypeMP2]", area.mapa)
    if mapa.visibility_mode == AreaVisibility.Never:
        return

    always_visible = area.mrea_asset_id in _AREAS_THAT_ALWAYS_VISIBLE
    never_visible = area.mrea_asset_id in map_visibility.areas_to_never_reveal

    objects_to_reveal = {
        ObjectTypeMP2.Elevator,
        ObjectTypeMP2.SaveStation,
        ObjectTypeMP2.Portal,
        ObjectTypeMP2.LightTeleporter,
        ObjectTypeMP2.TranslatorGate,
        ObjectTypeMP2.UpArrow,
        ObjectTypeMP2.DownArrow,
    }

    if (always_visible or map_visibility.reveal_map_at_start) and not never_visible:
        mapa.visibility_mode = AreaVisibility.Always
        if map_visibility.unvisited_map_icons:
            for mappable in mapa.mappable_objects:
                if mappable.object_type in objects_to_reveal:
                    mappable.visibility_mode = ObjectVisibility.AreaVisitOrMapStation

    else:
        area.mapa.visibility_mode = AreaVisibility.VisitOrMapStation


def change_area_name(editor: PatcherEditor, mlvl: Mlvl, area: Area, name: str) -> None:
    """
    Changes the name of an Area.
    """
    # duplicate the STRG in case it was used elsewhere and breaks things
    area.name_strg_id = editor.duplicate_asset(area._raw.area_name_id, f"custom_name_for_{area.internal_name}.STRG")

    area.name = name
