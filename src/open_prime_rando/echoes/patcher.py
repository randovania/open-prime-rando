from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from retro_data_structures.asset_manager import IsoFileProvider
from retro_data_structures.game_check import Game

from open_prime_rando.patcher_editor import PatcherEditor

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

LOG = logging.getLogger("echoes_patcher")


def patch_iso(
    input_iso: Path,
    output_iso: Path,
    configuration: dict,
    status_update: Callable[[str, float], None] = lambda s, _: LOG.info(s),
) -> None:
    """

    :param input_iso:
    :param output_iso:
    :param configuration:
    :param status_update:
    :return:
    """
    file_provider = IsoFileProvider(input_iso)
    editor = PatcherEditor(file_provider, Game.ECHOES)

    # Save our changes
    editor.flush_modified_assets()
