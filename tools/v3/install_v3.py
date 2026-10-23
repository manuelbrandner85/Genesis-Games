"""Safe additive installer. Default DRY-RUN. --apply creates missing only; never overwrites.
THIS IS NOT A MIGRATOR. Review conflicting configs and manually merge to enable V3.
"""
from __future__ import annotations
from pathlib import Path
import argparse, hashlib, json, shutil, sys
ROOT=Path(__file__).resolve().parents[2]
SKIP={'.gitignore','DATEIMANIFEST_SHA256.json','SOURCEMANIFEST_V3.json'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def plan(repo,apply=False):
    repo=repo.resolve()
    if not (repo/'Genesis.uproject').is_file() or not (repo/'.git').exists():raise ValueError('Target must be an EXISTING GENESIS git repo (.git and Genesis.uproject)')
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.relative_to(ROOT).as_posix() not in SKIP and not '__pycache__' in p.parts)
    info={'mode':'APPLY_MISSING_ONLY' if apply else 'DRY_RUN','source':str(ROOT),'repo':str(repo),'new':[],'identical':[],'conflicts_skip':[]}
    for p in files:
        rel=p.relative_to(ROOT); dst=repo/rel
        if dst.exists():
            (info['identical'] if dst.is_file() and sha(p)==sha(dst) else info['conflicts_skip']).append(rel.as_posix())
        else:
            info['new'].append(rel.as_posix())
            if apply:
                dst.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(p,dst)
    info['note']='Configuration collisions require MANUAL diff/merge, especially CLAUDE.md, .claude/settings.json, existing V2 agent files.'
    return info

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--apply',action='store_true');ap.add_argument('--report',type=Path)
    a=ap.parse_args()
    try:out=plan(a.repo,a.apply)
    except Exception as e:raise SystemExit('BLOCKED: '+str(e))
    data=json.dumps(out,indent=2,ensure_ascii=False)
    print(data)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(data,encoding='utf-8')
    if out['conflicts_skip']:print('NOTICE: manual configuration merge required; installer never overwrites.',file=sys.stderr)
if __name__=='__main__':main()
