import hashlib
from pathlib import Path

import pytest

from open_prime_rando.echoes import legacy_patcher


@pytest.fixture(
    params=[False, True],
)
def is_legacy(request: pytest.FixtureRequest) -> bool:
    return request.param


def hash_all_paks(base_path: Path) -> dict[str, bytes]:
    return {
        pak_path.relative_to(base_path).as_posix(): hashlib.sha256(pak_path.read_bytes()).digest()
        for pak_path in base_path.rglob("*.pak")
    }


def test_ntsc_paks(prime2_iso_provider, tmp_path, test_files_dir) -> None:
    output_path = tmp_path.joinpath("out")
    configuration = test_files_dir.read_json("echoes", "door_lock.json")

    expected_hashes = {
        "files/AudioGrp.pak": b"U\xc6\xfe\\\xac\xcd\xdc\x02\x0c\xed\xdd\xb3\xfarbP"
        b"\x90\xac\x8d\x1b=\xd4\x9fl\x82\xc8\x12\xd2\x85X{+",
        "files/LogBook.pak": b"K=z\x02\x9c>\x8a\xfbN\xbe\xb6\xb5\xc8\xad\xba\xb8"
        b"\x99\xae\x85_\xab55\xfe3\x15\x0b\xdc\xd1\xc7\x02^",
        "files/Metroid1.pak": b"\xde\xfb\x02\xfb{\xbc\xc5\xe4\x81\x8e_.>02\n"
        b"\xa1\xc0\xcc\xb5\x91\x7f\xb4\xf3t4\xfbU\xf8\x95|v",
        "files/Metroid2.pak": b'\xbdn\x83\xc6\x0c$)}\nv\xd1q"\x85\xa4\xc1\x99\xaa\xed\xc49-\xab\x08'
        b"\xf0\xef\xfa:\xc3]\xe8\xe3",
        "files/Metroid3.pak": b"\xab\xacT\xe2\xad\x03\xa3\xbecO#Ew!\x02\xfb\xec\x0eB\x13\xa4\x8b\xc96"
        b"\n\xb4\x16\x99\xeeC\xdbr",
        "files/Metroid4.pak": b"\xb3\xa1\xc3\xe0\x1d\xbdB\x7f\x96H\xa7_\xb8\x0e\xb2d\xe8\xe3\xde\xd6"
        b'#\x91L\xfaTI]"U\xd5\xea0',
        "files/Metroid5.pak": b"n\xee4\xb3\xd5\x1b\xcd\x00J\x05\x91'zr\x04\xeat\"\xc7\x87\x81)3\xce6\xcbPJE\xe9\xa2!",
        "files/MiscData.pak": b"'\xbd\x82\x84\xdf\xf0\x88\x1d\xda\xe0|{\xafo\x80\xd5\xbc\xe4xR"
        b"\xb4W\xdb\x1eT\x00@\xba{m`]",
        "files/SamusGun.pak": b"\xdd\xa99\x0b\x14b\x97&\xee\xdf\nE\xd0GR`c\x85\xf7m;\xdbX^\xe4\x87;\\?\xc9\x08\x1f",
        "files/SamusGunLow.pak": b"o8\xb8\xab^\xc3y\xc7\xd8v\xf1?\xe7a\x9enIE\xb7\xa5"
        b"q\x9f\xa2\xf6\xc2\xc6m&\x80G\x8f\x83",
        "files/TestAnim.pak": b"\xc0n\xfa2\x87\x96o\xd9\xf8\nL\xc8\xd5vVJi\xe2\xa0\xdb"
        b"\xdbq\t\x7f\xaf\x96\x8d\x02\x1f\xe7\x07\x12",
    }

    legacy_patcher.patch_paks(
        file_provider=prime2_iso_provider,
        output_path=output_path,
        configuration=configuration,
    )
    hashes = hash_all_paks(output_path)
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
