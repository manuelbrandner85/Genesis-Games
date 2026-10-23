"""Engine-free unit tests. Does NOT validate UE/Blender game runtime."""
import unittest,tempfile,json,sys,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from verify_v3_package import verify
from validate_evidence import evaluate
from canon_guard import manifest
from install_v3 import plan

class V3Checks(unittest.TestCase):
    def test_package(self):
        errors,_=verify();self.assertEqual(errors,[])
    def test_gate_refuses_no_evidence(self):
        e=evaluate({'status':'ACCEPTED','work_id':'X','evidence_paths':[]},Path.cwd());self.assertTrue(any('evidence absent' in s for s in e))
    def test_gate_refuses_no_reviewer(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'proof.txt';p.write_text('fake evidence placeholder');e=evaluate({'status':'ACCEPTED','work_id':'X','evidence_paths':['proof.txt']},Path(d));self.assertTrue(any('reviewer absent' in s for s in e))
    def test_canon_baseline(self):
        with tempfile.TemporaryDirectory() as d:
            repo=Path(d);(repo/'story.md').write_text('source');info=manifest(repo,['story.md']);self.assertEqual(info['story.md'],hashlib.sha256(b'source').hexdigest())
    def test_installer_never_overwrites(self):
        with tempfile.TemporaryDirectory() as d:
            repo=Path(d);(repo/'.git').mkdir();(repo/'Genesis.uproject').write_text('{}');(repo/'CLAUDE.md').write_text('DO NOT CHANGE')
            out=plan(repo,True);self.assertIn('CLAUDE.md',out['conflicts_skip']);self.assertEqual((repo/'CLAUDE.md').read_text(),'DO NOT CHANGE')
            self.assertTrue((repo/'docs/godmode_v3/GOLD_SLICE_GATES.json').exists())
if __name__=='__main__':unittest.main()
