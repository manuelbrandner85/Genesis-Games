"""Pure Python unit tests; no Unreal/Blender present in CI."""
import unittest,tempfile,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/pipeline'))
from asset_manifest import validate_manifest
class TestManifest(unittest.TestCase):
 def setUp(self):self.m={'asset_id':'TEST_ASSET_001','phase':'SMOKE_ONLY','type':'static_mesh','dimensions_m':{'x':1,'y':1,'z':1},'license_status':'SELF_CREATED','ue_path':'/Game/Genesis/SMOKE'}
 def test_good(self):self.assertEqual(validate_manifest(self.m),[])
 def test_reject_zero_width(self):self.m['dimensions_m']['x']=0;self.assertTrue(validate_manifest(self.m))
 def test_reject_foreign_ue(self):self.m['ue_path']='/Game/AION/Asset';self.assertTrue(validate_manifest(self.m))
 def test_real_asset_requires_story_ref(self):self.m['phase']='PRODUCTION';self.assertTrue(validate_manifest(self.m))
if __name__=='__main__':unittest.main()
