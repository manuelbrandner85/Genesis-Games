"""Read-only GENESIS Free AI hardware / executable inventory; no external network, no installs."""
import argparse, ctypes, json, os, platform, shutil, subprocess, sys, time
from pathlib import Path

def cmd(argv, timeout=8):
    try:
        p=subprocess.run(argv, capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout,check=False)
        return {'ok':p.returncode==0,'code':p.returncode,'output':(p.stdout or p.stderr).strip()[:4000]}
    except (OSError,subprocess.TimeoutExpired) as ex:return {'ok':False,'error':str(ex)}

def windows_gpu():
    ps=shutil.which('powershell') or shutil.which('pwsh')
    if not ps:return []
    r=cmd([ps,'-NoProfile','-Command','Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM,DriverVersion | ConvertTo-Json -Compress'])
    if not r.get('ok'):return []
    try:
        g=json.loads(r['output']); return g if isinstance(g,list) else [g]
    except (ValueError,KeyError):return []

def ram_bytes():
    try:
        if sys.platform=='win32':
            class M(ctypes.Structure):
                _fields_=[('dwLength',ctypes.c_ulong),('dwMemoryLoad',ctypes.c_ulong),('ullTotalPhys',ctypes.c_ulonglong),('ullAvailPhys',ctypes.c_ulonglong),('ullTotalPageFile',ctypes.c_ulonglong),('ullAvailPageFile',ctypes.c_ulonglong),('ullTotalVirtual',ctypes.c_ulonglong),('ullAvailVirtual',ctypes.c_ulonglong),('ullAvailExtendedVirtual',ctypes.c_ulonglong)]
            m=M();m.dwLength=ctypes.sizeof(M);ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m));return m.ullTotalPhys
        return os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES')
    except Exception:return None

def probe():
    out={'probe_status':'READ_ONLY','time_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'platform':sys.platform,'os':platform.platform(),'python':sys.version.split()[0], 'cpu':platform.processor(),'ram_bytes':ram_bytes(),'cwd':str(Path.cwd()),'nvidia_gpus':[],'windows_video_controllers':[],'executables':{},'disk_free_bytes':None,'local_installation_verified':False}
    try:out['disk_free_bytes']=shutil.disk_usage(Path.cwd()).free
    except OSError:pass
    for executable in ('git','blender','UnrealEditor','UnrealEditor-Cmd','nvidia-smi','ffmpeg','piper','uv','python'):
        out['executables'][executable]=shutil.which(executable)
    if shutil.which('nvidia-smi'):
        p=cmd(['nvidia-smi','--query-gpu=name,memory.total,driver_version','--format=csv,noheader,nounits'])
        out['nvidia_smi_query']=p
        if p.get('ok'):
            for line in p['output'].splitlines():
                cols=[x.strip() for x in line.split(',')]
                if len(cols)>=3:
                    try: memory=int(cols[1])
                    except ValueError:memory=None
                    out['nvidia_gpus'].append({'name':cols[0],'vram_mb':memory,'driver':cols[2]})
    if sys.platform=='win32':out['windows_video_controllers']=windows_gpu()
    out['notes']=['Executable presence does NOT prove runtime functionality','UE5 may not be on PATH; inspect installed project settings separately','GPU model memory data must be measured; Windows AdapterRAM often overflows on newer GPUs']
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path)
    a=ap.parse_args(); data=probe()
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(data,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
