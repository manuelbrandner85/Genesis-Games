"""Static V4.1 package acceptance checks (not Unreal/Blender runtime)."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2]

def verify():
    errors=[]
    essential=['CLAUDE.md','GENESIS_CLAUDE_CODE_MASTERPROMPT_V4.md','GENESIS_CLAUDE_CODE_MASTERPROMPT_V4_1.md','START_HIER_V4_1.md','config/free_ai_tools.json', 'docs/v4_1/FREE_AI_SYSTEM.md','docs/v4_1/FREE_AI_TOOL_MATRIX.md','docs/v4_1/FREE_AI_INSTALLATION_POLICY.md','docs/v4_1/FREE_AI_APPROVAL_GATE.md','docs/v4_1/FREE_AI_OUTPUT_REGISTER.md','docs/v4_1/FREE_AI_PRODUCTION_PIPELINES.md','tools/v4/init_new_game.py','tools/v4_1/hardware_probe.py','tools/v4_1/ai_tool_manager.py','tools/v4_1/approval_gate.py','tools/v4_1/comfyui_local.py','tools/v4_1/asset_register.py','tools/v4_1/audio_quality.py','tools/v4_1/blender_turnaround.py','tools/v4_1/comfyui_results.py','tools/v4_1/piper_preview.py','tools/v4_1/hooks/free_ai_pretool_guard.py']
    for x in essential:
        if not (ROOT/x).is_file():errors.append('MISSING '+x)
    ag=list((ROOT/'.claude/agents').glob('genesis-*.md'))
    if len(ag)!=24:errors.append(f'24 role files expected: {len(ag)}')
    skills=list((ROOT/'.claude/skills').glob('genesis-free-ai-*/SKILL.md'))
    if len(skills)!=8:errors.append(f'8 free-ai skills expected: {len(skills)}')
    if 'GENESIS_CLAUDE_CODE_MASTERPROMPT_V4_1.md' not in (ROOT/'tools/v4/init_new_game.py').read_text(encoding='utf8'):errors.append('V4 bootstrap omits V4.1')
    if any('FREE AI INTEGRATION' not in (ROOT/'CLAUDE.md').read_text(encoding='utf8') for _ in [0]):errors.append('CLAUDE missing v4.1 priority')
    try:tools=json.loads((ROOT/'config/free_ai_tools.json').read_text(encoding='utf8'))['tools']
    except Exception as e:errors.append('catalog invalid '+str(e));tools=[]
    if len(tools)<8:errors.append('catalog incomplete')
    return {'status':'STATIC_PASS_NOT_ENGINE_QA' if not errors else 'STATIC_FAILED','errors':errors,'v41_skills':len(skills),'agent_roles':len(ag),'catalog_tools':len(tools)}
if __name__=='__main__':
 v=verify();print(json.dumps(v,indent=2));sys.exit(bool(v['errors']))
