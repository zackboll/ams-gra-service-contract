import hashlib
from copy import deepcopy
from pathlib import Path

import pytest

from tools.schema_sources import compose_schema_source_set, load_verified_schema_source_set
from tools.validate import load_document
from tools.uci_resolver import UciResolverError, load_message_definitions, parse_uci_schema_bytes, resolve_contract_messages

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "uci-resolver"


def manifest(manifest_id: str, files: dict[str, bytes], role: str = "baseline") -> dict[str, object]:
    result: dict[str, object] = {
        "manifest_version": "0.1", "id": manifest_id, "schema_family": "uci", "schema_version": "2.5", "role": role,
        "source": {"kind": "git", "repository": "https://example.test/uci.git", "revision": "a" * 40},
        "root_schema": sorted(files)[0],
        "files": [{"path": path, "sha256": hashlib.sha256(data).hexdigest()} for path, data in sorted(files.items())],
    }
    if role == "extension":
        result["compatible_baseline_versions"] = ["2.5"]
    return result


def stage(tmp_path: Path, files: dict[str, bytes]) -> Path:
    for name, data in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return tmp_path


def fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def contract(message: str = "MessageA", extension_ids: list[str] | None = None) -> dict[str, object]:
    result = deepcopy(load_document(ROOT / "tests" / "valid" / "service-status.yaml"))
    result["functions"] = [deepcopy(result["functions"][0])]
    result["functions"][0]["exchanges"] = [deepcopy(result["functions"][0]["exchanges"][0])]
    result["functions"][0]["exchanges"][0]["message"] = message
    if extension_ids is not None:
        result["standards"]["uci_extension_schemas"] = extension_ids
    return result


def resolve(tmp_path: Path, contract_data: dict[str, object], baseline_files: dict[str, bytes], extensions: list[tuple[dict[str, object], dict[str, bytes]]]=[]) -> list:
    baseline = manifest("baseline", baseline_files)
    extension_manifests = [item[0] for item in extensions]
    schema_set, diagnostics = compose_schema_source_set(contract_data, baseline, extension_manifests)
    assert diagnostics == []
    roots = {"baseline": stage(tmp_path / "baseline", baseline_files)}
    for extension_manifest, files in extensions:
        roots[extension_manifest["id"]] = stage(tmp_path / str(extension_manifest["id"]), files)
    verified_schema_set, diagnostics = load_verified_schema_source_set(schema_set, roots)
    assert diagnostics == []
    return resolve_contract_messages(contract_data, verified_schema_set)


def test_parser_indexes_global_message_and_normalizes_trailing_period() -> None:
    definitions = parse_uci_schema_bytes(fixture("baseline.xsd"), "baseline", "baseline.xsd")
    assert [(item.local_name, item.primitive, item.expanded_name) for item in definitions] == [("MessageA", "Data-1", "{urn:baseline}MessageA")]


@pytest.mark.parametrize(("raw_primitive", "expected"), [("Status-1", "Status-1"), ("Status-1.", "Status-1"), ("Status-1..", "Status-1.")])
def test_parser_removes_exactly_one_final_prose_period(raw_primitive: str, expected: str) -> None:
    data = fixture("baseline.xsd").replace(b"Data-1.", raw_primitive.encode())
    assert parse_uci_schema_bytes(data, "baseline", "baseline.xsd")[0].primitive == expected


def test_parser_excludes_nested_and_unmarked_global_elements() -> None:
    names = [item.local_name for item in parse_uci_schema_bytes(fixture("baseline.xsd"), "baseline", "baseline.xsd")]
    assert "NestedMessage" not in names
    assert "NoPrimitive" not in names


def test_parser_excludes_primitive_metadata_on_inline_complex_type() -> None:
    assert parse_uci_schema_bytes(fixture("inline-primitive.xsd"), "baseline", "inline-primitive.xsd") == []


