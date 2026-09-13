"""Warp to start: declining a save while holding L+R returns you to the
starting room, mirroring randomprime's ``warpToStart`` for Metroid Prime 1.

Two halves:

**SCLY** (`register`): every Save Station room gets a new layer holding a
HUDMemo, a short Timer and a ``WorldTeleporter`` aimed at
``configuration.starting_area``, hung off a script state that nothing in
the vanilla game broadcasts.

**DOL** (`apply_dol_patches`): the save-station tick function broadcasts
``State.Zero`` when the player declines the prompt; one ``bl`` there is
redirected through a code cave that swaps the broadcast state for
``State.InternalState15`` when both triggers are held. Declining without
them held is bit-for-bit vanilla, and the swap (rather than an extra
broadcast) means the vanilla "no save" cinematic doesn't fight the warp.
"""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from ppc_asm.assembler.ppc import addi, b, bl, ble, cmpw, lis, lwz, ori, r0, r4, r5, r11, r12
from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats.strg import Strg
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.objects import HUDMemo, SpecialFunction, Timer, WorldTeleporter

if TYPE_CHECKING:
    from ppc_asm.assembler import BaseInstruction
    from retro_data_structures.formats.mlvl import Mlvl
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.area_patcher import AreaPatcher
    from open_prime_rando.dol_patching.code_cave_tracker import CodeCaveTracker
    from open_prime_rando.dol_patching.echoes.dol_patches import WarpToStartAddresses
    from open_prime_rando.echoes.pydantic_models import AreaReference
    from open_prime_rando.patcher_editor import PatcherEditor

_LAYER_NAME = "Warp To Start"

_MEMO_STRG_NAME = "ap_warp_to_start.STRG"
_MEMO_TEXT = "&just=center;Returning to starting room..."

WARP_DELAY_SECONDS = 3.0
"""How long the HUD memo shows before the transition starts -- randomprime's
``warpToStartDelayS``."""

_MEMORY_CARD_STRG = 0x88E242D6
"""``STRG_MemoryCard_0``, the memory-card prompt strings -- the same table
``open_prime_rando.echoes.general_changes.apply_corrupted_memory_card_change``
edits."""

_SAVE_PROMPT_NAME = "SaveFile"
_SAVE_PROMPT_HINT = "\nHold L + R while choosing No to warp to the starting room."

_SAVE_STATION_FUNCTION = 7
"""``SpecialFunction.Function.SaveStationCheckpoint``. Compared numerically
so this module doesn't need the enum imported at module scope."""


# --------------------------------------------------------------------------
# SCLY
# --------------------------------------------------------------------------


def find_save_station_special_function(area: Area) -> object | None:
    """Returns the area's save-station ``SpecialFunction`` instance, or None.

    Matches on ``function == SaveStationCheckpoint`` *and* the presence of a
    ``Zero`` connection, which is the state the game broadcasts when the
    player declines the prompt. Great Temple's Sanctum has a
    SaveStationCheckpoint with no ``Zero`` connections -- an autosave that
    never prompts -- and must not be patched; keying on the instance name
    ("SpecialFunction Save Station") would be less precise, since that name
    is a level-designer convention rather than something the game reads.

    Raises ValueError if an area somehow has more than one, rather than
    silently patching an arbitrary one.
    """
    matches = []
    for layer in area.layers:
        for instance in layer.instances:
            if instance.type_name != "SPFN":
                continue
            properties = instance.get_properties()
            if not isinstance(properties, SpecialFunction):
                continue
            if int(properties.function) != _SAVE_STATION_FUNCTION:
                continue
            if not any(connection.state == State.Zero for connection in instance.connections):
                continue
            matches.append(instance)

    if len(matches) > 1:
        raise ValueError(f"{area.name} has {len(matches)} save-station SpecialFunctions; expected at most one")
    return matches[0] if matches else None


def add_warp_to_start(editor: PatcherEditor, mlvl: Mlvl, area: Area, starting_area: AreaReference) -> None:
    """Global ``AreaPatcher`` function: no-op unless ``area`` is a Save
    Station, in which case it adds the warp objects and wires them to the
    save station's ``InternalState15`` broadcast (see the module docstring).
    """
    save_station = find_save_station_special_function(area)
    if save_station is None:
        return

    memo_strg, _ = editor.create_strg(_MEMO_STRG_NAME, _MEMO_TEXT)

    layer = area.add_layer(_LAYER_NAME)

    memo = layer.add_instance_with(
        HUDMemo(
            editor_properties=EditorProperties(name="Warp Memo"),
            display_time=WARP_DELAY_SECONDS,
            # 1 is the on-screen message box every vanilla save-station memo
            # uses (and what open-prime-rando's pickup_editing sets for a
            # memo meant to be seen); the default 0 is the silent variant.
            display_type=1,
            string=memo_strg,
        )
    )
    timer = layer.add_instance_with(
        Timer(
            editor_properties=EditorProperties(name="Warp Delay"),
            time=WARP_DELAY_SECONDS,
            auto_reset=False,
            auto_start=False,
        )
    )
    # Modelled on the Map Station's room-to-room warps (e.g. Hive Chamber A's
    # "Map to Hive Save 04"), which are the only vanilla WorldTeleporters that
    # move the player between two arbitrary, non-elevator rooms: no elevator
    # index, no platform/shaft model and no sound group, so this adds no new
    # asset dependencies to the 18 rooms it touches.
    teleporter = layer.add_instance_with(
        WorldTeleporter(
            editor_properties=EditorProperties(name="Warp To Start"),
            world=starting_area.mlvl_id,
            area=starting_area.mrea_id,
            elevator=-1,
            is_teleport=False,
            is_fade_white=False,
        )
    )

    save_station.add_connection(State.InternalState15, Message.SetToZero, memo)
    save_station.add_connection(State.InternalState15, Message.ResetAndStart, timer)
    timer.add_connection(State.Zero, Message.SetToZero, teleporter)


