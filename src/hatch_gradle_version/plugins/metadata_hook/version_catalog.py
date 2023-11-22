from functools import cached_property
from pathlib import Path

import tomllib
from pydantic import TypeAdapter

from hatch_gradle_version.common.gradle import GradleDependency, GradleVersion
from hatch_gradle_version.common.model import GradlePath

from .base import BaseMetadataHook


class VersionCatalogMetadataHook(BaseMetadataHook):
    PLUGIN_NAME = "version-catalog"

    path: GradlePath = Path("gradle/libs.versions.toml")

    def get_format_value(self, key: str):
        return self.versions[key]

    def parse_gradle_dependency(self, dependency: GradleDependency):
        raw_version = self.versions[dependency.key]
        gradle_version = GradleVersion.from_raw(raw_version, self.versions, None)
        return dependency.version_specifier(gradle_version)

    @cached_property
    def versions(self) -> dict[str, str]:
        with self.path.open("rb") as f:
            version_catalog = tomllib.load(f)

        ta = TypeAdapter(dict[str, str])
        return ta.validate_python(version_catalog["versions"])
