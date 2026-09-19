from copy import deepcopy
from pathlib import Path

import pytest

from tools.validate import (
    load_document,
    profile_diagnostics,
    validate_document,
    validate_path,
    validate_profile_document,
    validate_profile_path,
)

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
        "Subsystem Startup",
        "Subsystem Status",
        "Subsystem State Command Processing",
        "Subsystem Built-In Test (BIT)",
        "Subsystem Calibration",
        "Subsystem Shutdown",
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


def test_oms_25_profile_stops_after_oms_version_mismatch() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []

    diagnostics = validate_path(
        ROOT
        / "tests"
        / "profiles"
        / "oms-2.5"
        / "invalid"
        / "service-wrong-oms-version-missing-functions.yaml",
        profile,
    )

    messages = [diagnostic.message for diagnostic in diagnostics]
    assert len(messages) == 1
    assert "requires OMS version '2.5'" in messages[0]
    assert not any("requires function" in message for message in messages)
    assert not any("exchange" in message for message in messages)


def test_oms_25_profile_stops_after_contract_version_mismatch() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []

    document = load_document(
        ROOT / "tests" / "profiles" / "oms-2.5" / "valid" / "service-required-functions.yaml"
    )
    document["contract_version"] = "9.9"
    diagnostics = profile_diagnostics(document, profile)

    messages = [diagnostic.message for diagnostic in diagnostics]
    assert len(messages) == 1
    assert "does not support contract version '9.9'" in messages[0]
    assert not any("requires function" in message for message in messages)


def _complete_service_status_document() -> dict:
    return load_document(ROOT / "tests" / "profiles" / "oms-2.5" / "valid" / "service-required-functions.yaml")


def _complete_subsystem_document() -> dict:
    return load_document(
        ROOT / "tests" / "profiles" / "oms-2.5" / "valid" / "subsystem-required-functions-all-applicable.yaml"
    )


def _subsystem_function(document: dict, name: str) -> dict:
    return next(function for function in document["functions"] if function["name"] == name)


def _subsystem_status(document: dict) -> dict:
    return _subsystem_function(document, "Subsystem Status")


@pytest.mark.parametrize(
    "name",
    [
        "Subsystem Startup",
        "Subsystem Status",
        "Subsystem State Command Processing",
        "Subsystem Built-In Test (BIT)",
        "Subsystem Calibration",
        "Subsystem Shutdown",
    ],
)
def test_oms_25_profile_rejects_each_missing_required_subsystem_function(name: str) -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_subsystem_document()
    document["functions"] = [function for function in document["functions"] if function["name"] != name]

    diagnostics = profile_diagnostics(document, profile)
    assert len(diagnostics) == 1
    assert name in diagnostics[0].message


@pytest.mark.parametrize("name", ["Subsystem Startup", "Subsystem Status", "Subsystem Shutdown"])
def test_oms_25_profile_rejects_not_applicable_fixed_subsystem_function(name: str) -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_subsystem_document()
    function = _subsystem_function(document, name)
    function["applicability"] = "not_applicable"
    function["not_applicable_reason"] = "Incorrectly marked not applicable."

    diagnostics = profile_diagnostics(document, profile)
    assert len(diagnostics) == 1
    assert "requires applicability 'applicable'" in diagnostics[0].message


@pytest.mark.parametrize(
    "name",
    ["Subsystem State Command Processing", "Subsystem Built-In Test (BIT)", "Subsystem Calibration"],
)
def test_oms_25_profile_allows_not_applicable_conditional_subsystem_function(name: str) -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_subsystem_document()
    function = _subsystem_function(document, name)
    function["applicability"] = "not_applicable"
    function["not_applicable_reason"] = "This behavior is not provided."

    assert validate_path(
        ROOT / "tests" / "profiles" / "oms-2.5" / "valid" / "subsystem-required-functions-conditional-na.yaml", profile
    ) == []
    assert profile_diagnostics(document, profile) == []


@pytest.mark.parametrize(
    "field, value",
    [("category", "specific"), ("required_group", "service")],
)
def test_oms_25_profile_rejects_wrong_subsystem_function_metadata(field: str, value: str) -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_subsystem_document()
    _subsystem_function(document, "Subsystem Startup")[field] = value

    diagnostics = profile_diagnostics(document, profile)
    assert len(diagnostics) == 1
    assert field in diagnostics[0].message


def test_oms_25_profile_rejects_duplicate_subsystem_function_name() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_subsystem_document()
    duplicate = deepcopy(_subsystem_function(document, "Subsystem Status"))
    duplicate["id"] = "another-local-status-id"
    document["functions"].append(duplicate)

    diagnostics = profile_diagnostics(document, profile)
    assert len(diagnostics) == 1
    assert "multiple matches" in diagnostics[0].message


