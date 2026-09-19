#!/usr/bin/env python3
"""Generate a non-normative Inputs/Outputs projection from a resolved contract."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

try:
    from tools.uci_resolver import ResolvedOmsExchange, UciResolverError, prepare_resolution
except ModuleNotFoundError:
    from uci_resolver import ResolvedOmsExchange, UciResolverError, prepare_resolution


@dataclass(frozen=True)
class ProjectedExchange:
    exchange_id: str
    kind: str
    direction: str
    mandate: str
    timing_kind: str
    exchange_name: str
    information: str
    nominal: float | None
    maximum: float | None
    appendix_c_mapping: str | None
    reference: str | None
    topic: str | None
    operational_attribute: str | None
    subscription_group: str | None
    protocol: str | None
    data_type: str | None
    data_format: str | None
    sharing_pattern: str | None
    uci_primitive: str | None
    message_qname: str | None
    message_type_qname: str | None
    schema_manifest_id: str | None
    schema_source_path: str | None


@dataclass(frozen=True)
class ProjectedFunction:
    function_id: str
    function_name: str
    category: str
    applicability: str
    not_applicable_reason: str | None
    exchanges: tuple[ProjectedExchange, ...]


@dataclass(frozen=True)
class ProjectedInputsOutputs:
    functions: tuple[ProjectedFunction, ...]


class InputsOutputsProjectionError(Exception):
    """Expected fail-closed projection error."""


def _resolved_index(contract: dict[str, Any], resolved: list[ResolvedOmsExchange]) -> dict[tuple[str, str], ResolvedOmsExchange]:
    oms_messages = {(function["id"], exchange["id"]): exchange["message"] for function in contract["functions"] for exchange in function["exchanges"] if exchange["kind"] == "oms_message"}
    index: dict[tuple[str, str], ResolvedOmsExchange] = {}
    for item in resolved:
        key = (item.function_id, item.exchange_id)
        if key not in oms_messages:
            raise InputsOutputsProjectionError(f"resolved OMS exchange does not exist in contract: {key[0]!r}/{key[1]!r}")
        if key in index:
            raise InputsOutputsProjectionError(f"ambiguous OMS resolution for contract exchange: {key[0]!r}/{key[1]!r}")
        if item.message != oms_messages[key]:
            raise InputsOutputsProjectionError(f"OMS resolution message mismatch for contract exchange: {key[0]!r}/{key[1]!r}; contract message {oms_messages[key]!r}, resolved message {item.message!r}")
        index[key] = item
    missing = oms_messages.keys() - index.keys()
    if missing:
        function_id, exchange_id = sorted(missing)[0]
        raise InputsOutputsProjectionError(f"missing OMS resolution for contract exchange: {function_id!r}/{exchange_id!r}")
    return index


def _information(exchange: dict[str, Any]) -> str:
    if exchange["kind"] == "oms_message":
        values = [exchange["topic"]]
        for key in ("operational_attribute", "subscription_group"):
            if key in exchange:
                values.append(f"[{exchange[key]}]")
        return " ".join(values)
    if exchange["kind"] == "data_transfer":
        return f"{exchange['protocol']} [{exchange['data_type']}, {exchange['data_format']}, {exchange['sharing_pattern']}]"
    return exchange.get("details", "")


def project_inputs_outputs(contract: dict[str, Any], resolved: list[ResolvedOmsExchange]) -> ProjectedInputsOutputs:
    """Construct a contract-order-preserving semantic projection."""
    index = _resolved_index(contract, resolved)
    functions: list[ProjectedFunction] = []
    for function in contract["functions"]:
        exchanges: list[ProjectedExchange] = []
        for exchange in function["exchanges"]:
            timing = exchange["timing"]
            item = index.get((function["id"], exchange["id"]))
            exchanges.append(ProjectedExchange(
                exchange["id"], exchange["kind"], exchange["direction"], exchange["mandate"], timing["kind"],
                exchange["message"] if exchange["kind"] == "oms_message" else exchange["name"], _information(exchange),
                timing.get("nominal_response_seconds", timing.get("nominal_rate_hz")),
                timing.get("max_response_seconds", timing.get("max_rate_hz")), exchange.get("appendix_c_mapping"),
                exchange.get("reference"), exchange.get("topic"), exchange.get("operational_attribute"),
                exchange.get("subscription_group"), exchange.get("protocol"), exchange.get("data_type"),
                exchange.get("data_format"), exchange.get("sharing_pattern"), item.primitive if item else None,
                item.expanded_name if item else None, item.message_type_expanded_name if item else None,
                item.manifest_id if item else None, item.source_path if item else None,
            ))
        functions.append(ProjectedFunction(function["id"], function["name"], function["category"], function["applicability"], function.get("not_applicable_reason"), tuple(exchanges)))
    return ProjectedInputsOutputs(tuple(functions))


def _cell(value: object | None) -> str:
    return "" if value is None else str(value).replace("\n", " ").replace("|", "\\|")


def _timing_value(exchange: ProjectedExchange, value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:g} {'Hz' if exchange.timing_kind == 'periodic' else 's'}"


def render_markdown(projection: ProjectedInputsOutputs) -> str:
    """Render deterministic human-readable tables; display abbreviations are non-semantic."""
    lines: list[str] = []
    direction = {"input": "I", "output": "O"}
    mandate = {"mandatory": "M", "optional": "O"}
    timing = {"asynchronous": "A", "on_demand": "OD", "periodic": "P"}
    kinds = {"oms_message": "M", "data_transfer": "DT", "special_signal": "SS", "security_exchange": "SE", "non_oms_message": ""}
    for function in projection.functions:
        if lines:
            lines.append("")
        lines.append(f"## {_cell(function.function_name)}")
        if function.applicability == "not_applicable":
            lines.extend(("", f"Not Applicable — {_cell(function.not_applicable_reason)}"))
            continue
        lines.extend(("", "| UCI Primitive | I/O | DE | Data Exchange Name | Data Exchange Information | LoM | P | Nominal | Max | Appendix C | Reference |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"))
        for exchange in function.exchanges:
            lines.append("| " + " | ".join((_cell(exchange.uci_primitive), direction[exchange.direction], kinds[exchange.kind], _cell(exchange.exchange_name), _cell(exchange.information), mandate[exchange.mandate], timing[exchange.timing_kind], _timing_value(exchange, exchange.nominal), _timing_value(exchange, exchange.maximum), _cell(exchange.appendix_c_mapping), _cell(exchange.reference))) + " |")
    return "\n".join(lines) + "\n"


def render_json(projection: ProjectedInputsOutputs) -> str:
    return json.dumps(asdict(projection), indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--baseline-manifest", type=Path, required=True)
    parser.add_argument("--baseline-source-root", type=Path, required=True)
    parser.add_argument("--extension", nargs=2, action="append", metavar=("MANIFEST", "SOURCE_ROOT"), default=[])
    parser.add_argument("--format", choices=("markdown", "json"), required=True)
    args = parser.parse_args(argv)
    try:
        contract, _, resolved = prepare_resolution(args.contract, args.baseline_manifest, args.baseline_source_root, [(Path(manifest), Path(root)) for manifest, root in args.extension])
        projection = project_inputs_outputs(contract, resolved)
    except (UciResolverError, InputsOutputsProjectionError) as exc:
        print(f"FAIL {exc}")
        return 1
    print(render_markdown(projection) if args.format == "markdown" else render_json(projection), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
