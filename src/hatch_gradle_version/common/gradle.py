from __future__ import annotations

import re
from pathlib import Path

import jproperties  # pyright: ignore[reportMissingTypeStubs]
from packaging.version import Version
from pydantic import BaseModel

GRADLE_VERSION_RE = re.compile(
    r"""
    v?
    (?P<version>
        \d+
        (?:\.\d+)*
    )
    (?:
        -
        (?P<rc>\d+)
    )?
    """,
    re.VERBOSE,
)


class GradleVersion(BaseModel):
    raw_version: str
    version: str
    rc: int | None

    @classmethod
    def from_properties(cls, p: jproperties.Properties, key: str):
        raw_version = str(p[key].data)

        match = GRADLE_VERSION_RE.match(raw_version)
        if match is None:
            raise ValueError(f"Failed to parse version {key}={raw_version}")

        return cls.model_validate(match.groupdict() | {"raw_version": raw_version})

    def full_version(
        self,
        py_version: str | Version,
        *,
        next_rc: bool = False,
    ) -> str:
        # ensure py_version is a valid version by itself
        if isinstance(py_version, str):
            py_version = Version(py_version)

        if py_version.pre:
            raise ValueError("a/b/c/pre/rc is reserved for Gradle prereleases")

        # split py_version at the point where we need to insert the gradle prerelease
        py_base = py_version.base_version
        py_rest = str(py_version).removeprefix(py_base)

        # construct the full version
        # eg. 1.2.3 . 4.5 rc6 .dev7
        rc = self.rc_segment(next_rc)
        full_version = self.version + "." + py_base + rc + py_rest

        # round-trip through Version to normalize it
        return str(Version(full_version))

    def rc_segment(self, next_rc: bool):
        if self.rc is None:
            return ""
        return f"rc{self.next_rc if next_rc else self.rc}"

    @property
    def next_rc(self):
        if self.rc is None:
            raise ValueError("Tried to call next_rc on a non-rc version")
        return self.rc + 1

    def __str__(self) -> str:
        return self.raw_version


def load_properties(path: Path):
    p = jproperties.Properties()
    with open(path, "rb") as f:
        p.load(f, "utf-8")
    return p
