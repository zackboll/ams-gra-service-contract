from pathlib import Path

import pytest

from tools.schema_sources import load_manifest
from tools.validate import load_document
from tools.yaml_support import YamlInputError, load_text


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("scalar", "expected"),
    [
        ("yes", "yes"),
        ("no", "no"),
        ("on", "on"),
        ("off", "off"),
        ("true", True),
        ("FALSE", False),
        ("2026-01-22", "2026-01-22"),
        ("1:20", "1:20"),
        ("012", 12),
        ("0o12", 10),
    ],
)
def test_yaml_12_core_scalar_behavior(scalar: str, expected: object) -> None:
    assert load_text(f"value: {scalar}\n")["value"] == expected


@pytest.mark.parametrize(
    "text",
    [
        "value: .nan\n",
        "value: .inf\n",
        "value: -.Inf\n",
        "[not-a-string-key]: value\n",
        "value: !!set {item: null}\n",
        "value: !!python/object/apply:os.system ['false']\n",
    ],
)
def test_non_json_or_unsafe_yaml_is_rejected(text: str) -> None:
    with pytest.raises(YamlInputError):
        load_text(text)


def test_duplicate_mapping_key_is_rejected() -> None:
    with pytest.raises(YamlInputError, match="duplicate mapping key 'oms_version'"):
        load_text('standards:\n  oms_version: "2.5"\n  oms_version: "2.6"\n')


def test_normal_json_document_loads() -> None:
    assert load_text('{"enabled": true, "items": [1, null]}\n') == {"enabled": True, "items": [1, None]}


def test_checked_in_contract_examples_parse_identically() -> None:
    for path in sorted((ROOT / "examples").glob("*.yaml")):
        assert load_document(path) == load_text(path.read_text(encoding="utf-8"), str(path))


def test_checked_in_profile_and_schema_source_manifest_parse() -> None:
    profile = load_document(ROOT / "profiles" / "oms" / "2.5" / "profile.yaml")
    manifest = load_manifest(ROOT / "schema-sources" / "uci" / "2.5" / "manifest.yaml")
    assert profile["id"] == "oms-2.5"
    assert manifest["id"] == "uci-2.5-baseline"
