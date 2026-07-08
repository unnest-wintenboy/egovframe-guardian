from __future__ import annotations

import hashlib
import json
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Final, TypeAlias


JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
CHUNK_SIZE: Final = 1024 * 1024
HASH_ALGORITHMS: Final = ("md5", "sha1", "sha256")
SCRIPT_OR_BINARY_SUFFIXES: Final = {
    ".bat",
    ".cmd",
    ".dll",
    ".dylib",
    ".ear",
    ".exe",
    ".jar",
    ".ps1",
    ".sh",
    ".so",
    ".war",
}


@dataclass(frozen=True, slots=True)
class ExpectedHashes:
    md5: str | None = None
    sha1: str | None = None
    sha256: str | None = None


@dataclass(frozen=True, slots=True)
class ArchiveHashes:
    md5: str
    sha1: str
    sha256: str

    def to_json(self) -> dict[str, JsonValue]:
        return {"md5": self.md5, "sha1": self.sha1, "sha256": self.sha256}


@dataclass(frozen=True, slots=True)
class ZipSummary:
    entry_count: int
    total_uncompressed_bytes: int
    extension_counts: dict[str, int]
    largest_entries: list[JsonValue]

    def to_json(self) -> dict[str, JsonValue]:
        extension_counts_json: dict[str, JsonValue] = {
            key: value for key, value in self.extension_counts.items()
        }
        return {
            "entry_count": self.entry_count,
            "total_uncompressed_bytes": self.total_uncompressed_bytes,
            "extension_counts": extension_counts_json,
            "largest_entries": self.largest_entries,
        }


def archive_hashes(path: Path) -> ArchiveHashes:
    md5 = hashlib.md5(usedforsecurity=False)
    sha1 = hashlib.sha1(usedforsecurity=False)
    sha256 = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK_SIZE):
            md5.update(chunk)
            sha1.update(chunk)
            sha256.update(chunk)
    return ArchiveHashes(md5.hexdigest(), sha1.hexdigest(), sha256.hexdigest())


def checksum_errors(hashes: ArchiveHashes, expected: ExpectedHashes) -> list[str]:
    errors: list[str] = []
    if expected.md5 is not None and expected.md5 != hashes.md5:
        errors.append("md5 mismatch")
    if expected.sha1 is not None and expected.sha1 != hashes.sha1:
        errors.append("sha1 mismatch")
    if expected.sha256 is not None and expected.sha256 != hashes.sha256:
        errors.append("sha256 mismatch")
    return errors


def has_expected_hash(expected: ExpectedHashes) -> bool:
    return expected.md5 is not None or expected.sha1 is not None or expected.sha256 is not None


def is_unsafe_zip_name(name: str) -> bool:
    normalized = name.replace("\\", "/")
    if "\x00" in name or normalized.startswith("/"):
        return True
    if PureWindowsPath(name).drive:
        return True
    return ".." in PurePosixPath(normalized).parts


def entry_signals(name: str) -> set[str]:
    lowered = name.lower()
    suffix = Path(lowered).suffix
    signals: set[str] = set()
    if lowered == "pom.xml" or lowered.endswith("/pom.xml"):
        signals.add("maven-project")
    if lowered.endswith(("/build.gradle", "/build.gradle.kts", "/settings.gradle", "/settings.gradle.kts")):
        signals.add("gradle-project")
    if lowered.endswith(("/application.properties", "/application.yml", "/application.yaml")):
        signals.add("spring-config")
    if lowered.endswith(".xml") and ("mapper" in lowered or "sqlmap" in lowered):
        signals.add("mybatis-mapper")
    if lowered.endswith(".jsp") or "/web-inf/" in lowered:
        signals.add("jsp-webapp")
    if lowered.endswith(".sql"):
        signals.add("sql-script")
    if lowered.endswith("/dockerfile") or lowered.endswith(("/docker-compose.yml", "/docker-compose.yaml")):
        signals.add("docker")
    if "kubernetes" in lowered or lowered.endswith(("/deployment.yml", "/deployment.yaml")):
        signals.add("kubernetes")
    if lowered.startswith(("plugins/", "features/")) or lowered.endswith("/.eclipseproduct"):
        signals.add("eclipse-plugin-bundle")
    if lowered.endswith(("/index.html", "/package-list", "/element-list")):
        signals.add("documentation")
    if lowered.endswith(".java"):
        signals.add("java-source")
    if suffix in SCRIPT_OR_BINARY_SUFFIXES:
        signals.add("script-or-binary")
    return signals


