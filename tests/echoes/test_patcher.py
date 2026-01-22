import pytest

from open_prime_rando.echoes import patcher
from open_prime_rando.echoes.rando_configuration import RandoConfiguration


@pytest.fixture
def configuration(test_files_dir):
    data = test_files_dir.joinpath("echoes", "new_patcher.json").read_text()
    return RandoConfiguration.model_validate_json(data)


def test_ntsc_export(prime2_ntsc_iso_path, tmp_path, configuration) -> None:
    patcher.patch_iso(prime2_ntsc_iso_path, tmp_path, configuration)


def test_pal_export(prime2_pal_iso_path, tmp_path, configuration) -> None:
    patcher.patch_iso(prime2_pal_iso_path, tmp_path, configuration)
