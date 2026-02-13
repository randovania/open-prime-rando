import pydantic
from retro_data_structures.enums.echoes import PlayerItemEnum

from open_prime_rando.echoes.pickups.location import PickupLocation
from open_prime_rando.echoes.pickups.model_database import PickupModelByName


class Jingle(pydantic.BaseModel):
    file_name: str
    volume: int


class PickupAppearance(pydantic.BaseModel):
    model_data: PickupModelByName
    sound: int
    jingle: Jingle
    hud_text: str
    scan: str


class ResourceGain(pydantic.BaseModel):
    item: PlayerItemEnum
    amount: int


class ResourceConversion(pydantic.BaseModel):
    from_item: PlayerItemEnum
    to_item: PlayerItemEnum


class PickupStage(pydantic.BaseModel):
    required_item: PlayerItemEnum | None
    resources: list[ResourceGain]
    appearance: PickupAppearance
    conversion: list[ResourceConversion]


class PickupModification(pydantic.BaseModel):
    location: PickupLocation
    stages: list[PickupStage]
