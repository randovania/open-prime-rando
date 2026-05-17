from __future__ import annotations

import itertools
import typing

from retro_data_structures.enums.echoes import InventorySlotEnum
from retro_data_structures.formats.hier import Hier
from retro_data_structures.formats.scan import Scan
from retro_data_structures.formats.tree import Tree
from retro_data_structures.properties.echoes.objects import ScannableObjectInfo, ScanTreeInventory

from open_prime_rando.echoes.logbook.hierarchy_patch import HIERARCHY_PATCHES

if typing.TYPE_CHECKING:
    from open_prime_rando.dol_patching.echoes.dol_patches import EchoesDolVersion
    from open_prime_rando.patcher_editor import PatcherEditor


def _update_deps(editor: PatcherEditor, tree: Tree, hierarchy: Hier) -> None:
    paks = sorted(set(editor.find_paks(0x95B61279)) | set(editor.find_paks(0xDD79DC2A)))
    for dep in itertools.chain(tree.dependencies_for(), hierarchy.dependencies_for()):
        for pak in paks:
            editor.ensure_present(pak, dep.id)


def _patch_dark_temple_key_scans(editor: PatcherEditor) -> None:
    """
    Edit the SCANs for the dark temple key hints to use the temple key model in the logbook.
    """

    scan_ids = (0xA9B11356, 0x8C669B58, 0x813068D5)
    for scan_id in scan_ids:
        scan = editor.get_file(scan_id, Scan)
        with scan.scannable_object_info.edit_properties(ScannableObjectInfo) as info:
            info.animated_model.ancs = 0x41C2513F
            info.animated_model.character_index = 1
            info.animated_model.initial_anim = 1


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

    _patch_dark_temple_key_scans(editor)

    for patch in HIERARCHY_PATCHES:
        patch.apply(editor, tree, hierarchy_entries, version)

    hierarchy.entries = hierarchy_entries

    # Update paks manually (eww)
    _update_deps(editor, tree, hierarchy)
