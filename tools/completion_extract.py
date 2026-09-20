"""Deterministic, offline extraction of unconfirmed completion candidates."""
from __future__ import annotations
import hashlib, json, math, re
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator
try:
    from tools.completion_assistant import completion_schema_diagnostics, completion_semantic_diagnostics
    from tools.validate import Diagnostic
    from tools.yaml_support import YamlInputError, dump_text, load_path, load_text
except ModuleNotFoundError:
    from completion_assistant import completion_schema_diagnostics, completion_semantic_diagnostics
    from validate import Diagnostic
    from yaml_support import YamlInputError, dump_text, load_path, load_text
ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema/tooling/completion/v0.1/completion-extraction.schema.json"
CA_EXTRACTION_SCHEMA="CA_EXTRACTION_SCHEMA"; CA_EXTRACTION_DUPLICATE_SOURCE="CA_EXTRACTION_DUPLICATE_SOURCE"; CA_EXTRACTION_DUPLICATE_RULE="CA_EXTRACTION_DUPLICATE_RULE"; CA_EXTRACTION_UNKNOWN_SOURCE="CA_EXTRACTION_UNKNOWN_SOURCE"; CA_EXTRACTION_PATH="CA_EXTRACTION_PATH"; CA_EXTRACTION_HASH="CA_EXTRACTION_HASH"; CA_EXTRACTION_MATCH="CA_EXTRACTION_MATCH"; CA_EXTRACTION_VALUE="CA_EXTRACTION_VALUE"; CA_EXTRACTION_POINTER="CA_EXTRACTION_POINTER"; CA_EXTRACTION_SERIALIZATION="CA_EXTRACTION_SERIALIZATION"

def _path(parts):
    return "$" + "".join(f"[{p}]" if isinstance(p,int) else f".{p}" for p in parts)
def _duplicates(items):
    seen=set(); return {x for x in items if x in seen or seen.add(x)}
def load_extraction_recipe(path: Path):
    try: recipe=load_path(path)
    except YamlInputError as e: return None,[Diagnostic(CA_EXTRACTION_SCHEMA,"",str(e))]
    schema=json.loads(SCHEMA.read_text())
    diagnostics=[Diagnostic(CA_EXTRACTION_SCHEMA,_path(e.absolute_path),e.message) for e in Draft202012Validator(schema).iter_errors(recipe)]
    if not isinstance(recipe,dict): return None,diagnostics
    sources=recipe.get("sources",[]); rules=recipe.get("rules",[])
    if isinstance(sources,list):
        for value in _duplicates([x.get("id") for x in sources if isinstance(x,dict) and isinstance(x.get("id"),str)]): diagnostics.append(Diagnostic(CA_EXTRACTION_DUPLICATE_SOURCE,"$.sources",f"duplicate source id {value!r}"))
    if isinstance(rules,list):
        for value in _duplicates([x.get("id") for x in rules if isinstance(x,dict) and isinstance(x.get("id"),str)]): diagnostics.append(Diagnostic(CA_EXTRACTION_DUPLICATE_RULE,"$.rules",f"duplicate rule id {value!r}"))
        ids={x.get("id") for x in sources if isinstance(x,dict)}
        for i,r in enumerate(rules):
            if isinstance(r,dict) and r.get("source") not in ids: diagnostics.append(Diagnostic(CA_EXTRACTION_UNKNOWN_SOURCE,f"$.rules[{i}].source",f"unknown source {r.get('source')!r}"))
    return (recipe if not diagnostics else None), diagnostics
def verify_sources(recipe: dict[str,Any], source_root: Path):
    if not source_root.exists() or not source_root.is_dir(): return None,[Diagnostic(CA_EXTRACTION_PATH,"--source-root","must be an existing directory")]
    root=source_root.resolve(); verified={}
    for source in recipe["sources"]:
        local=Path(source["local_path"])
        if local.is_absolute() or ".." in local.parts or local.as_posix()!=source["local_path"]:
            return None,[Diagnostic(CA_EXTRACTION_PATH,f"$.sources[{source['id']}].local_path","must be a canonical relative path")]
        path=root/local
        if path.is_symlink() or not path.exists() or not path.is_file() or root not in path.resolve().parents:
            return None,[Diagnostic(CA_EXTRACTION_PATH,str(path),"must identify a regular non-symlink file beneath --source-root")]
        try: data=path.read_bytes()
        except OSError as e: return None,[Diagnostic(CA_EXTRACTION_PATH,str(path),str(e))]
        actual=hashlib.sha256(data).hexdigest()
        if actual != source["sha256"]: return None,[Diagnostic(CA_EXTRACTION_HASH,str(path),f"SHA-256 {actual} does not match recipe")]
        verified[source["id"]]=data
    return verified,[]
