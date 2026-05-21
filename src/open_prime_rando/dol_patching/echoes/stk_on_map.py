from __future__ import annotations

import dataclasses
import struct
from typing import TYPE_CHECKING

from ppc_asm.assembler import custom_ppc
from ppc_asm.assembler.ppc import *  # noqa: F403
from ppc_asm.dol_file import DolEditor
from retro_data_structures.enums.echoes import PlayerItemEnum

# ruff: noqa: F405

if TYPE_CHECKING:
    from ppc_asm.dol_file import DolEditor


@dataclasses.dataclass(frozen=True)
class StkMapIconSymbols:
    map_key_lut: int
    check_entry: int

    temple_key_found_icon: int
    temple_key_not_found_icon: int

    get_item_amount: int
    get_string_with_name: int

    wstring_append: int

    string_table: int

    increment_lut_entry: int
    check_lut_finished: int


def apply_stk_on_map(stk_symbols: StkMapIconSymbols, dol_editor: DolEditor) -> None:
    """
    Displays STKs on the map for Temple Grounds and Great Temple
    """
    _apply_lut_change(stk_symbols, dol_editor)
    _apply_for_loop_change(stk_symbols, dol_editor)


def _apply_lut_change(stk_symbols: StkMapIconSymbols, dol_editor: DolEditor) -> None:
    """
    update the lookup table to fit the necessary data in a smaller size
    so that we can then include sky temple keys in the LUT as well
    """

    dol_editor.symbols["kMapKeyLUT"] = stk_symbols.map_key_lut

    lut = [
        (PlayerItemEnum.DarkAgonKey1, 2),
        (PlayerItemEnum.DarkAgonKey2, 2),
        (PlayerItemEnum.DarkAgonKey3, 2),
        (PlayerItemEnum.DarkTorvusKey1, 3),
        (PlayerItemEnum.DarkTorvusKey2, 3),
        (PlayerItemEnum.DarkTorvusKey3, 3),
        (PlayerItemEnum.IngHiveKey1, 4),
        (PlayerItemEnum.IngHiveKey2, 4),
        (PlayerItemEnum.IngHiveKey3, 4),
        (PlayerItemEnum.SkyTempleKey1, 0),
        (PlayerItemEnum.SkyTempleKey2, 0),
        (PlayerItemEnum.SkyTempleKey3, 0),
        (PlayerItemEnum.SkyTempleKey4, 0),
        (PlayerItemEnum.SkyTempleKey5, 0),
        (PlayerItemEnum.SkyTempleKey6, 0),
        (PlayerItemEnum.SkyTempleKey7, 0),
        (PlayerItemEnum.SkyTempleKey8, 0),
        (PlayerItemEnum.SkyTempleKey9, 0),
    ]

    lut_data = b"".join(struct.pack(">hh", item, world_key_id) for item, world_key_id in lut)

    dol_editor.symbols["CAutoMapper::kSTKon"] = dol_editor.symbols["kMapKeyLUT"] + len(lut_data)
    stk_on = b"STKOn\0"

    orig_lut_len = 9 * 3 * 4
    if len(lut_data + stk_on) > orig_lut_len:
        raise RuntimeError("Overflowed map entry LUT")

    dol_editor.write("kMapKeyLUT", lut_data)
    dol_editor.write("CAutoMapper::kSTKon", stk_on)


