#!/usr/bin/env python3
"""Resolve OMS Message exchanges from manifest-verified local UCI XSD bytes."""
from __future__ import annotations
import argparse
from dataclasses import dataclass, replace
from io import BytesIO
from pathlib import Path
import re
from typing import Any
from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException
try:
    from tools.schema_sources import VerifiedSchemaSourceSet, compose_schema_source_set, load_verified_schema_source_set, validate_manifest_path
    from tools.validate import validate_document
    from tools.yaml_support import YamlInputError, load_path
except ModuleNotFoundError:
    from schema_sources import VerifiedSchemaSourceSet, compose_schema_source_set, load_verified_schema_source_set, validate_manifest_path
    from validate import validate_document
    from yaml_support import YamlInputError, load_path

XSD_NAMESPACE = "http://www.w3.org/2001/XMLSchema"
XSD_SCHEMA = f"{{{XSD_NAMESPACE}}}schema"
XSD_ELEMENT = f"{{{XSD_NAMESPACE}}}element"
XSD_COMPLEX_TYPE = f"{{{XSD_NAMESPACE}}}complexType"
XSD_SIMPLE_TYPE = f"{{{XSD_NAMESPACE}}}simpleType"
XSD_ANNOTATION = f"{{{XSD_NAMESPACE}}}annotation"
XSD_DOCUMENTATION = f"{{{XSD_NAMESPACE}}}documentation"
PRIMITIVE_PREFIX = "UCI_PRIMITIVE:"
QNAME_PATTERN = re.compile(r"^(?:(?P<prefix>[A-Za-z_][A-Za-z0-9_.-]*):)?(?P<local>[A-Za-z_][A-Za-z0-9_.-]*)$")

@dataclass(frozen=True)
class UciTypeDeclaration:
    local_name: str
    namespace: str
    expanded_name: str
    kind: str
    manifest_id: str
    source_path: str

@dataclass(frozen=True)
class UciMessageDefinition:
    local_name: str
    namespace: str
    expanded_name: str
    primitive: str
    lexical_type_name: str
    type_expanded_name: str
    type_declaration: UciTypeDeclaration | None
    manifest_id: str
    source_path: str

@dataclass(frozen=True)
class ParsedXsdDocument:
    target_namespace: str
    # Namespace bindings in scope on the document root only.
    namespace_bindings: tuple[tuple[str, str], ...]
    messages: tuple[UciMessageDefinition, ...]
    type_declarations: tuple[UciTypeDeclaration, ...]
    manifest_id: str
    source_path: str

@dataclass(frozen=True)
class ResolvedOmsExchange:
    function_id: str
    exchange_id: str
    message: str
    expanded_name: str
    primitive: str
    message_type_expanded_name: str
    manifest_id: str
    source_path: str

class UciResolverError(Exception):
    """Expected fail-closed UCI resolver input or resolution failure."""


class UciResolutionPreparationError(UciResolverError):
    """Expected manifest-selection failure with a CLI presentation stage."""

    def __init__(self, stage: str, diagnostics: list[Any]):
        self.stage = stage
        self.diagnostics = tuple(str(item) for item in diagnostics)
        super().__init__(f"{stage} failed:\n" + "\n".join(f"  {item}" for item in self.diagnostics))

def _context(manifest_id: str, source_path: str, local_name: str) -> str:
    return f"manifest {manifest_id!r}, file {source_path!r}, message {local_name!r}"

def resolve_lexical_qname(lexical_name: str | None, namespace_bindings: dict[str, str], context: str) -> str:
    """Resolve a lexical XSD QName using the containing element's in-scope bindings."""
    if lexical_name is None or not lexical_name.strip():
        raise UciResolverError(f"missing or empty type QName in {context}")
    match = QNAME_PATTERN.fullmatch(lexical_name)
    if not match:
        raise UciResolverError(f"malformed type QName {lexical_name!r} in {context}")
    prefix = match.group("prefix") or ""
    if prefix not in namespace_bindings:
        if not prefix:
            return match.group("local")
        raise UciResolverError(f"unknown namespace prefix {(prefix or 'default')!r} for type QName {lexical_name!r} in {context}")
    namespace = namespace_bindings[prefix]
    return f"{{{namespace}}}{match.group('local')}"

