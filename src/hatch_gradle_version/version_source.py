from functools import cached_property
from pathlib import Path
from typing import Any

from hatchling.version.source.plugin.interface import VersionSourceInterface
from pydantic import BaseModel, Field

from .gradle import GradleVersion, load_properties


class PropertiesVersionSourceConfig(BaseModel):
    py_version: str = Field(alias="py-version")

    path: Path = Path("gradle.properties")
    key: str = "modVersion"


class PropertiesVersionSource(VersionSourceInterface):
    PLUGIN_NAME = "gradle-properties"

    def get_version_data(self) -> dict[str, Any]:
        p = load_properties(self.full_path)
        gradle = GradleVersion.from_properties(p, self.key)

        return {
            "version": gradle.full_version(self.py_version, ""),
        }

    def set_version(self, version: str, version_data: dict[str, Any]) -> None:
        raise NotImplementedError  # TODO: implement

    @property
    def full_path(self):
        path = Path(self.root) / self.path
        if not path.is_file():
            raise FileNotFoundError(
                f"File does not exist or is not a file: {self.path}"
            )
        return path

    # config values

    @cached_property
    def typed_config(self):
        return PropertiesVersionSourceConfig.model_validate(self.config)

    @property
    def py_version(self):
        return self.typed_config.py_version

    @property
    def path(self):
        return self.typed_config.path

    @property
    def key(self):
        return self.typed_config.key
