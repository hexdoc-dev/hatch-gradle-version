from pathlib import Path
from typing import Any

import pytest

from .build_hook import GradlePropertiesBuildHook
from .cd import cd


@pytest.mark.parametrize(
    "package,op,key,py_version,gradle_version,rc_upper_bound,full_version",
    [
        ("P", "~=", "KEY", "4", "1.2.3", False, "P~=1.2.3.4"),
        ("P", "~=", "KEY", "4.5", "1.2.3", False, "P~=1.2.3.4.5"),
        ("P", ">=", "KEY", "4.5", "1.2.3", False, "P>=1.2.3.4.5"),
        ("P", "~=", "KEY", "4.5", "1.2.3-6", False, "P~=1.2.3.4.5rc6"),
        ("P", "~=", "KEY", "4.5", "1.2.3-6", True, "P~=1.2.3.4.5rc6,<1.2.3.4.5rc7"),
    ],
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
    hook = GradlePropertiesBuildHook(
        root="",
        config={
            "gradle-dependencies": [
                {
                    "package": package,
                    "op": op,
                    "key": key,
                    "py-version": py_version,
                    "rc-upper-bound": rc_upper_bound,
                }
            ],
        },
        build_config=None,
        metadata=None,  # type: ignore
        directory="",
        target_name="",
        app=None,
    )
    build_data = dict[str, Any]()
    (tmp_path / "gradle.properties").write_text(f"{key}={gradle_version}")

    # act
    with cd(tmp_path):
        hook.initialize("", build_data)

    # assert
    assert build_data["dependencies"] == [full_version]
