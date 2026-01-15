import typing

from retro_data_structures.asset_manager import AssetManager, FileProvider, FileWriter
from retro_data_structures.base_resource import AssetId, NameOrAssetId
from retro_data_structures.formats.mlvl import Mlvl
from retro_data_structures.formats.mrea import Area
from retro_data_structures.formats.strg import Strg
from retro_data_structures.game_check import Game

T = typing.TypeVar("T")


class PatcherEditor(AssetManager):
    custom_files: dict[str, bytes]

    def __init__(self, provider: FileProvider, target_game: Game):
        super().__init__(provider, target_game)
        self.custom_files = {}

    def get_mlvl(self, name: NameOrAssetId) -> Mlvl:
        return self.get_file(name, Mlvl)

    def get_area(self, mlvl: NameOrAssetId, mrea: NameOrAssetId) -> Area:
        return self.get_mlvl(mlvl).get_area(mrea)

    def create_strg(
        self,
        name: str,
        strings: str | typing.Iterable[str] = (),
    ) -> tuple[AssetId, Strg]:
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

    def save_modifications(self, output: FileWriter) -> None:
        super().save_modifications(output)
        for name, data in self.custom_files.items():
            with output.open_binary(name) as f:
                f.write(data)
