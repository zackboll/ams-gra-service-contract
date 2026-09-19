#!/usr/bin/env python3
"""Render a non-normative profile-derived completion authoring scaffold."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

try:
    from tools.completion_assistant import load_completion_path, load_decisions_path
    from tools.validate import Diagnostic, validate_profile_path
    from tools.yaml_support import YamlInputError, load_path
except ModuleNotFoundError:
    from completion_assistant import load_completion_path, load_decisions_path
    from validate import Diagnostic, validate_profile_path
    from yaml_support import YamlInputError, load_path

ROOT = Path(__file__).resolve().parents[1]
MAPPING_SCHEMA_PATH = ROOT / "schema/tooling/completion/v0.1/completion-mapping.schema.json"
CA_MAPPING_SCHEMA = "CA_MAPPING_SCHEMA"
CA_DUPLICATE_MAPPING_TARGET = "CA_DUPLICATE_MAPPING_TARGET"
CA_DUPLICATE_MAPPING_DESTINATION = "CA_DUPLICATE_MAPPING_DESTINATION"
CA_UNKNOWN_MAPPING_TARGET = "CA_UNKNOWN_MAPPING_TARGET"
CA_UNKNOWN_PROFILE_FUNCTION = "CA_UNKNOWN_PROFILE_FUNCTION"
CA_UNKNOWN_PROFILE_EXCHANGE = "CA_UNKNOWN_PROFILE_EXCHANGE"
CA_MAPPING_FIELD_INCOMPATIBLE = "CA_MAPPING_FIELD_INCOMPATIBLE"
CA_MAPPING_VALUE_TYPE = "CA_MAPPING_VALUE_TYPE"
CA_CONTEXT_ASSERTION_MISMATCH = "CA_CONTEXT_ASSERTION_MISMATCH"

def _path(parts: Any) -> str:
    return "$" + "".join(f"[{p}]" if isinstance(p, int) else f".{p}" for p in parts)

def load_mapping_schema() -> dict[str, Any]:
    return json.loads(MAPPING_SCHEMA_PATH.read_text(encoding="utf-8"))

def _dupes(values: list[str]) -> set[str]:
    return {value for value in values if values.count(value) > 1}

def _selector(exchange: dict[str, Any]) -> str:
    return exchange.get("message", exchange.get("name", ""))

def _decision_values(completion: dict[str, Any], decisions: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not decisions:
        return {}
    candidates = {item["id"]: item for item in completion["candidates"]}
    sources = {item["id"]: item for item in completion["sources"]}
    result = {}
    for decision in decisions["decisions"]:
        if "select_candidate" in decision:
            candidate = candidates[decision["select_candidate"]]
            source = sources[candidate["source"]]
            result[decision["target"]] = {"value": candidate["value"], "origin": "author_decision", "candidate_id": candidate["id"], "source": source["id"], "provenance": source["provenance"]}
        else:
            result[decision["target"]] = {"value": decision["value"], "origin": "author_decision"}
    return result

def _expected_type(destination: dict[str, Any], exchange: dict[str, Any] | None = None) -> type:
    if destination["kind"] == "context_assertion": return str
    if destination["field"] in {"nominal_rate_hz", "max_rate_hz", "nominal_response_seconds", "max_response_seconds"}: return (int, float)
    return str

def validate_mapping_document(mapping: Any, completion: dict[str, Any], decisions: dict[str, Any] | None, profile: dict[str, Any]) -> list[Diagnostic]:
    errors = sorted(Draft202012Validator(load_mapping_schema(), format_checker=FormatChecker()).iter_errors(mapping), key=lambda e: list(e.absolute_path))
    if errors: return [Diagnostic(CA_MAPPING_SCHEMA, _path(error.absolute_path), error.message) for error in errors]
    bindings = mapping["bindings"]
    diagnostics = [Diagnostic(CA_DUPLICATE_MAPPING_TARGET, "$.bindings", f"duplicate mapping target {x!r}") for x in sorted(_dupes([b["target"] for b in bindings]))]
    keys = [json.dumps(b["destination"], sort_keys=True) for b in bindings]
    diagnostics += [Diagnostic(CA_DUPLICATE_MAPPING_DESTINATION, "$.bindings", "duplicate mapping destination") for x in sorted(_dupes(keys))]
    known = {x["target"] for x in completion["candidates"]} | {x["target"] for x in (decisions or {}).get("decisions", [])}
    values = _decision_values(completion, decisions)
    for i, binding in enumerate(bindings):
        target, dest = binding["target"], binding["destination"]
        base = f"$.bindings[{i}].destination"
        if target not in known:
            diagnostics.append(Diagnostic(CA_UNKNOWN_MAPPING_TARGET, f"$.bindings[{i}].target", f"unknown completion target {target!r}")); continue
        function = exchange = None
        if dest["kind"] in {"required_function_field", "required_exchange_field"}:
            matches = [f for f in profile["required_functions"] if f["name"] == dest["profile_function"] and completion["target"]["service_kind"] in f["applies_to"]]
            if len(matches) != 1:
                diagnostics.append(Diagnostic(CA_UNKNOWN_PROFILE_FUNCTION, f"{base}.profile_function", f"profile function {dest['profile_function']!r} is not uniquely applicable")); continue
            function = matches[0]
        if dest["kind"] == "required_function_field":
            if dest["field"] == "applicability" and "allowed_applicability" not in function:
                diagnostics.append(Diagnostic(CA_MAPPING_FIELD_INCOMPATIBLE, f"{base}.field", "fixed profile applicability cannot be overridden"))
            if dest["field"] == "not_applicable_reason" and "allowed_applicability" not in function:
                diagnostics.append(Diagnostic(CA_MAPPING_FIELD_INCOMPATIBLE, f"{base}.field", "not_applicable_reason requires allowed applicability"))
            if dest["field"] == "applicability" and target in values and values[target]["value"] not in function.get("allowed_applicability", []):
                diagnostics.append(Diagnostic(CA_MAPPING_FIELD_INCOMPATIBLE, f"$.bindings[{i}]", "applicability decision is not allowed by the profile"))
            if dest["field"] == "not_applicable_reason":
                applicability_targets = [b["target"] for b in bindings if b["destination"] == {"kind": "required_function_field", "profile_function": function["name"], "field": "applicability"}]
                if len(applicability_targets) != 1 or values.get(applicability_targets[0], {}).get("value") != "not_applicable":
                    diagnostics.append(Diagnostic(CA_MAPPING_FIELD_INCOMPATIBLE, f"$.bindings[{i}]", "not_applicable_reason requires an explicit not_applicable decision"))
        if dest["kind"] == "required_exchange_field":
            matches = [x for x in function.get("required_exchanges", []) if _selector(x) == dest["selector"]]
            if len(matches) != 1:
                diagnostics.append(Diagnostic(CA_UNKNOWN_PROFILE_EXCHANGE, f"{base}.selector", f"profile exchange {dest['selector']!r} is not uniquely present in {function['name']!r}")); continue
            exchange = matches[0]; field = dest["field"]
            oms = {"id", "topic", "operational_attribute", "subscription_group", "appendix_c_mapping", "nominal_rate_hz", "max_rate_hz", "nominal_response_seconds", "max_response_seconds"}
            data = {"id", "protocol", "data_type", "data_format", "sharing_pattern"}
            valid = oms if exchange["kind"] == "oms_message" else data
            timing = exchange["timing_kind"]
            if field not in valid or (field.endswith("rate_hz") and timing != "periodic") or (field.endswith("response_seconds") and timing != "on_demand"):
                diagnostics.append(Diagnostic(CA_MAPPING_FIELD_INCOMPATIBLE, f"{base}.field", f"field {field!r} is incompatible with profile exchange kind/timing"))
        if dest["kind"] == "context_assertion" and target in values:
            context_key = {"service_kind": "service_kind", "oms_version": "oms_version", "contract_version": "contract_version"}[dest["field"]]
            if values[target]["value"] != completion["target"][context_key]: diagnostics.append(Diagnostic(CA_CONTEXT_ASSERTION_MISMATCH, f"$.bindings[{i}]", "author decision disagrees with completion target context"))
        if target in values:
            value = values[target]["value"]; expected = _expected_type(dest, exchange)
            if expected == (int, float): valid_type = isinstance(value, (int, float)) and not isinstance(value, bool)
            else: valid_type = isinstance(value, expected)
            if not valid_type: diagnostics.append(Diagnostic(CA_MAPPING_VALUE_TYPE, f"$.bindings[{i}]", f"decision value has incompatible type for {dest['kind']}.{dest['field']}"))
    return diagnostics

def load_mapping_path(path: Path, completion: dict[str, Any], decisions: dict[str, Any] | None, profile: dict[str, Any]) -> tuple[Any | None, list[Diagnostic]]:
    try: mapping = load_path(path)
    except YamlInputError as exc: return None, [Diagnostic(CA_MAPPING_SCHEMA, "", f"could not parse {path}: {exc}")]
    return mapping, validate_mapping_document(mapping, completion, decisions, profile)

def _missing() -> dict[str, str]: return {"state": "missing"}
def _profile(value: Any) -> dict[str, Any]: return {"state": "resolved", "value": value, "origin": "oms_profile"}
def _context(value: Any) -> dict[str, Any]: return {"state": "resolved", "value": value, "origin": "completion_target"}

def build_scaffold(completion: dict[str, Any], decisions: dict[str, Any] | None, mapping: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    values = _decision_values(completion, decisions); mapped = {x["target"]: x["destination"] for x in mapping["bindings"]}; assigned: dict[str, dict[str, Any]] = {}
    for target, dest in mapped.items():
        if target not in values or dest["kind"] == "context_assertion": continue
        key = json.dumps(dest, sort_keys=True); assigned[key] = {"state": "resolved", **values[target]}
    result = {"scaffold_version": "0.1", "target": {k: _context(v) for k, v in completion["target"].items() if k != "name"}, "service": {}, "standards": {}, "functions": [], "unresolved_required_fields": [], "unmapped_author_decisions": []}
    for kind, fields in (("service_field", result["service"]), ("standards_field", result["standards"])):
        allowed = ("name", "version", "description") if kind == "service_field" else ("uci_schema_version", "ams_gra_version")
        for field in allowed:
            dest = {"kind": kind, "field": field}; fields[field] = assigned.get(json.dumps(dest, sort_keys=True), _missing())
    for function in profile["required_functions"]:
        if completion["target"]["service_kind"] not in function["applies_to"]: continue
        fd = {"kind": "required_function_field", "profile_function": function["name"], "field": "applicability"}
        applicability = _profile(function["applicability"]) if "applicability" in function else assigned.get(json.dumps(fd, sort_keys=True), _missing())
        item = {"profile_function": function["name"], "id": assigned.get(json.dumps({"kind":"required_function_field","profile_function":function["name"],"field":"id"},sort_keys=True), _missing()), "name": _profile(function["name"]), "category": _profile(function["category"]), "required_group": _profile(function["required_group"]), "applicability": applicability, "exchanges": []}
        if applicability.get("value") == "not_applicable": item["not_applicable_reason"] = assigned.get(json.dumps({"kind":"required_function_field","profile_function":function["name"],"field":"not_applicable_reason"},sort_keys=True), _missing())
        active = applicability.get("value") != "not_applicable"
        for exchange in function.get("required_exchanges", []):
            selector = _selector(exchange); ex = {"selector": selector, "kind": _profile(exchange["kind"]), "direction": _profile(exchange["direction"]), "mandate": _profile(exchange["mandate"]), "timing_kind": _profile(exchange["timing_kind"]), "active": active}
            ex["message" if exchange["kind"] == "oms_message" else "name"] = _profile(selector)
            for field in (("id", "topic") if exchange["kind"] == "oms_message" else ("id", "protocol", "data_type", "data_format", "sharing_pattern")):
                dest = {"kind":"required_exchange_field","profile_function":function["name"],"selector":selector,"field":field}; ex[field] = assigned.get(json.dumps(dest,sort_keys=True), _missing())
            for field in ("nominal_rate_hz", "max_rate_hz") if exchange["timing_kind"] == "periodic" else (("nominal_response_seconds", "max_response_seconds") if exchange["timing_kind"] == "on_demand" else ()):
                dest = {"kind":"required_exchange_field","profile_function":function["name"],"selector":selector,"field":field}
                if json.dumps(dest,sort_keys=True) in assigned: ex[field] = assigned[json.dumps(dest,sort_keys=True)]
            item["exchanges"].append(ex)
        result["functions"].append(item)
    def walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            if value == {"state":"missing"}: result["unresolved_required_fields"].append(path)
            else:
                for k,v in value.items():
                    if k not in {"state","value","origin","candidate_id","source","provenance","active"}: walk(v, f"{path}.{k}" if path else k)
        elif isinstance(value, list):
            for x in value:
                identity = x.get("profile_function", x.get("selector", "")) if isinstance(x, dict) else ""
                walk(x, f"{path}[{identity}]")
    for section, fields in (("service", ("name", "version")), ("standards", ("uci_schema_version",))):
        for field in fields:
            if result[section][field]["state"] == "missing": result["unresolved_required_fields"].append(f"{section}.{field}")
    for f in result["functions"]:
        if f["applicability"]["state"] == "missing": result["unresolved_required_fields"].append(f"functions[{f['profile_function']}].applicability")
        if f["applicability"].get("value") != "not_applicable": walk({"id":f["id"], "exchanges":f["exchanges"]}, f"functions[{f['profile_function']}]")
        elif f.get("not_applicable_reason", {}).get("state") == "missing": result["unresolved_required_fields"].append(f"functions[{f['profile_function']}].not_applicable_reason")
    for target, value in values.items():
        if target not in mapped: result["unmapped_author_decisions"].append({"target":target, **value})
    return result

def render_json(scaffold: dict[str, Any]) -> str: return json.dumps(scaffold, indent=2, ensure_ascii=False) + "\n"
def render_markdown(scaffold: dict[str, Any]) -> str:
    lines = ["# Completion authoring scaffold", "", "Non-normative profile-derived preview; not a portable Service Contract.", "", "## Unresolved required fields", ""]
    lines += [f"- `{x}`" for x in scaffold["unresolved_required_fields"]] or ["- None."]
    lines += ["", "## Required functions", ""]
    for f in scaffold["functions"]:
        lines += [f"### {f['profile_function']}", "", f"- id: {f['id']['state']}", f"- applicability: {f['applicability'].get('value', 'missing')}"]
        for e in f["exchanges"]: lines.append(f"- {e['selector']}: {'active' if e['active'] else 'inactive'}")
    lines += ["", "## Unmapped author decisions", ""] + [f"- `{x['target']}`" for x in scaffold["unmapped_author_decisions"]]
    return "\n".join(lines) + "\n"

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--input", type=Path, required=True); parser.add_argument("--decisions", type=Path, required=True); parser.add_argument("--mapping", type=Path, required=True); parser.add_argument("--profile", type=Path, required=True); parser.add_argument("--format", choices=("markdown","json"), required=True); args = parser.parse_args(argv)
    completion, diagnostics = load_completion_path(args.input.resolve())
    if not diagnostics: decisions, diagnostics = load_decisions_path(args.decisions.resolve(), completion)
    if not diagnostics: profile, diagnostics = validate_profile_path(args.profile.resolve())
    if not diagnostics: mapping, diagnostics = load_mapping_path(args.mapping.resolve(), completion, decisions, profile)
    if diagnostics:
        for d in diagnostics: print(f"FAIL {d}", file=sys.stderr)
        return 1
    scaffold = build_scaffold(completion, decisions, mapping, profile); print(render_markdown(scaffold) if args.format == "markdown" else render_json(scaffold), end=""); return 0
if __name__ == "__main__": raise SystemExit(main())
