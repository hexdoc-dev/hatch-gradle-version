from __future__ import annotations

import re
from pathlib import Path

import jproperties  # pyright: ignore[reportMissingTypeStubs]
from pydantic import BaseModel, Field

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


class GradleVersion(BaseModel):
    version: str
    raw_rc: str | None = Field(alias="rc")

    @classmethod
    def from_properties(cls, p: jproperties.Properties, key: str):
        raw_version = str(p[key].data)

        match = GRADLE_VERSION_RE.match(raw_version)
        if match is None:
            raise ValueError(f"Failed to parse version {key}={raw_version}")

        return cls.model_validate(match.groupdict())

    def full_version(self, py_version: str, suffix: str) -> str:
        return f"{self.version}.{py_version}{self.rc}{suffix}"

    def next_full_rc_version(self, py_version: str, suffix: str) -> str:
        return f"{self.version}.{py_version}{self.next_rc}{suffix}"

    @property
    def rc(self):
        if self.raw_rc is None:
            return ""
        return f"rc{self.raw_rc}"

    @property
    def next_rc(self):
        if self.raw_rc is None:
            raise ValueError("Tried to call next_rc on a non-rc version")

        *rest, last_num = self.raw_rc.rsplit(".", 1)
        rest = rest[0] if rest else ""

        return f"rc{rest}{int(last_num) + 1}"


def load_properties(path: Path):
    p = jproperties.Properties()
    with open(path, "rb") as f:
        p.load(f, "utf-8")
    return p
