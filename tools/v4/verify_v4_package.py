"""Static package verification for V4. NOT an Unreal/Blender runtime test."""
from __future__ import annotations
import csv, hashlib, json, sys, ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ORIGINAL='original_md_unveraendert/GAMEFORGE_Verbesserung_03_Ultimate_Living_World_Simulation_GODMODE.md'
ORIGINAL_SHA='3f57041e3534c66220e83d7e7d3c9a0f45da613477bfe7d58aa9333f41b511af'

def verify(root=ROOT):
    errors=[]; counts={}
    required=['CLAUDE.md','GENESIS_CLAUDE_CODE_MASTERPROMPT_V4.md','START_HIER_V4.md',ORIGINAL,
       'templates/new_game/Genesis.uproject','tools/v4/init_new_game.py',
       'tools/v4/blender_smoke_prop.py','tools/v4/source_audit.py',
       'tools/v4/hooks/claude_pretool_guard.py',
       'docs/v4/QUELLEN_UND_KANON_SICHERN.md','docs/v4/GOLDSTANDARD_NEUSTART_GATES.md',
       'docs/godmode_v3/V3_TEST_CASE_MATRIX.csv','docs/produktion/GAMEFORGE03_50_FEATURES_MATRIX.csv']
    for r in required:
        if not (root/r).is_file():errors.append('missing '+r)
    original=root/ORIGINAL
    if original.is_file() and hashlib.sha256(original.read_bytes()).hexdigest()!=ORIGINAL_SHA:
        errors.append('ORIGINAL_GODMODE_MD_HASH_MISMATCH')
    patterns={'agents':'.claude/agents/genesis-*.md','v2_specs':'docs/verbesserungen_01_bis_10/VERBESSERUNG_*.md',
              'v3_specs':'docs/godmode_v3/verbesserungen/V3-*.md','skills':'.claude/skills/*/SKILL.md',
              'v4_skills':'.claude/skills/genesis-v4-*/SKILL.md'}
    for k,pat in patterns.items():counts[k]=len(list(root.glob(pat)))
    for k,n in [('agents',24),('v2_specs',10),('v3_specs',12),('skills',23),('v4_skills',5)]:
        if counts[k]!=n:errors.append(f'{k} expected {n}, got {counts[k]}')
    for name,n in [('docs/produktion/GAMEFORGE03_50_FEATURES_MATRIX.csv',50),('docs/godmode_v3/V3_TEST_CASE_MATRIX.csv',48)]:
        p=root/name
        if p.is_file():
            with p.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
            counts[p.name]=len(rows)
            if len(rows)!=n:errors.append(f'{p.name} should contain {n} rows')
    gates=root/'docs/v4/GOLDSTANDARD_NEUSTART_GATES.md'
    if gates.is_file() and any(f'| G{i} |' not in gates.read_text('utf-8') for i in range(11)):
        errors.append('missing G0-G10 in V4 gates')
    for p in root.rglob('*.py'):
        if '__pycache__' in p.parts:continue
        try:ast.parse(p.read_text('utf-8'))
        except Exception as ex: errors.append(f'syntax: {p.relative_to(root)}: {ex}')
    conf=root/'.claude/settings.json'
    if conf.is_file():
        try:
            data=json.loads(conf.read_text('utf-8'))
            if not data.get('hooks',{}).get('PreToolUse'):errors.append('missing pretool hook')
        except Exception as ex:errors.append('settings invalid '+str(ex))
    counts['scope']='STATIC_ONLY_UNREAL_AND_BLENDER_NOT_RUN'
    return errors,counts

if __name__=='__main__':
    errors,counts=verify()
    print(json.dumps({'ok':not errors,'errors':errors,'counts':counts},ensure_ascii=False,indent=2))
    sys.exit(bool(errors))
