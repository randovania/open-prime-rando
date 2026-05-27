from __future__ import annotations

import json
from typing import TYPE_CHECKING
from unittest.mock import ANY, MagicMock

from retro_data_structures.game_check import Game

from open_prime_rando.dol_patching.echoes import dol_versions
from open_prime_rando.echoes import legacy_patcher

if TYPE_CHECKING:
    from pathlib import Path

    import pytest_mock
    from conftest import HashUtil


def hash_all_paks(base_path: Path, hash_util: HashUtil) -> dict:
    result = {
        pak_path.relative_to(base_path).as_posix(): hash_util.hash_pak(pak_path.read_bytes())
        for pak_path in sorted(base_path.rglob("*.pak"))
    }
    path = base_path.joinpath("files/custom_names.json")
    result[path.relative_to(base_path).as_posix()] = json.loads(path.read_text())
    return result


def _update_hashes_file(path: Path, hashes: dict) -> None:
    path.write_text(json.dumps(hashes, indent=4))


def test_ntsc_paks(
    prime2_iso_provider,
    tmp_path,
    test_files_dir,
    hash_util: HashUtil,
    update_hashes: bool,
) -> None:
    output_path = tmp_path.joinpath("out")
    configuration = test_files_dir.read_json("echoes", "door_lock.json")

    legacy_patcher.patch_paks(
        file_provider=prime2_iso_provider,
        output_path=output_path,
        configuration=configuration,
    )
    hashes = hash_all_paks(output_path, hash_util)

    if update_hashes:
        _update_hashes_file(test_files_dir.joinpath("legacy_ntsc_hashes.json"), hashes)
    else:
        expected_hashes = test_files_dir.read_json("legacy_ntsc_hashes.json")
        assert hashes == expected_hashes


def test_pal_paks(pal_prime2_iso_provider, tmp_path, test_files_dir):
    output_path = tmp_path.joinpath("out")
    configuration = test_files_dir.read_json("echoes", "door_lock.json")

    legacy_patcher.patch_paks(
        file_provider=pal_prime2_iso_provider,
        output_path=output_path,
        configuration=configuration,
    )
    assert len(list(output_path.rglob("*.pak"))) == 10


def test_patch_dol(mocker: pytest_mock.MockerFixture):
    # Setup
    patches_data = MagicMock()
    version_patches = dol_versions.ALL_VERSIONS[0]
    mock_find_version_for_dol = mocker.patch(
        "open_prime_rando.dol_patching.dol_version.find_version_for_dol",
        return_value=version_patches,
        autospec=True,
    )
    dol_file = MagicMock()

    mock_apply_remote_exec = mocker.patch(
        "open_prime_rando.dol_patching.all_prime_dol_patches.apply_remote_execution_patch", autospec=True
    )
    mock_apply_etank_capacity: MagicMock = mocker.patch(
        "open_prime_rando.dol_patching.all_prime_dol_patches.apply_energy_tank_capacity_patch", autospec=True
    )

    mock_apply_game_options: MagicMock = mocker.patch(
        "open_prime_rando.dol_patching.echoes.game_options.apply_patch", autospec=True
    )
    mock_apply_beam_cost_patch: MagicMock = mocker.patch(
        "open_prime_rando.dol_patching.echoes.beam_cost.apply_patch", autospec=True
    )
    mock_apply_starting_visor_patch: MagicMock = mocker.patch(
        "open_prime_rando.dol_patching.echoes.dol_patches.apply_starting_visor_patch", autospec=True
    )
    mock_apply_fixes: MagicMock = mocker.patch(
        "open_prime_rando.dol_patching.echoes.dol_patches.apply_mandatory_fixes", autospec=True
    )
    mock_apply_unvisited_room_names: MagicMock = mocker.patch(
        "open_prime_rando.dol_patching.echoes.dol_patches.apply_unvisited_room_names", autospec=True
    )
    mock_apply_teleporter_sounds: MagicMock = mocker.patch(
        "open_prime_rando.dol_patching.echoes.dol_patches.apply_teleporter_sounds", autospec=True
    )

    # Run
    legacy_patcher.patch_dol(dol_file, patches_data)

    # Assert
    mock_find_version_for_dol.assert_called_once_with(dol_file, dol_versions.ALL_VERSIONS)
    mock_apply_remote_exec.assert_called_once_with(Game.ECHOES, version_patches.string_display, dol_file)
    mock_apply_game_options.assert_called_once_with(
        version_patches.game_options_constructor_address, dol_file, patches_data.game_options_defaults
    )
    mock_apply_etank_capacity.assert_called_once_with(
        version_patches.health_capacity, patches_data.energy_per_tank, dol_file
    )
    mock_apply_beam_cost_patch.assert_called_once_with(
        version_patches.beam_cost_addresses, dol_file, patches_data.beam_configuration
    )
    mock_apply_starting_visor_patch.assert_called_once_with(
        version_patches.starting_beam_visor,
        patches_data.default_items,
        dol_file,
    )
    mock_apply_fixes.assert_called_once_with(version_patches, ANY)
    mock_apply_unvisited_room_names.assert_called_once_with(
        version_patches, dol_file, patches_data.unvisited_room_names
    )
    mock_apply_teleporter_sounds.assert_called_once_with(version_patches, dol_file, patches_data.teleporter_sounds)
