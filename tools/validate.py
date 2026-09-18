#!/usr/bin/env python3
"""Validate v0.1 AMS GRA machine-readable service contracts.

This validator intentionally performs only:
  1. JSON Schema structural validation; and
  2. local cross-field semantic validation.

It does not load or resolve UCI XSDs. UCI resolution belongs to a
contract-aware resolver/code-generator in v0.1.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "v0.1" / "service-contract.schema.json"


@dataclass(frozen=True)
class Diagnostic:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}" if self.path else self.message


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_document(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return yaml.safe_load(stream)


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


def validate_document(document: Any) -> list[Diagnostic]:
    return schema_diagnostics(document) + semantic_diagnostics(document)


def validate_path(path: Path) -> list[Diagnostic]:
    try:
        document = load_document(path)
    except (OSError, yaml.YAMLError) as exc:
        return [Diagnostic("", f"could not parse {path}: {exc}")]
    return validate_document(document)


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
    args = parser.parse_args(argv)

    paths = list(args.paths)
    if args.all:
        paths.extend(_default_all_paths())
    if not paths:
        parser.error("provide one or more paths, or use --all")

    failed = False
    seen: set[Path] = set()
    for path in paths:
        path = path.resolve()
        if path in seen:
            continue
        seen.add(path)
        diagnostics = validate_path(path)
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
