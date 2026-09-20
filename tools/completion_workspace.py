"""Tooling-only completion workspace loading and path resolution."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

try:
    from tools.validate import Diagnostic
    from tools.yaml_support import YamlInputError, load_path
except ModuleNotFoundError:
    from validate import Diagnostic
    from yaml_support import YamlInputError, load_path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema/tooling/completion/v0.1/completion-workspace.schema.json"
CA_WORKSPACE_SCHEMA = "CA_WORKSPACE_SCHEMA"
CA_WORKSPACE_PATH = "CA_WORKSPACE_PATH"
CA_WORKSPACE_STAGE_REQUIREMENT = "CA_WORKSPACE_STAGE_REQUIREMENT"

STAGE_REQUIREMENTS = {
    "worksheet": ("input", "profile"),
    "scaffold": ("input", "profile", "decisions", "mapping"),
    "check": ("input", "profile", "decisions", "mapping"),
    "materialize": ("input", "profile", "decisions", "mapping"),
    "profile-evidence": ("input", "profile", "profile_evidence"),
}
PATH_FIELDS = ("input", "decisions", "specific_functions", "capabilities", "profile", "mapping", "traceability", "profile_evidence")


def _json_path(parts: Iterable[Any]) -> str:
    return "$" + "".join(f"[{part}]" if isinstance(part, int) else f".{part}" for part in parts)


def load_workspace(path: Path) -> tuple[dict[str, Any] | None, list[Diagnostic]]:
    """Load and schema-validate a workspace, without resolving its references."""
    try:
        document = load_path(path)
    except YamlInputError as exc:
        return None, [Diagnostic(CA_WORKSPACE_SCHEMA, str(path), str(exc))]
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document), key=lambda error: list(error.absolute_path))
    if errors:
        return None, [Diagnostic(CA_WORKSPACE_SCHEMA, _json_path(error.absolute_path), error.message) for error in errors]
    return document, []


def resolve_workspace(stage: str, workspace_path: Path) -> tuple[dict[str, Path] | None, list[Diagnostic]]:
    """Validate stage requirements and resolve readable regular artifact files."""
    workspace, diagnostics = load_workspace(workspace_path)
    if diagnostics:
        return None, diagnostics
    missing = [field for field in STAGE_REQUIREMENTS[stage] if field not in workspace]
    if missing:
        return None, [Diagnostic(CA_WORKSPACE_STAGE_REQUIREMENT, "$", f"{stage} requires workspace entries: {', '.join(missing)}")]
    resolved: dict[str, Path] = {}
    for field in PATH_FIELDS:
        if field not in workspace:
            continue
        value = workspace[field]
        if (Path(value).is_absolute() or value.startswith("~") or "$" in value or "%" in value
                or any(character in value for character in "*?[]{}")):
            diagnostics.append(Diagnostic(CA_WORKSPACE_PATH, f"$.{field}", "path must be a relative literal path"))
            continue
        reference = workspace_path.parent / value
        if not reference.is_file() or not os.access(reference, os.R_OK):
            diagnostics.append(Diagnostic(CA_WORKSPACE_PATH, f"$.{field}", f"referenced path is not a readable regular file: {reference}"))
            continue
        resolved[field] = reference.resolve()
    return (None, diagnostics) if diagnostics else (resolved, [])
