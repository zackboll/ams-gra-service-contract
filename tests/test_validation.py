from pathlib import Path

import pytest

from tools.validate import load_document, validate_path

ROOT = Path(__file__).resolve().parents[1]


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
