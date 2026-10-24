"""Analyze PCM WAV container, RMS, peak, clipping. Not a legal/audio-artistic review."""
import argparse, json, wave, array, math, sys
from pathlib import Path

def scan(path):
    with wave.open(str(path),'rb') as w:
        sample_width=w.getsampwidth();channels=w.getnchannels();rate=w.getframerate();n=w.getnframes();d=w.readframes(min(n,rate*90))
    out={'path':str(path.resolve()),'channels':channels,'sample_rate_hz':rate,'sample_width_bytes':sample_width,'duration_seconds':n/rate if rate else 0,'status':'FORMAT_CHECK_ONLY_NOT_ARTISTIC_QA'}
    if sample_width not in (1,2,4):out['warnings']=['Unsupported for amplitude check'];return out
    ar=array.array({1:'B',2:'h',4:'i'}[sample_width]);ar.frombytes(d)
    if sys.byteorder!='little' and sample_width>1:ar.byteswap()
    norm=(2**(sample_width*8-1));nums=[(v-128)/128 if sample_width==1 else v/norm for v in ar]
    if nums:
        out['peak']=max(abs(v) for v in nums);out['rms']=math.sqrt(sum(v*v for v in nums)/len(nums));out['clipped_samples']=sum(abs(v)>=.9999 for v in nums)
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);args=ap.parse_args();print(json.dumps(scan(args.input),indent=2))
if __name__=='__main__':main()