def patch_save_prompt_hint(editor: PatcherEditor) -> None:
    """Appends the gesture hint to "Save progress to Memory Card in Slot A?",
    so the feature is discoverable in-game (randomprime's
    ``patch_memorycard_strg`` does the same for Prime 1).

    Appends rather than rewrites, so it survives the prompt's wording
    differing between the NTSC-U and PAL tables.
    """
    table = editor.get_file(_MEMORY_CARD_STRG, Strg)
    index = table.raw.name_table[_SAVE_PROMPT_NAME]
    table.set_single_string(index, table.strings[index] + _SAVE_PROMPT_HINT)


def register(area_patcher: AreaPatcher, starting_area: AreaReference) -> None:
    """Registers the SCLY half: the per-area warp objects, plus the one-shot
    hint on the save prompt.

    The area half goes in as a global function rather than a hardcoded list
    of the 18 Save Station rooms: open-prime-rando already runs several
    global functions, so every area is loaded and walked regardless, and a
    discovered list can't drift out of sync with the game.
    """
    area_patcher.add_global_function(functools.partial(add_warp_to_start, starting_area=starting_area))
    patch_save_prompt_hint(area_patcher.editor)


# --------------------------------------------------------------------------
# DOL
# --------------------------------------------------------------------------

# CStateManager fields. Struct layout is identical on NTSC-U and PAL -- only
# code and data addresses move between the two builds.
_FINAL_INPUT_ARRAY = 0x153C
"""Offset from CStateManager of the per-player CFinalInput array. Taken from
the loop that feeds CPlayer::ProcessInput: ``r4 = mgr + 0x153C + player *
0x2C``."""

_LEFT_TRIGGER = 0x18
_RIGHT_TRIGGER = 0x1C
"""Offsets within CFinalInput of the two analog trigger values, as read by
the game's own *digital* (held) accessors for the trigger-bound commands.

CFinalInput is 0x2C bytes (the array at CStateManager+0x153C is built as a
4-element reserved_vector with element size 0x2C) and carries each trigger
twice: 0x18/0x1C are the current values, 0x20/0x24 the "pressed this frame"
values, which are zero on every frame except the one the trigger crosses
the threshold. Both pairs are read by accessors of identical shape, so they
are told apart by the two parallel CControlMapper member-function-pointer
tables: the entries at the same index in the second table additionally test
a just-pressed bit in the flags at CFinalInput+0x28. A gesture the player
*holds* must read the first pair -- reading 0x20/0x24 means both triggers
would have to cross the threshold on the exact frame of the broadcast, so
the warp effectively never fires."""

_TRIGGER_DEADZONE_BITS = 0x3D4CCCCD
"""``0.05f``, the threshold those accessors compare against. Both triggers
are normalised to [0, 1], and IEEE-754 ordering matches signed-integer
ordering for non-negative floats, so the cave compares the raw bits with
``cmpw`` instead of carrying a float constant."""

_INTERNAL_STATE_15 = 0x49533135
"""``State.InternalState15`` ('IS15'), as Echoes stores script states at
runtime. Nothing in the vanilla game broadcasts or listens for it."""


def build_gate_cave(addresses: WarpToStartAddresses) -> list[BaseInstruction]:
    """The code cave that replaces the declined-save ``bl``.

    On entry the save-station tick function has already set up the broadcast call:
    r3 = the SpecialFunction, r4 = the ``ZERO`` state, r5 = CStateManager,
    r6 = &editorId, r7 = -1, LR = the instruction after the ``bl``. All this
    does is swap r4 when both triggers are held, then tail-branch into the
    broadcast helper so it returns straight to the tick function -- no stack frame,
    and r0/r11/r12 are volatile and not arguments.
    """
    setup = [
        addi(r11, r5, _FINAL_INPUT_ARRAY),
        lis(r12, _TRIGGER_DEADZONE_BITS >> 16),
        ori(r12, r12, _TRIGGER_DEADZONE_BITS & 0xFFFF),
    ]
    check_left = [lwz(r0, _LEFT_TRIGGER, r11), cmpw(0, r0, r12)]
    check_right = [lwz(r0, _RIGHT_TRIGGER, r11), cmpw(0, r0, r12)]
    swap_state = [
        lis(r4, _INTERNAL_STATE_15 >> 16),
        ori(r4, r4, _INTERNAL_STATE_15 & 0xFFFF),
    ]

    # `ble` offsets are relative to the branch itself, so each must count the
    # instructions between it and the tail branch, plus itself.
    skip_from_left = (1 + len(check_right) + 1 + len(swap_state)) * 4
    skip_from_right = (1 + len(swap_state)) * 4

    return [
        *setup,
        *check_left,
        ble(skip_from_left, relative=True),
        *check_right,
        ble(skip_from_right, relative=True),
        *swap_state,
        b(addresses.send_script_msgs),
    ]


def apply_dol_patches(cave: CodeCaveTracker, addresses: WarpToStartAddresses) -> None:
    """Requests the gate cave and points the declined-save ``bl`` at it.

    Must run before ``CodeCaveTracker.fulfill_requests()``, i.e. from inside
    ``_apply_patches``.
    """

    def _with_cave(cave_address: int) -> None:
        cave.dol_editor.write_instructions(
            addresses.decline_broadcast_call,
            [bl(cave_address)],
        )

    cave.request_code_cave(build_gate_cave(addresses), _with_cave)
