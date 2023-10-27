from functools import cached_property
from pathlib import Path
from typing import Any

from hatchling.metadata.plugin.interface import MetadataHookInterface
from pydantic import Field

from hatch_gradle_version.common.decorators import listify
from hatch_gradle_version.common.gradle import GradleDependency, load_properties
from hatch_gradle_version.common.model import GradlePath, HookModel

Dependencies = list[str | GradleDependency]


class GradlePropertiesMetadataHook(HookModel, MetadataHookInterface):
    PLUGIN_NAME = "gradle-properties"

    dependencies: Dependencies = Field(default_factory=dict)
    optional_dependencies: dict[str, Dependencies] = Field(default_factory=dict)
    path: GradlePath = Path("gradle.properties")

    def update(self, metadata: dict[str, Any]) -> None:
        """Implements MetadataHookInterface."""
        self.set_dynamic(
            metadata,
            "dependencies",
            self.parse_dependencies(self.dependencies),
        )

        self.set_dynamic(
            metadata,
            "optional-dependencies",
            {
                key: self.parse_dependencies(value)
                for key, value in self.optional_dependencies.items()
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
    def properties(self):
        return load_properties(self.path)
