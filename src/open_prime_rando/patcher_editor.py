import contextlib
import io
import typing
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ppc_asm.dol_file import DolEditor, DolHeader
from retro_data_structures.asset_manager import AssetManager, FileProvider
from retro_data_structures.base_resource import AssetId, BaseResource, NameOrAssetId, Resource
from retro_data_structures.crc import crc32
from retro_data_structures.formats.mlvl import Mlvl
from retro_data_structures.formats.mrea import Area
from retro_data_structures.formats.ntwk import Ntwk
from retro_data_structures.formats.scan import Scan
from retro_data_structures.formats.strg import Strg
from retro_data_structures.game_check import Game
from retro_data_structures.properties.echoes.objects.ScannableObjectInfo import ScannableObjectInfo

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
    pooled_scans: dict[tuple[tuple[str, str, str], AssetId], AssetId]
    dol: MemoryDol | None = None
    tweaks: Ntwk | None = None

    def __init__(self, provider: FileProvider, game: Game):
        super().__init__(provider, game)
        self.memory_files = {}
        self.pooled_scans = {}

        if game in [Game.PRIME, Game.ECHOES]:
            self.dol = MemoryDol(provider.get_dol())
        if game == Game.ECHOES:
            with provider.open_binary("Standard.ntwk") as f:
                self.tweaks = Ntwk.parse(f.read(), game)

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
        self.pooled_scans = {}

    def add_file(
        self,
        name: str,
        asset: Resource,
    ) -> AssetId:
        asset_id = crc32(name)
        self.register_custom_asset_name(name, asset_id)
        self.add_new_asset(name, asset, ())
        return asset_id

    def duplicate_file(self, name: str, asset: AssetId) -> AssetId:
        return self.add_file(name, self.get_raw_asset(asset))

    def save_modifications(self, output_path: Path):
        # AssetManager exports files relative to what FileProvider says
        # Since the `files/` subpath is ignored by it, let's tell it to put all the files in there.
        super().save_modifications(output_path.joinpath("files"))

        if self.dol is not None:
            target_dol = output_path.joinpath("sys/main.dol")
            target_dol.parent.mkdir(exist_ok=True, parents=True)
            target_dol.write_bytes(self.dol.dol_file.getvalue())

        if self.tweaks is not None:
            output_path.joinpath("files/Standard.ntwk").write_bytes(self.tweaks.build())

    def add_or_replace_custom_asset(self, name: str, new_data: Resource) -> AssetId:
        if self.does_asset_exists(name):
            asset_id = self.replace_asset(name, new_data)
        else:
            asset_id = self.add_file(name, new_data)
        return asset_id

    def create_strg(
        self,
        name: str,
        strings: str | typing.Iterable[str] = (),
    ) -> tuple[AssetId, Strg]:

        if self.does_asset_exists(name):
            existing = self.get_file(name, Strg)
            if existing.strings == strings:
                return [self._resolve_asset_id(name), existing]
            raise ValueError(f"STRG named {name} already exists with different contents")

        template_id = None
        if self.target_game == Game.ECHOES:
            # Strings/Worlds/TempleHub/01_Temple_LandingSite.STRG
            template_id = 0x2E681FEF

        if template_id is None:
            raise NotImplementedError

        asset_id = self.duplicate_asset(template_id, name)

        strg = self.get_file(asset_id, Strg)

        # TODO: ???
        # if isinstance(strings, str):
        #     strings = strings

        strings = list(strings)

        for lang in strg.languages:
            strg.set_strings(lang, strings)

        return asset_id, strg

    def get_pickup_scan(self, strings: str | tuple[str, str, str], model: AssetId) -> AssetId:
        if isinstance(strings, str):
            strings = (strings, "", "")

        if (strings, model) not in self.pooled_scans:
            template_id = None
            if self.target_game == Game.ECHOES:
                # Uncategorized/Light Beam.SCAN
                template_id = 0x7427BA3C

            if template_id is None:
                raise NotImplementedError

            name = f"Pickup{strings}{model}"

            asset_id = self.duplicate_asset(template_id, f"{name}.SCAN")
            scan = self.get_file(asset_id, Scan)

            with scan.scannable_object_info.edit_properties(ScannableObjectInfo) as info:
                info.string, _ = self.create_strg(f"{name}.STRG", strings)
                info.static_model = model

            self.pooled_scans[(strings, model)] = asset_id

        return self.pooled_scans[(strings, model)]

