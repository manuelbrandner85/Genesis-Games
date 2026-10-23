"""Read-only hash inventory of a user-provided original source directory.
This NEVER infers approval from filename and NEVER modifies input sources.
"""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,datetime
ALLOW={'.md','.txt','.json','.pdf','.doc','.docx','.zip','.png','.jpg','.jpeg','.wav','.mp3','.mp4','.blend','.fbx','.glb','.gltf'}

def audit(folder:Path):
    folder=folder.resolve()
    if not folder.is_dir(): raise ValueError('Not a source directory')
    rows=[]
    for f in sorted(folder.rglob('*')):
        if not f.is_file() or f.suffix.lower() not in ALLOW or f.is_symlink(): continue
        with f.open('rb') as fh:
            digest=hashlib.file_digest(fh,'sha256').hexdigest() # read-only
        rows.append({'path':str(f),'relative_path':f.relative_to(folder).as_posix(),
                     'bytes':f.stat().st_size,'sha256':digest,'canon_approval':'UNVERIFIED','story_status':'NOT_READ'})
    return {'root':str(folder),'files':rows,'total_files':len(rows),
            'approval_state':'DIRECTOR_AND_SOURCE_VERIFICATION_REQUIRED',
            'warning':'Hash inventory is NOT proof of canon approval or source completeness.'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 r=audit(a.sources)
 if a.out.resolve().is_relative_to(a.sources.resolve()):raise SystemExit('BLOCKED: report cannot be written inside protected original source directory')
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'status':'SOURCE_INVENTORY_ONLY','files':r['total_files'],'report':str(a.out)},ensure_ascii=False))
if __name__=='__main__':main()
