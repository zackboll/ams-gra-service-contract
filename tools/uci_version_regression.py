#!/usr/bin/env python3
"""Compare pinned UCI 2.5 and 2.6 resolver results from supplied local bytes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from tools.schema_sources import VerifiedSchemaSourceSet, load_verified_schema_source, validate_manifest_path
    from tools.uci_resolver import UciMessageDefinition, load_message_definitions
except ModuleNotFoundError:
    from schema_sources import VerifiedSchemaSourceSet, load_verified_schema_source, validate_manifest_path
    from uci_resolver import UciMessageDefinition, load_message_definitions

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_A = ROOT / "schema-sources" / "uci" / "2.5" / "manifest.yaml"
MANIFEST_B = ROOT / "schema-sources" / "uci" / "2.6" / "manifest.yaml"
EXPECTED_COUNTS = {"2.5": {"primitive_tagged_messages": 722, "resolved_message_types": 722, "complex_types": 722, "simple_types": 0}, "2.6": {"primitive_tagged_messages": 725, "resolved_message_types": 725, "complex_types": 725, "simple_types": 0}}
CONTINUITY_MESSAGES = ("ServiceStatus", "ServiceStatusDataRequest", "ServiceStatusDataRequestStatus", "FileMetadata", "FileLocation", "SubsystemStatus", "SubsystemStatusDataRequest", "SubsystemStatusDataRequestStatus", "ESM_SettingsCommand", "ESM_SettingsCommandStatus")


def record(item: UciMessageDefinition | None) -> dict[str, str] | None:
    if item is None:
        return None
    assert item.type_declaration is not None
    return {"local_name": item.local_name, "expanded_name": item.expanded_name, "primitive": item.primitive, "type_expanded_name": item.type_expanded_name, "declaration_kind": item.type_declaration.kind}


def classify(a: dict[str, str] | None, b: dict[str, str] | None) -> str:
    if a is None and b is None:
        return "absent in both"
    if a is None:
        return "newly resolvable"
    if b is None:
        return "absent in 2.6"
    return "unchanged" if a == b else "changed"


def analyze(manifest_path: Path, source_root: Path) -> tuple[dict[str, Any], dict[str, UciMessageDefinition]]:
    manifest, diagnostics = validate_manifest_path(manifest_path)
    if diagnostics:
        raise ValueError("manifest validation failed: " + "; ".join(map(str, diagnostics)))
    verified, diagnostics = load_verified_schema_source(manifest, source_root)
    if diagnostics:
        raise ValueError("manifest verification failed: " + "; ".join(map(str, diagnostics)))
    definitions = load_message_definitions(VerifiedSchemaSourceSet(verified, ()))
    counts = {"primitive_tagged_messages": len(definitions), "resolved_message_types": sum(item.type_declaration is not None for item in definitions), "complex_types": sum(item.type_declaration is not None and item.type_declaration.kind == "complex" for item in definitions), "simple_types": sum(item.type_declaration is not None and item.type_declaration.kind == "simple" for item in definitions)}
    expected = EXPECTED_COUNTS[manifest["schema_version"]]
    if counts != expected:
        raise ValueError(f"unexpected UCI {manifest['schema_version']} resolver counts: {counts!r}, expected {expected!r}")
    return {"version": manifest["schema_version"], "manifest_id": manifest["id"], "counts": counts}, {item.local_name: item for item in definitions}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uci-25-source-root", type=Path, required=True)
    parser.add_argument("--uci-26-source-root", type=Path, required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        baseline_a, definitions_a = analyze(MANIFEST_A, args.uci_25_source_root)
        baseline_b, definitions_b = analyze(MANIFEST_B, args.uci_26_source_root)
    except ValueError as exc:
        print(f"FAIL {exc}")
        return 1
    messages = [{"message": name, "version_a": record(definitions_a.get(name)), "version_b": record(definitions_b.get(name)), "classification": classify(record(definitions_a.get(name)), record(definitions_b.get(name)))} for name in CONTINUITY_MESSAGES]
    result = {"baseline_a": baseline_a, "baseline_b": baseline_b, "messages": messages}
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for label in ("baseline_a", "baseline_b"):
            baseline = result[label]
            print(f"{label}: UCI {baseline['version']} ({baseline['manifest_id']})")
            print("  " + ", ".join(f"{key}={value}" for key, value in baseline["counts"].items()))
        for item in messages:
            print(f"{item['message']}: {item['classification']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
