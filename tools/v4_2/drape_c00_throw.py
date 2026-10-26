"""C00 (runs INSIDE Blender, scene C00_Schlafzimmer, after detail_c00_furniture.py): the mustard knitted throw over the
backrest of the daughter's chair, simulated again over the new curved backrest.

QA 2026-10-25: the throw had been simulated over the old flat board backrest (it would cut through the bent-plywood
one) and had no UVs - the knit pattern in Unreal (M_C00_SetFabric, WeaveScale) needs them. The sheet (1.10 x 1.30 m,
UV 0..1) starts hanging behind the backrest top and falls over it: most of it behind the chair (toward the radiator),
a short end on the back of the seat - the front of the seat stays free for the daughter.
Works in the chair's current frame (seat bounding-box centre + rotation), so it follows place_c00_chair.py.
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

sc = bpy.data.scenes["C00_Schlafzimmer"]
dc = bpy.data.collections["C00_SZ_Deko"]
D = 3.20
BX = -0.25
CX, CY = BX + 0.95, -0.15                                         # chair frame of build_c00_bedroom.py
seat = bpy.data.objects["SZ_ChairSeat"]
_bb = [seat.matrix_world @ Vector(c) for c in seat.bound_box]
_c = Vector((sum(v.x for v in _bb) / 8, sum(v.y for v in _bb) / 8, 0.46))
M_chair = Matrix.Translation(_c) @ seat.matrix_world.to_quaternion().to_matrix().to_4x4() @ Matrix.Translation((-CX, -CY, -0.46))

old = bpy.data.objects.get("SZ_Throw")
mat = old.data.materials[0] if old and old.data.materials else bpy.data.materials.get("M_SZ_ThrowWool")
if old:
    bpy.data.objects.remove(old, do_unlink=True)
colliders = [o for o in sc.objects if o.name.startswith(("SZ_Chair", "SZ_Radiator", "SZ_RadRib", "SZ_WallE", "SZ_InnerSill"))] +     [bpy.data.objects["SZ_Floor"]]                                # only 33 cm between backrest and radiator
for c in colliders:
    if not any(m.type == "COLLISION" for m in c.modifiers):
        c.modifiers.new("Collision", "COLLISION")
    c.collision.thickness_outer = 0.004
    c.collision.cloth_friction = 15
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=44, y_segments=52, size=0.5, calc_uvs=True)
for v in bm.verts:
    v.co = Vector((v.co.x * 1.3, v.co.y * 0.55, 0))                  # folded once lengthwise: 1.30 x 0.55, two layers
me = bpy.data.meshes.new("SZ_Throw")
bm.to_mesh(me)
bm.free()
for p in me.polygons:
    p.use_smooth = True
throw = bpy.data.objects.new("SZ_Throw", me)
dc.objects.link(throw)
me.materials.append(mat)
# chair frame: seat at (CX, CY), backrest at -y (top 0.86 m at ~CY-0.265). The sheet starts flat 4 cm above the
# backrest top, its centre 8 cm behind it: it folds over the backrest edge, ~10 cm lie on the back of the seat
# (a first try hanging vertically behind the backrest touched nothing and fell to the floor)
M_local = Matrix.Translation((CX + 0.02, CY - 0.205 - 0.06 - 0.08, 0.90)) @ Matrix.Rotation(math.radians(5), 4, "Z")
throw.matrix_world = M_chair @ M_local
cl = throw.modifiers.new("Cloth", "CLOTH")
st = cl.settings
st.quality, st.mass, st.air_damping = 10, 0.5, 2.0
st.bending_stiffness = 0.3
cl.collision_settings.use_self_collision = True
cl.collision_settings.distance_min = cl.collision_settings.self_distance_min = 0.004
cl.point_cache.frame_start, cl.point_cache.frame_end = 1, 80
sc.frame_start, sc.frame_end = 1, 80
for fr in range(1, 81):
    sc.frame_set(fr)
with bpy.context.temp_override(object=throw, active_object=throw, selected_objects=[throw], scene=sc):
    bpy.ops.object.modifier_apply(modifier="Cloth")
sc.frame_set(1)
so = throw.modifiers.new("Knit", "SOLIDIFY")
so.thickness, so.use_even_offset = 0.016, False                   # two knitted layers
throw.modifiers.new("Soft", "SUBSURF").levels = 1
for c in colliders:                                               # leave the colliders clean for the export
    for m in [m for m in c.modifiers if m.type == "COLLISION"]:
        c.modifiers.remove(m)
ws = [throw.matrix_world @ v.co for v in throw.data.vertices]
inv = M_chair.inverted()
loc = [inv @ w for w in ws]
result = {"throw_z": [round(min(w.z for w in ws), 3), round(max(w.z for w in ws), 3)],
          "on_seat_front": sum(1 for l in loc if l.y > CY + 0.0 and abs(l.x - CX) < 0.22 and 0.44 < l.z < 0.6)}
print("C00_THROW", result)
