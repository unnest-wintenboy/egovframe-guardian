# /// script
# requires-python = ">=3.12"
# ///
# ─── How to run ───
# python scripts/audit_coverage.py --skill-dir .

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias


JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]

EXPECTED_SECTIONS = {
    "표준프레임워크 소개",
    "개발가이드",
    "다운로드",
    "개발자 참여",
    "기술지원",
    "호환성확인",
}
MIN_PORTAL_RECORDS = 751
MIN_PORTAL_SEEDS = 60
MIN_REPOSITORIES = 23
MIN_DISTINCT_ZIP_NAMES = 250
REQUIRED_REFERENCE_FILES = {
    "portal-manual-map.md",
    "portal-crawl-records.json",
    "github-clone-manifest.json",
    "repository-directory-atlas.md",
    "repository-directory-index.json",
    "portal-zip-inventory.md",
    "distribution-file-playbook.md",
    "development-playbook.md",
    "example-code-catalog.md",
    "source-refresh.md",
    "coverage-protocol.md",
}
REQUIRED_EXAMPLE_DIRS = {
    "classic-mvc-crud",
    "boot-rest-crud",
    "msa-service",
    "batch-job",
    "security-login",
    "react-client",
}


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    passed: bool
    detail: str


def as_object(value: JsonValue) -> dict[str, JsonValue]:
    if not isinstance(value, dict):
        raise TypeError("expected JSON object")
    return value


def as_list(value: JsonValue) -> list[JsonValue]:
    if not isinstance(value, list):
        raise TypeError("expected JSON list")
    return value


def load_json(path: Path) -> JsonValue:
    value: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    return value


def skill_dir_from_argv(argv: list[str]) -> Path:
    if len(argv) == 1:
        return Path.cwd()
    if len(argv) == 3 and argv[1] == "--skill-dir":
        return Path(argv[2]).resolve()
    raise SystemExit("usage: python scripts/audit_coverage.py --skill-dir <skill-dir>")


def check_reference_files(skill_dir: Path) -> Check:
    reference_dir = skill_dir / "references"
    missing = sorted(name for name in REQUIRED_REFERENCE_FILES if not (reference_dir / name).exists())
    return Check(
        name="reference_files",
        passed=not missing,
        detail="all required references exist" if not missing else ", ".join(missing),
    )


def check_examples(skill_dir: Path) -> Check:
    example_root = skill_dir / "assets" / "examples"
    missing = sorted(name for name in REQUIRED_EXAMPLE_DIRS if not (example_root / name).is_dir())
    return Check(
        name="example_directories",
        passed=not missing,
        detail="all example directories exist" if not missing else ", ".join(missing),
    )


def check_portal(skill_dir: Path) -> list[Check]:
    payload = as_object(load_json(skill_dir / "references" / "portal-crawl-records.json"))
    stats = as_object(payload["stats"])
    records = as_list(payload["records"])
    sections = {str(as_object(record)["section"]) for record in records}
    seed_count = int(str(stats.get("seed_count", 0)))
    missing_sections = sorted(EXPECTED_SECTIONS - sections)
    return [
        Check(
            name="portal_seed_count",
            passed=seed_count >= MIN_PORTAL_SEEDS,
            detail=f"{seed_count} menu seeds",
        ),
        Check(
            name="portal_record_count",
            passed=len(records) >= MIN_PORTAL_RECORDS,
            detail=f"{len(records)} records",
        ),
        Check(
            name="portal_sections",
            passed=not missing_sections,
            detail="all expected sections present" if not missing_sections else ", ".join(missing_sections),
        ),
    ]


