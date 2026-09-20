from pathlib import Path
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools/completion.py"
EXAMPLES = ROOT / "examples/completion"
WORKSPACE = EXAMPLES / "rf-fm-demod-workspace.yaml"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CLI), *args], cwd=ROOT, capture_output=True, text=True, check=False)


def test_rf_fm_demod_real_evidence_workspace_fails_closed(tmp_path: Path) -> None:
    workspace = yaml.safe_load(WORKSPACE.read_text())
    assert workspace["input"] == "rf-fm-demod.yaml"
    assert "capabilities" not in workspace and "specific_functions" not in workspace
    evidence = yaml.safe_load((EXAMPLES / workspace["input"]).read_text())
    assert {source["id"] for source in evidence["sources"]} == {"primary-contract", "configuration-doc", "contracts-doc"}
    assert all(source["revision"] == "af13bd2926b15253e795920c91320733a29927ea" for source in evidence["sources"])
    candidates = {candidate["id"]: candidate for candidate in evidence["candidates"]}
    for candidate_id in ("service-name", "oms-version", "uci-version", "position-direction", "status-direction", "status-timing", "signal-direction", "position-topic", "status-topic", "signal-topic", "status-rate", "signal-rate-limit"):
        assert candidate_id in candidates
    assert candidates["position-direction"]["value"] == "input"
    assert candidates["status-timing"]["value"] == "periodic"
    assert candidates["signal-rate-limit"]["target"] == "observation[SignalReport].report_rate_limit_hz"
    assert not any(candidate["target"] == "exchange[SignalReport].timing.max_rate_hz" for candidate in candidates.values())

    worksheet = run("worksheet", str(WORKSPACE))
    assert worksheet.returncode == 0
    assert "Capability inventory" in worksheet.stdout
    assert "published_contract" in worksheet.stdout and "published_supporting_doc" in worksheet.stdout
    scaffold = run("scaffold", str(WORKSPACE))
    assert scaffold.returncode == 0
    assert "functions[Service Initialization].id" in scaffold.stdout
    assert "functions[Service Status].exchanges[ServiceStatus].id" in scaffold.stdout
    assert "SignalReport" not in scaffold.stdout and "PositionReport" not in scaffold.stdout
    check = run("check", str(WORKSPACE))
    assert check.returncode != 0 and check.stdout == ""
    assert "CA_MATERIALIZATION_INCOMPLETE" in check.stderr and "Traceback" not in check.stderr
    materialize = run("materialize", str(WORKSPACE), "--format", "yaml")
    assert materialize.returncode != 0 and materialize.stdout == ""
    output = tmp_path / "rf-fm-demod-contract.yaml"
    failed_output = run("materialize", str(WORKSPACE), "--format", "yaml", "--output", str(output))
    assert failed_output.returncode != 0 and failed_output.stdout == "" and not output.exists()
