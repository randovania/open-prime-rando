import typing
from collections.abc import Mapping

from pydantic import BeforeValidator, PlainSerializer, WithJsonSchema


def by_name_annotators[T](
    base_type: type[T],
    database: Mapping[str, T],
) -> list:
    """
    Provides the necessary typing.Annotation fields for configuring Pydantic to fetch instances from a mapping by name,
    when de-serializing.

    >>> PickupModelByName = typing.Annotated[PickupModel, *pydantic_util.by_name_annotators(PickupModel, PICKUP_MODELS)]
    """

    def _validate_name(value: typing.Any) -> T:
        if isinstance(value, base_type):
            return value
        if not isinstance(value, str):
            raise ValueError(f"Expected string {base_type.__name__} name, got {type(value).__name__}")
        if value not in database:
            raise ValueError(f"Unknown {base_type.__name__}: {value}. Valid options: {', '.join(database.keys())}")
        return database[value]

    def _serialize_name(value: T) -> str:
        for name, model in database.items():
            if model is value:
                return name
        raise ValueError(f"{value} not found in database")

    return [
        BeforeValidator(_validate_name),
        PlainSerializer(_serialize_name, return_type=str),
        WithJsonSchema({"type": "string", "enum": list(database.keys())}),
    ]
