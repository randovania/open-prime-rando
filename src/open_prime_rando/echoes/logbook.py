from __future__ import annotations

import dataclasses
import itertools
import typing

from retro_data_structures.enums.echoes import InventorySlotEnum, Message, PlayerItemEnum, State
from retro_data_structures.formats import Strg
from retro_data_structures.formats.hier import Hier, HierEntry
from retro_data_structures.formats.tree import Tree
from retro_data_structures.properties.echoes.archetypes import EditorProperties, ScannableParameters
from retro_data_structures.properties.echoes.objects import ScanTreeCategory, ScanTreeInventory

from open_prime_rando.echoes.pickups import model_database

if typing.TYPE_CHECKING:
    from retro_data_structures.base_resource import AssetId
    from retro_data_structures.formats.script_object import ScriptInstance

    from open_prime_rando.dol_patching.echoes.dol_patches import EchoesDolVersion
    from open_prime_rando.patcher_editor import PatcherEditor


@dataclasses.dataclass(frozen=True)
class NewLogbookEntry:
    model_name: str
    entry_title: str
    scan_text: str
    slot_index: InventorySlotEnum
    item_index: PlayerItemEnum

    def create_scan(self, editor: PatcherEditor) -> AssetId:
        """
        Creates the scan for this entry. Used by `create_inventory_instance` and `create_hier_entry`.
        """
        return editor.create_full_scan(
            "",
            "",
            self.scan_text,
            model=editor.resolve_asset_id(model_database.PICKUP_MODELS[self.model_name].model),
        )

    def create_inventory_instance(self, strg_id: AssetId, scan_id: AssetId) -> ScanTreeInventory:
        """
        :param strg_id: The strg created by `_create_strings`.
        :param scan_id: The scan created by `create_scan`.
        :return:
        """
        return ScanTreeInventory(
            editor_properties=EditorProperties(name=self.model_name),
            name_string_table=strg_id,
            name_string_name=self.model_name,
            inventory_slot=self.slot_index,
            scannable_parameters=ScannableParameters(
                scannable_info0=scan_id,
            ),
        )

    def create_hier_entry(self, strg_id: AssetId, scan_id: AssetId, category_obj: ScriptInstance) -> HierEntry:
        """Create an entry to add to `Hier`"""
        return HierEntry(
            string_table_id=strg_id,
            name=self.model_name,
            scan_id=scan_id,
            parent_id=category_obj.id,
        )


_LOGBOOK_ENTRIES = {
    "VioletTranslator": NewLogbookEntry(
        model_name="VioletTranslator",
        entry_title="Violet Translator",
        scan_text="The &push;&main-color=#784784;Violet Translator&pop; allows you to access devices"
        " and doors coded with &push;&main-color=#784784;Violet&pop; holograms.",
        slot_index=InventorySlotEnum.DarkBomb,
        item_index=PlayerItemEnum.VioletTranslator,
    ),
    "AmberTranslator": NewLogbookEntry(
        model_name="AmberTranslator",
        entry_title="Amber Translator",
        scan_text="The &push;&main-color=#A45600;Amber Translator&pop; allows you to access devices"
        " and doors coded with &push;&main-color=#A45600;Amber&pop; holograms.",
        slot_index=InventorySlotEnum.LightBomb,
        item_index=PlayerItemEnum.AmberTranslator,
    ),
    "EmeraldTranslator": NewLogbookEntry(
        model_name="EmeraldTranslator",
        entry_title="Emerald Translator",
        scan_text="The &push;&main-color=#4E9761;Emerald Translator&pop; allows you to access devices"
        " and doors coded with &push;&main-color=#4E9761;Emerald&pop; holograms.",
        slot_index=InventorySlotEnum.AnnihilatorBomb,
        item_index=PlayerItemEnum.EmeraldTranslator,
    ),
    "CobaltTranslator": NewLogbookEntry(
        model_name="CobaltTranslator",
        entry_title="Cobalt Translator",
        scan_text="The &push;&main-color=#56789D;Cobalt Translator&pop; allows you to access devices"
        " and doors coded with &push;&main-color=#56789D;Cobalt&pop; holograms.",
        slot_index=InventorySlotEnum.BeamCombo,
        item_index=PlayerItemEnum.CobaltTranslator,
    ),
}


