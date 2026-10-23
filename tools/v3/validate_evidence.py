"""Fail-closed evidence checker for a V3 work order or Gold Slice gate list.
Does not infer aesthetics, rights or successful gameplay from a file's existence.
"""
from __future__ import annotations
from pathlib import Path
import argparse,json,hashlib,re,sys
STATUSES={'SPECIFIED','NOT_RUN','BLOCKED_SOURCE','BLOCKED_TOOL','WAITING_APPROVAL','BUILT_UNTESTED','ENGINE_VERIFIED','HUMAN_REVIEWED','ACCEPTED','FAILED'}

def evaluate(data,base):
    errors=[];items=data.get('gates') if isinstance(data,dict) and 'gates' in data else [data]
    if not isinstance(items,list):return ['Invalid gates collection']
    for item in items:
        if not isinstance(item,dict):errors.append('Invalid item');continue
        key=str(item.get('gate_id',item.get('work_id','UNKNOWN')))
        status=item.get('status','NOT_RUN');paths=item.get('evidence_paths',[])
        if status not in STATUSES:errors.append(f'{key}: unknown status {status}')
        if not isinstance(paths,list):errors.append(f'{key}: evidence_paths must list');continue
        if status in ('ENGINE_VERIFIED','HUMAN_REVIEWED','ACCEPTED') and not paths:errors.append(f'{key}: evidence absent')
        if status in ('HUMAN_REVIEWED','ACCEPTED') and not item.get('reviewer'):errors.append(f'{key}: independent reviewer absent')
        if status=='ACCEPTED' and not item.get('approval_id'):errors.append(f'{key}: owner approval_id absent')
        for rel in paths:
            p=(base/str(rel)).resolve()
            if not p.is_relative_to(base.resolve()) or not p.is_file() or p.stat().st_size==0:errors.append(f'{key}: evidence missing or outside root {rel}')
    return errors

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--status',type=Path,required=True);ap.add_argument('--root',type=Path,default=Path.cwd());a=ap.parse_args()
    data=json.loads(a.status.read_text('utf-8'));errs=evaluate(data,a.root)
    print(json.dumps({'valid':not errs,'status_file':str(a.status),'errors':errs,'note':'File existence is not an actual runtime/creative verification'},indent=2,ensure_ascii=False))
    if errs:sys.exit(1)
if __name__=='__main__':main()
