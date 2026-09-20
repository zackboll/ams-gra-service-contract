"""Compare observed completion candidates with explicitly linked fixed OMS facts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator

try:
    from tools.validate import Diagnostic
    from tools.yaml_support import YamlInputError, load_path
except ModuleNotFoundError:
    from validate import Diagnostic
    from yaml_support import YamlInputError, load_path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema/tooling/completion/v0.1/completion-profile-evidence.schema.json"
CA_PROFILE_EVIDENCE_SCHEMA = "CA_PROFILE_EVIDENCE_SCHEMA"
CA_PROFILE_EVIDENCE_DUPLICATE_TARGET = "CA_PROFILE_EVIDENCE_DUPLICATE_TARGET"
CA_PROFILE_EVIDENCE_DUPLICATE_FACT = "CA_PROFILE_EVIDENCE_DUPLICATE_FACT"
CA_PROFILE_EVIDENCE_UNKNOWN_TARGET = "CA_PROFILE_EVIDENCE_UNKNOWN_TARGET"
CA_PROFILE_EVIDENCE_UNKNOWN_FUNCTION = "CA_PROFILE_EVIDENCE_UNKNOWN_FUNCTION"
CA_PROFILE_EVIDENCE_UNKNOWN_EXCHANGE = "CA_PROFILE_EVIDENCE_UNKNOWN_EXCHANGE"
CA_PROFILE_EVIDENCE_FIELD = "CA_PROFILE_EVIDENCE_FIELD"
CA_PROFILE_EVIDENCE_NONFIXED = "CA_PROFILE_EVIDENCE_NONFIXED"

FUNCTION_FIELDS = {"name", "category", "required_group", "applicability"}
EXCHANGE_FIELDS = {"kind", "selector", "direction", "mandate", "timing_kind"}

def _path(parts: Iterable[Any]) -> str:
    return "$" + "".join(f"[{x}]" if isinstance(x, int) else f".{x}" for x in parts)

def load_profile_evidence_path(path: Path) -> tuple[dict[str, Any] | None, list[Diagnostic]]:
    try: document = load_path(path)
    except YamlInputError as exc: return None, [Diagnostic(CA_PROFILE_EVIDENCE_SCHEMA, "", f"could not parse {path}: {exc}")]
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(document), key=lambda error: list(error.absolute_path))
    return (None, [Diagnostic(CA_PROFILE_EVIDENCE_SCHEMA, _path(error.absolute_path), error.message) for error in errors]) if errors else (document, [])

def _source(profile: dict[str, Any], traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sources = {item["id"]: item for item in profile["sources"]}
    return [{"document_number": sources.get(t["source"], {}).get("document_number", t["source"]), "locator": t["locator"]} for t in traces]

def validate_profile_evidence(evidence: dict[str, Any], completion: dict[str, Any], profile: dict[str, Any]) -> list[Diagnostic]:
    targets = {c["target"] for c in completion["candidates"]}; kind = completion["target"]["service_kind"]
    diagnostics: list[Diagnostic] = []; seen_targets: set[str] = set(); seen_facts: set[tuple[Any, ...]] = set()
    for i, link in enumerate(evidence["links"]):
        target, fact = link["target"], link["profile_fact"]; at = f"$.links[{i}]"
        if target in seen_targets: diagnostics.append(Diagnostic(CA_PROFILE_EVIDENCE_DUPLICATE_TARGET, at + ".target", f"duplicate target link {target!r}"))
        seen_targets.add(target)
        key = (fact["kind"], fact["profile_function"], fact.get("selector"), fact["field"])
        if key in seen_facts: diagnostics.append(Diagnostic(CA_PROFILE_EVIDENCE_DUPLICATE_FACT, at + ".profile_fact", "duplicate profile-fact link"))
        seen_facts.add(key)
        if target not in targets: diagnostics.append(Diagnostic(CA_PROFILE_EVIDENCE_UNKNOWN_TARGET, at + ".target", f"unknown completion candidate target {target!r}"))
        functions = [f for f in profile["required_functions"] if f["name"] == fact["profile_function"] and kind in f["applies_to"]]
        if len(functions) != 1: diagnostics.append(Diagnostic(CA_PROFILE_EVIDENCE_UNKNOWN_FUNCTION, at + ".profile_fact.profile_function", f"no uniquely applicable required function {fact['profile_function']!r}")); continue
        function = functions[0]
        if fact["kind"] == "required_function_fact":
            field = fact["field"]
            if field not in FUNCTION_FIELDS: diagnostics.append(Diagnostic(CA_PROFILE_EVIDENCE_FIELD, at + ".profile_fact.field", f"unsupported required-function field {field!r}"))
            elif field not in function: diagnostics.append(Diagnostic(CA_PROFILE_EVIDENCE_NONFIXED, at + ".profile_fact.field", f"profile fact {field!r} is not one fixed scalar value"))
        else:
            field = fact["field"]
            exchanges = [e for e in function.get("required_exchanges", []) if e.get("message", e.get("name")) == fact["selector"]]
            if len(exchanges) != 1: diagnostics.append(Diagnostic(CA_PROFILE_EVIDENCE_UNKNOWN_EXCHANGE, at + ".profile_fact.selector", f"no uniquely resolved required exchange {fact['selector']!r}")); continue
            if field not in EXCHANGE_FIELDS: diagnostics.append(Diagnostic(CA_PROFILE_EVIDENCE_FIELD, at + ".profile_fact.field", f"unsupported required-exchange field {field!r}"))
    return diagnostics

def _expected(profile: dict[str, Any], kind: str, fact: dict[str, Any]) -> tuple[Any, list[dict[str, Any]]]:
    function = next(f for f in profile["required_functions"] if f["name"] == fact["profile_function"] and kind in f["applies_to"])
    if fact["kind"] == "required_function_fact": return function[fact["field"]], _source(profile, function.get("traceability", []))
    exchange = next(e for e in function["required_exchanges"] if e.get("message", e.get("name")) == fact["selector"])
    return (exchange.get("message", exchange.get("name")) if fact["field"] == "selector" else exchange[fact["field"]]), _source(profile, exchange.get("traceability", []))

def build_profile_evidence_report(evidence: dict[str, Any], completion: dict[str, Any], profile: dict[str, Any], decisions: dict[str, Any] | None = None) -> dict[str, Any]:
    kind = completion["target"]["service_kind"]; sources = {s["id"]: s for s in completion["sources"]}; candidates = completion["candidates"]
    decision_by_target = {d["target"]: d for d in (decisions or {"decisions": []})["decisions"]}; by_id = {c["id"]: c for c in candidates}; comparisons = []
    for link in evidence["links"]:
        expected, traceability = _expected(profile, kind, link["profile_fact"]); observed = []
        for c in candidates:
            if c["target"] == link["target"]:
                source = sources[c["source"]]; observed.append({**c, "source_title": source["title"], "provenance": source["provenance"], "alignment": "aligned" if c["value"] == expected else "conflicting"})
        states = {item["alignment"] for item in observed}; alignment = "all_aligned" if states == {"aligned"} else "all_conflicting" if states == {"conflicting"} else "mixed"
        decision = decision_by_target.get(link["target"])
        if not decision: decision_result = {"alignment": "no_decision"}
        else:
            value = by_id[decision["select_candidate"]]["value"] if "select_candidate" in decision else decision["value"]
            decision_result = {"alignment": "aligned" if value == expected else "conflicting", "value": value}
            if "select_candidate" in decision: decision_result["selected_candidate"] = decision["select_candidate"]
        comparisons.append({"target": link["target"], "profile_fact": link["profile_fact"], "profile_expected": expected, "profile_traceability": traceability, "observed_evidence": observed, "observed_alignment": alignment, "author_decision": decision_result})
    linked = {x["target"] for x in comparisons}
    linked_facts = {(x["profile_fact"]["kind"], x["profile_fact"]["profile_function"], x["profile_fact"].get("selector"), x["profile_fact"]["field"]) for x in comparisons}
    uncompared = []
    for function in profile["required_functions"]:
        if kind not in function["applies_to"]: continue
        for field in FUNCTION_FIELDS:
            if field in function and ("required_function_fact", function["name"], None, field) not in linked_facts:
                uncompared.append({"kind": "required_function_fact", "profile_function": function["name"], "field": field, "profile_expected": function[field]})
        for exchange in function.get("required_exchanges", []):
            selector = exchange.get("message", exchange.get("name"))
            for field in EXCHANGE_FIELDS:
                key = ("required_exchange_fact", function["name"], selector, field)
                if key not in linked_facts:
                    uncompared.append({"kind": "required_exchange_fact", "profile_function": function["name"], "selector": selector, "field": field, "profile_expected": selector if field == "selector" else exchange[field]})
    return {"profile_id": profile["id"], "component_kind": kind, "comparisons": comparisons, "unlinked_candidate_targets": sorted({c["target"] for c in candidates} - linked), "uncompared_profile_facts": uncompared}

def render_json(report: dict[str, Any]) -> str: return json.dumps(report, indent=2, sort_keys=True) + "\n"
def render_markdown(report: dict[str, Any]) -> str:
    out = ["# OMS Profile Evidence Comparison", "", "Published service evidence is compared with OMS normative profile evidence. This is observed alignment, not profile conformance.", ""]
    for x in report["comparisons"]:
        f = x["profile_fact"]; out += [f"## {f['profile_function']} / {f.get('selector', '')} / {f['field']}", "", "Profile expected:", f"  {x['profile_expected']}", "", "Profile source:"]
        out += [f"  {t['document_number']}\n  {t['locator']}" for t in x["profile_traceability"]]
        out += ["", "Observed evidence:", ""]
        for c in x["observed_evidence"]: out += [f"  {c['alignment']}\n  {c['value']}\n  {c['id']}\n  {c['source']} ({c['provenance']})\n  {c['locator']}", ""]
        d = x["author_decision"]; out += [f"Observed alignment:\n  {x['observed_alignment']}", "", f"Author decision:\n  {d['alignment']}" + (f" ({d['value']})" if 'value' in d else ""), ""]
    out += ["## Unlinked candidate targets", ""] + [f"- {x}" for x in report["unlinked_candidate_targets"]]
    return "\n".join(out) + "\n"
