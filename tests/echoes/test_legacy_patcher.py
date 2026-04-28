import hashlib
import json
from pathlib import Path

from retro_data_structures.formats import Pak
from retro_data_structures.game_check import Game

from open_prime_rando.echoes import legacy_patcher


def _hash_pak(pak_path: Path) -> dict[str, bytes]:
    result = {}

    with pak_path.open("rb") as f:
        pak = Pak.parse_stream(f, target_game=Game.ECHOES)

        result["named_resources"] = {name: file.id for name, file in pak._raw.named_resources.items()}

        result["files"] = files = {}
        for asset in pak._raw.files:
            if asset.compressed_data is not None:
                data = "c_" + hashlib.sha256(asset.compressed_data).hexdigest()
            else:
                assert asset.uncompressed_data is not None
                data = hashlib.sha256(asset.uncompressed_data).hexdigest()
            files[f"{asset.asset_type}_{asset.asset_id:08x}"] = data

    return result


def hash_all_paks(base_path: Path) -> dict[str, dict]:
    return {pak_path.relative_to(base_path).as_posix(): _hash_pak(pak_path) for pak_path in base_path.rglob("*.pak")}


def test_ntsc_paks(prime2_iso_provider, tmp_path, test_files_dir) -> None:
    output_path = tmp_path.joinpath("out")
    configuration = test_files_dir.read_json("echoes", "door_lock.json")

    expected_hashes = test_files_dir.read_json("legacy_ntsc_hashes.json")

    legacy_patcher.patch_paks(
        file_provider=prime2_iso_provider,
        output_path=output_path,
        configuration=configuration,
    )
    hashes = hash_all_paks(output_path)

    test_files_dir.joinpath("legacy_ntsc_hashes.json").write_text(json.dumps(hashes, indent=4))

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
