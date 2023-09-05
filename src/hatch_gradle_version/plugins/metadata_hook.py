import os
from functools import cached_property
from pathlib import Path
from typing import Any

from hatchling.metadata.plugin.interface import MetadataHookInterface
from pydantic import Field, model_validator

from hatch_gradle_version.common.decorators import listify

from ..common.gradle import GradleDependency, load_properties
from ..common.model import KebabModel

Dependencies = list[str | GradleDependency]


class GradlePropertiesMetadataHook(MetadataHookInterface):
    PLUGIN_NAME = "gradle-properties"

    def update(self, metadata: dict[str, Any]) -> None:
        self.set_dynamic(
            metadata,
            "dependencies",
            self.parse_dependencies(self.typed_config.dependencies),
        )

        self.set_dynamic(
            metadata,
            "optional-dependencies",
            {
                key: self.parse_dependencies(value)
                for key, value in self.typed_config.optional_dependencies.items()
            },
        )

    @listify
    def parse_dependencies(self, dependencies: Dependencies):
        for dependency in dependencies:
            match dependency:
                case str():
                    yield dependency
                case GradleDependency():
                    yield dependency.version_specifier(self.properties)

    def set_dynamic(self, metadata: dict[str, Any], key: str, value: Any):
        if key in metadata:
            raise ValueError(
                f"`{key}` may not be listed in the `project` table when using hatch-gradle-version to populate dependencies. Please use `tool.hatch.metadata.hooks.{self.PLUGIN_NAME}.{key}` instead."
            )
        if key not in metadata.get("dynamic", []):
            raise ValueError(
                f"`{key}` must be listed in `project.dynamic` when using hatch-gradle-version to populate dependencies."
            )
        metadata[key] = value

    @cached_property
    def typed_config(self):
        return self.Config.model_validate(self.config)

    @cached_property
    def properties(self):
        return load_properties(self.typed_config.path)

    class Config(KebabModel):
        dependencies: Dependencies = Field(default_factory=list)
        optional_dependencies: dict[str, Dependencies] = Field(default_factory=dict)
        path: Path = Path("gradle.properties")

        @model_validator(mode="after")
        def _prepend_gradle_dir(self):
            gradle_dir = os.getenv("HATCH_GRADLE_DIR")
            if gradle_dir is None:
                return self

            self.path = Path(gradle_dir) / self.path
            return self
