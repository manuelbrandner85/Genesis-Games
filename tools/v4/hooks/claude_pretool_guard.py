"""Claude Code PreToolUse guard: defense in depth, NOT security sandbox.
Reads JSON from stdin; exit code 2 blocks. Never prints input payload or secrets.
"""
from __future__ import annotations
import sys,json,re
PROTECTED=('canon_sources/','canon_sources\\','original_md_unveraendert/','original_md_unveraendert\\')
# 2026-10-25 (Fund H-02, freigegeben): normaler 'git push' ist erlaubt (Nutzerregel: fertige Commits pushen);
# gesperrt bleiben Force-Push, Mirror-/Loesch-Push, reset --hard, clean -f, rm -rf, Repo-Loeschen.
PATTERNS=[r'git\s+push\b[^\n]*\s(?:-f|--force(?:-with-lease)?|--force-if-includes|--mirror|--delete|-d|--prune)\b',
 r'git\s+push\b[^\n]*\s\+\S',r'git\s+push\b[^\n]*\s:\S',r'git\s+reset\s+--hard',r'git\s+clean\s+-[^\s]*f',
 r'\brm\s+-[a-zA-Z]*r[a-zA-Z]*f\b',r'\brm\s+-[a-zA-Z]*f[a-zA-Z]*r\b',
 r'\bremove-item\b[^\n]*-recurse',r'\brmdir\s+/s',r'\bformat\s+[a-z]:',
 r'\bgh\s+repo\s+delete\b']

def check(payload):
 name=str(payload.get('tool_name') or '')
 inp=payload.get('tool_input') or {}
 if not isinstance(inp,dict):inp={}
 if name.lower() in ('write','edit','multiedit','notebookedit'):
  path=str(inp.get('file_path') or inp.get('path') or '').replace('\\','/')
  if any(s.replace('\\','/') in path.lower() for s in PROTECTED):
   return 'Protected GENESIS original source: writes must be reviewed and performed outside canon vault.'
 cmd=str(inp.get('command') or inp.get('cmd') or '')
 if name.lower() in ('bash','powershell'):
  if any(re.search(x,cmd,re.I) for x in PATTERNS):return 'Destructive or remote-push command requires explicit Director approval outside this session.'
  if any(s.lower() in cmd.lower() for s in PROTECTED) and re.search(r'\b(mv|move-item|cp|copy-item|sed\s+-i|rm|remove-item|del|unlink|write_text)\b',cmd,re.I):
   return 'Command might alter protected original source paths.'
 return None

def main():
 try: data=json.load(sys.stdin)
 except Exception:sys.stderr.write('Invalid guard input: fail closed\n');return 2
 blocked=check(data)
 if blocked:sys.stderr.write('GENESIS_V4_BLOCKED: '+blocked+'\n');return 2
 return 0
if __name__=='__main__':raise SystemExit(main())
