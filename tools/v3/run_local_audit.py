"""Runs an explicitly approved LOCAL audit. Default: dry run. No shell=True or installers.
Usage: python tools/v3/run_local_audit.py blender --exe "C:\\...\\blender.exe" --scene file.blend --out report.json --execute
       python tools/v3/run_local_audit.py unreal --exe "C:\\...\\UnrealEditor-Cmd.exe" --uproject file.uproject --asset /Game/Genesis/X --out report.json --execute
"""
from __future__ import annotations
from pathlib import Path
import argparse,sys,subprocess,os,json
BASE=Path(__file__).resolve().parent

def configure(a):
    exe=Path(a.exe).resolve();out=Path(a.out).resolve()
    if not exe.is_file():raise ValueError('local executable not found: '+str(exe))
    env=os.environ.copy()
    if a.tool=='blender':
        scene=Path(a.scene).resolve()
        if not scene.is_file() or scene.suffix.lower()!='.blend':raise ValueError('existing .blend required')
        command=[str(exe),'-b',str(scene),'--python',str(BASE/'blender_scene_audit.py'),'--','--out',str(out)]
    else:
        project=Path(a.uproject).resolve()
        if not project.is_file() or project.suffix.lower()!='.uproject':raise ValueError('existing .uproject required')
        if not a.asset or not a.asset.startswith('/Game/Genesis/'):raise ValueError('GENESIS asset path required')
        env.update(GENESIS_V3_UE_ASSET=a.asset,GENESIS_V3_REPORT=str(out))
        command=[str(exe),str(project),'-unattended','-nop4',f'-ExecutePythonScript={BASE/"unreal_asset_audit.py"}']
    return command,env,out

def main():
    p=argparse.ArgumentParser();p.add_argument('tool',choices=['blender','unreal']);p.add_argument('--exe',required=True);p.add_argument('--scene');p.add_argument('--uproject');p.add_argument('--asset');p.add_argument('--out',required=True);p.add_argument('--execute',action='store_true');p.add_argument('--timeout',type=int,default=900);a=p.parse_args()
    try:cmd,env,out=configure(a)
    except Exception as e:raise SystemExit('BLOCKED_TOOL: '+str(e))
    if not a.execute:
        print(json.dumps({'status':'DRY_RUN_NOT_EXECUTED','command':cmd,'out':str(out)},ensure_ascii=False,indent=2));return
    if out.exists():raise SystemExit('BLOCKED_EXISTING_REPORT: use new report path, no overwrites')
    out.parent.mkdir(parents=True,exist_ok=True)
    log=out.with_suffix(out.suffix+'.log')
    if log.exists():raise SystemExit('BLOCKED_EXISTING_LOG: use a unique output path')
    try:
        with log.open('w',encoding='utf-8') as f: cp=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=a.timeout,check=False)
        success=(cp.returncode==0 and out.is_file() and out.stat().st_size>40)
        if success:
            data=json.loads(out.read_text('utf-8'));success=data.get('status') in ('ASSET_READBACK_ONLY_NOT_PLAYTESTED','SCENE_STRUCTURE_INSPECTED_VISUAL_QA_NOT_DONE')
    except (subprocess.TimeoutExpired,OSError,ValueError,KeyError) as e:
        success=False;print(str(e),file=sys.stderr)
    print(json.dumps({'status':'AUDIT_RECORDED_NOT_ART_QA' if success else 'FAILED','report':str(out),'log':str(log)},ensure_ascii=False))
    if not success:sys.exit(1)
if __name__=='__main__':main()
