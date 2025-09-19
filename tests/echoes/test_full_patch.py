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
            "files/AudioGrp.pak": b"U\xc6\xfe\\\xac\xcd\xdc\x02\x0c\xed\xdd\xb3\xfarbP"
            b"\x90\xac\x8d\x1b=\xd4\x9fl\x82\xc8\x12\xd2\x85X{+",
            "files/LogBook.pak": b'\x05\xdf2\xb5\xf4\xe5\xce\xa3"\tk_\x91\x05\xe9\xa9'
            b"\xab\x8c.\x9c\xe0\xee\x89\xb7\x04\xa1\x7fI\x0bU,\xb4",
            "files/Metroid1.pak": b"\x14\x1fu\x02\x91\xd3\xdb\xe4\xf7\xd8`\xdb\xf2\x81\xd1K\x8fD:\xae"
            b"V\xe4\xe5'\x98sH\xa7\xbew\x92\x1a",
            "files/Metroid2.pak": b"13\x88\xafA\x01\xbe\xca7\x90\xf0X\xe7\xa1\xa6~\xd9Z%M\xa715$X\x12\x9f\xe3"
            b"\x92\xddi\xe0",
            "files/Metroid3.pak": b"\xf9U\x18g\xff\xf0\xc7?\xfeo\xea\xb0\x90 \xcdM\x05}\xf0\xc2"
            b"\x89\x8f\xf2\x00\xf0\xe4\xc2\xa5{\xf0(\x02",
            "files/Metroid4.pak": b'\xe0\xac\xf6\x1b\xec .\xe1Ak\xf2\xf3\xfdl\xe7\xe5s\xceY31"\x9c0}I\x98\x10'
            b"v\xb4\x86\x02",
            "files/Metroid5.pak": b"@\x12\x91[\x1e\xa9\x9fP5$@\x91h\xde\x9dI\xee\xf1^\x99C\xdf\xcc\x84!2\xfc/"
            b"l.\x0f\xd8",
            "files/MiscData.pak": b"\x97\x04\xb2\xd0\xadA\x8c:\xc5[\xfe\xfc\xd02\xa3\xf24\x9bh\x12"
            b"\xf3\x05g\xbenS\xc4}\x9ch\xad\xab",
            "files/SamusGun.pak": b"\xdd\xa99\x0b\x14b\x97&\xee\xdf\nE\xd0GR`c\x85\xf7m;\xdbX^\xe4\x87;\\?\xc9\x08\x1f",
            "files/SamusGunLow.pak": b"o8\xb8\xab^\xc3y\xc7\xd8v\xf1?\xe7a\x9enIE\xb7\xa5"
            b"q\x9f\xa2\xf6\xc2\xc6m&\x80G\x8f\x83",
            "files/TestAnim.pak": b"\xc0n\xfa2\x87\x96o\xd9\xf8\nL\xc8\xd5vVJi\xe2\xa0\xdb"
            b"\xdbq\t\x7f\xaf\x96\x8d\x02\x1f\xe7\x07\x12",
        },
        True: {
            "files/AudioGrp.pak": b"U\xc6\xfe\\\xac\xcd\xdc\x02\x0c\xed\xdd\xb3\xfarbP"
            b"\x90\xac\x8d\x1b=\xd4\x9fl\x82\xc8\x12\xd2\x85X{+",
            "files/LogBook.pak": b"K=z\x02\x9c>\x8a\xfbN\xbe\xb6\xb5\xc8\xad\xba\xb8"
            b"\x99\xae\x85_\xab55\xfe3\x15\x0b\xdc\xd1\xc7\x02^",
            "files/Metroid1.pak": b"\x14\xb9E\xb2\xdf\xec(E\x86\xa2\xff\x9dI\xdcCS\x9b\x90\xa0\x9do\xc1\xf1R"
            b"\x89\x1e\xc6\x94\xabk\x82\x1e",
            "files/Metroid2.pak": b"T\xfe\xb4\xa4SW\xbb\xfe\xb9\xd4p\xe5\x84\\GK\x93\xb6\xb6}\xf3\xda \x00"
            b'\x86ff"3q\xb0\xb6',
            "files/Metroid3.pak": b"\xf8\xf0\xbcFq\x83\xceB\xbfJ\xecY\xea\xbc\xf3\x1bQ\x19\x7f\xef\xe6\xfdi\n"
            b"\x93=PO\xbeC\xd6\xac",
            "files/Metroid4.pak": b"GR\xaf\xd0\x8bj1,\x1c\x94a\xbf\x91bY\x99\xac\xac0>\xae\x9f\x81\xcb"
            b"wT\xbd\xdfDo\x90\xa3",
            "files/Metroid5.pak": b"\xfb\xb6H\x1e\xbc\x93Q\nX\xeb\x14\xe2W4+\x85O\xef\x0c=\x08\xf9\x85\x17"
            b"}\x96\xdf\xa4\x9e!(\xab",
            "files/MiscData.pak": b"\x97\x04\xb2\xd0\xadA\x8c:\xc5[\xfe\xfc\xd02\xa3\xf24\x9bh\x12"
            b"\xf3\x05g\xbenS\xc4}\x9ch\xad\xab",
            "files/SamusGun.pak": b"\xdd\xa99\x0b\x14b\x97&\xee\xdf\nE\xd0GR`c\x85\xf7m;\xdbX^\xe4\x87;\\?\xc9\x08\x1f",
            "files/SamusGunLow.pak": b"o8\xb8\xab^\xc3y\xc7\xd8v\xf1?\xe7a\x9enIE\xb7\xa5"
            b"q\x9f\xa2\xf6\xc2\xc6m&\x80G\x8f\x83",
            "files/TestAnim.pak": b"\xc0n\xfa2\x87\x96o\xd9\xf8\nL\xc8\xd5vVJi\xe2\xa0\xdb"
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
