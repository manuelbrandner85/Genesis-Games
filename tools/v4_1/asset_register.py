"""Provenance registry: must have real existing file. Never grants final QA by itself."""
import argparse,hashlib,json,time,re
from pathlib import Path

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block)
    return h.hexdigest()

def build_record(artifact,asset_id,tool_id,model_id,source_ref,license_ref,status):
    if not artifact.is_file():raise FileNotFoundError(artifact)
    if not re.fullmatch('[A-Za-z0-9][A-Za-z0-9._-]{1,100}',asset_id):raise ValueError('Bad asset ID')
    if status not in ('GENERATED_PREVIEW','BLENDER_VALIDATED','UNREAL_VALIDATED','QA_REVIEWED'):
        raise ValueError('This script cannot mark DIRECTOR_ACCEPTED')
    if not license_ref or not source_ref:raise ValueError('Cannot register without provenance and license source')
    return {'asset_id':asset_id,'sha256':sha256(artifact),'bytes':artifact.stat().st_size,'path':str(artifact.resolve()),'tool_id':tool_id,'model_id':model_id,'source_ref':source_ref,'license_ref':license_ref,'status':status,'registered_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'note':'A file hash does not prove license validity, image fidelity or Unreal import.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--file',type=Path,required=True);ap.add_argument('--asset-id',required=True);ap.add_argument('--tool-id',required=True);ap.add_argument('--model-id',required=True);ap.add_argument('--source-ref',required=True);ap.add_argument('--license-ref',required=True);ap.add_argument('--status',default='GENERATED_PREVIEW');ap.add_argument('--registry',type=Path,required=True);args=ap.parse_args()
    r=build_record(args.file,args.asset_id,args.tool_id,args.model_id,args.source_ref,args.license_ref,args.status)
    args.registry.parent.mkdir(parents=True,exist_ok=True)
    with args.registry.open('a',encoding='utf8') as f:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    print(json.dumps(r,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
