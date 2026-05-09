import collections
import logging
import typing

from retro_data_structures.formats.mlvl import Mlvl
from retro_data_structures.formats.mrea import Area

from open_prime_rando.echoes.rando_configuration import AssetId
from open_prime_rando.patcher_editor import PatcherEditor

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

    def perform_changes(self) -> None:
        """
        Calls the registered functions.
        """
        for mlvl_id, area_changes in self._patcher_functions.items():
            mlvl = self.editor.get_mlvl(mlvl_id)
            logging.info("Patching %s", mlvl.world_name)

            for area in mlvl.areas:
                area_functions = area_changes[area.mrea_asset_id]
                if not area_functions:
                    # Area unchanged
                    continue

                logging.info("Patching %s", area.name)
                for func in area_functions:
                    func(self.editor, mlvl, area)

                area.update_all_dependencies(only_modified=True)

            if self.rebuild_savw:
                logging.info("Rebuilding %s save format", mlvl.world_name)
                mlvl.rebuild_savw()

        if self._frontend_functions:
            from open_prime_rando.echoes.specific_area_patches import front_end

            area = front_end.get_front_end_area(self.editor)

            logging.info("Patching FrontEnd")

            for func in self._frontend_functions:
                func(self.editor, area._parent_mlvl, area)
