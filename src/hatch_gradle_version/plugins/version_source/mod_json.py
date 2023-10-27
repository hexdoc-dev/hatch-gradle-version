import json
from typing import Annotated, Any

from pydantic import Field, field_validator

from hatch_gradle_version.common.gradle import GradleVersion
from hatch_gradle_version.common.model import GradlePath

from .base import BaseVersionSource


class ModJSONVersionSource(BaseVersionSource):
    PLUGIN_NAME = "mod-json"

    json_path: GradlePath
    key: Annotated[list[str], Field(min_length=1)]

    def get_gradle_version(self) -> GradleVersion:
        with self.json_path.open() as f:
            data = json.load(f)

        raw_version = data
        for key in self.key:
            raw_version = raw_version[key]

        return GradleVersion.from_raw(raw_version, {})

    @field_validator("key", mode="before")
    @classmethod
    def _split_key(cls, value: Any):
        match value:
            case str():
                return value.split(".")
            case _:
                return value
