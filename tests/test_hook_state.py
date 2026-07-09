from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import TypeAlias

from egovframe_guard_core import load_policy
from egovframe_guard_hooks import (
    permission_payload,
    post_tool_payload,
    stop_payload,
    subagent_start_payload,
    subagent_stop_payload,
)

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
GUARD = PLUGIN_ROOT / "scripts" / "egovframe_guard.py"
JsonScalar: TypeAlias = None | bool | int | float | str
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


def load_json_object(raw: str) -> dict[str, JsonValue]:
    loaded: JsonValue = json.loads(raw)
    assert isinstance(loaded, dict)
    return loaded


def make_bad_project(root: Path) -> None:
    src = root / "src" / "main" / "java" / "egovframework" / "demo" / "web"
    resources = root / "src" / "main" / "resources" / "egovframework" / "sqlmap"
    src.mkdir(parents=True)
    resources.mkdir(parents=True)
    _ = (root / "pom.xml").write_text(
        "<project><dependencies><dependency><groupId>org.egovframe.rte</groupId></dependency></dependencies></project>",
        encoding="utf-8",
    )
    _ = (src / "BoardController.java").write_text(
        'package egovframework.demo.web; public class BoardController { public String list() { return "select id from board where id = ?"; } }',
        encoding="utf-8",
    )
    _ = (resources / "BoardMapper.xml").write_text(
        '<mapper><select id="bad">select id from board</select></mapper>',
        encoding="utf-8",
    )
    _ = (root / "src" / "main" / "resources" / "application.properties").write_text(
        "spring.datasource.password=plain-secret",
        encoding="utf-8",
    )


def tool_payload(command: str) -> dict[str, JsonValue]:
    tool_input: dict[str, JsonValue] = {"command": command}
    return {"tool_name": "Bash", "tool_input": tool_input}


def set_plugin_data(path: Path) -> str | None:
    previous = os.environ.get("PLUGIN_DATA")
    os.environ["PLUGIN_DATA"] = str(path)
    return previous


def restore_plugin_data(previous: str | None) -> None:
    if previous is None:
        _ = os.environ.pop("PLUGIN_DATA", None)
    else:
        os.environ["PLUGIN_DATA"] = previous


def hook_matcher(hooks: dict[str, JsonValue], event: str) -> str:
    raw_entries = hooks[event]
    assert isinstance(raw_entries, list)
    first = raw_entries[0]
    assert isinstance(first, dict)
    matcher = first.get("matcher")
    assert isinstance(matcher, str)
    return matcher


def test_stop_gate_uses_tracked_blocking_scan_from_plugin_data(tmp_path: Path) -> None:
    previous = set_plugin_data(tmp_path / "plugin-data")
    project = tmp_path / "bad-project"
    try:
        make_bad_project(project)
        response = post_tool_payload(load_policy(PLUGIN_ROOT, project), project)
        assert response["continue"] is False
        stop_response = stop_payload(load_policy(PLUGIN_ROOT, project), project, {"stop_hook_active": False})
        assert stop_response["decision"] == "block"
        assert str(project) in str(stop_response["reason"])
    finally:
        restore_plugin_data(previous)


def test_stop_gate_ignores_unrelated_tracked_scan_from_plugin_data(tmp_path: Path) -> None:
    previous = set_plugin_data(tmp_path / "plugin-data")
    project = tmp_path / "bad-project"
    clean = tmp_path / "clean"
    try:
        clean.mkdir()
        make_bad_project(project)
        _ = post_tool_payload(load_policy(PLUGIN_ROOT, project), project)
        stop_response = stop_payload(load_policy(PLUGIN_ROOT, clean), clean, {"stop_hook_active": False})
        assert stop_response["continue"] is True
    finally:
        restore_plugin_data(previous)


def test_permission_request_denies_destructive_critical_command() -> None:
    response = permission_payload(tool_payload("git clean -fd src/main/resources/egovframework"))
    assert response is not None
    hook_output = response["hookSpecificOutput"]
    assert isinstance(hook_output, dict)
    decision = hook_output["decision"]
    assert isinstance(decision, dict)
    assert hook_output["hookEventName"] == "PermissionRequest"
    assert decision["behavior"] == "deny"


