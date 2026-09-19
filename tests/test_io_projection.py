from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest

from tools.io_projection import (
    INPUTS_OUTPUTS_DIAGNOSTIC_CODES, IP_AMBIGUOUS_RESOLUTION,
    IP_MESSAGE_MISMATCH, IP_MISSING_RESOLUTION, IP_UNEXPECTED_RESOLUTION,
    InputsOutputsProjectionError, project_inputs_outputs, render_json,
    render_markdown,
)
from tools.uci_resolver import ResolvedOmsExchange
from tools.validate import load_document


ROOT = Path(__file__).resolve().parents[1]


def oms_resolution(function_id: str, exchange_id: str, message: str = "MessageA") -> ResolvedOmsExchange:
    return ResolvedOmsExchange(function_id, exchange_id, message, "{urn:test}" + message, "Status-1", "{urn:test}" + message + "MT", "baseline", "test.xsd")


def real_resolution(function_id: str, exchange_id: str, message: str, primitive: str) -> ResolvedOmsExchange:
    namespace = "https://www.vdl.afrl.af.mil/programs/oam"
    return ResolvedOmsExchange(function_id, exchange_id, message, f"{{{namespace}}}{message}", primitive, f"{{{namespace}}}{message}MT", "uci-2.5-baseline", "OAC-STD-UCI_V2.5/UCI_MessageDefinitions_v2_5_0.xsd")


def manifest_for(xsd: bytes) -> dict[str, object]:
    return {"manifest_version": "0.1", "id": "baseline", "schema_family": "uci", "schema_version": "2.5", "role": "baseline", "source": {"kind": "git", "repository": "https://example.test/uci.git", "revision": "a" * 40}, "root_schema": "message.xsd", "files": [{"path": "message.xsd", "sha256": hashlib.sha256(xsd).hexdigest()}]}


def run_projection(contract_path: Path, manifest_path: Path, source: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "tools/io_projection.py", "--contract", str(contract_path), "--baseline-manifest", str(manifest_path), "--baseline-source-root", str(source), "--format", "json"], cwd=ROOT, text=True, capture_output=True, check=False)


def contract() -> dict:
    data = deepcopy(load_document(ROOT / "tests" / "valid" / "service-status.yaml"))
    function = data["functions"][0]
    function["id"] = "first"
    function["name"] = "First | Function\nName"
    function["exchanges"] = [function["exchanges"][0]]
    function["exchanges"][0].update({"id": "message", "message": "MessageA", "topic": "Topic|One\nTwo", "operational_attribute": "OA", "subscription_group": "SG", "appendix_c_mapping": "Appendix"})
    function["exchanges"].append({"id": "transfer", "kind": "data_transfer", "direction": "input", "mandate": "optional", "name": "Transfer", "protocol": "NFS", "data_type": "Configuration File", "data_format": "Custom Text", "sharing_pattern": "Exclusive Use", "timing": {"kind": "on_demand", "nominal_response_seconds": 0.5, "max_response_seconds": 3.0}})
    function["exchanges"].extend([
        {"id": "signal", "kind": "special_signal", "direction": "output", "mandate": "mandatory", "name": "Signal", "details": "signal details", "reference": "signal ref", "timing": {"kind": "asynchronous"}},
        {"id": "security", "kind": "security_exchange", "direction": "input", "mandate": "optional", "name": "Security", "details": "security details", "reference": "security ref", "timing": {"kind": "periodic", "nominal_rate_hz": 1.0, "max_rate_hz": 0.5}},
        {"id": "legacy", "kind": "non_oms_message", "direction": "output", "mandate": "optional", "name": "Legacy", "details": "legacy details", "reference": "legacy ref", "timing": {"kind": "on_demand"}},
    ])
    data["functions"].append({"id": "second", "name": "Second Function", "category": "specific", "applicability": "not_applicable", "not_applicable_reason": "No hardware", "exchanges": []})
    return data


