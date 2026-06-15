from __future__ import annotations

import collections
import logging
import typing

from retro_data_structures.formats.mlvl import Mlvl
from retro_data_structures.formats.mrea import Area

from open_prime_rando.patcher_editor import PatcherEditor

if typing.TYPE_CHECKING:
    from open_prime_rando.echoes.patcher import StatusUpdate
    from open_prime_rando.echoes.pydantic_models import PydanticAssetId

type RawPatcherFunction = typing.Callable[[PatcherEditor, Mlvl, Area], None]
type RawWorldPatcherFunction = typing.Callable[[PatcherEditor, PydanticAssetId], None]


class AreaPatcherFunction(typing.Protocol):
    mlvl_id: PydanticAssetId
    mrea_id: PydanticAssetId

    def __call__(self, editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None: ...


def decorate_patcher(
    mlvl_id: PydanticAssetId, mrea_id: PydanticAssetId
) -> typing.Callable[[RawPatcherFunction], AreaPatcherFunction]:
    """
    Annotates a function with the mlvl_id/mrea_id
    :param mlvl_id:
    :param mrea_id:
    :return:
    """

    def decorator(func: RawPatcherFunction) -> AreaPatcherFunction:
        result = typing.cast("AreaPatcherFunction", func)
        result.mlvl_id = mlvl_id
        result.mrea_id = mrea_id
        return result

    return decorator


def _verify_connected_docks(mlvl: Mlvl) -> None:
    """Checks if all dock connections in the given mlvl are two-way."""

    dock_pairs = {}

    for area in mlvl.areas:
        for dock_index, dock in enumerate(area._raw.docks):
            if len(dock.connecting_dock) == 1:
                # Ignoring docks that connect to nothing. There's no docks with more than 1 connection.
                dock_pairs[(area.index, dock_index)] = (
                    dock.connecting_dock[0].area_index,
                    dock.connecting_dock[0].dock_index,
                )

    for source_pair, target_pair in dock_pairs.items():
        reverse_pair = dock_pairs[target_pair]
        if reverse_pair != source_pair:
            raise ValueError(
                f"{source_pair} is connected to {target_pair}, but the reverse is connected to {reverse_pair}"
            )


class AreaPatcher:
    num_area_changes: int
    areas_changed: int
    _world_functions: dict[PydanticAssetId, list[RawWorldPatcherFunction]]
    _patcher_functions: dict[PydanticAssetId, dict[PydanticAssetId, list[RawPatcherFunction]]]
    _frontend_functions: list[RawPatcherFunction]

    def __init__(self, editor: PatcherEditor, mlvl_list: list[PydanticAssetId], *, rebuild_savw: bool = True):
        self.editor = editor
        self.mlvl_list = mlvl_list
        self.rebuild_savw = rebuild_savw

        self._world_functions = {mlvl_id: [] for mlvl_id in mlvl_list}
        self._patcher_functions = {mlvl_id: collections.defaultdict(list) for mlvl_id in mlvl_list}
        self._frontend_functions = []

    def add_function(self, func: AreaPatcherFunction) -> None:
        """
        Adds a function decorated with `decorate_patcher` that is used to patch an area.
        """
        self._patcher_functions[func.mlvl_id][func.mrea_id].append(func)

    def add_frontend_function(self, func: RawPatcherFunction) -> None:
        """
        Adds a function that is used to patch the FrontEnd area.
        The world and area asset IDs are automatically supplied.
        """
        self._frontend_functions.append(func)

    def add_raw_function(self, mlvl_id: PydanticAssetId, mrea_id: PydanticAssetId, func: RawPatcherFunction) -> None:
        """
        Adds a new function that is used to patch an area with the given ids.
        """
        self._patcher_functions[mlvl_id][mrea_id].append(func)

    def add_global_function(self, func: RawPatcherFunction) -> None:
        """
        Adds a function that is called for every area, except for FrontEnd.
        """
        for mlvl_id, area_changes in self._patcher_functions.items():
            mlvl = self.editor.get_mlvl(mlvl_id)
            for area in mlvl.areas:
                area_changes[area.mrea_asset_id].append(func)

    def add_world_function(self, mlvl_id: PydanticAssetId, func: RawWorldPatcherFunction) -> None:
        """
        Adds a new function that is used to patch a world with the given ID.
        """
        self._world_functions[mlvl_id].append(func)

    def _perform_world_change(self, mlvl_id: PydanticAssetId, status_update: StatusUpdate) -> None:
        area_changes = self._patcher_functions[mlvl_id]
        mlvl = self.editor.get_mlvl(mlvl_id)
        status_update(f"Patching {mlvl.world_name}", self.areas_changed / self.num_area_changes)

        for world_func in self._world_functions[mlvl_id]:
            world_func(self.editor, mlvl_id)

        for area in mlvl.areas:
            area_functions = area_changes[area.mrea_asset_id]
            if not area_functions:
                # Area unchanged
                continue

            status_update(f"Patching {area.name}", self.areas_changed / self.num_area_changes)
            for func in area_functions:
                func(self.editor, mlvl, area)

            area.update_all_dependencies(only_modified=True)
            self.areas_changed += 1

        _verify_connected_docks(mlvl)

        if self.rebuild_savw:
            status_update(f"Rebuilding {mlvl.world_name} save format", self.areas_changed / self.num_area_changes)
            mlvl.rebuild_savw()

    def perform_changes(self, status_update: StatusUpdate | None = None) -> None:
        """
        Calls the registered functions.
        """
        if status_update is None:

            def status_update(s: str, p: float) -> None:
                logging.info(s)

        self.num_area_changes = sum(len(area_changes) for area_changes in self._patcher_functions.values())
        self.areas_changed = 0

        for mlvl_id in self.mlvl_list:
            self._perform_world_change(mlvl_id, status_update)

        if self._frontend_functions:
            from open_prime_rando.echoes.specific_area_patches import front_end

            area = front_end.get_front_end_area(self.editor)

            status_update("Patching FrontEnd", 1.0)

            for func in self._frontend_functions:
                func(self.editor, area.parent_mlvl, area)
