"""C00 (runs INSIDE Blender, scene C00_Shirt): export the man's fitted shirt as the static source for the Unreal skinning
(tools/v4_2/c00_shirt_gs_skin.py imports ArtSource/Export/C00/SM_C00_Shirt_fitted.fbx).

Regie 2026-10-25 (close-up): the Fab shirt is a single sheet - collar and sleeve hems read as paper edges, the
inside showed as a dark line. Real cotton jersey is ~1 mm thick and the hems are turned and stitched (~3 mm). A
Solidify with rim fill gives the shirt that thickness, grown inward so the outer surface (which the duvet drape and
collision were fitted to) stays where it is. Exported in the rest pose (armature deform off), metres -> Unreal cm.
"""
import os

import bpy

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "ArtSource", "Export", "C00", "SM_C00_Shirt_fitted.fbx")
sc = bpy.data.scenes["C00_Shirt"]
shirt = bpy.data.objects["SM_Shirt_01_man"]
arm = shirt.parent
pose_was = arm.data.pose_position
arm.data.pose_position = "REST"
for m in shirt.modifiers:
    if m.type == "ARMATURE":
        m.show_viewport = m.show_render = False
so = shirt.modifiers.get("Thickness") or shirt.modifiers.new("Thickness", "SOLIDIFY")
so.thickness, so.offset = 0.003, -1.0                  # 3 mm hems/collar, grown toward the body
so.use_rim, so.use_rim_only, so.use_even_offset, so.use_quality_normals = True, False, False, True
with bpy.context.temp_override(scene=sc, view_layer=sc.view_layers[0]):   # the shirt's own scene, not the window's
    deps = bpy.context.evaluated_depsgraph_get()
    deps.update()
ev = shirt.evaluated_get(deps)
me = bpy.data.meshes.new_from_object(ev, depsgraph=deps)
tmp = bpy.data.objects.new("SM_C00_Shirt_fitted", me)
tmp.matrix_world = shirt.matrix_world.copy()
sc.collection.objects.link(tmp)
with bpy.context.temp_override(selected_objects=[tmp], active_object=tmp, scene=sc, view_layer=sc.view_layers[0]):
    bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, object_types={"MESH"}, apply_unit_scale=True,
                             apply_scale_options="FBX_SCALE_UNITS", mesh_smooth_type="FACE", axis_forward="-Z", axis_up="Y",
                             use_mesh_modifiers=False, bake_anim=False)
verts = len(me.vertices)
bpy.data.objects.remove(tmp, do_unlink=True)
bpy.data.meshes.remove(me)
shirt.modifiers.remove(so)                               # the skinned Blender shirt itself stays a single sheet
for m in shirt.modifiers:
    if m.type == "ARMATURE":
        m.show_viewport = m.show_render = True
arm.data.pose_position = pose_was
result = {"fbx": OUT, "verts": verts}
print("C00_SHIRT_FITTED", result)
