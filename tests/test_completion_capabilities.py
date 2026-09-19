from copy import deepcopy
import json
from pathlib import Path

from tools.completion_assistant import load_completion_path, load_decisions_path
from tools.completion_materialize import materialize_contract, render_json
from tools.completion_scaffold import (CA_DUPLICATE_CAPABILITY_KEY,
    CA_INACTIVE_CAPABILITY_FUNCTION, CA_MAPPING_VALUE_TYPE,
    CA_UNKNOWN_CAPABILITY_KEY, CA_UNKNOWN_CAPABILITY_ROLE, build_scaffold,
    load_capabilities_path, load_mapping_path, validate_capabilities,
    validate_mapping_document)
from tools.validate import profile_diagnostics, validate_document, validate_profile_path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "examples/completion/complete-capability-service.yaml"
DECISIONS = ROOT / "examples/completion/complete-capability-service-decisions.yaml"
MAPPING = ROOT / "examples/completion/complete-capability-service-mapping.yaml"
CAPABILITIES = ROOT / "examples/completion/complete-capability-service-capabilities.yaml"
PROFILE = ROOT / "profiles/oms/2.5/profile.yaml"
EXPECTED = ROOT / "tests/materialization-complete-capability-service.expected.json"

def _all():
    completion, diagnostics = load_completion_path(INPUT); assert not diagnostics
    decisions, diagnostics = load_decisions_path(DECISIONS, completion); assert not diagnostics
    capabilities, diagnostics = load_capabilities_path(CAPABILITIES); assert not diagnostics
    profile, diagnostics = validate_profile_path(PROFILE); assert not diagnostics
    mapping, diagnostics = load_mapping_path(MAPPING, completion, decisions, profile, None, capabilities); assert not diagnostics
    return completion, decisions, mapping, profile, capabilities

def test_two_capability_fixture_is_explicit_and_profile_valid() -> None:
    completion, decisions, mapping, profile, capabilities = _all()
    scaffold = build_scaffold(completion, decisions, mapping, profile, capabilities=capabilities)
    assert scaffold["capability_inventory_state"] == "declared"
    assert [x["capability_key"] for x in scaffold["capabilities"]] == ["esm", "radar"]
    assert [x["function_origin"] for x in scaffold["functions"][-7:]] == ["capability"] * 6 + ["component_capability"]
    contract, diagnostics = materialize_contract(scaffold)
    assert not diagnostics and render_json(contract) == EXPECTED.read_text()
    assert validate_document(contract) == [] and profile_diagnostics(contract, profile) == []
    assert len(contract["capabilities"]) == 2
    position = next(x for x in contract["functions"] if x.get("standard_role") == "position_information_processing")
    assert "capability" not in position and position["exchanges"] == []

def test_omitted_empty_and_position_conditions_are_distinct() -> None:
    completion, decisions, mapping, profile, capabilities = _all()
    omitted = build_scaffold(completion, decisions, mapping, profile)
    assert omitted["capability_inventory_state"] == "unknown" and "capabilities" not in omitted
    empty = {"capabilities_version":"0.1", "capabilities":[]}
    ordinary_decisions = deepcopy(decisions); ordinary_decisions["decisions"] = [x for x in ordinary_decisions["decisions"] if not (x["target"].startswith("capability.") or x["target"].startswith("esm.") or x["target"].startswith("radar.") or x["target"].startswith("position."))]
    ordinary_mapping = deepcopy(mapping); ordinary_mapping["bindings"] = [x for x in ordinary_mapping["bindings"] if not x["destination"]["kind"].endswith("capability_field") and x["destination"]["kind"] != "capability_field"]
    scaffold = build_scaffold(completion, ordinary_decisions, ordinary_mapping, profile, capabilities=empty)
    contract, diagnostics = materialize_contract(scaffold)
    assert not diagnostics and contract["capabilities"] == [] and not any(x.get("standard_role") for x in contract["functions"])
    all_false = deepcopy(decisions)
    for x in all_false["decisions"]:
        if x["target"].endswith(".position"): x["value"] = False
    scaffold = build_scaffold(completion, all_false, mapping, profile, capabilities=capabilities)
    assert not any(x.get("standard_role") == "position_information_processing" for x in scaffold["functions"])

def test_capability_diagnostics_and_no_key_inference() -> None:
    completion, decisions, mapping, profile, capabilities = _all()
    duplicate = deepcopy(capabilities); duplicate["capabilities"].append({"key":"esm"})
    assert CA_DUPLICATE_CAPABILITY_KEY in {x.code for x in validate_capabilities(duplicate)}
    bad = deepcopy(mapping); bad["bindings"][-1]["destination"]["role"] = "capability_status"
    assert CA_UNKNOWN_CAPABILITY_ROLE in {x.code for x in validate_mapping_document(bad, completion, decisions, profile, capabilities=capabilities)}
    bad = deepcopy(mapping); next(x for x in bad["bindings"] if x["destination"].get("kind") == "capability_field")["destination"]["capability_key"] = "missing"
    assert CA_UNKNOWN_CAPABILITY_KEY in {x.code for x in validate_mapping_document(bad, completion, decisions, profile, capabilities=capabilities)}
    bad_decisions = deepcopy(decisions); next(x for x in bad_decisions["decisions"] if x["target"] == "capability.esm.position")["value"] = "true"
    assert CA_MAPPING_VALUE_TYPE in {x.code for x in validate_mapping_document(mapping, completion, bad_decisions, profile, capabilities=capabilities)}
    inactive = deepcopy(mapping)
    all_false = deepcopy(decisions)
    for x in all_false["decisions"]:
        if x["target"].endswith(".position"): x["value"] = False
    assert CA_INACTIVE_CAPABILITY_FUNCTION in {x.code for x in validate_mapping_document(inactive, completion, all_false, profile, capabilities=capabilities)}

def test_isolator_retains_explicit_facts_without_section_33_functions() -> None:
    completion, decisions, mapping, profile, capabilities = _all()
    completion = deepcopy(completion); completion["target"]["service_kind"] = "isolator"
    decisions = deepcopy(decisions); decisions["decisions"] = [x for x in decisions["decisions"] if not (x["target"].startswith(("esm.", "radar.", "position.")))]
    mapping = deepcopy(mapping); mapping["bindings"] = [x for x in mapping["bindings"] if "capability_function" not in x["destination"]["kind"]]
    assert validate_mapping_document(mapping, completion, decisions, profile, capabilities=capabilities) == []
    scaffold = build_scaffold(completion, decisions, mapping, profile, capabilities=capabilities)
    assert not any(x["function_origin"] in {"capability", "component_capability"} for x in scaffold["functions"])
