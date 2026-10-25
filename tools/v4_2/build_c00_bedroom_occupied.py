"""C00 (runs INSIDE Blender 5.2 after build_c00_bedroom.py + build_c00_bedroom_detail.py): the man in bed.

The duvet is simulated again over a body proxy in exactly the lying transform the Unreal scene uses for
MHC_C00_Mann (tools/v4_2/c00_scene_bedroom.py reads LYING from the JSON written here):
- character space (MetaHuman, cm): feet at the origin, Z up, face +Y, A-pose arms
- lying: local Z -> +Y (head to the headboard), local Y (face) -> up, then raised 4 deg at the head end
  (head of the bed slightly up, as for a very ill person), feet at the foot end of the mattress
Proxy = torso, legs, lowered arms (pose A_C00_Mann_Liegen) and the A-pose sleeves as capsules.
The duvet edge lies at the collarbones (head, neck and V-neck stay visible); afterwards the proxy is removed and the room is exported for Unreal.
"""
import bmesh
import bpy
import json
import math
import os
from mathutils import Matrix, Vector

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_JSON = os.path.join(ROOT, "docs", "v4_2", "C00_BEDROOM_LYING.json")
with open(os.path.join(ROOT, "docs", "v4_2", "C00_POSE_JOINTS.json"), encoding="utf8") as f:
    POSE = json.load(f)                             # from tools/v4_2/c00_pose_lying.py (Unreal)
JOINTS = POSE["joints"]
sc = bpy.data.scenes["C00_Schlafzimmer"]
col = bpy.data.collections["C00_Schlafzimmer"]
D = 3.20
BX, BY0 = -0.25, D / 2 - 0.03
MATTRESS_TOP = 0.53
THETA = 0.0                                             # Regie 2026-10-25: lies flat, anatomically on the mattress
FEET_Y = BY0 - 0.10 - 2.0 + 0.20                       # 20 cm from the foot end: relaxed toes stay under the duvet

# local character (m) -> Blender world
R0 = Matrix(((-1, 0, 0), (0, 0, 1), (0, 1, 0)))      # columns: images of local X, Y, Z
RT = Matrix.Rotation(THETA, 3, "X")                   # raise the head end (+Y) by THETA
R = RT @ R0
MAN_X = BX + 0.33                                     # on the window-side pillow, not on the seam
BACK = 0.12                                             # back of the torso / buttocks behind the root plane (local -Y)
SINK = 0.045                                            # how far the body sinks into the soft mattress (Regie: no floating)
P0 = Vector((MAN_X, FEET_Y, MATTRESS_TOP - SINK + BACK))


def to_world(lx, ly, lz):
    return P0 + R @ Vector((lx / 100, ly / 100, lz / 100))


with open(OUT_JSON, "w", encoding="utf8") as f:
    json.dump({"note": "Blender metres; Unreal = (100x, -100y, 100z)", "P0": list(P0),
               "local_x": list(R.col[0]), "local_y": list(R.col[1]), "local_z": list(R.col[2]),
               "theta_deg": 0.0, "head_world": list(to_world(*POSE["joints"]["head"]))}, f, indent=1)


def recolor(mat, rgb):
    """The fabric materials mix two tones of one base colour: set both tones."""
    for n in mat.node_tree.nodes:
        if n.type == "MIX" and getattr(n, "data_type", "") == "RGBA":
            cols = [i for i in n.inputs if i.type == "RGBA" and not i.is_linked]
            for k, i in enumerate(cols):
                f = 0.94 if k == 0 else 1.0
                i.default_value = (rgb[0] * f, rgb[1] * f, rgb[2] * f, 1)


# ------------------------------------------------------------------ soft pillows (Regie: "viel zu steif")
# 80 x 40 cm down pillows: thick, rounded middle that runs out into a thin piped seam, uneven filling;
# the man's pillow carries the dent of his head (the back of the head rests ~6 cm above the mattress).
LINEN = bpy.data.materials.get("M_SZ_PillowLinen")
if LINEN is None:
    LINEN = bpy.data.materials["M_SZ_BedLinenWhite"].copy()
    LINEN.name = "M_SZ_PillowLinen"
    recolor(LINEN, (0.74, 0.70, 0.63))                                  # warm natural linen