@pytest.mark.parametrize(("name", "match"), [("duplicate-primitive.xsd", "duplicate UCI_PRIMITIVE"), ("empty-primitive.xsd", "empty UCI_PRIMITIVE"), ("malformed.xsd", "could not parse")])
def test_parser_rejects_bad_metadata_and_xml(name: str, match: str) -> None:
    with pytest.raises(UciResolverError, match=match):
        parse_uci_schema_bytes(fixture(name), "baseline", name)


def test_one_candidate_resolves(tmp_path: Path) -> None:
    resolved = resolve(tmp_path, contract(), {"baseline.xsd": fixture("baseline.xsd")})
    assert resolved[0].primitive == "Data-1"


def test_resolver_parses_verified_snapshot_after_filesystem_mutation(tmp_path: Path) -> None:
    original = fixture("baseline.xsd")
    replacement = original.replace(b"Data-1.", b"Status-1.")
    baseline = manifest("baseline", {"baseline.xsd": original})
    schema_set, diagnostics = compose_schema_source_set(contract(), baseline, [])
    assert diagnostics == []
    root = stage(tmp_path, {"baseline.xsd": original})
    verified_schema_set, diagnostics = load_verified_schema_source_set(schema_set, {"baseline": root})
    assert diagnostics == []
    (root / "baseline.xsd").write_bytes(replacement)
    assert resolve_contract_messages(contract(), verified_schema_set)[0].primitive == "Data-1"


def test_zero_candidates_fails_unknown(tmp_path: Path) -> None:
    with pytest.raises(UciResolverError, match="unknown UCI message 'DoesNotExist'.*service-status.*service-status-output"):
        resolve(tmp_path, contract("DoesNotExist"), {"baseline.xsd": fixture("baseline.xsd")})


def test_two_namespaces_with_same_local_name_fail_ambiguously(tmp_path: Path) -> None:
    with pytest.raises(UciResolverError, match=r"(?s)ambiguous UCI message 'ExampleMessage'.*\{urn:a\}ExampleMessage.*\{urn:b\}ExampleMessage"):
        resolve(tmp_path, contract("ExampleMessage"), {"a.xsd": fixture("ambiguous-a.xsd"), "b.xsd": fixture("ambiguous-b.xsd")})


def test_same_expanded_name_duplicate_fails_ambiguously(tmp_path: Path) -> None:
    source = fixture("ambiguous-a.xsd")
    with pytest.raises(UciResolverError, match="ambiguous UCI message 'ExampleMessage'"):
        resolve(tmp_path, contract("ExampleMessage"), {"a.xsd": source, "b.xsd": source})


def test_unique_extension_resolves_and_manifest_input_order_does_not_change_result(tmp_path: Path) -> None:
    extension_a = manifest("extension-a", {"extension.xsd": fixture("extension.xsd")}, "extension")
    extension_b = manifest("extension-b", {"unrelated.xsd": fixture("baseline.xsd")}, "extension")
    extensions = [(extension_a, {"extension.xsd": fixture("extension.xsd")}), (extension_b, {"unrelated.xsd": fixture("baseline.xsd")})]
    resolved = resolve(
        tmp_path / "forward", contract("ExtensionMessage", ["extension-a", "extension-b"]),
        {"baseline.xsd": fixture("baseline.xsd")},
        extensions,
    )
    reversed_resolved = resolve(
        tmp_path / "reverse", contract("ExtensionMessage", ["extension-a", "extension-b"]),
        {"baseline.xsd": fixture("baseline.xsd")},
        list(reversed(extensions)),
    )
    assert resolved[0].manifest_id == "extension-a"
    assert reversed_resolved == resolved


def test_non_oms_data_transfer_is_ignored(tmp_path: Path) -> None:
    data = load_document(ROOT / "examples" / "service-initialization.yaml")
    data["functions"][0]["exchanges"] = [data["functions"][0]["exchanges"][2]]
    assert resolve(tmp_path / "only-transfer", data, {"baseline.xsd": fixture("baseline.xsd")}) == []
