import fnmatch
import io
import os
import typing
from pathlib import Path

import typing_extensions
from mypy.dmypy_util import TracebackType
from retro_data_structures.asset_manager import AssetManager, FileProvider, FileWriter
from retro_data_structures.base_resource import AssetId, NameOrAssetId
from retro_data_structures.formats.mlvl import Mlvl
from retro_data_structures.formats.mrea import Area
from retro_data_structures.formats.scan import Scan
from retro_data_structures.formats.strg import Strg
from retro_data_structures.game_check import Game
from retro_data_structures.properties.echoes.objects.ScannableObjectInfo import ScannableObjectInfo

type LogbookScanStrings = tuple[str, str, str]
"""(Box 1, Box 2, Logbook)"""

type ScanContents = tuple[LogbookScanStrings | tuple[str], AssetId]
"""(Strings, Model ID)"""

try:
    import nod_rs

    # Keeping these classes only in OPR (instead of RDS) until `nod-rs` is available upstream
    # These are also optional until we're fine with including this in Randovania.

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
            return self.data_partition.read_file(self._all_files[name])  # type: ignore[invalid-return-type]

        def read_binary(self, name: str) -> bytes:
            return self.data_partition.read_file(self._all_files[name]).read()

        def get_dol(self) -> bytes:
            return self.data_partition.meta().raw_dol

        def get_file_list(self) -> list[str]:
            return list(self._all_files)

    class _MemoryStringIo(io.StringIO):
        _data: str | None = None

        @property
        def data(self) -> str:
            assert self._data is not None
            return self._data

        def __exit__(
            self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
        ):
            self._data = self.getvalue()
            return super().__exit__(exc_type, exc_val, exc_tb)

    class _MemoryBytesIo(io.BytesIO):
        _data: bytes | None = None

        @property
        def data(self) -> bytes:
            assert self._data is not None
            return self._data

        def __exit__(
            self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
        ):
            self._data = self.getvalue()
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

        @typing_extensions.override
        def open_text(self, name: str) -> typing.TextIO:
            file = self._files.setdefault(name, _MemoryStringIo())
            assert isinstance(file, _MemoryStringIo)
            return file

        @typing_extensions.override
        def open_binary(self, name: str) -> typing.BinaryIO:
            file = self._files.setdefault(name, _MemoryBytesIo())
            assert isinstance(file, _MemoryBytesIo)
            return file

        @typing_extensions.override
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
    pooled_scans: dict[ScanContents, AssetId]
    """Map scan contents to a SCAN asset ID"""

    def __init__(self, provider: FileProvider, target_game: Game):
        super().__init__(provider, target_game)
        self.pooled_scans = {}

    def get_mlvl(self, name: NameOrAssetId) -> Mlvl:
        return self.get_file(name, Mlvl)

    def get_area(self, mlvl: NameOrAssetId, mrea: NameOrAssetId) -> Area:
        return self.get_mlvl(mlvl).get_area(mrea)

    def build_modified_files(self) -> None:
        super().build_modified_files()
        self.pooled_scans.clear()

    def create_strg(
        self,
        name: str,
        strings: str | typing.Iterable[str] = (),
    ) -> tuple[AssetId, Strg]:

        if isinstance(strings, str):
            string_list = [strings]
        else:
            string_list = list(strings)

        if self.does_asset_exists(name):
            existing = self.get_file(name, Strg)
            expected = tuple(string_list)
            if existing.strings == expected:
                return self._resolve_asset_id(name), existing
            raise ValueError(
                f"STRG named {name!r} already exists with contents `{existing.strings!r}`, expected `{expected!r}`"
            )

        template_id = None
        if self.target_game == Game.ECHOES:
            # Strings/Worlds/TempleHub/01_Temple_LandingSite.STRG
            template_id = 0x2E681FEF

        if template_id is None:
            raise NotImplementedError

        asset_id = self.duplicate_asset(template_id, name)

        strg = self.get_file(asset_id, Strg)

        strg.set_string_list(string_list)

        return asset_id, strg

    def _create_scan(self, strings: LogbookScanStrings | tuple[str], model: AssetId) -> AssetId:
        if (strings, model) not in self.pooled_scans:
            template_id = None
            if self.target_game == Game.ECHOES:
                # Uncategorized/Light Beam.SCAN
                template_id = 0x7427BA3C

            if template_id is None:
                raise NotImplementedError

            name = f"CustomScan{strings}{model}"

            asset_id = self.duplicate_asset(template_id, f"{name}.SCAN")
            scan = self.get_file(asset_id, Scan)

            with scan.scannable_object_info.edit_properties(ScannableObjectInfo) as info:
                info.string, _ = self.create_strg(f"{name}.STRG", strings)
                info.static_model = model

            self.pooled_scans[(strings, model)] = asset_id

        return self.pooled_scans[(strings, model)]

    def create_simple_scan(self, box1: str, box2: str | None = None) -> AssetId:
        """
        Creates a SCAN that does not have a logbook entry, nor a dedicated model.
        """
        if box2 is None:
            return self._create_scan((box1,), 0xFFFFFFFF)
        else:
            return self._create_scan((box1, box2, " "), 0xFFFFFFFF)

    def create_full_scan(self, box1: str, box2: str, logbook: str, model: AssetId) -> AssetId:
        """
        Creates a SCAN with initial scan text, second box, logbook entry and a custom model.
        """
        # TODO: create the logbook entry as well?
        return self._create_scan((box1, box2, logbook), model)
