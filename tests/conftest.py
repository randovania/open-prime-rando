import hashlib
import json
import os
from pathlib import Path

import pytest
from retro_data_structures.file_provider import IsoFileProvider
from retro_data_structures.formats.ntwk import Ntwk
from retro_data_structures.game_check import Game

from open_prime_rando.patcher_editor import IsoFileWriter, PatcherEditor

_REPO_ROOT = Path(__file__).parent.parent
_DOT_ENV: dict[str, str] | None = None


def _load_dot_env() -> dict[str, str]:
    global _DOT_ENV  # noqa: PLW0603
    if _DOT_ENV is None:
        _DOT_ENV = {}
        dot_env_path = _REPO_ROOT / ".env"
        if dot_env_path.exists():
            for raw_line in dot_env_path.read_text().splitlines():
                stripped = raw_line.strip()
                if stripped and not stripped.startswith("#") and "=" in stripped:
                    key, _, value = stripped.partition("=")
                    _DOT_ENV[key.strip()] = value.strip()
    return _DOT_ENV


_FAIL_INSTEAD_OF_SKIP = True


class HashUtil:
    def hash_pak(self, contents: bytes) -> dict:
        result = {}

        from retro_data_structures.formats import Pak

        pak = Pak.parse(contents, target_game=Game.ECHOES)

        result["named_resources"] = {name: file.id for name, file in pak._raw.named_resources}

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

    def hash_iso_file_writer(self, output: IsoFileWriter) -> dict[str, str | dict]:
        result = {name: self.hash_file(name, contents.data) for name, contents in output._files.items()}
        if output._dol is not None:
            result["default.dol"] = self.hash_file("default.dol", output._dol)
        return result


@pytest.fixture(scope="session")
def hash_util():
    return HashUtil()


def get_env_or_skip(env_name: str, override_fail: bool | None = None) -> str:
    if override_fail is None:
        fail_or_skip = _FAIL_INSTEAD_OF_SKIP
    else:
        fail_or_skip = override_fail
    value = os.environ.get(env_name) or _load_dot_env().get(env_name)
    if value is None:
        if fail_or_skip:
            pytest.fail(f"Missing environment variable {env_name}")
        else:
            pytest.skip(f"Skipped due to missing environment variable {env_name}")
    return value


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
    editor._pak_strategy = {pak_name: editor._pak_strategy_factory(editor, pak_name) for pak_name in editor.all_paks}
    editor._custom_asset_ids = {}
    editor._modified_resources = {}
    with editor.provider.open_binary("Standard.ntwk") as f:
        editor.tweaks = Ntwk.parse(f.read(), Game.ECHOES)


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--skip-if-missing",
        action="store_false",
        dest="fail_if_missing",
        default=True,
        help="Skip tests instead of missing, in case any asset is missing",
    )
    parser.addoption(
        "--update-hashes",
        action="store_true",
        dest="update_hashes",
        default=False,
        help="Update hash files instead of comparing; only runs test_ntsc_export, test_pal_export, and test_ntsc_paks",
    )


def pytest_configure(config: pytest.Config) -> None:
    global _FAIL_INSTEAD_OF_SKIP  # noqa: PLW0603
    _FAIL_INSTEAD_OF_SKIP = config.option.fail_if_missing


def pytest_collection_modifyitems(config: pytest.Config, items: list) -> None:
    if not getattr(config.option, "update_hashes", False):
        return

    selected = [item for item in items if "update_hashes" in item.fixturenames]
    deselected = [item for item in items if "update_hashes" not in item.fixturenames]
    config.hook.pytest_deselected(items=deselected)
    items[:] = selected


@pytest.fixture(scope="session")
def update_hashes(request) -> bool:
    return bool(getattr(request.config.option, "update_hashes", False))
