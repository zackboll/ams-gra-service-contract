import hashlib
from copy import deepcopy
from pathlib import Path

from tools.schema_sources import validate_manifest, validate_manifest_path, verify_manifest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "schema-sources" / "uci" / "2.5" / "manifest.yaml"


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


def test_checked_in_uci_25_manifest_validates() -> None:
    manifest, diagnostics = validate_manifest_path(MANIFEST_PATH)
    assert diagnostics == []
    assert manifest["manifest_version"] == "0.1"


def test_root_not_in_files_is_rejected() -> None:
    manifest = synthetic_manifest({"other.xsd": b"other"})
    assert "must appear exactly once" in str(validate_manifest(manifest)[-1])


def test_duplicate_file_path_is_rejected() -> None:
    manifest = synthetic_manifest({"root.xsd": b"root"})
    manifest["files"].append(deepcopy(manifest["files"][0]))
    assert any("must be unique" in diagnostic.message for diagnostic in validate_manifest(manifest))


def test_unsafe_paths_are_rejected() -> None:
    for path in ("../foo.xsd", "foo/../bar.xsd", "./foo.xsd", "foo\\bar.xsd", "C:/foo.xsd"):
        manifest = synthetic_manifest({"root.xsd": b"root"})
        manifest["files"][0]["path"] = path
        assert any("safe relative POSIX" in diagnostic.message for diagnostic in validate_manifest(manifest))


def test_invalid_sha256_is_structurally_rejected() -> None:
    manifest = synthetic_manifest({"root.xsd": b"root"})
    manifest["files"][0]["sha256"] = "not-a-digest"
    assert any("does not match" in diagnostic.message for diagnostic in validate_manifest(manifest))


def test_unsorted_file_list_is_rejected() -> None:
    manifest = synthetic_manifest({"dependency.xsd": b"dependency", "root.xsd": b"root"})
    manifest["files"].reverse()
    assert any("sorted lexicographically" in diagnostic.message for diagnostic in validate_manifest(manifest))


def test_local_verification_accepts_exact_declared_subset(tmp_path: Path) -> None:
    files = {"root.xsd": b"root", "dependency.xsd": b"dependency"}
    for path, data in files.items():
        (tmp_path / path).write_bytes(data)
    (tmp_path / "unrelated.txt").write_text("ignored\n", encoding="utf-8")
    assert verify_manifest(synthetic_manifest(files), tmp_path) == []


def test_local_verification_reports_tampered_bytes(tmp_path: Path) -> None:
    manifest = synthetic_manifest({"root.xsd": b"root"})
    (tmp_path / "root.xsd").write_bytes(b"tampered")
    diagnostics = verify_manifest(manifest, tmp_path)
    assert len(diagnostics) == 1
    assert "expected sha256" in diagnostics[0].message
    assert "actual   sha256" in diagnostics[0].message


def test_local_verification_reports_missing_file(tmp_path: Path) -> None:
    diagnostics = verify_manifest(synthetic_manifest({"root.xsd": b"root"}), tmp_path)
    assert [diagnostic.message for diagnostic in diagnostics] == ["file listed by manifest is missing"]
