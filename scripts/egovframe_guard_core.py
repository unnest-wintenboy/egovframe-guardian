from __future__ import annotations

import fnmatch
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import TypeAlias

JsonScalar: TypeAlias = None | bool | int | float | str
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


class Severity(StrEnum):
    OFF = "off"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class Finding:
    severity: Severity
    rule: str
    path: str
    detail: str


@dataclass(frozen=True, slots=True)
class Suppression:
    rule: str
    path: str
    reason: str


@dataclass(frozen=True, slots=True)
class Policy:
    rules: dict[str, Severity]
    suppressions: tuple[Suppression, ...]


@dataclass(frozen=True, slots=True)
class ScanResult:
    root: Path
    detected: bool
    findings: tuple[Finding, ...]
    inspected: int

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.findings if item.severity == Severity.WARNING)


EXCLUDED = {".git", ".gradle", ".idea", ".settings", "__pycache__", "bin", "build", "dist", "node_modules", "target"}
SUFFIXES = {".gradle", ".java", ".jsp", ".properties", ".sql", ".ts", ".tsx", ".xml", ".yaml", ".yml"}
NAMES = {"pom.xml", "settings.gradle", "build.gradle", "Dockerfile"}
SQL = re.compile(r"\"[^\"\n]{0,240}\b(select|insert|update|delete|merge)\b\s+[^\"\n]{0,240}\b(from|into|set|where)\b[^\"\n]{0,240}\"", re.IGNORECASE)
SECRET = re.compile(r"(?i)\b(password|passwd|secret|token|api[-_]?key|access[-_]?key)\b\s*[:=]\s*(.+)")
WRITE_METHOD = re.compile(r"\b(create|insert|update|delete|save|remove|archive)[A-Z_\(]")


def load_policy(plugin_root: Path, project_root: Path) -> Policy:
    policy_paths = (plugin_root / "config" / "egovframe-guardian.json", project_root / ".egovframe-guardian.json")
    rules: dict[str, Severity] = {}
    suppressions: list[Suppression] = []
    for path in policy_paths:
        if path.exists():
            data: JsonValue = json.loads(path.read_text(encoding="utf-8-sig"))
            if isinstance(data, dict):
                rules.update(parse_rules(data.get("rules")))
                suppressions.extend(parse_suppressions(data.get("suppressions")))
    return Policy(rules, tuple(suppressions))


def parse_rules(raw: JsonValue) -> dict[str, Severity]:
    if not isinstance(raw, dict):
        return {}
    parsed: dict[str, Severity] = {}
    for key, value in raw.items():
        if isinstance(value, str):
            match value:
                case "off" | "info" | "warning" | "error":
                    parsed[key] = Severity(value)
                case _:
                    continue
    return parsed


def parse_suppressions(raw: JsonValue) -> list[Suppression]:
    if not isinstance(raw, list):
        return []
    parsed: list[Suppression] = []
    for item in raw:
        if isinstance(item, dict):
            rule = item.get("rule")
            path = item.get("path")
            reason = item.get("reason")
            if isinstance(rule, str) and isinstance(path, str) and isinstance(reason, str):
                parsed.append(Suppression(rule, path, reason))
    return parsed


def collect_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.name in NAMES or root.suffix in SUFFIXES else []
    files: list[Path] = []
    pending = [root]
    while pending:
        current = pending.pop()
        try:
            children = list(current.iterdir())
        except PermissionError:
            continue
        for child in children:
            if child.is_dir() and child.name not in EXCLUDED and not any(part in EXCLUDED for part in child.parts):
                pending.append(child)
            elif child.is_file() and (child.name in NAMES or child.suffix in SUFFIXES):
                files.append(child)
            if len(files) >= 2500:
                return files
    return files


def read_text(path: Path) -> str:
    return path.read_bytes()[:350_000].decode("utf-8", errors="ignore")


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def is_egov_project(files: list[Path]) -> bool:
    has_build_marker = False
    has_path_marker = False
    for path in files:
        lowered = path.as_posix().lower()
        if path.name in {"pom.xml", "build.gradle"}:
            build = read_text(path).lower()
            has_build_marker = has_build_marker or "egovframework" in build or "org.egovframe" in build
        has_path_marker = has_path_marker or "egovframework" in lowered or "org/egovframe" in lowered
    return has_build_marker or has_path_marker


def secret_is_safe(value: str) -> bool:
    lowered = value.strip().strip("\"'").lower()
    safe = ("${", "#{", "$$", "enc(", "change-me", "changeme", "example", "sample", "todo", "your-")
    return not lowered or any(fragment in lowered for fragment in safe)


def check_config(path: Path, root: Path, text: str) -> list[Finding]:
    if "/message/" in path.as_posix().lower() or path.name.startswith("message-"):
        return []
    findings: list[Finding] = []
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "//")):
            continue
        match = SECRET.search(stripped)
        if match and not secret_is_safe(match.group(2)):
            detail = "Literal secret-like value detected; use environment placeholders or encrypted configuration."
            findings.append(Finding(Severity.ERROR, "plain-secret", f"{rel(path, root)}:{number}", detail))
    return findings


