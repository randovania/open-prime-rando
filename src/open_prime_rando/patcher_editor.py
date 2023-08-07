import contextlib
import io
import typing
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ppc_asm.dol_file import DolEditor, DolHeader
from retro_data_structures.asset_manager import AssetManager, FileProvider
from retro_data_structures.base_resource import AssetId, BaseResource, NameOrAssetId
from retro_data_structures.formats.mlvl import Mlvl
from retro_data_structures.formats.mrea import Area
from retro_data_structures.formats.strg import Strg
from retro_data_structures.game_check import Game

T = typing.TypeVar("T")


class MemoryDol(DolEditor):
    def __init__(self, dol: bytes):
        super().__init__(DolHeader.from_bytes(dol))
        self.dol_file = io.BytesIO(dol)

    def _seek_and_read(self, seek: int, size: int):
        self.dol_file.seek(seek)
        return self.dol_file.read(size)

    def _seek_and_write(self, seek: int, data: bytes):
        self.dol_file.seek(seek)
        self.dol_file.write(data)


class PatcherEditor(AssetManager):
    memory_files: dict[NameOrAssetId, BaseResource]

    def __init__(self, provider: FileProvider, game: Game):
        super().__init__(provider, game)
        self.memory_files = {}

        if game in [Game.PRIME, Game.ECHOES]:
            self.dol = MemoryDol(provider.get_dol())
        else:
            self.dol = None

    def get_file(self, path: NameOrAssetId, type_hint: type[T] = BaseResource) -> T:
        if path not in self.memory_files:
            self.memory_files[path] = self.get_parsed_asset(path, type_hint=type_hint)
        return self.memory_files[path]

    @contextlib.contextmanager
    def edit_file(self, asset_id: NameOrAssetId, type_hint: type[T] = BaseResource):
        """
        When it's necessary to update dependencies immediately instead of building at the end,
        this function can be used instead of `get_file()`.
        """
        # FIXME: this function shouldn't be necessary
        asset_id = self._resolve_asset_id(asset_id)
        asset = self.get_parsed_asset(asset_id, type_hint=type_hint)

        yield asset

        self.replace_asset(asset_id, asset)
        self._cached_dependencies.pop(asset_id, None)
        self._cached_ancs_per_char_dependencies.pop(asset_id, None)

    def get_mlvl(self, name: NameOrAssetId) -> Mlvl:
        return self.get_file(name, Mlvl)

    def get_area(self, mlvl: NameOrAssetId, mrea: NameOrAssetId) -> Area:
        return self.get_mlvl(mlvl).get_area(mrea)

    def flush_modified_assets(self):
        with ThreadPoolExecutor() as executor:
            for name, resource in self.memory_files.items():
                executor.submit(self.replace_asset, name, resource)
        self.memory_files = {}

    def save_modifications(self, output_path: Path):
        super().save_modifications(output_path)

        if self.dol is not None:
            target_dol = output_path.joinpath("sys/main.dol")
            target_dol.parent.mkdir(exist_ok=True, parents=True)
            target_dol.write_bytes(self.dol.dol_file.getvalue())

    def create_strg(self,
                    name: str,
                    strings: str | typing.Iterable[str] = (),
                    ) -> tuple[AssetId, Strg]:
        template_id = None
        if self.target_game == Game.ECHOES:
            # Strings/Worlds/TempleHub/01_Temple_LandingSite.STRG
            template_id = 0x2E681FEF

        if template_id is None:
            raise NotImplementedError()

        asset_id = self.duplicate_file(name, template_id)

        strg = self.get_file(asset_id, Strg)

        if isinstance(strings, str):
            strings = strings
        strings = list(strings)

        for lang in strg.languages:
            strg.set_strings(lang, strings)

        return asset_id, strg
