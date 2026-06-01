from __future__ import annotations

import struct
from typing import TYPE_CHECKING

from ppc_asm.assembler import custom_ppc
from ppc_asm.assembler.ppc import cmplwi, lbzx, nop, r0, r4, r8
from retro_data_structures.enums.echoes import PlayerItemEnum

if TYPE_CHECKING:
    from open_prime_rando.dol_patching.echoes.dol_patches import EchoesDolVersion
    from open_prime_rando.patcher_editor import PatcherEditor


def setup_inventory_slot_to_item(dol_version: EchoesDolVersion, editor: PatcherEditor) -> None:
    """
    Sets the initial editor.inventory_slot_to_item and marks the original address as an available section.
    """

    original_slot_count = 0x35
    # "kInventorySlotToItemType"

    # Just read the binary to get the original mapping
    original_mapping = struct.unpack(
        ">" + "L" * original_slot_count,
        editor.dol.read(dol_version.inventory_slot_to_item_id_address, original_slot_count * 4),
    )
    editor.inventory_slot_to_item = [PlayerItemEnum(index) for index in original_mapping]

    # Mark the existing mapping as an available code cave
    editor.code_cave.replace_address(dol_version.inventory_slot_to_item_id_address, original_slot_count * 4, b"")


def create_new_inventory_slot_array(dol_version: EchoesDolVersion, editor: PatcherEditor) -> None:
    """
    Patches the game code that uses kInventorySlotToItemType to load from somewhere else.
    Also change the array to use 8-bit per index, instead of 32-bit ints.
    """

    encoded_mapping = struct.pack(
        ">" + "B" * len(editor.inventory_slot_to_item),
        *[it.value for it in editor.inventory_slot_to_item],
    )

    def _with_cave(address: int) -> None:
        editor.dol.symbols["kInventorySlotToItemType"] = address

        # Replace the bounds check with the new enum count size
        editor.dol.write_instructions(
            dol_version.load_scan_tree_inventory_slot_usage,
            [
                cmplwi(r0, len(editor.inventory_slot_to_item)),
            ],
        )

        # `dol_version.load_scan_tree_inventory_slot_usage + 4` is a branch operation
        # Leaving it untouched is a lot easier!

        # Replace the code that reads the
        editor.dol.write_instructions(
            dol_version.load_scan_tree_inventory_slot_usage + 8,
            [
                custom_ppc.load_address(r4, address),
                # r0 contains the slot index
                lbzx(r8, r4, r0),
                nop(),  # original code would expand the offset to be 4 times the index. that's not needed anymore
            ],
        )

    editor.code_cave.request_data_cave(encoded_mapping, 1, _with_cave)
