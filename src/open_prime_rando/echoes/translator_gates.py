from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Annotated, Literal

import pydantic
from retro_data_structures.base_resource import AssetId, NameOrAssetId
from retro_data_structures.enums.echoes import PlayerItemEnum
from retro_data_structures.formats import Cmdl, Txtr
from retro_data_structures.properties.echoes.core.AssetId import default_asset_id
from retro_data_structures.properties.echoes.objects import Actor, ConditionalRelay

from open_prime_rando.echoes.pydantic_models import PydanticInstanceId

if TYPE_CHECKING:
    from retro_data_structures.formats import Mlvl
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.patcher_editor import PatcherEditor


type TranslatorRequirement = Literal["violet", "amber", "emerald", "cobalt", "unlocked"]


@dataclasses.dataclass(frozen=True, kw_only=True)
class GateHoloInstances(pydantic.BaseModel):
    hologram: Annotated[PydanticInstanceId | str, Actor]
    glow: Annotated[PydanticInstanceId | str, Actor]


@dataclasses.dataclass(frozen=True, kw_only=True)
class TranslatorGateModification(pydantic.BaseModel):
    holo1: GateHoloInstances = GateHoloInstances(
        hologram="Gate Holo 1",
        glow="Glow For Holo 1",
    )
    holo2: GateHoloInstances = GateHoloInstances(
        hologram="Gate Holo 2",
        glow="Glow For Holo 2",
    )
    conditional_relay: Annotated[PydanticInstanceId | str, ConditionalRelay] = "Translator Check"
    translator: TranslatorRequirement


@dataclasses.dataclass(frozen=True, kw_only=True)
class TranslatorData:
    holo_texture: Annotated[NameOrAssetId, Txtr]
    glow_model: Annotated[AssetId, Cmdl]
    item_requirement: PlayerItemEnum


TRANSLATOR_DATA: dict[TranslatorRequirement, TranslatorData] = {
    "violet": TranslatorData(
        holo_texture="consistent_holo_violet.TXTR",
        glow_model=0x0E264630,
        item_requirement=PlayerItemEnum.VioletTranslator,
    ),
    "amber": TranslatorData(
        holo_texture="consistent_holo_amber.TXTR",
        glow_model=0xB9824E7E,
        item_requirement=PlayerItemEnum.AmberTranslator,
    ),
    "emerald": TranslatorData(
        holo_texture="consistent_holo_emerald.TXTR",
        glow_model=0xB9347860,
        item_requirement=PlayerItemEnum.EmeraldTranslator,
    ),
    "cobalt": TranslatorData(
        holo_texture="consistent_holo_cobalt.TXTR",
        glow_model=0xF2DE555A,
        item_requirement=PlayerItemEnum.CobaltTranslator,
    ),
    "unlocked": TranslatorData(
        holo_texture=default_asset_id,
        glow_model=default_asset_id,
        item_requirement=PlayerItemEnum.ScanVisor,
    ),
}


def patch_translator_gate(
    editor: PatcherEditor, mlvl: Mlvl, area: Area, modification: TranslatorGateModification
) -> None:
    translator_data = TRANSLATOR_DATA[modification.translator]

    # edit glow color
    for glow_id in (modification.holo1.glow, modification.holo2.glow):
        glow = area.get_instance(glow_id)
        with glow.edit_properties(Actor) as glow_props:
            glow_props.model = translator_data.glow_model

    # edit hologram color
    if translator_data.holo_texture == default_asset_id:
        holo_model_id = default_asset_id

    else:
        # use holo1 as the reference model, because sanc temple's holo2 has the wrong model lol
        hologram = area.get_instance(modification.holo1.hologram)
        original_model_id = hologram.get_properties_as(Actor).model

        # include an instance ID in the name, to ensure all gates hash uniquely
        new_model_name = f"translator_gate_holo_{hologram.id}.CMDL"

        # create a new model for this gate's hologram
        new_model_id = editor.duplicate_asset(original_model_id, new_model_name)
        new_model = editor.get_file(new_model_id, Cmdl)
        texture_id = editor.resolve_asset_id(translator_data.holo_texture)
        new_model.raw.material_sets[0].texture_file_ids[0] = texture_id

        holo_model_id = new_model_id

    for holo_id in (modification.holo1.hologram, modification.holo2.hologram):
        holo = area.get_instance(holo_id)
        with holo.edit_properties(Actor) as holo_props:
            holo_props.model = holo_model_id

    # edit item requirement
    with area.get_instance(modification.conditional_relay).edit_properties(ConditionalRelay) as conditional:
        conditional.conditional1.player_item = translator_data.item_requirement
