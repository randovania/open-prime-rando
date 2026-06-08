from __future__ import annotations

import itertools
import typing

from retro_data_structures.enums.echoes import InventorySlotEnum, PlayerItemEnum
from retro_data_structures.formats.hier import Hier
from retro_data_structures.formats.scan import Scan
from retro_data_structures.formats.tree import Tree
from retro_data_structures.properties.echoes.objects import ScannableObjectInfo, ScanTreeInventory

from open_prime_rando.echoes.logbook.hierarchy_patch import get_hierarchy_patches

if typing.TYPE_CHECKING:
    from open_prime_rando.dol_patching.echoes.dol_patches import EchoesDolVersion
    from open_prime_rando.echoes.rando_configuration import RandoConfiguration
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
            # TODO: when we introduce colored temple keys, update this with it
            info.animated_model.ancs = 0x41C2513F
            info.animated_model.character_index = 1
            info.animated_model.initial_anim = 1


def _patch_inventory_slots(editor: PatcherEditor, tree: Tree) -> None:
    """
    Edits existing inventory slots, to make certain
    logbook entries behave better in the randomizer.
    """

    # edit logbook entries to check for a different slot

    inventory_entries_to_change = {
        # Change the entry for charge combos to check for Supers instead
        141: InventorySlotEnum.SuperMissile,
        # Change the entry for Varia Suit to check for Power Beam, as we're reusing the item for Defense Up
        165: InventorySlotEnum.PowerBeam,  # TODO: some item we can guarantee is always present
    }

    for entry_id, slot in inventory_entries_to_change.items():
        with tree.get_node_by_id(entry_id).edit_properties(ScanTreeInventory) as tree_inventory:
            tree_inventory.inventory_slot = slot

    # edit slot assignments to check for a different inventory item

    slot_assignments_to_change = {
        # instead of dedicated logbook entry for ETM, use the normal item
        InventorySlotEnum.EnergyTransferModule: PlayerItemEnum.EnergyTransferModulePickup,
    }

    for slot, item in slot_assignments_to_change.items():
        editor.assign_item_to_inventory_slot(item, slot)


def patch_logbook(editor: PatcherEditor, version: EchoesDolVersion, configuration: RandoConfiguration) -> None:
    """
    Makes the needed modifications to the Logbook:
    - Add entries for the translators
    - Renames and reorganizes the lore entries for usage as hints
    """

    tree = editor.get_file(0x95B61279, Tree)

    hierarchy = editor.get_file(0xDD79DC2A, Hier)
    hierarchy_entries = list(hierarchy.entries)

    _patch_inventory_slots(editor, tree)
    _patch_dark_temple_key_scans(editor)

    for patch in get_hierarchy_patches(configuration):
        patch.apply(editor, tree, hierarchy_entries, version)

    hierarchy.entries = hierarchy_entries

    # Update paks manually (eww)
    _update_deps(editor, tree, hierarchy)
