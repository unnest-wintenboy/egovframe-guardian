from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from egovframe_distribution_core import ExpectedHashes, JsonValue, inspect_archive

ZIP_TOKEN: Final = re.compile(r"""(?:"([^"]+?\.zip)"|'([^']+?\.zip)'|([^\s;&|]+?\.zip))""", re.IGNORECASE)
ZIP_URL: Final = re.compile(r"""https?://[^\s'";&|]+/([^/\s'";&|]+\.zip)(?:[?#][^\s'";&|]*)?""", re.IGNORECASE)
EXTRACTION_MARKERS: Final = (
    "unzip ",
    "unzip.exe",
    "expand-archive",
    "jar xf",
    "jar -xf",
    "7z x",
    "7za x",
    "tar -xf",
    "tar -xvf",
    "bsdtar -xf",
    "python -m zipfile -e",
)
INSPECTOR_MARKERS: Final = ("egovframe_distribution.py inspect", "egovframe_distribution.py\" inspect")


@dataclass(frozen=True, slots=True)
class ZipInspection:
    path: Path
    report: dict[str, JsonValue]


def command_uses_distribution_inspector(command: str) -> bool:
    lowered = command.lower()
    return any(marker in lowered for marker in INSPECTOR_MARKERS)


def is_zip_extraction_command(command: str) -> bool:
    lowered = command.lower()
    return ".zip" in lowered and any(marker in lowered for marker in EXTRACTION_MARKERS)


def clean_token(token: str) -> str:
    return token.strip().strip("\"'").rstrip(").,;")


def resolve_zip_path(token: str, root: Path) -> Path | None:
    cleaned = clean_token(token)
    if not cleaned or "://" in cleaned:
        return None
    path = Path(cleaned).expanduser()
    return path if path.is_absolute() else root / path


def zip_paths_from_command(command: str, root: Path) -> tuple[Path, ...]:
    paths: list[Path] = []
    for match in ZIP_TOKEN.finditer(command):
        token = next(group for group in match.groups() if group is not None)
        path = resolve_zip_path(token, root)
        if path is not None:
            paths.append(path)
    for match in ZIP_URL.finditer(command):
        paths.append(root / clean_token(match.group(1)))
    return tuple(dict.fromkeys(paths))


def inspection_error_report(path: Path, detail: str) -> dict[str, JsonValue]:
    return {
        "archive": str(path),
        "safe": False,
        "checksum_verified": False,
        "errors": [detail],
        "warnings": [],
        "distribution_type": "archive",
        "signals": [],
        "summary": {"entry_count": 0, "total_uncompressed_bytes": 0, "extension_counts": {}, "largest_entries": []},
    }


def inspect_zip_paths(paths: tuple[Path, ...]) -> tuple[ZipInspection, ...]:
    inspections: list[ZipInspection] = []
    for path in paths:
        try:
            report = inspect_archive(path, ExpectedHashes())
        except FileNotFoundError:
            report = inspection_error_report(path, "archive not found")
        except PermissionError:
            report = inspection_error_report(path, "archive cannot be read")
        except zipfile.BadZipFile:
            report = inspection_error_report(path, "invalid zip archive")
        inspections.append(ZipInspection(path, report))
    return tuple(inspections)


def list_text(value: JsonValue) -> str:
    if not isinstance(value, list) or not value:
        return ""
    return ", ".join(str(item) for item in value[:3])


def inspection_has_errors(inspection: ZipInspection) -> bool:
    errors = inspection.report.get("errors")
    return isinstance(errors, list) and bool(errors)


def inspection_is_safe(inspection: ZipInspection) -> bool:
    safe = inspection.report.get("safe")
    return safe is True and not inspection_has_errors(inspection)


def render_zip_inspections(inspections: tuple[ZipInspection, ...]) -> str:
    lines = ["eGovFrame Guardian automatic ZIP inspection:"]
    for item in inspections:
        report = item.report
        kind = str(report.get("distribution_type", "archive"))
        safe = str(report.get("safe", False)).lower()
        checksum = str(report.get("checksum_verified", False)).lower()
        lines.append(f"- {item.path}: type={kind}, safe={safe}, checksum_verified={checksum}")
        errors = list_text(report.get("errors"))
        warnings = list_text(report.get("warnings"))
        scripts = list_text(report.get("script_or_binary_entries"))
        if errors:
            lines.append(f"  errors: {errors}")
        if warnings:
            lines.append(f"  warnings: {warnings}")
        if scripts:
            lines.append(f"  script_or_binary_entries: {scripts}")
    lines.append("Extract only into a temporary or sandbox directory, then adapt the needed source/config files.")
    return "\n".join(lines)


def zip_pre_tool_payload(command: str, root: Path) -> dict[str, JsonValue] | None:
    if command_uses_distribution_inspector(command) or not is_zip_extraction_command(command):
        return None
    paths = zip_paths_from_command(command, root)
    if not paths:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": (
                    "eGovFrame Guardian detected a ZIP extraction command. Inspect the archive before extraction "
                    "and extract only into a temporary or sandbox directory."
                ),
            }
        }
    inspections = inspect_zip_paths(paths)
    report = render_zip_inspections(inspections)
    if any(not inspection_is_safe(item) for item in inspections):
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "eGovFrame Guardian blocked ZIP extraction because automatic inspection found an unsafe or "
                    f"unreadable archive.\n{report}"
                ),
            }
        }
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": report,
        }
    }
