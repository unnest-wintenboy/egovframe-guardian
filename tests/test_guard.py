from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import TypeAlias

from egovframe_guard_core import load_policy, scan


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
GUARD = PLUGIN_ROOT / "scripts" / "egovframe_guard.py"
SCORE = PLUGIN_ROOT / "scripts" / "score_maturity.py"
JsonScalar: TypeAlias = None | bool | int | float | str
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


def run_command(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)


def load_json_object(raw: str) -> dict[str, JsonValue]:
    loaded: JsonValue = json.loads(raw)
    assert isinstance(loaded, dict)
    return loaded


def make_project(root: Path, bad: bool) -> None:
    src = root / "src" / "main" / "java" / "egovframework" / "demo" / "web"
    resources = root / "src" / "main" / "resources" / "egovframework" / "sqlmap"
    src.mkdir(parents=True)
    resources.mkdir(parents=True)
    _ = (root / "pom.xml").write_text(
        "<project><dependencies><dependency><groupId>org.egovframe.rte</groupId></dependency></dependencies></project>",
        encoding="utf-8",
    )
    controller_body = 'return "select id from board where id = ?";' if bad else 'return "ok";'
    _ = (src / "BoardController.java").write_text(
        f"package egovframework.demo.web; public class BoardController {{ public String list() {{ {controller_body} }} }}",
        encoding="utf-8",
    )
    mapper = "<mapper><select id=\"bad\">select id from board</select></mapper>" if bad else "<!DOCTYPE mapper><mapper namespace=\"egovframework.demo.BoardMapper\"></mapper>"
    _ = (resources / "BoardMapper.xml").write_text(mapper, encoding="utf-8")
    if bad:
        _ = (root / "src" / "main" / "resources" / "application.properties").write_text(
            "spring.datasource.password=plain-secret",
            encoding="utf-8",
        )


def test_guard_passes_when_project_has_no_blocking_findings(tmp_path: Path) -> None:
    make_project(tmp_path, bad=False)
    result = run_command([sys.executable, str(GUARD), "--mode", "scan", "--root", str(tmp_path)])
    assert result.returncode == 0
    assert "errors=0" in result.stdout


def test_guard_blocks_when_project_has_high_confidence_findings(tmp_path: Path) -> None:
    make_project(tmp_path, bad=True)
    result = run_command([sys.executable, str(GUARD), "--mode", "scan", "--root", str(tmp_path), "--json"])
    assert result.returncode == 2
    payload = load_json_object(result.stdout)
    counts = payload["counts"]
    assert isinstance(counts, dict)
    assert counts["error"] == 3


def test_guard_ignores_generic_java_project_without_egovframe_markers(tmp_path: Path) -> None:
    src = tmp_path / "src" / "main" / "java" / "com" / "example"
    src.mkdir(parents=True)
    _ = (tmp_path / "pom.xml").write_text("<project></project>", encoding="utf-8")
    for index in range(5):
        _ = (src / f"Example{index}.java").write_text("package com.example; public class Example {}", encoding="utf-8")
    _ = (tmp_path / "application.properties").write_text("spring.datasource.password=plain-secret", encoding="utf-8")
    result = run_command([sys.executable, str(GUARD), "--mode", "scan", "--root", str(tmp_path)])
    assert result.returncode == 0
    assert "no eGovFrame project signals" in result.stdout


def test_guard_ignores_generic_webinf_project_without_egovframe_markers(tmp_path: Path) -> None:
    webinf = tmp_path / "src" / "main" / "webapp" / "WEB-INF"
    webinf.mkdir(parents=True)
    _ = (tmp_path / "pom.xml").write_text("<project></project>", encoding="utf-8")
    _ = (webinf / "web.xml").write_text("<web-app></web-app>", encoding="utf-8")
    _ = (tmp_path / "application.properties").write_text("spring.datasource.password=plain-secret", encoding="utf-8")
    result = run_command([sys.executable, str(GUARD), "--mode", "scan", "--root", str(tmp_path)])
    assert result.returncode == 0
    assert "no eGovFrame project signals" in result.stdout


def test_core_scan_detects_bad_project_without_subprocess(tmp_path: Path) -> None:
    make_project(tmp_path, bad=True)
    policy = load_policy(PLUGIN_ROOT, tmp_path)
    result = scan(tmp_path, policy)
    assert result.detected is True
    assert result.error_count == 3


def test_hook_mode_returns_structured_blocking_payload(tmp_path: Path) -> None:
    make_project(tmp_path, bad=True)
    hook_input = json.dumps({"cwd": str(tmp_path)})
    result = subprocess.run(
        [sys.executable, str(GUARD), "--mode", "hook"],
        input=hook_input,
        text=True,
        capture_output=True,
        check=False,
    )
    payload = load_json_object(result.stdout)
    assert result.returncode == 0
    assert payload["continue"] is False
    stop_reason = payload["stopReason"]
    assert isinstance(stop_reason, str)
    assert "blocking standard violations" in stop_reason


def test_project_policy_can_downgrade_blocking_rules(tmp_path: Path) -> None:
    make_project(tmp_path, bad=True)
    _ = (tmp_path / ".egovframe-guardian.json").write_text(
        json.dumps(
            {
                "rules": {
                    "plain-secret": "warning",
                    "mapper-namespace": "warning",
                    "controller-sql": "warning",
                }
            }
        ),
        encoding="utf-8",
    )
    result = run_command([sys.executable, str(GUARD), "--mode", "scan", "--root", str(tmp_path), "--json"])
    payload = load_json_object(result.stdout)
    counts = payload["counts"]
    assert isinstance(counts, dict)
    assert result.returncode == 0
    assert counts["error"] == 0


def test_hook_mode_uses_project_policy_from_payload_cwd(tmp_path: Path) -> None:
    make_project(tmp_path, bad=True)
    _ = (tmp_path / ".egovframe-guardian.json").write_text(
        json.dumps(
            {
                "rules": {
                    "plain-secret": "warning",
                    "mapper-namespace": "warning",
                    "controller-sql": "warning",
                }
            }
        ),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(GUARD), "--mode", "hook"],
        input=json.dumps({"cwd": str(tmp_path)}),
        text=True,
        capture_output=True,
        check=False,
    )
    payload = load_json_object(result.stdout)
    assert result.returncode == 0
    assert payload["continue"] is True


def test_project_policy_accepts_utf8_bom(tmp_path: Path) -> None:
    make_project(tmp_path, bad=True)
    _ = (tmp_path / ".egovframe-guardian.json").write_text(
        json.dumps(
            {
                "rules": {
                    "plain-secret": "warning",
                    "mapper-namespace": "warning",
                    "controller-sql": "warning",
                }
            }
        ),
        encoding="utf-8-sig",
    )
    result = run_command([sys.executable, str(GUARD), "--mode", "scan", "--root", str(tmp_path), "--json"])
    payload = load_json_object(result.stdout)
    counts = payload["counts"]
    assert isinstance(counts, dict)
    assert result.returncode == 0
    assert counts["error"] == 0


def test_release_maturity_score_is_full() -> None:
    result = run_command([sys.executable, str(SCORE), str(PLUGIN_ROOT), "--fail-under", "110"])
    assert result.returncode == 0
    payload = load_json_object(result.stdout)
    assert payload["score"] == 110
    checks = payload["checks"]
    assert isinstance(checks, list)
    for item in checks:
        assert isinstance(item, dict)
        assert item["passed"] is True
