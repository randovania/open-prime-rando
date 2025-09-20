import io
import typing

from ppc_asm.dol_file import DolEditor, DolHeader
from retro_data_structures.asset_manager import AssetManager, FileProvider
from retro_data_structures.base_resource import AssetId, NameOrAssetId
from retro_data_structures.formats.mlvl import Mlvl
from retro_data_structures.formats.mrea import Area
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
        self.dol_editor.seek(seek)
        return self.dol_editor.read(size)

    def _seek_and_write(self, seek: int, data: bytes):
        self.dol_editor.seek(seek)
        self.dol_editor.write(data)


class PatcherEditor(AssetManager):
    pooled_scans: dict[tuple[tuple[str, str, str], AssetId], AssetId]

    def __init__(self, provider: FileProvider, game: Game):
        super().__init__(provider, game)
        self.pooled_scans = {}

    def get_mlvl(self, name: NameOrAssetId) -> Mlvl:
        return self.get_file(name, Mlvl)

    def get_area(self, mlvl: NameOrAssetId, mrea: NameOrAssetId) -> Area:
        return self.get_mlvl(mlvl).get_area(mrea)

    def build_modified_files(self):
        super().build_modified_files()
        self.pooled_scans.clear()

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
        strg.set_string_list(strings)

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
