import os
from functools import cached_property
from pathlib import Path
from typing import Any

import jproperties  # pyright: ignore[reportMissingTypeStubs]
from hatchling.bridge.app import Application
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from pydantic import BaseModel, Field, model_validator

from ..common.gradle import GradleVersion, load_properties


class GradleDependency(BaseModel):
    package: str
    op: str
    key: str
    py_version: str = Field(alias="py-version")
    rc_upper_bound: bool = Field(alias="rc-upper-bound", default=False)
    """If True and gradle_version has a pre-release suffix (eg. `0.1.0-1`), add a
    corresponding exclusive upper bound for the next RC version (eg. `<0.1.0.1.0rc2`).
    
    If True, the operators `>=` and `~=` effectively become `==`. If False, pip may
    install a later prerelease or a released version. There's not really a "best"
    option, which is why this flag exists.

    The default is `False`. We think this *should* work in more cases than not.
    """

    def version_specifier(self, p: jproperties.Properties, app: Application):
        gradle = self.gradle_version(p)

        full_version = gradle.full_version(self.py_version)
        lower_bound = self.op + full_version

        if not (gradle.rc is not None and self.rc_upper_bound):
            return self.package + lower_bound

        if "<" not in self.op:
            app.display_warning(
                f"WARNING: Dependency on package {self.package} will ONLY accept {full_version} (because gradle_version {self.gradle_version} is a prerelease)."
            )

        upper_bound = "<" + gradle.full_version(self.py_version, next_rc=True)
        return f"{self.package}{lower_bound},{upper_bound}"

    def gradle_version(self, p: jproperties.Properties):
        return GradleVersion.from_properties(p, self.key)


class GradlePropertiesBuildHookConfig(BaseModel):
    path: Path = Path("gradle.properties")
    gradle_dependencies: list[GradleDependency] = Field(alias="gradle-dependencies")

    @model_validator(mode="after")
    def _prepend_gradle_dir(self):
        gradle_dir = os.getenv("HATCH_GRADLE_DIR")
        if gradle_dir is None:
            return self

        self.path = Path(gradle_dir) / self.path
        return self


# TODO: this should probably be a metadata hook, actually
class GradlePropertiesBuildHook(BuildHookInterface[Any]):
    PLUGIN_NAME = "gradle-properties"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        build_data.setdefault("dependencies", [])

        p = load_properties(self.path)
        for dependency in self.gradle_dependencies:
            build_data["dependencies"].append(dependency.version_specifier(p, self.app))

    @cached_property
    def typed_config(self):
        return GradlePropertiesBuildHookConfig.model_validate(self.config)

    @property
    def path(self):
        return self.typed_config.path

    @property
    def gradle_dependencies(self):
        return self.typed_config.gradle_dependencies
