import hashlib
import re
from copy import deepcopy
from pathlib import Path

from tools import schema_sources
from tools.schema_sources import (
    SCHEMA_SOURCE_DIAGNOSTIC_CODES,
    SS_BASELINE_SELECTION,
    SS_DUPLICATE_FILE,
    SS_EXTENSION_COMPATIBILITY,
    SS_EXTENSION_MAPPING,
    SS_FILE_MISSING,
    SS_FILE_ORDER,
    SS_FILE_OUTSIDE_ROOT,
    SS_FILE_READ,
    SS_HASH_MISMATCH,
    SS_MANIFEST_ID_COLLISION,
    SS_ROOT_SCHEMA,
    SS_SCHEMA,
    SS_SOURCE_ROOT_SET,
    SS_UNSAFE_PATH,
    compose_schema_source_set,
    load_verified_schema_source,
    load_verified_schema_source_set,
    validate_manifest,
    validate_manifest_path,
    verify_manifest,
)
from tools.validate import load_document

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "schema-sources" / "uci" / "2.5" / "manifest.yaml"
UCI_26_MANIFEST_PATH = ROOT / "schema-sources" / "uci" / "2.6" / "manifest.yaml"


def synthetic_manifest(files: dict[str, bytes]) -> dict[str, object]:
    return {
        "manifest_version": "0.1",
        "id": "test-baseline",
        "schema_family": "uci",
        "schema_version": "2.5",
        "role": "baseline",
        "source": {
            "kind": "git",
            "repository": "https://example.test/uci.git",
            "revision": "a" * 40,
        },
        "root_schema": "root.xsd",
        "files": [
            {"path": path, "sha256": hashlib.sha256(data).hexdigest()}
            for path, data in sorted(files.items())
        ],
    }


def synthetic_extension(manifest_id: str, compatible_versions: list[str] | None = None) -> dict[str, object]:
    manifest = synthetic_manifest({"root.xsd": b"root"})
    manifest.update(
        id=manifest_id,
        schema_version="1.0",
        role="extension",
        compatible_baseline_versions=["2.5"] if compatible_versions is None else compatible_versions,
    )
    return manifest


def synthetic_contract(extension_ids: list[str] | None = None) -> dict[str, object]:
    contract = load_document(ROOT / "tests" / "valid" / "service-status.yaml")
    if extension_ids is None:
        contract["standards"].pop("uci_extension_schemas", None)
    else:
        contract["standards"]["uci_extension_schemas"] = extension_ids
    return contract


def test_checked_in_uci_25_manifest_validates() -> None:
    manifest, diagnostics = validate_manifest_path(MANIFEST_PATH)
    assert diagnostics == []
    assert manifest["manifest_version"] == "0.1"
    assert manifest["role"] == "baseline"
    assert manifest["schema_family"] == "uci"
    assert manifest["schema_version"] == "2.5"
    assert manifest["source"]["revision"] == "093610b7753944059360d3236770ab446d039556"
    assert sum(item["path"] == manifest["root_schema"] for item in manifest["files"]) == 1
    assert [item["path"] for item in manifest["files"]] == sorted(item["path"] for item in manifest["files"])


def test_checked_in_uci_26_manifest_validates() -> None:
    manifest, diagnostics = validate_manifest_path(UCI_26_MANIFEST_PATH)
    assert diagnostics == []
    assert manifest["manifest_version"] == "0.1"
    assert manifest["role"] == "baseline"
    assert manifest["schema_family"] == "uci"
    assert manifest["schema_version"] == "2.6"
    assert manifest["source"]["revision"] == "78eb61b6112c8bffa40820c33124b57787fc5bd9"
    assert sum(item["path"] == manifest["root_schema"] for item in manifest["files"]) == 1
    assert [item["path"] for item in manifest["files"]] == sorted(item["path"] for item in manifest["files"])


def test_root_not_in_files_is_rejected() -> None:
    manifest = synthetic_manifest({"other.xsd": b"other"})
    assert validate_manifest(manifest)[-1].code == SS_ROOT_SCHEMA


def test_duplicate_file_path_is_rejected() -> None:
    manifest = synthetic_manifest({"root.xsd": b"root"})
    manifest["files"].append(deepcopy(manifest["files"][0]))
    assert any(diagnostic.code == SS_DUPLICATE_FILE for diagnostic in validate_manifest(manifest))


def test_unsafe_root_path_is_rejected() -> None:
    manifest = synthetic_manifest({"root.xsd": b"root"})
    manifest["root_schema"] = "../root.xsd"
    assert validate_manifest(manifest)[0].code == SS_UNSAFE_PATH


