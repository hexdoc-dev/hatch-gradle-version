from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError
from typing_extensions import dataclass_transform

DEFAULT_CONFIG = ConfigDict(extra="forbid")


def to_kebab(string: str) -> str:
    return string.replace("_", "-")


@dataclass_transform()
class DefaultModel(BaseModel):
    model_config = DEFAULT_CONFIG

    # workaround for https://github.com/pypa/hatch/issues/959
    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: dict[str, Any] | None = None,
    ):
        try:
            return super().model_validate(
                obj,
                strict=strict,
                from_attributes=from_attributes,
                context=context,
            )
        except ValidationError as e:
            # wrap ValidationError so Hatchling doesn't try to construct it
            raise RuntimeError(e)

    # workaround for https://github.com/pypa/hatch/issues/959
    @classmethod
    def model_validate_json(
        cls,
        json_data: str | bytes | bytearray,
        *,
        strict: bool | None = None,
        context: dict[str, Any] | None = None,
    ):
        try:
            return super().model_validate_json(
                json_data,
                strict=strict,
                context=context,
            )
        except ValidationError as e:
            raise RuntimeError(e)


@dataclass_transform()
class KebabModel(DefaultModel, alias_generator=to_kebab):
    pass
