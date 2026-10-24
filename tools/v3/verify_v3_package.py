"""Static package integrity checker. Never implies Unreal/Blender runtime success."""
from __future__ import annotations
from pathlib import Path
import csv, hashlib, json, re, sys, ast

ROOT=Path(__file__).resolve().parents[2]
SOURCE='original_md_unveraendert/GAMEFORGE_Verbesserung_03_Ultimate_Living_World_Simulation_GODMODE.md'
SOURCE_HASH='3f57041e3534c66220e83d7e7d3c9a0f45da613477bfe7d58aa9333f41b511af'

def verify(root=ROOT):
    errors=[]; stats={}
    required=['CLAUDE.md','GENESIS_CLAUDE_CODE_MASTERPROMPT_V3.md','START_HIER_V3.md',SOURCE,'docs/godmode_v3/GOLD_SLICE_GATES.json','docs/godmode_v3/V3_TEST_CASE_MATRIX.csv']
    for r in required:
        if not (root/r).is_file():errors.append('Missing '+r)
    source=root/SOURCE
    if source.exists() and hashlib.sha256(source.read_bytes()).hexdigest()!=SOURCE_HASH:errors.append('Original-MD SHA256 mismatch')
    dirs={'agents':(root/'.claude/agents').glob('genesis-*.md'),'skills':(root/'.claude/skills').glob('*/SKILL.md'),'v3_specs':(root/'docs/godmode_v3/verbesserungen').glob('V3-*.md'),'v2_specs':(root/'docs/verbesserungen_01_bis_10').glob('VERBESSERUNG_*.md')}
    is_v4=(root/'GENESIS_CLAUDE_CODE_MASTERPROMPT_V4.md').exists()
    expected={'agents':24,'skills':18,'v3_specs':12,'v2_specs':10}
    for k,gl in dirs.items():
        paths=list(gl);stats[k]=len(paths)
        if is_v4 and k=='skills':
            paths=[p for p in paths if not p.parent.name.startswith(('genesis-v4-', 'genesis-free-ai-'))]
            stats[k]=len(paths)
        if len(paths)!=expected[k]:errors.append(f'{k} expected {expected[k]}, found {len(paths)}')
        for p in paths:
            t=p.read_text('utf-8')
            if not t.startswith('---\n') and k in ('skills','agents'):errors.append('frontmatter absent '+str(p))
    matrix=root/'docs/godmode_v3/V3_TEST_CASE_MATRIX.csv'
    if matrix.is_file():
        with matrix.open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
        stats['v3_test_cases']=len(rows)
        if len(rows)!=48 or len({r['TestID'] for r in rows})!=48:errors.append('V3 test matrix expected 48 unique cases')
        if any(r['Status']!='NOT_RUN' for r in rows):errors.append('V3 tests falsely marked done')
    for p in (root/'tools').rglob('*.py'):
        try:ast.parse(p.read_text('utf-8'))
        except Exception as e:errors.append(f'Python syntax: {p}: {e}')
    for p in [root/'.claude/settings.json',root/'docs/godmode_v3/GOLD_SLICE_GATES.json',root/'docs/godmode_v3/IMPROVEMENTS_INDEX.json']:
        try: json.loads(p.read_text('utf-8'))
        except Exception as e:errors.append(f'JSON: {p}: {e}')
    gates=root/'docs/godmode_v3/GOLD_SLICE_GATES.json'
    if gates.exists():
        info=json.loads(gates.read_text('utf-8'))
        if len(info.get('gates',[]))!=9 or any(g['status']!='NOT_RUN' for g in info['gates']):errors.append('Gold slice gates must start NOT_RUN')
    recorded=root/'SOURCEMANIFEST_V3.json'
    if recorded.is_file():
        try:
            listing=json.loads(recorded.read_text('utf-8')).get('files',{})
            if is_v4:
                # Legacy V3 test only protects inherited immutable V3 files.
                # V4 intentionally replaces project root instructions and hook settings.
                changed_by_v4={'CLAUDE.md','README.md','.claude/settings.json','.gitignore','tools/v3/verify_v3_package.py'}
                original_scope={k:v for k,v in listing.items() if k not in changed_by_v4}
                actual={name:hashlib.sha256((root/name).read_bytes()).hexdigest()
                        for name in original_scope if (root/name).is_file()}
                missing=set(original_scope)-set(actual)
                bad=[n for n,v in actual.items() if original_scope[n]!=v]
                if missing or bad:
                    errors.append(f'Legacy V3 integrity changed: missing={sorted(missing)[:5]}, modified={sorted(bad)[:5]}')
            else:
                actual={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and p.name!='SOURCEMANIFEST_V3.json' and '__pycache__' not in p.parts}
                if listing!=actual:
                    missing=set(actual)-set(listing); phantom=set(listing)-set(actual)
                    bad=[n for n in set(listing)&set(actual) if listing[n]!=actual[n]]
                    errors.append(f'Integrity manifest mismatch: unknown={sorted(missing)[:5]}, nonexistent={sorted(phantom)[:5]}, changed={sorted(bad)[:5]}')
        except Exception as exc:errors.append('Integrity manifest invalid: '+str(exc))
    stats['scope']='STATIC_PACKAGE_ONLY_ENGINE_NOT_TESTED'
    return errors,stats

if __name__=='__main__':
    e,s=verify();print(json.dumps({'ok':not e,'errors':e,'stats':s},ensure_ascii=False,indent=2));sys.exit(bool(e))
