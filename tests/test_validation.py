from pathlib import Path

import pytest

from tools.validate import load_document, validate_path, validate_profile_path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "profiles" / "oms" / "2.5" / "profile.yaml"


@pytest.mark.parametrize("path", sorted((ROOT / "tests" / "valid").glob("*.yaml")))
def test_valid_contracts(path: Path) -> None:
    assert validate_path(path) == []


@pytest.mark.parametrize("path", sorted((ROOT / "tests" / "invalid").glob("*.yaml")))
def test_invalid_contracts(path: Path) -> None:
    assert validate_path(path), f"expected {path} to be rejected"


def test_capability_enable_disable_reference_example() -> None:
    document = load_document(ROOT / "examples" / "capability-enable-disable.yaml")
    function = document["functions"][0]

    assert function["category"] == "required"
    assert function["required_group"] == "capability"

    exchanges = {exchange["message"]: exchange for exchange in function["exchanges"]}
    assert exchanges["ESM_SettingsCommand"] == {
        "id": "esm-settings-command-input",
        "kind": "oms_message",
        "direction": "input",
        "mandate": "mandatory",
        "message": "ESM_SettingsCommand",
        "topic": "ESM_SettingsCommand",
        "timing": {"kind": "asynchronous"},
        "traceability": [
            {
                "source": "oms-service-contract-instructions-v25",
                "locator": "Capability Enable/Disable / Inputs and Outputs",
            }
        ],
    }
    assert exchanges["ESM_SettingsCommandStatus"]["kind"] == "oms_message"
    assert exchanges["ESM_SettingsCommandStatus"]["direction"] == "output"
    assert exchanges["ESM_SettingsCommandStatus"]["mandate"] == "mandatory"
    assert exchanges["ESM_SettingsCommandStatus"]["timing"] == {"kind": "on_demand"}
    assert all("primitive" not in exchange for exchange in exchanges.values())


def test_service_initialization_data_transfer_reference_example() -> None:
    document = load_document(ROOT / "examples" / "service-initialization.yaml")
    function = document["functions"][0]

    assert function["category"] == "required"
    assert function["required_group"] == "service"

    exchanges = {
        exchange.get("message", exchange.get("name")): exchange
        for exchange in function["exchanges"]
    }

    assert exchanges["FileMetadata"]["kind"] == "oms_message"
    assert exchanges["FileLocation"]["kind"] == "oms_message"

    transfer = exchanges["ServiceConfigFile"]
    assert transfer["kind"] == "data_transfer"
    assert transfer["direction"] == "input"
    assert transfer["mandate"] == "optional"
    assert transfer["protocol"] == "NFS"
    assert transfer["data_type"] == "Configuration File"
    assert transfer["data_format"] == "Custom Text"
    assert transfer["sharing_pattern"] == "Exclusive Use"
    assert transfer["timing"] == {"kind": "asynchronous"}


def test_oms_25_profile_manifest() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)

    assert diagnostics == []
    assert profile["profile_version"] == "0.1"
    assert profile["id"] == "oms-2.5"
    assert profile["oms_version"] == "2.5"
    assert profile["contract_versions"] == ["0.1"]
    assert {source["id"] for source in profile["sources"]} == {
        "oms-service-contract-instructions-v25"
    }
    assert [function["name"] for function in profile["required_functions"]] == [
        "Service Initialization",
        "Service Status",
    ]
    assert all(len(function["applies_to"]) == len(set(function["applies_to"])) for function in profile["required_functions"])


@pytest.mark.parametrize(
    "path",
    sorted((ROOT / "tests" / "profiles" / "oms-2.5" / "valid").glob("*.yaml")),
)
def test_oms_25_profile_valid_contracts(path: Path) -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    assert validate_path(path, profile) == []


@pytest.mark.parametrize(
    "path",
    sorted((ROOT / "tests" / "profiles" / "oms-2.5" / "invalid").glob("*.yaml")),
)
def test_oms_25_profile_invalid_contracts(path: Path) -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    assert validate_path(path, profile), f"expected {path} to be rejected by OMS 2.5 profile"


def test_oms_25_profile_reports_duplicate_standard_function() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []

    diagnostics = validate_path(
        ROOT / "tests" / "profiles" / "oms-2.5" / "invalid" / "service-duplicate-status.yaml",
        profile,
    )
    assert any("multiple matches" in diagnostic.message for diagnostic in diagnostics)
