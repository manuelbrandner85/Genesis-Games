"""Check whether TWO supplied original-media files are byte-identical. No files modified."""
from pathlib import Path
import argparse,hashlib,json,sys

def sha256(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for part in iter(lambda:f.read(1048576),b''):h.update(part)
    return h.hexdigest()
def check(a,b):
    if not Path(a).is_file() or not Path(b).is_file():return {'status':'BLOCKED_SOURCE_MISSING','identical':False}
    x,y=sha256(a),sha256(b)
    return {'status':'PASS_IDENTICAL_BYTES' if x==y else 'FAIL_NONIDENTICAL','identical':x==y,'master_sha256':x,'replay_sha256':y,'note':'Same bytes verifies reuse, not creative approval, playback timecode or completeness.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--c00-master',required=True);p.add_argument('--c20-replay',required=True);a=p.parse_args();r=check(a.c00_master,a.c20_replay);print(json.dumps(r,indent=2));sys.exit(not r['identical'])
