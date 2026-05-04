from typing import Any

from jsonschema import Draft7Validator, validators
from jsonschema.protocols import Validator


def extend_with_default(validator_class: type[Validator]) -> type[Validator]:
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator: Any, properties: Any, instance: Any, schema: Any):
        for prop, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(prop, subschema["default"])

        yield from validate_properties(
            validator,
            properties,
            instance,
            schema,
        )

    return validators.extend(
        validator_class,
        {"properties": set_defaults},
    )


DefaultValidatingDraft7Validator = extend_with_default(Draft7Validator)
