#!/usr/bin/env python3
"""Validate schema-source manifests and verify declared local source bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "schema-source" / "v0.1" / "schema-source-manifest.schema.json"


@dataclass(frozen=True)
class Diagnostic:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}" if self.path else self.message


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_manifest(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def _format_json_path(parts: Iterable[Any]) -> str:
    result = "$"
    for part in parts:
        result += f"[{part}]" if isinstance(part, int) else f".{part}"
    return result


def schema_diagnostics(manifest: Any) -> list[Diagnostic]:
    validator = Draft202012Validator(load_schema(), format_checker=FormatChecker())
    return [
        Diagnostic(_format_json_path(error.absolute_path), error.message)
        for error in sorted(validator.iter_errors(manifest), key=lambda error: list(error.absolute_path))
    ]


def is_safe_manifest_path(value: str) -> bool:
    """Return whether value is a non-empty canonical relative POSIX path."""
    if (
        not value
        or "\\" in value
        or value.startswith("/")
        or "//" in value
        or re.match(r"^[A-Za-z]:", value)
        or any(part in (".", "..") for part in value.split("/"))
    ):
        return False
    path = PurePosixPath(value)
    return not path.is_absolute()


def semantic_diagnostics(manifest: Any) -> list[Diagnostic]:
    if not isinstance(manifest, dict):
        return []
    diagnostics: list[Diagnostic] = []
    root_schema = manifest.get("root_schema")
    if isinstance(root_schema, str) and not is_safe_manifest_path(root_schema):
        diagnostics.append(Diagnostic("$.root_schema", "must be a safe relative POSIX path"))

    files = manifest.get("files")
    if not isinstance(files, list):
        return diagnostics
    paths: list[str] = []
    for index, entry in enumerate(files):
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            continue
        path = entry["path"]
        paths.append(path)
        if not is_safe_manifest_path(path):
            diagnostics.append(Diagnostic(f"$.files[{index}].path", "must be a safe relative POSIX path"))
    if len(paths) != len(set(paths)):
        diagnostics.append(Diagnostic("$.files", "file paths must be unique"))
    if paths != sorted(paths):
        diagnostics.append(Diagnostic("$.files", "file paths must be sorted lexicographically"))
    if isinstance(root_schema, str) and paths.count(root_schema) != 1:
        diagnostics.append(Diagnostic("$.root_schema", "must appear exactly once in $.files"))
    return diagnostics


def validate_manifest(manifest: Any) -> list[Diagnostic]:
    return schema_diagnostics(manifest) + semantic_diagnostics(manifest)


def validate_manifest_path(path: Path) -> tuple[Any | None, list[Diagnostic]]:
    try:
        manifest = load_manifest(path)
    except (OSError, yaml.YAMLError) as exc:
        return None, [Diagnostic("", f"could not parse {path}: {exc}")]
    return manifest, validate_manifest(manifest)


def verify_manifest(manifest: Any, source_root: Path) -> list[Diagnostic]:
    """Verify raw local bytes after manifest validation has succeeded."""
    diagnostics = validate_manifest(manifest)
    if diagnostics:
        return diagnostics
    root = source_root.resolve()
    for entry in manifest["files"]:
        relative_path = entry["path"]
        path = root / PurePosixPath(relative_path)
        resolved_path = path.resolve(strict=False)
        if not resolved_path.is_relative_to(root):
            diagnostics.append(Diagnostic(relative_path, "file resolves outside --source-root"))
            continue
        if not resolved_path.is_file():
            diagnostics.append(Diagnostic(relative_path, "file listed by manifest is missing"))
            continue
        actual = hashlib.sha256(resolved_path.read_bytes()).hexdigest()
        if actual != entry["sha256"]:
            diagnostics.append(
                Diagnostic(relative_path, f"expected sha256 {entry['sha256']}\n  actual   sha256 {actual}")
            )
    return diagnostics


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate", help="validate a manifest")
    validate_parser.add_argument("manifest", type=Path)
    verify_parser = subparsers.add_parser("verify", help="verify declared bytes in a local source tree")
    verify_parser.add_argument("manifest", type=Path)
    verify_parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args(argv)

    manifest_path = args.manifest.resolve()
    manifest, diagnostics = validate_manifest_path(manifest_path)
    if not diagnostics and args.command == "verify":
        diagnostics = verify_manifest(manifest, args.source_root)
    if diagnostics:
        print(f"FAIL {manifest_path}")
        for diagnostic in diagnostics:
            print(f"  {diagnostic}")
        return 1
    print(f"OK   {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
