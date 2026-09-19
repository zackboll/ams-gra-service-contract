#!/usr/bin/env python3
"""Render a non-normative completion authoring scaffold."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator,FormatChecker
try:
 from tools.completion_assistant import load_completion_path,load_decisions_path
 from tools.validate import Diagnostic,validate_profile_path
 from tools.yaml_support import YamlInputError,load_path
except ModuleNotFoundError:
 from completion_assistant import load_completion_path,load_decisions_path
 from validate import Diagnostic,validate_profile_path
 from yaml_support import YamlInputError,load_path
ROOT=Path(__file__).resolve().parents[1]; MAPPING_SCHEMA_PATH=ROOT/"schema/tooling/completion/v0.1/completion-mapping.schema.json"; SPECIFIC_SCHEMA_PATH=ROOT/"schema/tooling/completion/v0.1/completion-specific-functions.schema.json"
CA_MAPPING_SCHEMA="CA_MAPPING_SCHEMA";CA_SPECIFIC_SCHEMA="CA_SPECIFIC_SCHEMA";CA_DUPLICATE_MAPPING_TARGET="CA_DUPLICATE_MAPPING_TARGET";CA_DUPLICATE_MAPPING_DESTINATION="CA_DUPLICATE_MAPPING_DESTINATION";CA_DUPLICATE_SPECIFIC_FUNCTION="CA_DUPLICATE_SPECIFIC_FUNCTION";CA_DUPLICATE_SPECIFIC_EXCHANGE="CA_DUPLICATE_SPECIFIC_EXCHANGE";CA_UNKNOWN_MAPPING_TARGET="CA_UNKNOWN_MAPPING_TARGET";CA_UNKNOWN_PROFILE_FUNCTION="CA_UNKNOWN_PROFILE_FUNCTION";CA_UNKNOWN_PROFILE_EXCHANGE="CA_UNKNOWN_PROFILE_EXCHANGE";CA_UNKNOWN_SPECIFIC_FUNCTION="CA_UNKNOWN_SPECIFIC_FUNCTION";CA_UNKNOWN_SPECIFIC_EXCHANGE="CA_UNKNOWN_SPECIFIC_EXCHANGE";CA_MAPPING_FIELD_INCOMPATIBLE="CA_MAPPING_FIELD_INCOMPATIBLE";CA_MAPPING_VALUE_TYPE="CA_MAPPING_VALUE_TYPE";CA_CONTEXT_ASSERTION_MISMATCH="CA_CONTEXT_ASSERTION_MISMATCH"
NUMERIC={"nominal_rate_hz","max_rate_hz","nominal_response_seconds","max_response_seconds"}
FIELDS={"oms_message":{"id","direction","mandate","message","topic","timing_kind","operational_attribute","subscription_group","appendix_c_mapping"},"data_transfer":{"id","direction","mandate","name","protocol","data_type","data_format","sharing_pattern","timing_kind"},"special_signal":{"id","direction","mandate","name","details","reference","timing_kind"},"security_exchange":{"id","direction","mandate","name","details","reference","timing_kind"},"non_oms_message":{"id","direction","mandate","name","details","reference","timing_kind"}}
def _path(p):return "$"+"".join(f"[{x}]" if isinstance(x,int) else f".{x}" for x in p)
def _dupes(v):return {x for x in v if v.count(x)>1}
def _selector(e):return e.get("message",e.get("name",""))
def _schema(p):return json.loads(p.read_text(encoding="utf-8"))
def validate_specific_functions(d):
 es=sorted(Draft202012Validator(_schema(SPECIFIC_SCHEMA_PATH),format_checker=FormatChecker()).iter_errors(d),key=lambda e:list(e.absolute_path))
 if es:return [Diagnostic(CA_SPECIFIC_SCHEMA,_path(e.absolute_path),e.message) for e in es]
 r=[Diagnostic(CA_DUPLICATE_SPECIFIC_FUNCTION,"$.functions",f"duplicate specific function key {x!r}") for x in sorted(_dupes([f["key"] for f in d["functions"]]))]
 for i,f in enumerate(d["functions"]):r += [Diagnostic(CA_DUPLICATE_SPECIFIC_EXCHANGE,f"$.functions[{i}].exchanges",f"duplicate specific exchange key {x!r}") for x in sorted(_dupes([e["key"] for e in f["exchanges"]]))]
 return r
def load_specific_functions_path(p):
 try:d=load_path(p)
 except YamlInputError as e:return None,[Diagnostic(CA_SPECIFIC_SCHEMA,"",f"could not parse {p}: {e}")]
 return d,validate_specific_functions(d)
def _values(c,d):
 if not d:return {}
 cs={x["id"]:x for x in c["candidates"]};ss={x["id"]:x for x in c["sources"]};r={}
 for x in d["decisions"]:
  if "select_candidate" in x:
   q=cs[x["select_candidate"]];s=ss[q["source"]];r[x["target"]]={"value":q["value"],"origin":"author_decision","candidate_id":q["id"],"source":s["id"],"provenance":s["provenance"]}
  else:r[x["target"]]={"value":x["value"],"origin":"author_decision"}
 return r
def _specific(s,f,e=None):
 x=next((x for x in (s or {"functions":[]})["functions"] if x["key"]==f),None)
 return next((x for x in x["exchanges"] if x["key"]==e),None) if x and e is not None else x
def validate_mapping_document(m,c,d,p,specific=None):
 es=sorted(Draft202012Validator(_schema(MAPPING_SCHEMA_PATH),format_checker=FormatChecker()).iter_errors(m),key=lambda e:list(e.absolute_path))
 if es:return [Diagnostic(CA_MAPPING_SCHEMA,_path(e.absolute_path),e.message) for e in es]
 b=m["bindings"];r=[Diagnostic(CA_DUPLICATE_MAPPING_TARGET,"$.bindings",f"duplicate mapping target {x!r}") for x in sorted(_dupes([x["target"] for x in b]))]+[Diagnostic(CA_DUPLICATE_MAPPING_DESTINATION,"$.bindings","duplicate mapping destination") for x in _dupes([json.dumps(x["destination"],sort_keys=True) for x in b])];v=_values(c,d);known={x["target"] for x in c["candidates"]}|set(v)
 for i,x in enumerate(b):
  t,z=x["target"],x["destination"];base=f"$.bindings[{i}].destination";e=None
  if t not in known:r.append(Diagnostic(CA_UNKNOWN_MAPPING_TARGET,f"$.bindings[{i}].target",f"unknown completion target {t!r}"));continue
  if z["kind"] in {"specific_function_field","specific_exchange_field"}:
   f=_specific(specific,z["function_key"])
   if not f:r.append(Diagnostic(CA_UNKNOWN_SPECIFIC_FUNCTION,f"{base}.function_key",f"unknown specific function {z['function_key']!r}"));continue
   if z["kind"]=="specific_exchange_field":
    e=_specific(specific,z["function_key"],z["exchange_key"])
    if not e:r.append(Diagnostic(CA_UNKNOWN_SPECIFIC_EXCHANGE,f"{base}.exchange_key",f"unknown specific exchange {z['exchange_key']!r}"));continue
    if z["field"] not in FIELDS[e["kind"]]|NUMERIC:r.append(Diagnostic(CA_MAPPING_FIELD_INCOMPATIBLE,f"{base}.field","field is incompatible with specific exchange kind"))
    times=[q["target"] for q in b if q["destination"]=={"kind":"specific_exchange_field","function_key":z["function_key"],"exchange_key":z["exchange_key"],"field":"timing_kind"}];tv=v.get(times[0],{}).get("value") if len(times)==1 else None
    if z["field"].endswith("rate_hz") and tv not in (None,"periodic"):r.append(Diagnostic(CA_MAPPING_FIELD_INCOMPATIBLE,base,"rate fields require periodic timing"))
    if z["field"].endswith("response_seconds") and tv not in (None,"on_demand"):r.append(Diagnostic(CA_MAPPING_FIELD_INCOMPATIBLE,base,"response fields require on_demand timing"))
    if z["field"]=="timing_kind" and t in v and v[t]["value"] not in {"asynchronous","on_demand","periodic"}:r.append(Diagnostic(CA_MAPPING_FIELD_INCOMPATIBLE,base,"unknown timing kind"))
   elif z["field"]=="applicability" and t in v and v[t]["value"] not in {"applicable","not_applicable"}:r.append(Diagnostic(CA_MAPPING_FIELD_INCOMPATIBLE,base,"specific applicability must be applicable or not_applicable"))
  elif z["kind"] in {"required_function_field","required_exchange_field"}:
   fs=[f for f in p["required_functions"] if f["name"]==z["profile_function"] and c["target"]["service_kind"] in f["applies_to"]]
   if len(fs)!=1:r.append(Diagnostic(CA_UNKNOWN_PROFILE_FUNCTION,base,"profile function is not uniquely applicable"));continue
   if z["kind"]=="required_exchange_field":
    e=next((q for q in fs[0].get("required_exchanges",[]) if _selector(q)==z["selector"]),None)
    if not e:r.append(Diagnostic(CA_UNKNOWN_PROFILE_EXCHANGE,base,"profile exchange is not present"));continue
    allowed=(FIELDS[e["kind"]]-{"direction","mandate","message","name","timing_kind"})|NUMERIC
    if z["field"] not in allowed or (z["field"].endswith("rate_hz") and e["timing_kind"]!="periodic") or (z["field"].endswith("response_seconds") and e["timing_kind"]!="on_demand"):r.append(Diagnostic(CA_MAPPING_FIELD_INCOMPATIBLE,base,"field is incompatible with profile exchange kind/timing"))
  elif z["kind"]=="context_assertion" and t in v:
   if v[t]["value"]!=c["target"][{"service_kind":"service_kind","oms_version":"oms_version","contract_version":"contract_version"}[z["field"]]]:r.append(Diagnostic(CA_CONTEXT_ASSERTION_MISMATCH,base,"author decision disagrees with completion target context"))
  if t in v:
   good=isinstance(v[t]["value"],(int,float) if z.get("field") in NUMERIC else str) and not isinstance(v[t]["value"],bool)
   if not good:r.append(Diagnostic(CA_MAPPING_VALUE_TYPE,base,"decision value has incompatible type"))
 return r
def load_mapping_path(path,c,d,p,specific=None):
 try:m=load_path(path)
 except YamlInputError as e:return None,[Diagnostic(CA_MAPPING_SCHEMA,"",f"could not parse {path}: {e}")]
 return m,validate_mapping_document(m,c,d,p,specific)
def _miss():return {"state":"missing"}
def _res(v,o):return {"state":"resolved","value":v,"origin":o}
def build_scaffold(c,d,m,p,specific=None):
 v=_values(c,d);a={json.dumps(x["destination"],sort_keys=True):{"state":"resolved",**v[x["target"]]} for x in m["bindings"] if x["target"] in v};get=lambda z,default=None:a.get(json.dumps(z,sort_keys=True),default or _miss())
 r={"scaffold_version":"0.1","service":{},"standards":{},"target":{},"functions":[],"unresolved_required_fields":[],"unmapped_author_decisions":[]}
 for n in ("name","version","description"):r["service"][n]=get({"kind":"service_field","field":n})
 for n in ("uci_schema_version","ams_gra_version"):r["standards"][n]=get({"kind":"standards_field","field":n})
 for n in ("contract_version","oms_version","service_kind"):r["target"][n]=get({"kind":"context_assertion","field":n},_res(c["target"][n],"completion_target"))
 def add(f,origin,key,exchanges):
  dk="specific_function_field" if origin.startswith("specific") else "required_function_field"; owner={"function_key":key[1]} if origin.startswith("specific") else {"profile_function":key[1]}
  dest=lambda field:{"kind":dk,**owner,"field":field}
  item={"function_origin":origin,key[0]:key[1],"id":get(dest("id")),"name":get(dest("name")) if origin.startswith("specific") else _res(f["name"],"oms_profile"),"category":_res("specific","specific_function_structure") if origin.startswith("specific") else _res(f["category"],"oms_profile"),"applicability":get(dest("applicability"),None if origin.startswith("specific") else (_res(f["applicability"],"oms_profile") if "applicability" in f else _miss())),"not_applicable_reason":get(dest("not_applicable_reason")),"description":get(dest("description")),"exchanges":[]}
  if not origin.startswith("specific"):item["required_group"]=_res(f["required_group"],"oms_profile")
  for e in exchanges:
   kind=e["kind"];ek=e.get("key",_selector(e));ex={"exchange_key":ek,"selector":_selector(e),"active":True,"kind":_res(kind,"specific_function_structure" if origin.startswith("specific") else "oms_profile")}
   for n in FIELDS[kind]|NUMERIC:
    if origin.startswith("specific"):ex[n]=get({"kind":"specific_exchange_field","function_key":key[1],"exchange_key":ek,"field":n})
    elif n in {"direction","mandate","timing_kind"}:ex[n]=_res(e[n],"oms_profile")
    elif n in {"message","name"}:ex[n]=_res(e[n],"oms_profile")
    else:ex[n]=get({"kind":"required_exchange_field","profile_function":key[1],"selector":ek,"field":n})
   item["exchanges"].append(ex)
  r["functions"].append(item)
 for f in p["required_functions"]:
  if c["target"]["service_kind"] in f["applies_to"]:add(f,"oms_profile",("profile_function",f["name"]),f.get("required_exchanges",[]))
 for f in (specific or {"functions":[]})["functions"]:add(f,"specific_function_structure",("function_key",f["key"]),f["exchanges"])
 for f in r["functions"]:
  ident=f.get("profile_function",f.get("function_key"));app=f["applicability"]
  if app["state"]=="missing":r["unresolved_required_fields"].append(f"functions[{ident}].applicability")
  if app.get("value")=="not_applicable":
   for e in f["exchanges"]:e["active"]=False
   if f["not_applicable_reason"]["state"]=="missing":r["unresolved_required_fields"].append(f"functions[{ident}].not_applicable_reason")
  else:
   for n in (("id","name") if f["function_origin"]=="specific_function_structure" else ("id",)):
    if f[n]["state"]=="missing":r["unresolved_required_fields"].append(f"functions[{ident}].{n}")
   for e in f["exchanges"]:
    req={"id","direction","mandate","timing_kind"}|({"message","topic"} if e["kind"]["value"]=="oms_message" else {"name"})|({"protocol","data_type","data_format","sharing_pattern"} if e["kind"]["value"]=="data_transfer" else set())
    for n in req:
     if e[n]["state"]=="missing":r["unresolved_required_fields"].append(f"functions[{ident}].exchanges[{e['exchange_key']}].{n}")

 r["unmapped_author_decisions"]=[{"target":t,**x} for t,x in v.items() if t not in {q["target"] for q in m["bindings"]}];return r
def render_json(s):return json.dumps(s,indent=2,ensure_ascii=False)+"\n"
def render_markdown(s):return "# Completion authoring scaffold\n\n"+"\n".join(f"- `{x}`" for x in s["unresolved_required_fields"])+"\n"
def main(argv=None):
 q=argparse.ArgumentParser(description=__doc__);[q.add_argument(*x,**y) for x,y in [(("--input",),{"type":Path,"required":True}),(("--decisions",),{"type":Path,"required":True}),(("--mapping",),{"type":Path,"required":True}),(("--specific-functions",),{"type":Path}),(("--profile",),{"type":Path,"required":True}),(("--format",),{"choices":("markdown","json"),"required":True})]];x=q.parse_args(argv);c,ds=load_completion_path(x.input.resolve());d=s=None
 if not ds:d,ds=load_decisions_path(x.decisions.resolve(),c)
 if not ds and x.specific_functions:s,ds=load_specific_functions_path(x.specific_functions.resolve())
 if not ds:p,ds=validate_profile_path(x.profile.resolve())
 if not ds:m,ds=load_mapping_path(x.mapping.resolve(),c,d,p,s)
 if ds:
  for z in ds:print(f"FAIL {z}",file=sys.stderr)
  return 1
 out=build_scaffold(c,d,m,p,s);print(render_json(out) if x.format=="json" else render_markdown(out),end="");return 0
if __name__=="__main__":raise SystemExit(main())
