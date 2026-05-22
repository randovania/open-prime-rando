import dataclasses

import pydantic

from open_prime_rando import pydantic_util


@dataclasses.dataclass
class Fun:
    name: str


_DB = {
    "foo": Fun("fun1"),
    "bar": Fun("fun2"),
}

FunByName = pydantic_util.model_by_name(Fun, _DB)


class FunModel(pydantic.BaseModel):
    fun: FunByName


def test_model_by_name() -> None:

    x = FunModel.model_validate({"fun": "foo"})

    assert x.fun.name == "fun1"
