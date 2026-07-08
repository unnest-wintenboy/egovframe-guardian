#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final, TypeAlias

JsonScalar: TypeAlias = None | bool | int | float | str
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]

REQUIRED_HOOK_EVENTS: Final = (
    "SessionStart",
    "UserPromptSubmit",
    "PreToolUse",
    "PermissionRequest",
    "PostToolUse",
    "SubagentStart",
    "SubagentStop",
    "PostCompact",
    "Stop",
)


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    weight: int
    passed: bool
    detail: str


@dataclass(frozen=True, slots=True)
class ScoreReport:
    score: int
    maximum: int
    checks: tuple[Check, ...]


def parse_args(argv: list[str]) -> tuple[Path, int]:
    root = Path.cwd()
    fail_under = 130
    index = 0
    while index < len(argv):
        token = argv[index]
        if token == "--fail-under" and index + 1 < len(argv):
            fail_under = int(argv[index + 1])
            index += 2
        elif token.startswith("--"):
            raise SystemExit(f"Unknown argument: {token}")
        else:
            root = Path(token)
            index += 1
    return root.resolve(), fail_under


def load_json(path: Path) -> dict[str, JsonValue]:
    loaded: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise SystemExit(f"Expected object JSON: {path}")
    return loaded


def has_all(data: dict[str, JsonValue], keys: tuple[str, ...]) -> bool:
    return all(bool(data.get(key)) for key in keys)


def has_required_hooks(root: Path) -> bool:
    hooks_path = root / "hooks" / "hooks.json"
    if not hooks_path.exists():
        return False
    hooks = load_json(hooks_path).get("hooks")
    if not isinstance(hooks, dict):
        return False
    return all(event in hooks for event in REQUIRED_HOOK_EVENTS)


def score(root: Path) -> ScoreReport:
    manifest = load_json(root / ".codex-plugin" / "plugin.json")
    interface = manifest.get("interface")
    interface_data = interface if isinstance(interface, dict) else {}
    checks = (
        Check("manifest-required", 10, has_all(manifest, ("name", "version", "description", "author", "interface")), "required identity fields"),
        Check("distribution-metadata", 12, has_all(manifest, ("homepage", "repository", "license", "keywords")), "homepage, repository, license, keywords"),
        Check("interface-rich-media", 8, has_all(interface_data, ("brandColor", "composerIcon", "logo", "screenshots")), "brand color, icon, logo, screenshots"),
        Check("public-policy-docs", 8, (root / "docs" / "privacy.md").exists() and (root / "docs" / "terms.md").exists(), "public privacy and terms documents"),
        Check("skill-bundle", 10, (root / "skills" / "egovframe-developer" / "SKILL.md").exists(), "bundled eGovFrame skill"),
        Check("hook-bundle", 10, has_required_hooks(root), "required lifecycle hook configuration"),
        Check(
            "guard-script",
            10,
            (root / "scripts" / "egovframe_guard.py").exists()
            and (root / "scripts" / "egovframe_distribution.py").exists()
            and (root / "scripts" / "egovframe_distribution_core.py").exists(),
            "guard and distribution scripts",
        ),
        Check("hook-policy", 8, (root / "config" / "egovframe-guardian.json").exists(), "severity and suppression policy"),
        Check("readme-docs", 8, (root / "README.md").exists(), "README documentation"),
        Check("license-file", 6, (root / "LICENSE").exists() or (root / "LICENSE.md").exists(), "license file"),
        Check("tests-dir", 10, (root / "tests").exists() and any((root / "tests").glob("test_*.py")), "pytest tests"),
        Check("ci-workflow", 10, (root / ".github" / "workflows" / "ci.yml").exists(), "GitHub Actions CI workflow"),
        Check("codex-marketplace", 8, (root / ".agents" / "plugins" / "marketplace.json").exists(), "Codex marketplace catalog"),
        Check("claude-plugin", 8, (root / ".claude-plugin" / "plugin.json").exists() and (root / ".claude-plugin" / "marketplace.json").exists(), "Claude Code plugin and marketplace metadata"),
        Check("release-workflow", 4, (root / ".github" / "workflows" / "release.yml").exists(), "GitHub release workflow"),
    )
    total = sum(item.weight for item in checks if item.passed)
    return ScoreReport(total, sum(item.weight for item in checks), checks)


def main(argv: list[str]) -> int:
    root, fail_under = parse_args(argv)
    report = score(root)
    payload = {
        "score": report.score,
        "maximum": report.maximum,
        "checks": [
            {"name": item.name, "weight": item.weight, "passed": item.passed, "detail": item.detail}
            for item in report.checks
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if report.score >= fail_under else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
