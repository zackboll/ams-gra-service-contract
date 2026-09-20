#!/usr/bin/env python3
"""Check or list a portable Service Contract conformance manifest."""
from __future__ import annotations
import argparse, hashlib, json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from jsonschema import Draft202012Validator
try:
 from tools.validate import Diagnostic, validate_document
 from tools.yaml_support import YamlInputError, load_path
except ModuleNotFoundError:
 from validate import Diagnostic, validate_document
 from yaml_support import YamlInputError, load_path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA=ROOT/'schema/tooling/conformance/v0.1/conformance-manifest.schema.json'
@dataclass(frozen=True)
class ConformanceDiagnostic:
 code:str; path:str; message:str
 def __str__(self): return f'{self.code} {self.path}: {self.message}' if self.path else f'{self.code} {self.message}'
def canonical_sha256(path: Path)->str:
 value=json.loads(path.read_text(encoding='utf-8'))
 canonical=json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)
 return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
def _safe_case_path(value: str)->bool:
 p=PurePosixPath(value)
 return not ('\\' in value or p.is_absolute() or '..' in p.parts or str(p)=='.')
def load_manifest(path: Path)->tuple[dict[str,Any]|None,list[ConformanceDiagnostic]]:
 try: value=load_path(path)
 except YamlInputError as exc:return None,[ConformanceDiagnostic('CF_SCHEMA','',f'could not parse manifest: {exc}')]
 errors=sorted(Draft202012Validator(json.loads(MANIFEST_SCHEMA.read_text())).iter_errors(value),key=lambda e:list(e.absolute_path))
 if errors:return None,[ConformanceDiagnostic('CF_SCHEMA','$.'+'.'.join(map(str,e.absolute_path)),e.message) for e in errors]
 return value,[]
def manifest_invariants(manifest:dict[str,Any], manifest_path:Path)->list[ConformanceDiagnostic]:
 d=[]; ids=set();paths=set(); root=manifest_path.parent.resolve()
 for i,case in enumerate(manifest['cases']):
  prefix=f'$.cases[{i}]'; cid=case['id']; rel=case['path']
  if cid in ids:d.append(ConformanceDiagnostic('CF_DUPLICATE_CASE',prefix+'.id',f'duplicate case ID {cid!r}'))
  ids.add(cid)
  if rel in paths:d.append(ConformanceDiagnostic('CF_DUPLICATE_CASE',prefix+'.path',f'duplicate case path {rel!r}'))
  paths.add(rel)
  if not _safe_case_path(rel): d.append(ConformanceDiagnostic('CF_CASE_PATH',prefix+'.path','path must be a safe relative POSIX path')) ; continue
  candidate=(root/rel).resolve()
  if root not in candidate.parents or not candidate.is_file():d.append(ConformanceDiagnostic('CF_CASE_PATH',prefix+'.path','case file must exist under conformance/v0.1'))
  if case['expect']=='valid' and case.get('reference_diagnostics'):d.append(ConformanceDiagnostic('CF_EXPECTATION',prefix,'valid cases cannot declare reference diagnostics'))
 return d
def check(manifest_path:Path)->list[ConformanceDiagnostic]:
 manifest,diags=load_manifest(manifest_path)
 if diags:return diags
 diags=manifest_invariants(manifest,manifest_path)
 schema=(ROOT/manifest['portable_schema']).resolve()
 if not schema.is_file() or canonical_sha256(schema)!=manifest['schema_canonical_sha256']:diags.append(ConformanceDiagnostic('CF_SCHEMA_FINGERPRINT','$.schema_canonical_sha256','portable schema canonical SHA-256 differs'))
 values={}
 for case in manifest['cases']:
  path=manifest_path.parent/case['path']
  try: value=load_path(path); values[case['id']]=value; reference=validate_document(value)
  except YamlInputError as exc:
   reference=[Diagnostic('SC_SCHEMA','',str(exc))]
  accepted=not reference
  if accepted != (case['expect']=='valid'):diags.append(ConformanceDiagnostic('CF_EXPECTATION',case['id'],f"expected {case['expect']}, reference validator {'accepted' if accepted else 'rejected'}"))
  expected=case.get('reference_diagnostics',[]); actual={x.code for x in reference}
  if expected and set(expected)!=actual:diags.append(ConformanceDiagnostic('CF_REFERENCE_DIAGNOSTIC',case['id'],f'expected {expected}, got {sorted(actual)}'))
 groups={}
 for case in manifest['cases']:
  if 'equivalence_group' in case:groups.setdefault(case['equivalence_group'],[]).append(case)
 for group,cases in groups.items():
  if len(cases)<2 or any(c['expect']!='valid' for c in cases):diags.append(ConformanceDiagnostic('CF_EQUIVALENCE',group,'group needs at least two valid cases'));continue
  first=values.get(cases[0]['id'])
  if any(values.get(c['id'])!=first for c in cases[1:]):diags.append(ConformanceDiagnostic('CF_EQUIVALENCE',group,'cases are not semantically equal'))
 return diags
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=('check','list'));p.add_argument('manifest',type=Path);a=p.parse_args(argv)
 manifest,diags=load_manifest(a.manifest)
 if a.command=='list' and not diags:
  for c in manifest['cases']:print(f"{c['expect']:7} {c['id']:45} {c['path']}")
  return 0
 diags=check(a.manifest)
 if diags:
  for d in diags:print(d)
  return 1
 print(f"OK: {len(manifest['cases'])} conformance cases")
 return 0
if __name__=='__main__':raise SystemExit(main())
