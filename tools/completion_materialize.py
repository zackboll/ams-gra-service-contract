#!/usr/bin/env python3
"""Fail-closed materialization of a completion scaffold into contract JSON."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from tools.completion_assistant import load_completion_path, load_decisions_path
    from tools.completion_scaffold import build_scaffold, load_capabilities_path, load_mapping_path, load_specific_functions_path
    from tools.validate import Diagnostic, profile_diagnostics, validate_document, validate_profile_path
except ModuleNotFoundError:  # Support direct execution as ``python tools/completion_materialize.py``.
    from completion_assistant import load_completion_path, load_decisions_path
    from completion_scaffold import build_scaffold, load_capabilities_path, load_mapping_path, load_specific_functions_path
    from validate import Diagnostic, profile_diagnostics, validate_document, validate_profile_path

CA_MATERIALIZATION_INCOMPLETE = "CA_MATERIALIZATION_INCOMPLETE"
CA_UNMAPPED_AUTHOR_DECISION = "CA_UNMAPPED_AUTHOR_DECISION"


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
        functions.append(item)
    contract = {"contract_version": _resolved(scaffold["target"]["contract_version"]), "service": service, "standards": standards, "functions": functions}
    if scaffold["capability_inventory_state"] != "unknown":
        contract["capabilities"] = [{field: _resolved(capability[field]) for field in ("id", "name", "requires_position_information")} for capability in scaffold["capabilities"]]
    return contract, []


def render_json(contract: dict[str, Any]) -> str:
    return json.dumps(contract, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--specific-functions", type=Path)
    parser.add_argument("--capabilities", type=Path)
    parser.add_argument("--profile", type=Path, required=True)
    args = parser.parse_args(argv)
    completion, diagnostics = load_completion_path(args.input.resolve())
    if not diagnostics: decisions, diagnostics = load_decisions_path(args.decisions.resolve(), completion)
    specific = None
    capabilities = None
    if not diagnostics and args.specific_functions: specific, diagnostics = load_specific_functions_path(args.specific_functions.resolve())
    if not diagnostics and args.capabilities: capabilities, diagnostics = load_capabilities_path(args.capabilities.resolve())
    if not diagnostics: profile, diagnostics = validate_profile_path(args.profile.resolve())
    if not diagnostics: mapping, diagnostics = load_mapping_path(args.mapping.resolve(), completion, decisions, profile, specific, capabilities)
    contract = None
    if not diagnostics:
        contract, diagnostics = materialize_contract(build_scaffold(completion, decisions, mapping, profile, specific, capabilities))
    if not diagnostics:
        diagnostics = validate_document(contract)
    if not diagnostics:
        diagnostics = profile_diagnostics(contract, profile)
    if diagnostics:
        for diagnostic in diagnostics:
            print(f"FAIL {diagnostic}", file=sys.stderr)
        return 1
    print(render_json(contract), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
