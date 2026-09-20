from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys

from tools.completion_assistant import load_completion_path, load_decisions_path
from tools.completion_materialize import materialize_contract, render_yaml
from tools.completion_scaffold import (CA_DUPLICATE_SOURCE_KEY, CA_DUPLICATE_TRACEABILITY,
    CA_INACTIVE_TRACE_TARGET, CA_SOURCE_REVISION_MISMATCH, CA_UNKNOWN_EVIDENCE_SOURCE, CA_UNKNOWN_TRACE_SOURCE,
    CA_UNKNOWN_TRACE_TARGET, build_scaffold, load_mapping_path, validate_traceability)
from tools.validate import profile_diagnostics, validate_document, validate_profile_path
from tools.yaml_support import load_path, load_text

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "examples/completion/complete-service-with-traceability.yaml"
TRACE = ROOT / "examples/completion/complete-service-traceability.yaml"
PROFILE = ROOT / "profiles/oms/2.5/profile.yaml"
EXPECTED = ROOT / "tests/materialization-complete-service-traceability.expected.json"

def _base():
    completion, diagnostics = load_completion_path(INPUT); assert not diagnostics
    decisions, diagnostics = load_decisions_path(ROOT / "examples/completion/complete-service-decisions.yaml", completion); assert not diagnostics
    profile, diagnostics = validate_profile_path(PROFILE); assert not diagnostics
    mapping, diagnostics = load_mapping_path(ROOT / "examples/completion/complete-service-mapping.yaml", completion, decisions, profile); assert not diagnostics
    return completion, decisions, mapping, profile, load_path(TRACE)

def test_explicit_adoption_and_required_trace_materialize_in_order() -> None:
    completion, decisions, mapping, profile, trace = _base()
    assert validate_traceability(trace, completion) == []
    contract, diagnostics = materialize_contract(build_scaffold(completion, decisions, mapping, profile, traceability=trace))
    assert not diagnostics and validate_document(contract) == [] and profile_diagnostics(contract, profile) == []
    assert json.dumps(contract, indent=2, ensure_ascii=False) + "\n" == EXPECTED.read_text(encoding="utf-8")
    assert [x["id"] for x in contract["sources"]] == ["synthetic-contract-source", "synthetic-config-source"]
    assert contract["sources"][0]["title"] == "Synthetic Service Contract Source"
    assert contract["sources"][0]["uri"] == "https://example.invalid/contracts/synthetic-service"
    assert contract["sources"][0]["revision"] == "A" and "provenance" not in json.dumps(contract)
    assert "Evidence-only note." not in json.dumps(contract)
    status = next(x for x in contract["functions"] if x["id"] == "service-status")
    assert status["traceability"] == [{"source":"synthetic-contract-source", "locator":"Section 4.1"}]
    assert status["exchanges"][0]["traceability"] == [{"source":"synthetic-contract-source", "locator":"Table 4-1"}]
    assert "source_key" not in json.dumps(contract)
    rendered = render_yaml(contract)
    assert load_text(rendered) == contract
    assert all(field not in rendered for field in ("source_key", "provenance", "candidate_id", "origin", "state"))

def test_traceability_semantic_diagnostics_and_revision_rules() -> None:
    completion, _, _, _, trace = _base()
    duplicate = deepcopy(trace); duplicate["sources"].append(deepcopy(duplicate["sources"][0]))
    assert CA_DUPLICATE_SOURCE_KEY in {x.code for x in validate_traceability(duplicate, completion)}
    bad = deepcopy(trace); bad["sources"][0]["from_completion_source"] = "nope"
    assert CA_UNKNOWN_EVIDENCE_SOURCE in {x.code for x in validate_traceability(bad, completion)}
    bad = deepcopy(trace); bad["sources"][0]["revision"] = "B"
    assert CA_SOURCE_REVISION_MISMATCH in {x.code for x in validate_traceability(bad, completion)}
    bad = deepcopy(trace); bad["traces"][0]["source_key"] = "nope"
    assert CA_UNKNOWN_TRACE_SOURCE in {x.code for x in validate_traceability(bad, completion)}
    duplicate = deepcopy(trace); duplicate["traces"].append(deepcopy(duplicate["traces"][0]))
    assert CA_DUPLICATE_TRACEABILITY in {x.code for x in validate_traceability(duplicate, completion)}

def test_unknown_target_is_not_silently_dropped() -> None:
    completion, decisions, mapping, profile, trace = _base()
    trace["traces"] = [{"destination":{"kind":"required_exchange","profile_function":"Service Status","selector":"missing"},"source_key":"primary-contract"}]
    scaffold = build_scaffold(completion, decisions, mapping, profile, traceability=trace)
    assert CA_UNKNOWN_TRACE_TARGET in {x.code for x in scaffold["traceability_diagnostics"]}
    assert materialize_contract(scaffold)[0] is None

def test_capability_function_and_inactive_component_target() -> None:
    completion, diagnostics = load_completion_path(ROOT / "examples/completion/complete-capability-service.yaml"); assert not diagnostics
    completion = deepcopy(completion); completion["sources"] = [{"id":"evidence", "provenance":"published_contract", "title":"Evidence", "uri":"https://example.invalid/evidence"}]
    decisions, diagnostics = load_decisions_path(ROOT / "examples/completion/complete-capability-service-decisions.yaml", completion); assert not diagnostics
    profile, diagnostics = validate_profile_path(PROFILE); assert not diagnostics
    from tools.completion_scaffold import load_capabilities_path
    capabilities, diagnostics = load_capabilities_path(ROOT / "examples/completion/complete-capability-service-capabilities.yaml"); assert not diagnostics
    mapping, diagnostics = load_mapping_path(ROOT / "examples/completion/complete-capability-service-mapping.yaml", completion, decisions, profile, capabilities=capabilities); assert not diagnostics
    trace = {"traceability_version":"0.1", "sources":[{"key":"evidence","id":"portable-evidence","from_completion_source":"evidence"}], "traces":[{"destination":{"kind":"capability_function","capability_key":"esm","role":"capability_status"},"source_key":"evidence"}]}
    contract, diagnostics = materialize_contract(build_scaffold(completion, decisions, mapping, profile, capabilities=capabilities, traceability=trace))
    assert not diagnostics and next(x for x in contract["functions"] if x["id"] == "esm-capability-status")["traceability"] == [{"source":"portable-evidence"}]
    trace["traces"] = [{"destination":{"kind":"component_capability_function","role":"position_information_processing"},"source_key":"evidence"}]
    decisions = deepcopy(decisions)
    next(x for x in decisions["decisions"] if x["target"] == "capability.esm.position")["value"] = False
    scaffold = build_scaffold(completion, decisions, mapping, profile, capabilities=capabilities, traceability=trace)
    assert CA_INACTIVE_TRACE_TARGET in {x.code for x in scaffold["traceability_diagnostics"]}

def test_cli_traceability_is_optional() -> None:
    command = [sys.executable, "tools/completion_materialize.py", "--input", str(INPUT), "--decisions", str(ROOT / "examples/completion/complete-service-decisions.yaml"), "--mapping", str(ROOT / "examples/completion/complete-service-mapping.yaml"), "--traceability", str(TRACE), "--profile", str(PROFILE)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0 and result.stderr == "" and json.loads(result.stdout)["sources"][0]["id"] == "synthetic-contract-source"
    assert {"--write", "--apply", "--in-place"}.isdisjoint(subprocess.run([sys.executable, "tools/completion_materialize.py", "--help"], cwd=ROOT, capture_output=True, text=True).stdout)