def _apply_for_loop_change(stk_symbols: StkMapIconSymbols, dol_editor: DolEditor) -> None:
    """
    body of the for loop. runs once for each entry in the LUT
    """
    dol_editor.symbols["CAutoMapper::UpdateTempleKeys::CheckEntry"] = stk_symbols.check_entry
    dol_editor.symbols["CAutoMapper::UpdateTempleKeys::IncrementLUTEntry"] = stk_symbols.increment_lut_entry

    dol_editor.symbols["CAutoMapper::kTempleKeyNotFoundIcon"] = stk_symbols.temple_key_not_found_icon
    dol_editor.symbols["CAutoMapper::kTempleKeyFoundIcon"] = stk_symbols.temple_key_found_icon

    dol_editor.symbols["CPlayerState::GetItemAmount"] = stk_symbols.get_item_amount
    dol_editor.symbols["CStringTable::GetStringWithName"] = stk_symbols.get_string_with_name
    dol_editor.symbols["wstring::append"] = stk_symbols.wstring_append

    dol_editor.symbols["gpStringTable"] = stk_symbols.string_table

    # semantic names for the registers being used
    entry_world_id = r0
    stack_pointer = r1

    iterator_value = r28
    lut_entry = r29
    player_state = r30
    selected_world_id = r31

    param0 = r3
    param1 = r4
    param2 = r5

    ret = r3

    WORLD_ID_FOR_STK_ICON = 0  # temple grounds and great temple

    # body of the for loop
    dol_editor.write_instructions(
        "CAutoMapper::UpdateTempleKeys::CheckEntry",
        [
            # check if current world index matches this entry's
            lhz(entry_world_id, 0x2, lut_entry),  # lut_entry.world_id
            cmpw(0, selected_world_id, entry_world_id),
            bne("CAutoMapper::UpdateTempleKeys::IncrementLUTEntry"),
            #
            # get item amount
            lhz(param1, 0x0, lut_entry),  # lut_entry.item
            or_(param0, player_state, player_state),
            li(param2, 0x1),
            bl("CPlayerState::GetItemAmount"),
            #
            # make sure world index is back in r0 before branching
            lhz(entry_world_id, 0x2, lut_entry),  # lut_entry.world_id
            #
            # check if player has the key
            cmpwi(ret, 0x0),
            ble("_case_NO_KEY"),
            #
            # player has key
            cmpwi(entry_world_id, WORLD_ID_FOR_STK_ICON),
            bne("_case_RED_KEY"),
            #
            # key is an STK
            custom_ppc.load_unsigned_32bit(param1, dol_editor.symbols["CAutoMapper::kSTKon"]).with_label("_case_STK"),
            b("CAutoMapper::UpdateTempleKeys::LoadString"),
            #
            # key is a red key
            custom_ppc.load_unsigned_32bit(param1, dol_editor.symbols["CAutoMapper::kTempleKeyFoundIcon"]).with_label(
                "_case_RED_KEY"
            ),
            b("CAutoMapper::UpdateTempleKeys::LoadString"),
            #
            # player does not have key
            custom_ppc.load_unsigned_32bit(
                param1, dol_editor.symbols["CAutoMapper::kTempleKeyNotFoundIcon"]
            ).with_label("_case_NO_KEY"),
            #
            # load appropriate string
            custom_ppc.load_unsigned_32bit(param0, dol_editor.symbols["gpStringTable"]).with_label(
                "CAutoMapper::UpdateTempleKeys::LoadString"
            ),
            lwz(param0, 0x0, param0),
            bl("CStringTable::GetStringWithName"),
            #
            # append to our string
            or_(param1, ret, ret),
            addi(param0, stack_pointer, 0x18),  # our wstring
            li(param2, -0x1),
            bl("wstring::append"),
            b("CAutoMapper::UpdateTempleKeys::IncrementLUTEntry"),
        ],
    )

    # end of the for loop
    dol_editor.symbols["CAutoMapper::UpdateTempleKeys::CheckLUTFinished"] = stk_symbols.check_lut_finished

    # update the increment to use the new size of the entries
    dol_editor.write_instructions(
        "CAutoMapper::UpdateTempleKeys::IncrementLUTEntry",
        [
            # i++
            addi(iterator_value, iterator_value, 0x1),
            #
            # increase the lut_entry pointer by the size of our new entries
            addi(lut_entry, lut_entry, 0x4),
        ],
    )

    # update the bounds check to use the new length of the LUT
    dol_editor.write_instructions(
        "CAutoMapper::UpdateTempleKeys::CheckLUTFinished",
        [
            cmpwi(iterator_value, 18),
        ],
    )
