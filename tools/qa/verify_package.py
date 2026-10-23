"""Independent static pack validation; cannot validate Blender, Unreal, visuals or runtime."""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,csv,re,sys,ast
ROOT=Path(__file__).resolve().parents[2]
REQUIRED=['CLAUDE.md','START_HIER.md','GENESIS_CLAUDE_CODE_MASTERPROMPT_V2.md',
         'original_md_unveraendert/GAMEFORGE_Verbesserung_03_Ultimate_Living_World_Simulation_GODMODE.md',
         '.claude/settings.json','docs/produktion/GAMEFORGE03_50_FEATURES_MATRIX.csv']
EXPECTED_HASH='3f57041e3534c66220e83d7e7d3c9a0f45da613477bfe7d58aa9333f41b511af'
def validate(root=ROOT):
 errors=[];info={}
 for p in REQUIRED:
  if not (root/p).is_file():errors.append('missing: '+p)
 ag=sorted((root/'.claude/agents').glob('genesis-*.md'));sk=sorted((root/'.claude/skills').glob('*/SKILL.md'));imp=list((root/'docs/verbesserungen_01_bis_10').glob('*.md'))
 info.update(agents=len(ag),skills=len(sk),improvements=len(imp))
 for k,num in [('agents',24),('improvements',10)]:
  if info[k]!=num:errors.append(f'{k} must be {num}; found {info[k]}')
 if info['skills']<11:errors.append(f'V2 requires at least 11 skills; found {info["skills"]}')
 for path in ag:
  t=path.read_text('utf-8')
  if not re.search(r'\A---\s*\nname: genesis-[a-z-]+\n.*\n---\n',t,re.S) or 'tools:' not in t:errors.append('agent frontmatter: '+path.name)
 for path in sk:
  t=path.read_text('utf-8')
  if not t.startswith('---\nname:') or 'description:' not in t:errors.append('skill frontmatter: '+str(path))
 for path in [root/'.claude/settings.json',*list((root/'templates').glob('*.json'))]:
  try:json.loads(path.read_text('utf-8-sig'))
  except Exception as e:errors.append(f'invalid JSON {path.name}: {e}')
 src=root/'original_md_unveraendert/GAMEFORGE_Verbesserung_03_Ultimate_Living_World_Simulation_GODMODE.md'
 if src.is_file():
  info['original_sha256']=hashlib.sha256(src.read_bytes()).hexdigest()
  if info['original_sha256']!=EXPECTED_HASH:errors.append('uploaded original md sha mismatch')
 matrix=root/'docs/produktion/GAMEFORGE03_50_FEATURES_MATRIX.csv'
 if matrix.is_file():
  with matrix.open('r',encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
  nums=[int(r['Funktion']) for r in rows];info['living_world_rows']=len(rows)
  if nums!=list(range(1,51)):errors.append('living world matrix not exactly 01..50')
 for p in (root/'tools').rglob('*.py'):
  try:ast.parse(p.read_text('utf-8'))
  except Exception as e:errors.append(f'python syntax error {p.relative_to(root)}: {e}')
 info['checks']='STATIC_ONLY_NOT_UNREAL_OR_BLENDER'
 return errors,info
if __name__=='__main__':
 errs,info=validate();print(json.dumps({'ok':not errs,'errors':errs,'info':info},indent=2,ensure_ascii=False));sys.exit(1 if errs else 0)