def test_subagent_start_adds_homepage_aligned_context() -> None:
    response = subagent_start_payload(
        {
            "agent_type": "lazycodex-code-reviewer",
            "prompt": "Review this eGovFrame mapper and compatibility flow.",
        }
    )
    assert response is not None
    hook_output = response["hookSpecificOutput"]
    assert isinstance(hook_output, dict)
    assert hook_output["hookEventName"] == "SubagentStart"
    assert "v5.0.0" in str(hook_output["additionalContext"])
    assert "compatibility" in str(hook_output["additionalContext"])


def test_subagent_start_stays_quiet_for_unrelated_context() -> None:
    response = subagent_start_payload({"agent_type": "lazycodex-code-reviewer", "prompt": "Review a README typo."})
    assert response is None


def test_subagent_start_stays_quiet_for_generic_compatibility_context() -> None:
    response = subagent_start_payload(
        {"agent_type": "lazycodex-code-reviewer", "prompt": "Review React browser compatibility fixes."}
    )
    assert response is None


def test_subagent_start_cli_stays_quiet_for_unrelated_context() -> None:
    result = subprocess.run(
        [sys.executable, str(GUARD), "--mode", "subagent-start"],
        input=json.dumps({"agent_type": "lazycodex-code-reviewer", "prompt": "Review a README typo."}),
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout == ""


def test_subagent_stop_blocks_when_tracked_scan_is_blocking(tmp_path: Path) -> None:
    previous = set_plugin_data(tmp_path / "plugin-data")
    project = tmp_path / "bad-project"
    try:
        make_bad_project(project)
        _ = post_tool_payload(load_policy(PLUGIN_ROOT, project), project)
        response = subagent_stop_payload(load_policy(PLUGIN_ROOT, project), project, {"stop_hook_active": False})
        assert response["decision"] == "block"
        assert "subagent" in str(response["reason"])
    finally:
        restore_plugin_data(previous)


def test_subagent_stop_ignores_unrelated_tracked_scan(tmp_path: Path) -> None:
    previous = set_plugin_data(tmp_path / "plugin-data")
    project = tmp_path / "bad-project"
    other = tmp_path / "other"
    try:
        other.mkdir()
        make_bad_project(project)
        _ = post_tool_payload(load_policy(PLUGIN_ROOT, project), project)
        response = subagent_stop_payload(load_policy(PLUGIN_ROOT, other), other, {"stop_hook_active": False})
        assert response["continue"] is True
    finally:
        restore_plugin_data(previous)


def test_subagent_stop_stays_quiet_without_tracked_findings(tmp_path: Path) -> None:
    clean = tmp_path / "clean"
    clean.mkdir()
    response = subagent_stop_payload(load_policy(PLUGIN_ROOT, clean), clean, {"stop_hook_active": False})
    assert response["continue"] is True


def test_permission_hook_cli_returns_deny_json() -> None:
    result = subprocess.run(
        [sys.executable, str(GUARD), "--mode", "permission"],
        input=json.dumps(tool_payload("remove-item src/main/java/egovframework -recurse")),
        text=True,
        capture_output=True,
        check=False,
    )
    payload = load_json_object(result.stdout)
    hook_output = payload["hookSpecificOutput"]
    assert isinstance(hook_output, dict)
    assert result.returncode == 0
    assert hook_output["hookEventName"] == "PermissionRequest"


def test_hook_matchers_cover_codex_and_claude_tool_names() -> None:
    hooks_file = PLUGIN_ROOT / "hooks" / "hooks.json"
    loaded: JsonValue = json.loads(hooks_file.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    hooks = loaded["hooks"]
    assert isinstance(hooks, dict)
    pre_matcher = hook_matcher(hooks, "PreToolUse")
    permission_matcher = hook_matcher(hooks, "PermissionRequest")
    post_matcher = hook_matcher(hooks, "PostToolUse")
    for matcher in (pre_matcher, permission_matcher):
        assert "exec_command" in matcher
        assert "mcp__git_bash" in matcher
        assert "MultiEdit" in matcher
    assert "MultiEdit" in post_matcher
    assert "NotebookEdit" in post_matcher