def test_projection_preserves_function_and_exchange_order_and_uci_metadata() -> None:
    projection = project_inputs_outputs(contract(), [oms_resolution("first", "message")])
    assert [item.function_id for item in projection.functions] == ["first", "second"]
    assert [item.exchange_id for item in projection.functions[0].exchanges] == ["message", "transfer", "signal", "security", "legacy"]
    message = projection.functions[0].exchanges[0]
    assert (message.uci_primitive, message.message_qname, message.message_type_qname) == ("Status-1", "{urn:test}MessageA", "{urn:test}MessageAMT")
    assert (message.schema_manifest_id, message.schema_source_path) == ("baseline", "test.xsd")


def test_all_exchange_kinds_and_information_are_projected() -> None:
    exchanges = project_inputs_outputs(contract(), [oms_resolution("first", "message")]).functions[0].exchanges
    assert exchanges[0].information == "Topic|One\nTwo [OA] [SG]"
    assert exchanges[1].information == "NFS [Configuration File, Custom Text, Exclusive Use]"
    assert exchanges[1].uci_primitive is None
    assert [(item.kind, item.information, item.reference) for item in exchanges[2:]] == [
        ("special_signal", "signal details", "signal ref"),
        ("security_exchange", "security details", "security ref"),
        ("non_oms_message", "legacy details", "legacy ref"),
    ]


def test_markdown_mappings_timing_blank_values_and_escaping_are_deterministic() -> None:
    projection = project_inputs_outputs(contract(), [oms_resolution("first", "message")])
    rendered = render_markdown(projection)
    assert rendered == render_markdown(projection)
    assert "## First \\| Function Name" in rendered
    assert "Topic\\|One Two [OA] [SG]" in rendered
    assert "| Status-1 | O | M | MessageA |" in rendered
    assert "| NFS [Configuration File, Custom Text, Exclusive Use] | O | OD | 0.5 s | 3 s |" in rendered
    assert "| 1 Hz | 0.5 Hz |" in rendered
    assert "|  | O |  | Legacy | legacy details | O | OD |  |  |  | legacy ref |" in rendered
    assert "Not Applicable — No hardware" in rendered
    assert rendered.endswith("\n")
    assert not any(line.endswith(" ") for line in rendered.splitlines())


def test_oms_information_without_optional_attributes_and_appendix_absence() -> None:
    data = contract()
    exchange = data["functions"][0]["exchanges"][0]
    del exchange["operational_attribute"]
    del exchange["subscription_group"]
    del exchange["appendix_c_mapping"]
    projected = project_inputs_outputs(data, [oms_resolution("first", "message")]).functions[0].exchanges[0]
    assert projected.information == "Topic|One\nTwo"
    assert projected.appendix_c_mapping is None


def test_json_is_deterministic_and_keeps_canonical_values() -> None:
    projection = project_inputs_outputs(contract(), [oms_resolution("first", "message")])
    rendered = render_json(projection)
    assert rendered == render_json(projection)
    assert '"direction": "output"' in rendered
    assert '"timing_kind": "periodic"' in rendered
    assert rendered.endswith("\n")


def test_inputs_outputs_diagnostic_code_inventory_is_stable() -> None:
    assert len(INPUTS_OUTPUTS_DIAGNOSTIC_CODES) == 4
    assert all(re.fullmatch(r"IP_[A-Z0-9_]+", code) for code in INPUTS_OUTPUTS_DIAGNOSTIC_CODES)


@pytest.mark.parametrize(
    ("resolved", "code", "message"),
    [
        ([oms_resolution("missing", "message")], IP_UNEXPECTED_RESOLUTION, "'missing'/'message'"),
        ([oms_resolution("first", "message"), oms_resolution("first", "message")], IP_AMBIGUOUS_RESOLUTION, "'first'/'message'"),
        ([oms_resolution("first", "message", "MessageB")], IP_MESSAGE_MISMATCH, "'MessageA', resolved message 'MessageB'"),
        ([], IP_MISSING_RESOLUTION, "'first'/'message'"),
    ],
)
def test_resolution_join_fails_closed_with_exact_projection_code(resolved: list[ResolvedOmsExchange], code: str, message: str) -> None:
    with pytest.raises(InputsOutputsProjectionError) as raised:
        project_inputs_outputs(contract(), resolved)
    assert raised.value.code == code
    assert message in raised.value.message
    assert str(raised.value).startswith(f"{code} ")


