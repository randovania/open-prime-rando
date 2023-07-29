import io
import typing
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ppc_asm.dol_file import DolEditor, DolHeader
from retro_data_structures.asset_manager import AssetManager, FileProvider
from retro_data_structures.base_resource import AssetId, BaseResource, NameOrAssetId, RawResource, Resource
from retro_data_structures.crc import crc32
from retro_data_structures.formats.mlvl import Mlvl
from retro_data_structures.formats.mrea import Area, Mrea
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


class AssetModifiedStatusReport:
    def __init__(self, total: int, status_update: typing.Callable[[str, float], None]):
        self.status_update = status_update
        self.done = 0
        self.total = total

    def __call__(self, *args, **kwargs):
        self.done += 1
        self.status_update(
            f"Finalizing modified files, {self.done} out of {self.total} done.",
            self.done / self.total
        )


class PatcherEditor(AssetManager):
    memory_files: dict[NameOrAssetId, BaseResource]
    _areas_to_update_dependencies: list[tuple[Area, bool]]

    def __init__(self, provider: FileProvider, game: Game):
        super().__init__(provider, game)
        self.memory_files = {}
        self._areas_to_update_dependencies = []

        if game in [Game.PRIME, Game.ECHOES]:
            self.dol = MemoryDol(provider.get_dol())
        else:
            self.dol = None

    def get_file(self, path: NameOrAssetId, type_hint: type[T] = BaseResource) -> T:
        if path not in self.memory_files:
            self.memory_files[path] = self.get_parsed_asset(path, type_hint=type_hint)
        return self.memory_files[path]

    def get_mlvl(self, name: NameOrAssetId) -> Mlvl:
        return self.get_file(name, Mlvl)

    def get_area(self, mlvl: NameOrAssetId, mrea: NameOrAssetId) -> Area:
        return self.get_mlvl(mlvl).get_area(mrea)

    def _bulk_replace_asset(self, assets: typing.Iterable[tuple[NameOrAssetId, BaseResource]],
                            on_done: typing.Callable[[typing.Any], None]):
        with ThreadPoolExecutor() as executor:
            for name, resource in assets:
                executor.submit(self.replace_asset, name, resource).add_done_callback(on_done)

    def _get_final_areas_to_update_dependencies(self) -> list[tuple[Area, bool]]:
        id_to_area: dict[int, tuple[Area, bool]] = {}

        for area, only_modified in self._areas_to_update_dependencies:
            if not only_modified or area.mrea_asset_id not in id_to_area:
                id_to_area[area.mrea_asset_id] = (area, only_modified)

        return list(id_to_area.values())

    def flush_modified_assets(self, status_update: typing.Callable[[str, float], None]):
        areas_to_update = self._get_final_areas_to_update_dependencies()

        modified_report = AssetModifiedStatusReport(
            len(areas_to_update) + len(self.memory_files),
            status_update
        )

        modified_report()

        non_mrea_mlvl = []
        for name, resource in list(self.memory_files.items()):
            if resource.resource_type() not in (Mlvl, Mrea):
                non_mrea_mlvl.append((name, resource))
                self.memory_files.pop(name)

        self._bulk_replace_asset(non_mrea_mlvl, modified_report)

        # Clear all previously calculated dependencies
        # TODO: invalidate the dependency cache whenever we modify an asset, but do so smartly
        self._cached_dependencies.clear()
        self._cached_ancs_per_char_dependencies.clear()

        for area, only_modified in areas_to_update:
            area.update_all_dependencies(only_modified=only_modified)
            modified_report()

        self._areas_to_update_dependencies.clear()
        self._bulk_replace_asset(self.memory_files.items(), modified_report)
        self.memory_files = {}

    def add_file(self,
                 name: str,
                 asset: RawResource | BaseResource
                 ) -> AssetId:
        asset_id = crc32(name)
        self.register_custom_asset_name(name, asset_id)
        self.add_new_asset(name, asset, ())
        return asset_id

    def duplicate_file(self, name: str, asset: AssetId) -> AssetId:
        return self.add_file(name, self.get_parsed_asset(asset))

    def schedule_dependency_update(self, area: Area, only_modified: bool = False):
        self._areas_to_update_dependencies.append((area, only_modified))

    def save_modifications(self, output_path: Path):
        super().save_modifications(output_path)

        if self.dol is not None:
            target_dol = output_path.joinpath("sys/main.dol")
            target_dol.parent.mkdir(exist_ok=True, parents=True)
            target_dol.write_bytes(self.dol.dol_file.getvalue())

    def add_or_replace_custom_asset(self, name: str, new_data: Resource) -> AssetId:
        if self.does_asset_exists(name):
            asset_id = self.replace_asset(name, new_data)
        else:
            asset_id = self.add_file(name, new_data)
        return asset_id
