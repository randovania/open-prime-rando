from __future__ import annotations

import dataclasses
import traceback
from typing import TYPE_CHECKING, overload

from ppc_asm import assembler

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ppc_asm.dol_file import DolEditor

type MemoryAddress = int


@dataclasses.dataclass(frozen=True)
class Section:
    start: MemoryAddress
    length: int

    created_at: tuple[traceback.FrameSummary, ...]
    derived_from: Section | None = None


class CodeCaveTracker:
    """Tracks of all known code caves in the Dol, and provides APIs for requesting space for use."""

    dol_editor: DolEditor
    _symbol_sizes: dict[str, int]
    _sections: list[Section]

    def __init__(self, dol_editor: DolEditor):
        self.dol_editor = dol_editor
        self._symbol_sizes = {}
        self._sections = []

    @overload
    def add_empty_space(self, start: MemoryAddress, *, length: int) -> None: ...

    @overload
    def add_empty_space(self, start: MemoryAddress, *, end: MemoryAddress) -> None: ...

    def add_empty_space(
        self,
        start: MemoryAddress,
        *,
        length: int | None = None,
        end: MemoryAddress | None = None,
    ) -> None:
        """
        Declares that some memory segment is available to be used.
        :param start: The starting memory address of the segment.
        :param length: The length of the segment.
        :param end: The end memory address of the segment
        :return:
        """
        if end is not None:
            if length is not None:
                raise TypeError("Pass either 'length' or 'end', not both.")
            length = end - start

        if length is None:
            raise TypeError("Must pass either 'length' or 'end'.")

        if length <= 0:
            raise ValueError("'length' must be positive.")

        self._sections.append(
            Section(
                start=start,
                length=length,
                created_at=tuple(traceback.extract_stack()[:-1]),
            )
        )

    def register_symbol(self, symbol: str, start: MemoryAddress, end: MemoryAddress) -> None:
        """Register a debugging symbol to the editor, allowing the use of replace_symbol (and write_instructions)"""
        self.dol_editor.symbols[symbol] = start
        self._symbol_sizes[symbol] = end - start

    def replace_symbol(self, symbol: str, instructions: Sequence[assembler.BaseInstruction]) -> None:
        """Replaces the code at the given symbol with the given instructions, marking the remaining space as empty."""

        address = self.dol_editor.resolve_symbol(symbol)
        symbol_end = address + self._symbol_sizes[symbol]

        assembled = list(assembler.assemble_instructions(address, instructions, symbols=self.dol_editor.symbols))
        self.dol_editor.write(address, assembled)
        self.add_empty_space(address + len(assembled), end=symbol_end)

        self.dol_editor.write_instructions(
            symbol,
            instructions,
        )