def test_unsafe_file_paths_are_rejected() -> None:
    for path in ("../foo.xsd", "foo/../bar.xsd", "./foo.xsd", "foo\\bar.xsd", "C:/foo.xsd"):
        manifest = synthetic_manifest({"root.xsd": b"root"})
        manifest["files"][0]["path"] = path
        assert any(diagnostic.code == SS_UNSAFE_PATH for diagnostic in validate_manifest(manifest))


def test_invalid_sha256_is_structurally_rejected() -> None:
    manifest = synthetic_manifest({"root.xsd": b"root"})
    manifest["files"][0]["sha256"] = "not-a-digest"
    assert any(diagnostic.code == SS_SCHEMA for diagnostic in validate_manifest(manifest))


def test_manifest_parse_failure_uses_schema_code(tmp_path: Path) -> None:
    path = tmp_path / "manifest.yaml"
    path.write_text("{not valid", encoding="utf-8")
    _, diagnostics = validate_manifest_path(path)
    assert [diagnostic.code for diagnostic in diagnostics] == [SS_SCHEMA]


def test_unsorted_file_list_is_rejected() -> None:
    manifest = synthetic_manifest({"dependency.xsd": b"dependency", "root.xsd": b"root"})
    manifest["files"].reverse()
    assert any(diagnostic.code == SS_FILE_ORDER for diagnostic in validate_manifest(manifest))


def test_local_verification_accepts_exact_declared_subset(tmp_path: Path) -> None:
    files = {"root.xsd": b"root", "dependency.xsd": b"dependency"}
    for path, data in files.items():
        (tmp_path / path).write_bytes(data)
    (tmp_path / "unrelated.txt").write_text("ignored\n", encoding="utf-8")
    assert verify_manifest(synthetic_manifest(files), tmp_path) == []


def test_verified_source_retains_the_exact_digest_verified_bytes(tmp_path: Path) -> None:
    data = b"verified bytes"
    manifest = synthetic_manifest({"root.xsd": data})
    (tmp_path / "root.xsd").write_bytes(data)
    verified, diagnostics = load_verified_schema_source(manifest, tmp_path)
    assert diagnostics == []
    assert verified.files[0].data == data


def test_verified_loading_reads_each_manifest_file_once(tmp_path: Path, monkeypatch) -> None:
    files = {"dependency.xsd": b"dependency", "root.xsd": b"root"}
    for path, data in files.items():
        (tmp_path / path).write_bytes(data)
    calls: list[Path] = []
    original_read_bytes = Path.read_bytes

    def read_bytes_once(path: Path) -> bytes:
        calls.append(path)
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", read_bytes_once)
    _, diagnostics = load_verified_schema_source(synthetic_manifest(files), tmp_path)
    assert diagnostics == []
    assert len(calls) == len(files)


def test_verified_source_set_requires_exact_source_root_ids(tmp_path: Path) -> None:
    baseline = synthetic_manifest({"root.xsd": b"root"})
    extension = synthetic_extension("ext-a")
    schema_set, diagnostics = compose_schema_source_set(synthetic_contract(["ext-a"]), baseline, [extension])
    assert diagnostics == []
    _, diagnostics = load_verified_schema_source_set(schema_set, {baseline["id"]: tmp_path})
    assert [diagnostic.code for diagnostic in diagnostics] == [SS_SOURCE_ROOT_SET]
    assert any("missing source root for manifest 'ext-a'" in diagnostic.message for diagnostic in diagnostics)
    _, diagnostics = load_verified_schema_source_set(schema_set, {baseline["id"]: tmp_path, "ext-a": tmp_path, "extra": tmp_path})
    assert [diagnostic.code for diagnostic in diagnostics] == [SS_SOURCE_ROOT_SET]
    assert any("source root supplied for unselected manifest 'extra'" in diagnostic.message for diagnostic in diagnostics)


def test_verified_source_set_preserves_composed_extension_order(tmp_path: Path) -> None:
    baseline = synthetic_manifest({"root.xsd": b"baseline"})
    extension_a = synthetic_extension("ext-a")
    extension_b = synthetic_extension("ext-b")
    schema_set, diagnostics = compose_schema_source_set(synthetic_contract(["ext-b", "ext-a"]), baseline, [extension_a, extension_b])
    assert diagnostics == []
    roots = {"test-baseline": tmp_path / "baseline", "ext-a": tmp_path / "ext-a", "ext-b": tmp_path / "ext-b"}
    for manifest_id, root in roots.items():
        root.mkdir()
        (root / "root.xsd").write_bytes(b"baseline" if manifest_id == "test-baseline" else b"root")
    verified_set, diagnostics = load_verified_schema_source_set(schema_set, roots)
    assert diagnostics == []
    assert [source.manifest_id for source in verified_set.extensions] == ["ext-b", "ext-a"]


