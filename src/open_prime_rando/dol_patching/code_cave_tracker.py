from __future__ import annotations

import dataclasses
import functools
import logging
import traceback
from collections.abc import Callable, Iterable, Sequence
from typing import TYPE_CHECKING, overload

from ppc_asm import assembler
from ppc_asm.assembler import ppc

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
    alignment: int
    callback: Callable[[int], None]
    created_at: tuple[traceback.FrameSummary, ...]


def _align_address(address: MemoryAddress, alignment: int) -> MemoryAddress:
    remainder = address % alignment
    if remainder == 0:
        return address
    return address + (alignment - remainder)


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

    def replace_address(self, address: MemoryAddress, length: int, data: bytes | Iterable[int]) -> None:
        """Replaces the data at the given address and size with the given data, marking the remaining space as empty."""

        if not isinstance(data, bytes):
            data = bytes(data)

        self.add_empty_space(address + len(data), length=length - len(data))
        self.dol_editor.write(address, data)

    def replace_instructions(
        self,
        address: MemoryAddress,
        instruction_count: int,
        *,
        instructions: Sequence[assembler.BaseInstruction],
        add_jump_at_end: bool,
    ) -> None:
        """
        Places the given instructions at the given address. Then marks the remaining space as empty.

        :param address: The address of the memory block to replace.
        :param instruction_count: How many instructions the block has. Not how many instructions it'll be.
        :param instructions:
        :param add_jump_at_end: If true, at the end of the given instructions add a jump
        """
        if add_jump_at_end:
            instructions = list(instructions)
            instructions.append(ppc.b(address + instruction_count * 4))

        assembled = bytes(assembler.assemble_instructions(address, instructions, symbols=self.dol_editor.symbols))
        self.replace_address(address, instruction_count * 4, assembled)

    def replace_symbol(self, symbol: str, instructions: Sequence[assembler.BaseInstruction]) -> None:
        """Replaces the code at the given symbol with the given instructions, marking the remaining space as empty."""

        address = self.dol_editor.resolve_symbol(symbol)
        assembled = bytes(assembler.assemble_instructions(address, instructions, symbols=self.dol_editor.symbols))
        self.replace_address(address, self._symbol_sizes[symbol], assembled)

    def request_data_cave(self, data: bytes, alignment: int, callback: Callable[[int], None]) -> None:
        """
        Creates a request for a block of memory with enough size to fit given bytes.
        :param data:
        :param alignment: What kind of alignment is required for this data.
        :param callback: A function to be called with the address of the allocated cave.
        :return:
        """

        @functools.wraps(callback)
        def wrap_callback(address: MemoryAddress) -> None:
            callback(address)
            logging.debug("Writing to %d: %s", address, data)
            self.dol_editor.write(address, data)

        self._requests.append(
            CaveRequest(
                size=len(data),
                alignment=alignment,
                callback=wrap_callback,
                created_at=tuple(traceback.extract_stack()[:-1]),
            )
        )

    def request_code_cave(
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

        @functools.wraps(callback)
        def wrap_callback(address: MemoryAddress) -> None:
            callback(address)
            logging.debug("Writing to %d: %s", address, instructions)
            self.dol_editor.write_instructions(address, instructions)

        self._requests.append(
            CaveRequest(
                size=assembler.byte_count(instructions),
                alignment=4,
                callback=wrap_callback,
                created_at=tuple(traceback.extract_stack()[:-1]),
            )
        )

    def fulfill_requests(self) -> None:
        """Fulfill all cave requests, using empty space registered."""

        self._requests.sort(key=lambda x: x.size)

        while self._requests:
            request = self._requests.pop()
            logging.debug(f"Fulfilling request: {request}")

            def _sort_section_for_alignment(s: Section) -> int:
                return s.length - (_align_address(s.start, request.alignment) - s.start)

            address = None
            self._sections.sort(key=_sort_section_for_alignment)

            for i, section in enumerate(self._sections):
                logging.debug(f"Inspecting section: {section}")

                adjusted_start = _align_address(section.start, request.alignment)
                adjustment = adjusted_start - section.start
                adjusted_length = section.length - adjustment

                if adjusted_length >= request.size:
                    self._sections.pop(i)
                    address = adjusted_start

                    if adjustment > 0:
                        self._sections.append(
                            Section(
                                start=section.start,
                                length=adjustment,
                                created_at=request.created_at,
                                derived_from=section,
                            )
                        )

                    if section.length > request.size + adjustment:
                        self._sections.append(
                            Section(
                                start=section.start + adjustment + request.size,
                                length=section.length - adjustment - request.size,
                                created_at=request.created_at,
                                derived_from=section,
                            )
                        )
                    break

            if address is None:
                raise ValueError(f"Unable to find a section to fulfill {request}.")

            request.callback(address)
