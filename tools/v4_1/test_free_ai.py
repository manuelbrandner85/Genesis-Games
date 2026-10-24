import unittest, json, tempfile, wave, math, struct, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ai_tool_manager import select
from approval_gate import valid_receipt,digest,check_plan
from comfyui_local import check_url,load_workflow
from asset_register import build_record
from audio_quality import scan
from validate_package import verify
from comfyui_results import fetch as comfy_fetch
from hooks.free_ai_pretool_guard import check as install_check

class FreeAITests(unittest.TestCase):
 def test_package(self):self.assertEqual('STATIC_PASS_NOT_ENGINE_QA',verify()['status'])
 def test_no_trellis_on_low_vram_windows(self):
  d=select({'platform':'win32','nvidia_gpus':[{'vram_mb':8192}]})
  x={x['tool_id']:x for x in d['tools']}
  self.assertEqual(x['trellis']['status'],'PLATFORM_UNVERIFIED')
  self.assertEqual(x['flux1-dev']['status'],'BLOCKED_LICENSE')
 def test_trellis_low_vram_linux(self):
  d=select({'platform':'linux','nvidia_gpus':[{'vram_mb':8192}]})
  self.assertEqual([x for x in d['tools'] if x['tool_id']=='trellis'][0]['status'],'BLOCKED_RESOURCE')
 def test_approval_invalidates_changed_plan(self):
  p={'plan_id':'FAI-001','tool_id':'comfyui','source_url':'https://example.org','source_revision':'hash','license_evidence':'verified','download_size_gb':2,'install_directory':'C:/tools','commands':['do'], 'rollback':'remove'}
  check_plan(p)
  r={'approved':True,'scope':'ONE_TOOL_REVISION','confirmation':'FREIGABE FAI-001','plan_sha256':digest(p)}
  self.assertTrue(valid_receipt(p,r));p['source_revision']='other';self.assertFalse(valid_receipt(p,r))
 def test_results_reject_bad_prompt_id(self):
  with self.assertRaises(ValueError):comfy_fetch('http://127.0.0.1:8188','../x',Path('/tmp/test-genesis-nonexistent'))
 def test_paid_api_blocked(self):
  p={'plan_id':'FAI-01','tool_id':'x','source_url':'a','source_revision':'v','license_evidence':'yes','download_size_gb':1,'install_directory':'x','commands':['x'],'rollback':'x','paid_api':True}
  with self.assertRaises(ValueError):check_plan(p)
 def test_comfyui_remote_block(self):
  for u in ['https://127.0.0.1:8188','http://www.example.com:8188','http://127.0.0.1:8188/prompt','http://localhost:80@bad.test:8188']:
   with self.assertRaises(ValueError):check_url(u)
  check_url('http://127.0.0.1:8188')
 def test_comfyui_workflow_schema(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'w.json';p.write_text(json.dumps({'1':{'class_type':'SaveImage','inputs':{'filename_prefix':'GENESIS'}}}))
   self.assertEqual(1,len(load_workflow(p)))
   p.write_text('{}')
   with self.assertRaises(ValueError):load_workflow(p)
 def test_real_asset_hash_and_no_final(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'g.bin';p.write_bytes(b'abc')
   r=build_record(p,'GENESIS_TEST_01','blender','none','CANON_TEST','LICENSE_TEST','GENERATED_PREVIEW')
   self.assertEqual(64,len(r['sha256']))
   with self.assertRaises(ValueError):build_record(p,'GENESIS_TEST_01','blender','none','X','Y','DIRECTOR_ACCEPTED')
 def test_hook_denies_unapproved_pip_install(self):
  with tempfile.TemporaryDirectory() as d:
   payload={'tool_name':'Bash','tool_input':{'command':'pip install an-unreviewed-package'}}
   self.assertIsNotNone(install_check(payload,Path(d)))
 def test_hook_allows_safe_read(self):
  self.assertIsNone(install_check({'tool_name':'Bash','tool_input':{'command':'git status --short'}},Path('/tmp/nonexistent-genesis-approvals')))
 def test_hook_receipt_for_exact_command(self):
  with tempfile.TemporaryDirectory() as d:
   dir=Path(d)
   p={'plan_id':'INSTALL-001','tool_id':'comfyui','source_url':'https://github.com/Comfy-Org/ComfyUI','source_revision':'pinned','license_evidence':'checked','download_size_gb':1,'install_directory':'C:/tools/comfy','commands':['git clone https://github.com/Comfy-Org/ComfyUI'], 'rollback':'delete isolated tool folder'}
   (dir/'p.json').write_text(json.dumps(p))
   (dir/'p.approval.json').write_text(json.dumps({'approved':True,'scope':'ONE_TOOL_REVISION','confirmation':'FREIGABE INSTALL-001','plan_sha256':digest(p)}))
   self.assertIsNone(install_check({'tool_name':'Bash','tool_input':{'command':p['commands'][0]}},dir))
   self.assertIsNotNone(install_check({'tool_name':'Bash','tool_input':{'command':'git clone https://example.org/another'}} ,dir))
 def test_audio_wav_scan(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'test.wav'
   with wave.open(str(f),'wb') as wf:wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(8000);wf.writeframes(b'\0\0'*8000)
   self.assertAlmostEqual(1.,scan(f)['duration_seconds'])
 def test_no_model_downloads_in_package(self):
  root=Path(__file__).resolve().parents[2]
  # Unreal build/cache folders (gitignored) hold engine-made .pth path files, not models
  engine_dirs={'Intermediate','Saved','Binaries','DerivedDataCache'}
  bad=[p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in ('.safetensors','.ckpt','.onnx','.pt','.pth') and not engine_dirs.intersection(p.relative_to(root).parts[:1])]
  self.assertEqual([],bad)

if __name__=='__main__':unittest.main()
