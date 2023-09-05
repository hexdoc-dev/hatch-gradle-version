import copy
from pathlib import Path
from typing import Any

import pytest

from ..common.cd import cd
from .metadata_hook import GradlePropertiesMetadataHook


@pytest.mark.parametrize(
    # fmt: off
    "package, op,key,py_version,gradle_version,rc_upper_bound,full_version",
    [
        ("P", "~=", "KEY", "4",       "1.2.3",   False, "P~=1.2.3.4"),
        ("P", "~=", "KEY", "4.5",     "1.2.3",   False, "P~=1.2.3.4.5"),
        ("P", ">=", "KEY", "4.5",     "1.2.3",   False, "P>=1.2.3.4.5"),
        ("P", "~=", "KEY", "4.5",     "1.2.3-6", False, "P~=1.2.3.4.5rc6"),
        ("P", "~=", "KEY", "4.5",     "1.2.3-6", True,  "P~=1.2.3.4.5rc6,<1.2.3.4.5rc7"),
        ("P", "~=", "KEY", "4.5dev6", "1.2.3",   False, "P~=1.2.3.4.5.dev6"),
        ("P", "~=", "KEY", "4.5dev7", "1.2.3-6", False, "P~=1.2.3.4.5rc6.dev7"),
        ("P", "~=", "KEY", "4.5dev8", "1.2.3-6", True,  "P~=1.2.3.4.5rc6.dev8,<1.2.3.4.5rc7.dev8"),
    ],
    # fmt: on
)
def test_gradle_properties_deps(
    tmp_path: Path,
    package: str,
    op: str,
    key: str,
    py_version: str,
    gradle_version: str,
    rc_upper_bound: bool,
    full_version: str,
):
    # arrange
    hook = GradlePropertiesMetadataHook(
        root="",
        config={
            "dependencies": [
                {
                    "package": package,
                    "op": op,
                    "key": key,
                    "py-version": py_version,
                    "rc-upper-bound": rc_upper_bound,
                }
            ],
        },
    )
    (tmp_path / "gradle.properties").write_text(f"{key}={gradle_version}")
    orig_metadata = {
        "dynamic": ["dependencies", "optional-dependencies"],
    }

    # act
    metadata: dict[str, Any] = copy.deepcopy(orig_metadata)
    with cd(tmp_path):
        hook.update(metadata)

    # assert
    assert metadata == orig_metadata | {
        "dependencies": [full_version],
        "optional-dependencies": {},
    }
