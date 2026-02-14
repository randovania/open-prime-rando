import dataclasses
import functools
from pathlib import Path

from retro_data_structures.base_resource import AssetId, NameOrAssetId, RawResource
from retro_data_structures.formats import Ancs, Cmdl

from open_prime_rando.patcher_editor import PatcherEditor


@functools.cache
def custom_asset_path() -> Path:
    return Path(__file__).parent


SCAN_VISOR_CMDL = 0xAFC70004
COMBAT_VISOR_CMDL = 0x0B7E6CA9
DARK_VISOR_ANCS = 0x851B526E


@dataclasses.dataclass
class TranslatorAssets:
    txtr: NameOrAssetId
    new_cmdl: int | None = None
    new_ancs: int | None = None


TRANSLATORS: dict[str, TranslatorAssets] = {
    "violet_translator": TranslatorAssets(
        txtr=0x4BE5342E,
        new_cmdl=1448365380,
        new_ancs=1448362318,
    ),
    "amber_translator": TranslatorAssets(
        txtr=0xF5308558,
        new_cmdl=1096043844,
        new_ancs=1096040782,
    ),
    "emerald_translator": TranslatorAssets(
        txtr=0xA9640FDF,
        new_cmdl=1163152708,
        new_ancs=1163149646,
    ),
    "cobalt_translator": TranslatorAssets(
        txtr=0x2C56D2D4,
        new_cmdl=1129598276,
        new_ancs=1129595214,
    ),
}


def _create_visor_derivatives(editor: PatcherEditor):
    cmdls: dict[str, AssetId] = {
        "combat_visor": COMBAT_VISOR_CMDL,
        "scan_visor": SCAN_VISOR_CMDL,
    }

    for name, assets in TRANSLATORS.items():
        if assets.new_ancs is not None and assets.new_cmdl is not None:
            editor.register_custom_asset_name(f"{name}.CMDL", assets.new_cmdl)
            editor.register_custom_asset_name(f"{name}.ANCS", assets.new_ancs)

        texture = editor._resolve_asset_id(assets.txtr)
        cmdl_id = editor.duplicate_asset(SCAN_VISOR_CMDL, f"{name}.CMDL")

        cmdl = editor.get_file(cmdl_id, type_hint=Cmdl)
        cmdl.raw.material_sets[0].texture_file_ids[0] = texture
        cmdl.raw.material_sets[0].texture_file_ids[1] = texture

        cmdls[name] = cmdl_id

    for name, model in cmdls.items():
        ancs_id = editor.duplicate_asset(DARK_VISOR_ANCS, f"{name}.ANCS")
        ancs = editor.get_file(ancs_id, type_hint=Ancs)
        ancs.raw.character_set.characters[0].model_id = model


@dataclasses.dataclass
class BeamAmmoAssets:
    txtr_a: int
    txtr_b: int
    particle: int
    new_cmdl: int
    new_ancs: int


BEAM_AMMO_EXPANSION_CMDL = 0x352C8B02
BEAM_AMMO_EXPANSION_ANCS = 0x4E00188C

BEAM_AMMO = {
    "dark_ammo": BeamAmmoAssets(
        txtr_a=1385637646,
        txtr_b=3277274054,
        particle=0x8E0C499D,
        new_cmdl=1631670273,
        new_ancs=0x61415002,
    ),
    "light_ammo": BeamAmmoAssets(
        txtr_a=1815959726,
        txtr_b=2738959665,
        particle=0xA180BB7F,
        new_cmdl=1631670275,
        new_ancs=1631670276,
    ),
}


def _create_split_ammo(editor: PatcherEditor):
    for name, ammo in BEAM_AMMO.items():
        editor.register_custom_asset_name(f"{name}.CMDL", ammo.new_cmdl)
        editor.register_custom_asset_name(f"{name}.ANCS", ammo.new_ancs)

        cmdl_id = editor.duplicate_asset(BEAM_AMMO_EXPANSION_CMDL, f"{name}.CMDL")
        cmdl = editor.get_file(cmdl_id, type_hint=Cmdl)
        cmdl.raw.material_sets[0].texture_file_ids[0] = ammo.txtr_a
        cmdl.raw.material_sets[0].texture_file_ids[2] = ammo.txtr_a
        cmdl.raw.material_sets[0].texture_file_ids[3] = ammo.txtr_b
        cmdl.raw.material_sets[0].texture_file_ids[4] = ammo.txtr_b

        ancs_id = editor.duplicate_asset(BEAM_AMMO_EXPANSION_ANCS, f"{name}.ANCS")
        ancs = editor.get_file(ancs_id, type_hint=Ancs)
        ancs.raw.character_set.characters[0].model_id = ammo.new_cmdl
        ancs.raw.character_set.characters[0].particle_resource_data.generic_particles = [
            0x89C2F268,
            ammo.particle,
        ]
        ancs.raw.animation_set.event_sets[0].particle_poi_nodes[0].particle.id = ammo.particle
        ancs.raw.animation_set.event_sets[0].particle_poi_nodes[1].particle.id = ammo.particle


def _import_premade_assets(editor: PatcherEditor):
    assets = custom_asset_path().joinpath("general")
    for f in assets.rglob("*.*"):
        name = f.name
        asset_type = f.suffix[1:].upper()  # remove leading period, force uppercase
        raw = f.read_bytes()
        editor.add_new_asset(name, RawResource(asset_type, raw), ())


def create_custom_assets(editor: PatcherEditor):
    _import_premade_assets(editor)

    _create_visor_derivatives(editor)
    _create_split_ammo(editor)
