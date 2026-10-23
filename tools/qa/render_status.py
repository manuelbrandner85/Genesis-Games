"""Offline static HTML summary of existing JSON reports. No fake live counters."""
from pathlib import Path
import json,datetime,html,argparse

def main():
 a=argparse.ArgumentParser();a.add_argument('--input',type=Path,default=Path('docs/production-status'));a.add_argument('--output',type=Path,default=Path('status_local.html'));ns=a.parse_args()
 jobs=[];warnings=[]
 for path in sorted(ns.input.glob('*.json')):
  try:
   d=json.loads(path.read_text('utf-8'))
   if isinstance(d,list):jobs+=d
   elif isinstance(d,dict):jobs.append(d)
  except Exception as e:warnings.append(f'{path.name}: {e}')
 rows=[]
 for j in jobs:
  status=html.escape(str(j.get('status','UNKNOWN')))
  rows.append('<tr><td>'+html.escape(str(j.get('task_id',j.get('work_id','—'))))+'</td><td>'+status+'</td><td>'+html.escape(str(j.get('owner_role',j.get('owner','—'))))+'</td><td>'+html.escape(', '.join(str(x) for x in j.get('evidence_paths',[])))+'</td></tr>')
 stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
 content=f'''<!doctype html><html lang="de"><meta charset="utf-8"><title>GENESIS Produktionsstatus</title><style>body{{font:16px system-ui;margin:3rem auto;max-width:1000px;background:#101924;color:#eef}}table{{width:100%;border-collapse:collapse}}td,th{{text-align:left;border-bottom:1px solid #48556a;padding:.8rem}}small{{color:#b6c4db}}</style><h1>GENESIS · Produktionsstand</h1><p><small>Statischer Snapshot {html.escape(stamp)} – keine Liveverbindung und kein gemessener Game-Fortschritt</small></p><p>{len(jobs)} belegte Job-Datensätze gefunden.</p><table><tr><th>WorkID</th><th>Status aus Quelle</th><th>Agent</th><th>Belege</th></tr>{''.join(rows)}</table><p>{'Keine Produktionsdaten vorhanden.' if not jobs else ''}</p><p>{html.escape('; '.join(warnings))}</p></html>'''
 ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(content,encoding='utf-8');print(json.dumps({'output':str(ns.output),'records':len(jobs),'warnings':warnings},ensure_ascii=False))
if __name__=='__main__':main()
