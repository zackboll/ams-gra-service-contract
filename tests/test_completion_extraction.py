import json
from copy import deepcopy
from pathlib import Path
import subprocess, sys
from tools.completion_extract import build_completion_input, extract_candidates, load_extraction_recipe, verify_sources
from tools.yaml_support import load_path, load_text
ROOT=Path(__file__).resolve().parents[1]; FIX=ROOT/"tests/fixtures/completion-extraction"; CLI=ROOT/"tools/completion.py"
def run(*args): return subprocess.run([sys.executable,str(CLI),"extract",*map(str,args)],cwd=ROOT,capture_output=True,text=True)
def prepared():
 r,d=load_extraction_recipe(FIX/"recipe.yaml"); assert not d
 s,d=verify_sources(r,FIX/"source"); assert not d
 return r,s
def test_synthetic_extraction_order_metadata_and_formats():
 r,s=prepared(); c,d=extract_candidates(r,s); assert not d
 document,d=build_completion_input(r,c); assert not d
 assert [x["id"] for x in document["sources"]]==["text","json","yaml"]
 assert [x["id"] for x in document["candidates"]]==["version","enabled","periodic","topic","item","rate"]
 assert all("local_path" not in x and "sha256" not in x for x in document["sources"])
 yaml=run(FIX/"recipe.yaml","--source-root",FIX/"source","--format","yaml"); js=run(FIX/"recipe.yaml","--source-root",FIX/"source","--format","json")
 assert yaml.returncode==js.returncode==0 and load_path(FIX/"recipe.yaml")["target"]==json.loads(js.stdout)["target"]
 assert json.loads(js.stdout)==load_text(yaml.stdout)
def test_fail_closed_hash_path_match_and_pointer(tmp_path):
 r,s=prepared()
 bad=deepcopy(r); bad["sources"][0]["sha256"]="0"*64
 assert verify_sources(bad,FIX/"source")[1][0].code=="CA_EXTRACTION_HASH"
 bad=deepcopy(r); bad["sources"][0]["local_path"]="../primary.md"
 assert verify_sources(bad,FIX/"source")[1][0].code=="CA_EXTRACTION_PATH"
 bad=deepcopy(r); bad["rules"][0]["extractor"]["pattern"]="missing"
 assert extract_candidates(bad,s)[1][0].code=="CA_EXTRACTION_MATCH"
 bad=deepcopy(r); bad["rules"][3]["extractor"]["pointer"]="/items"
 assert extract_candidates(bad,s)[1][0].code=="CA_EXTRACTION_POINTER"
 output=tmp_path/"out.yaml"; badpath=tmp_path/"bad.yaml"; badpath.write_text("extraction_version: 'no'\n")
 result=run(badpath,"--source-root",FIX/"source","--output",output)
 assert result.returncode and result.stdout=="" and not output.exists() and "Traceback" not in result.stderr
def test_safe_output_and_rf_parity(tmp_path):
 output=tmp_path/"out.yaml"; args=(FIX/"recipe.yaml","--source-root",FIX/"source","--output",output)
 assert run(*args).returncode==0 and output.exists()
 assert "CA_OUTPUT_EXISTS" in run(*args).stderr and run(*args,"--force").returncode==0
 rf=ROOT/"examples/completion/rf-fm-demod-extraction.yaml"
 result=run(rf,"--source-root","/tmp/rf-fm-demod","--format","json")
 if Path("/tmp/rf-fm-demod").is_dir(): assert result.returncode==0 and json.loads(result.stdout)==load_path(ROOT/"examples/completion/rf-fm-demod.yaml")
