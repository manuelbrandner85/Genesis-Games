"""Baseline hashes for explicitly named SOURCE files; guard only detects changes, is not a sandbox."""
from __future__ import annotations
from pathlib import Path
import json, argparse, hashlib

def inside(repo,text):
    p=(repo/text).resolve() if not Path(text).is_absolute() else Path(text).resolve()
    if not p.is_relative_to(repo.resolve()):raise ValueError('path outside repo: '+str(text))
    if not p.is_file():raise ValueError('source absent: '+str(text))
    return p

def manifest(repo,names):
    return {str(inside(repo,n).relative_to(repo.resolve())).replace('\\','/'):hashlib.sha256(inside(repo,n).read_bytes()).hexdigest() for n in names}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['baseline','verify']);ap.add_argument('--repo',required=True,type=Path);ap.add_argument('--manifest',required=True,type=Path);ap.add_argument('--files',nargs='*',default=[]);a=ap.parse_args();repo=a.repo.resolve()
    if not (repo/'.git').exists() or not (repo/'Genesis.uproject').exists():raise SystemExit('BLOCKED_WRONG_REPO')
    if a.mode=='baseline':
        if not a.files:raise SystemExit('BLOCKED_SOURCE_MISSING: explicit --files required, never guess protected paths')
        if a.manifest.exists():raise SystemExit('BLOCKED_EXISTING_MANIFEST: never silently overwrite baseline')
        info=manifest(repo,a.files);a.manifest.parent.mkdir(parents=True,exist_ok=True);a.manifest.write_text(json.dumps(info,indent=2),encoding='utf-8');print('BASELINE_RECORDED',len(info))
    else:
        if not a.manifest.is_file():raise SystemExit('BLOCKED_NO_BASELINE')
        baseline=json.loads(a.manifest.read_text('utf-8'))
        if not baseline:raise SystemExit('BLOCKED_EMPTY_BASELINE')
        errors=[]
        for n,digest in baseline.items():
            try:actual=hashlib.sha256(inside(repo,n).read_bytes()).hexdigest()
            except ValueError as e:errors.append(str(e));continue
            if actual!=digest:errors.append(n+' has changed')
        print(json.dumps({'verified':not errors,'baseline_count':len(baseline),'changes':errors},ensure_ascii=False,indent=2))
        if errors:raise SystemExit(1)
if __name__=='__main__':main()
