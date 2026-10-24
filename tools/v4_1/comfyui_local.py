"""Submit an exported ComfyUI API-format workflow to localhost only. Dry-run by default."""
import argparse,json,ipaddress,urllib.parse,urllib.request
from pathlib import Path

def check_url(url):
    x=urllib.parse.urlparse(url)
    if x.scheme!='http' or x.hostname not in ('localhost','127.0.0.1','::1') or x.username or x.password or x.path not in ('','/'):
        raise ValueError('Only local http://127.0.0.1:PORT allowed')
    if not x.port or x.port not in range(1,65536):raise ValueError('Explicit port required')
    return x

def load_workflow(path):
    d=json.loads(path.read_text(encoding='utf8'))
    if 'prompt' in d and isinstance(d['prompt'],dict):d=d['prompt']
    if not isinstance(d,dict) or not d:raise ValueError('Workflow must be a nonempty ComfyUI API JSON object')
    for key,node in d.items():
        if not isinstance(node,dict) or 'class_type' not in node or 'inputs' not in node:raise ValueError(f'Invalid ComfyUI API node {key}')
    return d

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--workflow',type=Path,required=True);ap.add_argument('--endpoint',default='http://127.0.0.1:8188');ap.add_argument('--dry-run',action='store_true');ap.add_argument('--submit',action='store_true');ap.add_argument('--output',type=Path);args=ap.parse_args()
    check_url(args.endpoint)
    prompt=load_workflow(args.workflow)
    if not args.submit:
        print(json.dumps({'state':'READY_FOR_LOCAL_SUBMIT_NOT_GENERATED','nodes':len(prompt),'endpoint':args.endpoint,'network_calls':0,'needs_license_and_local_model_approval':True},indent=2));return
    # Requires an already-approved and running local ComfyUI; does NOT download models or assets.
    payload=json.dumps({'prompt':prompt,'client_id':'genesis-free-ai-4.1'}).encode('utf8')
    req=urllib.request.Request(args.endpoint.rstrip('/')+'/prompt',data=payload,headers={'Content-Type':'application/json'},method='POST')
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise ValueError('ComfyUI redirect blocked: remote URL not allowed')
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect)
    with opener.open(req,timeout=15) as resp:
        result=json.loads(resp.read().decode('utf8'))
    out={'status':'QUEUED_NOT_GENERATED','server_response':result,'endpoint':args.endpoint}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
