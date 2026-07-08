from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import TypeAlias


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
DISTRIBUTION = PLUGIN_ROOT / "scripts" / "egovframe_distribution.py"
PORTAL_RECORDS = PLUGIN_ROOT / "skills" / "egovframe-developer" / "references" / "portal-crawl-records.json"
JsonScalar: TypeAlias = None | bool | int | float | str
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def load_json_object(raw: str) -> dict[str, JsonValue]:
    loaded: JsonValue = json.loads(raw)
    assert isinstance(loaded, dict)
    return loaded


def make_zip(path: Path, entries: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, body in entries.items():
            archive.writestr(name, body)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_inspect_classifies_egovframe_distribution_archive(tmp_path: Path) -> None:
    archive = tmp_path / "egovframe-template-common-components-5.0.4.zip"
    make_zip(
        archive,
        {
            "pom.xml": "<project><groupId>org.egovframe</groupId></project>",
            "src/main/resources/application.yml": "spring:\n  datasource:\n    url: jdbc:h2:mem:test",
            "src/main/resources/egovframework/sqlmap/BoardMapper.xml": "<mapper namespace='BoardMapper'></mapper>",
            "DATABASE/hsql/sample.sql": "create table sample(id integer);",
        },
    )

    result = run_command(
        [
            sys.executable,
            str(DISTRIBUTION),
            "inspect",
            "--zip",
            str(archive),
            "--expected-sha256",
            sha256(archive),
            "--json",
        ]
    )

    payload = load_json_object(result.stdout)
    assert result.returncode == 0
    assert payload["safe"] is True
    assert payload["checksum_verified"] is True
    assert payload["distribution_type"] == "source-project"
    signals = payload["signals"]
    assert isinstance(signals, list)
    assert "maven-project" in signals
    assert "spring-config" in signals
    assert "mybatis-mapper" in signals
    assert "sql-script" in signals


def test_inspect_rejects_checksum_mismatch(tmp_path: Path) -> None:
    archive = tmp_path / "egovframe-runtime.zip"
    make_zip(archive, {"pom.xml": "<project />"})

    result = run_command(
        [
            sys.executable,
            str(DISTRIBUTION),
            "inspect",
            "--zip",
            str(archive),
            "--expected-sha256",
            "0" * 64,
            "--json",
        ]
    )

    payload = load_json_object(result.stdout)
    assert result.returncode == 1
    assert payload["checksum_verified"] is False
    assert "sha256 mismatch" in str(payload["errors"])


def test_inspect_rejects_zip_slip_paths(tmp_path: Path) -> None:
    archive = tmp_path / "egovframe-unsafe.zip"
    make_zip(archive, {"../outside.txt": "nope", "pom.xml": "<project />"})

    result = run_command([sys.executable, str(DISTRIBUTION), "inspect", "--zip", str(archive), "--json"])

    payload = load_json_object(result.stdout)
    assert result.returncode == 2
    assert payload["safe"] is False
    assert "../outside.txt" in str(payload["unsafe_entries"])


def test_inventory_summarizes_portal_zip_records() -> None:
    result = run_command([sys.executable, str(DISTRIBUTION), "inventory", "--portal-json", str(PORTAL_RECORDS), "--json"])

    payload = load_json_object(result.stdout)
    assert result.returncode == 0
    assert isinstance(payload["distinct_zip_names"], int)
    assert payload["distinct_zip_names"] >= 250
    assert isinstance(payload["checksum_mentions"], dict)
    checksum_mentions = payload["checksum_mentions"]
    md5_mentions = checksum_mentions["md5"]
    sha1_mentions = checksum_mentions["sha1"]
    assert isinstance(md5_mentions, int)
    assert isinstance(sha1_mentions, int)
    assert md5_mentions >= 500
    assert sha1_mentions >= 500
