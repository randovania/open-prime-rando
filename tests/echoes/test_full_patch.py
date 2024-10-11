import hashlib
from pathlib import Path

import pytest

from open_prime_rando import echoes_patcher


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


def test_ntsc_paks(prime2_iso_provider, tmp_path, test_files_dir, is_legacy: bool) -> None:
    output_path = tmp_path.joinpath("out")
    configuration = test_files_dir.read_json("echoes", "door_lock.json")
    configuration["legacy_compatibility"] = is_legacy

    expected_hashes = {
        False: {
            "AudioGrp.pak": b"U\xc6\xfe\\\xac\xcd\xdc\x02\x0c\xed\xdd\xb3\xfarbP"
            b"\x90\xac\x8d\x1b=\xd4\x9fl\x82\xc8\x12\xd2\x85X{+",
            "LogBook.pak": b'\x05\xdf2\xb5\xf4\xe5\xce\xa3"\tk_\x91\x05\xe9\xa9'
            b"\xab\x8c.\x9c\xe0\xee\x89\xb7\x04\xa1\x7fI\x0bU,\xb4",
            "Metroid1.pak": b"\x11%\x80\xe4t\x9e?\x1d\xaa\xf2\xc9\xc3\x1d&\xa6v\xfc?E\xcf"
            b'\xc4\x06\x13\x83"A#\xfb\xa1\x84\xcf\xca',
            "Metroid2.pak": b"\x96lH\x85\xae\xddX\xceo\xd1\x0cfnk\xbex\xaa\x94Y\x08"
            b"\x05\\-\xf9?\xa4\x9a]\xa8\x0ez\x93",
            "Metroid3.pak": b"\xe8\xee\x80\xf6\\\xd5\x1c4\xf5\x1b\xe1*\xfbY\x9a\xe0"
            b"\x8c\xb9\xd1\xe0(\x96\xb4R-\xe0\xf1\x86y\x88T\xa9",
            "Metroid4.pak": b"\xce\xc5\x838\x19q\xd0\xf7\xf4\x86hQ\xb3\xf5\xf5p\xf9\xd3}8"
            b"\xfemx\xb5x\tQ\xf8\xc6\xdc.\xb6",
            "Metroid5.pak": b"\xa9n\xb5\xf5\x04U\x13\xc0 \xcf\xcfe\x11\xbd\x04\xad"
            b"c\xd2\xc6\x8b\xb4\xc5\xc0\xd0P \xb1f\xf1\xdc\x90T",
            "MiscData.pak": b"\x0bM\xedR\xb7+\xaf+#\x06\x87\x88\xe5\xec\xbbxg@i\xbc"
            b"\xa3n\xb1\xabi\xfajb\x00\xf3\xd1\xaa",
            "SamusGun.pak": b"\xdd\xa99\x0b\x14b\x97&\xee\xdf\nE\xd0GR`c\x85\xf7m;\xdbX^" b"\xe4\x87;\\?\xc9\x08\x1f",
            "SamusGunLow.pak": b"o8\xb8\xab^\xc3y\xc7\xd8v\xf1?\xe7a\x9enIE\xb7\xa5"
            b"q\x9f\xa2\xf6\xc2\xc6m&\x80G\x8f\x83",
            "TestAnim.pak": b"\xc0n\xfa2\x87\x96o\xd9\xf8\nL\xc8\xd5vVJi\xe2\xa0\xdb"
            b"\xdbq\t\x7f\xaf\x96\x8d\x02\x1f\xe7\x07\x12",
        },
        True: {
            "AudioGrp.pak": b"U\xc6\xfe\\\xac\xcd\xdc\x02\x0c\xed\xdd\xb3\xfarbP"
            b"\x90\xac\x8d\x1b=\xd4\x9fl\x82\xc8\x12\xd2\x85X{+",
            "LogBook.pak": b"K=z\x02\x9c>\x8a\xfbN\xbe\xb6\xb5\xc8\xad\xba\xb8"
            b"\x99\xae\x85_\xab55\xfe3\x15\x0b\xdc\xd1\xc7\x02^",
            "Metroid1.pak": b"7\x18\xe7+\xdbR\xbf6\x0e\xa2=\x8b\xc8\xcc\x98-"
            b"\x8f\xdc\xe5\x8d\x17\xedz\xf9c\xe1\xd5\xfc\xf2\x18\xf2$",
            "Metroid2.pak": b"U\x9b\xa7;\xbf\xad\xac\xf7\x05\xe9hKC\xcd\xa5\x0f"
            b"\xc9C\xc7\xf2\xe7A$\xcc\x1c&0A\xcb\xaa(\xf1",
            "Metroid3.pak": b"\xeaO\x17\x0e\xaa\xbd\xaa\xabJvO\x9d\x08\x15Y\xca"
            b"\xe7\x97z\x0c\xcb\xf6],\xf9\xfa\xee*\x17\xc2\xf6(",
            "Metroid4.pak": b"9\xc2\x87\x91\x91%\x82\x0f>\x7f;Q\xacLP\xca-\xb6\xc1\x1b"
            b"+\xc7\xecy{\xc0\x12\x19\xa7\x04\x7ft",
            "Metroid5.pak": b"\xaf\xfe\xec3<ofO\xd4\x0ci&\x96>\xf1\xfeh\xbb\x05\x00"
            b"\xb5\x0fP\xd7\xa2\xf0\xb9\x81\xa7\xa1\x84\xbe",
            "MiscData.pak": b"\x0bM\xedR\xb7+\xaf+#\x06\x87\x88\xe5\xec\xbbxg@i\xbc"
            b"\xa3n\xb1\xabi\xfajb\x00\xf3\xd1\xaa",
            "SamusGun.pak": b"\xdd\xa99\x0b\x14b\x97&\xee\xdf\nE\xd0GR`c\x85\xf7m;\xdbX^" b"\xe4\x87;\\?\xc9\x08\x1f",
            "SamusGunLow.pak": b"o8\xb8\xab^\xc3y\xc7\xd8v\xf1?\xe7a\x9enIE\xb7\xa5"
            b"q\x9f\xa2\xf6\xc2\xc6m&\x80G\x8f\x83",
            "TestAnim.pak": b"\xc0n\xfa2\x87\x96o\xd9\xf8\nL\xc8\xd5vVJi\xe2\xa0\xdb"
            b"\xdbq\t\x7f\xaf\x96\x8d\x02\x1f\xe7\x07\x12",
        },
    }

    echoes_patcher.patch_paks(
        file_provider=prime2_iso_provider,
        output_path=output_path,
        configuration=configuration,
    )
    hashes = hash_all_paks(output_path)
    assert hashes == expected_hashes[is_legacy]


def test_pal_paks(pal_prime2_iso_provider, tmp_path, test_files_dir):
    output_path = tmp_path.joinpath("out")
    configuration = test_files_dir.read_json("echoes", "door_lock.json")

    echoes_patcher.patch_paks(
        file_provider=pal_prime2_iso_provider,
        output_path=output_path,
        configuration=configuration,
    )
    assert len(list(output_path.rglob("*.pak"))) == 11
