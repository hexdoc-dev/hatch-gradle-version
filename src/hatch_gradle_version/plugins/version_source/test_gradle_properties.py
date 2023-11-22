from pathlib import Path

from pytest import MonkeyPatch

from hatch_gradle_version.common.gradle import GradleVersion

from .gradle_properties import GradlePropertiesVersionSource


def test_gradle_version(tmp_path: Path, monkeypatch: MonkeyPatch):
    # arrange
    monkeypatch.setenv("HATCH_GRADLE_DIR", "gradle_dir")

    gradle = tmp_path / "gradle_dir" / "gradle.properties"
    gradle.parent.mkdir()
    gradle.write_text("modVersion=0.11.1-7")

    hook = GradlePropertiesVersionSource.from_config(
        tmp_path.as_posix(),
        {
            "source": "json",
            "py-path": "",
            "gradle-path": "gradle.properties",
            "key": "modVersion",
        },
    )

    gradle_version = hook.get_gradle_version()

    assert gradle_version == GradleVersion(
        raw_version="0.11.1-7",
        version="0.11.1",
        rc=7,
        build=None,
        extra_versions={"modVersion": "'0.11.1-7'"},
    )


def test_gloopy(tmp_path: Path, monkeypatch: MonkeyPatch):
    # arrange
    monkeypatch.setenv("HATCH_GRADLE_DIR", "gradle_dir")

    gradle = tmp_path / "gradle_dir" / "gradle.properties"
    gradle.parent.mkdir()
    gradle.write_text("modVersion=1.19.2-0.1.0")

    hook = GradlePropertiesVersionSource.from_config(
        tmp_path.as_posix(),
        {
            "source": "json",
            "py-path": "",
            "gradle-path": "gradle.properties",
            "key": "modVersion",
            "gradle-version-regex": r".+?-(\d+\.\d+\.\d+)",
        },
    )

    gradle_version = hook.get_gradle_version()

    assert gradle_version == GradleVersion(
        raw_version="0.1.0",
        version="0.1.0",
        rc=None,
        build=None,
        extra_versions={"modVersion": "'1.19.2-0.1.0'"},
    )
