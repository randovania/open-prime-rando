import fnmatch
import io
import os
import typing
from pathlib import Path

from retro_data_structures.asset_manager import AssetManager, FileProvider, FileWriter
from retro_data_structures.base_resource import AssetId, NameOrAssetId
from retro_data_structures.formats.mlvl import Mlvl
from retro_data_structures.formats.mrea import Area
from retro_data_structures.formats.strg import Strg
from retro_data_structures.game_check import Game

T = typing.TypeVar("T")

try:
    import nod_rs

    class IsoFileProvider(FileProvider):
        disc_reader: nod_rs.DiscReader

        def __init__(self, iso_path: Path):
            self.iso_path = iso_path

            self.disc_reader = nod_rs.DiscReader(os.fspath(iso_path))
            self.data_partition = self.disc_reader.open_partition_kind("Data")
            meta = self.data_partition.meta()
            fst = meta.fst()
            self._all_files = {entry.path: entry for entry in fst if entry.is_file}

        def __repr__(self) -> str:
            return f"<IsoFileProvider {self.iso_path}>"

        def is_file(self, name: str) -> bool:
            return name in self._all_files

        def rglob(self, pattern: str) -> typing.Iterator[str]:
            for it in self._all_files:
                if fnmatch.fnmatch(it, pattern):
                    yield it

        def open_binary(self, name: str) -> typing.BinaryIO:
            return self.data_partition.read_file(self._all_files[name])

        def read_binary(self, name: str) -> bytes:
            return self.data_partition.read_file(self._all_files[name]).read()

        def get_dol(self) -> bytes:
            return self.data_partition.meta().raw_dol

        def get_file_list(self) -> list[str]:
            return list(self._all_files)

    class _MemoryStringIo(io.StringIO):
        data: str | None = None

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.data = self.getvalue()
            return super().__exit__(exc_type, exc_val, exc_tb)

    class _MemoryBytesIo(io.BytesIO):
        data: bytes | None = None

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.data = self.getvalue()
            return super().__exit__(exc_type, exc_val, exc_tb)

    class IsoFileWriter(FileWriter):
        """
        A FileWriter that creates a GameCube ISO disc, using an existing IsoFileProvider as reference.
        The ISO is only created when `commit` is called.
        """

        source: IsoFileProvider
        patcher: nod_rs.DiscPatcher
        _files: dict[str, _MemoryStringIo | _MemoryBytesIo]
        _dol: bytes | None

        def __init__(self, source: IsoFileProvider):
            self.source = source
            self.patcher = nod_rs.DiscPatcher(source.disc_reader)
            self._files = {}
            self._dol = None

        @typing.override
        def open_text(self, name: str) -> typing.TextIO:
            return self._files.setdefault(name, _MemoryStringIo())

        @typing.override
        def open_binary(self, name: str) -> typing.BinaryIO:
            return self._files.setdefault(name, _MemoryBytesIo())

        @typing.override
        def write_dol(self, data: bytes) -> None:
            self._dol = data

        def commit(
            self,
            output: Path,
            format: str = "ISO",
            callback: typing.Callable[[int, int], None] | None = None,
        ) -> None:
            """Creates the ISO with all the files written so far."""

            for name, file in self._files.items():
                if isinstance(file, _MemoryStringIo):
                    self.patcher.add_file(name, file.data.encode("utf-8"))
                else:
                    self.patcher.add_file(name, file.data)

            self._files.clear()

            if self._dol is not None:
                self.patcher.set_dol(self._dol)

            writer = nod_rs.DiscWriter(
                self.patcher.build(),
                format,
            )
            writer.process(
                os.fspath(output),
                callback=callback,
            )
except ImportError:
    pass


class PatcherEditor(AssetManager):
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
