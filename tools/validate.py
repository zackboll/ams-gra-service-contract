#!/usr/bin/env python3
"""Validate v0.1 AMS GRA machine-readable service contracts and opt-in profiles.

This validator intentionally performs only:
  1. JSON Schema structural validation; and
  2. local cross-field semantic validation.

It does not load or resolve UCI XSDs. The separate non-normative reference
resolver exercises that behavior against manifest-verified snapshots.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

try:
    from tools.yaml_support import YamlInputError, load_path
except ModuleNotFoundError:  # Support direct execution as ``python tools/validate.py``.
    from yaml_support import YamlInputError, load_path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "v0.1" / "service-contract.schema.json"
PROFILE_SCHEMA_PATH = ROOT / "schema" / "profile" / "v0.1" / "oms-profile.schema.json"


@dataclass(frozen=True)
class Diagnostic:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}" if self.path else self.message


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_profile_schema() -> dict[str, Any]:
    return json.loads(PROFILE_SCHEMA_PATH.read_text(encoding="utf-8"))


def load_document(path: Path) -> Any:
    return load_path(path)


def _format_json_path(parts: Iterable[Any]) -> str:
    result = "$"
    for part in parts:
        if isinstance(part, int):
            result += f"[{part}]"
        else:
            result += f".{part}"
    return result


def schema_diagnostics(document: Any) -> list[Diagnostic]:
    validator = Draft202012Validator(load_schema(), format_checker=FormatChecker())
    diagnostics: list[Diagnostic] = []
    for error in sorted(validator.iter_errors(document), key=lambda e: list(e.absolute_path)):
        diagnostics.append(Diagnostic(_format_json_path(error.absolute_path), error.message))
    return diagnostics


def profile_schema_diagnostics(profile: Any) -> list[Diagnostic]:
    validator = Draft202012Validator(load_profile_schema(), format_checker=FormatChecker())
    return [
        Diagnostic(_format_json_path(error.absolute_path), error.message)
        for error in sorted(validator.iter_errors(profile), key=lambda e: list(e.absolute_path))
    ]


def _duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def semantic_diagnostics(document: Any) -> list[Diagnostic]:
    # Structural validation should run first. Be defensive here so malformed
    # documents produce useful schema errors rather than validator tracebacks.
    if not isinstance(document, dict):
        return []

    diagnostics: list[Diagnostic] = []

    sources = document.get("sources", [])
    if isinstance(sources, list):
        source_ids = [s.get("id") for s in sources if isinstance(s, dict) and isinstance(s.get("id"), str)]
    else:
        source_ids = []
    source_id_set = set(source_ids)

    for dup in sorted(_duplicates(source_ids)):
        diagnostics.append(Diagnostic("$.sources", f"duplicate source id {dup!r}"))

    functions = document.get("functions", [])
    if not isinstance(functions, list):
        return diagnostics

    function_ids = [f.get("id") for f in functions if isinstance(f, dict) and isinstance(f.get("id"), str)]
    for dup in sorted(_duplicates(function_ids)):
        diagnostics.append(Diagnostic("$.functions", f"duplicate function id {dup!r}"))

    def check_traceability(items: Any, base: str) -> None:
        if not isinstance(items, list):
            return
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            source = item.get("source")
            if isinstance(source, str) and source not in source_id_set:
                diagnostics.append(
                    Diagnostic(f"{base}[{idx}].source", f"unknown source id {source!r}")
                )

    for f_idx, function in enumerate(functions):
        if not isinstance(function, dict):
            continue
        fbase = f"$.functions[{f_idx}]"
        check_traceability(function.get("traceability", []), f"{fbase}.traceability")

        exchanges = function.get("exchanges", [])
        if not isinstance(exchanges, list):
            continue

        exchange_ids = [e.get("id") for e in exchanges if isinstance(e, dict) and isinstance(e.get("id"), str)]
        for dup in sorted(_duplicates(exchange_ids)):
            diagnostics.append(Diagnostic(f"{fbase}.exchanges", f"duplicate exchange id {dup!r}"))

        for e_idx, exchange in enumerate(exchanges):
            if isinstance(exchange, dict):
                check_traceability(
                    exchange.get("traceability", []),
                    f"{fbase}.exchanges[{e_idx}].traceability",
                )

    return diagnostics


def profile_semantic_diagnostics(profile: Any) -> list[Diagnostic]:
    """Validate source references and uniqueness required by the current profile model."""
    if not isinstance(profile, dict):
        return []

    diagnostics: list[Diagnostic] = []
    sources = profile.get("sources", [])
    source_ids = [
        source.get("id")
        for source in sources
        if isinstance(source, dict) and isinstance(source.get("id"), str)
    ]
    for duplicate in sorted(_duplicates(source_ids)):
        diagnostics.append(Diagnostic("$.sources", f"duplicate source id {duplicate!r}"))
    source_id_set = set(source_ids)

    functions = profile.get("required_functions", [])
    function_names = [
        function.get("name")
        for function in functions
        if isinstance(function, dict) and isinstance(function.get("name"), str)
    ]
    for duplicate in sorted(_duplicates(function_names)):
        diagnostics.append(Diagnostic("$.required_functions", f"duplicate required function name {duplicate!r}"))

    for index, function in enumerate(functions):
        if not isinstance(function, dict):
            continue
        applies_to = function.get("applies_to", [])
        if not isinstance(applies_to, list):
            applies_to = []
        applies_to = [kind for kind in applies_to if isinstance(kind, str)]
        for duplicate in sorted(_duplicates(applies_to)):
            diagnostics.append(
                Diagnostic(f"$.required_functions[{index}].applies_to", f"duplicate component kind {duplicate!r}")
            )
        for trace_index, trace in enumerate(function.get("traceability", [])):
            if isinstance(trace, dict) and trace.get("source") not in source_id_set:
                diagnostics.append(
                    Diagnostic(
                        f"$.required_functions[{index}].traceability[{trace_index}].source",
                        f"unknown source id {trace.get('source')!r}",
                    )
                )
        exchanges = function.get("required_exchanges", [])
        if not isinstance(exchanges, list):
            exchanges = []
        exchange_keys: list[tuple[str, str, str, str, str]] = []
        for exchange_index, exchange in enumerate(exchanges):
            if not isinstance(exchange, dict):
                continue
            key = required_exchange_identity(exchange)
            if key is not None:
                exchange_keys.append(key)
            for trace_index, trace in enumerate(exchange.get("traceability", [])):
                if isinstance(trace, dict) and trace.get("source") not in source_id_set:
                    diagnostics.append(
                        Diagnostic(
                            f"$.required_functions[{index}].required_exchanges[{exchange_index}]."
                            f"traceability[{trace_index}].source",
                            f"unknown source id {trace.get('source')!r}",
                        )
                    )
        seen_exchange_keys: set[tuple[str, str, str, str, str]] = set()
        duplicate_exchange_keys: set[tuple[str, str, str, str, str]] = set()
        for key in exchange_keys:
            if key in seen_exchange_keys:
                duplicate_exchange_keys.add(key)
            seen_exchange_keys.add(key)
        for key in exchange_keys:
            if key not in duplicate_exchange_keys:
                continue
            diagnostics.append(
                Diagnostic(
                    f"$.required_functions[{index}].required_exchanges",
                    "duplicate required exchange rule "
                    f"kind={key[0]!r}, {'message' if key[0] == 'oms_message' else 'name'}={key[1]!r}, direction={key[2]!r}, "
                    f"mandate={key[3]!r}, timing_kind={key[4]!r}",
                )
            )
            duplicate_exchange_keys.remove(key)
    return diagnostics


def validate_profile_document(profile: Any) -> list[Diagnostic]:
    return profile_schema_diagnostics(profile) + profile_semantic_diagnostics(profile)


def validate_profile_path(path: Path) -> tuple[Any | None, list[Diagnostic]]:
    try:
        profile = load_document(path)
    except YamlInputError as exc:
        return None, [Diagnostic("", f"could not parse {path}: {exc}")]
    return profile, validate_profile_document(profile)


def validate_document(document: Any) -> list[Diagnostic]:
    return schema_diagnostics(document) + semantic_diagnostics(document)


def required_exchange_identity(requirement: dict[str, Any]) -> tuple[str, str, str, str, str] | None:
    """Return the kind-specific semantic identity for a required exchange rule."""
    kind = requirement.get("kind")
    selector_field = {"oms_message": "message", "data_transfer": "name"}.get(kind)
    if selector_field is None:
        return None
    values = (
        kind,
        requirement.get(selector_field),
        requirement.get("direction"),
        requirement.get("mandate"),
        requirement.get("timing_kind"),
    )
    return values if all(isinstance(value, str) for value in values) else None


def required_exchange_matches(actual: dict[str, Any], requirement: dict[str, Any]) -> bool:
    """Match an actual exchange against a supported kind-specific profile rule."""
    kind = requirement.get("kind")
    selector_field = {"oms_message": "message", "data_transfer": "name"}.get(kind)
    if selector_field is None:
        return False
    return (
        actual.get("kind") == kind
        and actual.get(selector_field) == requirement.get(selector_field)
        and actual.get("direction") == requirement.get("direction")
        and actual.get("mandate") == requirement.get("mandate")
        and actual.get("timing", {}).get("kind") == requirement.get("timing_kind")
    )


def profile_diagnostics(document: Any, profile: Any) -> list[Diagnostic]:
    """Apply a validated OMS profile to a structurally valid contract."""
    if not isinstance(document, dict) or not isinstance(profile, dict):
        return []

    compatibility_diagnostics: list[Diagnostic] = []
    profile_id = profile["id"]
    contract_version = document.get("contract_version")
    if contract_version not in profile["contract_versions"]:
        compatibility_diagnostics.append(
            Diagnostic(
                "$.contract_version",
                f"profile {profile_id!r} does not support contract version {contract_version!r}",
            )
        )

    contract_oms_version = document.get("standards", {}).get("oms_version")
    if contract_oms_version != profile["oms_version"]:
        compatibility_diagnostics.append(
            Diagnostic(
                "$.standards.oms_version",
                f"profile {profile_id!r} requires OMS version {profile['oms_version']!r}, "
                f"contract declares {contract_oms_version!r}",
            )
        )

    if compatibility_diagnostics:
        return compatibility_diagnostics

    diagnostics: list[Diagnostic] = []
    kind = document.get("service", {}).get("kind")
    functions = document.get("functions", [])
    for requirement in profile["required_functions"]:
        if kind not in requirement["applies_to"]:
            continue
        matches = [
            (index, function)
            for index, function in enumerate(functions)
            if function.get("name") == requirement["name"]
        ]
        if not matches:
            diagnostics.append(
                Diagnostic(
                    "$.functions",
                    f"OMS profile {profile_id!r} requires function {requirement['name']!r} for {kind}",
                )
            )
            continue
        if len(matches) > 1:
            diagnostics.append(
                Diagnostic(
                    "$.functions",
                    f"OMS profile {profile_id!r} found multiple matches for required function "
                    f"{requirement['name']!r} for {kind}",
                )
            )
            continue
        index, function = matches[0]
        for field in ("category", "required_group"):
            if function.get(field) != requirement[field]:
                diagnostics.append(
                    Diagnostic(
                        f"$.functions[{index}].{field}",
                        f"OMS profile {profile_id!r} requires {requirement['name']!r} to have "
                        f"{field} {requirement[field]!r} for {kind}",
                    )
                )
        if "applicability" in requirement:
            if function.get("applicability") != requirement["applicability"]:
                diagnostics.append(
                    Diagnostic(
                        f"$.functions[{index}].applicability",
                        f"OMS profile {profile_id!r} requires applicability {requirement['applicability']!r} "
                        f"for {requirement['name']!r} for {kind}",
                    )
                )
        elif function.get("applicability") not in requirement["allowed_applicability"]:
            diagnostics.append(
                Diagnostic(
                    f"$.functions[{index}].applicability",
                    f"OMS profile {profile_id!r} requires {requirement['name']!r} applicability to be one of "
                    f"{requirement['allowed_applicability']!r} for {kind}",
                )
            )
        for exchange_requirement in requirement.get("required_exchanges", []):
            if any(
                required_exchange_matches(exchange, exchange_requirement)
                for exchange in function.get("exchanges", [])
            ):
                continue
            selector = exchange_requirement.get("message", exchange_requirement.get("name", "<unknown>"))
            diagnostics.append(
                Diagnostic(
                    f"$.functions[{index}].exchanges",
                    f"OMS profile {profile_id!r} requires {requirement['name']!r} exchange "
                    f"{selector!r} with direction "
                    f"{exchange_requirement['direction']!r}, mandate "
                    f"{exchange_requirement['mandate']!r}, and timing kind "
                    f"{exchange_requirement['timing_kind']!r} for {kind}",
                )
            )
    return diagnostics


def validate_path(path: Path, profile: Any | None = None) -> list[Diagnostic]:
    try:
        document = load_document(path)
    except YamlInputError as exc:
        return [Diagnostic("", f"could not parse {path}: {exc}")]
    diagnostics = validate_document(document)
    if diagnostics or profile is None:
        return diagnostics
    return profile_diagnostics(document, profile)


def _default_all_paths() -> list[Path]:
    return sorted((ROOT / "examples").glob("*.yaml")) + sorted((ROOT / "tests" / "valid").glob("*.yaml"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="contract YAML/JSON files to validate")
    parser.add_argument(
        "--all",
        action="store_true",
        help="validate all examples and tests/valid fixtures",
    )
    parser.add_argument("--profile", type=Path, help="OMS profile YAML/JSON file to apply after normal validation")
    args = parser.parse_args(argv)

    paths = list(args.paths)
    if args.all:
        paths.extend(_default_all_paths())
    if not paths:
        parser.error("provide one or more paths, or use --all")

    profile: Any | None = None
    if args.profile is not None:
        profile_path = args.profile.resolve()
        profile, diagnostics = validate_profile_path(profile_path)
        if diagnostics:
            print(f"FAIL {profile_path}")
            for diagnostic in diagnostics:
                print(f"  {diagnostic}")
            return 1

    failed = False
    seen: set[Path] = set()
    for path in paths:
        path = path.resolve()
        if path in seen:
            continue
        seen.add(path)
        diagnostics = validate_path(path, profile)
        if diagnostics:
            failed = True
            print(f"FAIL {path}")
            for diag in diagnostics:
                print(f"  {diag}")
        else:
            print(f"OK   {path}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
