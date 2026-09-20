from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools/completion.py"
EXAMPLES = ROOT / "examples/completion"
PROFILE = ROOT / "profiles/oms/2.5/profile.yaml"


def run(*args: str, cwd: Path = ROOT):
    return subprocess.run([sys.executable, str(CLI), *args], cwd=cwd, capture_output=True, text=True, check=False)


def test_workspace_schema_paths_and_stage_requirements(tmp_path: Path) -> None:
    minimal = tmp_path / "minimal.yaml"
    minimal.write_text('workspace_version: "0.1"\ninput: input.yaml\nprofile: profile.yaml\n')
    (tmp_path / "input.yaml").write_text((EXAMPLES / "complete-service.yaml").read_text())
    (tmp_path / "profile.yaml").write_text(PROFILE.read_text())
    assert run("worksheet", str(minimal)).returncode == 0
    assert "CA_WORKSPACE_STAGE_REQUIREMENT" in run("scaffold", str(minimal)).stderr
    for text in ('workspace_version: "0.2"\ninput: input.yaml\nprofile: profile.yaml\n', 'workspace_version: "0.1"\ninput: /tmp/input.yaml\nprofile: profile.yaml\n', 'workspace_version: "0.1"\ninput: missing.yaml\nprofile: profile.yaml\n', 'workspace_version: "0.1"\ninput: input.yaml\nprofile: profile.yaml\nunknown: x\n'):
        minimal.write_text(text)
        result = run("worksheet", str(minimal))
        assert result.returncode and ("CA_WORKSPACE_SCHEMA" in result.stderr or "CA_WORKSPACE_PATH" in result.stderr)


def test_workspace_cwd_relative_paths_and_parity(tmp_path: Path) -> None:
    workspace = EXAMPLES / "complete-service-workspace.yaml"
    result = run("check", str(workspace.resolve()), cwd=tmp_path)
    assert result.returncode == 0
    direct = subprocess.run([sys.executable, "tools/completion_materialize.py", "--input", str(EXAMPLES / "complete-service.yaml"), "--decisions", str(EXAMPLES / "complete-service-decisions.yaml"), "--mapping", str(EXAMPLES / "complete-service-mapping.yaml"), "--profile", str(PROFILE), "--format", "yaml"], cwd=ROOT, capture_output=True, text=True, check=False)
    workspace_result = run("materialize", str(workspace), "--format", "yaml")
    assert direct.returncode == workspace_result.returncode == 0
    assert direct.stdout == workspace_result.stdout


def test_workspace_worksheet_and_scaffold_match_direct_tools() -> None:
    workspace = str(EXAMPLES / "ir-search-and-track-workspace.yaml")
    worksheet = run("worksheet", workspace, "--format", "markdown")
    direct_worksheet = subprocess.run([sys.executable, "tools/completion_assistant.py", "--input", str(EXAMPLES / "ir-search-and-track.yaml"), "--decisions", str(EXAMPLES / "ir-search-and-track-decisions.yaml"), "--profile", str(PROFILE), "--format", "markdown"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert worksheet.returncode == direct_worksheet.returncode == 0
    assert worksheet.stdout == direct_worksheet.stdout
    scaffold = run("scaffold", workspace, "--format", "json")
    direct_scaffold = subprocess.run([sys.executable, "tools/completion_scaffold.py", "--input", str(EXAMPLES / "ir-search-and-track.yaml"), "--decisions", str(EXAMPLES / "ir-search-and-track-decisions.yaml"), "--mapping", str(EXAMPLES / "ir-search-and-track-mapping.yaml"), "--specific-functions", str(EXAMPLES / "ir-search-and-track-specific-functions.yaml"), "--profile", str(PROFILE), "--format", "json"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert scaffold.returncode == direct_scaffold.returncode == 0
    assert json.loads(scaffold.stdout) == json.loads(direct_scaffold.stdout)


def test_workspace_optional_artifacts_and_output_safety(tmp_path: Path) -> None:
    for name in ("complete-service-traceability-workspace.yaml", "complete-capability-service-workspace.yaml"):
        assert run("check", str(EXAMPLES / name)).returncode == 0
    output = tmp_path / "contract.yaml"
    workspace = str(EXAMPLES / "complete-service-workspace.yaml")
    assert run("materialize", workspace, "--format", "yaml", "--output", str(output)).returncode == 0
    assert "CA_OUTPUT_EXISTS" in run("materialize", workspace, "--format", "yaml", "--output", str(output)).stderr
    assert run("materialize", workspace, "--format", "yaml", "--output", str(output), "--force").returncode == 0


def test_incomplete_workspace_preserves_materialization_diagnostic() -> None:
    result = run("check", str(EXAMPLES / "ir-search-and-track-workspace.yaml"))
    assert result.returncode and result.stdout == "" and "CA_MATERIALIZATION_INCOMPLETE" in result.stderr and "Traceback" not in result.stderr
