from pathlib import Path
from textwrap import dedent

from pytest import MonkeyPatch

from hatch_gradle_version.common.gradle import GradleVersion

from .json import JSONVersionSource


def test_json_version(tmp_path: Path, monkeypatch: MonkeyPatch):
    # arrange
    monkeypatch.setenv("HATCH_GRADLE_DIR", "gradle_dir")

    json = tmp_path / "gradle_dir" / "mod.json"
    json.parent.mkdir()
    json.write_text(
        dedent(
            """
            {
                "core": {
                    "name": "hexbound",
                    "version": "0.1.4+1.19.2",
                    "repository": "https://github.com/Cypher121/hexbound/"
                },
                "platforms": {
                    "modrinth": {
                        "id": "PHgo4bVw"
                    },
                    "curseforge": {
                        "id": "739791"
                    }
                }
            }
            """
        )
    )

    hook = JSONVersionSource.from_config(
        tmp_path.as_posix(),
        {
            "source": "json",
            "py-path": "",
            "json-path": "mod.json",
            "key": "core.version",
        },
    )

    gradle_version = hook.get_gradle_version()

    assert gradle_version == GradleVersion(
        raw_version="0.1.4+1.19.2",
        version="0.1.4",
        rc=None,
        build="1.19.2",
        extra_versions={},
    )
