from __future__ import annotations

import contextlib
import fnmatch
import io
import os
import typing
from concurrent.futures import ThreadPoolExecutor, as_completed

import typing_extensions
from retro_data_structures.asset_manager import AssetManager, FileWriter
from retro_data_structures.base_resource import AssetId, NameOrAssetId
from retro_data_structures.enums.echoes import InventorySlotEnum, PlayerItemEnum
from retro_data_structures.file_provider import FileProvider
from retro_data_structures.formats.mlvl import Mlvl
from retro_data_structures.formats.scan import Scan
from retro_data_structures.formats.strg import Strg
from retro_data_structures.game_check import Game
from retro_data_structures.properties.echoes.objects.ScannableObjectInfo import ScannableObjectInfo

from open_prime_rando.dol_patching.code_cave_tracker import CodeCaveTracker

if typing.TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from retro_data_structures.formats.mrea import Area
    from retro_data_structures.properties.echoes.objects import (
        TweakAutoMapper,
        TweakBall,
        TweakCameraBob,
        TweakGame,
        TweakGui,
        TweakGuiColors,
        TweakParticle,
        TweakPlayer,
        TweakPlayerControls,
        TweakPlayerGun,
        TweakPlayerRes,
        TweakSlideShow,
        TweakTargeting,
    )

    type TweakObject = (
        TweakAutoMapper
        | TweakBall
        | TweakCameraBob
        | TweakGame
        | TweakGui
        | TweakGuiColors
        | TweakParticle
        | TweakPlayer
        | TweakPlayerControls
        | TweakPlayerGun
        | TweakPlayerRes
        | TweakSlideShow
        | TweakTargeting
    )

    from open_prime_rando.echoes.patcher import StatusUpdate

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
            # TODO: nod_rs.DiscReader ideally should satisfy the BinaryIO protocol
            return typing.cast("typing.BinaryIO", self.data_partition.read_file(self._all_files[name]))

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

        def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: typing.Any):
            self._data = self.getvalue()
            return super().__exit__(exc_type, exc_val, exc_tb)

    class _MemoryBytesIo(io.BytesIO):
        _data: bytes | None = None

        @property
        def data(self) -> bytes:
            assert self._data is not None
            return self._data

        def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: typing.Any):
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

    code_cave: CodeCaveTracker

    def __init__(self, provider: FileProvider, target_game: Game):
        super().__init__(provider, target_game)
        self.pooled_scans = {}
        self.code_cave = CodeCaveTracker(self.dol)

    def get_mlvl(self, name: NameOrAssetId) -> Mlvl:
        return self.get_file(name, Mlvl)

    def get_area(self, mlvl: NameOrAssetId, mrea: NameOrAssetId) -> Area:
        return self.get_mlvl(mlvl).get_area(mrea)

    def build_modified_files(self, status_update: StatusUpdate | None = None) -> None:
        # super().build_modified_files()

        if status_update is None:

            def status_update(s: str, p: float) -> None:
                pass

        _last_percent = None

        def _write_callback(files_built: int, total_files: int) -> None:
            nonlocal _last_percent
            percent = int(100 * (files_built / total_files))
            if percent != _last_percent:
                status_update(f"Building modified files: {percent}%", files_built / total_files)
                _last_percent = percent

        # flush dependencies before building to prevent inaccuracy
        self._cached_dependencies.clear()
        self._cached_ancs_per_char_dependencies.clear()

        status_update("Building modified files", 0.0)
        total_files = len(self._memory_files)

        with ThreadPoolExecutor() as executor:
            futures = []

            for name, resource in self._memory_files.items():
                future = executor.submit(self.replace_asset, name, resource, keep_in_memory=False)
                futures.append(future)

            for i, _ in enumerate(as_completed(futures)):
                _write_callback(i, total_files)

        status_update("Finalizing modification", 1.0)

        self._memory_files.clear()
        self.pooled_scans.clear()

    def _export_paks(self, output: FileWriter) -> None:
        strategies = {name: strategy for name, strategy in self._pak_strategy.items() if strategy.should_export()}
        num_strategies = len(strategies)

        for i, (name, strategy) in enumerate(strategies.items()):
            self._pak_status_update(f"Building {name}", i / num_strategies)
            strategy.export(output)
        self._pak_status_update("Built PAKs", 1.0)

    def save_modifications(self, output: FileWriter, status_update: StatusUpdate | None = None) -> None:
        if status_update is None:

            def status_update(s: str, p: float) -> None:
                pass

        self._pak_status_update: StatusUpdate = status_update
        return super().save_modifications(output)

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
                return self.resolve_asset_id(name), existing
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

    def create_simple_scan(self, box1: str, box2: str | None = None, model: AssetId = 0xFFFFFFFF) -> AssetId:
        """
        Creates a SCAN that does not have a logbook entry, nor a dedicated model.
        """
        if box2 is None:
            return self._create_scan((box1,), model)
        else:
            return self._create_scan((box1, box2, " "), model)

    def create_full_scan(self, box1: str, box2: str, logbook: str, model: AssetId) -> AssetId:
        """
        Creates a SCAN with initial scan text, second box, logbook entry and a custom model.
        """
        # TODO: create the logbook entry as well?
        return self._create_scan((box1, box2, logbook), model)

    @contextlib.contextmanager
    def edit_tweak[T: TweakObject](self, tweak_class: type[T]) -> Generator[T, None, None]:
        """Context manager for editing the single-player tweak of the given class."""

        for instance in self.tweaks.instances:
            if instance.script_type == tweak_class:
                prop = instance.get_properties_as(tweak_class)
                if prop.instance_name.endswith("2"):
                    continue

                yield prop

                instance.set_properties(prop)
                return

        raise KeyError(f"Unknown tweak class: {tweak_class}")

    # InventorySlot management
    inventory_slot_to_item: list[PlayerItemEnum]

    def assign_item_to_inventory_slot(self, item: PlayerItemEnum, slot: InventorySlotEnum) -> None:
        while len(self.inventory_slot_to_item) <= slot.value:
            # Using an item we're unlikely to use
            self.inventory_slot_to_item.append(PlayerItemEnum.Invisibility)

        self.inventory_slot_to_item[slot.value] = item
