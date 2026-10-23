"""Install project handoff without overwriting existing files.
Default is DRY RUN. --apply copies only missing files. Never pushes or commits.
"""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys

PACKAGE=Path(__file__).resolve().parents[1]
# Complete handoff, including prior source references. All destination collisions are skipped.
SOURCES=[
 '.claude/agents','.claude/skills','.claude/hooks','.claude/settings.json',
 'agents','templates',
 'tools/pipeline','tools/blender','tools/unreal','tools/qa',
 'tools/blender_smoke_crate.py','tools/unreal_import_smoke.py',
 'docs/verbesserungen_01_bis_10','docs/produktion','docs/production-status',
 'original_md_unveraendert',
 'CLAUDE.md','START_HIER.md','README.md',
 'GENESIS_CLAUDE_CODE_MASTERPROMPT.md','GENESIS_CLAUDE_CODE_MASTERPROMPT_V2.md',
 '01_KANON_UND_FEATURES.md','02_AGENTEN_ARCHITEKTUR.md','03_BLENDER_UNREAL_REFERENZPIPELINE.md',
 '04_ARBEITSPAKETE.md','05_QA_ABNAHME.md','06_REPO_BESTAND_UND_QUELLEN.md',
 '07_REFERENZBIBEL_TEMPLATE.md','08_RISIKEN_FREIGABEN.md','09_GAMEFORGE_LIVING_WORLD_INTEGRATION.md',
 'QUELLEN_LESEN_UND_SHA256.md'
]


def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description='GENESIS package installer (dry-run by default)')
 p.add_argument('--repo',type=Path,required=True)
 p.add_argument('--apply',action='store_true',help='Explicitly copy missing files; NEVER overwrite')
 args=p.parse_args();dest=args.repo.resolve()
 if not dest.is_dir() or not (dest/'Genesis.uproject').is_file():
  raise SystemExit('ERROR: target must be an existing GENESIS repository with Genesis.uproject')
 if not (dest/'.git').exists():raise SystemExit('ERROR: existing git repository required')
 plan=[]; collisions=[];copied=[]
 for relative in SOURCES:
  source=PACKAGE/relative
  if not source.exists():raise SystemExit('PACKAGE_BROKEN missing: '+relative)
  files=[source] if source.is_file() else sorted(p for p in source.rglob('*') if p.is_file())
  for file in files:
   rel=file.relative_to(PACKAGE); target=dest/rel
   if target.exists():
    status='IDENTICAL' if sha(target)==sha(file) else 'CONFLICT_SKIP'
    if status=='CONFLICT_SKIP':collisions.append(str(rel))
   else:status='COPY' if args.apply else 'WOULD_COPY'
   plan.append({'path':str(rel),'action':status})
   if args.apply and status=='COPY':
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,target);copied.append(str(rel))
 print(json.dumps({'mode':'APPLY_MISSING_ONLY' if args.apply else 'DRY_RUN','repo':str(dest),'files':len(plan),'copied':len(copied),'collisions':collisions,'actions':plan},ensure_ascii=False,indent=2))
 if collisions:print('NOTICE: conflicts preserved; merge manually after review, especially .claude/settings.json and CLAUDE.md.',file=sys.stderr)
if __name__=='__main__':main()
