#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Final, TypeAlias

JsonScalar: TypeAlias = None | bool | int | float | str
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]

LOCAL_USER_MARKER: Final = "SIL"
INTERNAL_MARKER: Final = "internal"
VERSION_PATTERN: Final = re.compile(r'(?m)^version\s*=\s*"([^"]+)"\s*$')
FORBIDDEN_TEXT_BASE: Final = (
    "C:" + "\\Users\\" + LOCAL_USER_MARKER,
    "C:" + "/Users/" + LOCAL_USER_MARKER,
    "Users\\" + LOCAL_USER_MARKER,
    "Users/" + LOCAL_USER_MARKER,
    INTERNAL_MARKER + " team beta",
    "private GitHub" + " source control",
    "local" + " maintainers",
)
SKIP_DIRS: Final = {
    ".git",
    ".venv",
    ".pytest_cache",
    ".ruff_cache",
    ".basedpyright",
    "__pycache__",
    "dist",
}
TEXT_SUFFIXES: Final = {
    ".json",
    ".md",
    ".py",
    ".yml",
    ".yaml",
    ".toml",
    ".txt",
    ".xml",
    ".java",
    ".jsp",
    ".jsx",
    ".js",
    ".properties",
    ".svg",
}


def load_object(path: Path) -> dict[str, JsonValue]:
    loaded: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return loaded


def project_version(root: Path) -> str:
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    match = VERSION_PATTERN.search(text)
    if match is None:
        raise ValueError("pyproject.toml must contain a project version")
    return match.group(1)


def forbidden_text(version: str) -> tuple[str, ...]:
    return FORBIDDEN_TEXT_BASE + (
        "0.1.0-" + INTERNAL_MARKER + "-beta",
        version + "-" + INTERNAL_MARKER + "-beta",
    )


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def as_dict(value: JsonValue | None) -> dict[str, JsonValue]:
    return value if isinstance(value, dict) else {}


def scan_forbidden_text(root: Path, version: str) -> list[str]:
    findings: list[str] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for forbidden in forbidden_text(version):
            if forbidden in text:
                findings.append(f"{path.relative_to(root)} contains forbidden public-release text: {forbidden}")
    return findings


def validate_codex_manifest(root: Path, version: str, errors: list[str]) -> None:
    manifest = load_object(root / ".codex-plugin" / "plugin.json")
    interface = as_dict(manifest.get("interface"))
    require(manifest.get("name") == "egovframe-guardian", "Codex manifest name must be egovframe-guardian", errors)
    require(manifest.get("version") == version, f"Codex manifest version must be {version}", errors)
    require(str(manifest.get("repository", "")).startswith("https://github.com/"), "Codex manifest repository must be public GitHub URL", errors)
    require(str(manifest.get("homepage", "")).startswith("https://github.com/"), "Codex manifest homepage must be public GitHub URL", errors)
    require(str(interface.get("privacyPolicyURL", "")).startswith("https://github.com/"), "Codex privacyPolicyURL must be public", errors)
    require(str(interface.get("termsOfServiceURL", "")).startswith("https://github.com/"), "Codex termsOfServiceURL must be public", errors)


def validate_claude_manifest(root: Path, version: str, errors: list[str]) -> None:
    manifest = load_object(root / ".claude-plugin" / "plugin.json")
    require(manifest.get("name") == "egovframe-guardian", "Claude manifest name must be egovframe-guardian", errors)
    require(manifest.get("version") == version, f"Claude manifest version must be {version}", errors)
    require(manifest.get("skills") == "./skills", "Claude manifest must expose bundled skills", errors)
    require(manifest.get("hooks") == "./hooks/hooks.json", "Claude manifest must expose bundled hooks", errors)


def validate_codex_marketplace(root: Path, version: str, errors: list[str]) -> None:
    marketplace = load_object(root / ".agents" / "plugins" / "marketplace.json")
    plugins = marketplace.get("plugins")
    require(marketplace.get("name") == "egovframe-guardian", "Codex marketplace name must be egovframe-guardian", errors)
    require(isinstance(plugins, list) and len(plugins) == 1, "Codex marketplace must contain exactly one plugin", errors)
    if not isinstance(plugins, list) or not plugins:
        return
    entry = plugins[0]
    if not isinstance(entry, dict):
        errors.append("Codex marketplace plugin entry must be an object")
        return
    source = as_dict(entry.get("source"))
    policy = as_dict(entry.get("policy"))
    require(entry.get("name") == "egovframe-guardian", "Codex marketplace entry name mismatch", errors)
    require(source.get("source") == "url", "Codex marketplace must use Git URL source for root plugin", errors)
    require(source.get("url") == "https://github.com/unnest-wintenboy/egovframe-guardian.git", "Codex marketplace URL mismatch", errors)
    require(source.get("ref") == f"v{version}", f"Codex marketplace ref must be v{version}", errors)
    require(policy.get("installation") == "AVAILABLE", "Codex marketplace installation policy missing", errors)
    require(policy.get("authentication") == "ON_INSTALL", "Codex marketplace authentication policy missing", errors)
    require(bool(entry.get("category")), "Codex marketplace category missing", errors)


def validate_claude_marketplace(root: Path, version: str, errors: list[str]) -> None:
    marketplace = load_object(root / ".claude-plugin" / "marketplace.json")
    plugins = marketplace.get("plugins")
    owner = as_dict(marketplace.get("owner"))
    require(marketplace.get("name") == "egovframe-guardian", "Claude marketplace name must be egovframe-guardian", errors)
    require(bool(owner.get("name")), "Claude marketplace owner.name is required", errors)
    require(isinstance(plugins, list) and len(plugins) == 1, "Claude marketplace must contain exactly one plugin", errors)
    if not isinstance(plugins, list) or not plugins:
        return
    entry = plugins[0]
    if not isinstance(entry, dict):
        errors.append("Claude marketplace plugin entry must be an object")
        return
    source = as_dict(entry.get("source"))
    require(entry.get("name") == "egovframe-guardian", "Claude marketplace entry name mismatch", errors)
    require(source.get("source") == "github", "Claude marketplace must use GitHub source", errors)
    require(source.get("repo") == "unnest-wintenboy/egovframe-guardian", "Claude marketplace repo mismatch", errors)
    require(source.get("ref") == f"v{version}", f"Claude marketplace ref must be v{version}", errors)
    require(entry.get("version") == version, f"Claude marketplace entry version must be {version}", errors)
    require(bool(entry.get("description")), "Claude marketplace entry description missing", errors)


def validate_release_tag(version: str, errors: list[str]) -> None:
    release_tag = os.environ.get("RELEASE_TAG")
    if release_tag is None or not release_tag.strip():
        return
    require(release_tag == f"v{version}", f"RELEASE_TAG must be v{version}", errors)


def main(argv: list[str]) -> int:
    root = Path(argv[0]).resolve() if argv else Path.cwd()
    errors: list[str] = []
    try:
        version = project_version(root)
        validate_codex_manifest(root, version, errors)
        validate_claude_manifest(root, version, errors)
        validate_codex_marketplace(root, version, errors)
        validate_claude_marketplace(root, version, errors)
        validate_release_tag(version, errors)
        errors.extend(scan_forbidden_text(root, version))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    print("Release package metadata is public-ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
