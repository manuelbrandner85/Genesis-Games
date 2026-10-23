"""Run INSIDE Unreal Python Editor/Commandlet with GENESIS_ASSET_MANIFEST path in env.
Never marks import successful unless real AssetRegistry load returns a valid Unreal asset.
Only supports static meshes automatically; skeletal meshes require verified importer contract.
"""
import os,json
from pathlib import Path
import unreal
p=os.environ.get('GENESIS_ASSET_MANIFEST')
if not p or not Path(p).is_file(): raise RuntimeError('GENESIS_ASSET_MANIFEST must refer to existing JSON')
m=json.loads(Path(p).read_text('utf-8'))
if m.get('type')!='static_mesh':raise RuntimeError('Skeletal mesh requires separate verified rig import workflow')
asset_path=str(m.get('ue_path') or '/Game/Genesis/Prototyping')
if not asset_path.startswith('/Game/Genesis/') or '..' in asset_path:raise RuntimeError('Non-GENESIS UE path denied')
exports=m.get('exports') or []
if not exports:raise RuntimeError('Manifest contains no exports')
exp=next((e for e in exports if str(e).lower().endswith('.fbx')),None)
if not exp:raise RuntimeError('FBX export not found')
if not Path(exp).is_file():raise RuntimeError('Missing real FBX export: '+exp)
req=unreal.AssetImportTask();req.set_editor_property('filename',str(Path(exp).resolve()))
req.set_editor_property('destination_path',asset_path)
req.set_editor_property('automated',True);req.set_editor_property('save',True);req.set_editor_property('replace_existing',False)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([req])
paths=list(req.get_editor_property('imported_object_paths'))
if not paths:raise RuntimeError('Unreal returned 0 imported objects')
for path in paths:
 obj=unreal.load_asset(path)
 if obj is None:raise RuntimeError('Imported object cannot be reloaded: '+path)
 unreal.log('GENESIS_REAL_IMPORT_SUCCESS: '+path+' '+str(obj.get_class().get_name()))
print(json.dumps({'status':'UE_IMPORT_READBACK_PASS','real_asset_paths':paths,'graphics_playtest':'NOT_RUN','performance':'NOT_RUN'},ensure_ascii=False))
