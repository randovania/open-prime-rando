import os
from pathlib import Path

import pytest
from retro_data_structures.asset_manager import IsoFileProvider
from retro_data_structures.game_check import Game

from open_prime_rando.patcher_editor import PatcherEditor

_FAIL_INSTEAD_OF_SKIP = False


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
def prime2_editor(prime2_iso_provider):
    return PatcherEditor(prime2_iso_provider, game=Game.ECHOES)


def pytest_addoption(parser):
    parser.addoption('--fail-if-missing', action='store_true', dest="fail_if_missing",
                     default=False, help="Fails tests instead of skipping, in case any asset is missing")


def pytest_configure(config: pytest.Config):
    global _FAIL_INSTEAD_OF_SKIP
    _FAIL_INSTEAD_OF_SKIP = config.option.fail_if_missing