def test_oms_25_profile_conditional_subsystem_function_without_reason_fails_contract_validation() -> None:
    document = _complete_subsystem_document()
    function = _subsystem_function(document, "Subsystem Calibration")
    function["applicability"] = "not_applicable"

    diagnostics = validate_path(
        ROOT / "tests" / "profiles" / "oms-2.5" / "valid" / "subsystem-required-functions-all-applicable.yaml"
    )
    assert diagnostics == []
    diagnostics = validate_document(document)
    assert any("not_applicable_reason" in diagnostic.message for diagnostic in diagnostics)


def test_oms_25_profile_subsystem_version_mismatch_stops_before_required_functions() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = load_document(
        ROOT / "tests" / "profiles" / "oms-2.5" / "invalid" / "subsystem-wrong-oms-version-missing-functions.yaml"
    )

    diagnostics = profile_diagnostics(document, profile)
    assert len(diagnostics) == 1
    assert "requires OMS version '2.5'" in diagnostics[0].message
    assert not any("requires function" in diagnostic.message for diagnostic in diagnostics)
    assert not any("required exchange" in diagnostic.message for diagnostic in diagnostics)


def test_oms_25_profile_subsystem_status_exchange_order_local_ids_and_topics_are_irrelevant() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_subsystem_document()
    status = _subsystem_status(document)
    status["id"] = "entirely-local-subsystem-status-id"
    status["exchanges"].reverse()
    for index, exchange in enumerate(status["exchanges"]):
        exchange["id"] = f"local-id-{index}"
        exchange["topic"] = f"unrelated/topic/{index}"
    assert profile_diagnostics(document, profile) == []


def test_oms_25_profile_allows_additional_subsystem_status_exchanges() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_subsystem_document()
    _subsystem_status(document)["exchanges"].append(
        {
            "id": "local-extra-status-row",
            "kind": "non_oms_message",
            "direction": "input",
            "mandate": "optional",
            "name": "LocalSubsystemIntegrationMessage",
            "timing": {"kind": "asynchronous"},
        }
    )
    assert profile_diagnostics(document, profile) == []


@pytest.mark.parametrize(
    "message",
    ["SubsystemStatus", "SubsystemStatusDataRequest", "SubsystemStatusDataRequestStatus"],
)
def test_oms_25_profile_rejects_each_missing_subsystem_status_exchange(message: str) -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_subsystem_document()
    status = _subsystem_status(document)
    status["exchanges"] = [item for item in status["exchanges"] if item["message"] != message]

    diagnostics = profile_diagnostics(document, profile)
    assert len(diagnostics) == 1
    assert message in diagnostics[0].message


@pytest.mark.parametrize(
    ("message", "field", "value"),
    [
        ("SubsystemStatus", "direction", "input"),
        ("SubsystemStatus", "mandate", "optional"),
        ("SubsystemStatus", "timing.kind", "asynchronous"),
        ("SubsystemStatusDataRequest", "direction", "output"),
        ("SubsystemStatusDataRequest", "mandate", "optional"),
        ("SubsystemStatusDataRequest", "timing.kind", "periodic"),
        ("SubsystemStatusDataRequestStatus", "direction", "input"),
        ("SubsystemStatusDataRequestStatus", "mandate", "optional"),
        ("SubsystemStatusDataRequestStatus", "timing.kind", "asynchronous"),
    ],
)
def test_oms_25_profile_rejects_subsystem_status_exchange_shape_mismatches(
    message: str, field: str, value: str
) -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_subsystem_document()
    exchange = _exchange(_subsystem_status(document), message)
    if field == "timing.kind":
        exchange["timing"]["kind"] = value
    else:
        exchange[field] = value

    diagnostics = profile_diagnostics(document, profile)
    assert len(diagnostics) == 1
    assert message in diagnostics[0].message


def test_oms_25_profile_requires_oms_message_kind_for_subsystem_status() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_subsystem_document()
    exchange = _exchange(_subsystem_status(document), "SubsystemStatus")
    exchange["kind"] = "non_oms_message"
    exchange["name"] = exchange.pop("message")
    exchange.pop("topic")

    diagnostics = profile_diagnostics(document, profile)
    assert len(diagnostics) == 1
    assert "SubsystemStatus" in diagnostics[0].message




def test_oms_25_profile_schema_requires_exactly_one_applicability_form() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    conditional = profile["required_functions"][4]
    conditional["applicability"] = "applicable"
    assert validate_profile_document(profile)

    del conditional["applicability"]
    del conditional["allowed_applicability"]
    assert validate_profile_document(profile)


def test_oms_25_profile_schema_rejects_duplicate_or_empty_allowed_applicability() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    conditional = profile["required_functions"][4]
    conditional["allowed_applicability"] = ["applicable", "applicable"]
    assert validate_profile_document(profile)

    conditional["allowed_applicability"] = []
    assert validate_profile_document(profile)