def distribution_type(signals: set[str]) -> str:
    if "eclipse-plugin-bundle" in signals:
        return "developer-tooling"
    if "maven-project" in signals or "gradle-project" in signals or "java-source" in signals:
        return "source-project"
    if "documentation" in signals:
        return "documentation"
    if "script-or-binary" in signals:
        return "binary-package"
    return "archive"


def summarize_zip(infos: list[zipfile.ZipInfo]) -> ZipSummary:
    extensions: Counter[str] = Counter()
    total_size = 0
    for info in infos:
        if info.is_dir():
            continue
        total_size += info.file_size
        suffix = Path(info.filename.lower()).suffix or "[none]"
        extensions[suffix] += 1
    largest = sorted((info for info in infos if not info.is_dir()), key=lambda item: item.file_size, reverse=True)[:5]
    largest_entries: list[JsonValue] = []
    for info in largest:
        largest_entries.append({"name": info.filename, "bytes": info.file_size})
    return ZipSummary(len(infos), total_size, dict(sorted(extensions.items())), largest_entries)


def strings_to_json(values: list[str]) -> list[JsonValue]:
    json_values: list[JsonValue] = []
    for value in values:
        json_values.append(value)
    return json_values


def inspect_archive(path: Path, expected: ExpectedHashes) -> dict[str, JsonValue]:
    hashes = archive_hashes(path)
    errors = checksum_errors(hashes, expected)
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
    unsafe_entries = [info.filename for info in infos if is_unsafe_zip_name(info.filename)]
    signals = sorted({signal for info in infos for signal in entry_signals(info.filename)})
    script_entries = [
        info.filename
        for info in infos
        if Path(info.filename.lower()).suffix in SCRIPT_OR_BINARY_SUFFIXES
    ][:10]
    if unsafe_entries:
        errors.append("unsafe archive paths")
    warnings = ["script or binary entries present; do not execute automatically"] if script_entries else []
    checksum_verified = has_expected_hash(expected) and not checksum_errors(hashes, expected)
    return {
        "archive": str(path),
        "safe": not unsafe_entries,
        "checksum_verified": checksum_verified,
        "hashes": hashes.to_json(),
        "errors": strings_to_json(errors),
        "unsafe_entries": strings_to_json(unsafe_entries),
        "warnings": strings_to_json(warnings),
        "script_or_binary_entries": strings_to_json(script_entries),
        "distribution_type": distribution_type(set(signals)),
        "signals": strings_to_json(signals),
        "summary": summarize_zip(infos).to_json(),
        "next_steps": [
            "compare hashes with the official portal page",
            "inspect this report before extracting",
            "extract only into a temporary or sandbox directory",
            "adapt source projects by matching controller, service, mapper, config, and SQL layers",
        ],
    }


def load_json(path: Path) -> JsonValue:
    loaded: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    return loaded


def portal_inventory(path: Path) -> dict[str, JsonValue]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise SystemExit("portal JSON must be an object")
    records = payload.get("records")
    if not isinstance(records, list):
        raise SystemExit("portal JSON must contain a records list")
    zip_names: set[str] = set()
    checksum_mentions: Counter[str] = Counter()
    attachment_records = 0
    zip_records = 0
    for record in records:
        if not isinstance(record, dict):
            continue
        text = "\n".join(str(value) for value in record.values())
        lowered = text.lower()
        zip_records += 1 if ".zip" in lowered else 0
        for algorithm in HASH_ALGORITHMS:
            checksum_mentions[algorithm] += lowered.count(algorithm)
        tokens = text.replace("[", " ").replace("]", " ").replace("(", " ").replace(")", " ").split()
        for token in tokens:
            cleaned = token.strip(".,;:\"'`")
            if cleaned.lower().endswith(".zip"):
                zip_names.add(cleaned)
        if "readdownloadfile.do" in lowered and ".zip" in lowered:
            attachment_records += 1
    return {
        "portal_json": str(path),
        "records": len(records),
        "zip_records": zip_records,
        "distinct_zip_names": len(zip_names),
        "checksum_mentions": dict(sorted(checksum_mentions.items())),
        "attachment_records": attachment_records,
    }
