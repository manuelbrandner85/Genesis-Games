"""A conservative Blender smoke runner; UE import is a separate explicitly approved Editor step."""
from __future__ import annotations
from pathlib import Path
import argparse, subprocess, json, shutil, os, hashlib

def main():
    ap=argparse.ArgumentParser(description='Only creates basic test geometry, NOT a production asset')
    ap.add_argument('--blender',default=os.environ.get('BLENDER_EXE') or shutil.which('blender'))
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--execute',action='store_true',help='Explicitly start installed Blender')
    ns=ap.parse_args();out=ns.output.resolve();base=Path(__file__).resolve().parents[1]
    script=base/'blender_smoke_crate.py'
    if not ns.execute:
        print(json.dumps({'status':'PLANNED_NOT_EXECUTED','blender':ns.blender,'script':str(script),'output':str(out)},indent=2));return
    if not ns.blender or not Path(ns.blender).is_file() and not shutil.which(ns.blender):
        raise SystemExit('BLOCKED_TOOL_MISSING: Blender executable not found')
    out.mkdir(parents=True,exist_ok=True)
    command=[str(ns.blender),'-b','--python',str(script),'--',str(out)]
    with (out/'blender_run.log').open('w',encoding='utf-8') as log:
        cp=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=False,timeout=900)
    required=[out/'TEST_SMOKE_CRATE_001.blend',out/'TEST_SMOKE_CRATE_001.fbx',out/'TEST_SMOKE_CRATE_001.glb']
    ok=cp.returncode==0 and all(p.is_file() and p.stat().st_size>1000 for p in required)
    print(json.dumps({'status':'BLENDER_SMOKE_PASS_UNREAL_NOT_TESTED' if ok else 'TEST_FAILED','exit_code':cp.returncode,'file_checks':{p.name:p.is_file() for p in required},'log':str(out/'blender_run.log')},indent=2))
    if not ok:raise SystemExit(1)
if __name__=='__main__':main()
