"""C00 (runs INSIDE Blender 5.2): export SET_C00_SCHLAFZIMMER for Unreal.

Every visible mesh of the C00_Schlafzimmer collection (room, bed with the occupied duvet, rain, exterior)
is evaluated with its modifiers and written in world space (origin = room origin), so Unreal can place
all imported meshes at its world origin. Material slots keep the M_SZ_* names; Unreal maps them to its own
material instances (tools/v4_2/c00_scene_bedroom.py). Output: ArtSource/Export/C00/SET_C00_Schlafzimmer.fbx
"""
import bpy
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "ArtSource", "Export", "C00", "SET_C00_Schlafzimmer.fbx")
sc = bpy.data.scenes["C00_Schlafzimmer"]
src = bpy.data.collections["C00_Schlafzimmer"]
tmp = bpy.data.collections.get("C00_SZ_Export")
if tmp:
    for o in list(tmp.objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    tmp = bpy.data.collections.new("C00_SZ_Export")
    sc.collection.children.link(tmp)
deps = bpy.context.evaluated_depsgraph_get()
count = 0
for o in src.all_objects:
    if o.type != "MESH" or o.hide_render:
        continue
    me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
    me.transform(o.matrix_world)
    c = bpy.data.objects.new("UE_" + o.name, me)
    tmp.objects.link(c)
    count += 1
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with bpy.context.temp_override(selected_objects=list(tmp.objects), active_object=tmp.objects[0], scene=sc):
    bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
                             object_types={"MESH"}, use_mesh_modifiers=False, mesh_smooth_type="FACE",
                             path_mode="AUTO", embed_textures=False, axis_forward="-Z", axis_up="Y")
for o in list(tmp.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.collections.remove(tmp)
result = {"meshes": count, "fbx": OUT, "mb": round(os.path.getsize(OUT) / 1e6, 1)}
