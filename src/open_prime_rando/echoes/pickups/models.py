import copy
import dataclasses

from retro_data_structures.asset_manager import NameOrAssetId
from retro_data_structures.enums.echoes import WorldLightingOptions
from retro_data_structures.formats.ancs import Ancs
from retro_data_structures.formats.cmdl import Cmdl
from retro_data_structures.properties.echoes.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.echoes.core.AssetId import default_asset_id
from retro_data_structures.properties.echoes.core.Color import Color
from retro_data_structures.properties.echoes.core.Vector import Vector

from open_prime_rando.patcher_editor import PatcherEditor


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModelLighting:
    cast_shadow: bool = True
    unk_bool: bool = True
    use_world_lighting: WorldLightingOptions = WorldLightingOptions.NormalWorldLighting
    use_old_lighting: bool = False
    ambient_color: Color = Color(1.0, 1.0, 1.0, 1.0)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModelTransform:
    rotation: Vector = Vector(0.0, 0.0, 0.0)
    scale: Vector = Vector(1.0, 1.0, 1.0)
    orbit_offset: Vector = Vector(0.0, 0.0, 0.0)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PickupModel:
    model: NameOrAssetId = default_asset_id
    scan_model: NameOrAssetId = default_asset_id
    animation: AnimationParameters = AnimationParameters()
    lighting: ModelLighting = ModelLighting()
    transform: ModelTransform = ModelTransform()
    auto_spin: bool = False

    def __post_init__(self):
        if self.model == default_asset_id:
            raise ValueError(f"No model defined for {self}!")


SCAN_VISOR_CMDL   = 0xafc70004
COMBAT_VISOR_CMDL = 0x0B7E6CA9
DARK_VISOR_ANCS   = 0x851b526e

def _create_visor_derivatives(editor: PatcherEditor):
    cmdls = [COMBAT_VISOR_CMDL, SCAN_VISOR_CMDL]

    translators = {
        "violet":  0x4BE5342E,
        "amber":   0xF5308558,
        "emerald": 0xA9640FDF,
        "cobalt":  0x2C56D2D4,
    }
    for name, texture in translators.items():
        cmdl_id = editor.duplicate_asset(SCAN_VISOR_CMDL, f"{name}_translator.CMDL")

        cmdl = editor.get_parsed_asset(cmdl_id, type_hint=Cmdl)
        cmdl.raw.material_sets[0].texture_file_ids[0] = texture
        cmdl.raw.material_sets[0].texture_file_ids[1] = texture
        editor.replace_asset(cmdl_id, cmdl)

        cmdls.append(cmdl_id)

    dark_visor_ancs = editor.get_parsed_asset(DARK_VISOR_ANCS, type_hint=Ancs)
    characters = dark_visor_ancs.raw.character_set.characters
    base_char = characters[0]

    for cmdl_id in cmdls:
        char = copy.copy(base_char)
        char.model_id = cmdl_id
        characters.append(char)

    editor.replace_asset(DARK_VISOR_ANCS, dark_visor_ancs)


def create_custom_models(editor: PatcherEditor):
    pass
