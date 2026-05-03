import collections
import logging
import typing

from retro_data_structures.formats.mlvl import Mlvl
from retro_data_structures.formats.mrea import Area

from open_prime_rando.echoes.rando_configuration import AssetId
from open_prime_rando.patcher_editor import PatcherEditor

type RawPatcherFunction = typing.Callable[[PatcherEditor, Mlvl, Area], None]


class AreaPatcherFunction(typing.Protocol):
    @property
    def mlvl_id(self) -> AssetId: ...

    @property
    def mrea_id(self) -> AssetId: ...

    def __call__(self, editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None: ...


def decorate_patcher(mlvl_id: AssetId, mrea_id: AssetId) -> typing.Callable[[RawPatcherFunction], AreaPatcherFunction]:
    """
    Annotates a function with the mlvl_id/mrea_id
    :param mlvl_id:
    :param mrea_id:
    :return:
    """

    def decorator(func: RawPatcherFunction) -> AreaPatcherFunction:
        func.mlvl_id = mlvl_id
        func.mrea_id = mrea_id
        return func

    return decorator


class AreaPatcher:
    _patcher_functions: dict[AssetId, dict[AssetId, list[AreaPatcherFunction]]]

    def __init__(self, editor: PatcherEditor, mlvl_list: list[AssetId]):
        self.editor = editor
        self.mlvl_list = mlvl_list

        self._patcher_functions = {mlvl_id: collections.defaultdict(list) for mlvl_id in mlvl_list}

    def add_function(self, func: AreaPatcherFunction) -> None:
        """
        Adds a new function that is used to patch an area.
        """
        self._patcher_functions[func.mlvl_id][func.mrea_id].append(func)

    def perform_changes(self) -> None:
        """

        :return:
        """
        for mlvl_id, area_changes in self._patcher_functions.items():
            mlvl = self.editor.get_mlvl(mlvl_id)
            logging.info("Patching %s", mlvl.world_name)

            for area in mlvl.areas:
                area_functions = self._patcher_functions[mlvl_id][area.mrea_asset_id]
                if not area_functions:
                    # Area unchanged
                    continue

                logging.info("Patching %s", area.name)
                for func in area_functions:
                    func(self.editor, mlvl, area)
