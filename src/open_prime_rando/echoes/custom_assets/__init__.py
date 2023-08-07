import dataclasses
import functools
from pathlib import Path

from retro_data_structures.base_resource import AssetId, NameOrAssetId, RawResource
from retro_data_structures.formats import Ancs, Cmdl

from open_prime_rando.patcher_editor import PatcherEditor


@functools.cache
def custom_asset_path() -> Path:
    return Path(__file__).parent


SCAN_VISOR_CMDL   = 0xafc70004
COMBAT_VISOR_CMDL = 0x0B7E6CA9
DARK_VISOR_ANCS   = 0x851b526e

TRANSLATORS: dict[str, NameOrAssetId] = {
    "violet":   0x4BE5342E,
    "amber":    0xF5308558,
    "emerald":  0xA9640FDF,
    "cobalt":   0x2C56D2D4,
    "crimson":  "custom_translator_holo_crimson.TXTR",
    "obsidian": "custom_translator_holo_obsidian.TXTR",
    "pearl":    "custom_translator_holo_pearl.TXTR",
}

def _create_visor_derivatives(editor: PatcherEditor):
    cmdls = {
        "combat_visor": COMBAT_VISOR_CMDL,
        "scan_visor": SCAN_VISOR_CMDL,
    }

    for name, texture in TRANSLATORS.items():
        texture = editor._resolve_asset_id(texture)
        cmdl_id = editor.duplicate_asset(SCAN_VISOR_CMDL, f"{name}_translator.CMDL")

        with editor.edit_file(cmdl_id, type_hint=Cmdl) as cmdl:
            cmdl.raw.material_sets[0].texture_file_ids[0] = texture
            cmdl.raw.material_sets[0].texture_file_ids[1] = texture

        cmdls[f"{name}_translator"] = cmdl_id

    for name, model in cmdls.items():
        ancs_id = editor.duplicate_asset(DARK_VISOR_ANCS, f"{name}.ANCS")
        with editor.edit_file(ancs_id, type_hint=Ancs) as ancs:
            ancs.raw.character_set.characters[0].model_id = model


@dataclasses.dataclass
class BeamAmmoAssets:
    txtr_a: AssetId
    txtr_b: AssetId
    particle: AssetId

BEAM_AMMO_EXPANSION_CMDL = 0x352c8b02
BEAM_AMMO_EXPANSION_ANCS = 0x4e00188c

BEAM_AMMO = {
    "dark_ammo": BeamAmmoAssets(
        txtr_a  =0x5297270E,
        txtr_b  =0xC3573BC6,
        particle=0x8e0c499d,
    ),
    "light_ammo": BeamAmmoAssets(
        txtr_a  =0x6C3D58AE,
        txtr_b  =0xA3413531,
        particle=0xa180bb7f,
    )
}

def _create_split_ammo(editor: PatcherEditor):
    for name, ammo in BEAM_AMMO.items():
        cmdl_id = editor.duplicate_asset(BEAM_AMMO_EXPANSION_CMDL, f"{name}.CMDL")
        with editor.edit_file(cmdl_id, type_hint=Cmdl) as cmdl:
            cmdl.raw.material_sets[0].texture_file_ids[0] = ammo.txtr_a
            cmdl.raw.material_sets[0].texture_file_ids[2] = ammo.txtr_a
            cmdl.raw.material_sets[0].texture_file_ids[3] = ammo.txtr_b
            cmdl.raw.material_sets[0].texture_file_ids[4] = ammo.txtr_b

        ancs_id = editor.duplicate_asset(BEAM_AMMO_EXPANSION_ANCS, f"{name}.ANCS")
        with editor.edit_file(ancs_id, type_hint=Ancs) as ancs:
            ancs.raw.character_set.characters[0].model_id = ammo.new_cmdl
            ancs.raw.character_set.characters[0].particle_resource_data.generic_particles = [
                0x89C2F268,
                ammo.particle,
            ]
            ancs.raw.animation_set.event_sets[0].particle_poi_nodes[0].particle.id = ammo.particle
            ancs.raw.animation_set.event_sets[0].particle_poi_nodes[1].particle.id = ammo.particle


TEMPLE_KEY_CMDL = 0x5C8C5F22
TEMPLE_KEY_ANCS = 0x41C2513F

def _create_regional_keys(editor: PatcherEditor):
    for name in ("dark_agon", "dark_torvus", "ing_hive"):
        cmdl_id = editor.duplicate_asset(TEMPLE_KEY_CMDL, f"{name}_key.CMDL")
        with editor.edit_file(cmdl_id, type_hint=Cmdl) as cmdl:
            textures = cmdl.raw.material_sets[0].texture_file_ids
            textures[2] = editor._resolve_asset_id(f"{name}_key_base.TXTR")
            textures[3] = editor._resolve_asset_id(f"{name}_key_emissive.TXTR")

        ancs_id = editor.duplicate_asset(TEMPLE_KEY_ANCS, f"{name}_key.ANCS")
        with editor.edit_file(ancs_id, type_hint=Ancs) as ancs:
            ancs.raw.character_set.characters[1].model_id = cmdl_id


def _import_premade_assets(editor: PatcherEditor):
    assets = custom_asset_path().joinpath("general")
    for f in assets.rglob("*.*"):
        name = f.name
        asset_type = f.suffix[1:].upper() # remove leading period, force uppercase
        raw = f.read_bytes()
        editor.add_new_asset(name, RawResource(asset_type, raw), ())


def create_custom_assets(editor: PatcherEditor):
    _import_premade_assets(editor)

    _create_visor_derivatives(editor)
    _create_split_ammo(editor)
    _create_regional_keys(editor)