def test_resolver_cli_output_is_unchanged_for_invalid_contract() -> None:
    result = subprocess.run([sys.executable, "tools/uci_resolver.py", "resolve", "--contract", "missing.yaml", "--baseline-manifest", "missing.yaml", "--baseline-source-root", "."], cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode == 1
    assert result.stdout.startswith("FAIL contract input")
    assert "SC_SCHEMA could not parse contract missing.yaml:" in result.stdout


def test_schema_source_cli_failures_are_clear_and_resolver_compatible(tmp_path: Path) -> None:
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(json.dumps(contract()), encoding="utf-8")
    invalid_manifest = tmp_path / "invalid-manifest.json"
    invalid_manifest.write_text("{}", encoding="utf-8")
    xsd = b"<xs:schema xmlns:xs=\"http://www.w3.org/2001/XMLSchema\" targetNamespace=\"urn:test\"/>"
    composition_manifest = tmp_path / "composition-manifest.json"
    composition_manifest.write_text(json.dumps({"manifest_version": "0.1", "id": "baseline", "schema_family": "uci", "schema_version": "2.4", "role": "baseline", "source": {"kind": "git", "repository": "https://example.test/uci.git", "revision": "a" * 40}, "root_schema": "message.xsd", "files": [{"path": "message.xsd", "sha256": hashlib.sha256(xsd).hexdigest()}]}), encoding="utf-8")
    for manifest_path, expected in ((invalid_manifest, "FAIL schema-source manifests"), (composition_manifest, "FAIL schema-source set")):
        resolver = subprocess.run([sys.executable, "tools/uci_resolver.py", "resolve", "--contract", str(contract_path), "--baseline-manifest", str(manifest_path), "--baseline-source-root", str(tmp_path)], cwd=ROOT, text=True, capture_output=True, check=False)
        projection = subprocess.run([sys.executable, "tools/io_projection.py", "--contract", str(contract_path), "--baseline-manifest", str(manifest_path), "--baseline-source-root", str(tmp_path), "--format", "json"], cwd=ROOT, text=True, capture_output=True, check=False)
        assert resolver.returncode == projection.returncode == 1
        assert resolver.stdout.splitlines()[0] == expected
        assert projection.stdout.splitlines()[0] == f"{expected} failed:"
        assert "Traceback" not in resolver.stderr + projection.stderr


def test_projection_cli_handles_a_synthetic_verified_source(tmp_path: Path) -> None:
    data = contract()
    xsd = b'''<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" targetNamespace="urn:test" xmlns:tns="urn:test"><xs:complexType name="MessageAMT"/><xs:element name="MessageA" type="tns:MessageAMT"><xs:annotation><xs:documentation>UCI_PRIMITIVE: Status-1.</xs:documentation></xs:annotation></xs:element></xs:schema>'''
    source = tmp_path / "source"
    source.mkdir()
    (source / "message.xsd").write_bytes(xsd)
    manifest = manifest_for(xsd)
    contract_path = tmp_path / "contract.json"
    manifest_path = tmp_path / "manifest.json"
    contract_path.write_text(json.dumps(data), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = run_projection(contract_path, manifest_path, source)
    assert result.returncode == 0
    assert json.loads(result.stdout)["functions"][0]["exchanges"][0]["uci_primitive"] == "Status-1"


@pytest.mark.parametrize("failure", ["invalid-contract", "tampered-source", "unknown-message", "malformed-xml"])
def test_projection_cli_preserves_lower_layer_diagnostic_ownership(tmp_path: Path, failure: str) -> None:
    data = contract()
    xsd = b'''<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" targetNamespace="urn:test" xmlns:tns="urn:test"><xs:complexType name="MessageAMT"/><xs:element name="MessageA" type="tns:MessageAMT"><xs:annotation><xs:documentation>UCI_PRIMITIVE: Status-1.</xs:documentation></xs:annotation></xs:element></xs:schema>'''
    source = tmp_path / "source"
    source.mkdir()
    source_bytes = xsd
    expected = {"invalid-contract": "SC_SCHEMA", "tampered-source": "SS_HASH_MISMATCH", "unknown-message": "UR_UNKNOWN_MESSAGE", "malformed-xml": "UR_XML_PARSE"}[failure]
    if failure == "invalid-contract":
        del data["functions"]
    elif failure == "tampered-source":
        source_bytes = b"tampered"
    elif failure == "unknown-message":
        data["functions"][0]["exchanges"][0]["message"] = "DoesNotExist"
    elif failure == "malformed-xml":
        xsd = b"<xs:schema"
        source_bytes = xsd
    (source / "message.xsd").write_bytes(source_bytes)
    contract_path = tmp_path / "contract.json"
    manifest_path = tmp_path / "manifest.json"
    contract_path.write_text(json.dumps(data), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest_for(xsd)), encoding="utf-8")
    result = run_projection(contract_path, manifest_path, source)
    assert result.returncode == 1
    assert expected in result.stdout
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr
    assert "IP_" not in result.stdout


def test_source_example_projection_preserves_expected_uci_identities() -> None:
    status = load_document(ROOT / "examples" / "service-status.yaml")
    status_ids = [("service-status", "service-status-output", "ServiceStatus", "Status-1"), ("service-status", "service-status-data-request-input", "ServiceStatusDataRequest", "DataRequest-2"), ("service-status", "service-status-data-request-status-output", "ServiceStatusDataRequestStatus", "DataRequest-2")]
    status_projection = project_inputs_outputs(status, [real_resolution(function, exchange, message, primitive) for function, exchange, message, primitive in status_ids])
    assert [(item.exchange_name, item.uci_primitive, item.message_type_qname) for item in status_projection.functions[0].exchanges] == [(message, primitive, f"{{https://www.vdl.afrl.af.mil/programs/oam}}{message}MT") for _, _, message, primitive in status_ids]
    initialization = load_document(ROOT / "examples" / "service-initialization.yaml")
    initialization_projection = project_inputs_outputs(initialization, [real_resolution("service-initialization", "file-metadata-input", "FileMetadata", "DataRecord-1"), real_resolution("service-initialization", "file-location-input", "FileLocation", "DataRecord-1")])
    assert [(item.exchange_name, item.uci_primitive) for item in initialization_projection.functions[0].exchanges] == [("FileMetadata", "DataRecord-1"), ("FileLocation", "DataRecord-1"), ("ServiceConfigFile", None)]
    subsystem_status = load_document(ROOT / "examples" / "subsystem-status.yaml")
    subsystem_status_ids = [("subsystem-status", "subsystem-status-output", "SubsystemStatus", "Status-1"), ("subsystem-status", "subsystem-status-data-request-input", "SubsystemStatusDataRequest", "DataRequest-2"), ("subsystem-status", "subsystem-status-data-request-status-output", "SubsystemStatusDataRequestStatus", "DataRequest-2")]
    subsystem_projection = project_inputs_outputs(subsystem_status, [real_resolution(function, exchange, message, primitive) for function, exchange, message, primitive in subsystem_status_ids])
    assert [(item.exchange_name, item.uci_primitive, item.message_type_qname) for item in subsystem_projection.functions[0].exchanges] == [(message, primitive, f"{{https://www.vdl.afrl.af.mil/programs/oam}}{message}MT") for _, _, message, primitive in subsystem_status_ids]
