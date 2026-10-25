"""C00 (runs INSIDE Blender 5.2): the man's real posed body + shirt as collision for the duvet.

Capsule proxies only approximated the shirt; parts of it showed through the duvet (Regie 2026-10-25). Here the
exported body (SKM_C00_Mann_Body.fbx) and the fitted, skinned shirt in scene "C00_Shirt"
(tools/v4_2/build_c00_shirt_skinned.py) are put into exactly the pose Unreal uses: the component-space ref/new
transforms of every posed bone come from tools/v4_2/c00_pose_lying.py (C00_POSE_JOINTS.json "posed").
UE component space (cm, left-handed) -> Blender armature space: b = S c / 100 with S = diag(1, -1, 1).
Arms, hands and sleeves are removed (they rest ON the duvet). Output: meshes "SZ_PosedBody" and "SZ_PosedShirt" in
collection "C00_SZ_Collision" (Blender armature space; not exported, not rendered).
"""
import bpy
import json
import os
from mathutils import Matrix, Quaternion, Vector

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
POSE = json.load(open(os.path.join(ROOT, "docs", "v4_2", "C00_POSE_JOINTS.json"), encoding="utf8"))
sc = bpy.data.scenes["C00_Shirt"]
arm = sc.objects["root"]
body = next(o for o in sc.objects if o.type == "MESH" and not o.name.startswith("SM_Shirt"))
shirt = sc.objects["SM_Shirt_01_man"]
if body.find_armature() is None:
    m = body.modifiers.new("Armature", "ARMATURE")
    m.object = arm

S = Matrix(((1, 0, 0), (0, -1, 0), (0, 0, 1)))
ORDER = ["thigh_l", "thigh_r", "foot_l", "foot_r", "neck_01", "neck_02", "head",
         "upperarm_l", "lowerarm_l", "hand_l", "upperarm_r", "lowerarm_r", "hand_r"]


def ue_quat(q):
    x, y, z, w = q
    return Quaternion((w, x, y, z))


arm.data.pose_position = "POSE"                               # the shirt export leaves it in REST
for pb in arm.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
sc.view_layers[0].update()
for name in ORDER:
    if name not in POSE["posed"] or name not in arm.pose.bones:
        continue
    ref_t, ref_q = POSE["posed"][name]["ref"]
    new_t, new_q = POSE["posed"][name]["new"]
    Rc = (ue_quat(new_q) @ ue_quat(ref_q).inverted()).to_matrix()
    Rb = S @ Rc @ S
    tb = S @ (Vector(new_t) - Rc @ Vector(ref_t)) / 100.0
    delta = Matrix.Translation(tb) @ Rb.to_4x4()
    arm.pose.bones[name].matrix = delta @ arm.data.bones[name].matrix_local
    sc.view_layers[0].update()

ARM_BONES = ("upperarm", "lowerarm", "hand", "thumb", "index", "middle", "ring", "pinky")
col = bpy.data.collections.get("C00_SZ_Collision")
if col is None:
    col = bpy.data.collections.new("C00_SZ_Collision")
    bpy.data.scenes["C00_Schlafzimmer"].collection.children.link(col)
for o in list(col.objects):
    bpy.data.objects.remove(o, do_unlink=True)
with bpy.context.temp_override(scene=sc, view_layer=sc.view_layers[0]):   # the shirt scene, also without a window
    deps = bpy.context.evaluated_depsgraph_get()
    deps.update()
out = {}
for src, name in ((body, "SZ_PosedBody"), (shirt, "SZ_PosedShirt")):
    me = bpy.data.meshes.new_from_object(src.evaluated_get(deps), preserve_all_data_layers=False, depsgraph=deps)
    me.transform(src.matrix_world)
    arm_groups = {g.index for g in src.vertex_groups if g.name.startswith(ARM_BONES)}
    drop = set()
    for v in src.data.vertices:                         # same vertex order as the evaluated mesh (no topology change)
        w_arm = sum(g.weight for g in v.groups if g.group in arm_groups)
        # QA 2026-10-25: at 0.3 the shirt lost its sleeve roots from the collision and a shirt sliver pierced the duvet
        # beside the chest; the shirt keeps everything except the sleeve proper, the body still drops its arms
        if w_arm > (0.3 if src is body else 0.85):
            drop.add(v.index)
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.verts[i] for i in drop if i < len(bm.verts)], context="VERTS")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    o.hide_render = True
    out[name] = {"verts": len(me.vertices), "dropped_arm": len(drop)}
for pb in arm.pose.bones:                                 # leave the shirt scene in rest pose
    pb.matrix_basis = Matrix.Identity(4)
result = out
