from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import ANY

from retro_data_structures.enums.echoes import InventorySlotEnum
from retro_data_structures.formats.tree import Tree
from retro_data_structures.properties.echoes.archetypes import EditorProperties, ScannableParameters
from retro_data_structures.properties.echoes.objects import ScanTreeCategory, ScanTreeInventory

from open_prime_rando.dol_patching.echoes import dol_versions
from open_prime_rando.echoes import logbook

if TYPE_CHECKING:
    from open_prime_rando.patcher_editor import PatcherEditor


def test_patch_logbook(prime2_editor: PatcherEditor) -> None:
    logbook.patch_logbook(prime2_editor, dol_versions.ALL_VERSIONS[0])

    tree = prime2_editor.get_file(0x95B61279, Tree)
    nodes = list(tree.nodes)[-5:]
    props = [node.get_properties() for node in nodes]

    assert props == [
        ScanTreeCategory(
            editor_properties=EditorProperties(name="Translators"),
            name_string_table=ANY,
            name_string_name="Translators",
        ),
        ScanTreeInventory(
            editor_properties=EditorProperties(name="VioletTranslator"),
            name_string_table=ANY,
            name_string_name="VioletTranslator",
            inventory_slot=InventorySlotEnum.DarkBomb,
            scannable_parameters=ScannableParameters(scannable_info0=ANY),
        ),
        ScanTreeInventory(
            editor_properties=EditorProperties(name="AmberTranslator"),
            name_string_table=ANY,
            name_string_name="AmberTranslator",
            inventory_slot=InventorySlotEnum.LightBomb,
            scannable_parameters=ScannableParameters(scannable_info0=ANY),
        ),
        ScanTreeInventory(
            editor_properties=EditorProperties(name="EmeraldTranslator"),
            name_string_table=ANY,
            name_string_name="EmeraldTranslator",
            inventory_slot=InventorySlotEnum.AnnihilatorBomb,
            scannable_parameters=ScannableParameters(scannable_info0=ANY),
        ),
        ScanTreeInventory(
            editor_properties=EditorProperties(name="CobaltTranslator"),
            name_string_table=ANY,
            name_string_name="CobaltTranslator",
            inventory_slot=InventorySlotEnum.BeamCombo,
            scannable_parameters=ScannableParameters(scannable_info0=ANY),
        ),
    ]
