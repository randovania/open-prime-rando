from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from retro_data_structures.game_check import Game

from open_prime_rando.echoes import patcher
from open_prime_rando.echoes.rando_configuration import PracticeModMode, RandoConfiguration
from open_prime_rando.patcher_editor import IsoFileProvider, IsoFileWriter, PatcherEditor

if TYPE_CHECKING:
    from pathlib import Path

    from conftest import HashUtil


@pytest.fixture
def configuration(test_files_dir):
    data = test_files_dir.joinpath("echoes", "new_patcher.json").read_text()
    return RandoConfiguration.model_validate_json(data)


def _update_hashes_file(path: Path, hashes: dict[str, str | dict]) -> None:
    path.write_text(json.dumps(hashes, indent=4, sort_keys=True))
    pytest.fail("updated hashes file")


def test_ntsc_export(prime2_ntsc_iso_path, tmp_path, configuration, test_files_dir, hash_util: HashUtil) -> None:
    file_provider = IsoFileProvider(prime2_ntsc_iso_path)
    editor = PatcherEditor(file_provider, Game.ECHOES)
    output = IsoFileWriter(file_provider)

    expected_hashes = test_files_dir.read_json("ntsc_hashes.json")

    # Run
    patcher._apply_patches(editor, configuration, output)

    # Assert
    hashes = {name: hash_util.hash_file(name, contents.data) for name, contents in output._files.items()}

    # _update_hashes_file(test_files_dir.joinpath("ntsc_hashes.json"), hashes)

    assert hashes == expected_hashes


def test_pal_export(prime2_pal_iso_path, tmp_path, configuration, test_files_dir, hash_util: HashUtil) -> None:
    configuration.practice_mod = PracticeModMode.disabled

    file_provider = IsoFileProvider(prime2_pal_iso_path)
    editor = PatcherEditor(file_provider, Game.ECHOES)
    output = IsoFileWriter(file_provider)

    expected_hashes = test_files_dir.read_json("pal_hashes.json")

    # Run
    patcher._apply_patches(editor, configuration, output)

    # Assert
    hashes = {name: hash_util.hash_file(name, contents.data) for name, contents in output._files.items()}

    # _update_hashes_file(test_files_dir.joinpath("pal_hashes.json"), hashes)

    assert hashes == expected_hashes