@dataclasses.dataclass(frozen=True)
class HierarchyPatch:
    node_id: int
    rename: str | None
    connections: tuple[int | HierarchyPatch, ...] = ()

    def apply(self, editor: PatcherEditor, tree: Tree, hierarchy_entries: list[HierEntry]) -> None:
        """
        Apply this patch to the matching entry.
        Renames if needed, changes parent of the connections and recurses as needed.
        """
        node = tree.get_node_by_id(self.node_id)
        node.connections = []

        if self.rename is not None:
            entry = hierarchy_entries[node.id]
            editor.get_file(entry.string_table_id, Strg).set_single_string_by_name(entry.name, self.rename)

        for new_conn in self.connections:
            if isinstance(new_conn, HierarchyPatch):
                new_conn.apply(editor, tree, hierarchy_entries)
                the_id = new_conn.node_id
            else:
                the_id = new_conn

            node.add_connection(State.Connect, Message.Attach, the_id)
            hierarchy_entries[the_id] = dataclasses.replace(hierarchy_entries[the_id], parent_id=node.id)


hierarchy_patch = [
    # TODO: are these inventory stuff?
    HierarchyPatch(
        25,
        None,
        (
            HierarchyPatch(81, "Keys 1, 2, 3", (148, 151, 156)),
            HierarchyPatch(166, "Keys 4, 5, 6", (45, 303, 317)),
            HierarchyPatch(195, "Keys 7, 8, 9", (159, 221, 231)),
        ),
    ),
    HierarchyPatch(
        318,
        None,
        (
            HierarchyPatch(
                119,
                "Hints",
                (
                    HierarchyPatch(
                        60,
                        "Regular Hints",
                        (
                            HierarchyPatch(
                                38,
                                "Violet",
                                (
                                    HierarchyPatch(4, "&line-spacing=75;Transport to\nAgon Wastes"),
                                    HierarchyPatch(33, "Meeting Grounds"),
                                    HierarchyPatch(120, "Path of Eyes"),
                                    HierarchyPatch(251, "&line-spacing=75;Fortress\nTransport\nAccess"),
                                    HierarchyPatch(364, "&line-spacing=75;Main Energy\nController"),
                                ),
                            ),
                            HierarchyPatch(
                                74,
                                "Amber",
                                (
                                    HierarchyPatch(59, "Mining Plaza"),
                                    HierarchyPatch(75, "Mining Station A"),
                                    HierarchyPatch(82, "Mining Station B"),
                                    HierarchyPatch(102, "&line-spacing=75;Agon Energy\nController"),
                                    HierarchyPatch(260, "Portal Terminal"),
                                ),
                            ),
                            HierarchyPatch(
                                154,
                                "Emerald",
                                (
                                    HierarchyPatch(169, "Path of Roots"),
                                    HierarchyPatch(200, "Underground Tunnel"),
                                    HierarchyPatch(228, "&line-spacing=75;Torvus Energy\nController"),
                                    HierarchyPatch(243, "Training Chamber"),
                                    HierarchyPatch(312, "Gathering Hall"),
                                    HierarchyPatch(342, "Catacombs"),
                                ),
                            ),
                            HierarchyPatch(
                                196,
                                "Cobalt",
                                (
                                    HierarchyPatch(17, "Sanctuary Entrance"),
                                    HierarchyPatch(19, "&line-spacing=75;Hall of Combat\nMastery"),
                                    HierarchyPatch(23, "Main Gyro Chamber"),
                                    HierarchyPatch(162, "&line-spacing=75;Sanctuary\nEnergy\nController"),
                                    HierarchyPatch(183, "Watch Station"),
                                    HierarchyPatch(379, "Main Research"),
                                ),
                            ),
                        ),
                    ),
                    HierarchyPatch(
                        254,
                        "&line-spacing=75;Sky Temple\nKey Hints",
                        (
                            HierarchyPatch(129, "Keys 1, 2, 3", (29, 118, 367)),
                            HierarchyPatch(233, "Keys 4, 5, 6", (58, 191, 373)),
                            HierarchyPatch(319, "Keys 7, 8, 9", (52, 289, 329)),
                        ),
                    ),
                    HierarchyPatch(
                        326,
                        "&line-spacing=75;Flying Ing\nCache Hints",
                        (
                            HierarchyPatch(124, "Temple Grounds", (35, 152, 355)),
                            HierarchyPatch(194, "Agon Wastes", (1, 6)),
                            HierarchyPatch(241, "Torvus Bog", (223, 284)),
                            HierarchyPatch(327, "Sanctuary Fortress", (46, 275)),
                        ),
                    ),
                ),
            ),
            216,
            277,
            343,
        ),
    ),
]


