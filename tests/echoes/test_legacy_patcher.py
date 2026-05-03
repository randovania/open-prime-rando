from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from open_prime_rando.echoes import legacy_patcher

if TYPE_CHECKING:
    from pathlib import Path

    from conftest import HashUtil


def hash_all_paks(base_path: Path, hash_util: HashUtil) -> dict[str, dict]:
    return {
        pak_path.relative_to(base_path).as_posix(): hash_util.hash_pak(pak_path.read_bytes())
        for pak_path in base_path.rglob("*.pak")
    }


def _update_hashes_file(path: Path, hashes: dict[str, dict]) -> None:
    path.write_text(json.dumps(hashes, indent=4))
    pytest.fail("updated hashes file")


def test_ntsc_paks(prime2_iso_provider, tmp_path, test_files_dir, hash_util: HashUtil) -> None:
    output_path = tmp_path.joinpath("out")
    configuration = test_files_dir.read_json("echoes", "door_lock.json")

    expected_hashes = test_files_dir.read_json("legacy_ntsc_hashes.json")

    legacy_patcher.patch_paks(
        file_provider=prime2_iso_provider,
        output_path=output_path,
        configuration=configuration,
    )
    hashes = hash_all_paks(output_path, hash_util)

    # _update_hashes_file(test_files_dir.joinpath("legacy_ntsc_hashes.json"), hashes)

    assert hashes == expected_hashes


def test_pal_paks(pal_prime2_iso_provider, tmp_path, test_files_dir):
    output_path = tmp_path.joinpath("out")
    configuration = test_files_dir.read_json("echoes", "door_lock.json")

    legacy_patcher.patch_paks(
        file_provider=pal_prime2_iso_provider,
        output_path=output_path,
        configuration=configuration,
    )
    assert len(list(output_path.rglob("*.pak"))) == 11
