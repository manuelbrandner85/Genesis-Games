"""GENESIS V4.1 defense-in-depth: block obvious install/download shell commands lacking manual plan receipt.
Not a secure sandbox. Excludes unknown commands and subprocess-level hidden installs.
"""
from __future__ import annotations
import json,re,sys
from pathlib import Path
THIS=Path(__file__).resolve().parents[3]
RISKY=[r'\bpip(?:3)?\s+install\b',r'\buv\s+(?:sync|pip\s+install)\b',r'\b(?:hf|huggingface-cli)\s+download\b',r'\bacestep-download\b',r'\bgit\s+clone\b',r'\bwinget\s+install\b',r'\bchoco\s+install\b',r'\b(?:Invoke-WebRequest|Start-BitsTransfer)\b',r'\bcurl\b[^\n]*(?:-o|-O|--output)\b',r'\b(?:wget|irm|iwr)\b',r'\b(?:pip\s+install|model_downloader|snapshot_download)\b']

def is_risky(cmd):return any(re.search(p,cmd,re.I) for p in RISKY)

def check(payload,approval_dir=None):
    name=str(payload.get('tool_name','')).lower()
    if name not in ('bash','powershell'):return None
    inp=payload.get('tool_input') or {}
    if not isinstance(inp,dict):return None
    cmd=str(inp.get('command') or inp.get('cmd') or '')
    if not is_risky(cmd):return None
    from pathlib import Path
    try:
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
        from approval_gate import valid_receipt
    except Exception:return 'Approval gate unavailable'
    approvals=Path(approval_dir) if approval_dir else THIS/'.genesis_approvals'
    if approvals.exists():
        for planpath in approvals.glob('*.json'):
            if planpath.name.endswith('.approval.json') or planpath.is_symlink():continue
            receiptpath=planpath.with_suffix('.approval.json')
            if not receiptpath.is_file() or receiptpath.is_symlink():continue
            try:
                plan=json.loads(planpath.read_text(encoding='utf8'))
                receipt=json.loads(receiptpath.read_text(encoding='utf8'))
                if cmd in plan['commands'] and valid_receipt(plan,receipt):return None
            except (ValueError,KeyError,TypeError,OSError):pass
    return 'Installation, Download oder Netzwerkkommando ohne passende interaktive Planfreigabe blockiert. Siehe docs/v4_1/FREE_AI_APPROVAL_GATE.md; manueller Plan+Receipt nötig.'

def main():
    try: payload=json.load(sys.stdin)
    except Exception:sys.stderr.write('GENESIS V4.1 guard: invalid input, deny\n');return 2
    err=check(payload)
    if err:sys.stderr.write('GENESIS V4.1 BLOCKED: '+err+'\n');return 2
    return 0
if __name__=='__main__':raise SystemExit(main())
