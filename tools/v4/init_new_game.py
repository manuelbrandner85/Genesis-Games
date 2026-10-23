"""GENESIS V4: create a COMPLETELY NEW, separate Unreal C++ project.
DRY RUN BY DEFAULT. --apply creates only if directory does NOT exist. Never touches old repo.
Does not install Unreal/Blender, use paid services, push to GitHub, or claim game works.
"""
from __future__ import annotations
from pathlib import Path
import argparse, hashlib, json, shutil, sys

PACKAGE = Path(__file__).resolve().parents[2]
TEMPLATE = PACKAGE / 'templates' / 'new_game'
REQUIRED = ['Genesis.uproject', 'Source/Genesis/Genesis.Build.cs', 'Source/GenesisEditor.Target.cs', 'CLAUDE.md']
COPY_ITEMS = ['.claude', 'agents', 'docs', 'tools', 'templates', 'original_md_unveraendert',
    'CLAUDE.md', 'README.md', 'START_HIER_V4.md', 'GENESIS_CLAUDE_CODE_MASTERPROMPT_V4.md',
    'GENESIS_GODMODE_V3_ALLE_12_VERBESSERUNGEN.md',
    'GENESIS_CLAUDE_CODE_MASTERPROMPT_V2.md', 'GENESIS_CLAUDE_CODE_MASTERPROMPT_V3.md',
    '01_KANON_UND_FEATURES.md', '02_AGENTEN_ARCHITEKTUR.md',
    '03_BLENDER_UNREAL_REFERENZPIPELINE.md', '04_ARBEITSPAKETE.md', '05_QA_ABNAHME.md']


def validate_target(target: Path) -> Path:
    target = target.resolve()
    if target.exists():
        raise ValueError('TARGET_EXISTS: target MUST NOT exist. Choose an entirely new empty path.')
    if target == PACKAGE or PACKAGE in target.parents or target in PACKAGE.parents:
        raise ValueError('PACKAGE_COLLISION: target must be separate from handoff package.')
    for parent in target.parents:
        if (parent/'.git').exists() and (parent/'Genesis.uproject').exists():
            raise ValueError('OLD_REPO_COLLISION: cannot create inside an existing Genesis repo.')
    return target


def file_plan():
    todo=[]
    for d in COPY_ITEMS:
        src=PACKAGE/d
        if not src.exists(): raise FileNotFoundError('MISSING V4 SOURCE: '+d)
        fs=[src] if src.is_file() else [p for p in src.rglob('*') if p.is_file()]
        for f in fs:
            if f.is_symlink() or '__pycache__' in f.parts: continue
            todo.append((f, f.relative_to(PACKAGE)))
    for f in TEMPLATE.rglob('*'):
        if f.is_file() and not f.is_symlink():
            dest=f.relative_to(TEMPLATE)
            if dest not in {rel for _,rel in todo}:
                todo.append((f,dest))
    return todo


def plan(target:Path,engine_association:str,apply=False):
    target=validate_target(target)
    if not engine_association or not all(c.isalnum() or c in '-_.' for c in engine_association):
        raise ValueError('ENGINE_ASSOCIATION_REQUIRED: exact locally verified Unreal engine association')
    files=file_plan()
    report={'mode':'APPLY_TO_NEW_DIR_ONLY' if apply else 'DRY_RUN',
            'target':str(target), 'engine_association':engine_association,
            'files':len(files),'would_modify_old_repo':False,
            'original_story_included':False,
            'status':'PROJECT_SCAFFOLD_ONLY_NOT_BUILT'}
    if apply:
        # exclusive mkdir prevents overwriting even if target appears between validation and apply
        target.mkdir(parents=True,exist_ok=False)
        for source,rel in files:
            dest=target/rel
            dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists():
                raise FileExistsError('Internal template collision: '+str(rel))
            if rel.as_posix()=='Genesis.uproject':
                data=source.read_text(encoding='utf-8').replace('__ENGINE_ASSOCIATION__',engine_association)
                dest.write_text(data,encoding='utf-8')
            else:
                shutil.copy2(source,dest)
        report['created']=True
        report['next']='Open Genesis.uproject locally, compile with matching Unreal engine, read CLAUDE.md, G0-G10.'
    return report


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--target',type=Path,required=True)
    ap.add_argument('--engine-association',required=True)
    ap.add_argument('--apply',action='store_true')
    a=ap.parse_args()
    try: print(json.dumps(plan(a.target,a.engine_association,a.apply),ensure_ascii=False,indent=2))
    except Exception as e: raise SystemExit('BLOCKED: '+str(e))
if __name__=='__main__': main()
