#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///

# How to run:
# python scripts/egovframe_distribution.py inspect --zip path/to/archive.zip --json
# python scripts/egovframe_distribution.py inventory --portal-json skills/egovframe-developer/references/portal-crawl-records.json --json

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from egovframe_distribution_core import (
    ExpectedHashes,
    JsonValue,
    inspect_archive,
    portal_inventory,
)


@dataclass(frozen=True, slots=True)
class CliArgs:
    command: str
    archive: Path | None
    portal_json: Path | None
    expected: ExpectedHashes
    emit_json: bool


def usage() -> str:
    return (
        "usage:\n"
        "  egovframe_distribution.py inspect --zip <archive.zip> [--expected-md5 H] "
        "[--expected-sha1 H] [--expected-sha256 H] [--json]\n"
        "  egovframe_distribution.py inventory --portal-json <portal-crawl-records.json> [--json]"
    )


def parse_cli(argv: list[str]) -> CliArgs:
    if not argv:
        raise SystemExit(usage())
    command = argv[0]
    archive: Path | None = None
    portal_json: Path | None = None
    expected = ExpectedHashes()
    emit_json = False
    index = 1
    while index < len(argv):
        token = argv[index]
        if token == "--zip" and index + 1 < len(argv):
            archive = Path(argv[index + 1])
            index += 2
        elif token == "--portal-json" and index + 1 < len(argv):
            portal_json = Path(argv[index + 1])
            index += 2
        elif token == "--expected-md5" and index + 1 < len(argv):
            expected = ExpectedHashes(argv[index + 1].lower(), expected.sha1, expected.sha256)
            index += 2
        elif token == "--expected-sha1" and index + 1 < len(argv):
            expected = ExpectedHashes(expected.md5, argv[index + 1].lower(), expected.sha256)
            index += 2
        elif token == "--expected-sha256" and index + 1 < len(argv):
            expected = ExpectedHashes(expected.md5, expected.sha1, argv[index + 1].lower())
            index += 2
        elif token == "--json":
            emit_json = True
            index += 1
        else:
            raise SystemExit(f"Unknown or incomplete argument: {token}\n{usage()}")
    return CliArgs(command, archive, portal_json, expected, emit_json)


def emit(payload: dict[str, JsonValue], emit_json: bool) -> None:
    if emit_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    for key, value in payload.items():
        print(f"{key}: {value}")


def inspect_command(args: CliArgs) -> int:
    if args.archive is None:
        raise SystemExit("--zip is required for inspect")
    payload = inspect_archive(args.archive, args.expected)
    emit(payload, args.emit_json)
    if not payload["safe"]:
        return 2
    return 1 if payload["errors"] else 0


def inventory_command(args: CliArgs) -> int:
    if args.portal_json is None:
        raise SystemExit("--portal-json is required for inventory")
    emit(portal_inventory(args.portal_json), args.emit_json)
    return 0


def main(argv: list[str]) -> int:
    args = parse_cli(argv)
    if args.command == "inspect":
        return inspect_command(args)
    if args.command == "inventory":
        return inventory_command(args)
    raise SystemExit(usage())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
