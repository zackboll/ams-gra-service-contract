#!/usr/bin/env python3
"""Render a non-normative, provenance-preserving completion worksheet."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

try:
    from tools.validate import Diagnostic, validate_profile_path
    from tools.yaml_support import YamlInputError, load_path
except ModuleNotFoundError:  # Support direct execution as ``python tools/completion_assistant.py``.
    from validate import Diagnostic, validate_profile_path
    from yaml_support import YamlInputError, load_path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "tooling" / "completion" / "v0.1" / "completion-input.schema.json"
DECISIONS_SCHEMA_PATH = ROOT / "schema" / "tooling" / "completion" / "v0.1" / "completion-decisions.schema.json"

CA_SCHEMA = "CA_SCHEMA"
CA_DUPLICATE_SOURCE = "CA_DUPLICATE_SOURCE"
CA_DUPLICATE_CANDIDATE = "CA_DUPLICATE_CANDIDATE"
CA_UNKNOWN_SOURCE = "CA_UNKNOWN_SOURCE"
CA_UNSUPPORTED_CONTRACT_VERSION = "CA_UNSUPPORTED_CONTRACT_VERSION"
CA_OMS_VERSION_MISMATCH = "CA_OMS_VERSION_MISMATCH"
CA_DECISION_SCHEMA = "CA_DECISION_SCHEMA"
CA_DUPLICATE_DECISION_TARGET = "CA_DUPLICATE_DECISION_TARGET"
CA_UNKNOWN_CANDIDATE = "CA_UNKNOWN_CANDIDATE"
CA_DECISION_TARGET_MISMATCH = "CA_DECISION_TARGET_MISMATCH"

COMPLETION_ASSISTANT_DIAGNOSTIC_CODES = frozenset({
    CA_SCHEMA, CA_DUPLICATE_SOURCE, CA_DUPLICATE_CANDIDATE, CA_UNKNOWN_SOURCE,
    CA_UNSUPPORTED_CONTRACT_VERSION, CA_OMS_VERSION_MISMATCH,
    CA_DECISION_SCHEMA, CA_DUPLICATE_DECISION_TARGET, CA_UNKNOWN_CANDIDATE,
    CA_DECISION_TARGET_MISMATCH,
})


def _format_json_path(parts: Iterable[Any]) -> str:
    path = "$"
    for part in parts:
        path += f"[{part}]" if isinstance(part, int) else f".{part}"
    return path


def load_completion_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_decisions_schema() -> dict[str, Any]:
    return json.loads(DECISIONS_SCHEMA_PATH.read_text(encoding="utf-8"))


def completion_schema_diagnostics(document: Any) -> list[Diagnostic]:
    validator = Draft202012Validator(load_completion_schema(), format_checker=FormatChecker())
    return [Diagnostic(CA_SCHEMA, _format_json_path(error.absolute_path), error.message)
            for error in sorted(validator.iter_errors(document), key=lambda error: list(error.absolute_path))]


def decisions_schema_diagnostics(document: Any) -> list[Diagnostic]:
    validator = Draft202012Validator(load_decisions_schema(), format_checker=FormatChecker())
    return [Diagnostic(CA_DECISION_SCHEMA, _format_json_path(error.absolute_path), error.message)
            for error in sorted(validator.iter_errors(document), key=lambda error: list(error.absolute_path))]


def _duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def completion_semantic_diagnostics(document: Any) -> list[Diagnostic]:
    if not isinstance(document, dict):
        return []
    sources = document.get("sources", [])
    candidates = document.get("candidates", [])
    source_ids = [source["id"] for source in sources if isinstance(source, dict) and isinstance(source.get("id"), str)] if isinstance(sources, list) else []
    candidate_ids = [candidate["id"] for candidate in candidates if isinstance(candidate, dict) and isinstance(candidate.get("id"), str)] if isinstance(candidates, list) else []
    diagnostics = [Diagnostic(CA_DUPLICATE_SOURCE, "$.sources", f"duplicate source id {value!r}") for value in sorted(_duplicates(source_ids))]
    diagnostics.extend(Diagnostic(CA_DUPLICATE_CANDIDATE, "$.candidates", f"duplicate candidate id {value!r}") for value in sorted(_duplicates(candidate_ids)))
    source_set = set(source_ids)
    if isinstance(candidates, list):
        for index, candidate in enumerate(candidates):
            if isinstance(candidate, dict) and isinstance(candidate.get("source"), str) and candidate["source"] not in source_set:
                diagnostics.append(Diagnostic(CA_UNKNOWN_SOURCE, f"$.candidates[{index}].source", f"unknown source id {candidate['source']!r}"))
    return diagnostics


def validate_completion_document(document: Any) -> list[Diagnostic]:
    diagnostics = completion_schema_diagnostics(document)
    return diagnostics if diagnostics else completion_semantic_diagnostics(document)


def load_completion_path(path: Path) -> tuple[Any | None, list[Diagnostic]]:
    try:
        document = load_path(path)
    except YamlInputError as exc:
        return None, [Diagnostic(CA_SCHEMA, "", f"could not parse {path}: {exc}")]
    return document, validate_completion_document(document)


def validate_decisions_document(document: Any, completion_document: dict[str, Any]) -> list[Diagnostic]:
    diagnostics = decisions_schema_diagnostics(document)
    if diagnostics:
        return diagnostics
    decisions = document["decisions"]
    targets = [decision["target"] for decision in decisions]
    diagnostics = [Diagnostic(CA_DUPLICATE_DECISION_TARGET, "$.decisions", f"duplicate decision target {target!r}")
                   for target in sorted(_duplicates(targets))]
    candidates = {candidate["id"]: candidate for candidate in completion_document["candidates"]}
    for index, decision in enumerate(decisions):
        candidate_id = decision.get("select_candidate")
        if candidate_id is None:
            continue
        candidate = candidates.get(candidate_id)
        if candidate is None:
            diagnostics.append(Diagnostic(CA_UNKNOWN_CANDIDATE, f"$.decisions[{index}].select_candidate", f"unknown candidate id {candidate_id!r}"))
        elif candidate["target"] != decision["target"]:
            diagnostics.append(Diagnostic(CA_DECISION_TARGET_MISMATCH, f"$.decisions[{index}].target", f"decision target {decision['target']!r} does not match candidate {candidate_id!r} target {candidate['target']!r}"))
    return diagnostics


def load_decisions_path(path: Path, completion_document: dict[str, Any]) -> tuple[Any | None, list[Diagnostic]]:
    try:
        document = load_path(path)
    except YamlInputError as exc:
        return None, [Diagnostic(CA_DECISION_SCHEMA, "", f"could not parse {path}: {exc}")]
    return document, validate_decisions_document(document, completion_document)


def _value_sort_key(value: Any) -> tuple[str, str]:
    return type(value).__name__, json.dumps(value, ensure_ascii=False, sort_keys=True)


def _candidate_sort_key(candidate: dict[str, Any]) -> tuple[str, tuple[str, str], str]:
    return candidate["target"], _value_sort_key(candidate["value"]), candidate["id"]


def _requirements(profile: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    requirements: list[dict[str, Any]] = []
    for function in profile["required_functions"]:
        if kind not in function["applies_to"]:
            continue
        item = {key: function[key] for key in ("name", "category", "required_group", "traceability")}
        item["component_kind"] = kind
        if "applicability" in function:
            item["applicability"] = function["applicability"]
        else:
            item["allowed_applicability"] = function["allowed_applicability"]
        exchanges = []
        for exchange in function.get("required_exchanges", []):
            rendered = {key: exchange[key] for key in ("kind", "direction", "mandate", "timing_kind", "traceability")}
            rendered["selector"] = exchange.get("message", exchange.get("name"))
            exchanges.append(rendered)
        if exchanges:
            item["required_exchanges"] = exchanges
        requirements.append(item)
    return requirements


def build_worksheet(document: dict[str, Any], profile: dict[str, Any], decisions_document: dict[str, Any] | None = None) -> dict[str, Any]:
    target = document["target"]
    candidates = sorted(document["candidates"], key=_candidate_sort_key)
    sources = {source["id"]: source for source in document["sources"]}
    evidence = [{**candidate, "provenance": sources[candidate["source"]]["provenance"], "source_title": sources[candidate["source"]]["title"]} for candidate in candidates]
    by_target: dict[str, list[dict[str, Any]]] = {}
    for candidate in evidence:
        by_target.setdefault(candidate["target"], []).append(candidate)
    evidence_by_id = {candidate["id"]: candidate for candidate in evidence}
    author_decisions: list[dict[str, Any]] = []
    for decision in (decisions_document or {"decisions": []})["decisions"]:
        if "select_candidate" in decision:
            candidate = evidence_by_id[decision["select_candidate"]]
            rendered = {"target": decision["target"], "decision_kind": "candidate", "value": candidate["value"],
                        "candidate_id": candidate["id"], "source": candidate["source"], "provenance": candidate["provenance"]}
        else:
            rendered = {"target": decision["target"], "decision_kind": "explicit_value", "value": decision["value"]}
        if "note" in decision:
            rendered["note"] = decision["note"]
        author_decisions.append(rendered)
    author_decisions.sort(key=lambda decision: decision["target"])
    decided_targets = {decision["target"] for decision in author_decisions}
    conflicts = [{"target": name, "candidates": items, "decision": "Explicit author decision required; no candidate is selected."}
                 for name, items in sorted(by_target.items()) if len({_value_sort_key(item["value"]) for item in items}) > 1]
    decisions = [conflict["decision"] + f" Target: {conflict['target']}." for conflict in conflicts if conflict["target"] not in decided_targets]
    if target["service_kind"] in {"service", "subsystem"}:
        decisions.append("Confirm Capability inventory: Capability facts not supplied / unknown; explicitly zero Capabilities; or one or more Capabilities.")
    return {"completion_version": document["completion_version"], "target": target, "candidates": evidence,
            "conflicts": conflicts, "author_decisions": author_decisions,
            "resolved_targets": sorted(decided_targets), "profile_requirements": _requirements(profile, target["service_kind"]),
            "open_decisions": decisions}


def worksheet_diagnostics(document: dict[str, Any], profile: dict[str, Any]) -> list[Diagnostic]:
    target = document["target"]
    diagnostics: list[Diagnostic] = []
    if target["contract_version"] not in profile["contract_versions"]:
        diagnostics.append(Diagnostic(CA_UNSUPPORTED_CONTRACT_VERSION, "$.target.contract_version", f"profile {profile['id']!r} does not support contract version {target['contract_version']!r}"))
    if target["oms_version"] != profile["oms_version"]:
        diagnostics.append(Diagnostic(CA_OMS_VERSION_MISMATCH, "$.target.oms_version", f"profile {profile['id']!r} requires OMS version {profile['oms_version']!r}, got {target['oms_version']!r}"))
    return diagnostics


def _cell(value: Any) -> str:
    return "" if value is None else str(value).replace("\n", " ").replace("|", "\\|")


def render_json(worksheet: dict[str, Any]) -> str:
    return json.dumps(worksheet, indent=2, ensure_ascii=False) + "\n"


def render_markdown(worksheet: dict[str, Any]) -> str:
    target = worksheet["target"]
    lines = ["# Service Contract Completion Worksheet", "", "## Target", "",
             "| Field | Value |", "| --- | --- |"]
    for key in ("contract_version", "oms_version", "service_kind", "name"):
        if key in target:
            lines.append(f"| {_cell(key)} | {_cell(target[key])} |")
    lines.extend(["", "## Candidate evidence", "", "| Target | Candidate value | Provenance | Source | Locator | Note |", "| --- | --- | --- | --- | --- | --- |"])
    for candidate in worksheet["candidates"]:
        lines.append("| " + " | ".join(_cell(candidate.get(key)) for key in ("target", "value", "provenance", "source_title", "locator", "note")) + " |")
    lines.extend(["", "## Candidate conflicts", ""])
    if worksheet["conflicts"]:
        for conflict in worksheet["conflicts"]:
            values = ", ".join(_cell(candidate["value"]) for candidate in conflict["candidates"])
            suffix = "An explicit author decision is recorded." if conflict["target"] in worksheet["resolved_targets"] else "Explicit author decision required; no candidate is selected."
            lines.append(f"- **{_cell(conflict['target'])}**: conflicting candidate values {values}. {suffix}")
    else:
        lines.append("- No distinct candidate values conflict. Candidates remain unconfirmed and unselected.")
    lines.extend(["", "## Author decisions", ""])
    if worksheet["author_decisions"]:
        lines.extend(["| Target | Decision type | Value | Selected candidate | Provenance | Source | Note |", "| --- | --- | --- | --- | --- | --- | --- |"])
        for decision in worksheet["author_decisions"]:
            lines.append("| " + " | ".join(_cell(decision.get(key)) for key in ("target", "decision_kind", "value", "candidate_id", "provenance", "source", "note")) + " |")
    else:
        lines.append("- No explicit author decisions recorded.")
    lines.extend(["", "## OMS profile requirements", ""])
    for requirement in worksheet["profile_requirements"]:
        applicability = requirement["applicability"] if "applicability" in requirement else ", ".join(requirement["allowed_applicability"])
        lines.append(f"- **{_cell(requirement['name'])}** — component kind: {_cell(requirement['component_kind'])}; category: {_cell(requirement['category'])}; required group: {_cell(requirement['required_group'])}; applicability: {_cell(applicability)}; traceability: " + "; ".join(f"{item['source']} {_cell(item['locator'])}" for item in requirement["traceability"]))
        for exchange in requirement.get("required_exchanges", []):
            lines.append(f"  - Exchange: kind {_cell(exchange['kind'])}; selector {_cell(exchange['selector'])}; direction {_cell(exchange['direction'])}; mandate {_cell(exchange['mandate'])}; timing kind {_cell(exchange['timing_kind'])}; traceability: " + "; ".join(f"{item['source']} {_cell(item['locator'])}" for item in exchange["traceability"]))
    lines.extend(["", "## Remaining open decisions", ""])
    lines.extend(f"- {_cell(decision)}" for decision in worksheet["open_decisions"]) or lines.append("- Review all candidate evidence before authoring contract semantics.")
    lines.extend(["", "## Safety boundary", "", "Candidate values are not Service Contract semantics until explicitly reviewed and authored into a valid contract. This worksheet is non-normative evidence tooling: it does not validate OMS compliance, select candidates, infer missing semantics, or generate/edit a contract."])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--decisions", type=Path)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--format", choices=("markdown", "json"), required=True)
    args = parser.parse_args(argv)
    document, diagnostics = load_completion_path(args.input.resolve())
    decisions_document = None
    if not diagnostics and args.decisions:
        decisions_document, diagnostics = load_decisions_path(args.decisions.resolve(), document)
    if not diagnostics:
        profile, diagnostics = validate_profile_path(args.profile.resolve())
        if not diagnostics:
            diagnostics = worksheet_diagnostics(document, profile)
    if diagnostics:
        for diagnostic in diagnostics:
            print(f"FAIL {diagnostic}", file=sys.stderr)
        return 1
    worksheet = build_worksheet(document, profile, decisions_document)
    print(render_markdown(worksheet) if args.format == "markdown" else render_json(worksheet), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
