"""C00 (runs INSIDE Blender, scene C00_Schlafzimmer, after build_c00_bedroom.py): furniture details.

QA 2026-10-25 (Regie: "es gibt immer noch sehr unrealistische Details ... schaue weitere Details im Raum an"): nightstand
and chair were plain boxes with 4-6 mm bevels - read as toy blocks up close.
- nightstand: top board 2.2 cm with 8 mm overhang and a softened edge, the carcass set back under it, a recessed plinth
  shadow gap, the drawer front as its own panel with 3 mm gaps and a turned oak knob
- chair: seat with a 1 cm rounded edge and a slightly dished top, backrest as a curved bent-plywood panel, legs tapered
  and splayed 3 deg, with stretchers between the legs
Idempotent: replaces the objects of the same names. The chair's own transform from place_c00_chair.py is kept by
building in the chair's original frame and applying the current seat matrix.
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

sc = bpy.data.scenes["C00_Schlafzimmer"]
col = bpy.data.collections["C00_Schlafzimmer"]
D = 3.20
BX, BY0 = -0.25, D / 2 - 0.03
NX, NY = BX + 0.75 + 0.27, D / 2 - 0.22
OAK = bpy.data.materials["M_SZ_OakVeneer"]
GAP = bpy.data.materials["M_SZ_FrameWood"]


def make(name, bm, m, bevel=None, seg=3, smooth=False):
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    me.materials.append(m)
    if bevel:
        b = o.modifiers.new("Bevel", "BEVEL")
        b.width, b.segments, b.limit_method, b.harden_normals = bevel, seg, "ANGLE", True
        me.shade_smooth()
        if hasattr(me, "set_sharp_from_angle"):
            me.set_sharp_from_angle(angle=math.radians(40))
    return o


def box(size, c):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0] + c[0], v.co.y * size[1] + c[1], v.co.z * size[2] + c[2]))
    return bm


def taper_cyl(r1, r2, h, c, segs=24):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts:
        v.co += Vector(c)
    return bm


# ------------------------------------------------------------------ nightstand (0.45 x 0.38 x 0.50 on 6 cm legs)
for n in ("SZ_Nightstand", "SZ_NightstandDrawerGap"):
    o = bpy.data.objects.get(n)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
Z0, Z1 = 0.06, 0.56
TOPT = 0.022
make("SZ_Nightstand", box((0.43, 0.365, Z1 - TOPT - Z0 - 0.012), (NX, NY + 0.004, (Z0 + 0.012 + Z1 - TOPT) / 2)), OAK, 0.002)
make("SZ_NightstandTop", box((0.45, 0.38, TOPT), (NX, NY, Z1 - TOPT / 2)), OAK, 0.005, 4)
make("SZ_NightstandPlinth", box((0.40, 0.33, 0.012), (NX, NY + 0.01, Z0 + 0.006)), GAP, 0.001)          # shadow gap
DRZ0, DRZ1 = 0.415, Z1 - TOPT - 0.003
make("SZ_NightstandDrawer", box((0.424, 0.018, DRZ1 - DRZ0), (NX, NY - 0.365 / 2 + 0.004 - 0.009, (DRZ0 + DRZ1) / 2)), OAK, 0.002)
make("SZ_NightstandDoor", box((0.424, 0.018, DRZ0 - 0.003 - (Z0 + 0.015)), (NX, NY - 0.365 / 2 + 0.004 - 0.009,
                                                                             (DRZ0 - 0.003 + Z0 + 0.015) / 2)), OAK, 0.002)
kb = taper_cyl(0.012, 0.009, 0.022, (0, 0, 0), 32)                                    # turned knob
for v in kb.verts:
    v.co = Vector((v.co.x, v.co.z, v.co.y))
knob = make("SZ_NightstandKnob", kb, OAK, 0.0025, 3, smooth=True)
knob.location = (NX, NY - 0.365 / 2 + 0.004 - 0.018 - 0.011, (DRZ0 + DRZ1) / 2)

# ------------------------------------------------------------------ chair (built in its original frame, then placed)
seat = bpy.data.objects["SZ_ChairSeat"]
# where the seat stands now (place_c00_chair.py may have moved/turned it): its bounding-box centre and its rotation -
# independent of where the object origin sits, so the script can run again
_bb = [seat.matrix_world @ Vector(c) for c in seat.bound_box]
_c = Vector((sum(v.x for v in _bb) / 8, sum(v.y for v in _bb) / 8, 0.46))
M_now = Matrix.Translation(_c) @ seat.matrix_world.to_quaternion().to_matrix().to_4x4()
M_ref = Matrix.Translation((BX + 0.95, -0.15, 0.46))               # frame of build_c00_bedroom.py
M_fix = M_now @ M_ref.inverted()
for n in [o.name for o in sc.objects if o.name.startswith("SZ_Chair")]:
    bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
CX, CY = BX + 0.95, -0.15
parts = []
sb = box((0.43, 0.41, 0.032), (0, 0, 0))                           # seat: origin at its centre (place_c00_chair.py)
for v in sb.verts:                                                 # slightly dished seat
    if v.co.z > 0:
        d = (v.co.x / 0.215) ** 2 + (v.co.y / 0.205) ** 2
        v.co.z -= 0.004 * max(0.0, 1 - d)
seat_o = make("SZ_ChairSeat", sb, OAK, 0.009, 4)
seat_o.matrix_world = Matrix.Translation((CX, CY, 0.46))
parts.append(seat_o)
bm = bmesh.new()                                                   # curved bent-plywood backrest
nu, nv = 24, 8
R, ANG = 0.55, 0.44 / 0.55
rows = []
for j in range(nv + 1):
    z = 0.50 + 0.36 * j / nv
    row = []
    for i in range(nu + 1):
        a = -ANG / 2 + ANG * i / nu
        row.append(bm.verts.new((CX + R * math.sin(a), CY - 0.205 - R * (1 - math.cos(a)) - 0.06 * (j / nv), z)))
    rows.append(row)
for j in range(nv):
    for i in range(nu):
        bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
back = make("SZ_ChairBack", bm, OAK, smooth=True)
sol = back.modifiers.new("Ply", "SOLIDIFY")
sol.thickness, sol.offset = 0.014, 0.0
bv = back.modifiers.new("Bevel", "BEVEL")
bv.width, bv.segments = 0.004, 3
parts.append(back)
for fx in (-0.18, 0.18):
    for fy in (-0.17, 0.17):
        leg = make(f"SZ_ChairLeg{fx}{fy}", taper_cyl(0.016, 0.011, 0.445, (0, 0, 0)), OAK, 0.002, 2, smooth=True)
        tilt = math.radians(3.0)
        leg.matrix_world = Matrix.Translation((CX + fx * 1.03, CY + fy * 1.03, 0.222)) @ \
            Matrix.Rotation(tilt * (1 if fy > 0 else -1), 4, "X") @ Matrix.Rotation(-tilt * (1 if fx > 0 else -1), 4, "Y")
        parts.append(leg)
for fy in (-0.17, 0.17):                                           # side stretchers
    st = make(f"SZ_ChairStretch{fy}", taper_cyl(0.007, 0.007, 0.35, (0, 0, 0), 16), OAK, smooth=True)
    st.matrix_world = Matrix.Translation((CX, CY + fy * 1.06, 0.14)) @ Matrix.Rotation(math.pi / 2, 4, "Y")
    parts.append(st)
for o in parts:
    o.matrix_world = M_fix @ o.matrix_world
result = {"nightstand": ["Top", "Carcass", "Plinth", "Drawer", "Door", "Knob"], "chair_parts": len(parts)}
print("C00_FURNITURE", result)

# ------------------------------------------------------------------ wool rug: UVs for the woven wool in Unreal
# (QA 2026-10-25: the ArchViz checkerboard rug is no longer used; the own rug needs UVs, 1 unit = 1 m)
rug = bpy.data.objects.get("SZ_Rug")
if rug:
    me = rug.data
    uvl = me.uv_layers.get("UVMap") or me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        for li in poly.loop_indices:
            w = rug.matrix_world @ me.vertices[me.loops[li].vertex_index].co
            n = poly.normal
            uvl.data[li].uv = (w.x, w.y) if abs(n.z) > 0.5 else ((w.x + w.y), w.z)
    print("C00_RUG_UV", len(me.polygons))

# ------------------------------------------------------------------ the father/daughter photo above the bed must render
# (QA 2026-10-26: its 7 objects were found render-hidden in the shared .blend - after the clean re-import it was gone)
for o in sc.objects:
    if o.name.startswith(("SZ_WallFrame", "SZ_WallPhoto")) and (o.hide_render or o.hide_viewport):
        o.hide_render = o.hide_viewport = False         # viewport-disabled objects are not evaluated: stale transform
        print("C00_UNHIDE", o.name)
# their frame, mat and glass had also lost their location (all at the room origin, under the floor): back to the
# positions of build_c00_bedroom_decor.py (1.00 x 0.78 oak frame, 4 cm profile, centred over the bed at 1.66 m)
_FW, _FH, _PROF, _DEPTH = 1.00, 0.78, 0.04, 0.035
_wy, _cx, _cz = D / 2 - 0.004, BX, 1.66
_pos = {"SZ_WallFrameTop": (_cx, _wy - _DEPTH / 2, _cz + _FH / 2 - _PROF / 2),
        "SZ_WallFrameBot": (_cx, _wy - _DEPTH / 2, _cz - _FH / 2 + _PROF / 2),
        "SZ_WallFrameL": (_cx - _FW / 2 + _PROF / 2, _wy - _DEPTH / 2, _cz),
        "SZ_WallFrameR": (_cx + _FW / 2 - _PROF / 2, _wy - _DEPTH / 2, _cz),
        "SZ_WallFrameMat": (_cx, _wy - 0.012, _cz), "SZ_WallFrameGlass": (_cx, _wy - 0.022, _cz)}
for n, p in _pos.items():
    o = bpy.data.objects.get(n)
    if o and (o.matrix_world.translation - Vector(p)).length > 0.01:
        o.location = p
        print("C00_REPLACE", n)
