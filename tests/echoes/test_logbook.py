from __future__ import annotations

from typing import TYPE_CHECKING

from open_prime_rando.dol_patching.echoes import dol_versions
from open_prime_rando.echoes import logbook

if TYPE_CHECKING:
    from open_prime_rando.patcher_editor import PatcherEditor


def test_patch_logbook(prime2_editor: PatcherEditor) -> None:
    logbook.patch_logbook(prime2_editor, dol_versions.ALL_VERSIONS[0])
