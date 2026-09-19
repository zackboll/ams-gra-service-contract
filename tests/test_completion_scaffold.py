from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

from tools.completion_assistant import load_completion_path, load_decisions_path
from tools.completion_scaffold import (
    CA_CONTEXT_ASSERTION_MISMATCH, CA_DUPLICATE_MAPPING_DESTINATION,
    CA_DUPLICATE_MAPPING_TARGET, CA_MAPPING_FIELD_INCOMPATIBLE,
    CA_MAPPING_VALUE_TYPE, CA_UNKNOWN_MAPPING_TARGET, CA_UNKNOWN_PROFILE_EXCHANGE,
    CA_UNKNOWN_PROFILE_FUNCTION, build_scaffold, load_mapping_path,
    render_json, render_markdown, validate_mapping_document,
)
from tools.validate import validate_profile_path
from tools.yaml_support import load_path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "examples/completion/ir-search-and-track.yaml"
DECISIONS = ROOT / "examples/completion/ir-search-and-track-decisions.yaml"
MAPPING = ROOT / "examples/completion/ir-search-and-track-mapping.yaml"
PROFILE = ROOT / "profiles/oms/2.5/profile.yaml"

def _all():
    completion, d = load_completion_path(INPUT); assert not d
    decisions, d = load_decisions_path(DECISIONS, completion); assert not d
    profile, d = validate_profile_path(PROFILE); assert not d
    mapping = load_path(MAPPING)
    return completion, decisions, mapping, profile

def test_valid_mapping_and_profile_derived_scaffold() -> None:
    completion, decisions, mapping, profile = _all()
    assert validate_mapping_document(mapping, completion, decisions, profile) == []
    scaffold = build_scaffold(completion, decisions, mapping, profile)
    status = next(x for x in scaffold["functions"] if x["profile_function"] == "Service Status")
    exchange = next(x for x in status["exchanges"] if x["selector"] == "ServiceStatus")
    assert status["id"]["state"] == "missing" and status["name"]["origin"] == "oms_profile"
    assert exchange["id"]["state"] == "missing" and exchange["kind"]["value"] == "oms_message"
    assert exchange["topic"]["value"] == "mission.service-status"
    assert exchange["topic"]["candidate_id"] == "status-topic"
    assert exchange["nominal_rate_hz"]["value"] == 1
    assert "functions[Service Initialization].exchanges[FileMetadata].topic" in scaffold["unresolved_required_fields"]
    assert {x["target"] for x in scaffold["unmapped_author_decisions"]} >= {"exchange[PositionReport].topic", "exchange[ObservationMeasurementReport].topic"}
    assert render_json(scaffold) == render_json(scaffold) and render_markdown(scaffold) == render_markdown(scaffold)

def test_mapping_diagnostics_are_distinct_and_fail_closed() -> None:
    completion, decisions, mapping, profile = _all()
    cases = [
        (lambda m: m["bindings"].append(deepcopy(m["bindings"][0])), CA_DUPLICATE_MAPPING_TARGET),
        (lambda m: m["bindings"].append({"target":"exchange[PositionReport].topic", "destination":deepcopy(m["bindings"][0]["destination"])}), CA_DUPLICATE_MAPPING_DESTINATION),
        (lambda m: m["bindings"].__setitem__(0, {"target":"typo", "destination":m["bindings"][0]["destination"]}), CA_UNKNOWN_MAPPING_TARGET),
        (lambda m: m["bindings"][5]["destination"].__setitem__("profile_function", "No such function"), CA_UNKNOWN_PROFILE_FUNCTION),
        (lambda m: m["bindings"][5]["destination"].__setitem__("selector", "NoSuchMessage"), CA_UNKNOWN_PROFILE_EXCHANGE),
        (lambda m: m["bindings"][5]["destination"].__setitem__("field", "protocol"), CA_MAPPING_FIELD_INCOMPATIBLE),
        (lambda m: m["bindings"][6]["destination"].__setitem__("field", "nominal_response_seconds"), CA_MAPPING_FIELD_INCOMPATIBLE),
    ]
    for edit, code in cases:
        modified = deepcopy(mapping); edit(modified)
        assert code in {x.code for x in validate_mapping_document(modified, completion, decisions, profile)}

def test_context_types_missing_decisions_and_explicit_values() -> None:
    completion, decisions, mapping, profile = _all()
    decisions = deepcopy(decisions); decisions["decisions"] = [x for x in decisions["decisions"] if x["target"] != "service.name"]
    scaffold = build_scaffold(completion, decisions, mapping, profile)
    assert scaffold["service"]["name"] == {"state": "missing"}
    decisions["decisions"].append({"target":"service.name", "value":"Entered"})
    scaffold = build_scaffold(completion, decisions, mapping, profile)
    assert scaffold["service"]["name"] == {"state":"resolved", "value":"Entered", "origin":"author_decision"}
    bad = deepcopy(decisions); version = next(x for x in bad["decisions"] if x["target"] == "service.version"); version.pop("select_candidate"); version["value"] = True
    assert CA_MAPPING_VALUE_TYPE in {x.code for x in validate_mapping_document(mapping, completion, bad, profile)}
    bad = deepcopy(decisions); kind = next(x for x in bad["decisions"] if x["target"] == "service.kind"); kind.pop("select_candidate"); kind["value"] = "isolator"
    assert CA_CONTEXT_ASSERTION_MISMATCH in {x.code for x in validate_mapping_document(mapping, completion, bad, profile)}

def test_conditional_applicability_not_applicable_deactivates_exchanges() -> None:
    completion, decisions, mapping, profile = _all(); completion = deepcopy(completion); completion["target"]["service_kind"] = "subsystem"
    mapping = {"mapping_version":"0.1", "bindings":[{"target":"subsystem.applicability", "destination":{"kind":"required_function_field", "profile_function":"Subsystem State Command Processing", "field":"applicability"}}, {"target":"subsystem.reason", "destination":{"kind":"required_function_field", "profile_function":"Subsystem State Command Processing", "field":"not_applicable_reason"}}]}
    completion["candidates"] += [{"id":"a", "target":"subsystem.applicability", "value":"not_applicable", "source":"primary-contract", "locator":"x"}, {"id":"r", "target":"subsystem.reason", "value":"not needed", "source":"primary-contract", "locator":"x"}]
    decisions = {"decision_version":"0.1", "decisions":[{"target":"subsystem.applicability", "select_candidate":"a"}, {"target":"subsystem.reason", "select_candidate":"r"}]}
    assert not validate_mapping_document(mapping, completion, decisions, profile)
    function = next(x for x in build_scaffold(completion, decisions, mapping, profile)["functions"] if x["profile_function"] == "Subsystem State Command Processing")
    assert function["applicability"]["value"] == "not_applicable" and not function["exchanges"][0]["active"]
    no_decisions = build_scaffold(completion, {"decision_version":"0.1", "decisions":[]}, mapping, profile)
    assert "functions[Subsystem State Command Processing].applicability" in no_decisions["unresolved_required_fields"]

def test_cli_has_only_scaffold_formats_and_fails() -> None:
    command = [sys.executable, "tools/completion_scaffold.py", "--input", str(INPUT), "--decisions", str(DECISIONS), "--mapping", str(MAPPING), "--profile", str(PROFILE), "--format", "json"]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0 and json.loads(result.stdout)["scaffold_version"] == "0.1"
    assert "output-contract" not in subprocess.run([sys.executable, "tools/completion_scaffold.py", "--help"], cwd=ROOT, capture_output=True, text=True).stdout
