"""Strict offline manifest validation. Production status is NEVER claimed here."""
from __future__ import annotations
from pathlib import Path
import argparse, json, re, hashlib

def validate_manifest(data: dict) -> list[str]:
    errors=[]
    if not isinstance(data,dict): return ['Manifest must be a JSON object']
    aid=data.get('asset_id','')
    if not isinstance(aid,str) or not re.fullmatch(r'[A-Z0-9][A-Z0-9_\-]{2,79}',aid):
        errors.append('asset_id must be 3-80 uppercase ASCII digits/underscores/hyphens')
    dims=data.get('dimensions_m',{})
    if not isinstance(dims,dict): errors.append('dimensions_m must be an object')
    else:
        for a in ('x','y','z'):
            try:
                d=float(dims[a])
                if not (0.001<=d<=10000): raise ValueError()
            except (KeyError,TypeError,ValueError,OverflowError):errors.append(f'dimensions_m.{a} must be finite and in [0.001,10000]')
    if data.get('type') not in ('static_mesh','skeletal_mesh'):
        errors.append('type must be static_mesh or skeletal_mesh')
    if data.get('phase') != 'SMOKE_ONLY' and not data.get('story_ref'):
        errors.append('non-smoke asset requires story_ref / verified asset brief')
    if not data.get('license_status'):
        errors.append('license_status is required')
    p=data.get('ue_path','')
    if p and (not isinstance(p,str) or not p.startswith('/Game/Genesis/') or '..' in p):
        errors.append('ue_path must stay within /Game/Genesis/')
    return errors

def main():
    ap=argparse.ArgumentParser();ap.add_argument('manifest');args=ap.parse_args()
    p=Path(args.manifest)
    try: data=json.loads(p.read_text('utf-8')); errors=validate_manifest(data)
    except Exception as e: errors=[str(e)]
    print(json.dumps({'manifest':str(p),'static_valid':not errors,'errors':errors},indent=2,ensure_ascii=False))
    raise SystemExit(1 if errors else 0)
if __name__=='__main__': main()
