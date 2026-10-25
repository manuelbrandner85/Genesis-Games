"""C00 (runs INSIDE Blender 5.2, scene "C00_Shirt"): the Fab V-neck shirt as an own skinned mesh for the man.

MetaHuman outfits do not follow a pose in a level (only in the Creator preview), so the shirt's sleeves stayed in
A-pose when he lies with his hands on the duvet. Here the Fab source mesh (SM_Shirt_01_man, Nyanpasinka, Standard
licence) is fitted to the man's real exported body (SKM_C00_Mann_Body.fbx, tools/v4_2/c00_export_body_shirt.py):
- 2x subdivided (the source mesh has 887 vertices), vertices inside the body pushed 5 mm outside
- vertex weights transferred from the body (nearest face, interpolated), bound to the body armature
Output: ArtSource/Export/C00/SKM_C00_Mann_Shirt.fbx (skeleton = metahuman_base_skel; local only, Fab content)
"""
import bpy
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "ArtSource", "Export", "C00", "SKM_C00_Mann_Shirt.fbx")
sc = bpy.data.scenes["C00_Shirt"]
arm = next(o for o in sc.objects if o.type == "ARMATURE")
other = bpy.data.objects.get("root")
if other and other != arm:
    other.name = "root_other_scene"
arm.name = "root"                                             # FBX null node = root bone of metahuman_base_skel
body = next(o for o in sc.objects if o.type == "MESH" and o.find_armature() == arm and not o.name.startswith("SM_Shirt"))
# the UE FBX import puts the armature (bones in cm) under an empty scaled 0.01; exporting the armature alone would
# lose that scale and the shirt collapses 100x in Unreal - so the scale is applied to armature and body first
if arm.parent:
    for o in (arm, body):
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = mw
    with bpy.context.temp_override(selected_objects=[arm, body], selected_editable_objects=[arm, body], active_object=arm, object=arm, scene=sc):
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
old = sc.objects.get("SM_Shirt_01_man")
if old:
    bpy.data.objects.remove(old, do_unlink=True)
with bpy.context.temp_override(scene=sc, view_layer=sc.view_layers[0]):
    bpy.ops.import_scene.fbx(filepath=os.path.join(ROOT, "ArtSource", "Export", "C00", "SM_C00_Shirt01_man.fbx"))
shirt = sc.objects["SM_Shirt_01_man"]

with bpy.context.temp_override(object=shirt, active_object=shirt, selected_objects=[shirt], selected_editable_objects=[shirt], scene=sc):
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for m in list(shirt.modifiers):
    shirt.modifiers.remove(m)
for g in list(shirt.vertex_groups):
    shirt.vertex_groups.remove(g)
sub = shirt.modifiers.new("Subdiv", "SUBSURF")
sub.levels = sub.render_levels = 2
sw = shirt.modifiers.new("Clear", "SHRINKWRAP")              # only vertices inside the body move out
sw.wrap_method, sw.wrap_mode, sw.target, sw.offset = "NEAREST_SURFACEPOINT", "OUTSIDE", body, 0.005
dt = shirt.modifiers.new("Weights", "DATA_TRANSFER")
dt.object, dt.use_vert_data, dt.data_types_verts = body, True, {"VGROUP_WEIGHTS"}
dt.vert_mapping = "POLYINTERP_NEAREST"
dt.layers_vgroup_select_src, dt.layers_vgroup_select_dst = "ALL", "NAME"
with bpy.context.temp_override(object=shirt, active_object=shirt, selected_objects=[shirt], scene=sc):
    bpy.ops.object.datalayout_transfer(modifier="Weights")
    for name in ("Subdiv", "Clear", "Weights"):
        bpy.ops.object.modifier_apply(modifier=name)
for p in shirt.data.polygons:
    p.use_smooth = True
shirt.parent = arm
am = shirt.modifiers.new("Armature", "ARMATURE")
am.object = arm
# keep only groups that carry weight (the body has hundreds of corrective bones)
used = set()
for v in shirt.data.vertices:
    for g in v.groups:
        if g.weight > 0.001:
            used.add(shirt.vertex_groups[g.group].name)
for name in [g.name for g in shirt.vertex_groups if g.name not in used]:   # by name: indices shift on removal
    shirt.vertex_groups.remove(shirt.vertex_groups[name])

# export the rest pose only: a leftover import pose makes FBX cluster and pose bind matrices disagree
# (Unreal: "ungueltige Bindeposen" - the torso then collapses onto the spine under the leader pose)
for pb in arm.pose.bones:
    pb.location, pb.rotation_quaternion, pb.rotation_euler, pb.scale = (0, 0, 0), (1, 0, 0, 0), (0, 0, 0), (1, 1, 1)
arm.data.pose_position = "REST"
with bpy.context.temp_override(selected_objects=[arm, shirt], active_object=arm, scene=sc):
    bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, object_types={"ARMATURE", "MESH"}, add_leaf_bones=False,
                             apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS", use_armature_deform_only=False,
                             bake_anim=False, mesh_smooth_type="FACE", axis_forward="-Z", axis_up="Y", primary_bone_axis="Y",
                             secondary_bone_axis="X", armature_nodetype="NULL")
result = {"verts": len(shirt.data.vertices), "groups": len(shirt.vertex_groups), "fbx": OUT,
          "root_bone": arm.data.bones[0].name, "armature_obj": arm.name}