def check_java(path: Path, root: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    name = path.name
    if name.lower().endswith("controller.java") and (SQL.search(text) or "JdbcTemplate" in text or "SqlSession" in text):
        detail = "Controller contains inline SQL or direct persistence access; route through service and mapper layers."
        findings.append(Finding(Severity.ERROR, "controller-sql", rel(path, root), detail))
    if name.endswith("ServiceImpl.java") and WRITE_METHOD.search(text) and "@Transactional" not in text:
        detail = "Write-oriented service code appears to lack an explicit transaction boundary."
        findings.append(Finding(Severity.WARNING, "service-transaction", rel(path, root), detail))
    if name.endswith("Mapper.java") and "interface " in text and "@Mapper" not in text:
        detail = "Mapper interface has no @Mapper annotation; ensure @MapperScan or XML registration covers it."
        findings.append(Finding(Severity.WARNING, "mapper-annotation", rel(path, root), detail))
    return findings


def check_xml(path: Path, root: Path, text: str) -> list[Finding]:
    if "<mapper" not in text:
        return []
    start = text.find("<mapper")
    tag = text[start : text.find(">", start) + 1]
    findings: list[Finding] = []
    if "namespace=" not in tag:
        findings.append(Finding(Severity.ERROR, "mapper-namespace", rel(path, root), "MyBatis mapper XML must declare a namespace matching the mapper interface."))
    if "<!DOCTYPE mapper" not in text:
        findings.append(Finding(Severity.WARNING, "mapper-doctype", rel(path, root), "Mapper XML has no MyBatis mapper DOCTYPE; confirm this is intentional for the configured parser."))
    return findings


def check_wide(root: Path, files: list[Path], texts: dict[Path, str]) -> list[Finding]:
    findings: list[Finding] = []
    has_mapper_xml = any("<mapper" in texts.get(path, "") for path in files if path.suffix == ".xml")
    has_mapper_scan = any("@MapperScan" in text or "mapper-locations" in text for text in texts.values())
    build_text = "\n".join(texts[path] for path in files if path.name in {"pom.xml", "build.gradle"}).lower()
    if has_mapper_xml and not has_mapper_scan:
        detail = "Mapper XML files were found, but mapper-locations or @MapperScan was not detected in scanned files."
        findings.append(Finding(Severity.WARNING, "mapper-scan", ".", detail))
    if build_text and "egovframework" not in build_text and "org.egovframe" not in build_text:
        detail = "Detected eGovFrame project signals but no eGovFrame runtime dependency in scanned build files."
        findings.append(Finding(Severity.WARNING, "egov-runtime", rel(root, root), detail))
    return findings


def apply_policy(findings: list[Finding], policy: Policy) -> tuple[Finding, ...]:
    applied: list[Finding] = []
    for item in findings:
        severity = policy.rules.get(item.rule, item.severity)
        if severity == Severity.OFF or is_suppressed(item, policy):
            continue
        applied.append(Finding(severity, item.rule, item.path, item.detail))
    return tuple(applied)


def is_suppressed(finding: Finding, policy: Policy) -> bool:
    for item in policy.suppressions:
        if item.rule == finding.rule and fnmatch.fnmatchcase(finding.path, item.path):
            return True
    return False


def scan(root: Path, policy: Policy) -> ScanResult:
    resolved = root.resolve()
    files = collect_files(resolved)
    if not is_egov_project(files):
        return ScanResult(resolved, False, (), len(files))
    findings: list[Finding] = []
    texts: dict[Path, str] = {}
    for path in files:
        text = read_text(path)
        texts[path] = text
        findings.extend(check_config(path, resolved, text) if path.suffix in {".properties", ".yml", ".yaml", ".xml"} else [])
        findings.extend(check_java(path, resolved, text) if path.suffix == ".java" else [])
        findings.extend(check_xml(path, resolved, text) if path.suffix == ".xml" else [])
    findings.extend(check_wide(resolved, files, texts))
    return ScanResult(resolved, True, apply_policy(findings, policy), len(files))


def to_json(result: ScanResult) -> dict[str, JsonValue]:
    counts: dict[str, JsonValue] = {
        severity.value: sum(1 for item in result.findings if item.severity == severity)
        for severity in Severity
        if severity != Severity.OFF
    }
    findings: list[JsonValue] = [
        {"severity": item.severity.value, "rule": item.rule, "path": item.path, "detail": item.detail}
        for item in result.findings
    ]
    return {
        "root": str(result.root),
        "projectDetected": result.detected,
        "inspectedFiles": result.inspected,
        "counts": counts,
        "findings": findings,
    }


def render_report(result: ScanResult) -> str:
    if not result.detected:
        return f"eGovFrame Guard: no eGovFrame project signals found under {result.root}."
    lines = [f"eGovFrame Guard: inspected {result.inspected} files, errors={result.error_count}, warnings={result.warning_count}."]
    lines.extend(f"- {item.severity.value.upper()} {item.rule} {item.path}: {item.detail}" for item in result.findings[:30])
    lines.extend(["- PASS no high-confidence eGovFrame guardrail findings."] if not result.findings else [])
    lines.extend([f"- ... {len(result.findings) - 30} more findings omitted."] if len(result.findings) > 30 else [])
    return "\n".join(lines)
