#!/usr/bin/env python3
"""Fail-closed materialization of a completion scaffold into portable contracts."""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    from tools.completion_assistant import load_completion_path, load_decisions_path
    from tools.completion_scaffold import build_scaffold, load_capabilities_path, load_mapping_path, load_specific_functions_path
    from tools.validate import Diagnostic, profile_diagnostics, validate_document, validate_profile_path
    from tools.yaml_support import YamlInputError, dump_text, load_text
except ModuleNotFoundError:  # Support direct execution as ``python tools/completion_materialize.py``.
    from completion_assistant import load_completion_path, load_decisions_path
    from completion_scaffold import build_scaffold, load_capabilities_path, load_mapping_path, load_specific_functions_path
    from validate import Diagnostic, profile_diagnostics, validate_document, validate_profile_path
    from yaml_support import YamlInputError, dump_text, load_text

CA_MATERIALIZATION_INCOMPLETE = "CA_MATERIALIZATION_INCOMPLETE"
CA_UNMAPPED_AUTHOR_DECISION = "CA_UNMAPPED_AUTHOR_DECISION"
CA_SERIALIZATION_ROUNDTRIP = "CA_SERIALIZATION_ROUNDTRIP"
CA_OUTPUT_EXISTS = "CA_OUTPUT_EXISTS"
CA_OUTPUT_PATH = "CA_OUTPUT_PATH"
CA_OUTPUT_WRITE = "CA_OUTPUT_WRITE"


def _resolved(value: dict[str, Any]) -> Any:
    return value["value"]


def _optional(target: dict[str, Any], field: str, result: dict[str, Any]) -> None:
    value = target.get(field)
    if value and value.get("state") == "resolved":
        result[field] = _resolved(value)


def _timing(exchange: dict[str, Any]) -> dict[str, Any]:
    kind = _resolved(exchange["timing_kind"])
    result = {"kind": kind}
    fields = {
        "periodic": ("nominal_rate_hz", "max_rate_hz"),
        "on_demand": ("nominal_response_seconds", "max_response_seconds"),
    }
    for field in fields.get(kind, ()):
        _optional(exchange, field, result)
    return result


def _traceability(target: dict[str, Any], result: dict[str, Any]) -> None:
    if target.get("traceability"):
        result["traceability"] = [{key: item[key] for key in ("source", "locator", "note") if key in item} for item in target["traceability"]]


def _exchange(exchange: dict[str, Any]) -> dict[str, Any]:
    kind = _resolved(exchange["kind"])
    result = {
        "id": _resolved(exchange["id"]),
        "kind": kind,
        "direction": _resolved(exchange["direction"]),
        "mandate": _resolved(exchange["mandate"]),
    }
    if kind == "oms_message":
        result["message"] = _resolved(exchange["message"])
        result["topic"] = _resolved(exchange["topic"])
        for field in ("operational_attribute", "subscription_group", "appendix_c_mapping"):
            _optional(exchange, field, result)
    else:
        result["name"] = _resolved(exchange["name"])
        for field in ("protocol", "data_type", "data_format", "sharing_pattern", "details", "reference"):
            _optional(exchange, field, result)
        if kind == "data_transfer":
            for field in ("protocol", "data_type", "data_format", "sharing_pattern"):
                result[field] = _resolved(exchange[field])
    result["timing"] = _timing(exchange)
    _traceability(exchange, result)
    return result


def materialize_contract(scaffold: dict[str, Any]) -> tuple[dict[str, Any] | None, list[Diagnostic]]:
    """Construct a portable contract only when every scaffold precondition holds."""
    diagnostics: list[Diagnostic] = []
    missing = sorted(scaffold["unresolved_required_fields"])
    if missing:
        diagnostics.append(Diagnostic(CA_MATERIALIZATION_INCOMPLETE, "", "unresolved required fields:\n" + ",\n".join(missing)))
    unmapped = sorted(item["target"] for item in scaffold["unmapped_author_decisions"])
    if unmapped:
        diagnostics.append(Diagnostic(CA_UNMAPPED_AUTHOR_DECISION, "", "unmapped author decisions:\n" + ",\n".join(unmapped)))
    if diagnostics:
        return None, diagnostics
    if scaffold.get("traceability_diagnostics"):
        return None, scaffold["traceability_diagnostics"]

    service = {"name": _resolved(scaffold["service"]["name"]), "version": _resolved(scaffold["service"]["version"]), "kind": _resolved(scaffold["target"]["service_kind"])}
    _optional(scaffold["service"], "description", service)
    standards = {"oms_version": _resolved(scaffold["target"]["oms_version"]), "uci_schema_version": _resolved(scaffold["standards"]["uci_schema_version"])}
    _optional(scaffold["standards"], "ams_gra_version", standards)
    functions = []
    for function in scaffold["functions"]:
        item = {"id": _resolved(function["id"]), "name": _resolved(function["name"]), "category": _resolved(function["category"])}
        if "required_group" in function:
            item["required_group"] = _resolved(function["required_group"])
        _optional(function, "standard_role", item)
        _optional(function, "capability", item)
        item["applicability"] = _resolved(function["applicability"])
        _optional(function, "description", item)
        if item["applicability"] == "not_applicable":
            item["not_applicable_reason"] = _resolved(function["not_applicable_reason"])
            item["exchanges"] = []
        else:
            item["exchanges"] = [_exchange(exchange) for exchange in function["exchanges"] if exchange["active"]]
        _traceability(function, item)
        functions.append(item)
    contract = {"contract_version": _resolved(scaffold["target"]["contract_version"]), "service": service, "standards": standards, "functions": functions}
    if scaffold["capability_inventory_state"] != "unknown":
        contract["capabilities"] = [{field: _resolved(capability[field]) for field in ("id", "name", "requires_position_information")} for capability in scaffold["capabilities"]]
    if scaffold.get("contract_sources"):
        contract["sources"] = [{key: source[key] for key in ("id", "title", "uri", "document_number", "revision", "date", "note") if key in source} for source in scaffold["contract_sources"]]
    return contract, []