def check_portal_zip_inventory(skill_dir: Path) -> list[Check]:
    payload = as_object(load_json(skill_dir / "references" / "portal-crawl-records.json"))
    records = as_list(payload["records"])
    inventory = (skill_dir / "references" / "portal-zip-inventory.md").read_text(encoding="utf-8")
    zip_names: set[str] = set()
    for record in records:
        text = "\n".join(str(value) for value in as_object(record).values())
        for token in text.replace("[", " ").replace("]", " ").replace("(", " ").replace(")", " ").split():
            cleaned = token.strip(".,;:\"'`")
            if cleaned.lower().endswith(".zip"):
                zip_names.add(cleaned)
    policy_markers = [
        "not as embedded binaries",
        "Internal structure not assumed",
        "Verify MD5, SHA1, or SHA256",
    ]
    missing_policy = [marker for marker in policy_markers if marker not in inventory]
    return [
        Check(
            name="portal_zip_mentions",
            passed=len(zip_names) >= MIN_DISTINCT_ZIP_NAMES,
            detail=f"{len(zip_names)} distinct .zip filename mentions",
        ),
        Check(
            name="portal_zip_inventory_policy",
            passed=not missing_policy,
            detail="ZIP metadata and safe inspection policy documented"
            if not missing_policy
            else ", ".join(missing_policy),
        ),
    ]


def check_distribution_workflow(skill_dir: Path) -> Check:
    plugin_root = skill_dir.parents[1]
    script = plugin_root / "scripts" / "egovframe_distribution.py"
    core_script = plugin_root / "scripts" / "egovframe_distribution_core.py"
    playbook = (skill_dir / "references" / "distribution-file-playbook.md").read_text(encoding="utf-8")
    required_markers = [
        "egovframe_distribution.py inspect",
        "checksum",
        "ZIP-slip",
        "temporary or sandbox",
        "script-or-binary",
        "curated diff",
    ]
    missing = [marker for marker in required_markers if marker not in playbook]
    if not script.exists():
        missing.append(str(script.relative_to(plugin_root)))
    if not core_script.exists():
        missing.append(str(core_script.relative_to(plugin_root)))
    return Check(
        name="distribution_file_workflow",
        passed=not missing,
        detail="distribution inspector and safe ZIP application workflow documented"
        if not missing
        else ", ".join(missing),
    )


def check_repositories(skill_dir: Path) -> list[Check]:
    index = as_object(load_json(skill_dir / "references" / "repository-directory-index.json"))
    manifest = as_object(load_json(skill_dir / "references" / "github-clone-manifest.json"))
    repositories = as_list(index["repositories"])
    manifest_repositories = as_list(manifest["repositories"])
    index_names = {str(as_object(repo)["name"]) for repo in repositories}
    manifest_names = {str(as_object(repo)["name"]) for repo in manifest_repositories}
    missing_from_index = sorted(manifest_names - index_names)
    missing_directory_counts = [
        str(as_object(repo)["name"])
        for repo in repositories
        if not as_object(repo).get("directory_counts")
    ]
    return [
        Check(
            name="repository_count",
            passed=len(repositories) >= MIN_REPOSITORIES,
            detail=f"{len(repositories)} repositories",
        ),
        Check(
            name="repository_manifest_match",
            passed=not missing_from_index,
            detail="repository atlas matches manifest" if not missing_from_index else ", ".join(missing_from_index),
        ),
        Check(
            name="repository_directory_counts",
            passed=not missing_directory_counts,
            detail="all repos have directory counts"
            if not missing_directory_counts
            else ", ".join(missing_directory_counts),
        ),
    ]


def check_openai_yaml(skill_dir: Path) -> Check:
    path = skill_dir / "agents" / "openai.yaml"
    text = path.read_text(encoding="utf-8")
    needle = "$egovframe-developer"
    return Check(
        name="openai_default_prompt",
        passed=needle in text,
        detail=f"default prompt mentions {needle}" if needle in text else "default prompt is stale",
    )


def run_checks(skill_dir: Path) -> list[Check]:
    checks = [check_reference_files(skill_dir), check_examples(skill_dir)]
    checks.extend(check_portal(skill_dir))
    checks.extend(check_portal_zip_inventory(skill_dir))
    checks.append(check_distribution_workflow(skill_dir))
    checks.extend(check_repositories(skill_dir))
    checks.append(check_openai_yaml(skill_dir))
    return checks


def main() -> int:
    skill_dir = skill_dir_from_argv(sys.argv)
    checks = run_checks(skill_dir)
    payload = {
        "skill_dir": str(skill_dir),
        "passed": all(check.passed for check in checks),
        "checks": [
            {"name": check.name, "passed": check.passed, "detail": check.detail}
            for check in checks
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
