import hashlib
import json
import os
from pathlib import Path

import pytest
from retro_data_structures.asset_manager import IsoFileProvider
from retro_data_structures.game_check import Game

from open_prime_rando.patcher_editor import PatcherEditor

_FAIL_INSTEAD_OF_SKIP = True


class HashUtil:
    def hash_pak(self, contents: bytes) -> dict:
        result = {}

        from retro_data_structures.formats import Pak

        pak = Pak.parse(contents, target_game=Game.ECHOES)

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

    def hash_file(self, name: str, contents: str | bytes) -> str | dict:
        if isinstance(contents, str):
            contents = contents.encode("utf-8")

        if name.endswith(".pak"):
            return self.hash_pak(contents)

        if name.endswith(".json"):
            return json.loads(contents)

        return hashlib.sha256(contents).hexdigest()


@pytest.fixture(scope="session")
def hash_util():
    return HashUtil()


def get_env_or_skip(env_name: str, override_fail: bool | None = None) -> str:
    if override_fail is None:
        fail_or_skip = _FAIL_INSTEAD_OF_SKIP
    else:
        fail_or_skip = override_fail
    if env_name not in os.environ:
        if fail_or_skip:
            pytest.fail(f"Missing environment variable {env_name}")
        else:
            pytest.skip(f"Skipped due to missing environment variable {env_name}")
    return os.environ[env_name]


class TestFilesDir:
    def __init__(self, root: Path):
        self.root = root

    def joinpath(self, *paths) -> Path:
        return self.root.joinpath(*paths)

    def read_json(self, *paths) -> dict | list:
        with self.joinpath(*paths).open() as f:
            return json.load(f)


@pytest.fixture(scope="session")
def test_files_dir() -> TestFilesDir:
    return TestFilesDir(Path(__file__).parent.joinpath("test_files"))


@pytest.fixture(scope="module")
def prime2_ntsc_iso_path() -> Path:
    return Path(get_env_or_skip("PRIME2_ISO"))


@pytest.fixture(scope="module")
def prime2_pal_iso_path() -> Path:
    return Path(get_env_or_skip("PRIME2_PAL_ISO", override_fail=False))


@pytest.fixture(scope="module")
def prime2_iso_provider(prime2_ntsc_iso_path) -> IsoFileProvider:
    return IsoFileProvider(prime2_ntsc_iso_path)


@pytest.fixture(scope="module")
def pal_prime2_iso_provider(prime2_pal_iso_path) -> IsoFileProvider:
    return IsoFileProvider(prime2_pal_iso_path)


@pytest.fixture(scope="module")
def raw_prime2_editor(prime2_iso_provider: IsoFileProvider) -> PatcherEditor:
    return PatcherEditor(prime2_iso_provider, target_game=Game.ECHOES)


@pytest.fixture
def prime2_editor(raw_prime2_editor: PatcherEditor):
    editor = raw_prime2_editor
    yield editor
    editor._memory_files = {}
    for custom_asset, asset_id in editor._custom_asset_ids.items():
        editor._paks_for_asset_id.pop(asset_id)
    editor._custom_asset_ids = {}
    editor._modified_resources = {}


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--skip-if-missing",
        action="store_false",
        dest="fail_if_missing",
        default=True,
        help="Skip tests instead of missing, in case any asset is missing",
    )


def pytest_configure(config: pytest.Config) -> None:
    global _FAIL_INSTEAD_OF_SKIP  # noqa: PLW0603
    _FAIL_INSTEAD_OF_SKIP = config.option.fail_if_missing
