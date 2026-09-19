from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys

from tools.completion_assistant import (
    CA_DUPLICATE_CANDIDATE,
    CA_DUPLICATE_DECISION_TARGET,
    CA_DECISION_SCHEMA,
    CA_DECISION_TARGET_MISMATCH,
    CA_DUPLICATE_SOURCE,
    CA_OMS_VERSION_MISMATCH,
    CA_SCHEMA,
    CA_UNKNOWN_SOURCE,
    CA_UNKNOWN_CANDIDATE,
    CA_UNSUPPORTED_CONTRACT_VERSION,
    build_worksheet,
    load_completion_path,
    load_decisions_path,
    render_json,
    render_markdown,
    worksheet_diagnostics,
)
from tools.validate import validate_profile_path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "completion" / "ir-search-and-track.yaml"
DECISIONS = ROOT / "examples" / "completion" / "ir-search-and-track-decisions.yaml"
PROFILE = ROOT / "profiles" / "oms" / "2.5" / "profile.yaml"


def _document() -> dict:
    document, diagnostics = load_completion_path(EXAMPLE)
    assert diagnostics == []
    return document


def _profile() -> dict:
    profile, diagnostics = validate_profile_path(PROFILE)
    assert diagnostics == []
    return profile


def _decisions(document: dict | None = None) -> dict:
    decisions, diagnostics = load_decisions_path(DECISIONS, document or _document())
    assert diagnostics == []
    return decisions


def test_valid_completion_input_and_ir_example_does_not_invent_function_metadata() -> None:
    document = _document()
    assert {candidate["target"] for candidate in document["candidates"]} >= {"service.name", "exchange[ServiceStatus].timing.kind"}
    forbidden = {"LoM", "function.category", "function.required_group", "function.applicability", "capabilities"}
    assert not any(candidate["target"] in forbidden for candidate in document["candidates"])


def test_ir_search_and_track_provenance_uses_pinned_repository_and_published_field_names() -> None:
    document = _document()
    assert all("open-arsenal/ams-gra-hello-world-sk-skills-ir-search-and-track" in source["uri"] for source in document["sources"])
    locators = {candidate["id"]: candidate["locator"] for candidate in document["candidates"]}
    assert {locators[key] for key in ("position-topic", "observation-topic", "status-topic", "status-rate")} == {"position_topic", "observation_topic", "service_status_topic", "status_report_rate_hz"}


def test_malformed_completion_input_is_schema_error() -> None:
    document = _document()
    del document["target"]["service_kind"]
    from tools.completion_assistant import validate_completion_document
    assert validate_completion_document(document)[0].code == CA_SCHEMA


def test_duplicate_source_candidate_and_unknown_source_diagnostics() -> None:
    from tools.completion_assistant import validate_completion_document
    document = _document()
    document["sources"].append(deepcopy(document["sources"][0]))
    document["candidates"].append(deepcopy(document["candidates"][0]))
    document["candidates"][1]["source"] = "missing"
    assert [item.code for item in validate_completion_document(document)] == [CA_DUPLICATE_SOURCE, CA_DUPLICATE_CANDIDATE, CA_UNKNOWN_SOURCE]


def test_candidate_order_retention_conflicts_and_no_auto_selection() -> None:
    document = _document()
    document["candidates"].extend([
        {"id": "same-value-other-source", "target": "service.name", "value": "IR Search and Track", "source": "configuration-doc", "locator": "name"},
        {"id": "conflicting-name", "target": "service.name", "value": "IR S&T", "source": "configuration-doc", "locator": "short_name"},
    ])
    worksheet = build_worksheet(document, _profile())
    names = [candidate for candidate in worksheet["candidates"] if candidate["target"] == "service.name"]
    assert [candidate["id"] for candidate in names] == ["conflicting-name", "same-value-other-source", "service-name"]
    assert worksheet["conflicts"][0]["target"] == "service.name"
    assert "selected" not in worksheet["conflicts"][0]
    assert len(worksheet["conflicts"][0]["candidates"]) == 3


def test_valid_partial_decisions_preserve_selected_provenance_and_do_not_affect_profile_requirements() -> None:
    document = _document()
    worksheet = build_worksheet(document, _profile(), _decisions(document))
    decision = next(item for item in worksheet["author_decisions"] if item["candidate_id"] == "status-topic")
    assert decision == {"target": "exchange[ServiceStatus].topic", "decision_kind": "candidate", "value": "mission.service-status", "candidate_id": "status-topic", "source": "configuration-doc", "provenance": "published_supporting_doc"}
    assert "function.category" not in worksheet["resolved_targets"]
    assert worksheet["profile_requirements"] == build_worksheet(document, _profile())["profile_requirements"]


def test_decision_schema_duplicate_unknown_and_target_mismatch_diagnostics() -> None:
    from tools.completion_assistant import validate_decisions_document
    document = _document()
    malformed = {"decision_version": "0.1", "decisions": [{"target": "service.name", "value": None}]}
    assert validate_decisions_document(malformed, document)[0].code == CA_DECISION_SCHEMA
    duplicate = {"decision_version": "0.1", "decisions": [{"target": "service.name", "select_candidate": "service-name"}, {"target": "service.name", "select_candidate": "service-name"}]}
    assert validate_decisions_document(duplicate, document)[0].code == CA_DUPLICATE_DECISION_TARGET
    unknown = {"decision_version": "0.1", "decisions": [{"target": "service.name", "select_candidate": "missing"}]}
    assert validate_decisions_document(unknown, document)[0].code == CA_UNKNOWN_CANDIDATE
    mismatch = {"decision_version": "0.1", "decisions": [{"target": "service.name", "select_candidate": "status-topic"}]}
    assert validate_decisions_document(mismatch, document)[0].code == CA_DECISION_TARGET_MISMATCH


