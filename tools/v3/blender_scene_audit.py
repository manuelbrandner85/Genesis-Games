"""Runs INSIDE Blender: blender -b scene.blend --python this_file.py -- --out report.json
Inspects opened scene, does not generate or certify a high-end model.
"""
import bpy,sys,json,hashlib,datetime
from pathlib import Path
from mathutils import Vector

def main():
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    if '--out' not in args or args.index('--out')+1>=len(args):raise RuntimeError('Must provide -- --out path')
    out=Path(args[args.index('--out')+1]).resolve();scene_file=Path(bpy.data.filepath)
    if not scene_file.is_file():raise RuntimeError('Real saved .blend file must be opened before audit')
    results=[]
    for obj in bpy.data.objects:
        entry={'name':obj.name,'type':obj.type,'hidden_render':bool(obj.hide_render),'materials':[]}
        if obj.type=='MESH':
            world_corners=[obj.matrix_world@Vector(c) for c in obj.bound_box]
            scale_m=float(bpy.context.scene.unit_settings.scale_length) if bpy.context.scene.unit_settings.system!='NONE' else 1.0
            bounds={ax:round((max(v[i] for v in world_corners)-min(v[i] for v in world_corners))*scale_m,6) for i,ax in enumerate('xyz')}
            entry.update(vertices=len(obj.data.vertices),polygons=len(obj.data.polygons),bounds_m=bounds,scale=[float(v) for v in obj.scale])
            entry['materials']=[m.name if m else None for m in obj.data.materials]
        if obj.type=='ARMATURE':entry['bones']=[bone.name for bone in obj.data.bones]
        results.append(entry)
    info={'status':'SCENE_STRUCTURE_INSPECTED_VISUAL_QA_NOT_DONE','blender_version':bpy.app.version_string,'blend_file':str(scene_file),'blend_sha256':hashlib.sha256(scene_file.read_bytes()).hexdigest(),'unit_system':bpy.context.scene.unit_settings.system,'scale_length':bpy.context.scene.unit_settings.scale_length,'unit_note':'Bounds interpreted as meters only when scene unit convention is correct; compare to approved asset measurements','objects':results,'external_images':[{'name':i.name,'filepath':bpy.path.abspath(i.filepath),'exists':bool(i.packed_file) or Path(bpy.path.abspath(i.filepath)).is_file()} for i in bpy.data.images if i.source=='FILE']}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    print('GENESIS_V3_BLENDER_AUDIT_WRITTEN',str(out))
if __name__=='__main__':main()
