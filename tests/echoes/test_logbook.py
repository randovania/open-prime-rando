from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import ANY

from retro_data_structures.enums.echoes import InventorySlotEnum
from retro_data_structures.formats.tree import Tree
from retro_data_structures.properties.echoes.archetypes import EditorProperties, ScannableParameters
from retro_data_structures.properties.echoes.objects import ScanTreeCategory, ScanTreeInventory, ScanTreeScan

from open_prime_rando.dol_patching.echoes import dol_versions
from open_prime_rando.echoes import logbook
from open_prime_rando.echoes.rando_configuration import RandoConfiguration

if TYPE_CHECKING:
    from open_prime_rando.patcher_editor import PatcherEditor


_EXPECTED_NEW_ENTRIES = [
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
    ScanTreeInventory(
        editor_properties=EditorProperties(name="UnlimitedBeamAmmo"),
        name_string_table=ANY,
        name_string_name="UnlimitedBeamAmmo",
        inventory_slot=InventorySlotEnum(54),
        scannable_parameters=ScannableParameters(scannable_info0=ANY),
    ),
    ScanTreeInventory(
        editor_properties=EditorProperties(name="UnlimitedMissiles"),
        name_string_table=ANY,
        name_string_name="UnlimitedMissiles",
        inventory_slot=InventorySlotEnum(55),
        scannable_parameters=ScannableParameters(scannable_info0=ANY),
    ),
    ScanTreeInventory(
        editor_properties=EditorProperties(name="MassiveDamage"),
        name_string_table=ANY,
        name_string_name="MassiveDamage",
        inventory_slot=InventorySlotEnum(53),
        scannable_parameters=ScannableParameters(scannable_info0=ANY),
    ),
    ScanTreeCategory(
        editor_properties=EditorProperties(name="DarkTempleKeyHints"),
        name_string_table=ANY,
        name_string_name="DarkTempleKeyHints",
    ),
    ScanTreeScan(
        editor_properties=EditorProperties(name="DarkAgonKeyHints"),
        name_string_table=ANY,
        name_string_name="DarkAgonKeyHints",
        scannable_parameters=ScannableParameters(scannable_info0=0xA9B11356),
    ),
    ScanTreeScan(
        editor_properties=EditorProperties(name="DarkTorvusKeyHints"),
        name_string_table=ANY,
        name_string_name="DarkTorvusKeyHints",
        scannable_parameters=ScannableParameters(scannable_info0=0x8C669B58),
    ),
    ScanTreeScan(
        editor_properties=EditorProperties(name="IngHiveKeyHints"),
        name_string_table=ANY,
        name_string_name="IngHiveKeyHints",
        scannable_parameters=ScannableParameters(scannable_info0=0x813068D5),
    ),
]


def test_patch_logbook(prime2_editor: PatcherEditor) -> None:
    prime2_editor.inventory_slot_to_item = []
    logbook.patch_logbook(
        prime2_editor,
        dol_versions.ALL_VERSIONS[0],
        RandoConfiguration(
            game_title="OPR",
            title_screen_text="Foo",
            seed=0,
        ),
    )

    tree = prime2_editor.get_file(0x95B61279, Tree)
    nodes = list(tree.nodes)[-len(_EXPECTED_NEW_ENTRIES) :]
    props = [node.get_properties() for node in nodes]

    assert props == _EXPECTED_NEW_ENTRIES