def test_conflict_decision_retains_all_evidence_and_removes_only_open_conflict() -> None:
    document = _document()
    document["candidates"].append({"id": "conflicting-name", "target": "service.name", "value": "IR S&T", "source": "configuration-doc", "locator": "short_name"})
    decisions = {"decision_version": "0.1", "decisions": [{"target": "service.name", "select_candidate": "conflicting-name"}]}
    worksheet = build_worksheet(document, _profile(), decisions)
    assert [item["id"] for item in worksheet["conflicts"][0]["candidates"]] == ["conflicting-name", "service-name"]
    assert not any("Target: service.name." in item for item in worksheet["open_decisions"])
    assert "explicit author decision is recorded" in render_markdown(worksheet).lower()


def test_same_value_candidates_and_explicit_values_remain_distinct() -> None:
    document = _document()
    document["candidates"].append({"id": "same-name", "target": "service.name", "value": "IR Search and Track", "source": "configuration-doc", "locator": "name"})
    decisions = {"decision_version": "0.1", "decisions": [{"target": "service.name", "value": "IR Search and Track", "note": "Deployment author confirmed this value."}]}
    worksheet = build_worksheet(document, _profile(), decisions)
    assert [item["id"] for item in worksheet["candidates"] if item["target"] == "service.name"] == ["same-name", "service-name"]
    assert worksheet["author_decisions"] == [{"target": "service.name", "decision_kind": "explicit_value", "value": "IR Search and Track", "note": "Deployment author confirmed this value."}]
    assert "source" not in worksheet["author_decisions"][0]


def test_author_decisions_are_deterministic_and_capability_remains_open() -> None:
    document = _document()
    decisions = {"decision_version": "0.1", "decisions": [{"target": "service.version", "select_candidate": "service-version"}, {"target": "service.name", "select_candidate": "service-name"}]}
    worksheet = build_worksheet(document, _profile(), decisions)
    assert [item["target"] for item in worksheet["author_decisions"]] == ["service.name", "service.version"]
    assert render_json(worksheet) == render_json(worksheet)
    assert render_markdown(worksheet) == render_markdown(worksheet)
    assert any("Capability inventory" in item for item in worksheet["open_decisions"])


def test_profile_requirements_and_capability_boundary_by_explicit_target_kind() -> None:
    profile = _profile()
    for kind, expected in (("service", "Service Status"), ("isolator", "Service Initialization"), ("subsystem", "Subsystem Status")):
        document = _document()
        document["target"]["service_kind"] = kind
        worksheet = build_worksheet(document, profile)
        assert expected in {item["name"] for item in worksheet["profile_requirements"]}
        if kind == "isolator":
            assert not any("Capability inventory" in decision for decision in worksheet["open_decisions"])
        else:
            assert any("Capability inventory" in decision for decision in worksheet["open_decisions"])
    document = _document()
    document["target"]["service_kind"] = "isolator"
    document["candidates"].append({"id": "capability-like-name", "target": "exchange[PositionReport].selector", "value": "PositionReport", "source": "primary-contract", "locator": "x"})
    assert not any(item["required_group"] == "capability" for item in build_worksheet(document, profile)["profile_requirements"])


def test_profile_version_mismatches_are_deterministic() -> None:
    document = _document()
    document["target"]["oms_version"] = "2.6"
    assert worksheet_diagnostics(document, _profile())[0].code == CA_OMS_VERSION_MISMATCH
    document["target"]["contract_version"] = "0.2"
    assert [item.code for item in worksheet_diagnostics(document, _profile())] == [CA_UNSUPPORTED_CONTRACT_VERSION, CA_OMS_VERSION_MISMATCH]


def test_markdown_and_json_rendering_are_deterministic() -> None:
    worksheet = build_worksheet(_document(), _profile())
    assert render_markdown(worksheet) == render_markdown(worksheet)
    assert render_json(worksheet) == render_json(worksheet)
    assert "Candidate values are not Service Contract semantics" in render_markdown(worksheet)
    assert json.loads(render_json(worksheet))["completion_version"] == "0.1"


def test_cli_outputs_only_requested_format_and_fails_with_ca_diagnostic(tmp_path: Path) -> None:
    command = [sys.executable, "tools/completion_assistant.py", "--input", str(EXAMPLE), "--profile", str(PROFILE), "--format", "json"]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert json.loads(result.stdout)["target"]["name"] == "IR Search and Track"
    invalid = _document()
    invalid["candidates"][0]["source"] = "missing"
    path = tmp_path / "invalid.yaml"
    path.write_text(json.dumps(invalid), encoding="utf-8")
    result = subprocess.run([*command[:3], str(path), *command[4:]], cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 1
    assert result.stdout == ""
    assert "FAIL CA_UNKNOWN_SOURCE" in result.stderr


def test_cli_decisions_and_backward_compatible_omission() -> None:
    command = [sys.executable, "tools/completion_assistant.py", "--input", str(EXAMPLE), "--profile", str(PROFILE), "--format", "json"]
    without_decisions = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    with_decisions = subprocess.run([sys.executable, "tools/completion_assistant.py", "--input", str(EXAMPLE), "--decisions", str(DECISIONS), "--profile", str(PROFILE), "--format", "json"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert without_decisions.returncode == with_decisions.returncode == 0
    assert json.loads(without_decisions.stdout)["author_decisions"] == []
    assert json.loads(with_decisions.stdout)["author_decisions"]
