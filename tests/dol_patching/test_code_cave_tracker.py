from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from ppc_asm.assembler import ppc

from open_prime_rando.dol_patching.code_cave_tracker import CodeCaveTracker

if TYPE_CHECKING:
    from ppc_asm.dol_file import DolEditor, DolFile


@pytest.fixture
def cave(dol_file: DolEditor) -> CodeCaveTracker:
    return CodeCaveTracker(dol_file)


def test_add_empty_cave_bad_args(cave: CodeCaveTracker) -> None:
    with pytest.raises(ValueError, match=r"'length' must be positive."):
        cave.add_empty_space(0, length=-1)


async def test_fulfill_requests_valid(dol_file: DolFile) -> None:
    callback1 = MagicMock()
    callback2 = MagicMock()

    dol_file.set_editable(True)
    cave = CodeCaveTracker(dol_file)

    async def work():
        cave.add_empty_space(0x2000, end=0x2001)
        cave.add_empty_space(0x2100, length=4)
        callback1(
            await cave.request_cave_for(
                [ppc.b(0, relative=True)],
            )
        )
        cave.add_empty_space(0x2104, length=4)
        callback2(
            await cave.request_cave_for(
                [ppc.b(0, relative=True)],
            )
        )

    cave.add_task(work())
    assert len(cave._sections) == 2

    with dol_file:
        await cave.fulfill_requests()

    callback1.assert_called_once_with(0x2100)
    callback2.assert_called_once_with(0x2104)
    assert len(cave._sections) == 1


async def test_fulfill_requests_no_section(cave: CodeCaveTracker) -> None:
    async def work():
        await cave.request_cave_for(
            [ppc.b(0, relative=True)],
        )

    cave.add_task(work())
    with pytest.raises(ValueError, match="Unable to find a section to fulfill"):
        await cave.fulfill_requests()
