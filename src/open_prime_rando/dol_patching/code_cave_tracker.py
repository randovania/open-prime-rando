from __future__ import annotations

import dataclasses
import logging
import traceback
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, overload

from ppc_asm import assembler

if TYPE_CHECKING:
    from ppc_asm.dol_file import DolEditor

type MemoryAddress = int


@dataclasses.dataclass(frozen=True)
class Section:
    start: MemoryAddress
    length: int

    created_at: tuple[traceback.FrameSummary, ...]
    derived_from: Section | None = None


@dataclasses.dataclass(frozen=True)
class CaveRequest:
    size: int
    instructions: Sequence[assembler.BaseInstruction]
    callback: Callable[[int], None]
    created_at: tuple[traceback.FrameSummary, ...]


class CodeCaveTracker:
    """Tracks of all known code caves in the Dol, and provides APIs for requesting space for use."""

    dol_editor: DolEditor
    _symbol_sizes: dict[str, int]
    _sections: list[Section]
    _requests: list[CaveRequest]

    def __init__(self, dol_editor: DolEditor):
        self.dol_editor = dol_editor
        self._symbol_sizes = {}
        self._sections = []
        self._requests = []

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
            if length is not None:  # pragma: no cover
                raise TypeError("Pass either 'length' or 'end', not both.")
            length = end - start

        if length is None:  # pragma: no cover
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

    def request_cave_for(
        self,
        instructions: Sequence[assembler.BaseInstruction],
        callback: Callable[[int], None],
    ) -> None:
        """
        Creates a request for a block of memory with enough size to fit given instructions.
        These instructions are automatically placed
        :param instructions:
        :param callback: A function to be called with the address of the allocated cave.
        :return:
        """
        self._requests.append(
            CaveRequest(
                size=assembler.byte_count(instructions),
                instructions=instructions,
                callback=callback,
                created_at=tuple(traceback.extract_stack()[:-1]),
            )
        )

    def fulfill_requests(self) -> None:
        """Fulfill all cave requests, using empty space registered."""

        self._requests.sort(key=lambda x: x.size)

        while self._requests:
            request = self._requests.pop()
            logging.debug(f"Fulfilling request: {request}")

            address = None
            self._sections.sort(key=lambda x: x.length)

            for i, section in enumerate(self._sections):
                logging.debug(f"Inspecting section: {section}")
                if section.length >= request.size:
                    self._sections.pop(i)
                    address = section.start
                    if section.length > request.size:
                        new_section = Section(
                            start=section.start + request.size,
                            length=section.length - request.size,
                            created_at=request.created_at,
                            derived_from=section,
                        )
                        self._sections.append(new_section)
                    break

            if address is None:
                raise ValueError(f"Unable to find a section to fulfill {request}.")

            request.callback(address)

            # write the instructions after, in case they reference a symbol created in the callback
            # (like the address of a cave!)
            self.dol_editor.write_instructions(address, request.instructions)
