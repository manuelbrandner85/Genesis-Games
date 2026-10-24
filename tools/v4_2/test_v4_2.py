"""Offline/contract tests only. These do not execute Unreal Editor, Blender or a Windows build."""
from pathlib import Path
import unittest, tempfile, sys, json, hashlib
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/v4_2'))
from validate_cinematic_bundle import audit
from check_replay_identity import check

class TestCinematicBundle(unittest.TestCase):
    def test_full_scene_matrix(self):
        r=audit(ROOT);self.assertEqual(r['status'],'STATIC_PASS_ONLY_NOT_ENGINE_TESTED',r)
        self.assertEqual(r['scene_count'],22)
    def test_original_script_source_pending_not_faked(self):
        d=json.loads((ROOT/'docs/v4_2/SCENE_MATRIX_C00_C21.json').read_text(encoding='utf8'))
        self.assertTrue(all(s['approval_status']=='SOURCE_PENDING' for s in d['scenes']))
    def test_c00_c20_shared_master(self):
        d=json.loads((ROOT/'docs/v4_2/SCENE_MATRIX_C00_C21.json').read_text(encoding='utf8'))
        self.assertEqual(d['replay_master_rule']['shared_master_asset_id'],'C00_ORIGINAL_MASTER')
        self.assertTrue(d['replay_master_rule']['prohibit_rerender_as_replay'])
    def test_no_fake_cinematics(self):
        d=json.loads((ROOT/'docs/v4_2/SCENE_MATRIX_C00_C21.json').read_text(encoding='utf8'))
        self.assertTrue(all(s['implementation_status']=='NOT_IMPLEMENTED' for s in d['scenes']))
    def test_menu_node_reachability(self):
        d=json.loads((ROOT/'docs/v4_2/MENU_FLOW.json').read_text(encoding='utf8'))
        self.assertIn('BOOT', [n['id'] for n in d['nodes']]);self.assertIn('IN_GAME', [n['id'] for n in d['nodes']])
    def test_master_identity_pass(self):
        with tempfile.TemporaryDirectory() as td:
            a,b=Path(td)/'a.mov',Path(td)/'b.mov';a.write_bytes(b'same');b.write_bytes(b'same');self.assertTrue(check(a,b)['identical'])
    def test_master_identity_fail(self):
        with tempfile.TemporaryDirectory() as td:
            a,b=Path(td)/'a.mov',Path(td)/'b.mov';a.write_bytes(b'original');b.write_bytes(b'new');self.assertFalse(check(a,b)['identical'])
    def test_missing_media_is_blocked(self):
        self.assertEqual(check('/not-here/a.mov','/not-here/b.mov')['status'],'BLOCKED_SOURCE_MISSING')
    def test_bootstrap_copies_latest_files(self):
        s=(ROOT/'tools/v4/init_new_game.py').read_text(encoding='utf8');self.assertIn('GENESIS_CLAUDE_CODE_MASTERPROMPT_V4_2.md',s);self.assertIn('START_HIER_V4_2.md',s)
    def test_latest_claude_instruction(self):
        s=(ROOT/'CLAUDE.md').read_text(encoding='utf8');self.assertIn('GODMODE 4.2',s);self.assertIn('C00',s)
    def test_skills(self):
        self.assertEqual(len(list((ROOT/'.claude/skills').glob('genesis-v4-2-*/SKILL.md'))),5)
    def test_source_md_unchanged_presence(self):
        self.assertTrue((ROOT/'original_md_unveraendert/GAMEFORGE_Verbesserung_03_Ultimate_Living_World_Simulation_GODMODE.md').is_file())

if __name__=='__main__':unittest.main()
