"""Load and deterministically dump repository YAML/JSON-compatible data."""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any

import yaml


class YamlInputError(ValueError):
    """Expected YAML/JSON input error suitable for user-facing diagnostics."""


class JsonCompatibleYamlLoader(yaml.SafeLoader):
    """Private loader with controlled YAML 1.2 core-style scalar resolution."""


class JsonCompatibleYamlDumper(yaml.SafeDumper):
    """Safe deterministic YAML emitter for the repository JSON data model."""

    def ignore_aliases(self, data: Any) -> bool:
        return True


# Do not inherit PyYAML's YAML 1.1 implicit resolver table.
JsonCompatibleYamlLoader.yaml_implicit_resolvers = {}
JsonCompatibleYamlLoader.add_implicit_resolver(
    "tag:yaml.org,2002:null", re.compile(r"^(?:~|null|Null|NULL|)$"), ["~", "n", "N", ""]
)
JsonCompatibleYamlLoader.add_implicit_resolver(
    "tag:yaml.org,2002:bool", re.compile(r"^(?:true|True|TRUE|false|False|FALSE)$"), list("tTfF")
)
JsonCompatibleYamlLoader.add_implicit_resolver(
    "tag:yaml.org,2002:int", re.compile(r"^(?:[-+]?[0-9]+|0o[0-7]+|0x[0-9a-fA-F]+)$"), list("-+0123456789")
)
JsonCompatibleYamlLoader.add_implicit_resolver(
    "tag:yaml.org,2002:float",
    re.compile(
        r"^[-+]?(?:[0-9]+\.[0-9]*(?:[eE][-+]?[0-9]+)?|\.[0-9]+(?:[eE][-+]?[0-9]+)?|[0-9]+[eE][-+]?[0-9]+|\.(?:inf|Inf|INF|nan|NaN|NAN))$"
    ),
    list("-+0123456789."),
)
# The dumper must make quoting decisions against precisely the resolver used for
# reloads, rather than PyYAML's YAML 1.1 resolver table.
JsonCompatibleYamlDumper.yaml_implicit_resolvers = JsonCompatibleYamlLoader.yaml_implicit_resolvers


def _construct_yaml_int(loader: JsonCompatibleYamlLoader, node: yaml.Node) -> int:
    value = loader.construct_scalar(node).replace("_", "")
    match = re.fullmatch(r"(?:[-+]?[0-9]+|0o[0-7]+|0x[0-9a-fA-F]+)", value)
    if match is None:
        raise YamlInputError(f"invalid YAML 1.2 integer {value!r}")
    base = 8 if value.startswith("0o") else 16 if value.startswith("0x") else 10
    return int(value[2:] if base != 10 else value, base)


def _construct_mapping(loader: JsonCompatibleYamlLoader, node: yaml.MappingNode, deep: bool = False) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise YamlInputError("mapping keys must be strings")
        if key in mapping:
            raise YamlInputError(f"duplicate mapping key {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


JsonCompatibleYamlLoader.add_constructor("tag:yaml.org,2002:int", _construct_yaml_int)
JsonCompatibleYamlLoader.add_constructor("tag:yaml.org,2002:map", _construct_mapping)


def _validate_json_compatible(value: Any, active: set[int] | None = None) -> None:
    if active is None:
        active = set()
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise YamlInputError("non-finite numeric values are not JSON-compatible")
        return
    if isinstance(value, (list, dict)):
        identity = id(value)
        if identity in active:
            raise YamlInputError("recursive aliases are not JSON-compatible")
        active.add(identity)
        if isinstance(value, list):
            for item in value:
                _validate_json_compatible(item, active)
        else:
            for key, item in value.items():
                if not isinstance(key, str):
                    raise YamlInputError("mapping keys must be strings")
                _validate_json_compatible(item, active)
        active.remove(identity)
        return
    raise YamlInputError(f"value of type {type(value).__name__} is not JSON-compatible")


def load_text(text: str, source: str = "input") -> Any:
    """Parse YAML/JSON text into the documented JSON-compatible data model."""
    try:
        value = yaml.load(text, Loader=JsonCompatibleYamlLoader)
    except YamlInputError:
        raise
    except yaml.YAMLError as exc:
        raise YamlInputError(f"malformed YAML/JSON in {source}: {exc.problem or str(exc)}") from exc
    except (ValueError, TypeError, OverflowError) as exc:
        raise YamlInputError(f"invalid YAML/JSON value in {source}: {exc}") from exc
    _validate_json_compatible(value)
    return value


def load_path(path: Path) -> Any:
    """Read and parse one UTF-8 YAML/JSON document."""
    try:
        return load_text(path.read_text(encoding="utf-8"), str(path))
    except OSError as exc:
        raise YamlInputError(f"could not read {path}: {exc}") from exc


def dump_text(value: Any) -> str:
    """Render JSON-compatible data as stable, loader-compatible YAML text."""
    _validate_json_compatible(value)
    return yaml.dump(
        value,
        Dumper=JsonCompatibleYamlDumper,
        allow_unicode=True,
        default_flow_style=False,
        indent=2,
        sort_keys=False,
        width=1000,
        line_break="\n",
    )
