# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false

import re
from functools import cached_property
from pathlib import Path
from typing import Any

import jproperties  # pyright: ignore[reportMissingTypeStubs]
from hatchling.version.source.plugin.interface import VersionSourceInterface

GRADLE_VERSION_RE = re.compile(
    r"""
    v?
    (?P<version>
        \d+
        (?:\.\d+)*
    )
    (?:
        -
        (?P<rc>
            \d+
            (?:\.\d+)*
        )
    )?
    """,
    re.VERBOSE,
)


class PropertiesVersionSource(VersionSourceInterface):
    PLUGIN_NAME = "gradle-properties"

    def get_version_data(self) -> dict[str, Any]:
        p = jproperties.Properties()
        with open(self.full_path, "rb") as f:
            p.load(f, "utf-8")

        parent, pre = self.parse_gradle_version(p)
        pre = f".rc{pre}" if pre is not None else ""

        version = f"{parent}.{self.py_version}{pre}"
        return {"version": version}

    def set_version(self, version: str, version_data: dict[str, Any]) -> None:
        raise NotImplementedError  # TODO: implement

    def parse_gradle_version(self, p: jproperties.Properties) -> tuple[str, str | None]:
        gradle_version = str(p[self.key].data)

        match = GRADLE_VERSION_RE.match(gradle_version)
        if match is None:
            raise ValueError(f"Failed to parse version {self.key}={gradle_version}")

        return match["version"], match["rc"]

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
    def path(self) -> Path:
        match self.config.get("path", "gradle.properties"):
            case str(path_str):
                return Path(path_str)
            case Path() as path:
                return path
            case _:
                raise TypeError(
                    f"Option `path` for version source `{self.PLUGIN_NAME}` must be a string"
                )

    @cached_property
    def key(self) -> str:
        return self.config.get("key", "modVersion")

    @cached_property
    def py_version(self) -> str:
        return self.config["py_version"]
