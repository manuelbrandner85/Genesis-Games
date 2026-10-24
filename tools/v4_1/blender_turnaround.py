"""Run in Blender 4.x/5.x: blender -b your_asset.blend --python tools/v4_1/blender_turnaround.py -- --output DIR.
Renders existing mesh without changing/saving source scene. Does not generate mesh from prompts.
"""
import sys
from pathlib import Path

def main():
    import bpy,math
    from mathutils import Vector
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    if '--output' not in args:raise SystemExit('Usage: blender -b asset.blend --python this.py -- --output output_dir')
    output=Path(args[args.index('--output')+1]).resolve();output.mkdir(parents=True,exist_ok=True)
    meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH' and not obj.hide_render]
    if not meshes:raise SystemExit('NO_MESH_IN_SCENE: no actual asset to render')
    world=[]
    for obj in meshes:world += [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    mins=[min(v[i] for v in world) for i in range(3)];maxs=[max(v[i] for v in world) for i in range(3)]
    center=Vector([(mins[i]+maxs[i])/2 for i in range(3)]);radius=max(maxs[i]-mins[i] for i in range(3)) or 1
    cam=bpy.data.cameras.new('GENESIS_V41_QA_Camera');o=bpy.data.objects.new('GENESIS_V41_QA_Camera',cam);bpy.context.scene.collection.objects.link(o)
    bpy.context.scene.camera=o;cam.type='ORTHO';cam.ortho_scale=radius*1.8
    scene=bpy.context.scene;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    for name,angle in [('front',0),('side',90),('back',180),('quarter',45)]:
        radians=math.radians(angle);o.location=center+Vector((math.cos(radians),math.sin(radians),.35))*radius*2.5
        o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(output/(name+'.png'));bpy.ops.render.render(write_still=True)
        print('RENDERED_REAL_ASSET:',name,scene.render.filepath)
    bpy.data.objects.remove(o,do_unlink=True)
    print('BLENDER_RENDERED_FROM_EXISTING_SCENE_NOT_MODEL_GENERATION')
if __name__=='__main__':main()
