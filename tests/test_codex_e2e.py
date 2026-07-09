from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import TypeAlias


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
GUARD = PLUGIN_ROOT / "scripts" / "egovframe_guard.py"
JsonScalar: TypeAlias = None | bool | int | float | str
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


def load_json_object(raw: str) -> dict[str, JsonValue]:
    loaded: JsonValue = json.loads(raw)
    assert isinstance(loaded, dict)
    return loaded


def run_hook(mode: str, payload: dict[str, JsonValue], plugin_data: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PLUGIN_DATA"] = str(plugin_data)
    return subprocess.run(
        [sys.executable, str(GUARD), "--mode", mode],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def make_codex_project(root: Path) -> None:
    src = root / "src" / "main" / "java" / "egovframework" / "codex" / "web"
    resources = root / "src" / "main" / "resources" / "egovframework" / "sqlmap"
    src.mkdir(parents=True)
    resources.mkdir(parents=True)
    _ = (root / "pom.xml").write_text(
        "<project><dependencies><dependency><groupId>org.egovframe.rte</groupId></dependency></dependencies></project>",
        encoding="utf-8",
    )
    _ = (src / "BoardController.java").write_text(
        'package egovframework.codex.web; public class BoardController { public String list() { return "select id from board where id = ?"; } }',
        encoding="utf-8",
    )
    _ = (resources / "BoardMapper.xml").write_text(
        '<mapper><select id="bad">select id from board</select></mapper>',
        encoding="utf-8",
    )


def test_codex_hook_lifecycle_blocks_tracked_findings_for_current_project(tmp_path: Path) -> None:
    project = tmp_path / "egov-project"
    plugin_data = tmp_path / "plugin-data"
    make_codex_project(project)

    pre_tool = run_hook(
        "pre-tool",
        {
            "cwd": str(project),
            "tool_name": "exec_command",
            "tool_input": {"command": "rm -rf src/main/java/egovframework/codex"},
        },
        plugin_data,
    )
    pre_payload = load_json_object(pre_tool.stdout)
    pre_output = pre_payload["hookSpecificOutput"]
    assert isinstance(pre_output, dict)
    assert pre_tool.returncode == 0
    assert pre_output["permissionDecision"] == "deny"

    post_tool = run_hook("hook", {"cwd": str(project), "tool_name": "apply_patch"}, plugin_data)
    post_payload = load_json_object(post_tool.stdout)
    assert post_tool.returncode == 0
    assert post_payload["continue"] is False

    stop = run_hook("stop", {"cwd": str(project), "stop_hook_active": False}, plugin_data)
    stop_payload = load_json_object(stop.stdout)
    assert stop.returncode == 0
    assert stop_payload["decision"] == "block"
    assert str(project) in str(stop_payload["reason"])


def test_codex_hook_lifecycle_ignores_unrelated_project_state(tmp_path: Path) -> None:
    project = tmp_path / "egov-project"
    other = tmp_path / "plain-project"
    plugin_data = tmp_path / "plugin-data"
    make_codex_project(project)
    other.mkdir()
    _ = run_hook("hook", {"cwd": str(project), "tool_name": "apply_patch"}, plugin_data)

    stop = run_hook("stop", {"cwd": str(other), "stop_hook_active": False}, plugin_data)
    payload = load_json_object(stop.stdout)
    assert stop.returncode == 0
    assert payload["continue"] is True


def test_codex_prompt_and_subagent_hooks_are_egovframe_specific(tmp_path: Path) -> None:
    plugin_data = tmp_path / "plugin-data"

    generic_prompt = run_hook("prompt", {"prompt": "Review React browser compatibility."}, plugin_data)
    assert generic_prompt.returncode == 0
    assert generic_prompt.stdout == ""

    egov_prompt = run_hook("prompt", {"prompt": "Review this eGovFrame mapper flow."}, plugin_data)
    egov_payload = load_json_object(egov_prompt.stdout)
    egov_output = egov_payload["hookSpecificOutput"]
    assert isinstance(egov_output, dict)
    assert egov_output["hookEventName"] == "UserPromptSubmit"

    generic_subagent = run_hook(
        "subagent-start",
        {"agent_type": "lazycodex-code-reviewer", "prompt": "Review generic compatibility notes."},
        plugin_data,
    )
    assert generic_subagent.returncode == 0
    assert generic_subagent.stdout == ""

    egov_subagent = run_hook(
        "subagent-start",
        {"agent_type": "lazycodex-code-reviewer", "prompt": "Review eGovFrame service and mapper layout."},
        plugin_data,
    )
    subagent_payload = load_json_object(egov_subagent.stdout)
    subagent_output = subagent_payload["hookSpecificOutput"]
    assert isinstance(subagent_output, dict)
    assert subagent_output["hookEventName"] == "SubagentStart"
