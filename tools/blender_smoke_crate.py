"""GENESIS smoke test: build a simple editable crate, export FBX+GLB, render views.
Run inside Blender, e.g. blender -b --python tools/blender_smoke_crate.py -- <output_dir>
This deliberately produces a BASIC TEST object, NOT a production GENESIS asset.
"""
import bpy, os, math, sys, json
from mathutils import Vector
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[0]) if args else Path.cwd()/'smoke_output'
out.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1.0
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,0,0.5))
crate=bpy.context.object; crate.name='SM_TEST_Crate_1m'
crate.dimensions=(1.0,1.0,1.0); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
mat=bpy.data.materials.new('MAT_TEST_WarmWood');mat.diffuse_color=(0.36,0.20,0.10,1)
mat.use_nodes=True; bsdf=mat.node_tree.nodes.get('Principled BSDF')
if bsdf:
    bsdf.inputs['Base Color'].default_value=(0.36,0.20,0.10,1)
    bsdf.inputs['Roughness'].default_value=0.72
crate.data.materials.append(mat)
bevel=crate.modifiers.new('EdgeBevel','BEVEL');bevel.width=0.02;bevel.segments=2
bpy.context.view_layer.objects.active=crate
bpy.ops.object.modifier_apply(modifier=bevel.name)
crate.select_set(True)
# Light + camera objects are NOT exported as selected objects.
ld=bpy.data.lights.new('Softbox','AREA');lo=bpy.data.objects.new('Softbox',ld);s.collection.objects.link(lo)
lo.location=(3,-4,6);ld.energy=900;ld.shape='DISK';ld.size=5
camd=bpy.data.cameras.new('TurnaroundCam');cam=bpy.data.objects.new('TurnaroundCam',camd);s.collection.objects.link(cam)
s.camera=cam;camd.type='ORTHO';camd.ortho_scale=2.5
s.render.resolution_x=512;s.render.resolution_y=512;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
views={'front':(0,-4,1.2),'back':(0,4,1.2),'left':(-4,0,1.2),'right':(4,0,1.2),'top':(0,0,5),'iso':(3,-4,3)}
for name,pos in views.items():
    cam.location=pos
    direction=Vector((0,0,0.5))-cam.location
    cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str(out/f'view_{name}.png')
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'TEST_SMOKE_CRATE_001.blend'))
# Select only mesh: gives a clear FBX import target.
bpy.ops.object.select_all(action='DESELECT');crate.select_set(True);bpy.context.view_layer.objects.active=crate
bpy.ops.export_scene.fbx(filepath=str(out/'TEST_SMOKE_CRATE_001.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False)
bpy.ops.export_scene.gltf(filepath=str(out/'TEST_SMOKE_CRATE_001.glb'),export_format='GLB',use_selection=True)
files=[str(x) for x in sorted(out.iterdir()) if x.is_file()]
(out/'smoke_manifest.json').write_text(json.dumps({'asset_id':'TEST_SMOKE_CRATE_001','object_dims_m':list(crate.dimensions),'blender_version':bpy.app.version_string,'files':files,'status':'BUILT_UNTESTED_UNREAL'},indent=2),encoding='utf-8')
print('GENESIS_SMOKE_BLENDER_SUCCESS',str(out))
