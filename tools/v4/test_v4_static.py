"""Unit tests for V4 installer/canon safety. These do not run Unreal or Blender."""
import sys, unittest, tempfile, hashlib, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from init_new_game import plan, validate_target
from source_audit import audit
from verify_v4_package import verify
from hooks.claude_pretool_guard import check

class V4UnitTests(unittest.TestCase):
    def test_v4_package(self):
        errors,_=verify()
        self.assertEqual(errors,[])
    def test_new_project_requires_explicit_apply(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'new_genesis'
            report=plan(target,'5.8',apply=False)
            self.assertFalse(target.exists())
            self.assertEqual(report['mode'],'DRY_RUN')
    def test_new_project_scaffold_generated(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'new_genesis'
            report=plan(target,'5.8',apply=True)
            self.assertTrue((target/'Genesis.uproject').exists())
            self.assertEqual(json.loads((target/'Genesis.uproject').read_text())['EngineAssociation'],'5.8')
            self.assertTrue((target/'.claude/agents/genesis-master-director.md').exists())
            self.assertTrue((target/'Source/Genesis/Genesis.Build.cs').exists())
            self.assertEqual(report['status'],'PROJECT_SCAFFOLD_ONLY_NOT_BUILT')
            with self.assertRaises(ValueError):plan(target,'5.8',apply=True)
    def test_old_repo_inside_collision(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'old';p.mkdir()
            (p/'.git').mkdir();(p/'Genesis.uproject').write_text('{}')
            with self.assertRaises(ValueError):validate_target(p/'fresh')
    def test_source_hash_readonly(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);orig=p/'original.md';orig.write_bytes(b'ABC')
            report=audit(p)
            self.assertEqual(report['files'][0]['sha256'],hashlib.sha256(b'ABC').hexdigest())
            self.assertEqual(orig.read_bytes(),b'ABC')
            self.assertEqual(report['approval_state'],'DIRECTOR_AND_SOURCE_VERIFICATION_REQUIRED')
    def test_hook_blocks_source_edit(self):
        self.assertIsNotNone(check({'tool_name':'Write','tool_input':{'file_path':'canon_sources/bibel.md','content':'wrong'}}))
    def test_hook_blocks_push(self):
        self.assertIsNotNone(check({'tool_name':'Bash','tool_input':{'command':'git push origin main'}}))
    def test_hook_allows_read_only(self):
        self.assertIsNone(check({'tool_name':'Bash','tool_input':{'command':'git status --short'}}))

if __name__=='__main__':unittest.main()
