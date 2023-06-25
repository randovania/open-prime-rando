import os
from pathlib import Path

import pytest
from retro_data_structures.asset_manager import IsoFileProvider
from retro_data_structures.game_check import Game

from open_prime_rando.patcher_editor import PatcherEditor

_FAIL_INSTEAD_OF_SKIP = True


def get_env_or_skip(env_name):
    if env_name not in os.environ:
        if _FAIL_INSTEAD_OF_SKIP:
            pytest.fail(f"Missing environment variable {env_name}")
        else:
            pytest.skip(f"Skipped due to missing environment variable {env_name}")
    return os.environ[env_name]


@pytest.fixture(scope="module")
def prime2_iso_provider():
    return IsoFileProvider(Path(get_env_or_skip("PRIME2_ISO")))


@pytest.fixture(scope="module")
def raw_prime2_editor(prime2_iso_provider):
    return PatcherEditor(prime2_iso_provider, game=Game.ECHOES)


@pytest.fixture()
def prime2_editor(raw_prime2_editor):
    editor = raw_prime2_editor
    yield editor
    editor.memory_files = {}
    for custom_asset, asset_id in editor._custom_asset_ids.items():
        editor._paks_for_asset_id.pop(asset_id)
    editor._custom_asset_ids = {}
    editor._modified_resources = {}


def pytest_addoption(parser):
    parser.addoption('--skip-if-missing', action='store_false', dest="fail_if_missing",
                     default=True, help="Skip tests instead of missing, in case any asset is missing")


def pytest_configure(config: pytest.Config):
    global _FAIL_INSTEAD_OF_SKIP
    _FAIL_INSTEAD_OF_SKIP = config.option.fail_if_missing
