import json
from pathlib import Path
import subprocess
import sys

import yaml

from tools.validate import profile_diagnostics, validate_document, validate_profile_path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools/completion.py"
EXAMPLES = ROOT / "examples/completion"
ORIGINAL = EXAMPLES / "rf-fm-demod-workspace.yaml"
WORKSPACE = EXAMPLES / "rf-fm-demod-owner-confirmed-workspace.yaml"
EXPECTED = ROOT / "tests/rf-fm-demod-simulated-owner-confirmed.expected.yaml"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CLI), *args], cwd=ROOT, capture_output=True, text=True, check=False)


def scaffold(path: Path) -> dict:
    result = run("scaffold", str(path), "--format", "json")
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def field(document: dict, function_name: str, selector: str, name: str) -> dict:
    function = next(item for item in document["functions"] if item["name"]["value"] == function_name)
    exchange = next(item for item in function["exchanges"] if item.get("selector") == selector or item.get("message", {}).get("value") == selector)
    return exchange[name]


def leaves(value: object) -> list[object]:
    if isinstance(value, dict):
        return [item for child in value.values() for item in leaves(child)]
    if isinstance(value, list):
        return [item for child in value for item in leaves(child)]
    return [value]


def test_simulated_owner_answer_loop_is_complete_and_provenance_preserving(tmp_path: Path) -> None:
    original_workspace = yaml.safe_load(ORIGINAL.read_text())
    confirmed_workspace = yaml.safe_load(WORKSPACE.read_text())
    assert "capabilities" not in original_workspace
    assert confirmed_workspace["input"] == original_workspace["input"] == "rf-fm-demod.yaml"
    assert yaml.safe_load((EXAMPLES / confirmed_workspace["capabilities"]).read_text()) == {"capabilities_version": "0.1", "capabilities": []}

    candidates = yaml.safe_load((EXAMPLES / "rf-fm-demod.yaml").read_text())["candidates"]
    assert len(candidates) == 23
    assert {item["id"] for item in candidates} >= {"signal-energy-trigger", "signal-rate-limit", "position-topic", "signal-topic"}
    assert all("simulated" not in item["id"] for item in candidates)

    original = scaffold(ORIGINAL)
    confirmed = scaffold(WORKSPACE)
    assert len(original["unresolved_required_fields"]) == 16
    assert original["capability_inventory_state"] == "unknown"
    assert confirmed["unresolved_required_fields"] == []
    assert confirmed["unmapped_author_decisions"] == []
    assert confirmed["capability_inventory_state"] == "explicit_empty"
    assert confirmed["capabilities"] == []
    assert not any(item.get("function_origin") in {"capability", "component_capability"} for item in confirmed["functions"])

    position_topic = field(confirmed, "RF FM Demod Processing", "PositionReport", "topic")
    position_mandate = field(confirmed, "RF FM Demod Processing", "PositionReport", "mandate")
    status_mandate = field(confirmed, "Service Status", "ServiceStatus", "mandate")
    assert position_topic == {"state": "resolved", "value": "mission.position-report", "origin": "author_decision", "candidate_id": "position-topic", "source": "configuration-doc", "provenance": "published_supporting_doc"}
    assert position_mandate == {"state": "resolved", "value": "optional", "origin": "author_decision"}
    assert status_mandate["origin"] == "oms_profile"

    original_check = run("check", str(ORIGINAL))
    assert original_check.returncode != 0 and "CA_MATERIALIZATION_INCOMPLETE" in original_check.stderr
    check = run("check", str(WORKSPACE))
    assert check.returncode == 0 and "materializable: yes" in check.stdout

    output = tmp_path / "rf-fm-demod-simulated-contract.yaml"
    materialize = run("materialize", str(WORKSPACE), "--format", "yaml", "--output", str(output))
    assert materialize.returncode == 0, materialize.stderr
    assert output.read_text() == EXPECTED.read_text()
    contract = yaml.safe_load(output.read_text())
    profile, diagnostics = validate_profile_path(ROOT / "profiles/oms/2.5/profile.yaml")
    assert diagnostics == [] and validate_document(contract) == [] and profile_diagnostics(contract, profile) == []

    assert contract["capabilities"] == []
    assert [(item["name"], item["category"]) for item in contract["functions"]] == [("Service Initialization", "required"), ("Service Status", "required"), ("RF FM Demod Processing", "specific")]
    specific = contract["functions"][-1]
    assert specific["id"] == "rf-fm-demod-processing"
    exchanges = {item["message"]: item for item in specific["exchanges"]}
    assert exchanges["PositionReport"] == {"id": "position-report-input", "kind": "oms_message", "direction": "input", "mandate": "optional", "message": "PositionReport", "topic": "mission.position-report", "timing": {"kind": "asynchronous"}}
    assert exchanges["SignalReport"] == {"id": "signal-report-output", "kind": "oms_message", "direction": "output", "mandate": "mandatory", "message": "SignalReport", "topic": "mission.signal-report", "timing": {"kind": "asynchronous"}}
    rendered = output.read_text()
    assert all(token not in rendered for token in ("candidate_id", "provenance", "origin", "state", "function_key", "exchange_key", "capability_key", "workspace_version", "decision_version", "mapping_version", "publication_trigger", "report_rate_limit_hz", "max_rate_hz"))
    assert "fm-demod-processing" not in leaves(contract)

    profile_evidence = run("profile-evidence", str(WORKSPACE))
    assert profile_evidence.returncode == 0
    assert profile_evidence.stdout.count("all_aligned") == 3