def render_json(contract: dict[str, Any]) -> str:
    return json.dumps(contract, indent=2, ensure_ascii=False) + "\n"


def render_yaml(contract: dict[str, Any]) -> str:
    return dump_text(contract)


def _serialization_diagnostics(serialized: str, format_name: str, contract: dict[str, Any], profile: dict[str, Any]) -> list[Diagnostic]:
    try:
        parsed = json.loads(serialized) if format_name == "json" else load_text(serialized)
    except (json.JSONDecodeError, YamlInputError, ValueError, TypeError) as exc:
        return [Diagnostic(CA_SERIALIZATION_ROUNDTRIP, "", f"could not parse rendered {format_name}: {exc}")]
    if parsed != contract:
        return [Diagnostic(CA_SERIALIZATION_ROUNDTRIP, "", f"rendered {format_name} does not round-trip to the materialized contract")]
    diagnostics = validate_document(parsed)
    return diagnostics if diagnostics else profile_diagnostics(parsed, profile)


def _output_path_diagnostic(path: Path, force: bool) -> Diagnostic | None:
    parent = path.parent
    if not parent.exists() or not parent.is_dir():
        return Diagnostic(CA_OUTPUT_PATH, str(path), "parent directory must already exist")
    if path.is_symlink():
        return Diagnostic(CA_OUTPUT_PATH, str(path), "destination must not be a symlink")
    if path.exists() and path.is_dir():
        return Diagnostic(CA_OUTPUT_PATH, str(path), "destination must not be a directory")
    if path.exists() and not path.is_file():
        return Diagnostic(CA_OUTPUT_PATH, str(path), "destination must be a regular file")
    if path.exists() and not force:
        return Diagnostic(CA_OUTPUT_EXISTS, str(path), "destination already exists; use --force to replace a regular file")
    return None


def _write_output(path: Path, serialized: str, force: bool) -> Diagnostic | None:
    path_error = _output_path_diagnostic(path, force)
    if path_error:
        return path_error
    replace_existing = path.exists()
    try:
        if not replace_existing:
            created = False
            try:
                with path.open("x", encoding="utf-8", newline="\n") as stream:
                    created = True
                    stream.write(serialized)
            except Exception:
                if created and path.exists() and not path.is_symlink():
                    path.unlink()
                raise
            return None
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(serialized)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise
        return None
    except OSError as exc:
        return Diagnostic(CA_OUTPUT_WRITE, str(path), str(exc))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--specific-functions", type=Path)
    parser.add_argument("--capabilities", type=Path)
    parser.add_argument("--traceability", type=Path)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--format", choices=("json", "yaml"), default="json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.force and args.output is None:
        parser.error("--force requires --output")
    completion, diagnostics = load_completion_path(args.input.resolve())
    if not diagnostics: decisions, diagnostics = load_decisions_path(args.decisions.resolve(), completion)
    specific = None
    capabilities = None
    traceability = None
    if not diagnostics and args.specific_functions: specific, diagnostics = load_specific_functions_path(args.specific_functions.resolve())
    if not diagnostics and args.capabilities: capabilities, diagnostics = load_capabilities_path(args.capabilities.resolve())
    if not diagnostics and args.traceability:
        try:
            from tools.completion_scaffold import load_traceability_path
        except ModuleNotFoundError:
            from completion_scaffold import load_traceability_path
        traceability, diagnostics = load_traceability_path(args.traceability.resolve(), completion)
    if not diagnostics: profile, diagnostics = validate_profile_path(args.profile.resolve())
    if not diagnostics: mapping, diagnostics = load_mapping_path(args.mapping.resolve(), completion, decisions, profile, specific, capabilities)
    contract = None
    if not diagnostics:
        contract, diagnostics = materialize_contract(build_scaffold(completion, decisions, mapping, profile, specific, capabilities, traceability))
    if not diagnostics:
        diagnostics = validate_document(contract)
    if not diagnostics:
        diagnostics = profile_diagnostics(contract, profile)
    serialized = ""
    if not diagnostics:
        try:
            serialized = render_json(contract) if args.format == "json" else render_yaml(contract)
        except (TypeError, ValueError, YamlInputError) as exc:
            diagnostics = [Diagnostic(CA_SERIALIZATION_ROUNDTRIP, "", f"could not render {args.format}: {exc}")]
    if not diagnostics:
        diagnostics = _serialization_diagnostics(serialized, args.format, contract, profile)
    if not diagnostics and args.output:
        output_diagnostic = _write_output(args.output, serialized, args.force)
        if output_diagnostic:
            diagnostics = [output_diagnostic]
    if diagnostics:
        for diagnostic in diagnostics:
            print(f"FAIL {diagnostic}", file=sys.stderr)
        return 1
    if args.output is None:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
