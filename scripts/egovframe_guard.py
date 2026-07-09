#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///

# ─── How to run ───
# 1. Install uv (if not installed):
#      curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run directly:
#      uv run scripts/egovframe_guard.py --mode scan --root .
# 3. Or run with Python when no third-party dependencies are needed:
#      python scripts/egovframe_guard.py --mode scan --root .
# ──────────────────

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from egovframe_guard_core import JsonValue, load_policy, render_report, scan, to_json
from egovframe_guard_hooks import (
    HOOK_INPUT_MODES,
    permission_payload,
    post_compact_payload,
    post_tool_payload,
    pre_tool_payload,
    prompt_payload,
    root_from_payload,
    stop_payload,
    subagent_start_payload,
    subagent_stop_payload,
)


@dataclass(frozen=True, slots=True)
class CliArgs:
    mode: str
    root: Path
    emit_json: bool


def parse_cli(argv: list[str]) -> CliArgs:
    mode = "scan"
    root = Path.cwd()
    emit_json = False
    index = 0
    while index < len(argv):
        token = argv[index]
        if token == "--mode" and index + 1 < len(argv):
            mode = argv[index + 1]
            index += 2
        elif token == "--root" and index + 1 < len(argv):
            root = Path(argv[index + 1])
            index += 2
        elif token == "--json":
            emit_json = True
            index += 1
        else:
            raise SystemExit(f"Unknown or incomplete argument: {token}")
    return CliArgs(mode, root, emit_json)


def read_hook_payload() -> JsonValue:
    raw = sys.stdin.read().strip()
    loaded: JsonValue = json.loads(raw) if raw else None
    return loaded if isinstance(loaded, (dict, list, str, int, float, bool)) or loaded is None else None


def emit_json(payload: dict[str, JsonValue]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def plugin_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main(argv: list[str]) -> int:
    args = parse_cli(argv)
    if args.mode == "session":
        print("eGovFrame Guardian: bundled skill and local compliance hooks are ready.")
        return 0
    payload = read_hook_payload() if args.mode in HOOK_INPUT_MODES else None
    root = root_from_payload(payload, args.root)
    policy = load_policy(plugin_root(), root)
    if args.mode == "hook":
        emit_json(post_tool_payload(policy, root))
        return 0
    if args.mode == "pre-tool":
        response = pre_tool_payload(payload, root)
        if response is not None:
            emit_json(response)
        return 0
    if args.mode == "permission":
        response = permission_payload(payload, root)
        if response is not None:
            emit_json(response)
        return 0
    if args.mode == "prompt":
        response = prompt_payload(payload)
        if response is not None:
            emit_json(response)
        return 0
    if args.mode == "post-compact":
        emit_json(post_compact_payload())
        return 0
    if args.mode == "stop":
        emit_json(stop_payload(policy, root, payload))
        return 0
    if args.mode == "subagent-start":
        response = subagent_start_payload(payload)
        if response is not None:
            emit_json(response)
        return 0
    if args.mode == "subagent-stop":
        emit_json(subagent_stop_payload(policy, root, payload))
        return 0
    result = scan(root, policy)
    print(json.dumps(to_json(result), ensure_ascii=False, indent=2) if args.emit_json else render_report(result))
    return 2 if result.error_count > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
