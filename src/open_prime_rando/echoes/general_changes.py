from __future__ import annotations

from typing import TYPE_CHECKING

from retro_data_structures.formats.strg import Strg
from retro_data_structures.properties.echoes.objects import Camera
from retro_data_structures.properties.echoes.objects.Camera import FlagsCinematicCamera

if TYPE_CHECKING:
    from retro_data_structures.formats.mlvl import Mlvl
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.patcher_editor import PatcherEditor


def apply_corrupted_memory_card_change(editor: PatcherEditor):
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
