from __future__ import annotations

import dataclasses
import typing

from retro_data_structures.base_resource import NameOrAssetId
from retro_data_structures.enums.echoes import InventorySlotEnum, PlayerItemEnum
from retro_data_structures.formats import Strg
from retro_data_structures.formats.hier import HierEntry
from retro_data_structures.properties.echoes.archetypes import EditorProperties, ScannableParameters
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.echoes.objects import (
    ScanTreeCategory,
    ScanTreeInventory,
    ScanTreeMenu,
    ScanTreeScan,
    ScanTreeSlider,
)

from open_prime_rando.dol_patching.echoes.dol_patches import EchoesDolVersion
from open_prime_rando.echoes.pickups import model_database
from open_prime_rando.patcher_editor import PatcherEditor

if typing.TYPE_CHECKING:
    from retro_data_structures.formats.script_object import ScriptInstance
    from retro_data_structures.formats.tree import Tree

    from open_prime_rando.dol_patching.echoes.dol_patches import EchoesDolVersion
    from open_prime_rando.patcher_editor import PatcherEditor


type ScanTreeInstance = ScanTreeCategory | ScanTreeInventory | ScanTreeScan | ScanTreeMenu | ScanTreeSlider


class HierarchySharedProperties(typing.TypedDict):
    editor_properties: EditorProperties
    name_string_table: AssetId
    name_string_name: str


@dataclasses.dataclass(frozen=True)
class NewHierarchyEntry[T: ScanTreeInstance]:
    _name_string_table_id: typing.ClassVar[AssetId | None] = None

    name_string_name: str

    @typing.final
    @classmethod
    def name_string_table_id(cls, editor: PatcherEditor) -> AssetId:
        """
        Gets the shared name string table ID for all new entries of this class.
        Creates it first, if necessary.
        """

        asset_name = f"{cls.__name__}Logbook.STRG"
        if not editor.does_asset_exists(asset_name):
            editor.duplicate_asset(0x2E681FEF, asset_name)
            strg = editor.get_file(asset_name, Strg)
            strg.set_strings_by_name_dict({})
        return editor.resolve_asset_id(asset_name)

    def apply(
        self, editor: PatcherEditor, tree: Tree, hierarchy_entries: list[HierEntry], dol_version: EchoesDolVersion
    ) -> ScriptInstance:
        """Prepares this hierarchy entry for use in a `HierarchyPatch`."""

        name_string_table = editor.get_file(self.name_string_table_id(editor), Strg)
        name_string_table.append_string(self.name_string_name, name=self.name_string_name)

        hierarchy_entries.append(self._create_hier_entry(editor))

        return tree.add_new_instance(self._create_instance(editor))

    @typing.final
    def _shared_properties(self, editor: PatcherEditor) -> HierarchySharedProperties:
        return HierarchySharedProperties(
            editor_properties=EditorProperties(name=self.name_string_name),
            name_string_table=self.name_string_table_id(editor),
            name_string_name=self.name_string_name,
        )

    def _create_instance(self, editor: PatcherEditor) -> T:
        """Creates a new instance for this entry."""
        raise NotImplementedError

    def _scan_id(self, editor: PatcherEditor) -> AssetId:
        """Gets or creates the scan for this entry. Used by `create_instance` and `create_hier_entry`."""
        raise NotImplementedError

    @typing.final
    def _create_hier_entry(self, editor: PatcherEditor) -> HierEntry:
        """Creates an entry to add to `Hier`."""
        return HierEntry(
            string_table_id=self.name_string_table_id(editor),
            name=self.name_string_name,
            scan_id=self._scan_id(editor),
            parent_id=default_asset_id,
        )


@dataclasses.dataclass(frozen=True)
class NewInventoryEntry(NewHierarchyEntry[ScanTreeInventory]):
    model_name: str
    scan_text: str
    slot_index: InventorySlotEnum
    item_index: PlayerItemEnum

    @typing.override
    def apply(
        self, editor: PatcherEditor, tree: Tree, hierarchy_entries: list[HierEntry], dol_version: EchoesDolVersion
    ) -> ScriptInstance:
        # Patch the inventory slot to check for the intended item
        editor.dol.write(
            dol_version.inventory_slot_to_item_id_address + 4 * self.slot_index.value,
            self.item_index.value.to_bytes(4, "big"),
        )

        return super().apply(editor, tree, hierarchy_entries, dol_version)

    @typing.override
    def _scan_id(self, editor: PatcherEditor) -> AssetId:
        return editor.create_full_scan(
            "",
            "",
            self.scan_text,
            model=editor.resolve_asset_id(model_database.PICKUP_MODELS[self.model_name].model),
        )

    @typing.override
    def _create_instance(self, editor: PatcherEditor) -> ScanTreeInventory:
        return ScanTreeInventory(
            **self._shared_properties(editor),
            inventory_slot=self.slot_index,
            scannable_parameters=ScannableParameters(
                scannable_info0=self._scan_id(editor),
            ),
        )


@dataclasses.dataclass(frozen=True)
class NewCategoryEntry(NewHierarchyEntry[ScanTreeCategory]):
    @typing.override
    def _scan_id(self, editor: PatcherEditor) -> int:
        return default_asset_id

    @typing.override
    def _create_instance(self, editor: PatcherEditor) -> ScanTreeCategory:
        return ScanTreeCategory(
            **self._shared_properties(editor),
        )


@dataclasses.dataclass(frozen=True)
class NewScanEntry(NewHierarchyEntry[ScanTreeScan]):
    scan_id: NameOrAssetId

    @typing.override
    def _scan_id(self, editor: PatcherEditor) -> AssetId:
        return editor.resolve_asset_id(self.scan_id)

    @typing.override
    def _create_instance(self, editor: PatcherEditor) -> ScanTreeScan:
        return ScanTreeScan(
            **self._shared_properties(editor),
            scannable_parameters=ScannableParameters(
                scannable_info0=self._scan_id(editor),
            ),
        )
