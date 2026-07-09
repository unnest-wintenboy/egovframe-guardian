from __future__ import annotations

import os
from pathlib import Path

from validate_release_package import (
    project_version,
    validate_claude_marketplace,
    validate_codex_marketplace,
    validate_release_tag,
)

PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def test_release_metadata_uses_project_version() -> None:
    version = project_version(PLUGIN_ROOT)
    errors: list[str] = []

    validate_codex_marketplace(PLUGIN_ROOT, version, errors)
    validate_claude_marketplace(PLUGIN_ROOT, version, errors)

    assert version.count(".") == 2
    assert errors == []


def test_release_tag_validation_rejects_mismatched_tag() -> None:
    previous = os.environ.get("RELEASE_TAG")
    os.environ["RELEASE_TAG"] = "v9.9.9"
    errors: list[str] = []

    try:
        version = project_version(PLUGIN_ROOT)
        validate_release_tag(version, errors)
    finally:
        if previous is None:
            del os.environ["RELEASE_TAG"]
        else:
            os.environ["RELEASE_TAG"] = previous

    assert errors == [f"RELEASE_TAG must be v{project_version(PLUGIN_ROOT)}"]