def _service_initialization(document: dict) -> dict:
    return next(function for function in document["functions"] if function["name"] == "Service Initialization")


def _exchange(function: dict, selector: str) -> dict:
    return next(item for item in function["exchanges"] if item.get("message", item.get("name")) == selector)


def test_oms_25_profile_service_initialization_exchange_order_and_local_ids_are_irrelevant() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_service_status_document()
    initialization = _service_initialization(document)
    initialization["id"] = "entirely-local-function-id"
    initialization["exchanges"].reverse()
    assert profile_diagnostics(document, profile) == []


def test_oms_25_profile_allows_additional_service_initialization_exchanges() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_service_status_document()
    _service_initialization(document)["exchanges"].append(
        {
            "id": "local-extra-initialization-row",
            "kind": "non_oms_message",
            "direction": "input",
            "mandate": "optional",
            "name": "LocalBootstrapMessage",
            "timing": {"kind": "asynchronous"},
        }
    )
    assert profile_diagnostics(document, profile) == []


@pytest.mark.parametrize(
    ("selector", "field", "value"),
    [
        ("FileMetadata", "direction", "output"),
        ("FileMetadata", "mandate", "mandatory"),
        ("FileMetadata", "timing.kind", "on_demand"),
        ("FileLocation", "direction", "output"),
        ("ServiceConfigFile", "direction", "output"),
        ("ServiceConfigFile", "mandate", "mandatory"),
        ("ServiceConfigFile", "timing.kind", "periodic"),
    ],
)
def test_oms_25_profile_rejects_wrong_service_initialization_exchange_shape(
    selector: str, field: str, value: str
) -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_service_status_document()
    exchange = _exchange(_service_initialization(document), selector)
    if field == "timing.kind":
        exchange["timing"]["kind"] = value
    else:
        exchange[field] = value

    diagnostics = profile_diagnostics(document, profile)
    assert len(diagnostics) == 1
    assert selector in diagnostics[0].message


@pytest.mark.parametrize("selector", ["FileMetadata", "FileLocation", "ServiceConfigFile"])
def test_oms_25_profile_rejects_each_missing_service_initialization_exchange(selector: str) -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_service_status_document()
    initialization = _service_initialization(document)
    initialization["exchanges"] = [item for item in initialization["exchanges"] if item.get("message", item.get("name")) != selector]

    diagnostics = profile_diagnostics(document, profile)
    assert len(diagnostics) == 1
    assert selector in diagnostics[0].message


def test_oms_25_profile_does_not_match_exchange_kinds_by_local_selector_text() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_service_status_document()
    transfer = _exchange(_service_initialization(document), "ServiceConfigFile")
    transfer["kind"] = "oms_message"
    transfer["message"] = transfer.pop("name")
    transfer["topic"] = "local.config"
    for field in ("protocol", "data_type", "data_format", "sharing_pattern"):
        transfer.pop(field)

    diagnostics = profile_diagnostics(document, profile)
    assert len(diagnostics) == 1
    assert "ServiceConfigFile" in diagnostics[0].message


def test_oms_25_profile_leaves_data_transfer_implementation_details_configurable() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_service_status_document()
    transfer = _exchange(_service_initialization(document), "ServiceConfigFile")
    transfer.update(
        protocol="MQTT",
        data_type="Program-Specific Configuration",
        data_format="CBOR",
        sharing_pattern="Shared Mutable",
    )
    assert profile_diagnostics(document, profile) == []


def test_oms_25_profile_does_not_apply_required_service_functions_to_complete_subsystems() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_subsystem_document()
    assert profile_diagnostics(document, profile) == []




@pytest.mark.parametrize(
    ("message", "field", "value"),
    [
        ("ServiceStatus", "direction", "input"),
        ("ServiceStatus", "mandate", "optional"),
        ("ServiceStatus", "timing.kind", "on_demand"),
    ],
)
def test_oms_25_profile_rejects_service_status_exchange_shape_mismatches(
    message: str, field: str, value: str
) -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_service_status_document()
    exchange = next(item for item in document["functions"][1]["exchanges"] if item["message"] == message)
    if field == "timing.kind":
        exchange["timing"]["kind"] = value
    else:
        exchange[field] = value

    diagnostics = profile_diagnostics(document, profile)
    assert len(diagnostics) == 1
    assert message in diagnostics[0].message


@pytest.mark.parametrize(
    "message",
    ["ServiceStatus", "ServiceStatusDataRequest", "ServiceStatusDataRequestStatus"],
)
def test_oms_25_profile_rejects_each_missing_service_status_exchange(message: str) -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_service_status_document()
    exchanges = document["functions"][1]["exchanges"]
    document["functions"][1]["exchanges"] = [item for item in exchanges if item["message"] != message]

    diagnostics = profile_diagnostics(document, profile)
    assert len(diagnostics) == 1
    assert message in diagnostics[0].message


