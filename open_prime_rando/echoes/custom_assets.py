import dataclasses
import struct
from pathlib import Path

from retro_data_structures.formats import Ancs, Cmdl

from open_prime_rando.patcher_editor import PatcherEditor


@dataclasses.dataclass
class TranslatorAssets:
    name: str
    txtr: int
    new_cmdl: int
    new_ancs: int


SCAN_VISOR_CMDL = 0xafc70004
DARK_VISOR_ANCS = 0x851b526e

VIOLET_TXTR = 0x4be5342e
AMBER_TXTR = 0xf5308558
EMERALD_TXTR = 0xa9640fdf
COBALT_TXTR = 0x2c56d2d4


VIOLET_TRANSLATOR = TranslatorAssets(
    name="violet_translator",
    txtr=0x4be5342e,
    new_cmdl=1448365380,
    new_ancs=1448362318,
)
AMBER_TRANSLATOR = TranslatorAssets(
    name="amber_translator",
    txtr=0xf5308558,
    new_cmdl=1096043844,
    new_ancs=1096040782,
)
EMERALD_TRANSLATOR = TranslatorAssets(
    name="emerald_translator",
    txtr=0xa9640fdf,
    new_cmdl=1163152708,
    new_ancs=1163149646,
)
COBALT_TRANSLATOR = TranslatorAssets(
    name="cobalt_translator",
    txtr=0x2c56d2d4,
    new_cmdl=1129598276,
    new_ancs=1129595214,
)


def _create_visor_derivatives(editor: PatcherEditor):
    for translator in [VIOLET_TRANSLATOR, AMBER_TRANSLATOR, EMERALD_TRANSLATOR, COBALT_TRANSLATOR]:
        editor.register_custom_asset_name(f"{translator.name}_cmdl", translator.new_cmdl)
        editor.register_custom_asset_name(f"{translator.name}_ancs", translator.new_ancs)

        cmdl = editor.get_parsed_asset(SCAN_VISOR_CMDL, type_hint=Cmdl)
        cmdl.raw.material_sets[0].texture_file_ids[0] = translator.txtr
        cmdl.raw.material_sets[0].texture_file_ids[1] = translator.txtr
        editor.add_new_asset(f"{translator.name}_cmdl", cmdl, editor.find_paks(SCAN_VISOR_CMDL))

        ancs = editor.get_parsed_asset(DARK_VISOR_ANCS, type_hint=Ancs)
        ancs.raw.character_set.characters[0].model_id = translator.new_cmdl
        editor.add_new_asset(f"{translator.name}_ancs", ancs, editor.find_paks(DARK_VISOR_ANCS))


def create_custom_assets(editor: PatcherEditor):
    _create_visor_derivatives(editor)
