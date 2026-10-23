"""Read-only, local preflight; never installs tools or asserts an Unreal run."""
from __future__ import annotations
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess, sys, time

def probe(exe,cmd,timeout=8):
    if not exe:return {'available':False,'reason':'NOT_FOUND'}
    try:
        cp=subprocess.run([exe,*cmd],capture_output=True,text=True,timeout=timeout,check=False)
        return {'available':cp.returncode==0,'exit_code':cp.returncode,'output':(cp.stdout+'\n'+cp.stderr)[-500:]}
    except Exception as e:return {'available':False,'reason':str(e)}

def run(root:Path)->dict:
    root=root.resolve()
    proj=root/'Genesis.uproject'
    data={'status':'READ_ONLY_PREFLIGHT','repo_root':str(root),'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'found_uproject':proj.is_file()}
    if proj.is_file():
        try:
            config=json.loads(proj.read_text('utf-8-sig'))
            data['engine_association']=config.get('EngineAssociation')
            data['project_plugins']={x.get('Name'):x.get('Enabled') for x in config.get('Plugins',[])}
        except Exception as e:data['uproject_parse_error']=str(e)
    git=shutil.which('git')
    data['git']={'installed':bool(git)}
    if git:
        for key,cmd in [('branch',['rev-parse','--abbrev-ref','HEAD']),('commit',['rev-parse','HEAD']),('dirty',['status','--porcelain'])]:
            try:
                p=subprocess.run([git,'-C',str(root),*cmd],capture_output=True,text=True,timeout=8,check=False)
                data['git'][key]=p.stdout.strip() if p.returncode==0 else 'UNKNOWN'
            except Exception:data['git'][key]='UNKNOWN'
    b=shutil.which('blender') or os.getenv('BLENDER_EXE')
    data['blender']=probe(b,['--version'])
    ue=os.getenv('UNREAL_EDITOR_EXE')
    data['unreal_editor']={'path':ue,'exists':bool(ue and Path(ue).is_file()),'tested':False,'reason':'Editor not launched by read-only preflight'}
    data['project_mcp_config_present']=(root/'.mcp.json').exists()
    data['mcp_actual_connection_tested']=False
    data['studio_brain_present']='UNKNOWN_UNTIL_AUDIT'
    data['story_scriptlock_present']=bool(list(root.rglob('*ScriptLock*'))) if root.is_dir() else False
    return data
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--repo',default='.',type=Path);a.add_argument('--output',type=Path)
    ns=a.parse_args(); report=run(ns.repo)
    if ns.output:
        ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
