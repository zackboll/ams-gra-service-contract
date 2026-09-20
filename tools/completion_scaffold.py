#!/usr/bin/env python3
"""Render a non-normative completion authoring scaffold."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker
try:
 from tools.completion_assistant import load_completion_path,load_decisions_path
 from tools.validate import Diagnostic,validate_profile_path
 from tools.yaml_support import YamlInputError,load_path
except ModuleNotFoundError:
 from completion_assistant import load_completion_path,load_decisions_path
 from validate import Diagnostic,validate_profile_path
 from yaml_support import YamlInputError,load_path
ROOT=Path(__file__).resolve().parents[1]
MAPPING_SCHEMA_PATH=ROOT/'schema/tooling/completion/v0.1/completion-mapping.schema.json'
SPECIFIC_SCHEMA_PATH=ROOT/'schema/tooling/completion/v0.1/completion-specific-functions.schema.json'
CAPABILITY_SCHEMA_PATH=ROOT/'schema/tooling/completion/v0.1/completion-capabilities.schema.json'
TRACEABILITY_SCHEMA_PATH=ROOT/'schema/tooling/completion/v0.1/completion-traceability.schema.json'
CA_MAPPING_SCHEMA='CA_MAPPING_SCHEMA';CA_SPECIFIC_SCHEMA='CA_SPECIFIC_SCHEMA';CA_CAPABILITY_SCHEMA='CA_CAPABILITY_SCHEMA';CA_DUPLICATE_MAPPING_TARGET='CA_DUPLICATE_MAPPING_TARGET';CA_DUPLICATE_MAPPING_DESTINATION='CA_DUPLICATE_MAPPING_DESTINATION';CA_DUPLICATE_SPECIFIC_FUNCTION='CA_DUPLICATE_SPECIFIC_FUNCTION';CA_DUPLICATE_SPECIFIC_EXCHANGE='CA_DUPLICATE_SPECIFIC_EXCHANGE';CA_DUPLICATE_CAPABILITY_KEY='CA_DUPLICATE_CAPABILITY_KEY';CA_UNKNOWN_MAPPING_TARGET='CA_UNKNOWN_MAPPING_TARGET';CA_UNKNOWN_PROFILE_FUNCTION='CA_UNKNOWN_PROFILE_FUNCTION';CA_UNKNOWN_PROFILE_EXCHANGE='CA_UNKNOWN_PROFILE_EXCHANGE';CA_UNKNOWN_SPECIFIC_FUNCTION='CA_UNKNOWN_SPECIFIC_FUNCTION';CA_UNKNOWN_SPECIFIC_EXCHANGE='CA_UNKNOWN_SPECIFIC_EXCHANGE';CA_UNKNOWN_CAPABILITY_KEY='CA_UNKNOWN_CAPABILITY_KEY';CA_UNKNOWN_CAPABILITY_ROLE='CA_UNKNOWN_CAPABILITY_ROLE';CA_INACTIVE_CAPABILITY_FUNCTION='CA_INACTIVE_CAPABILITY_FUNCTION';CA_MAPPING_FIELD_INCOMPATIBLE='CA_MAPPING_FIELD_INCOMPATIBLE';CA_MAPPING_VALUE_TYPE='CA_MAPPING_VALUE_TYPE';CA_CONTEXT_ASSERTION_MISMATCH='CA_CONTEXT_ASSERTION_MISMATCH'
CA_TRACEABILITY_SCHEMA='CA_TRACEABILITY_SCHEMA';CA_DUPLICATE_SOURCE_KEY='CA_DUPLICATE_SOURCE_KEY';CA_UNKNOWN_EVIDENCE_SOURCE='CA_UNKNOWN_EVIDENCE_SOURCE';CA_SOURCE_REVISION_MISMATCH='CA_SOURCE_REVISION_MISMATCH';CA_UNKNOWN_TRACE_SOURCE='CA_UNKNOWN_TRACE_SOURCE';CA_UNKNOWN_TRACE_TARGET='CA_UNKNOWN_TRACE_TARGET';CA_INACTIVE_TRACE_TARGET='CA_INACTIVE_TRACE_TARGET';CA_DUPLICATE_TRACEABILITY='CA_DUPLICATE_TRACEABILITY'
NUMERIC={'nominal_rate_hz','max_rate_hz','nominal_response_seconds','max_response_seconds'}
FIELDS={'oms_message':{'id','direction','mandate','message','topic','timing_kind','operational_attribute','subscription_group','appendix_c_mapping'},'data_transfer':{'id','direction','mandate','name','protocol','data_type','data_format','sharing_pattern','timing_kind'},'special_signal':{'id','direction','mandate','name','details','reference','timing_kind'},'security_exchange':{'id','direction','mandate','name','details','reference','timing_kind'},'non_oms_message':{'id','direction','mandate','name','details','reference','timing_kind'}}
def _path(p):return '$'+''.join(f'[{x}]' if isinstance(x,int) else f'.{x}' for x in p)
def _dupes(v):return {x for x in v if v.count(x)>1}
def _selector(e):return e.get('message',e.get('name',''))
def _schema(p):return json.loads(p.read_text(encoding='utf-8'))
def _validate(d,path,code):
 es=sorted(Draft202012Validator(_schema(path),format_checker=FormatChecker()).iter_errors(d),key=lambda e:list(e.absolute_path));return [Diagnostic(code,_path(e.absolute_path),e.message) for e in es]
def validate_specific_functions(d):
 r=_validate(d,SPECIFIC_SCHEMA_PATH,CA_SPECIFIC_SCHEMA)
 if r:return r
 r=[Diagnostic(CA_DUPLICATE_SPECIFIC_FUNCTION,'$.functions',f'duplicate specific function key {x!r}') for x in sorted(_dupes([f['key'] for f in d['functions']]))]
 for i,f in enumerate(d['functions']):r += [Diagnostic(CA_DUPLICATE_SPECIFIC_EXCHANGE,f'$.functions[{i}].exchanges',f'duplicate specific exchange key {x!r}') for x in sorted(_dupes([e['key'] for e in f['exchanges']]))]
 return r
def validate_capabilities(d):
 r=_validate(d,CAPABILITY_SCHEMA_PATH,CA_CAPABILITY_SCHEMA)
 if r:return r
 return [Diagnostic(CA_DUPLICATE_CAPABILITY_KEY,'$.capabilities',f'duplicate capability key {x!r}') for x in sorted(_dupes([x['key'] for x in d['capabilities']]))]
def _load(p,fn,code):
 try:d=load_path(p)
 except YamlInputError as e:return None,[Diagnostic(code,'',f'could not parse {p}: {e}')]
 return d,fn(d)
def load_specific_functions_path(p):return _load(p,validate_specific_functions,CA_SPECIFIC_SCHEMA)
def load_capabilities_path(p):return _load(p,validate_capabilities,CA_CAPABILITY_SCHEMA)
def validate_traceability(d,completion):
 r=_validate(d,TRACEABILITY_SCHEMA_PATH,CA_TRACEABILITY_SCHEMA)
 if r:return r
 r=[Diagnostic(CA_DUPLICATE_SOURCE_KEY,'$.sources',f'duplicate source key {x!r}') for x in sorted(_dupes([x['key'] for x in d['sources']]))]
 evidence={x['id']:x for x in completion['sources']}
 for i,x in enumerate(d['sources']):
  e=evidence.get(x['from_completion_source'])
  if not e:r.append(Diagnostic(CA_UNKNOWN_EVIDENCE_SOURCE,f'$.sources[{i}].from_completion_source',f'unknown completion evidence source {x["from_completion_source"]!r}'))
  elif 'revision' in e and 'revision' in x and e['revision'] != x['revision']:r.append(Diagnostic(CA_SOURCE_REVISION_MISMATCH,f'$.sources[{i}].revision','authored revision differs from completion evidence revision'))
 keys={x['key'] for x in d['sources']}
 for i,x in enumerate(d['traces']):
  if x['source_key'] not in keys:r.append(Diagnostic(CA_UNKNOWN_TRACE_SOURCE,f'$.traces[{i}].source_key',f'unknown authored source key {x["source_key"]!r}'))
 seen=set()
 for i,x in enumerate(d['traces']):
  key=json.dumps({k:x.get(k) for k in ('destination','source_key','locator','note')},sort_keys=True)
  if key in seen:r.append(Diagnostic(CA_DUPLICATE_TRACEABILITY,f'$.traces[{i}]','duplicate traceability declaration'))
  seen.add(key)
 return r
def load_traceability_path(p,completion):return _load(p,lambda d:validate_traceability(d,completion),CA_TRACEABILITY_SCHEMA)
def _values(c,d):
 if not d:return {}
 cs={x['id']:x for x in c['candidates']};ss={x['id']:x for x in c['sources']};r={}
 for x in d['decisions']:
  if 'select_candidate' in x:
   q=cs[x['select_candidate']];s=ss[q['source']];r[x['target']]={'value':q['value'],'origin':'author_decision','candidate_id':q['id'],'source':s['id'],'provenance':s['provenance']}
  else:r[x['target']]={'value':x['value'],'origin':'author_decision'}
 return r
def _specific(s,f,e=None):
 x=next((x for x in (s or {'functions':[]})['functions'] if x['key']==f),None);return next((x for x in x['exchanges'] if x['key']==e),None) if x and e is not None else x
def _cap(caps,key):return next((x for x in (caps or {'capabilities':[]})['capabilities'] if x['key']==key),None)
def _roles(p):return {x['role']:x for x in p['required_capability_functions']}
def validate_mapping_document(m,c,d,p,specific=None,capabilities=None):
 r=_validate(m,MAPPING_SCHEMA_PATH,CA_MAPPING_SCHEMA)
 if r:return r
 b=m['bindings'];v=_values(c,d);known={x['target'] for x in c['candidates']}|set(v);r=[Diagnostic(CA_DUPLICATE_MAPPING_TARGET,'$.bindings',f'duplicate mapping target {x!r}') for x in sorted(_dupes([x['target'] for x in b]))]+[Diagnostic(CA_DUPLICATE_MAPPING_DESTINATION,'$.bindings','duplicate mapping destination') for x in _dupes([json.dumps(x['destination'],sort_keys=True) for x in b])];roles=_roles(p);kind=c['target']['service_kind']
 for i,x in enumerate(b):
  t,z=x['target'],x['destination'];base=f'$.bindings[{i}].destination'
  if t not in known:r.append(Diagnostic(CA_UNKNOWN_MAPPING_TARGET,f'$.bindings[{i}].target',f'unknown completion target {t!r}'));continue
  if z['kind']=='capability_field':
   if not _cap(capabilities,z['capability_key']):r.append(Diagnostic(CA_UNKNOWN_CAPABILITY_KEY,f'{base}.capability_key',f'unknown capability key {z["capability_key"]!r}'))
  elif z['kind'] in {'capability_function_field','component_capability_function_field'}:
   role=roles.get(z['role'])
   if z['kind']=='capability_function_field' and not _cap(capabilities,z['capability_key']):r.append(Diagnostic(CA_UNKNOWN_CAPABILITY_KEY,f'{base}.capability_key',f'unknown capability key {z["capability_key"]!r}'));continue
   if not role or kind not in role['applies_to'] or role['per_capability'] != (z['kind']=='capability_function_field'):r.append(Diagnostic(CA_UNKNOWN_CAPABILITY_ROLE,f'{base}.role','Capability role is unknown, inapplicable, or has incompatible ownership'));continue
   if not role['per_capability'] and not any(_value_for(b,v,{'kind':'capability_field','capability_key':q['key'],'field':'requires_position_information'}) is True for q in (capabilities or {'capabilities':[]})['capabilities']):r.append(Diagnostic(CA_INACTIVE_CAPABILITY_FUNCTION,base,'component Capability function is inactive'))
  elif z['kind'] in {'specific_function_field','specific_exchange_field'}:
   f=_specific(specific,z['function_key'])
   if not f:r.append(Diagnostic(CA_UNKNOWN_SPECIFIC_FUNCTION,f'{base}.function_key',f'unknown specific function {z["function_key"]!r}'));continue
   if z['kind']=='specific_exchange_field':
    e=_specific(specific,z['function_key'],z['exchange_key'])
    if not e:r.append(Diagnostic(CA_UNKNOWN_SPECIFIC_EXCHANGE,f'{base}.exchange_key',f'unknown specific exchange {z["exchange_key"]!r}'));continue
    if z['field'] not in FIELDS[e['kind']]|NUMERIC:r.append(Diagnostic(CA_MAPPING_FIELD_INCOMPATIBLE,f'{base}.field','field is incompatible with specific exchange kind'))
    times=[q['target'] for q in b if q['destination']=={'kind':'specific_exchange_field','function_key':z['function_key'],'exchange_key':z['exchange_key'],'field':'timing_kind'}];tv=v.get(times[0],{}).get('value') if len(times)==1 else None
    if z['field'].endswith('rate_hz') and tv not in (None,'periodic'):r.append(Diagnostic(CA_MAPPING_FIELD_INCOMPATIBLE,base,'rate fields require periodic timing'))
    if z['field'].endswith('response_seconds') and tv not in (None,'on_demand'):r.append(Diagnostic(CA_MAPPING_FIELD_INCOMPATIBLE,base,'response fields require on_demand timing'))
  elif z['kind'] in {'required_function_field','required_exchange_field'}:
   fs=[f for f in p['required_functions'] if f['name']==z['profile_function'] and kind in f['applies_to']]
   if len(fs)!=1:r.append(Diagnostic(CA_UNKNOWN_PROFILE_FUNCTION,base,'profile function is not uniquely applicable'));continue
   if z['kind']=='required_exchange_field':
    e=next((q for q in fs[0].get('required_exchanges',[]) if _selector(q)==z['selector']),None)
    if not e:r.append(Diagnostic(CA_UNKNOWN_PROFILE_EXCHANGE,base,'profile exchange is not present'));continue
    if z['field'] not in (FIELDS[e['kind']]-{'direction','mandate','message','name','timing_kind'})|NUMERIC or (z['field'].endswith('rate_hz') and e['timing_kind']!='periodic') or (z['field'].endswith('response_seconds') and e['timing_kind']!='on_demand'):r.append(Diagnostic(CA_MAPPING_FIELD_INCOMPATIBLE,base,'field is incompatible with profile exchange kind/timing'))
  elif z['kind']=='context_assertion' and t in v and v[t]['value']!=c['target'][z['field']]:r.append(Diagnostic(CA_CONTEXT_ASSERTION_MISMATCH,base,'author decision disagrees with completion target context'))
  if t in v:
   expected=bool if z.get('field')=='requires_position_information' else ((int,float) if z.get('field') in NUMERIC else str);good=isinstance(v[t]['value'],expected) and not (expected != bool and isinstance(v[t]['value'],bool))
   if not good:r.append(Diagnostic(CA_MAPPING_VALUE_TYPE,base,'decision value has incompatible type'))
 return r
def _value_for(bindings,values,dest):
 targets=[x['target'] for x in bindings if x['destination']==dest];return values.get(targets[0],{}).get('value') if len(targets)==1 else None
def load_mapping_path(path,c,d,p,specific=None,capabilities=None):
 try:m=load_path(path)
 except YamlInputError as e:return None,[Diagnostic(CA_MAPPING_SCHEMA,'',f'could not parse {path}: {e}')]
 return m,validate_mapping_document(m,c,d,p,specific,capabilities)
def _miss():return {'state':'missing'}
def _res(v,o):return {'state':'resolved','value':v,'origin':o}
def build_scaffold(c,d,m,p,specific=None,capabilities=None,traceability=None):
 v=_values(c,d);a={json.dumps(x['destination'],sort_keys=True):{'state':'resolved',**v[x['target']]} for x in m['bindings'] if x['target'] in v};get=lambda z,default=None:a.get(json.dumps(z,sort_keys=True),default or _miss());r={'scaffold_version':'0.1','service':{},'standards':{},'target':{},'functions':[],'unresolved_required_fields':[],'unmapped_author_decisions':[],'capability_inventory_state':'unknown'}
 for n in ('name','version','description'):r['service'][n]=get({'kind':'service_field','field':n})
 for n in ('uci_schema_version','ams_gra_version'):r['standards'][n]=get({'kind':'standards_field','field':n})
 for n in ('contract_version','oms_version','service_kind'):r['target'][n]=get({'kind':'context_assertion','field':n},_res(c['target'][n],'completion_target'))
 def add(f,origin,key,exchanges=[],capability=None):
  if origin=='capability':dk='capability_function_field';owner={'capability_key':key[1],'role':key[2]};name=get({**{'kind':dk},**owner,'field':'name'})
  elif origin=='component_capability':dk='component_capability_function_field';owner={'role':key[1]};name=get({**{'kind':dk},**owner,'field':'name'})
  else:dk='specific_function_field' if origin.startswith('specific') else 'required_function_field';owner={'function_key':key[1]} if origin.startswith('specific') else {'profile_function':key[1]};name=get({'kind':dk,**owner,'field':'name'}) if origin.startswith('specific') else _res(f['name'],'oms_profile')
  dest=lambda field:{'kind':dk,**owner,'field':field};item={'function_origin':origin,key[0]:key[1],'id':get(dest('id')),'name':name,'category':_res('specific','specific_function_structure') if origin.startswith('specific') else _res(f['category'],'oms_profile'),'applicability':get(dest('applicability'),_res(f['applicability'],'oms_profile') if 'applicability' in f else _miss()),'not_applicable_reason':get(dest('not_applicable_reason')),'description':get(dest('description')),'exchanges':[]}
  if not origin.startswith('specific'):item['required_group']=_res(f['required_group'],'oms_profile')
  if origin in {'capability','component_capability'}:item['standard_role']=_res(f['role'],'oms_profile');item.update({'capability':_res(capability,'capability') } if capability else {})
  for e in exchanges:
   ek=e.get('key',_selector(e));ex={'exchange_key':ek,'selector':_selector(e),'active':True,'kind':_res(e['kind'],'specific_function_structure' if origin.startswith('specific') else 'oms_profile')}
   for n in FIELDS[e['kind']]|NUMERIC:ex[n]=get({'kind':'specific_exchange_field','function_key':key[1],'exchange_key':ek,'field':n}) if origin.startswith('specific') else (_res(e[n],'oms_profile') if n in {'direction','mandate','timing_kind','message','name'} else get({'kind':'required_exchange_field','profile_function':key[1],'selector':ek,'field':n}))
   item['exchanges'].append(ex)
  r['functions'].append(item)
 for f in p['required_functions']:
  if c['target']['service_kind'] in f['applies_to']:add(f,'oms_profile',('profile_function',f['name']),f.get('required_exchanges',[]))
 if capabilities is not None:
  r['capability_inventory_state']='explicit_empty' if not capabilities['capabilities'] else 'declared';r['capabilities']=[]
  for cap in capabilities['capabilities']:
   item={'capability_key':cap['key']}
   for field in ('id','name','requires_position_information'):item[field]=get({'kind':'capability_field','capability_key':cap['key'],'field':field});r['unresolved_required_fields'] += [f'capabilities[{cap["key"]}].{field}'] if item[field]['state']=='missing' else []
   r['capabilities'].append(item)
  for cap in r['capabilities']:
   for role in p['required_capability_functions']:
    if role['per_capability'] and c['target']['service_kind'] in role['applies_to']:add(role,'capability',('capability_key',cap['capability_key'],role['role']),capability=cap['id']['value'] if cap['id']['state']=='resolved' else None)
  for role in p['required_capability_functions']:
   if not role['per_capability'] and c['target']['service_kind'] in role['applies_to'] and role.get('requires_position_information') and any(x['requires_position_information'].get('value') is True for x in r['capabilities']):add(role,'component_capability',('role',role['role']))
 for f in (specific or {'functions':[]})['functions']:add(f,'specific_function_structure',('function_key',f['key']),f['exchanges'])
 for f in r['functions']:
  ident=f.get('profile_function',f.get('function_key',f.get('capability_key',f.get('role'))));app=f['applicability']
  if app['state']=='missing':r['unresolved_required_fields'].append(f'functions[{ident}].applicability')
  elif app.get('value')!='not_applicable':
   for n in (('id','name') if f['function_origin'] in {'specific_function_structure','capability','component_capability'} else ('id',)):
    if f[n]['state']=='missing':r['unresolved_required_fields'].append(f'functions[{ident}].{n}')
   for e in f['exchanges']:
    req={'id','direction','mandate','timing_kind'}|({'message','topic'} if e['kind']['value']=='oms_message' else {'name'})|({'protocol','data_type','data_format','sharing_pattern'} if e['kind']['value']=='data_transfer' else set())
    for n in req:
     if e[n]['state']=='missing':r['unresolved_required_fields'].append(f"functions[{ident}].exchanges[{e['exchange_key']}].{n}")
  else:
   for e in f['exchanges']:e['active']=False
   if f['not_applicable_reason']['state']=='missing':r['unresolved_required_fields'].append(f'functions[{ident}].not_applicable_reason')
 r['unmapped_author_decisions']=[{'target':t,**x} for t,x in v.items() if t not in {q['target'] for q in m['bindings']}]
 if traceability is not None:_apply_traceability(r,c,traceability)
 return r
def _apply_traceability(scaffold,completion,traceability):
 evidence={x['id']:x for x in completion['sources']};scaffold['contract_sources']=[]
 for declaration in traceability['sources']:
  source=evidence[declaration['from_completion_source']];item={'source_key':declaration['key'],'id':declaration['id'],'title':source['title'],'uri':source['uri']}
  for field in ('document_number','date','note'):
   if field in declaration:item[field]=declaration[field]
  if 'revision' in source:item['revision']=source['revision']
  elif 'revision' in declaration:item['revision']=declaration['revision']
  scaffold['contract_sources'].append(item)
 def function(destination):
  kind=destination['kind']
  for item in scaffold['functions']:
   if kind=='required_function' and item['function_origin']=='oms_profile' and item.get('profile_function')==destination['profile_function']:return item
   if kind=='specific_function' and item['function_origin']=='specific_function_structure' and item.get('function_key')==destination['function_key']:return item
   if kind=='capability_function' and item['function_origin']=='capability' and item.get('capability_key')==destination['capability_key'] and item.get('standard_role',{}).get('value')==destination['role']:return item
   if kind=='component_capability_function' and item['function_origin']=='component_capability' and item.get('standard_role',{}).get('value')==destination['role']:return item
  return None
 for i,trace in enumerate(traceability['traces']):
  destination=trace['destination'];kind=destination['kind'];target=function(destination)
  if kind=='required_exchange':target=function({'kind':'required_function','profile_function':destination['profile_function']})
  if kind=='specific_exchange':target=function({'kind':'specific_function','function_key':destination['function_key']})
  if not target:
   code=CA_INACTIVE_TRACE_TARGET if kind=='component_capability_function' else CA_UNKNOWN_TRACE_TARGET
   scaffold.setdefault('traceability_diagnostics',[]).append(Diagnostic(code,f'$.traces[{i}].destination','trace destination is not active in scaffold'));continue
  entry={'source_key':trace['source_key'],'source':next(x['id'] for x in scaffold['contract_sources'] if x['source_key']==trace['source_key'])}
  for field in ('locator','note'):
   if field in trace:entry[field]=trace[field]
  if kind.endswith('exchange'):
   selector=destination['selector'] if kind=='required_exchange' else destination['exchange_key'];exchange=next((x for x in target['exchanges'] if x['exchange_key']==selector),None)
   if not exchange:scaffold.setdefault('traceability_diagnostics',[]).append(Diagnostic(CA_UNKNOWN_TRACE_TARGET,f'$.traces[{i}].destination','unknown trace exchange target'))
   elif not exchange['active']:scaffold.setdefault('traceability_diagnostics',[]).append(Diagnostic(CA_INACTIVE_TRACE_TARGET,f'$.traces[{i}].destination','trace exchange target is inactive'))
   else:exchange.setdefault('traceability',[]).append(entry)
  else:target.setdefault('traceability',[]).append(entry)
def render_json(s):return json.dumps(s,indent=2,ensure_ascii=False)+'\n'
def render_markdown(s):return '# Completion authoring scaffold\n\n'+'\n'.join(f'- `{x}`' for x in s['unresolved_required_fields'])+'\n'
def main(argv=None):
 q=argparse.ArgumentParser(description=__doc__)
 for x,y in [(('--input',),{'type':Path,'required':True}),(('--decisions',),{'type':Path,'required':True}),(('--mapping',),{'type':Path,'required':True}),(('--specific-functions',),{'type':Path}),(('--capabilities',),{'type':Path}),(('--traceability',),{'type':Path}),(('--profile',),{'type':Path,'required':True}),(('--format',),{'choices':('markdown','json'),'required':True})]:q.add_argument(*x,**y)
 x=q.parse_args(argv);c,ds=load_completion_path(x.input.resolve());d=s=caps=traces=None
 if not ds:d,ds=load_decisions_path(x.decisions.resolve(),c)
 if not ds and x.specific_functions:s,ds=load_specific_functions_path(x.specific_functions.resolve())
 if not ds and x.capabilities:caps,ds=load_capabilities_path(x.capabilities.resolve())
 if not ds and x.traceability:traces,ds=load_traceability_path(x.traceability.resolve(),c)
 if not ds:p,ds=validate_profile_path(x.profile.resolve())
 if not ds:m,ds=load_mapping_path(x.mapping.resolve(),c,d,p,s,caps)
 if ds:
  for z in ds:print(f'FAIL {z}',file=sys.stderr)
  return 1
 scaffold=build_scaffold(c,d,m,p,s,caps,traces)
 if scaffold.get('traceability_diagnostics'):
  for z in scaffold['traceability_diagnostics']:print(f'FAIL {z}',file=sys.stderr)
  return 1
 print(render_json(scaffold) if x.format=='json' else render_markdown(scaffold),end='');return 0
if __name__=='__main__':raise SystemExit(main())
