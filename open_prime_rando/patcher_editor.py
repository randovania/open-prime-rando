import typing

from retro_data_structures.base_resource import BaseResource, NameOrAssetId
from retro_data_structures.asset_manager import AssetManager, FileProvider
from retro_data_structures.formats import Mlvl
from retro_data_structures.formats.mrea import Mrea
from retro_data_structures.game_check import Game

T = typing.TypeVar("T")


class PatcherEditor(AssetManager):
    memory_files: dict[NameOrAssetId, BaseResource]

    def __init__(self, provider: FileProvider):
        super().__init__(provider, Game.ECHOES)
        self.memory_files = {}

    def get_file(self, path: NameOrAssetId, type_hint: typing.Type[T] = BaseResource) -> T:
        if path not in self.memory_files:
            self.memory_files[path] = self.get_parsed_asset(path, type_hint=type_hint)
        return self.memory_files[path]

    def get_mlvl(self, name: NameOrAssetId) -> Mlvl:
        return self.get_file(name, Mlvl)

    def get_mrea(self, name: NameOrAssetId) -> Mrea:
        return self.get_file(name, Mrea)

    def flush_modified_assets(self):
        for name, resource in self.memory_files.items():
            self.replace_asset(name, resource)
        self.memory_files = {}
