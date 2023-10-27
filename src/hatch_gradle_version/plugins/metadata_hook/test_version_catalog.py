import copy
from pathlib import Path
from textwrap import dedent

from pytest import MonkeyPatch

from .version_catalog import VersionCatalogMetadataHook


def test_gradle_properties_deps(tmp_path: Path, monkeypatch: MonkeyPatch):
    # arrange
    monkeypatch.setenv("HATCH_GRADLE_DIR", "gradle_dir")

    version_catalog = tmp_path / "gradle_dir" / "gradle" / "my-libs.versions.toml"
    version_catalog.parent.mkdir(parents=True)
    version_catalog.write_text(
        dedent(
            f"""\
            [versions]
            K = "1.2.3"
            """
        )
    )

    hook = VersionCatalogMetadataHook(
        tmp_path.as_posix(),
        {
            "path": "gradle/my-libs.versions.toml",
            "dependencies": [
                {
                    "package": "P",
                    "op": "~=",
                    "key": "K",
                    "py-version": "4.5",
                }
            ],
        },
    )

    orig_metadata = {
        "dynamic": [
            "dependencies",
            "optional-dependencies",
        ],
    }

    # act
    metadata = copy.deepcopy(orig_metadata)
    hook.update(metadata)

    # assert
    assert metadata == orig_metadata | {
        "dependencies": ["P~=1.2.3.4.5"],
        "optional-dependencies": {},
    }
