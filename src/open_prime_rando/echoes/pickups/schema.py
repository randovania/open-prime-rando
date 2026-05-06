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
    resources: list[ResourceGain]
    appearance: PickupAppearance
    conversion: list[ResourceConversion]


class ProgressivePickupStage(PickupStage):
    required_item: PlayerItemEnum


class PickupModification(pydantic.BaseModel):
    """Modifies an existing pickup or create a new one."""

    location: PickupLocation
    """
    The pickup to modify.
    Use StandardPickupLocation for an existing pickup and CustomPickupLocation to create a new one.
    """

    stage: PickupStage
    """
    The intended resources given and appearance of the pickup.
    For progressive pickups, it's the one used when none of the progressive stages requirements are met.
    """

    progressive_stages: list[ProgressivePickupStage]
    """
    Makes this pickup a progressive one, where the resources given and appearance depends on the player having
    certain items.
    """
