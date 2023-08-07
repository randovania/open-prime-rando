import dataclasses

from retro_data_structures.asset_manager import NameOrAssetId
from retro_data_structures.enums.echoes import WorldLightingOptions
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


@dataclasses.dataclass
class ModelAnim:
    ancs: NameOrAssetId = default_asset_id
    character_index: int = 0

    def get_animation_parameters(self, editor: PatcherEditor) -> AnimationParameters:
        return AnimationParameters(
            ancs=editor._resolve_asset_id(self.ancs),
            character_index=self.character_index,
        )


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
