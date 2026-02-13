import typing

import pydantic
from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats.script_object import Connection, InstanceId
from retro_data_structures.properties.echoes.core.Vector import Vector


def _validate_instance_id(value: typing.Any) -> InstanceId:
    if isinstance(value, InstanceId):
        return value
    if isinstance(value, int):
        if value < 0 or value > 0xFFFFFFFF:
            raise ValueError(f"InstanceId must be a positive 32-bit integer (0 to 0xFFFFFFFF), got {value}")
        return InstanceId(value)
    raise ValueError(f"Cannot convert {type(value).__name__} to InstanceId")


def _serialize_instance_id(value: InstanceId) -> int:
    return int(value)


PydanticInstanceId = typing.Annotated[
    InstanceId,
    pydantic.PlainValidator(_validate_instance_id),
    pydantic.PlainSerializer(_serialize_instance_id, return_type=int),
]


class PydanticConnection(pydantic.BaseModel):
    state: State
    message: Message
    target: PydanticInstanceId

    @property
    def as_connection(self) -> Connection:
        return Connection(
            state=self.state,
            message=self.message,
            target=self.target,
        )


def _validate_vector(value: typing.Any) -> Vector:
    if isinstance(value, Vector):
        return value
    if isinstance(value, (list, tuple)):
        if len(value) != 3:
            raise ValueError(f"Vector must have exactly 3 elements, got {len(value)}")
        try:
            return Vector(float(value[0]), float(value[1]), float(value[2]))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Vector elements must be floats: {e}")
    raise ValueError(f"Cannot convert {type(value).__name__} to Vector")


def _serialize_vector(value: Vector) -> list[float]:
    return [value.x, value.y, value.z]


PydanticVector = typing.Annotated[
    Vector,
    pydantic.PlainValidator(_validate_vector),
    pydantic.PlainSerializer(_serialize_vector, return_type=list[float]),
    pydantic.WithJsonSchema(
        {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 3,
            "maxItems": 3,
            "description": "A 3D vector [x, y, z]",
        }
    ),
]
