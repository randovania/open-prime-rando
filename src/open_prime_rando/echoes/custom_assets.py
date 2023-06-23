import dataclasses

from retro_data_structures.asset_manager import AssetManager
from retro_data_structures.formats import Ancs, Cmdl


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


def _create_visor_derivatives(editor: AssetManager):
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

    editor.register_custom_asset_name("scan_visor_ancs", editor.generate_asset_id())
    ancs = editor.get_parsed_asset(DARK_VISOR_ANCS, type_hint=Ancs)
    ancs.raw.character_set.characters[0].model_id = SCAN_VISOR_CMDL
    editor.add_new_asset("scan_visor_ancs", ancs, editor.find_paks(DARK_VISOR_ANCS))


@dataclasses.dataclass
class BeamAmmoAssets:
    name: str
    txtr_a: int
    txtr_b: int
    particle: int
    new_cmdl: int
    new_ancs: int


BEAM_AMMO_EXPANSION_CMDL = 0x352c8b02
BEAM_AMMO_EXPANSION_ANCS = 0x4e00188c

DARK_AMMO = BeamAmmoAssets(
    name="dark_ammo",
    txtr_a=1385637646,
    txtr_b=3277274054,
    particle=0x8e0c499d,
    new_cmdl=1631670273,
    new_ancs=0x61415002,
)
LIGHT_AMMO = BeamAmmoAssets(
    name="light_ammo",
    txtr_a=1815959726,
    txtr_b=2738959665,
    particle=0xa180bb7f,
    new_cmdl=1631670275,
    new_ancs=1631670276,
)


def _create_split_ammo(editor: AssetManager):
    for ammo in [DARK_AMMO, LIGHT_AMMO]:
        editor.register_custom_asset_name(f"{ammo.name}_cmdl", ammo.new_cmdl)
        editor.register_custom_asset_name(f"{ammo.name}_ancs", ammo.new_ancs)

        cmdl = editor.get_parsed_asset(BEAM_AMMO_EXPANSION_CMDL, type_hint=Cmdl)
        cmdl.raw.material_sets[0].texture_file_ids[0] = ammo.txtr_a
        cmdl.raw.material_sets[0].texture_file_ids[2] = ammo.txtr_a
        cmdl.raw.material_sets[0].texture_file_ids[3] = ammo.txtr_b
        cmdl.raw.material_sets[0].texture_file_ids[4] = ammo.txtr_b
        editor.add_new_asset(f"{ammo.name}_cmdl", cmdl, editor.find_paks(BEAM_AMMO_EXPANSION_CMDL))

        ancs = editor.get_parsed_asset(BEAM_AMMO_EXPANSION_ANCS, type_hint=Ancs)
        ancs.raw.character_set.characters[0].model_id = ammo.new_cmdl
        ancs.raw.character_set.characters[0].particle_resource_data.generic_particles = [
            0x89C2F268,
            ammo.particle,
        ]
        ancs.raw.animation_set.event_sets[0].particle_poi_nodes[0].particle.id = ammo.particle
        ancs.raw.animation_set.event_sets[0].particle_poi_nodes[1].particle.id = ammo.particle
        editor.add_new_asset(f"{ammo.name}_ancs", ancs, editor.find_paks(BEAM_AMMO_EXPANSION_ANCS))


def create_custom_assets(editor: AssetManager):
    _create_visor_derivatives(editor)
    _create_split_ammo(editor)
