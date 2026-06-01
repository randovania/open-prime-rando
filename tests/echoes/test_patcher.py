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


def _no_status_update(s: str, p: float) -> None:
    pass


def test_ntsc_export(
    prime2_ntsc_iso_path,
    configuration,
    test_files_dir,
    hash_util: HashUtil,
    update_hashes: bool,
) -> None:
    file_provider = IsoFileProvider(prime2_ntsc_iso_path)
    editor = PatcherEditor(file_provider, Game.ECHOES)
    output = IsoFileWriter(file_provider)

    # Run
    patcher._apply_patches(
        editor,
        configuration,
        output,
        _no_status_update,
        _no_status_update,
        _no_status_update,
    )

    # Assert
    hashes = hash_util.hash_iso_file_writer(output)

    if update_hashes:
        _update_hashes_file(test_files_dir.joinpath("ntsc_hashes.json"), hashes)
    else:
        expected_hashes = test_files_dir.read_json("ntsc_hashes.json")
        assert hashes == expected_hashes


def test_pal_export(
    prime2_pal_iso_path,
    configuration,
    test_files_dir,
    hash_util: HashUtil,
    update_hashes: bool,
) -> None:
    configuration.practice_mod = PracticeModMode.disabled

    file_provider = IsoFileProvider(prime2_pal_iso_path)
    editor = PatcherEditor(file_provider, Game.ECHOES)
    output = IsoFileWriter(file_provider)

    # Run
    patcher._apply_patches(
        editor,
        configuration,
        output,
        _no_status_update,
        _no_status_update,
        _no_status_update,
    )

    # Assert
    hashes = hash_util.hash_iso_file_writer(output)

    if update_hashes:
        _update_hashes_file(test_files_dir.joinpath("pal_hashes.json"), hashes)
    else:
        expected_hashes = test_files_dir.read_json("pal_hashes.json")
        assert hashes == expected_hashes
