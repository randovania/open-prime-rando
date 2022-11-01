import io
import typing
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ppc_asm.dol_file import DolEditor, DolHeader
from retro_data_structures.asset_manager import AssetManager, FileProvider
from retro_data_structures.base_resource import BaseResource, NameOrAssetId, RawResource, AssetId
from retro_data_structures.crc import crc32
from retro_data_structures.formats.mlvl import Mlvl, AreaWrapper
from retro_data_structures.formats.mrea import Mrea
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

    def __init__(self, provider: FileProvider):
        super().__init__(provider, Game.ECHOES)
        self.memory_files = {}
        self.dol = MemoryDol(provider.open_binary("sys/main.dol").read())

    def get_file(self, path: NameOrAssetId, type_hint: typing.Type[T] = BaseResource) -> T:
        if path not in self.memory_files:
            self.memory_files[path] = self.get_parsed_asset(path, type_hint=type_hint)
        return self.memory_files[path]

    def get_mlvl(self, name: NameOrAssetId) -> Mlvl:
        return self.get_file(name, Mlvl)

    def get_mrea(self, name: NameOrAssetId) -> Mrea:
        return self.get_file(name, Mrea)

    def get_area_helper(self, mlvl: NameOrAssetId, mrea: NameOrAssetId) -> AreaWrapper:
        return self.get_mlvl(mlvl).get_area(mrea)

    def flush_modified_assets(self):
        with ThreadPoolExecutor() as executor:
            for name, resource in self.memory_files.items():
                executor.submit(self.replace_asset, name, resource)
        self.memory_files = {}

    def add_file(self,
                 name: str,
                 asset: typing.Union[RawResource, BaseResource],
                 paks: typing.Iterable[str]
                 ) -> AssetId:
        asset_id = crc32(name)
        self.register_custom_asset_name(name, asset_id)
        self.add_new_asset(name, asset, paks)
        return asset_id

    def save_modifications(self, output_path: Path):
        super().save_modifications(output_path)
        output_path.joinpath("sys/main.dol").write_bytes(self.dol.dol_file.getvalue())
