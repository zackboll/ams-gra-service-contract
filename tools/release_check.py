#!/usr/bin/env python3
"""Check repository release-support metadata without network access or mutation."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator

try:
    from tools.conformance import canonical_sha256
    from tools.schema_sources import validate_manifest_path
    from tools.validate import validate_profile_path
except ModuleNotFoundError:
    from conformance import canonical_sha256
    from schema_sources import validate_manifest_path
    from validate import validate_profile_path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema/tooling/release/v0.1/support-manifest.schema.json"
PROJECT_RELEASE = "0.2.0"
RC_SCHEMA = "RC_SCHEMA"
RC_PATH = "RC_PATH"
RC_VERSION = "RC_VERSION"
RC_FINGERPRINT = "RC_FINGERPRINT"
RC_CONFORMANCE = "RC_CONFORMANCE"
RC_PROFILE = "RC_PROFILE"
RC_SCHEMA_SOURCE = "RC_SCHEMA_SOURCE"
RC_CHANGELOG = "RC_CHANGELOG"
RELEASE_CHECK_DIAGNOSTIC_CODES = frozenset({RC_SCHEMA, RC_PATH, RC_VERSION, RC_FINGERPRINT, RC_CONFORMANCE, RC_PROFILE, RC_SCHEMA_SOURCE, RC_CHANGELOG})


@dataclass(frozen=True)
class Diagnostic:
    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.code} {self.path}: {self.message}" if self.path else f"{self.code} {self.message}"


def _safe_relative_path(value: str) -> bool:
    path = PurePosixPath(value)
    return not ("\\" in value or path.is_absolute() or ".." in path.parts or str(path) in {".", ""})


def _repository_file(root: Path, value: str, diagnostic_path: str, diagnostics: list[Diagnostic]) -> Path | None:
    if not _safe_relative_path(value):
        diagnostics.append(Diagnostic(RC_PATH, diagnostic_path, "path must be a safe repository-relative POSIX path"))
        return None
    candidate = (root / value).resolve()
    if root not in candidate.parents or not candidate.is_file():
        diagnostics.append(Diagnostic(RC_PATH, diagnostic_path, "referenced file must exist under the repository root"))
        return None
    return candidate


def load_manifest(path: Path) -> tuple[dict[str, Any] | None, list[Diagnostic]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [Diagnostic(RC_SCHEMA, "", f"could not parse support manifest: {exc}")]
    errors = sorted(Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))).iter_errors(value), key=lambda error: list(error.absolute_path))
    if errors:
        return None, [Diagnostic(RC_SCHEMA, "$" + "".join(f"[{part}]" if isinstance(part, int) else f".{part}" for part in error.absolute_path), error.message) for error in errors]
    return value, []


def check_manifest(manifest: dict[str, Any], root: Path = ROOT, changelog_path: Path | None = None) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if manifest["project_release"] != PROJECT_RELEASE:
        diagnostics.append(Diagnostic(RC_VERSION, "$.project_release", f"expected prospective repository release {PROJECT_RELEASE!r}"))
    portable = manifest["portable_contract"]
    versions = portable["versions"]
    if versions != ["0.1"]:
        diagnostics.append(Diagnostic(RC_VERSION, "$.portable_contract.versions", "supported portable contract versions must be exactly ['0.1']"))
    schema_path = _repository_file(root, portable["schema"], "$.portable_contract.schema", diagnostics)
    conformance_path = _repository_file(root, portable["conformance_manifest"], "$.portable_contract.conformance_manifest", diagnostics)
    if schema_path and canonical_sha256(schema_path) != portable["canonical_schema_sha256"]:
        diagnostics.append(Diagnostic(RC_FINGERPRINT, "$.portable_contract.canonical_schema_sha256", "canonical portable-schema SHA-256 differs"))
    if conformance_path:
        try:
            conformance = json.loads(conformance_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            diagnostics.append(Diagnostic(RC_CONFORMANCE, "$.portable_contract.conformance_manifest", f"could not parse conformance manifest: {exc}"))
        else:
            if conformance.get("contract_version") not in versions:
                diagnostics.append(Diagnostic(RC_CONFORMANCE, "$.portable_contract.conformance_manifest", "conformance contract_version is not supported by this manifest"))
            if conformance.get("schema_canonical_sha256") != portable["canonical_schema_sha256"]:
                diagnostics.append(Diagnostic(RC_CONFORMANCE, "$.portable_contract.conformance_manifest", "conformance fingerprint differs from support manifest"))
    for index, entry in enumerate(manifest["oms_profiles"]):
        path = _repository_file(root, entry["path"], f"$.oms_profiles[{index}].path", diagnostics)
        if not path:
            continue
        profile, profile_diagnostics = validate_profile_path(path)
        if profile_diagnostics:
            diagnostics.append(Diagnostic(RC_PROFILE, f"$.oms_profiles[{index}].path", "profile does not validate"))
            continue
        for key, expected in (("id", entry["id"]), ("oms_version", entry["oms_version"]), ("profile_version", entry["profile_format"])):
            if profile.get(key) != expected:
                diagnostics.append(Diagnostic(RC_PROFILE, f"$.oms_profiles[{index}].{key}", f"profile {key} does not match manifest"))
        if not set(versions).issubset(profile.get("contract_versions", [])):
            diagnostics.append(Diagnostic(RC_PROFILE, f"$.oms_profiles[{index}]", "profile does not support every declared portable contract version"))
    uci = manifest["uci"]
    observed_versions: list[str] = []
    for index, entry in enumerate(uci["baseline_manifests"]):
        entry_path = f"$.uci.baseline_manifests[{index}]"
        path = _repository_file(root, entry["path"], f"{entry_path}.path", diagnostics)
        if not path:
            continue
        source_manifest, source_diagnostics = validate_manifest_path(path)
        if source_diagnostics:
            diagnostics.append(Diagnostic(RC_SCHEMA_SOURCE, entry_path, "schema-source manifest does not validate"))
        else:
            for key, expected in (("id", entry["id"]), ("schema_version", entry["schema_version"]), ("schema_family", "uci"), ("role", "baseline")):
                if source_manifest.get(key) != expected:
                    diagnostics.append(Diagnostic(RC_SCHEMA_SOURCE, f"{entry_path}.{key}", f"schema-source manifest {key} does not match required baseline metadata"))
            observed_versions.append(source_manifest["schema_version"])
    if len(observed_versions) != len(set(observed_versions)) or set(observed_versions) != set(uci["baseline_versions"]):
        diagnostics.append(Diagnostic(RC_SCHEMA_SOURCE, "$.uci", "baseline manifest versions must exactly match declared baseline_versions"))
    changelog = changelog_path or root / "CHANGELOG.md"
    if not changelog.is_file():
        diagnostics.append(Diagnostic(RC_CHANGELOG, "CHANGELOG.md", "CHANGELOG.md is missing"))
    else:
        headings = changelog.read_text(encoding="utf-8").splitlines()
        if sum(line == "## [Unreleased]" for line in headings) != 1:
            diagnostics.append(Diagnostic(RC_CHANGELOG, "CHANGELOG.md", "CHANGELOG must contain exactly one '## [Unreleased]' heading"))
        if not any(line.startswith("## [0.2.0]") for line in headings):
            diagnostics.append(Diagnostic(RC_CHANGELOG, "CHANGELOG.md", "CHANGELOG must contain a prospective [0.2.0] section"))
        if not any(line == "## [0.1.0] - 2026-09-18" for line in headings):
            diagnostics.append(Diagnostic(RC_CHANGELOG, "CHANGELOG.md", "historical [0.1.0] section must remain present"))
    return diagnostics


def check_path(path: Path, root: Path = ROOT) -> list[Diagnostic]:
    manifest, diagnostics = load_manifest(path)
    return diagnostics if diagnostics else check_manifest(manifest, root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args(argv)
    diagnostics = check_path(args.manifest)
    if diagnostics:
        for diagnostic in diagnostics:
            print(diagnostic)
        return 1
    print(f"OK: release support manifest {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
