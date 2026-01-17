from open_prime_rando.echoes import patcher
from open_prime_rando.echoes.rando_configuration import RandoConfiguration


def test_ntsc_export(prime2_ntsc_iso_path, tmp_path) -> None:
    patcher.patch_iso(prime2_ntsc_iso_path, tmp_path, RandoConfiguration())


def test_pal_export(prime2_pal_iso_path, tmp_path) -> None:
    patcher.patch_iso(prime2_pal_iso_path, tmp_path, RandoConfiguration())
