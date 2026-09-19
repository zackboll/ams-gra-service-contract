#!/usr/bin/env python3
"""Validate, compose, and verify schema-source manifests without network access."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

try:
    from tools.validate import validate_document
    from tools.yaml_support import YamlInputError, load_path
except ModuleNotFoundError:  # Support direct execution as ``python tools/schema_sources.py``.
    from validate import validate_document
    from yaml_support import YamlInputError, load_path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "schema-source" / "v0.1" / "schema-source-manifest.schema.json"

# Public, stable diagnostic identities for schema-source manifest validation,
# composition, and local byte verification.
SS_SCHEMA = "SS_SCHEMA"
SS_UNSAFE_PATH = "SS_UNSAFE_PATH"
SS_DUPLICATE_FILE = "SS_DUPLICATE_FILE"
SS_FILE_ORDER = "SS_FILE_ORDER"
SS_ROOT_SCHEMA = "SS_ROOT_SCHEMA"
SS_FILE_OUTSIDE_ROOT = "SS_FILE_OUTSIDE_ROOT"
SS_FILE_MISSING = "SS_FILE_MISSING"
SS_FILE_READ = "SS_FILE_READ"
SS_HASH_MISMATCH = "SS_HASH_MISMATCH"
SS_SOURCE_ROOT_SET = "SS_SOURCE_ROOT_SET"
SS_BASELINE_SELECTION = "SS_BASELINE_SELECTION"
SS_EXTENSION_MAPPING = "SS_EXTENSION_MAPPING"
SS_EXTENSION_COMPATIBILITY = "SS_EXTENSION_COMPATIBILITY"
SS_MANIFEST_ID_COLLISION = "SS_MANIFEST_ID_COLLISION"

SCHEMA_SOURCE_DIAGNOSTIC_CODES = frozenset(
    {
        SS_SCHEMA, SS_UNSAFE_PATH, SS_DUPLICATE_FILE, SS_FILE_ORDER, SS_ROOT_SCHEMA,
        SS_FILE_OUTSIDE_ROOT, SS_FILE_MISSING, SS_FILE_READ, SS_HASH_MISMATCH,
        SS_SOURCE_ROOT_SET, SS_BASELINE_SELECTION, SS_EXTENSION_MAPPING,
        SS_EXTENSION_COMPATIBILITY, SS_MANIFEST_ID_COLLISION,
    }
)


@dataclass(frozen=True)
class Diagnostic:
    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.code} {self.path}: {self.message}" if self.path else f"{self.code} {self.message}"


@dataclass(frozen=True)
class SchemaSourceSet:
    """Internal deterministic selection of validated schema-source manifests."""

    baseline: dict[str, Any]
    extensions: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class VerifiedSchemaFile:
    """One manifest-declared file, retained as the bytes whose digest was verified."""

    path: str
    data: bytes


@dataclass(frozen=True)
class VerifiedSchemaSource:
    """Immutable verified snapshot of one selected schema source."""

    manifest_id: str
    root_schema: str
    files: tuple[VerifiedSchemaFile, ...]


@dataclass(frozen=True)
class VerifiedSchemaSourceSet:
    """Immutable verified snapshots in deterministic SchemaSourceSet order."""

    baseline: VerifiedSchemaSource
    extensions: tuple[VerifiedSchemaSource, ...]


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_manifest(path: Path) -> Any:
    return load_path(path)


def _format_json_path(parts: Iterable[Any]) -> str:
    result = "$"
    for part in parts:
        result += f"[{part}]" if isinstance(part, int) else f".{part}"
    return result


def schema_diagnostics(manifest: Any) -> list[Diagnostic]:
    validator = Draft202012Validator(load_schema(), format_checker=FormatChecker())
    return [
        Diagnostic(SS_SCHEMA, _format_json_path(error.absolute_path), error.message)
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
        diagnostics.append(Diagnostic(SS_UNSAFE_PATH, "$.root_schema", "must be a safe relative POSIX path"))

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
            diagnostics.append(Diagnostic(SS_UNSAFE_PATH, f"$.files[{index}].path", "must be a safe relative POSIX path"))
    if len(paths) != len(set(paths)):
        diagnostics.append(Diagnostic(SS_DUPLICATE_FILE, "$.files", "file paths must be unique"))
    if paths != sorted(paths):
        diagnostics.append(Diagnostic(SS_FILE_ORDER, "$.files", "file paths must be sorted lexicographically"))
    if isinstance(root_schema, str) and paths.count(root_schema) != 1:
        diagnostics.append(Diagnostic(SS_ROOT_SCHEMA, "$.root_schema", "must appear exactly once in $.files"))
    return diagnostics


def validate_manifest(manifest: Any) -> list[Diagnostic]:
    return schema_diagnostics(manifest) + semantic_diagnostics(manifest)


def validate_manifest_path(path: Path) -> tuple[Any | None, list[Diagnostic]]:
    try:
        manifest = load_manifest(path)
    except YamlInputError as exc:
        return None, [Diagnostic(SS_SCHEMA, "", f"could not parse {path}: {exc}")]
    return manifest, validate_manifest(manifest)


def verify_manifest(manifest: Any, source_root: Path) -> list[Diagnostic]:
    """Verify raw local bytes after manifest validation has succeeded."""
    _, diagnostics = load_verified_schema_source(manifest, source_root)
    return diagnostics


def load_verified_schema_source(manifest: Any, source_root: Path) -> tuple[VerifiedSchemaSource | None, list[Diagnostic]]:
    """Read each declared file once and retain precisely the digest-verified bytes."""
    diagnostics = validate_manifest(manifest)
    if diagnostics:
        return None, diagnostics
    root = source_root.resolve()
    files: list[VerifiedSchemaFile] = []
    for entry in manifest["files"]:
        relative_path = entry["path"]
        path = root / PurePosixPath(relative_path)
        resolved_path = path.resolve(strict=False)
        if not resolved_path.is_relative_to(root):
            diagnostics.append(Diagnostic(SS_FILE_OUTSIDE_ROOT, relative_path, "file resolves outside --source-root"))
            continue
        if not resolved_path.is_file():
            diagnostics.append(Diagnostic(SS_FILE_MISSING, relative_path, "file listed by manifest is missing"))
            continue
        try:
            data = resolved_path.read_bytes()
        except OSError as exc:
            diagnostics.append(Diagnostic(SS_FILE_READ, relative_path, f"could not read file listed by manifest: {exc}"))
            continue
        actual = hashlib.sha256(data).hexdigest()
        if actual != entry["sha256"]:
            diagnostics.append(
                Diagnostic(SS_HASH_MISMATCH, relative_path, f"expected sha256 {entry['sha256']}\n  actual   sha256 {actual}")
            )
            continue
        files.append(VerifiedSchemaFile(relative_path, data))
    if diagnostics:
        return None, diagnostics
    return VerifiedSchemaSource(manifest["id"], manifest["root_schema"], tuple(files)), []


def load_verified_schema_source_set(
    schema_source_set: SchemaSourceSet, source_roots_by_manifest_id: dict[str, Path]
) -> tuple[VerifiedSchemaSourceSet | None, list[Diagnostic]]:
    """Load all and only a composed source set, preserving extension order."""
    manifests = (schema_source_set.baseline, *schema_source_set.extensions)
    manifest_ids = [manifest["id"] for manifest in manifests]
    diagnostics: list[Diagnostic] = []
    if len(manifest_ids) != len(set(manifest_ids)):
        diagnostics.append(Diagnostic(SS_MANIFEST_ID_COLLISION, "$.schema_source_set", "baseline and extension manifest ids must be unique"))
    expected_ids = set(manifest_ids)
    supplied_ids = set(source_roots_by_manifest_id)
    for manifest_id in sorted(expected_ids - supplied_ids):
        diagnostics.append(Diagnostic(SS_SOURCE_ROOT_SET, "$.source_roots", f"missing source root for manifest {manifest_id!r}"))
    for manifest_id in sorted(supplied_ids - expected_ids):
        diagnostics.append(Diagnostic(SS_SOURCE_ROOT_SET, "$.source_roots", f"source root supplied for unselected manifest {manifest_id!r}"))
    if diagnostics:
        return None, diagnostics

    verified_sources: list[VerifiedSchemaSource] = []
    for manifest in manifests:
        verified_source, source_diagnostics = load_verified_schema_source(manifest, source_roots_by_manifest_id[manifest["id"]])
        diagnostics.extend(Diagnostic(diagnostic.code, f"{manifest['id']}:{diagnostic.path}", diagnostic.message) for diagnostic in source_diagnostics)
        if verified_source is not None:
            verified_sources.append(verified_source)
    if diagnostics:
        return None, diagnostics
    return VerifiedSchemaSourceSet(verified_sources[0], tuple(verified_sources[1:])), []


def compose_schema_source_set(
    contract: Any, baseline_manifest: Any, extension_manifests: Iterable[Any]
) -> tuple[SchemaSourceSet | None, list[Diagnostic]]:
    """Compose a validated baseline and exactly the contract-declared extensions.

    This operation validates metadata only; it does not verify source bytes.
    """
    diagnostics = [Diagnostic(diagnostic.code, diagnostic.path, diagnostic.message) for diagnostic in validate_document(contract)]
    diagnostics.extend(validate_manifest(baseline_manifest))
    extension_manifests = list(extension_manifests)
    for index, manifest in enumerate(extension_manifests):
        diagnostics.extend(
            Diagnostic(diagnostic.code, f"$.extension_manifests[{index}]{diagnostic.path[1:]}", diagnostic.message)
            for diagnostic in validate_manifest(manifest)
        )
    if diagnostics:
        return None, diagnostics

    baseline_version = contract["standards"]["uci_schema_version"]
    if baseline_manifest["role"] != "baseline":
        diagnostics.append(Diagnostic(SS_BASELINE_SELECTION, "$.baseline_manifest.role", "must be 'baseline'"))
    if baseline_manifest["schema_family"] != "uci":
        diagnostics.append(Diagnostic(SS_BASELINE_SELECTION, "$.baseline_manifest.schema_family", "must be 'uci'"))
    if baseline_manifest["schema_version"] != baseline_version:
        diagnostics.append(
            Diagnostic(SS_BASELINE_SELECTION,
                "$.baseline_manifest.schema_version",
                f"must match contract UCI baseline version {baseline_version!r}",
            )
        )

    declared_ids = contract["standards"].get("uci_extension_schemas", [])
    manifests_by_id: dict[str, dict[str, Any]] = {}
    for index, manifest in enumerate(extension_manifests):
        manifest_id = manifest["id"]
        if manifest_id == baseline_manifest["id"]:
            diagnostics.append(Diagnostic(SS_MANIFEST_ID_COLLISION, f"$.extension_manifests[{index}].id", f"extension manifest id {manifest_id!r} collides with baseline manifest id"))
        if manifest_id in manifests_by_id:
            diagnostics.append(Diagnostic(SS_MANIFEST_ID_COLLISION, f"$.extension_manifests[{index}].id", f"duplicate supplied manifest id {manifest_id!r}"))
        else:
            manifests_by_id[manifest_id] = manifest

    declared_id_set = set(declared_ids)
    for manifest_id in sorted(set(manifests_by_id) - declared_id_set):
        diagnostics.append(Diagnostic(SS_EXTENSION_MAPPING, "$.extension_manifests", f"undeclared extension manifest id {manifest_id!r}"))
    for manifest_id in declared_ids:
        if manifest_id not in manifests_by_id:
            diagnostics.append(Diagnostic(SS_EXTENSION_MAPPING, "$.standards.uci_extension_schemas", f"missing declared extension manifest id {manifest_id!r}"))

    ordered_extensions: list[dict[str, Any]] = []
    for manifest_id in declared_ids:
        manifest = manifests_by_id.get(manifest_id)
        if manifest is None:
            continue
        if manifest["role"] != "extension":
            diagnostics.append(Diagnostic(SS_EXTENSION_MAPPING, "$.extension_manifests", f"manifest {manifest_id!r} must have role 'extension'"))
        if manifest["schema_family"] != "uci":
            diagnostics.append(Diagnostic(SS_EXTENSION_MAPPING, "$.extension_manifests", f"manifest {manifest_id!r} must have schema_family 'uci'"))
        if manifest["role"] == "extension" and baseline_version not in manifest["compatible_baseline_versions"]:
            diagnostics.append(
                Diagnostic(SS_EXTENSION_COMPATIBILITY,
                    "$.extension_manifests",
                    f"manifest {manifest_id!r} is not compatible with UCI baseline version {baseline_version!r}",
                )
            )
        ordered_extensions.append(manifest)

    if diagnostics:
        return None, diagnostics
    return SchemaSourceSet(baseline_manifest, tuple(ordered_extensions)), []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate", help="validate a manifest")
    validate_parser.add_argument("manifest", type=Path)
    verify_parser = subparsers.add_parser("verify", help="verify declared bytes in a local source tree")
    verify_parser.add_argument("manifest", type=Path)
    verify_parser.add_argument("--source-root", type=Path, required=True)
    compose_parser = subparsers.add_parser("compose", help="compose a contract's schema-source manifest set")
    compose_parser.add_argument("--contract", type=Path, required=True)
    compose_parser.add_argument("--baseline-manifest", type=Path, required=True)
    compose_parser.add_argument("--extension-manifest", type=Path, action="append", default=[])
    args = parser.parse_args(argv)

    if args.command == "compose":
        try:
            contract = load_path(args.contract)
        except YamlInputError as exc:
            print(f"FAIL {args.contract.resolve()}\n  SC_SCHEMA could not parse contract: {exc}")
            return 1
        baseline_path = args.baseline_manifest.resolve()
        baseline_manifest, baseline_diagnostics = validate_manifest_path(baseline_path)
        extension_paths = [path.resolve() for path in args.extension_manifest]
        extension_results = [validate_manifest_path(path) for path in extension_paths]
        diagnostics = baseline_diagnostics[:]
        for path, (_, manifest_diagnostics) in zip(extension_paths, extension_results):
            diagnostics.extend(Diagnostic(diagnostic.code, str(path), diagnostic.message) for diagnostic in manifest_diagnostics)
        if not diagnostics:
            schema_set, diagnostics = compose_schema_source_set(
                contract, baseline_manifest, [manifest for manifest, _ in extension_results]
            )
        else:
            schema_set = None
        if diagnostics:
            print("FAIL schema-source set")
            for diagnostic in diagnostics:
                print(f"  {diagnostic}")
            return 1
        print("OK schema-source set")
        print(f"  baseline: {schema_set.baseline['id']}")
        if schema_set.extensions:
            print("  extensions:")
            for manifest in schema_set.extensions:
                print(f"    - {manifest['id']}")
        else:
            print("  extensions: none")
        return 0

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