def _primitive_from_element(element: Any, manifest_id: str, source_path: str) -> str | None:
    local_name = element.get("name", "<unnamed>")
    values = [(item.text or "").strip()[len(PRIMITIVE_PREFIX):].strip() for item in element.findall(f"{XSD_ANNOTATION}/{XSD_DOCUMENTATION}") if (item.text or "").strip().startswith(PRIMITIVE_PREFIX)]
    if len(values) > 1:
        raise UciResolverError(f"duplicate UCI_PRIMITIVE metadata in {_context(manifest_id, source_path, local_name)}")
    if not values:
        return None
    primitive = values[0][:-1] if values[0].endswith(".") else values[0]
    if not primitive:
        raise UciResolverError(f"empty UCI_PRIMITIVE metadata in {_context(manifest_id, source_path, local_name)}")
    return primitive

def parse_uci_schema_document(data: bytes, manifest_id: str, source_path: str) -> ParsedXsdDocument:
    """Parse one verified XSD snapshot and index direct global declarations."""
    try:
        pending_bindings: dict[str, str] = {}
        scope_stack: list[dict[str, str]] = []
        root_bindings: dict[str, str] | None = None
        element_scopes: dict[int, dict[str, str]] = {}
        events = ElementTree.iterparse(BytesIO(data), events=("start-ns", "start", "end"))
        for event, value in events:
            if event == "start-ns":
                prefix, namespace = value
                pending_bindings[prefix or ""] = namespace
            elif event == "start":
                scope = dict(scope_stack[-1]) if scope_stack else {}
                scope.update(pending_bindings)
                pending_bindings = {}
                scope_stack.append(scope)
                element_scopes[id(value)] = scope
                if root_bindings is None:
                    root_bindings = dict(scope)
            else:
                scope_stack.pop()
        root = events.root
    except (DefusedXmlException, ElementTree.ParseError) as exc:
        raise UciResolverError(f"could not parse manifest {manifest_id!r}, file {source_path!r}: {exc}") from exc
    if root.tag != XSD_SCHEMA:
        raise UciResolverError(f"manifest {manifest_id!r}, file {source_path!r}: document root must be xs:schema")
    namespace = root.get("targetNamespace")
    if not namespace:
        raise UciResolverError(f"manifest {manifest_id!r}, file {source_path!r}: xs:schema must declare targetNamespace")
    messages: list[UciMessageDefinition] = []
    declarations: list[UciTypeDeclaration] = []
    for child in root:
        if child.tag in (XSD_COMPLEX_TYPE, XSD_SIMPLE_TYPE) and child.get("name"):
            name = child.get("name")
            declarations.append(UciTypeDeclaration(name, namespace, f"{{{namespace}}}{name}", "complex" if child.tag == XSD_COMPLEX_TYPE else "simple", manifest_id, source_path))
        if child.tag != XSD_ELEMENT or not child.get("name"):
            continue
        primitive = _primitive_from_element(child, manifest_id, source_path)
        if primitive is None:
            continue
        name = child.get("name")
        context = _context(manifest_id, source_path, name)
        lexical = child.get("type")
        messages.append(UciMessageDefinition(name, namespace, f"{{{namespace}}}{name}", primitive, lexical or "", resolve_lexical_qname(lexical, element_scopes[id(child)], context), None, manifest_id, source_path))
    return ParsedXsdDocument(namespace, tuple(sorted((root_bindings or {}).items())), tuple(messages), tuple(declarations), manifest_id, source_path)

def parse_uci_schema_bytes(data: bytes, manifest_id: str, source_path: str) -> list[UciMessageDefinition]:
    return list(parse_uci_schema_document(data, manifest_id, source_path).messages)

def load_message_definitions(verified_schema_source_set: VerifiedSchemaSourceSet) -> list[UciMessageDefinition]:
    """Parse only immutable verified bytes and resolve every message type globally."""
    documents = [parse_uci_schema_document(file.data, source.manifest_id, file.path) for source in (verified_schema_source_set.baseline, *verified_schema_source_set.extensions) for file in source.files]
    index: dict[str, list[UciTypeDeclaration]] = {}
    for declaration in (item for document in documents for item in document.type_declarations):
        index.setdefault(declaration.expanded_name, []).append(declaration)
    definitions: list[UciMessageDefinition] = []
    for message in (item for document in documents for item in document.messages):
        candidates = index.get(message.type_expanded_name, [])
        if not candidates:
            raise UciResolverError(f"unknown global UCI type {message.type_expanded_name} referenced by {_context(message.manifest_id, message.source_path, message.local_name)}")
        if len(candidates) > 1:
            descriptions = sorted(f"{item.kind} ({item.manifest_id}:{item.source_path})" for item in candidates)
            raise UciResolverError(f"ambiguous global UCI type {message.type_expanded_name} referenced by {_context(message.manifest_id, message.source_path, message.local_name)}\ncandidates:\n" + "\n".join(f"  - {item}" for item in descriptions))
        definitions.append(replace(message, type_declaration=candidates[0]))
    return definitions