def test_oms_25_profile_allows_additional_service_status_exchanges() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    document = _complete_service_status_document()
    document["functions"][1]["exchanges"].append(
        {
            "id": "local-extra-row",
            "kind": "non_oms_message",
            "direction": "input",
            "mandate": "optional",
            "name": "LocalIntegrationMessage",
            "timing": {"kind": "asynchronous"},
        }
    )
    assert profile_diagnostics(document, profile) == []


def test_oms_25_profile_rejects_duplicate_required_exchange_rules() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    duplicate = dict(profile["required_functions"][1]["required_exchanges"][0])
    duplicate["traceability"] = [
        {"source": "oms-service-contract-instructions-v25", "locator": "different prose"}
    ]
    profile["required_functions"][1]["required_exchanges"].append(duplicate)

    diagnostics = validate_profile_document(profile)
    assert any("duplicate required exchange rule" in diagnostic.message for diagnostic in diagnostics)


def test_oms_25_profile_rejects_duplicate_data_transfer_required_exchange_rules() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    duplicate = deepcopy(profile["required_functions"][0]["required_exchanges"][2])
    duplicate["traceability"][0]["locator"] = "different prose"
    profile["required_functions"][0]["required_exchanges"].append(duplicate)

    diagnostics = validate_profile_document(profile)
    assert any("duplicate required exchange rule" in diagnostic.message for diagnostic in diagnostics)


def test_oms_25_profile_rejects_unknown_required_exchange_traceability_source() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    profile["required_functions"][1]["required_exchanges"][0]["traceability"][0]["source"] = "unknown-source"

    diagnostics = validate_profile_document(profile)
    assert any("unknown source id 'unknown-source'" in diagnostic.message for diagnostic in diagnostics)


def test_oms_25_profile_schema_rejects_required_exchange_primitive() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    profile["required_functions"][1]["required_exchanges"][0]["primitive"] = "D"

    diagnostics = validate_profile_document(profile)
    assert any("primitive" in diagnostic.message for diagnostic in diagnostics)


@pytest.mark.parametrize("field", ["protocol", "data_type", "data_format", "sharing_pattern"])
def test_oms_25_profile_schema_rejects_data_transfer_implementation_requirements(field: str) -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    profile["required_functions"][0]["required_exchanges"][2][field] = "not-a-profile-constraint"

    diagnostics = validate_profile_document(profile)
    assert any(field in diagnostic.message for diagnostic in diagnostics)


def test_oms_25_profile_schema_rejects_data_transfer_rule_with_message() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    profile["required_functions"][0]["required_exchanges"][2]["message"] = "FileMetadata"

    diagnostics = validate_profile_document(profile)
    assert any("message" in diagnostic.message for diagnostic in diagnostics)


def test_oms_25_profile_schema_rejects_unsupported_required_exchange_kind() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    profile["required_functions"][0]["required_exchanges"][2]["kind"] = "special_signal"

    diagnostics = validate_profile_document(profile)
    assert diagnostics


def test_oms_25_profile_rejects_unknown_data_transfer_traceability_source() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []
    profile["required_functions"][0]["required_exchanges"][2]["traceability"][0]["source"] = "unknown-source"

    diagnostics = validate_profile_document(profile)
    assert any("unknown source id 'unknown-source'" in diagnostic.message for diagnostic in diagnostics)


def test_service_status_partial_example_lacks_only_service_initialization_for_oms_profile() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []

    diagnostics = validate_path(ROOT / "examples" / "service-status.yaml", profile)
    assert len(diagnostics) == 1
    assert "Service Initialization" in diagnostics[0].message


def test_service_initialization_partial_example_lacks_only_service_status_for_oms_profile() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []

    diagnostics = validate_path(ROOT / "examples" / "service-initialization.yaml", profile)
    assert len(diagnostics) == 1
    assert "Service Status" in diagnostics[0].message


def test_subsystem_status_partial_example_lacks_only_other_required_subsystem_functions() -> None:
    profile, diagnostics = validate_profile_path(PROFILE_PATH)
    assert diagnostics == []

    assert validate_path(ROOT / "examples" / "subsystem-status.yaml") == []
    diagnostics = validate_path(ROOT / "examples" / "subsystem-status.yaml", profile)
    messages = [diagnostic.message for diagnostic in diagnostics]
    assert len(messages) == 5
    for name in [
        "Subsystem Startup",
        "Subsystem State Command Processing",
        "Subsystem Built-In Test (BIT)",
        "Subsystem Calibration",
        "Subsystem Shutdown",
    ]:
        assert any(name in message for message in messages)
    assert not any("Subsystem Status" in message or "required exchange" in message for message in messages)
