from copy import deepcopy
import json
from pathlib import Path

from tools import release_check

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "compatibility" / "support-v0.2.0.json"


def manifest() -> dict:
    value, diagnostics = release_check.load_manifest(MANIFEST_PATH)
    assert diagnostics == []
    return deepcopy(value)


def codes(value: dict) -> list[str]:
    return [diagnostic.code for diagnostic in release_check.check_manifest(value)]


def test_checked_in_support_manifest_is_valid() -> None:
    assert release_check.check_path(MANIFEST_PATH) == []


def test_rejects_bad_manifest_schema(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text("{}", encoding="utf-8")
    assert [diagnostic.code for diagnostic in release_check.check_path(path)] == [release_check.RC_SCHEMA] * 5


def test_rejects_missing_referenced_path() -> None:
    value = manifest()
    value["portable_contract"]["schema"] = "schema/v0.1/missing.json"
    assert release_check.RC_PATH in codes(value)


def test_rejects_unsafe_path() -> None:
    value = manifest()
    value["portable_contract"]["schema"] = "../schema/v0.1/service-contract.schema.json"
    assert release_check.RC_PATH in codes(value)


def test_rejects_project_release_mismatch() -> None:
    value = manifest()
    value["project_release"] = "0.2.1"
    assert release_check.RC_VERSION in codes(value)


def test_rejects_portable_version_mismatch() -> None:
    value = manifest()
    value["portable_contract"]["versions"] = ["0.2"]
    assert release_check.RC_VERSION in codes(value)


def test_rejects_canonical_fingerprint_mismatch() -> None:
    value = manifest()
    value["portable_contract"]["canonical_schema_sha256"] = "0" * 64
    assert release_check.RC_FINGERPRINT in codes(value)


def test_rejects_conformance_version_mismatch(monkeypatch) -> None:
    value = manifest()
    original = release_check.json.loads

    def modified_json(value_text: str):
        result = original(value_text)
        if isinstance(result, dict) and "contract_version" in result and "cases" in result:
            result["contract_version"] = "0.2"
        return result

    monkeypatch.setattr(release_check.json, "loads", modified_json)
    assert release_check.RC_CONFORMANCE in codes(value)


def test_rejects_profile_id_version_and_contract_support_mismatches(monkeypatch) -> None:
    value = manifest()
    original = release_check.validate_profile_path

    def modified_profile(path: Path):
        profile, diagnostics = original(path)
        profile = deepcopy(profile)
        profile.update(id="wrong", oms_version="2.6", profile_version="0.2", contract_versions=[])
        return profile, diagnostics

    monkeypatch.setattr(release_check, "validate_profile_path", modified_profile)
    assert codes(value).count(release_check.RC_PROFILE) == 4


def test_rejects_missing_uci_manifest() -> None:
    value = manifest()
    value["uci"]["baseline_manifests"][1]["path"] = "schema-sources/uci/2.6/missing.yaml"
    assert release_check.RC_PATH in codes(value)
    assert release_check.RC_SCHEMA_SOURCE in codes(value)


def test_rejects_uci_version_mismatch(monkeypatch) -> None:
    value = manifest()
    original = release_check.validate_manifest_path

    def modified_source(path: Path):
        source, diagnostics = original(path)
        source = deepcopy(source)
        source["schema_version"] = "9.9"
        return source, diagnostics

    monkeypatch.setattr(release_check, "validate_manifest_path", modified_source)
    assert release_check.RC_SCHEMA_SOURCE in codes(value)


def test_checked_in_uci_baselines_match_declared_identity_and_semantics() -> None:
    value = manifest()
    assert value["uci"]["baseline_versions"] == ["2.5", "2.6"]
    for entry in value["uci"]["baseline_manifests"]:
        source, diagnostics = release_check.validate_manifest_path(ROOT / entry["path"])
        assert diagnostics == []
        assert source["id"] == entry["id"]
        assert source["schema_version"] == entry["schema_version"]
        assert source["schema_family"] == "uci"
        assert source["role"] == "baseline"
    assert release_check.check_manifest(value) == []


def test_rejects_extension_manifest_as_uci_baseline(monkeypatch) -> None:
    value = manifest()
    original = release_check.validate_manifest_path

    def extension_source(path: Path):
        source, diagnostics = original(path)
        source = deepcopy(source)
        if source["schema_version"] == "2.5":
            source["role"] = "extension"
        return source, diagnostics

    monkeypatch.setattr(release_check, "validate_manifest_path", extension_source)
    assert release_check.RC_SCHEMA_SOURCE in codes(value)


def test_rejects_extra_observed_baseline_version() -> None:
    value = manifest()
    value["uci"]["baseline_versions"] = ["2.5"]
    assert release_check.RC_SCHEMA_SOURCE in codes(value)


def test_rejects_missing_observed_baseline_version() -> None:
    value = manifest()
    value["uci"]["baseline_manifests"] = [value["uci"]["baseline_manifests"][0]]
    assert release_check.RC_SCHEMA_SOURCE in codes(value)


def test_rejects_unexpected_observed_baseline_version(monkeypatch) -> None:
    value = manifest()
    original = release_check.validate_manifest_path

    def unexpected_source(path: Path):
        source, diagnostics = original(path)
        source = deepcopy(source)
        if source["schema_version"] == "2.6":
            source["schema_version"] = "9.9"
        return source, diagnostics

    monkeypatch.setattr(release_check, "validate_manifest_path", unexpected_source)
    assert release_check.RC_SCHEMA_SOURCE in codes(value)


def test_rejects_old_resolver_evidence_field(tmp_path: Path) -> None:
    value = manifest()
    value["uci"]["resolver_evidence"] = value["uci"].pop("baseline_versions")
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    assert release_check.RC_SCHEMA in [diagnostic.code for diagnostic in release_check.check_path(path)]


def test_rejects_duplicate_unreleased_and_missing_prospective_section(tmp_path: Path) -> None:
    value = manifest()
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("## [Unreleased]\n## [Unreleased]\n## [0.1.0] - 2026-09-18\n", encoding="utf-8")
    codes = [diagnostic.code for diagnostic in release_check.check_manifest(value, changelog_path=changelog)]
    assert codes.count(release_check.RC_CHANGELOG) == 2


def test_rejects_missing_historical_release_section(tmp_path: Path) -> None:
    value = manifest()
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("## [Unreleased]\n## [0.2.0] - TBD\n", encoding="utf-8")
    assert release_check.RC_CHANGELOG in [
        diagnostic.code for diagnostic in release_check.check_manifest(value, changelog_path=changelog)
    ]
