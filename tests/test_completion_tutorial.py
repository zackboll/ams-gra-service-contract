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
    workspace = ROOT / "examples/completion/ir-search-and-track-workspace.yaml"
    complete_workspace = ROOT / "examples/completion/complete-service-workspace.yaml"
    worksheet = subprocess.run([sys.executable, "tools/completion.py", "worksheet", str(workspace), "--format", "markdown"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert worksheet.returncode == 0 and "## Candidate evidence" in worksheet.stdout
    scaffold = subprocess.run([sys.executable, "tools/completion.py", "scaffold", str(workspace), "--format", "markdown"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert scaffold.returncode == 0 and "functions[Service Status].id" in scaffold.stdout
    output = tmp_path / "contract.yaml"
    assert subprocess.run([sys.executable, "tools/completion.py", "check", str(workspace)], cwd=ROOT, capture_output=True, text=True, check=False).returncode != 0
    assert subprocess.run([sys.executable, "tools/completion.py", "check", str(complete_workspace)], cwd=ROOT, capture_output=True, text=True, check=False).returncode == 0
    materialize = subprocess.run([sys.executable, "tools/completion.py", "materialize", str(complete_workspace), "--format", "yaml", "--output", str(output)], cwd=ROOT, capture_output=True, text=True, check=False)
    assert materialize.returncode == 0 and materialize.stdout == materialize.stderr == ""
    validate = subprocess.run([sys.executable, "tools/validate.py", "--profile", str(PROFILE), str(output)], cwd=ROOT, capture_output=True, text=True, check=False)
    assert validate.returncode == 0 and "OK" in validate.stdout
