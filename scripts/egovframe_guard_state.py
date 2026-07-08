from __future__ import annotations

import json
import os
from dataclasses import dataclass
from json import JSONDecodeError
from pathlib import Path
from typing import TypeAlias

from egovframe_guard_core import ScanResult, render_report

JsonScalar: TypeAlias = None | bool | int | float | str
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


@dataclass(frozen=True, slots=True)
class ProjectSnapshot:
    root: str
    pending: bool
    detected: bool
    error_count: int
    warning_count: int
    summary: str


@dataclass(frozen=True, slots=True)
class GuardState:
    projects: tuple[ProjectSnapshot, ...]


def plugin_data_path() -> Path | None:
    raw = os.environ.get("PLUGIN_DATA") or os.environ.get("CLAUDE_PLUGIN_DATA")
    if raw is None or not raw.strip():
        return None
    return Path(raw).expanduser() / "egovframe_guard_state.json"


def parse_snapshot(raw: JsonValue) -> ProjectSnapshot | None:
    if not isinstance(raw, dict):
        return None
    root = raw.get("root")
    summary = raw.get("summary")
    pending = raw.get("pending")
    detected = raw.get("detected")
    errors = raw.get("error_count")
    warnings = raw.get("warning_count")
    if not isinstance(root, str) or not isinstance(summary, str):
        return None
    if not isinstance(pending, bool) or not isinstance(detected, bool):
        return None
    if not isinstance(errors, int) or not isinstance(warnings, int):
        return None
    return ProjectSnapshot(root, pending, detected, errors, warnings, summary)


def load_state() -> GuardState:
    path = plugin_data_path()
    if path is None or not path.exists():
        return GuardState(())
    try:
        loaded: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, JSONDecodeError):
        return GuardState(())
    if not isinstance(loaded, dict):
        return GuardState(())
    raw_projects = loaded.get("projects")
    if not isinstance(raw_projects, list):
        return GuardState(())
    projects = tuple(item for raw in raw_projects if (item := parse_snapshot(raw)) is not None)
    return GuardState(projects)


def snapshot_json(snapshot: ProjectSnapshot) -> dict[str, JsonValue]:
    return {
        "root": snapshot.root,
        "pending": snapshot.pending,
        "detected": snapshot.detected,
        "error_count": snapshot.error_count,
        "warning_count": snapshot.warning_count,
        "summary": snapshot.summary,
    }


def save_state(state: GuardState) -> None:
    path = plugin_data_path()
    if path is None:
        return
    payload: dict[str, JsonValue] = {"projects": [snapshot_json(item) for item in state.projects]}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        return


def upsert_snapshot(state: GuardState, snapshot: ProjectSnapshot) -> GuardState:
    kept = tuple(item for item in state.projects if item.root != snapshot.root)
    return GuardState(kept + (snapshot,))


def record_scan(result: ScanResult) -> None:
    snapshot = ProjectSnapshot(
        str(result.root),
        False,
        result.detected,
        result.error_count,
        result.warning_count,
        render_report(result),
    )
    save_state(upsert_snapshot(load_state(), snapshot))


def record_pending(root: Path, summary: str) -> None:
    snapshot = ProjectSnapshot(str(root.resolve()), True, False, 0, 0, summary)
    save_state(upsert_snapshot(load_state(), snapshot))


def gate_snapshots() -> tuple[ProjectSnapshot, ...]:
    return tuple(item for item in load_state().projects if item.pending or item.error_count > 0)