for n in ("SZ_Pillow-0.36", "SZ_Pillow0.36"):
    o = bpy.data.objects.get(n)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
head_back = to_world(POSE["joints"]["head"][0], POSE["joints"]["head"][1] - 9.0, POSE["joints"]["head"][2] + 4)   # Regie: head rests in the pillow, not above it


def pillow(name, cx, cy, dent=None, seed=0):
    import random
    rnd = random.Random(seed)
    W2, D2, H2 = 0.40, 0.20, 0.075                       # half sizes: 80 x 40 cm, up to 15 cm thick
    lumps = [(rnd.uniform(-W2, W2), rnd.uniform(-D2, D2), rnd.uniform(0.08, 0.16), rnd.uniform(-0.012, 0.012)) for _ in range(7)]
    bm = bmesh.new()
    nu, nv = 48, 26
    rows = {}
    for side in (1, -1):                                  # top and bottom shell, joined at the seam
        for j in range(nv + 1):
            for i in range(nu + 1):
                u, v = -1 + 2 * i / nu, -1 + 2 * j / nv
                fill = max(0.0, (1 - abs(u) ** 2.6)) ** 0.55 * max(0.0, (1 - abs(v) ** 2.2)) ** 0.55
                x, y = cx + u * W2, cy + v * D2
                h = H2 * fill
                for lx, ly, lr, la in lumps:               # uneven down filling
                    h += la * fill * math.exp(-((x - cx - lx) ** 2 + (y - cy - ly) ** 2) / (lr * lr))
                if side > 0:
                    z = MATTRESS_TOP + 0.012 + h
                    if dent:                                # head dent: smooth bowl, filling pushed to the sides
                        d2 = ((x - dent.x) / 0.13) ** 2 + ((y - dent.y) / 0.11) ** 2
                        floor = dent.z
                        push = math.exp(-d2)
                        z = z * (1 - push) + min(z, floor) * push + 0.02 * math.exp(-(math.sqrt(d2) - 1.3) ** 2 / 0.15) * fill
                else:
                    z = MATTRESS_TOP + 0.012 - min(h, 0.012)  # flat underside resting on the sheet
                rows[(side, j, i)] = bm.verts.new((x, y, z))
    for side in (1, -1):
        for j in range(nv):
            for i in range(nu):
                q = (rows[(side, j, i)], rows[(side, j, i + 1)], rows[(side, j + 1, i + 1)], rows[(side, j + 1, i)])
                bm.faces.new(q if side > 0 else q[::-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    me.materials.append(LINEN)
    sub = o.modifiers.new("Soft", "SUBSURF")
    sub.levels = sub.render_levels = 1
    d = o.modifiers.new("Wrinkle", "DISPLACE")
    d.texture, d.strength, d.texture_coords = bpy.data.textures["TX_SZ_Crease"], 0.004, "GLOBAL"
    return o


pillow("SZ_Pillow0.36", MAN_X + 0.02, BY0 - 0.30, dent=head_back, seed=3)
pillow("SZ_Pillow-0.36", BX - 0.36, BY0 - 0.30, seed=8)

# ------------------------------------------------------------------ body proxy (capsules from MetaHuman landmarks)
proxy_parts = []


def capsule(name, a, b, r):
    a, b = Vector(a), Vector(b)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=1.0)
    axis = b - a
    length = axis.length
    rot = axis.normalized().to_track_quat("Z", "Y").to_matrix()
    for v in bm.verts:
        z = v.co.z
        p = Vector((v.co.x * r, v.co.y * r, z * r + (length if z > 0 else 0)))
        v.co = a + rot @ p
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    proxy_parts.append(o)
    return o


# proxy from the man's real bones (tools/v4_2/c00_pose_lying.py -> C00_POSE_JOINTS.json, component space cm).
# Regie 2026-10-25 ("Deckenhuegel flacher"): anatomical sizes of a very thin old man + ~1.5 cm margin. Radii checked against a
# render without the duvet (hips/shorts and hands were the widest parts).
A = POSE["a_pose"]
BACK_Y = -BACK * 100                                   # back of the torso in local cm (lies on the mattress)
POSED = bpy.data.collections.get("C00_SZ_Collision")
if POSED and len(POSED.objects):
    # Regie 2026-10-25 ("Teile vom Hemd schauen durch die Decke", "Decke muss sich anatomisch anpassen"): the real
    # posed body + shirt (tools/v4_2/build_c00_posed_man.py, Blender armature space = S c / 100) instead of capsules.
    # Arms/hands are not in it - they rest on the duvet. Into the bed: world = P0 + R @ S @ v.
    _S = Matrix(((1, 0, 0), (0, -1, 0), (0, 0, 1)))
    _M = Matrix.Translation(P0) @ (R @ _S).to_4x4()
    for src in POSED.objects:
        me = src.data.copy()
        me.transform(_M)
        me.flip_normals()                                # R @ S mirrors - keep the normals pointing outward
        o = bpy.data.objects.new("SZ_Proxy_" + src.name, me)
        col.objects.link(o)
        proxy_parts.append(o)
    # the thin toes of the left foot pierced the duvet (Regie 2026-10-25): a margin capsule from heel to toe tip
    _jl = JOINTS["l"]
    _ank, _ball = Vector(A["foot_l"]), Vector(_jl["ball"])
    _toe = _ball + (_ball - _ank).normalized() * 8
    capsule("SZ_Proxy_FootMargin_l", to_world(_ank.x, _ank.y - 5, _ank.z), to_world(*_toe), 0.075)
else:
    for dx in (6.5, -6.5):                                # torso: two capsules side by side, ~36 cm wide, ~23 cm deep
        capsule(f"SZ_Proxy_Torso{dx}", to_world(dx, BACK_Y + 13, A["pelvis"][2] - 12), to_world(dx, BACK_Y + 13, A["spine_05"][2] + 6), 0.127)
    # the own skinned shirt (SKM_C00_Mann_Shirt) follows the pose, but its loose front still stands ~19 cm off the back
    capsule("SZ_Proxy_ShirtFront", to_world(0, 15.5 - 12, A["pelvis"][2] + 6), to_world(0, 15.5 - 12, A["spine_05"][2] - 10), 0.12)   # front at local y 15.5 (shirt laid onto the body)
    # pelvis front: the base body's shorts stand ~2 cm proud of the torso capsules
    capsule("SZ_Proxy_Pelvis", to_world(-7, BACK_Y + 15, A["pelvis"][2] - 9), to_world(7, BACK_Y + 15, A["pelvis"][2] - 9), 0.11)
    for s, side in ((1, "l"), (-1, "r")):
        j = JOINTS[side]
        th, ca = Vector(A[f"thigh_{side}"]), Vector(A[f"calf_{side}"])
        capsule(f"SZ_Proxy_Hip{s}", to_world(*th), to_world(*(th + (ca - th) * 0.45)), 0.10)      # hip, upper thigh, shorts
        capsule(f"SZ_Proxy_Thigh{s}", to_world(*th), to_world(*ca), 0.082)
        capsule(f"SZ_Proxy_Calf{s}", to_world(*A[f"calf_{side}"]), to_world(*A[f"foot_{side}"]), 0.065)
        # feet in the relaxed plantar flexion of A_C00_Mann_Liegen: heel behind the ankle, toes past the posed ball
        ank, ball = Vector(j.get("foot_out", A[f"foot_{side}"])), Vector(j.get("ball_out", j["ball"]))   # right leg turned out
        toe = ball + (ball - ank).normalized() * 7
        capsule(f"SZ_Proxy_Foot{s}", to_world(ank.x, ank.y - 6, ank.z), to_world(*toe), 0.062)
        # Regie 2026-10-25: the arms lie ON the duvet (hands resting on it) - no arm proxies; the pose is fitted to the
        # simulated duvet afterwards (height map below -> tools/v4_2/c00_pose_lying.py)
for o in proxy_parts:
    o.modifiers.new("Collision", "COLLISION")
    o.collision.thickness_outer = 0.006
    o.collision.cloth_friction = 6

# ------------------------------------------------------------------ duvet again, edge at the chest
for n in ("SZ_DuvetCloth",):
    o = bpy.data.objects.get(n)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
chest_y = to_world(0, 0, 128).y                       # Regie 2026-10-25: duvet to the chest, shoulders out
# Draped procedurally (cloth simulation over the narrow proxy exploded): every grid point is dropped onto
# body proxy + mattress + pillows, the parts beyond the mattress edges hang down, then a constrained
# smoothing lets the duvet tent between the body and the mattress like a real filled duvet.
from mathutils.bvhtree import BVHTree
deps = bpy.context.evaluated_depsgraph_get()
verts, polys = [], []
for o in proxy_parts + [bpy.data.objects[n] for n in ("SZ_Mattress", "SZ_Pillow-0.36", "SZ_Pillow0.36")]:
    ev = o.evaluated_get(deps)
    m = ev.to_mesh()
    base = len(verts)
    verts += [o.matrix_world @ v.co for v in m.vertices]
    polys += [tuple(base + i for i in p.vertices) for p in m.polygons]
    ev.to_mesh_clear()
bvh = BVHTree.FromPolygons(verts, polys)
HALF_W, FOOT = 0.70, BY0 - 0.10 - 2.0                  # mattress half width, foot end
TOP, THICK = MATTRESS_TOP, 0.045                       # down duvet ~4.5 cm thick
X0, X1, Y0, Y1, STEP = BX - 0.80, BX + 0.80, FOOT - 0.16, chest_y, 0.02
nx, ny = int(round((X1 - X0) / STEP)), int(round((Y1 - Y0) / STEP))


def surface(x, y):
    hit = bvh.ray_cast(Vector((x, y, 2.0)), Vector((0, 0, -1)), 3.0)[0]
    return hit.z if hit else TOP


grid = [[None] * (nx + 1) for _ in range(ny + 1)]
floor_z = [[0.0] * (nx + 1) for _ in range(ny + 1)]
for j in range(ny + 1):
    for i in range(nx + 1):
        x, y = X0 + i * STEP, Y0 + j * STEP
        dx = abs(x - BX) - HALF_W
        dy = FOOT - y
        if dx > 0 or dy > 0:                                 # beyond an edge: hangs down along the bed side
            over = max(dx, 0.0) + max(dy, 0.0)
            px = BX + math.copysign(min(abs(x - BX), HALF_W + 0.03), x - BX)
            py = max(y, FOOT - 0.03)
            z = TOP + THICK - over * 0.95
            grid[j][i] = Vector((px, py, z))
            floor_z[j][i] = -10.0
        else:
            z = surface(x, y) + THICK
            grid[j][i] = Vector((x, y, z))
            floor_z[j][i] = z
for _ in range(60):                                       # constrained smoothing: tent, never sink into the body
    nxt = [[v.copy() for v in row] for row in grid]
    for j in range(ny + 1):
        for i in range(nx + 1):
            if floor_z[j][i] < -1:
                continue
            nb = [grid[jj][ii].z for jj, ii in ((j - 1, i), (j + 1, i), (j, i - 1), (j, i + 1))
                  if 0 <= jj <= ny and 0 <= ii <= nx and floor_z[jj][ii] > -1]      # edge rows too (one-sided)
            if nb:
                nxt[j][i].z = max(floor_z[j][i], grid[j][i].z * 0.5 + sum(nb) / len(nb) * 0.5)
    grid = nxt
# Regie 2026-10-25: the right foot looks out - the duvet corner over it is pushed back diagonally
_fr = to_world(*JOINTS["r"].get("foot_out", A["foot_r"]))
# fold line: a diagonal across the foot-end corner on the window side, from the foot end of the duvet (FA) to the
# bed side (FB); the triangle beyond it (containing the right foot) is turned back onto the duvet
FA = Vector((MAN_X - 0.10, FOOT - 0.02))                   # turned-back triangle: the whole right foot is free,
FB = Vector((BX + 0.72, FOOT + 0.55))                      # the ankle sits at the fold


def corner_open(x, y):
    ab, ap = FB - FA, Vector((x, y)) - FA
    return ab.x * ap.y - ab.y * ap.x < 0


# Regie 2026-10-25 ("umgeschlagen, nicht ein fehlendes Stueck"): the small corner triangle over the right foot is
# turned back over the fold line FA-FB and laid on the duvet (base surface + one duvet thickness), with a rounded
# crease. It is pinned in the simulation (no self collision needed - that crumpled the whole duvet).
_ab = (FB - FA).normalized()
_nn = Vector((_ab.y, -_ab.x))
_base = [[grid[j][i].copy() for i in range(nx + 1)] for j in range(ny + 1)]


def base_z(x, y):
    fi, fj = (x - X0) / STEP, (y - Y0) / STEP
    i, j = max(0, min(nx - 1, int(fi))), max(0, min(ny - 1, int(fj)))
    tx, ty = min(1, max(0, fi - i)), min(1, max(0, fj - j))
    z0 = _base[j][i].z * (1 - tx) + _base[j][i + 1].z * tx
    z1 = _base[j + 1][i].z * (1 - tx) + _base[j + 1][i + 1].z * tx
    return z0 * (1 - ty) + z1 * ty


flap_ij = set()
for j in range(ny + 1):
    for i in range(nx + 1):
        x, y = X0 + i * STEP, Y0 + j * STEP                  # grid (unhung) position decides the side of the fold
        if not corner_open(x, y):
            continue
        d = (Vector((x, y)) - FA).dot(_nn)
        r = Vector((x, y)) - _nn * (2 * d)
        crease = 0.022 * math.exp(-(d / 0.03) ** 2)
        grid[j][i] = Vector((r.x, r.y, base_z(r.x, r.y) + THICK + 0.004 + crease))
        flap_ij.add((j, i))
bm = bmesh.new()
bv = [[bm.verts.new(grid[j][i]) for i in range(nx + 1)] for j in range(ny + 1)]
FLAP = [j * (nx + 1) + i for (j, i) in flap_ij]            # vertex index = creation order
for j in range(ny):
    for i in range(nx):
        f = bm.faces.new((bv[j][i], bv[j][i + 1], bv[j + 1][i + 1], bv[j + 1][i]))
uv_layer = bm.loops.layers.uv.new("UVMap")                 # duvet cover UVs (1 unit = 1 m): quilting channels in Unreal
for f in bm.faces:
    for loop in f.loops:
        loop[uv_layer].uv = ((loop.vert.co.x - X0), (loop.vert.co.y - Y0))
me = bpy.data.meshes.new("SZ_DuvetCloth")
bm.to_mesh(me)
bm.free()
for p in me.polygons:
    p.use_smooth = True
duv = bpy.data.objects.new("SZ_DuvetCloth", me)
col.objects.link(duv)
SAGE = bpy.data.materials.get("M_SZ_DuvetSage")
if SAGE is None:                                          # Regie: friendlier, more modern - washed sage-green linen
    SAGE = bpy.data.materials["M_SZ_BedLinenWhite"].copy()
    SAGE.name = "M_SZ_DuvetSage"
    recolor(SAGE, (0.30, 0.38, 0.29))
duv.data.materials.append(SAGE)

# Regie 2026-10-25: "realistisch an den Koerper ... realistische Falten, nicht wie gegossen". The drape above
# is only the starting shape: the duvet gets 7 % extra width (real duvets are wider than the body they cover),
# is lifted 2 cm and then settles in a real cloth simulation on body proxy, pillows and mattress. Starting
# close to rest keeps the solver stable (the free fall from 1 m exploded on the narrow proxy).
for o in proxy_parts + [bpy.data.objects[n] for n in ("SZ_Mattress", "SZ_BedBase", "SZ_Pillow0.36", "SZ_Pillow-0.36")]:
    if not any(m.type == "COLLISION" for m in o.modifiers):
        o.modifiers.new("Collision", "COLLISION")
    o.collision.thickness_outer = 0.006
    o.collision.cloth_friction = 10
for v in duv.data.vertices:
    v.co.x = BX + (v.co.x - BX) * 1.07
    v.co.z += 0.02
# the top edge (folded over at the collarbones) is held in place, otherwise the duvet slides over the head
pin = duv.vertex_groups.new(name="Pin")
top_y = max(v.co.y for v in duv.data.vertices)
pin.add([v.index for v in duv.data.vertices if v.co.y > top_y - 0.04 and abs(v.co.x - MAN_X) < 0.30], 1.0, "REPLACE")
pin.add(FLAP, 1.0, "REPLACE")                              # the turned-back flap stays where it was laid
cl = duv.modifiers.new("Cloth", "CLOTH")
st = cl.settings
st.vertex_group_mass = "Pin"
st.quality, st.mass, st.air_damping = 10, 1.2, 4.0          # heavy down duvet
st.tension_stiffness = st.compression_stiffness = 8.0
st.shear_stiffness, st.bending_stiffness = 3.0, 0.35        # a little stiffer: bridges between the legs (stiff+self collision crumpled)
st.use_internal_springs = False
cl.collision_settings.use_self_collision = False
cl.collision_settings.collision_quality = 5
cl.collision_settings.distance_min = 0.006
cl.point_cache.frame_start, cl.point_cache.frame_end = 1, 70
sc.frame_start, sc.frame_end = 1, 70
sc.frame_set(1)
for f in range(1, 71):
    sc.frame_set(f)
with bpy.context.temp_override(object=duv, active_object=duv, selected_objects=[duv], scene=sc):
    bpy.ops.object.modifier_apply(modifier="Cloth")
sc.frame_set(1)
# Regie 2026-10-25 ("an der Huefte merkwuerdig verknotet"): the solver pinches the cloth into tight knots where it
# meets the shorts' waistband. A relaxed duvet does not form knots: smooth the result (keeps the large folds),
# then push it back outside the body so smoothing never sinks it in.
sm0 = duv.modifiers.new("Relax", "SMOOTH")
sm0.factor, sm0.iterations = 0.8, 25
with bpy.context.temp_override(object=duv, active_object=duv, selected_objects=[duv], scene=sc):
    bpy.ops.object.modifier_apply(modifier="Relax")
for v in duv.data.vertices:
    loc, nrm, _, dist = bvh.find_nearest(v.co)
    if loc is not None and ((v.co - loc).dot(nrm) < 0 or dist < THICK * 0.6):
        v.co = loc + nrm * THICK * 0.6
duv.data.update()
so = duv.modifiers.new("Puff", "SOLIDIFY")
so.thickness, so.offset, so.use_even_offset = 0.045, -1.0, False   # even offset shot spikes out of sharp folds
so.thickness_clamp, so.use_quality_normals = 1.0, True
sm = duv.modifiers.new("Smooth", "SUBSURF")
sm.levels = sm.render_levels = 1
folds = bpy.data.textures.get("TX_SZ_Folds") or bpy.data.textures.new("TX_SZ_Folds", "CLOUDS")
folds.noise_scale, folds.noise_depth = 0.12, 2
dp = duv.modifiers.new("Folds", "DISPLACE")
dp.texture, dp.strength, dp.texture_coords = folds, 0.004, "GLOBAL"
# no cellular crease texture on the duvet: its ridges read as knots (Regie 2026-10-25) - the simulation's folds stay
sc.frame_set(1)
for o in proxy_parts:
    bpy.data.objects.remove(o, do_unlink=True)

# ------------------------------------------------------------------ duvet height map for the arm pose
# local character space (cm): x left/right, z along the body; value = local y of the duvet top (up when lying)
from mathutils.bvhtree import BVHTree as _BVH
_ev = duv.evaluated_get(bpy.context.evaluated_depsgraph_get())
_m = _ev.to_mesh()
_bvh = _BVH.FromPolygons([duv.matrix_world @ v.co for v in _m.vertices], [tuple(p.vertices) for p in _m.polygons])
_ev.to_mesh_clear()
hmap = {"x0": -44, "z0": 70, "step": 2, "nx": 45, "nz": 41, "y": []}
for k in range(hmap["nz"]):
    row = []
    for i in range(hmap["nx"]):
        wpt = to_world(hmap["x0"] + i * hmap["step"], 60, hmap["z0"] + k * hmap["step"])
        hit = _bvh.ray_cast(wpt, Vector((0, 0, -1)), 2.0)[0]
        row.append(round((hit.z - P0.z) * 100, 2) if hit else None)
    hmap["y"].append(row)
with open(OUT_JSON, encoding="utf8") as f:
    lying_json = json.load(f)
lying_json["duvet_height_local"] = hmap
with open(OUT_JSON, "w", encoding="utf8") as f:
    json.dump(lying_json, f, indent=1)

result = {"P0": [round(v, 3) for v in P0], "head": [round(v, 3) for v in to_world(*POSE["joints"]["head"])], "chest_y": round(chest_y, 3)}