def resolve_contract_messages(contract: Any, verified_schema_source_set: VerifiedSchemaSourceSet) -> list[ResolvedOmsExchange]:
    diagnostics = validate_document(contract)
    if diagnostics:
        raise UciResolverError("contract validation failed:\n" + "\n".join(f"  {item}" for item in diagnostics))
    definitions = load_message_definitions(verified_schema_source_set)
    resolved: list[ResolvedOmsExchange] = []
    for function in contract["functions"]:
        for exchange in function["exchanges"]:
            if exchange["kind"] != "oms_message":
                continue
            message = exchange["message"]
            candidates = [item for item in definitions if item.local_name == message]
            context = f"function {function['id']!r}, exchange {exchange['id']!r}"
            if not candidates:
                raise UciResolverError(f"unknown UCI message {message!r} ({context})")
            if len(candidates) > 1:
                descriptions = sorted(f"{item.expanded_name} ({item.manifest_id}:{item.source_path})" for item in candidates)
                raise UciResolverError(f"ambiguous UCI message {message!r} ({context})\ncandidates:\n" + "\n".join(f"  - {item}" for item in descriptions))
            item = candidates[0]
            resolved.append(ResolvedOmsExchange(function["id"], exchange["id"], message, item.expanded_name, item.primitive, item.type_expanded_name, item.manifest_id, item.source_path))
    return resolved

def _load_contract(path: Path) -> Any:
    try:
        return load_path(path)
    except YamlInputError as exc:
        raise UciResolverError(f"could not parse contract {path}: {exc}") from exc


def prepare_resolution(
    contract_path: Path,
    baseline_manifest_path: Path,
    baseline_source_root: Path,
    extensions: list[tuple[Path, Path]],
) -> tuple[Any, VerifiedSchemaSourceSet, list[ResolvedOmsExchange]]:
    """Load, validate, verify, and resolve a contract using selected UCI sources.

    This is shared orchestration for non-normative reference consumers.  Schema
    parsing remains strictly downstream of manifest byte verification.
    """
    contract = _load_contract(contract_path)
    baseline, diagnostics = validate_manifest_path(baseline_manifest_path.resolve())
    extension_results = [validate_manifest_path(manifest.resolve()) for manifest, _ in extensions]
    diagnostics.extend(item for _, items in extension_results for item in items)
    if diagnostics:
        raise UciResolutionPreparationError("schema-source manifests", diagnostics)
    schema_set, diagnostics = compose_schema_source_set(contract, baseline, [item for item, _ in extension_results])
    if diagnostics:
        raise UciResolutionPreparationError("schema-source set", diagnostics)
    roots = {baseline["id"]: baseline_source_root}
    roots.update({manifest["id"]: root for (manifest, _), (_, root) in zip(extension_results, extensions)})
    verified, diagnostics = load_verified_schema_source_set(schema_set, roots)
    if diagnostics:
        raise UciResolverError("manifest verification failed:\n" + "\n".join(f"  {item}" for item in diagnostics))
    return contract, verified, resolve_contract_messages(contract, verified)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    resolve = commands.add_parser("resolve", help="resolve OMS Messages from verified local XSD files")
    resolve.add_argument("--contract", type=Path, required=True)
    resolve.add_argument("--baseline-manifest", type=Path, required=True)
    resolve.add_argument("--baseline-source-root", type=Path, required=True)
    resolve.add_argument("--extension", nargs=2, action="append", metavar=("MANIFEST", "SOURCE_ROOT"), default=[])
    args = parser.parse_args(argv)
    try:
        _, _, resolved = prepare_resolution(
            args.contract, args.baseline_manifest, args.baseline_source_root,
            [(Path(manifest), Path(root)) for manifest, root in args.extension],
        )
    except UciResolutionPreparationError as exc:
        print(f"FAIL {exc.stage}", *(f"  {item}" for item in exc.diagnostics), sep="\n")
        return 1
    except UciResolverError as exc:
        print(f"FAIL {exc}")
        return 1
    print("OK resolved OMS messages")
    for item in resolved:
        print(f"  {item.function_id}/{item.exchange_id}:\n    {item.message}\n    primitive: {item.primitive}\n    qname: {item.expanded_name}\n    type: {item.message_type_expanded_name}\n    source: {item.manifest_id}:{item.source_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
