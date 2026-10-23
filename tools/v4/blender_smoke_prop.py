"""Run in BLENDER, not normal CPython: blender -b --python script.py -- --output <DIR>
Creates only neutral TECH SMOKE assets; not an actual GENESIS character or real game asset.
"""
import sys,argparse,hashlib,json
from pathlib import Path
try:
    import bpy
except ImportError as e:
    raise RuntimeError('TOOL_UNAVAILABLE: this script must run inside Blender') from e

ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,0.5))
ob=bpy.context.active_object;ob.name='SM_SmokeCrate_001';ob.dimensions=(1,1,1)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
blend=out/'SM_SmokeCrate_001.blend';fbx=out/'SM_SmokeCrate_001.fbx'
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
if not hasattr(bpy.ops,'export_scene') or not hasattr(bpy.ops.export_scene,'fbx'):
    raise RuntimeError('BLENDER_EXPORT_UNAVAILABLE: FBX exporter missing or Blender API changed')
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,apply_unit_scale=True)
if not blend.is_file() or not fbx.is_file() or fbx.stat().st_size<=0:raise RuntimeError('Asset output missing')
manifest={'asset_id':'SM_SmokeCrate_001','type':'static_mesh','is_technical_proxy':True,'ue_path':'/Game/Genesis/TechSmoke',
 'exports':[str(fbx)],'blender_master':str(blend),'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [blend,fbx]},
 'quality':'DCC_EXPORT_ONLY','ue_import':'NOT_TESTED'}
(out/'asset_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'status':'BLENDER_SMOKE_EXPORT_DONE_UE_NOT_TESTED','manifest':str(out/'asset_manifest.json')},ensure_ascii=False))
