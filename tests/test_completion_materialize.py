from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

from tools.completion_assistant import load_completion_path, load_decisions_path
from tools.completion_materialize import CA_MATERIALIZATION_INCOMPLETE, CA_UNMAPPED_AUTHOR_DECISION, materialize_contract, render_json
from tools.completion_scaffold import build_scaffold, load_mapping_path
from tools.validate import profile_diagnostics, validate_document, validate_profile_path

ROOT = Path(__file__).resolve().parents[1]
COMPLETE = ROOT / "examples/completion/complete-service.yaml"
COMPLETE_DECISIONS = ROOT / "examples/completion/complete-service-decisions.yaml"
COMPLETE_MAPPING = ROOT / "examples/completion/complete-service-mapping.yaml"
IR = ROOT / "examples/completion/ir-search-and-track.yaml"
IR_DECISIONS = ROOT / "examples/completion/ir-search-and-track-decisions.yaml"
IR_MAPPING = ROOT / "examples/completion/ir-search-and-track-mapping.yaml"
PROFILE = ROOT / "profiles/oms/2.5/profile.yaml"
EXPECTED = ROOT / "conformance/v0.1/valid/materialized-complete-service.json"


def _scaffold(input_path=COMPLETE, decisions_path=COMPLETE_DECISIONS, mapping_path=COMPLETE_MAPPING):
    completion, diagnostics = load_completion_path(input_path); assert not diagnostics
    decisions, diagnostics = load_decisions_path(decisions_path, completion); assert not diagnostics
    profile, diagnostics = validate_profile_path(PROFILE); assert not diagnostics
    mapping, diagnostics = load_mapping_path(mapping_path, completion, decisions, profile); assert not diagnostics
    return build_scaffold(completion, decisions, mapping, profile), profile


def test_complete_materialization_matches_fixture_and_validates() -> None:
    scaffold, profile = _scaffold()
    contract, diagnostics = materialize_contract(scaffold)
    assert diagnostics == []
    assert render_json(contract) == EXPECTED.read_text(encoding="utf-8")
    assert validate_document(contract) == []
    assert profile_diagnostics(contract, profile) == []
    assert "capabilities" not in contract and "sources" not in contract
    encoded = json.dumps(contract)
    assert all(field not in encoded for field in ("scaffold_version", "origin", "candidate_id", "provenance", "state", "unresolved_required_fields"))


def test_materialized_fields_and_timing_are_explicit_only() -> None:
    contract, diagnostics = materialize_contract(_scaffold()[0]); assert not diagnostics
    initialization, status = contract["functions"]
    assert initialization["name"] == "Service Initialization" and initialization["category"] == "required"
    transfer = initialization["exchanges"][2]
    assert {key: transfer[key] for key in ("protocol", "data_type", "data_format", "sharing_pattern")} == {"protocol": "https", "data_type": "ServiceConfigFile", "data_format": "application/json", "sharing_pattern": "request_response"}
    periodic, asynchronous, on_demand = status["exchanges"]
    assert periodic["timing"] == {"kind": "periodic", "nominal_rate_hz": 1.0}
    assert asynchronous["timing"] == {"kind": "asynchronous"}
    assert on_demand["timing"] == {"kind": "on_demand", "nominal_response_seconds": 0.5}
    assert "description" not in contract["service"] and "description" not in status and "not_applicable_reason" not in status


def test_incomplete_and_unmapped_scaffolds_fail_before_contract_construction() -> None:
    scaffold, _ = _scaffold()
    incomplete = deepcopy(scaffold); incomplete["unresolved_required_fields"] = ["functions[Service Status].id"]
    contract, diagnostics = materialize_contract(incomplete)
    assert contract is None and [item.code for item in diagnostics] == [CA_MATERIALIZATION_INCOMPLETE]
    unmapped = deepcopy(scaffold); unmapped["unmapped_author_decisions"] = [{"target": "specific.exchange"}]
    contract, diagnostics = materialize_contract(unmapped)
    assert contract is None and [item.code for item in diagnostics] == [CA_UNMAPPED_AUTHOR_DECISION]


def test_not_applicable_has_reason_and_no_exchanges() -> None:
    scaffold, _ = _scaffold()
    function = scaffold["functions"][1]
    function["applicability"] = {"state": "resolved", "value": "not_applicable", "origin": "author_decision"}
    function["not_applicable_reason"] = {"state": "resolved", "value": "not offered", "origin": "author_decision"}
    contract, diagnostics = materialize_contract(scaffold)
    assert not diagnostics
    assert contract["functions"][1]["not_applicable_reason"] == "not offered"
    assert contract["functions"][1]["exchanges"] == []


def test_cli_json_only_and_ir_search_and_track_fail_closed() -> None:
    command = [sys.executable, "tools/completion_materialize.py", "--input", str(COMPLETE), "--decisions", str(COMPLETE_DECISIONS), "--mapping", str(COMPLETE_MAPPING), "--profile", str(PROFILE)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0 and result.stderr == "" and result.stdout == EXPECTED.read_text(encoding="utf-8")
    assert {"--output", "--write", "--apply", "--in-place"}.isdisjoint(subprocess.run([sys.executable, "tools/completion_materialize.py", "--help"], cwd=ROOT, capture_output=True, text=True).stdout)
    command[command.index(str(COMPLETE))] = str(IR)
    command[command.index(str(COMPLETE_DECISIONS))] = str(IR_DECISIONS)
    command[command.index(str(COMPLETE_MAPPING))] = str(IR_MAPPING)
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode != 0 and result.stdout == "" and CA_MATERIALIZATION_INCOMPLETE in result.stderr
