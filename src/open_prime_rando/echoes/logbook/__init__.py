from __future__ import annotations

import itertools
import typing

from retro_data_structures.enums.echoes import InventorySlotEnum
from retro_data_structures.formats.hier import Hier
from retro_data_structures.formats.tree import Tree
from retro_data_structures.properties.echoes.objects import ScanTreeInventory

from open_prime_rando.echoes.logbook.hierarchy_patch import HIERARCHY_PATCHES

if typing.TYPE_CHECKING:
    from open_prime_rando.dol_patching.echoes.dol_patches import EchoesDolVersion
    from open_prime_rando.patcher_editor import PatcherEditor


def _update_deps(editor: PatcherEditor, tree: Tree, hierarchy: Hier) -> None:
    paks = sorted(set(editor.find_paks(0x95B61279)) | set(editor.find_paks(0xDD79DC2A)))
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

    for patch in HIERARCHY_PATCHES:
        patch.apply(editor, tree, hierarchy_entries, version)

    hierarchy.entries = hierarchy_entries

    # Update paks manually (eww)
    _update_deps(editor, tree, hierarchy)
