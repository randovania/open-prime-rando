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


def test_fulfill_requests_valid(dol_file: DolFile) -> None:
    callback = MagicMock()

    dol_file.set_editable(True)
    cave = CodeCaveTracker(dol_file)
    cave.add_empty_space(0x2000, end=0x2001)
    section = cave._sections[0]
    cave.add_empty_space(0x2100, length=4)

    cave.request_cave_for(
        [ppc.b(0, relative=True)],
        callback,
    )
    with dol_file:
        cave.fulfill_requests()

    callback.assert_called_once_with(0x2100)
    assert cave._sections == [section]


def test_fulfill_requests_no_section(cave: CodeCaveTracker) -> None:
    cave.request_cave_for(
        [ppc.b(0, relative=True)],
        MagicMock(),
    )
    with pytest.raises(ValueError, match="Unable to find a section to fulfill"):
        cave.fulfill_requests()
