from __future__ import annotations

from pathlib import Path
from typing import Final

from egovframe_guard_context import (
    COMPACT_CONTEXT,
    CONFIRM_TOKEN,
    DESTRUCTIVE_MARKERS,
    EGOV_CRITICAL_MARKERS,
    PLUGIN_CRITICAL_MARKERS,
    PROMPT_CONTEXT,
    PROMPT_MARKERS,
    SUBAGENT_CONTEXT,
)
from egovframe_guard_core import JsonValue, Policy, render_report, scan
from egovframe_guard_zip import zip_pre_tool_payload
from egovframe_guard_state import gate_snapshots, record_pending, record_scan

HOOK_INPUT_MODES: Final = {
    "hook",
    "permission",
    "post-compact",
    "pre-tool",
    "prompt",
    "stop",
    "subagent-start",
    "subagent-stop",
}


def payload_object(payload: JsonValue) -> dict[str, JsonValue]:
    return payload if isinstance(payload, dict) else {}


def text_value(payload: dict[str, JsonValue], key: str) -> str:
    value = payload.get(key)
    return value if isinstance(value, str) else ""


def payload_text(payload: JsonValue) -> str:
    if isinstance(payload, dict):
        return " ".join(payload_text(value) for value in payload.values())
    if isinstance(payload, list):
        return " ".join(payload_text(value) for value in payload)
    if isinstance(payload, (str, int, float, bool)):
        return str(payload)
    return ""


def bool_value(payload: dict[str, JsonValue], key: str) -> bool:
    value = payload.get(key)
    return value if isinstance(value, bool) else False


def contains_marker(text: str, markers: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


def command_from_payload(payload: JsonValue) -> str:
    data = payload_object(payload)
    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    return text_value(tool_input, "command")


def root_from_payload(payload: JsonValue, fallback: Path) -> Path:
    data = payload_object(payload)
    if not data:
        return fallback
    cwd = data.get("cwd")
    if isinstance(cwd, str) and cwd.strip():
        return Path(cwd).expanduser()
    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        return fallback
    for key in ("workdir", "cwd"):
        candidate = tool_input.get(key)
        if isinstance(candidate, str) and candidate.strip():
            return Path(candidate).expanduser()
    return fallback


def deny_pre_tool(reason: str) -> dict[str, JsonValue]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def pre_tool_payload(payload: JsonValue, root: Path | None = None) -> dict[str, JsonValue] | None:
    command = command_from_payload(payload)
    if not command.strip() or CONFIRM_TOKEN in command.lower():
        return None
    if root is not None:
        zip_response = zip_pre_tool_payload(command, root)
        if zip_response is not None:
            record_pending(root, "A distribution ZIP extraction was attempted and must be followed by adaptation checks.")
            return zip_response
    critical_markers = EGOV_CRITICAL_MARKERS + PLUGIN_CRITICAL_MARKERS
    is_destructive = contains_marker(command, DESTRUCTIVE_MARKERS)
    touches_critical = contains_marker(command, critical_markers)
    deletes_plugin_source = "*** delete file:" in command.lower() and contains_marker(command, PLUGIN_CRITICAL_MARKERS)
    if (is_destructive and touches_critical) or deletes_plugin_source:
        reason = (
            "eGovFrame Guardian blocked a destructive change touching eGovFrame/plugin-critical "
            f"paths. Re-run only with explicit user confirmation and {CONFIRM_TOKEN}."
        )
        return deny_pre_tool(reason)
    if touches_critical:
        if root is not None:
            record_pending(root, "A tool call touched eGovFrame-critical paths and must be followed by a guard scan.")
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": "This tool call touches eGovFrame-critical paths; run the guard scanner before final response.",
            }
        }
    return None


def permission_payload(payload: JsonValue, root: Path | None = None) -> dict[str, JsonValue] | None:
    command = command_from_payload(payload)
    if not command.strip() or CONFIRM_TOKEN in command.lower():
        return None
    critical_markers = EGOV_CRITICAL_MARKERS + PLUGIN_CRITICAL_MARKERS
    if contains_marker(command, DESTRUCTIVE_MARKERS) and contains_marker(command, critical_markers):
        message = (
            "eGovFrame Guardian denied an approval request for a destructive command touching "
            f"standard/plugin-critical paths. Require explicit confirmation and {CONFIRM_TOKEN}."
        )
        return {
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {"behavior": "deny", "message": message},
            }
        }
    if root is not None and contains_marker(command, critical_markers):
        record_pending(root, "An approval request touched eGovFrame-critical paths and still needs a guard scan.")
    return None


def prompt_payload(payload: JsonValue) -> dict[str, JsonValue] | None:
    prompt = text_value(payload_object(payload), "prompt")
    if not contains_marker(prompt, PROMPT_MARKERS):
        return None
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": PROMPT_CONTEXT,
        }
    }


def post_compact_payload() -> dict[str, JsonValue]:
    return {"continue": True, "systemMessage": COMPACT_CONTEXT}


def subagent_start_payload(payload: JsonValue) -> dict[str, JsonValue] | None:
    if not contains_marker(payload_text(payload), PROMPT_MARKERS):
        return None
    agent_type = text_value(payload_object(payload), "agent_type")
    context = f"{SUBAGENT_CONTEXT} Agent type: {agent_type or 'unknown'}."
    return {"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": context}}


def post_tool_payload(policy: Policy, root: Path) -> dict[str, JsonValue]:
    result = scan(root, policy)
    record_scan(result)
    report = render_report(result)
    has_errors = result.error_count > 0
    return {
        "continue": not has_errors,
        "stopReason": "eGovFrame guard found blocking standard violations." if has_errors else "",
        "systemMessage": report,
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": report,
        },
    }


def tracked_gate_payload(root: Path, payload: JsonValue, actor: str) -> dict[str, JsonValue] | None:
    snapshots = gate_snapshots(root)
    if not snapshots:
        return None
    details = "\n".join(f"- {item.root}: {item.summary}" for item in snapshots)
    if bool_value(payload_object(payload), "stop_hook_active"):
        return {"continue": True, "systemMessage": f"eGovFrame Guardian tracked gate still has findings.\n{details}"}
    reason = (
        f"eGovFrame Guardian tracked {actor} work that still needs attention. Fix blocking findings "
        f"or rerun the scanner after resolving them.\n{details}"
    )
    return {"decision": "block", "reason": reason}


def stop_payload(_policy: Policy, root: Path, payload: JsonValue) -> dict[str, JsonValue]:
    tracked = tracked_gate_payload(root, payload, "main-agent")
    if tracked is not None:
        return tracked
    return {"continue": True}


def subagent_stop_payload(_policy: Policy, root: Path, payload: JsonValue) -> dict[str, JsonValue]:
    tracked = tracked_gate_payload(root, payload, "subagent")
    if tracked is not None:
        return tracked
    return {"continue": True}
