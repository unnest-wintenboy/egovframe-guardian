from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import TypeAlias

from egovframe_guard_core import load_policy
from egovframe_guard_hooks import (
    post_tool_payload,
    pre_tool_payload,
    prompt_payload,
    root_from_payload,
    stop_payload,
)

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
GUARD = PLUGIN_ROOT / "scripts" / "egovframe_guard.py"
JsonScalar: TypeAlias = None | bool | int | float | str
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


def load_json_object(raw: str) -> dict[str, JsonValue]:
    loaded: JsonValue = json.loads(raw)
    assert isinstance(loaded, dict)
    return loaded


def tool_payload(command: str) -> dict[str, JsonValue]:
    tool_input: dict[str, JsonValue] = {"command": command}
    return {"tool_input": tool_input}


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


def make_zip(path: Path, entries: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, body in entries.items():
            archive.writestr(name, body)


def test_root_from_payload_prefers_hook_cwd(tmp_path: Path) -> None:
    result = root_from_payload({"cwd": str(tmp_path)}, Path("fallback"))
    assert result == tmp_path


def test_root_from_payload_uses_tool_workdir(tmp_path: Path) -> None:
    result = root_from_payload({"tool_input": {"workdir": str(tmp_path)}}, Path("fallback"))
    assert result == tmp_path


def test_pre_tool_payload_adds_context_for_critical_non_destructive_change() -> None:
    response = pre_tool_payload(tool_payload("*** Update File: src/main/java/egovframework/demo/BoardController.java"))
    assert response is not None
    hook_output = response["hookSpecificOutput"]
    assert isinstance(hook_output, dict)
    assert hook_output["hookEventName"] == "PreToolUse"
    assert "additionalContext" in hook_output


def test_pre_tool_payload_allows_generic_java_delete_path() -> None:
    response = pre_tool_payload(tool_payload("rm -rf src/main/java/com/example/tmp"))
    assert response is None


def test_pre_tool_payload_allows_confirmed_destructive_command() -> None:
    command = "rm -rf src/main/java/egovframework # egovframe-guardian:allow-destructive"
    assert pre_tool_payload(tool_payload(command)) is None


def test_pre_tool_payload_auto_inspects_safe_zip_extraction(tmp_path: Path) -> None:
    archive = tmp_path / "egovframe-template.zip"
    make_zip(archive, {"pom.xml": "<project><groupId>org.egovframe</groupId></project>"})

    response = pre_tool_payload(tool_payload(f"unzip {archive} -d extracted"), tmp_path)

    assert response is not None
    hook_output = response["hookSpecificOutput"]
    assert isinstance(hook_output, dict)
    assert hook_output["hookEventName"] == "PreToolUse"
    context = str(hook_output["additionalContext"])
    assert "automatic ZIP inspection" in context
    assert "type=source-project" in context


def test_pre_tool_payload_blocks_unsafe_zip_extraction(tmp_path: Path) -> None:
    archive = tmp_path / "egovframe-unsafe.zip"
    make_zip(archive, {"../outside.txt": "nope", "pom.xml": "<project />"})

    response = pre_tool_payload(tool_payload(f"Expand-Archive -Path {archive} -DestinationPath extracted"), tmp_path)

    assert response is not None
    hook_output = response["hookSpecificOutput"]
    assert isinstance(hook_output, dict)
    assert hook_output["hookEventName"] == "PreToolUse"
    assert hook_output["permissionDecision"] == "deny"
    assert "unsafe archive paths" in str(hook_output["permissionDecisionReason"])


def test_prompt_payload_directly_matches_egov_terms() -> None:
    response = prompt_payload({"prompt": "egovframe mybatis mapper update"})
    assert response is not None
    hook_output = response["hookSpecificOutput"]
    assert isinstance(hook_output, dict)
    assert hook_output["hookEventName"] == "UserPromptSubmit"


def test_prompt_payload_stays_quiet_for_generic_compatibility() -> None:
    response = prompt_payload({"prompt": "check React browser compatibility and mapper utility tests"})
    assert response is None


def test_post_tool_payload_blocks_bad_project_directly(tmp_path: Path) -> None:
    make_bad_project(tmp_path)
    response = post_tool_payload(load_policy(PLUGIN_ROOT, tmp_path), tmp_path)
    assert response["continue"] is False
    assert "blocking standard violations" in str(response["stopReason"])


def test_stop_payload_stays_quiet_without_tracked_work(tmp_path: Path) -> None:
    make_bad_project(tmp_path)
    response = stop_payload(load_policy(PLUGIN_ROOT, tmp_path), tmp_path, {"stop_hook_active": False})
    assert response["continue"] is True


def test_prompt_hook_adds_context_for_egovframe_work() -> None:
    result = subprocess.run(
        [sys.executable, str(GUARD), "--mode", "prompt"],
        input=json.dumps({"prompt": "Build an eGovFrame v5.0.0 board feature with compatibility checks."}),
        text=True,
        capture_output=True,
        check=False,
    )
    payload = load_json_object(result.stdout)
    hook_output = payload["hookSpecificOutput"]
    assert isinstance(hook_output, dict)
    assert result.returncode == 0
    assert hook_output["hookEventName"] == "UserPromptSubmit"
    assert "egovframe-developer" in str(hook_output["additionalContext"])


def test_prompt_hook_stays_quiet_for_unrelated_work() -> None:
    result = subprocess.run(
        [sys.executable, str(GUARD), "--mode", "prompt"],
        input=json.dumps({"prompt": "write a tiny hello world"}),
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_pre_tool_hook_denies_destructive_egovframe_shell_command() -> None:
    result = subprocess.run(
        [sys.executable, str(GUARD), "--mode", "pre-tool"],
        input=json.dumps({"tool_name": "Bash", "tool_input": {"command": "rm -rf src/main/java/egovframework"}}),
        text=True,
        capture_output=True,
        check=False,
    )
    payload = load_json_object(result.stdout)
    hook_output = payload["hookSpecificOutput"]
    assert isinstance(hook_output, dict)
    assert result.returncode == 0
    assert hook_output["hookEventName"] == "PreToolUse"
    assert hook_output["permissionDecision"] == "deny"
    assert "destructive" in str(hook_output["permissionDecisionReason"])


def test_stop_hook_stays_quiet_without_tracked_work(tmp_path: Path) -> None:
    make_bad_project(tmp_path)
    result = subprocess.run(
        [sys.executable, str(GUARD), "--mode", "stop"],
        input=json.dumps({"cwd": str(tmp_path), "stop_hook_active": False}),
        text=True,
        capture_output=True,
        check=False,
    )
    payload = load_json_object(result.stdout)
    assert result.returncode == 0
    assert payload["continue"] is True


def test_stop_hook_stays_quiet_when_already_active_without_tracked_work(tmp_path: Path) -> None:
    make_bad_project(tmp_path)
    result = subprocess.run(
        [sys.executable, str(GUARD), "--mode", "stop"],
        input=json.dumps({"cwd": str(tmp_path), "stop_hook_active": True}),
        text=True,
        capture_output=True,
        check=False,
    )
    payload = load_json_object(result.stdout)
    assert result.returncode == 0
    assert payload["continue"] is True


def test_post_compact_hook_restores_guard_context() -> None:
    result = subprocess.run(
        [sys.executable, str(GUARD), "--mode", "post-compact"],
        input=json.dumps({"trigger": "auto"}),
        text=True,
        capture_output=True,
        check=False,
    )
    payload = load_json_object(result.stdout)
    assert result.returncode == 0
    assert payload["continue"] is True
    assert "eGovFrame Guardian" in str(payload["systemMessage"])
