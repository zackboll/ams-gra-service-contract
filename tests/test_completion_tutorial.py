from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TUTORIAL = ROOT / "docs/tutorials/completion-assistant-walkthrough.md"
IR_INPUT = ROOT / "examples/completion/ir-search-and-track.yaml"
IR_DECISIONS = ROOT / "examples/completion/ir-search-and-track-decisions.yaml"
IR_MAPPING = ROOT / "examples/completion/ir-search-and-track-mapping.yaml"
IR_SPECIFIC = ROOT / "examples/completion/ir-search-and-track-specific-functions.yaml"
COMPLETE = ROOT / "examples/completion/complete-service.yaml"
COMPLETE_DECISIONS = ROOT / "examples/completion/complete-service-decisions.yaml"
COMPLETE_MAPPING = ROOT / "examples/completion/complete-service-mapping.yaml"
PROFILE = ROOT / "profiles/oms/2.5/profile.yaml"


def test_completion_walkthrough_paths_and_commands(tmp_path: Path) -> None:
    for path in (TUTORIAL, IR_INPUT, IR_DECISIONS, IR_MAPPING, IR_SPECIFIC, COMPLETE, COMPLETE_DECISIONS, COMPLETE_MAPPING, PROFILE):
        assert path.is_file()
    worksheet = subprocess.run([sys.executable, "tools/completion_assistant.py", "--input", str(IR_INPUT), "--profile", str(PROFILE), "--format", "markdown"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert worksheet.returncode == 0 and "## Candidate evidence" in worksheet.stdout
    scaffold = subprocess.run([sys.executable, "tools/completion_scaffold.py", "--input", str(IR_INPUT), "--decisions", str(IR_DECISIONS), "--mapping", str(IR_MAPPING), "--specific-functions", str(IR_SPECIFIC), "--profile", str(PROFILE), "--format", "markdown"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert scaffold.returncode == 0 and "functions[Service Status].id" in scaffold.stdout
    output = tmp_path / "contract.yaml"
    materialize = subprocess.run([sys.executable, "tools/completion_materialize.py", "--input", str(COMPLETE), "--decisions", str(COMPLETE_DECISIONS), "--mapping", str(COMPLETE_MAPPING), "--profile", str(PROFILE), "--format", "yaml", "--output", str(output)], cwd=ROOT, capture_output=True, text=True, check=False)
    assert materialize.returncode == 0 and materialize.stdout == materialize.stderr == ""
    validate = subprocess.run([sys.executable, "tools/validate.py", "--profile", str(PROFILE), str(output)], cwd=ROOT, capture_output=True, text=True, check=False)
    assert validate.returncode == 0 and "OK" in validate.stdout
