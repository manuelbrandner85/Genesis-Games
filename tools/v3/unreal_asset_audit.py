"""Run INSIDE Unreal Editor-Python, never standard Python; needs GENESIS_V3_UE_ASSET and GENESIS_V3_REPORT.
"""
import os, json
from pathlib import Path
import unreal
path=os.environ.get('GENESIS_V3_UE_ASSET','');out=os.environ.get('GENESIS_V3_REPORT','')
if not path.startswith('/Game/Genesis/') or '..' in path:raise RuntimeError('GENESIS_V3_UE_ASSET missing or outside /Game/Genesis/')
if not out:raise RuntimeError('GENESIS_V3_REPORT absent')
asset=unreal.load_asset(path)
if asset is None:raise RuntimeError('Unreal asset not loaded: '+path)
asset_class=asset.get_class().get_name()
entry={'status':'ASSET_READBACK_ONLY_NOT_PLAYTESTED','path':path,'asset_class':str(asset_class),'unreal_version':str(unreal.SystemLibrary.get_engine_version())}
try:
    mats=asset.get_editor_property('static_materials')
    entry['static_material_count']=len(mats)
except Exception as exc:
    entry['static_material_count']='UNAVAILABLE_'+str(type(exc).__name__)
p=Path(out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(entry,indent=2,ensure_ascii=False),encoding='utf-8')
unreal.log('GENESIS_V3_ASSET_READBACK_WRITTEN '+str(p))
