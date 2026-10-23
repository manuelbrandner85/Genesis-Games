"""Render six views of an EXISTING Blender model; not image generation from a text prompt.
blender -b MASTER.blend --python tools/blender/render_turnaround.py -- OUTPUT_DIR [OBJECT_NAME]
"""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if not args:raise SystemExit('usage: -- OUTPUT_DIR [OBJECT_NAME]')
out=Path(args[0]).resolve();out.mkdir(parents=True,exist_ok=True)
obj=bpy.data.objects.get(args[1]) if len(args)>1 else next((x for x in bpy.context.scene.objects if x.type=='MESH'),None)
if not obj or obj.type!='MESH':raise RuntimeError('Existing mesh required; reference not fabricated')
scene=bpy.context.scene
center=sum((obj.matrix_world @ Vector(corner) for corner in obj.bound_box),Vector())/8.0
radius=max(float(x) for x in obj.dimensions) * 2.6
camera_data=bpy.data.cameras.new('GENESIS_Turnaround_Camera');cam=bpy.data.objects.new('GENESIS_Turnaround_Camera',camera_data);scene.collection.objects.link(cam);scene.camera=cam
camera_data.type='ORTHO';camera_data.ortho_scale=max(float(x) for x in obj.dimensions)*1.5
world=bpy.data.worlds.new('GENESIS_Turnaround_World') if scene.world is None else scene.world
world.use_nodes=True;scene.world=world
scene.render.resolution_x=1024;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
light=bpy.data.lights.new('GENESIS_Turnaround_Light','AREA');l=bpy.data.objects.new('GENESIS_Turnaround_Light',light);scene.collection.objects.link(l);l.location=center+Vector((radius,-radius,radius*2));light.energy=1000;light.shape='DISK';light.size=max(2,radius)
views={'front':(0,-1,0),'back':(0,1,0),'left':(-1,0,0),'right':(1,0,0),'top':(0,0,1),'three_quarter':(0.7,-1,0.35)}
files=[]
for name,direction in views.items():
  cam.location=center+Vector(direction).normalized()*radius
  cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
  scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);files.append(str(out/(name+'.png')))
(out/'turnaround_report.json').write_text(json.dumps({'object':obj.name,'views':files,'asset_has_only_existing_geometry':True,'artist_review':'NOT_RUN','unreal_test':'NOT_RUN'},indent=2),'utf-8')
print('GENESIS_TURNAROUND_RENDERED',len(files))
