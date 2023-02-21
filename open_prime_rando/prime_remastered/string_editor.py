import typing

from retro_data_structures.asset_manager import AssetManager
from retro_data_structures.base_resource import AssetId
from retro_data_structures.formats import Msbt


class StringEditor:
    def __init__(self, asset_manager: AssetManager):
        self.asset_manager = asset_manager
        self.all_labels = None

    def load_all_msbt(self):
        if self.all_labels is not None:
            return

        self.all_labels = {}
        for asset_id in self.asset_manager.all_asset_ids():
            if self.asset_manager.get_asset_type(asset_id) == "MSBT":
                msbt = self.asset_manager.get_file(asset_id, Msbt)
                for i, label_array in enumerate(msbt.raw.us_english.contents.labels):
                    for label in label_array:
                        assert label.str not in self.all_labels
                        self.all_labels[label.str] = (msbt, i)

    def _get_label_for(self, asset_id: AssetId, index: int):
        self.load_all_msbt()
        return "[{:08X}]_{:03}".format(asset_id.node, index)

    def get_string(self, asset_id: AssetId, index: int) -> typing.Optional[str]:
        label_for_id = self._get_label_for(asset_id, index)
        try:
            msbt, i = self.all_labels[label_for_id]
            label = msbt.raw.us_english.contents.labels[i]
            return msbt.raw.us_english.contents.texts[label.string_table_index]
        except KeyError:
            return None

    def set_string(self, asset_id: AssetId, index: int, s: str):
        label_for_id = self._get_label_for(asset_id, index)
        msbt, label, i = self.all_labels[label_for_id]
        msbt.raw.us_english.contents.texts[msbt.raw.us_english.contents.labels[i].string_table_index] = s