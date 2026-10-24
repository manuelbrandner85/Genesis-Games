"""Optional local Piper binary adapter for licensed preview voices; no voice downloads or final dubbing claims."""
import argparse,subprocess,json,hashlib
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--binary',type=Path,required=True);ap.add_argument('--model',type=Path,required=True);ap.add_argument('--text-file',type=Path,required=True);ap.add_argument('--model-card',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--execute',action='store_true');args=ap.parse_args()
    for name,path in [('binary',args.binary),('model',args.model),('text_file',args.text_file),('model_card',args.model_card)]:
        if not path.is_file():raise SystemExit(f'NOT_READY: {name} unavailable: {path}')
    if args.output.exists():raise SystemExit('STOP: will not overwrite existing voice file')
    if not args.model_card.read_text(encoding='utf8',errors='replace').strip():raise SystemExit('LICENSE_REVIEW: empty model card')
    cmd=[str(args.binary.resolve()),'--model',str(args.model.resolve()),'--output_file',str(args.output.resolve())]
    if not args.execute:
        print(json.dumps({'status':'DRY_RUN_NO_AUDIO_GENERATED','command':cmd,'model_card_path':str(args.model_card),'license_review_still_required':True},ensure_ascii=False,indent=2));return
    args.output.parent.mkdir(parents=True,exist_ok=True)
    text=args.text_file.read_text(encoding='utf8')
    if len(text)>10000:raise SystemExit('LIMIT: dialog too long for one preview')
    p=subprocess.run(cmd,input=text+'\n',text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=240,check=False)
    if p.returncode!=0 or not args.output.exists() or args.output.stat().st_size<44:
        raise SystemExit('PIPER_FAILED: '+p.stderr[-2000:])
    print(json.dumps({'status':'PREVIEW_NOT_FINAL','wav_path':str(args.output),'wav_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),'license_final_review_required':True},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
