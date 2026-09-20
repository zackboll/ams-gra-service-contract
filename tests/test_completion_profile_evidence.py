from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys

from tools.completion_assistant import load_completion_path
from tools.completion_profile_evidence import (CA_PROFILE_EVIDENCE_DUPLICATE_FACT, CA_PROFILE_EVIDENCE_DUPLICATE_TARGET, CA_PROFILE_EVIDENCE_NONFIXED, CA_PROFILE_EVIDENCE_UNKNOWN_TARGET, build_profile_evidence_report, load_profile_evidence_path, render_json, render_markdown, validate_profile_evidence)
from tools.validate import validate_profile_path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "examples/completion/rf-fm-demod.yaml"
PROFILE = ROOT / "profiles/oms/2.5/profile.yaml"
EVIDENCE = ROOT / "examples/completion/rf-fm-demod-profile-evidence.yaml"

def data():
    completion, errors = load_completion_path(INPUT); assert not errors
    profile, errors = validate_profile_path(PROFILE); assert not errors
    evidence, errors = load_profile_evidence_path(EVIDENCE); assert not errors
    return completion, profile, evidence

def test_valid_report_alignment_provenance_and_determinism():
    completion, profile, evidence = data()
    assert validate_profile_evidence(evidence, completion, profile) == []
    report = build_profile_evidence_report(evidence, completion, profile)
    assert [x["observed_alignment"] for x in report["comparisons"]] == ["all_aligned"] * 3
    assert report["comparisons"][1]["observed_evidence"][1]["source_title"] == "RF FM Demod External Interface Contracts"
    assert report["comparisons"][0]["profile_traceability"][0]["document_number"] == "OMSC-INS-003"
    assert "exchange[ServiceStatus].topic" in report["unlinked_candidate_targets"]
    assert render_json(report) == render_json(report) and render_markdown(report) == render_markdown(report)

def test_invalid_links_and_nonfixed_function_fact():
    completion, profile, evidence = data()
    evidence["links"].append(deepcopy(evidence["links"][0])); evidence["links"][1]["target"] = "unknown"
    codes = {x.code for x in validate_profile_evidence(evidence, completion, profile)}
    assert {CA_PROFILE_EVIDENCE_DUPLICATE_TARGET, CA_PROFILE_EVIDENCE_DUPLICATE_FACT, CA_PROFILE_EVIDENCE_UNKNOWN_TARGET} <= codes
    bad = {"links": [{"target": "service.name", "profile_fact": {"kind": "required_function_fact", "profile_function": "Subsystem State Command Processing", "field": "applicability"}}]}
    altered = completion | {"target": completion["target"] | {"service_kind": "subsystem"}}
    assert CA_PROFILE_EVIDENCE_NONFIXED in {x.code for x in validate_profile_evidence(bad, altered, profile)}

def test_conflicts_and_decisions_are_report_data():
    completion, profile, evidence = data()
    completion["candidates"].append({"id": "wrong", "target": "exchange[ServiceStatus].direction", "value": "input", "source": "primary-contract", "locator": "x"})
    report = build_profile_evidence_report(evidence, completion, profile, {"decisions": [{"target": "exchange[ServiceStatus].direction", "value": "input"}]})
    assert report["comparisons"][1]["observed_alignment"] == "mixed"
    assert report["comparisons"][1]["author_decision"]["alignment"] == "conflicting"

def test_cli_works_without_mapping_or_decisions(tmp_path):
    (tmp_path / "input.yaml").write_text(INPUT.read_text()); (tmp_path / "profile.yaml").write_text(PROFILE.read_text()); (tmp_path / "evidence.yaml").write_text(EVIDENCE.read_text())
    workspace = tmp_path / "workspace.yaml"; workspace.write_text('workspace_version: "0.1"\ninput: input.yaml\nprofile: profile.yaml\nprofile_evidence: evidence.yaml\n')
    result = subprocess.run([sys.executable, "tools/completion.py", "profile-evidence", str(workspace), "--format", "json"], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0 and json.loads(result.stdout)["component_kind"] == "service"
