import dataclasses
import re
import typing

import pydantic
import pytest
from pydantic_core import PydanticSerializationError

from open_prime_rando import pydantic_util


@dataclasses.dataclass
class Fun:
    name: str


_DB = {
    "foo": Fun("fun1"),
    "bar": Fun("fun2"),
}

FunByName = typing.Annotated[Fun, *pydantic_util.by_name_annotators(Fun, _DB)]


class FunModel(pydantic.BaseModel):
    fun: FunByName


def test_validate_by_name_valid() -> None:
    x = FunModel.model_validate({"fun": "foo"})
    assert x.fun.name == "fun1"


def test_validate_by_name_unknown() -> None:
    with pytest.raises(pydantic.ValidationError, match="Unknown Fun: foo2"):
        FunModel.model_validate({"fun": "foo2"})


def test_validate_by_name_not_string() -> None:
    with pytest.raises(pydantic.ValidationError, match="Expected string Fun name, got int"):
        FunModel.model_validate({"fun": 2})


def test_serialize_valid() -> None:
    x = FunModel(fun=_DB["foo"])

    assert x.model_dump() == {"fun": "foo"}


def test_serialize_unknown() -> None:
    x = FunModel(fun=Fun("kitchen"))

    with pytest.raises(PydanticSerializationError, match=re.escape(r"Fun(name='kitchen') not found in database")):
        x.model_dump()
