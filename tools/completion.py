#!/usr/bin/env python3
"""Completion workspace tools: worksheet, scaffold, check, and materialize."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from tools.completion_assistant import build_worksheet, load_completion_path, load_decisions_path, render_json as render_worksheet_json, render_markdown, worksheet_diagnostics
    from tools.completion_materialize import _serialization_diagnostics, _write_output, materialize_contract, render_json, render_yaml
    from tools.completion_scaffold import build_scaffold, load_capabilities_path, load_mapping_path, load_specific_functions_path, load_traceability_path, render_json as render_scaffold_json, render_markdown as render_scaffold_markdown
    from tools.completion_workspace import resolve_workspace
    from tools.validate import Diagnostic, profile_diagnostics, validate_document, validate_profile_path
    from tools.yaml_support import YamlInputError
except ModuleNotFoundError:
    from completion_assistant import build_worksheet, load_completion_path, load_decisions_path, render_json as render_worksheet_json, render_markdown, worksheet_diagnostics
    from completion_materialize import _serialization_diagnostics, _write_output, materialize_contract, render_json, render_yaml
    from completion_scaffold import build_scaffold, load_capabilities_path, load_mapping_path, load_specific_functions_path, load_traceability_path, render_json as render_scaffold_json, render_markdown as render_scaffold_markdown
    from completion_workspace import resolve_workspace
    from validate import Diagnostic, profile_diagnostics, validate_document, validate_profile_path
    from yaml_support import YamlInputError


def _prepare(stage: str, workspace_path: Path):
    paths, diagnostics = resolve_workspace(stage, workspace_path.resolve())
    if diagnostics:
        return None, diagnostics
    completion, diagnostics = load_completion_path(paths["input"])
    decisions = specific = capabilities = traceability = mapping = profile = None
    if not diagnostics and "decisions" in paths:
        decisions, diagnostics = load_decisions_path(paths["decisions"], completion)
    if not diagnostics and "specific_functions" in paths:
        specific, diagnostics = load_specific_functions_path(paths["specific_functions"])
    if not diagnostics and "capabilities" in paths:
        capabilities, diagnostics = load_capabilities_path(paths["capabilities"])
    if not diagnostics:
        profile, diagnostics = validate_profile_path(paths["profile"])
    if not diagnostics and "mapping" in paths:
        mapping, diagnostics = load_mapping_path(paths["mapping"], completion, decisions, profile, specific, capabilities)
    if not diagnostics and "traceability" in paths:
        traceability, diagnostics = load_traceability_path(paths["traceability"], completion)
    if diagnostics:
        return None, diagnostics
    return (completion, decisions, specific, capabilities, profile, mapping, traceability), []


def _print_failures(diagnostics: list[Diagnostic]) -> int:
    for diagnostic in diagnostics:
        print(f"FAIL {diagnostic}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Completion workspace tools", epilog="worksheet: review evidence; scaffold: inspect missing fields; check: verify readiness; materialize: emit a validated portable Service Contract.")
    subparsers = parser.add_subparsers(dest="command", required=True, title="commands")
    for name, help_text in (("worksheet", "review evidence and author decisions"), ("scaffold", "inspect resolved and missing contract fields")):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("workspace", type=Path)
        command.add_argument("--format", choices=("markdown", "json"), default="markdown")
    check = subparsers.add_parser("check", help="verify workspace is ready to materialize")
    check.add_argument("workspace", type=Path)
    materialize = subparsers.add_parser("materialize", help="emit a validated portable Service Contract")
    materialize.add_argument("workspace", type=Path)
    materialize.add_argument("--format", choices=("json", "yaml"), required=True)
    materialize.add_argument("--output", type=Path)
    materialize.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "materialize" and args.force and args.output is None:
        parser.error("--force requires --output")
    prepared, diagnostics = _prepare(args.command, args.workspace)
    if diagnostics:
        return _print_failures(diagnostics)
    completion, decisions, specific, capabilities, profile, mapping, traceability = prepared
    if args.command == "worksheet":
        diagnostics = worksheet_diagnostics(completion, profile)
        if diagnostics:
            return _print_failures(diagnostics)
        worksheet = build_worksheet(completion, profile, decisions)
        print(render_markdown(worksheet) if args.format == "markdown" else render_worksheet_json(worksheet), end="")
        return 0
    scaffold = build_scaffold(completion, decisions, mapping, profile, specific, capabilities, traceability)
    if args.command == "scaffold":
        print(render_scaffold_markdown(scaffold) if args.format == "markdown" else render_scaffold_json(scaffold), end="")
        return 0
    contract, diagnostics = materialize_contract(scaffold)
    if not diagnostics:
        diagnostics = validate_document(contract)
    if not diagnostics:
        diagnostics = profile_diagnostics(contract, profile)
    if diagnostics:
        return _print_failures(diagnostics)
    if args.command == "check":
        print("OK completion workspace\n  materializable: yes\n  portable contract: valid\n  OMS profile: valid")
        return 0
    try:
        serialized = render_json(contract) if args.format == "json" else render_yaml(contract)
    except (TypeError, ValueError, YamlInputError) as exc:
        return _print_failures([Diagnostic("CA_SERIALIZATION_ROUNDTRIP", "", f"could not render {args.format}: {exc}")])
    diagnostics = _serialization_diagnostics(serialized, args.format, contract, profile)
    if not diagnostics and args.output:
        output_diagnostic = _write_output(args.output, serialized, args.force)
        diagnostics = [output_diagnostic] if output_diagnostic else []
    if diagnostics:
        return _print_failures(diagnostics)
    if args.output is None:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
