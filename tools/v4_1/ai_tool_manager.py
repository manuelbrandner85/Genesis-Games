"""Read-only selection of free AI candidates. Does not install or verify licenses."""
import argparse,json,platform,sys
from pathlib import Path
REG=Path(__file__).resolve().parents[2]/'config/free_ai_tools.json'

def select(hardware, registry=None):
    registry=registry or json.loads(REG.read_text(encoding='utf8'))
    osname=('Windows' if hardware.get('platform')=='win32' else 'Linux' if str(hardware.get('platform','')).startswith('linux') else 'macOS' if str(hardware.get('platform',''))=='darwin' else 'Unknown')
    gpu_mbs=[g.get('vram_mb') for g in hardware.get('nvidia_gpus',[]) if isinstance(g.get('vram_mb'),int)]
    best=max(gpu_mbs, default=None)
    outcome=[]
    for tool in registry['tools']:
        reasons=[];status='CANDIDATE_APPROVAL_REQUIRED'
        if tool.get('blocked_by_policy'):
            status='BLOCKED_LICENSE';reasons.append('model non-commercial by default')
        elif osname not in tool.get('os',[]):
            status='PLATFORM_UNVERIFIED';reasons.append('officially supported OS not matched')
        else:
            minimum=tool.get('min_nvidia_vram_gb')
            if minimum is not None and (best is None or best<minimum*1024):
                status='BLOCKED_RESOURCE';reasons.append(f'requires NVIDIA >= {minimum} GiB documented; inventory reported {best or "unknown"} MiB')
        if status=='CANDIDATE_APPROVAL_REQUIRED':reasons.append('installation and model license have not been verified')
        outcome.append({'tool_id':tool['id'],'status':status,'os':osname,'measured_nvidia_vram_mb':best,'reasons':reasons,'url':tool['url']})
    return {'status':'RECOMMENDATIONS_ONLY','tools_installed_by_this_script':0,'hardware_probe_status':hardware.get('probe_status','MISSING'), 'tools':outcome}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--hardware',type=Path);ap.add_argument('--output',type=Path);args=ap.parse_args()
    hw=json.loads(args.hardware.read_text(encoding='utf8')) if args.hardware else {'platform':sys.platform,'nvidia_gpus':[]}
    result=select(hw)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
