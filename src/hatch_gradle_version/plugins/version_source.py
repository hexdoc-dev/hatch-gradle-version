from functools import cached_property
from pathlib import Path
from typing import Any

from hatchling.version.source.regex import RegexSource
from pydantic import BaseModel, Field

from ..common.gradle import GradleVersion, load_properties


class PropertiesVersionSourceConfig(BaseModel):
    py_path: str = Field(alias="py-path")

    gradle_path: Path = Field(alias="gradle-path", default=Path("gradle.properties"))
    key: str = "modVersion"


class PropertiesVersionSource(RegexSource):
    PLUGIN_NAME = "gradle-properties"

    def get_version_data(self) -> dict[str, Any]:
        # load gradle version from gradle.properties
        p = load_properties(self.gradle_path)
        gradle = GradleVersion.from_properties(p, self.key)

        # use the regex source to load py_version from a file
        self.config["path"] = self.py_path
        py_version_data = super().get_version_data()
        py_version = py_version_data["version"]

        return py_version_data | {
            "version": gradle.full_version(py_version),
            "gradle_version": gradle,
            "py_version": py_version,
        }

    def set_version(self, version: str, version_data: dict[str, Any]) -> None:
        super().set_version(version_data["py_version"], version_data)

    # config values

    @cached_property
    def typed_config(self):
        return PropertiesVersionSourceConfig.model_validate(self.config)

    @property
    def gradle_path(self):
        path = Path(self.root) / self.typed_config.gradle_path
        if not path.is_file():
            raise FileNotFoundError(
                f"File does not exist or is not a file: {self.typed_config.gradle_path}"
            )
        return path

    @property
    def key(self):
        return self.typed_config.key

    @property
    def py_path(self):
        return self.typed_config.py_path
