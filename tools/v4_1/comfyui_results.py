"""Download completed ComfyUI images from local endpoint. Verifies actual response; does NOT approve images.
Example: python tools/v4_1/comfyui_results.py --prompt-id UUID --output-dir assets/free_ai_previews
"""
import argparse,json,re,urllib.parse,urllib.request
from pathlib import Path
from comfyui_local import check_url

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Remote or redirected ComfyUI response blocked')

def opener():return urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect)

def fetch(endpoint,prompt_id,output_dir):
    check_url(endpoint)
    if not re.fullmatch(r'[a-zA-Z0-9-]{8,80}',prompt_id):raise ValueError('Invalid prompt ID')
    transport=opener()
    req=endpoint.rstrip('/')+'/history/'+urllib.parse.quote(prompt_id,safe='')
    with transport.open(req,timeout=15) as response:
        history=json.loads(response.read().decode('utf8'))
    if prompt_id not in history:raise RuntimeError('NOT_COMPLETE_OR_NOT_FOUND')
    images=[]
    for node in history[prompt_id].get('outputs',{}).values():
        images.extend(node.get('images',[]))
    if not images:raise RuntimeError('NO_IMAGES_IN_COMPLETED_OUTPUT')
    output_dir=Path(output_dir).resolve()
    output_dir.mkdir(parents=True,exist_ok=True)
    result=[]
    for i,item in enumerate(images):
        original=str(item.get('filename',''))
        if not original:continue
        args=urllib.parse.urlencode({'filename':original,'subfolder':str(item.get('subfolder','')),'type':str(item.get('type','output'))})
        safe=re.sub(r'[^a-zA-Z0-9_.-]','_',Path(original).name)
        if safe in ('','..','.'):raise ValueError('Invalid output filename')
        target=output_dir/(f'{prompt_id}_{i:03d}_{safe}')
        if target.exists():raise FileExistsError('Would overwrite generated result: '+str(target))
        with transport.open(endpoint.rstrip('/')+'/view?'+args,timeout=60) as r:
            body=r.read(100*1024*1024+1)
        if not body or len(body)>100*1024*1024:raise ValueError('Empty or unexpectedly large output')
        # Basic PNG/JPEG/WebP file signature, not AI quality proof.
        if not (body.startswith(b'\x89PNG\r\n\x1a\n') or body[:3]==b'\xff\xd8\xff' or (body.startswith(b'RIFF') and body[8:12]==b'WEBP')):
            raise ValueError('Downloaded data is not a recognized PNG/JPEG/WebP')
        target.write_bytes(body)
        result.append(str(target))
    return {'status':'DOWNLOADED_UNREVIEWED','images':result,'still_requires':['License','Reference consistency','Human artistic review','Blender / Unreal QA']}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--endpoint',default='http://127.0.0.1:8188');ap.add_argument('--prompt-id',required=True);ap.add_argument('--output-dir',type=Path,required=True);a=ap.parse_args()
    print(json.dumps(fetch(a.endpoint,a.prompt_id,a.output_dir),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
