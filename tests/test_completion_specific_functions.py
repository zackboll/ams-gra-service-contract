from copy import deepcopy
from pathlib import Path

from tools.completion_assistant import load_completion_path, load_decisions_path
from tools.completion_materialize import materialize_contract
from tools.completion_scaffold import (CA_DUPLICATE_SPECIFIC_EXCHANGE,
    CA_DUPLICATE_SPECIFIC_FUNCTION, CA_MAPPING_FIELD_INCOMPATIBLE,
    CA_UNKNOWN_SPECIFIC_EXCHANGE, build_scaffold, load_mapping_path,
    validate_mapping_document, validate_specific_functions)
from tools.validate import profile_diagnostics, validate_document, validate_profile_path
from tools.yaml_support import load_path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles/oms/2.5/profile.yaml"
INPUT = ROOT / "examples/completion/complete-service.yaml"
DECISIONS = ROOT / "examples/completion/complete-service-decisions.yaml"
STRUCTURE = ROOT / "examples/completion/complete-service-specific-functions.yaml"

def test_specific_structure_and_materialization_are_explicit() -> None:
    completion, d = load_completion_path(INPUT); assert not d
    decisions, d = load_decisions_path(DECISIONS, completion); assert not d
    profile, d = validate_profile_path(PROFILE); assert not d
    structure = load_path(STRUCTURE); assert validate_specific_functions(structure) == []
    bindings = []
    values = {"function.id":"synthetic-processing-id", "function.name":"Synthetic Processing", "function.app":"applicable", "in.id":"synthetic-input-id", "in.message":"SyntheticInput", "in.direction":"input", "in.mandate":"mandatory", "in.topic":"synthetic.in", "in.timing":"asynchronous", "out.id":"synthetic-output-id", "out.message":"SyntheticOutput", "out.direction":"output", "out.mandate":"optional", "out.topic":"synthetic.out", "out.timing":"periodic"}
    decisions = deepcopy(decisions); decisions["decisions"] += [{"target":k,"value":v} for k,v in values.items()]
    for target, field in (("function.id","id"),("function.name","name"),("function.app","applicability")):
        bindings.append({"target":target,"destination":{"kind":"specific_function_field","function_key":"synthetic-processing","field":field}})
    for prefix, key in (("in","synthetic-input"),("out","synthetic-output")):
        for field in ("id","message","direction","mandate","topic"):
            bindings.append({"target":f"{prefix}.{field}","destination":{"kind":"specific_exchange_field","function_key":"synthetic-processing","exchange_key":key,"field":field}})
        bindings.append({"target":f"{prefix}.timing","destination":{"kind":"specific_exchange_field","function_key":"synthetic-processing","exchange_key":key,"field":"timing_kind"}})
    mapping=load_path(ROOT / "examples/completion/complete-service-mapping.yaml")
    mapping["bindings"] += bindings
    assert validate_mapping_document(mapping, completion, decisions, profile, structure) == []
    scaffold=build_scaffold(completion,decisions,mapping,profile,structure)
    specific=scaffold["functions"][-1]
    assert specific["function_origin"] == "specific_function_structure"
    assert "required_group" not in specific and specific["category"]["value"] == "specific"
    contract, diagnostics=materialize_contract(scaffold); assert diagnostics == []
    function=contract["functions"][-1]
    assert function["id"] == "synthetic-processing-id" and function["name"] == "Synthetic Processing"
    assert [x["id"] for x in function["exchanges"]] == ["synthetic-input-id","synthetic-output-id"]
    assert validate_document(contract) == [] and profile_diagnostics(contract,profile) == []

def test_specific_duplicate_and_timing_diagnostics() -> None:
    structure=load_path(STRUCTURE); duplicate=deepcopy(structure); duplicate["functions"].append(deepcopy(duplicate["functions"][0]))
    assert CA_DUPLICATE_SPECIFIC_FUNCTION in {x.code for x in validate_specific_functions(duplicate)}
    duplicate=deepcopy(structure); duplicate["functions"][0]["exchanges"].append(deepcopy(duplicate["functions"][0]["exchanges"][0]))
    assert CA_DUPLICATE_SPECIFIC_EXCHANGE in {x.code for x in validate_specific_functions(duplicate)}
    completion,_=load_completion_path(INPUT); decisions,_=load_decisions_path(DECISIONS,completion); profile,_=validate_profile_path(PROFILE)
    decisions=deepcopy(decisions); decisions["decisions"] += [{"target":"timing","value":"asynchronous"},{"target":"rate","value":1}]
    mapping={"mapping_version":"0.1","bindings":[{"target":"timing","destination":{"kind":"specific_exchange_field","function_key":"synthetic-processing","exchange_key":"synthetic-input","field":"timing_kind"}},{"target":"rate","destination":{"kind":"specific_exchange_field","function_key":"synthetic-processing","exchange_key":"nope","field":"nominal_rate_hz"}}]}
    assert CA_UNKNOWN_SPECIFIC_EXCHANGE in {x.code for x in validate_mapping_document(mapping,completion,decisions,profile,structure)}
    mapping["bindings"][1]["destination"]["exchange_key"]="synthetic-input"
    assert CA_MAPPING_FIELD_INCOMPATIBLE in {x.code for x in validate_mapping_document(mapping,completion,decisions,profile,structure)}
