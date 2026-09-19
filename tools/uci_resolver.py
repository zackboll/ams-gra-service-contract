#!/usr/bin/env python3
"""Resolve OMS Message exchanges from manifest-verified local UCI XSD bytes."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException
import yaml

try:
    from tools.schema_sources import VerifiedSchemaSourceSet, compose_schema_source_set, load_verified_schema_source_set, validate_manifest_path
    from tools.validate import validate_document
except ModuleNotFoundError:  # Support direct execution as ``python tools/uci_resolver.py``.
    from schema_sources import VerifiedSchemaSourceSet, compose_schema_source_set, load_verified_schema_source_set, validate_manifest_path
    from validate import validate_document


XSD_NAMESPACE = "http://www.w3.org/2001/XMLSchema"
XSD_SCHEMA = f"{{{XSD_NAMESPACE}}}schema"
XSD_ELEMENT = f"{{{XSD_NAMESPACE}}}element"
XSD_ANNOTATION = f"{{{XSD_NAMESPACE}}}annotation"
XSD_DOCUMENTATION = f"{{{XSD_NAMESPACE}}}documentation"
PRIMITIVE_PREFIX = "UCI_PRIMITIVE:"


@dataclass(frozen=True)
class UciMessageDefinition:
    local_name: str
    namespace: str
    expanded_name: str
    primitive: str
    type_name: str | None
    manifest_id: str
    source_path: str


@dataclass(frozen=True)
class ResolvedOmsExchange:
    function_id: str
    exchange_id: str
    message: str
    expanded_name: str
    primitive: str
    manifest_id: str
    source_path: str


class UciResolverError(Exception):
    """Expected fail-closed UCI resolver input or resolution failure."""


def _context(manifest_id: str, source_path: str, local_name: str) -> str:
    return f"manifest {manifest_id!r}, file {source_path!r}, message {local_name!r}"


def _primitive_from_element(element: Any, manifest_id: str, source_path: str) -> str | None:
    local_name = element.get("name", "<unnamed>")
    values = [
        (documentation.text or "").strip()[len(PRIMITIVE_PREFIX) :].strip()
        for documentation in element.findall(f"{XSD_ANNOTATION}/{XSD_DOCUMENTATION}")
        if (documentation.text or "").strip().startswith(PRIMITIVE_PREFIX)
    ]
    if len(values) > 1:
        raise UciResolverError(f"duplicate UCI_PRIMITIVE metadata in {_context(manifest_id, source_path, local_name)}")
    if not values:
        return None
    primitive = values[0]
    if not primitive:
        raise UciResolverError(f"empty UCI_PRIMITIVE metadata in {_context(manifest_id, source_path, local_name)}")
    primitive = primitive[:-1] if primitive.endswith(".") else primitive
    if not primitive:
        raise UciResolverError(f"empty UCI_PRIMITIVE metadata in {_context(manifest_id, source_path, local_name)}")
    return primitive


def parse_uci_schema_bytes(data: bytes, manifest_id: str, source_path: str) -> list[UciMessageDefinition]:
    """Parse direct global UCI message declarations from one verified XSD document."""
    try:
        root = ElementTree.fromstring(data)
    except (DefusedXmlException, ElementTree.ParseError) as exc:
        raise UciResolverError(f"could not parse manifest {manifest_id!r}, file {source_path!r}: {exc}") from exc
    if root.tag != XSD_SCHEMA:
        raise UciResolverError(f"manifest {manifest_id!r}, file {source_path!r}: document root must be xs:schema")
    namespace = root.get("targetNamespace")
    if not namespace:
        raise UciResolverError(f"manifest {manifest_id!r}, file {source_path!r}: xs:schema must declare targetNamespace")

    definitions: list[UciMessageDefinition] = []
    for element in root.findall(XSD_ELEMENT):
        local_name = element.get("name")
        if not local_name:
            continue
        primitive = _primitive_from_element(element, manifest_id, source_path)
        if primitive is None:
            continue
        definitions.append(
            UciMessageDefinition(
                local_name=local_name,
                namespace=namespace,
                expanded_name=f"{{{namespace}}}{local_name}",
                primitive=primitive,
                type_name=element.get("type"),
                manifest_id=manifest_id,
                source_path=source_path,
            )
        )
    return definitions


def load_message_definitions(verified_schema_source_set: VerifiedSchemaSourceSet) -> list[UciMessageDefinition]:
    """Parse only immutable bytes retained by verified schema-source snapshots."""
    definitions: list[UciMessageDefinition] = []
    for source in (verified_schema_source_set.baseline, *verified_schema_source_set.extensions):
        for file in source.files:
            definitions.extend(parse_uci_schema_bytes(file.data, source.manifest_id, file.path))
    return definitions


def resolve_contract_messages(contract: Any, verified_schema_source_set: VerifiedSchemaSourceSet) -> list[ResolvedOmsExchange]:
    """Resolve OMS exchanges in function/exchange declaration order."""
    diagnostics = validate_document(contract)
    if diagnostics:
        raise UciResolverError("contract validation failed:\n" + "\n".join(f"  {diagnostic}" for diagnostic in diagnostics))
    definitions = load_message_definitions(verified_schema_source_set)
    resolved: list[ResolvedOmsExchange] = []
    for function in contract["functions"]:
        for exchange in function["exchanges"]:
            if exchange["kind"] != "oms_message":
                continue
            message = exchange["message"]
            candidates = [definition for definition in definitions if definition.local_name == message]
            context = f"function {function['id']!r}, exchange {exchange['id']!r}"
            if not candidates:
                raise UciResolverError(f"unknown UCI message {message!r} ({context})")
            if len(candidates) > 1:
                descriptions = sorted(
                    f"{candidate.expanded_name} ({candidate.manifest_id}:{candidate.source_path})" for candidate in candidates
                )
                raise UciResolverError(
                    f"ambiguous UCI message {message!r} ({context})\ncandidates:\n"
                    + "\n".join(f"  - {description}" for description in descriptions)
                )
            candidate = candidates[0]
            resolved.append(
                ResolvedOmsExchange(function["id"], exchange["id"], message, candidate.expanded_name,
                                    candidate.primitive, candidate.manifest_id, candidate.source_path)
            )
    return resolved


def _load_contract(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as stream:
            return yaml.safe_load(stream)
    except (OSError, yaml.YAMLError) as exc:
        raise UciResolverError(f"could not parse contract {path}: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    resolve = commands.add_parser("resolve", help="resolve OMS Messages from verified local XSD files")
    resolve.add_argument("--contract", type=Path, required=True)
    resolve.add_argument("--baseline-manifest", type=Path, required=True)
    resolve.add_argument("--baseline-source-root", type=Path, required=True)
    resolve.add_argument("--extension", nargs=2, action="append", metavar=("MANIFEST", "SOURCE_ROOT"), default=[])
    args = parser.parse_args(argv)

    contract = _load_contract(args.contract)
    baseline, diagnostics = validate_manifest_path(args.baseline_manifest.resolve())
    extension_results = [validate_manifest_path(Path(manifest).resolve()) for manifest, _ in args.extension]
    diagnostics.extend(diagnostic for _, manifest_diagnostics in extension_results for diagnostic in manifest_diagnostics)
    if diagnostics:
        print("FAIL schema-source manifests")
        for diagnostic in diagnostics:
            print(f"  {diagnostic}")
        return 1
    schema_source_set, diagnostics = compose_schema_source_set(contract, baseline, [manifest for manifest, _ in extension_results])
    if diagnostics:
        print("FAIL schema-source set")
        for diagnostic in diagnostics:
            print(f"  {diagnostic}")
        return 1
    roots = {baseline["id"]: args.baseline_source_root}
    roots.update({manifest["id"]: Path(source_root) for (manifest, _), (_, source_root) in zip(extension_results, args.extension)})
    try:
        verified_schema_source_set, diagnostics = load_verified_schema_source_set(schema_source_set, roots)
        if diagnostics:
            raise UciResolverError("manifest verification failed:\n" + "\n".join(f"  {diagnostic}" for diagnostic in diagnostics))
        resolved = resolve_contract_messages(contract, verified_schema_source_set)
    except UciResolverError as exc:
        print(f"FAIL {exc}")
        return 1
    print("OK resolved OMS messages")
    for exchange in resolved:
        print(f"  {exchange.function_id}/{exchange.exchange_id}:")
        print(f"    {exchange.message}")
        print(f"    primitive: {exchange.primitive}")
        print(f"    qname: {exchange.expanded_name}")
        print(f"    source: {exchange.manifest_id}:{exchange.source_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
