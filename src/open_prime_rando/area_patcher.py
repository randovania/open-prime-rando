from __future__ import annotations

import collections
import logging
import typing

from retro_data_structures.formats.mlvl import Mlvl
from retro_data_structures.formats.mrea import Area

from open_prime_rando.patcher_editor import PatcherEditor

if typing.TYPE_CHECKING:
    from open_prime_rando.echoes.patcher import StatusUpdate
    from open_prime_rando.echoes.rando_configuration import AssetId

type RawPatcherFunction = typing.Callable[[PatcherEditor, Mlvl, Area], None]


class AreaPatcherFunction(typing.Protocol):
    mlvl_id: AssetId
    mrea_id: AssetId

    def __call__(self, editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None: ...


def decorate_patcher(mlvl_id: AssetId, mrea_id: AssetId) -> typing.Callable[[RawPatcherFunction], AreaPatcherFunction]:
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


class AreaPatcher:
    _patcher_functions: dict[AssetId, dict[AssetId, list[RawPatcherFunction]]]
    _frontend_functions: list[RawPatcherFunction]

    def __init__(self, editor: PatcherEditor, mlvl_list: list[AssetId], *, rebuild_savw: bool = True):
        self.editor = editor
        self.mlvl_list = mlvl_list
        self.rebuild_savw = rebuild_savw

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

    def add_raw_function(self, mlvl_id: AssetId, mrea_id: AssetId, func: RawPatcherFunction) -> None:
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

    def perform_changes(self, status_update: StatusUpdate | None = None) -> None:
        """
        Calls the registered functions.
        """
        if status_update is None:

            def status_update(s: str, p: float) -> None:
                logging.info(s)

        num_area_changes = sum(len(area_changes) for area_changes in self._patcher_functions.values())
        areas_changed = 0

        for mlvl_id, area_changes in self._patcher_functions.items():
            mlvl = self.editor.get_mlvl(mlvl_id)
            status_update(f"Patching {mlvl.world_name}", areas_changed / num_area_changes)

            for area in mlvl.areas:
                area_functions = area_changes[area.mrea_asset_id]
                if not area_functions:
                    # Area unchanged
                    continue

                status_update(f"Patching {area.name}", areas_changed / num_area_changes)
                for func in area_functions:
                    func(self.editor, mlvl, area)

                area.update_all_dependencies(only_modified=True)
                areas_changed += 1

            if self.rebuild_savw:
                status_update(f"Rebuilding {mlvl.world_name} save format", areas_changed / num_area_changes)
                mlvl.rebuild_savw()

        if self._frontend_functions:
            from open_prime_rando.echoes.specific_area_patches import front_end

            area = front_end.get_front_end_area(self.editor)

            status_update("Patching FrontEnd", 1.0)

            for func in self._frontend_functions:
                func(self.editor, area._parent_mlvl, area)