def _create_strings(editor: PatcherEditor) -> AssetId:
    # Create the STRG with the strings for all the logbook tree items
    # All entries needs a name
    strings = {"Translators": "Translators"}

    for translator in _LOGBOOK_ENTRIES.values():
        strings[translator.model_name] = translator.entry_title

    translator_category_strg_id = editor.duplicate_asset(0x2E681FEF, "TranslatorsLogbook.STRG")
    translator_category_strg = editor.get_file(translator_category_strg_id, Strg)
    translator_category_strg.set_strings_by_name_dict(strings)

    return translator_category_strg_id


def _update_deps(editor: PatcherEditor, tree: Tree, hierarchy: Hier) -> None:
    paks = sorted(set(editor.find_paks(0x95B61279)) | set(editor.find_paks(0x2E681FEF)))
    for dep in itertools.chain(tree.dependencies_for(), hierarchy.dependencies_for()):
        for pak in paks:
            editor.ensure_present(pak, dep.id)


def patch_logbook(editor: PatcherEditor, version: EchoesDolVersion) -> None:
    """
    Makes the needed modifications to the Logbook:
    - Add entries for the translators
    - Renames and reorganizes the lore entries for usage as hints
    """

    tree = editor.get_file(0x95B61279, Tree)

    hierarchy = editor.get_file(0xDD79DC2A, Hier)
    hierarchy_entries = list(hierarchy.entries)

    # Change the entry for charge combos to check for Supers instead
    with tree.get_node_by_id(141).edit_properties(ScanTreeInventory) as tree_inventory:
        tree_inventory.inventory_slot = InventorySlotEnum.SuperMissile

    translator_category_strg_id = _create_strings(editor)

    # Create the category
    category_obj = tree.add_new_instance(
        ScanTreeCategory(
            editor_properties=EditorProperties(name="Translators"),
            name_string_table=translator_category_strg_id,
            name_string_name="Translators",
        )
    )
    tree.get_node_by_id(320).add_connection(State.Connect, Message.Attach, category_obj)
    hierarchy_entries.append(
        HierEntry(
            string_table_id=translator_category_strg_id,
            name="Translators",
            scan_id=0xFFFFFFFF,
            parent_id=320,  # Visors
        )
    )

    for translator in _LOGBOOK_ENTRIES.values():
        scan_id = translator.create_scan(editor)

        log_entry = tree.add_new_instance(translator.create_inventory_instance(translator_category_strg_id, scan_id))
        category_obj.add_connection(State.Connect, Message.Attach, log_entry)
        hierarchy_entries.append(translator.create_hier_entry(translator_category_strg_id, scan_id, category_obj))

        # Patch the slot to check for the intended item
        editor.dol.write(
            version.inventory_slot_to_item_id_address + 4 * translator.slot_index.value,
            translator.item_index.value.to_bytes(4, "big"),
        )

    for patch in hierarchy_patch:
        patch.apply(editor, tree, hierarchy_entries)

    hierarchy.entries = hierarchy_entries

    # Update paks manually (eww)
    _update_deps(editor, tree, hierarchy)
