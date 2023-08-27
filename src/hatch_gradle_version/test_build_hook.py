from pathlib import Path
from typing import Any

import pytest

from .build_hook import GradlePropertiesBuildHook
from .cd import cd

testdata = [
    ("PACKAGE", "~=", "KEY", "4", "1.2.3", "PACKAGE~=1.2.3.4"),
    ("PACKAGE", "~=", "KEY", "4.5", "1.2.3", "PACKAGE~=1.2.3.4.5"),
    ("PACKAGE", ">=", "KEY", "4.5", "1.2.3", "PACKAGE>=1.2.3.4.5"),
    ("PACKAGE", "~=", "KEY", "4.5", "1.2.3-6", "PACKAGE~=1.2.3.4.5rc6,<1.2.3.4.5rc7"),
]


@pytest.mark.parametrize(
    "package,op,key,py_version,gradle_version,full_version", testdata
)
def test_gradle_properties_deps(
    tmp_path: Path,
    gradle_version: str,
    package: str,
    op: str,
    key: str,
    py_version: str,
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