def test_local_verification_reports_tampered_bytes(tmp_path: Path) -> None:
    manifest = synthetic_manifest({"root.xsd": b"root"})
    (tmp_path / "root.xsd").write_bytes(b"tampered")
    diagnostics = verify_manifest(manifest, tmp_path)
    assert len(diagnostics) == 1
    assert diagnostics[0].code == SS_HASH_MISMATCH
    assert "expected sha256" in diagnostics[0].message
    assert "actual   sha256" in diagnostics[0].message


def test_local_verification_reports_missing_file(tmp_path: Path) -> None:
    diagnostics = verify_manifest(synthetic_manifest({"root.xsd": b"root"}), tmp_path)
    assert [diagnostic.code for diagnostic in diagnostics] == [SS_FILE_MISSING]
    assert [diagnostic.message for diagnostic in diagnostics] == ["file listed by manifest is missing"]


def test_local_verification_reports_file_outside_source_root(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.xsd"
    outside.write_bytes(b"outside")
    (tmp_path / "root.xsd").symlink_to(outside)
    diagnostics = verify_manifest(synthetic_manifest({"root.xsd": b"outside"}), tmp_path)
    assert [diagnostic.code for diagnostic in diagnostics] == [SS_FILE_OUTSIDE_ROOT]


def test_local_verification_reports_file_read_error(tmp_path: Path, monkeypatch) -> None:
    manifest = synthetic_manifest({"root.xsd": b"root"})
    path = tmp_path / "root.xsd"
    path.write_bytes(b"root")

    def fail_read_bytes(_: Path) -> bytes:
        raise OSError("read denied")

    monkeypatch.setattr(Path, "read_bytes", fail_read_bytes)
    diagnostics = verify_manifest(manifest, tmp_path)
    assert [diagnostic.code for diagnostic in diagnostics] == [SS_FILE_READ]


def test_extension_requires_compatible_baseline_versions() -> None:
    manifest = synthetic_extension("ext-a")
    del manifest["compatible_baseline_versions"]
    assert any("required property" in diagnostic.message for diagnostic in validate_manifest(manifest))


def test_baseline_forbids_compatible_baseline_versions() -> None:
    manifest = synthetic_manifest({"root.xsd": b"root"})
    manifest["compatible_baseline_versions"] = ["2.5"]
    assert validate_manifest(manifest)


def test_extension_compatibility_list_must_be_nonempty_and_unique() -> None:
    for versions in ([], ["2.5", "2.5"]):
        assert validate_manifest(synthetic_extension("ext-a", versions))


def test_composition_accepts_matching_baseline_without_extensions() -> None:
    schema_set, diagnostics = compose_schema_source_set(synthetic_contract(), synthetic_manifest({"root.xsd": b"root"}), [])
    assert diagnostics == []
    assert schema_set is not None
    assert schema_set.extensions == ()


def test_composition_rejects_invalid_contract_before_selection() -> None:
    contract = synthetic_contract()
    contract["standards"].pop("uci_schema_version")
    schema_set, diagnostics = compose_schema_source_set(contract, synthetic_manifest({"root.xsd": b"root"}), [])
    assert schema_set is None
    assert any(diagnostic.code == "SC_SCHEMA" and "uci_schema_version" in diagnostic.message for diagnostic in diagnostics)


def test_composition_preserves_duplicate_contract_function_code() -> None:
    contract = synthetic_contract()
    contract["functions"].append(deepcopy(contract["functions"][0]))
    _, diagnostics = compose_schema_source_set(contract, synthetic_manifest({"root.xsd": b"root"}), [])
    assert [diagnostic.code for diagnostic in diagnostics] == ["SC_DUPLICATE_FUNCTION"]


def test_composition_rejects_baseline_version_mismatch_and_wrong_role() -> None:
    manifest = synthetic_manifest({"root.xsd": b"root"})
    manifest["schema_version"] = "2.6"
    _, diagnostics = compose_schema_source_set(synthetic_contract(), manifest, [])
    assert any(diagnostic.code == SS_BASELINE_SELECTION and "must match contract UCI baseline" in diagnostic.message for diagnostic in diagnostics)
    manifest["schema_version"] = "1.0"
    manifest["role"] = "extension"
    manifest["compatible_baseline_versions"] = ["2.5"]
    _, diagnostics = compose_schema_source_set(synthetic_contract(), manifest, [])
    assert any(diagnostic.code == SS_BASELINE_SELECTION and "must be 'baseline'" in diagnostic.message for diagnostic in diagnostics)


def test_composition_rejects_baseline_wrong_family(monkeypatch) -> None:
    manifest = synthetic_manifest({"root.xsd": b"root"})
    manifest["schema_family"] = "other"
    monkeypatch.setattr(schema_sources, "validate_manifest", lambda _: [])
    _, diagnostics = compose_schema_source_set(synthetic_contract(), manifest, [])
    assert [diagnostic.code for diagnostic in diagnostics] == [SS_BASELINE_SELECTION]


def test_composition_rejects_extension_wrong_family(monkeypatch) -> None:
    extension = synthetic_extension("ext-a")
    extension["schema_family"] = "other"
    monkeypatch.setattr(schema_sources, "validate_manifest", lambda _: [])
    _, diagnostics = compose_schema_source_set(synthetic_contract(["ext-a"]), synthetic_manifest({"root.xsd": b"root"}), [extension])
    assert [diagnostic.code for diagnostic in diagnostics] == [SS_EXTENSION_MAPPING]


def test_composition_selects_extensions_in_contract_declaration_order() -> None:
    extensions = [synthetic_extension("ext-c"), synthetic_extension("ext-a"), synthetic_extension("ext-b")]
    schema_set, diagnostics = compose_schema_source_set(synthetic_contract(["ext-a", "ext-b", "ext-c"]), synthetic_manifest({"root.xsd": b"root"}), extensions)
    assert diagnostics == []
    assert [manifest["id"] for manifest in schema_set.extensions] == ["ext-a", "ext-b", "ext-c"]


def test_composition_rejects_missing_undeclared_and_exact_id_mismatches() -> None:
    _, diagnostics = compose_schema_source_set(synthetic_contract(["ext-a", "ext-b"]), synthetic_manifest({"root.xsd": b"root"}), [synthetic_extension("Ext-A")])
    messages = [diagnostic.message for diagnostic in diagnostics]
    assert [diagnostic.code for diagnostic in diagnostics] == [SS_EXTENSION_MAPPING] * 3
    assert any("missing declared extension manifest id 'ext-a'" in message for message in messages)
    assert any("missing declared extension manifest id 'ext-b'" in message for message in messages)
    assert any("undeclared extension manifest id 'Ext-A'" in message for message in messages)


def test_composition_rejects_duplicate_wrong_role_and_incompatible_extensions() -> None:
    wrong_role = synthetic_manifest({"root.xsd": b"root"})
    wrong_role["id"] = "ext-a"
    incompatible = synthetic_extension("ext-b", ["2.6"])
    _, diagnostics = compose_schema_source_set(synthetic_contract(["ext-a", "ext-b"]), synthetic_manifest({"root.xsd": b"root"}), [wrong_role, synthetic_extension("ext-a"), incompatible])
    messages = [diagnostic.message for diagnostic in diagnostics]
    assert [diagnostic.code for diagnostic in diagnostics] == [SS_MANIFEST_ID_COLLISION, SS_EXTENSION_MAPPING, SS_EXTENSION_COMPATIBILITY]
    assert any("duplicate supplied manifest id 'ext-a'" in message for message in messages)
    assert any("must have role 'extension'" in message for message in messages)
    assert any("not compatible with UCI baseline version '2.5'" in message for message in messages)


def test_composition_rejects_extension_id_collision_with_baseline() -> None:
    baseline = synthetic_manifest({"root.xsd": b"root"})
    extension = synthetic_extension("test-baseline")
    _, diagnostics = compose_schema_source_set(synthetic_contract(["test-baseline"]), baseline, [extension])
    assert [diagnostic.code for diagnostic in diagnostics] == [SS_MANIFEST_ID_COLLISION]
    assert any("collides with baseline manifest id" in diagnostic.message for diagnostic in diagnostics)


def test_schema_source_diagnostic_codes_are_unique_and_well_formed() -> None:
    assert len(SCHEMA_SOURCE_DIAGNOSTIC_CODES) == 14
    assert all(re.fullmatch(r"SS_[A-Z0-9_]+", code) for code in SCHEMA_SOURCE_DIAGNOSTIC_CODES)
