from open_prime_rando.echoes import patcher


def test_ntsc_export(prime2_ntsc_iso_path, tmp_path) -> None:
    patcher.patch_iso(prime2_ntsc_iso_path, tmp_path, {})


def test_pal_export(prime2_pal_iso_path, tmp_path) -> None:
    patcher.patch_iso(prime2_pal_iso_path, tmp_path, {})