def _scalar(value, path):
    if value is None or isinstance(value,(dict,list)) or not isinstance(value,(str,bool,int,float)) or isinstance(value,float) and not math.isfinite(value): raise ValueError(f"{path} must select a finite completion scalar")
    return value
def _convert(value, kind):
    if kind=="string": return value
    if kind=="boolean":
        if value not in ("true","false"): raise ValueError("Boolean captures must be exactly 'true' or 'false'")
        return value=="true"
    try: parsed=json.loads(value)
    except json.JSONDecodeError as e: raise ValueError("number capture is not JSON number") from e
    if isinstance(parsed,bool) or not isinstance(parsed,(int,float)) or isinstance(parsed,float) and not math.isfinite(parsed): raise ValueError("number capture is not finite JSON number")
    return parsed
def _pointer(value,pointer):
    if pointer=="": return value
    current=value
    for token in pointer[1:].split("/"):
        token=token.replace("~1","/").replace("~0","~")
        if isinstance(current,dict) and token in current: current=current[token]
        elif isinstance(current,list) and token.isdigit() and str(int(token))==token and int(token)<len(current): current=current[int(token)]
        else: raise ValueError("pointer does not exist")
    return current
def extract_candidates(recipe, verified):
    candidates=[]
    for i,rule in enumerate(recipe["rules"]):
        extractor=rule["extractor"]; data=verified[rule["source"]]
        try:
            if extractor["kind"] == "structured_pointer": value=_scalar(_pointer(load_text(data.decode("utf-8"),rule["source"]),extractor["pointer"]),extractor["pointer"])
            else:
                flags=(re.MULTILINE if extractor.get("multiline",False) else 0)|(re.DOTALL if extractor.get("dotall",False) else 0)
                matches=list(re.finditer(extractor["pattern"],data.decode("utf-8"),flags))
                if len(matches)!=1: raise LookupError(f"pattern matched {len(matches)} occurrences; expected exactly one")
                value=extractor["value"] if extractor["kind"]=="text_regex_assert" else _convert(matches[0].group(extractor["group"]),extractor["value_type"])
            candidate={"id":rule["id"], "target":rule["target"], "value":value, "source":rule["source"], "locator":rule["locator"]}
            if "note" in rule: candidate["note"]=rule["note"]
            candidates.append(candidate)
        except (UnicodeDecodeError,YamlInputError) as e: return None,[Diagnostic(CA_EXTRACTION_POINTER,f"$.rules[{i}]",str(e))]
        except (re.error,IndexError,LookupError) as e: return None,[Diagnostic(CA_EXTRACTION_MATCH,f"$.rules[{i}]",str(e))]
        except ValueError as e: return None,[Diagnostic(CA_EXTRACTION_VALUE if extractor["kind"]!="structured_pointer" else CA_EXTRACTION_POINTER,f"$.rules[{i}]",str(e))]
    return candidates,[]
def build_completion_input(recipe,candidates):
    sources=[{k:s[k] for k in ("id","provenance","title","uri","revision","note") if k in s} for s in recipe["sources"]]
    result={"completion_version":"0.1","target":recipe["target"],"sources":sources,"candidates":candidates}
    return result, completion_schema_diagnostics(result) + completion_semantic_diagnostics(result)
def render(document, format_name):
    text=json.dumps(document,indent=2,ensure_ascii=False)+"\n" if format_name=="json" else dump_text(document)
    try: reparsed=json.loads(text) if format_name=="json" else load_text(text)
    except (json.JSONDecodeError,YamlInputError) as e: return None,[Diagnostic(CA_EXTRACTION_SERIALIZATION,"",str(e))]
    diagnostics=completion_schema_diagnostics(reparsed) + completion_semantic_diagnostics(reparsed)
    if reparsed != document or diagnostics: return None,[Diagnostic(CA_EXTRACTION_SERIALIZATION,"","rendered completion input does not round-trip and validate")]
    return text,[]
