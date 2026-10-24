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
SINK = 0.015                                            # how far the body sinks into the mattress
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
head_back = to_world(POSE["joints"]["head"][0], POSE["joints"]["head"][1] - 10.5, POSE["joints"]["head"][2] + 4)


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


# proxy from the man's real bones (tools/v4_2/c00_pose_lying.py -> C00_POSE_JOINTS.json, component space cm),
# radii = body thickness + ~3 cm margin so no hand, toe or sleeve pierces the duvet
A = POSE["a_pose"]
for dx in (7, -7):                                    # torso as two side-by-side capsules: ~44 cm wide, ~28 cm deep
    capsule(f"SZ_Proxy_Torso{dx}", to_world(dx, A["pelvis"][1], A["pelvis"][2] - 6), to_world(dx, A["spine_05"][1] + 2, A["spine_05"][2] + 6), 0.15)
# the shirt front hangs loose in the outfit's standing rest shape and stands ~20 cm off the back when lying
capsule("SZ_Proxy_ShirtFront", to_world(0, 6, A["pelvis"][2] + 4), to_world(0, 6, A["spine_05"][2] - 4), 0.155)
for s, side in ((1, "l"), (-1, "r")):
    j = JOINTS[side]
    capsule(f"SZ_Proxy_Thigh{s}", to_world(*A[f"thigh_{side}"]), to_world(*A[f"calf_{side}"]), 0.10)
    capsule(f"SZ_Proxy_Calf{s}", to_world(*A[f"calf_{side}"]), to_world(*A[f"foot_{side}"]), 0.08)
    # feet in the relaxed plantar flexion of A_C00_Mann_Liegen: heel behind the ankle, toes past the posed ball
    ank, ball = Vector(A[f"foot_{side}"]), Vector(j["ball"])
    toe = ball + (ball - ank).normalized() * 8
    capsule(f"SZ_Proxy_Foot{s}", to_world(ank.x, ank.y - 6, ank.z), to_world(*toe), 0.075)
    # arms lowered by A_C00_Mann_Liegen; fingers continue the forearm by ~19 cm
    e, h = Vector(j["elbow"]), Vector(j["hand"])
    tip = h + (h - e).normalized() * 19
    capsule(f"SZ_Proxy_UpperArm{s}", to_world(*j["shoulder"]), to_world(*j["elbow"]), 0.08)
    capsule(f"SZ_Proxy_ForeArm{s}", to_world(*j["elbow"]), to_world(*j["hand"]), 0.07)
    capsule(f"SZ_Proxy_Hand{s}", to_world(*j["hand"]), to_world(*tip), 0.065)
    # the outfit sleeves stay in A-pose in the editor preview: shoulder to just past the A-pose elbow
    ua, la = Vector(A[f"upperarm_{side}"]), Vector(A[f"lowerarm_{side}"])
    capsule(f"SZ_Proxy_Sleeve{s}", to_world(*ua), to_world(*(la + (Vector(A[f"hand_{side}"]) - la) * 0.55)), 0.12)
for o in proxy_parts:
    o.modifiers.new("Collision", "COLLISION")
    o.collision.thickness_outer = 0.006
    o.collision.cloth_friction = 6

# ------------------------------------------------------------------ duvet again, edge at the chest
for n in ("SZ_DuvetCloth",):
    o = bpy.data.objects.get(n)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
chest_y = to_world(0, 0, 139).y                       # duvet edge at the collarbones
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
TOP, THICK = MATTRESS_TOP, 0.03
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
bm = bmesh.new()
bv = [[bm.verts.new(grid[j][i]) for i in range(nx + 1)] for j in range(ny + 1)]
for j in range(ny):
    for i in range(nx):
        bm.faces.new((bv[j][i], bv[j][i + 1], bv[j + 1][i + 1], bv[j + 1][i]))
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
pin.add([v.index for v in duv.data.vertices if v.co.y > top_y - 0.05 and abs(v.co.x - MAN_X) < 0.35], 1.0, "REPLACE")
cl = duv.modifiers.new("Cloth", "CLOTH")
st = cl.settings
st.vertex_group_mass = "Pin"
st.quality, st.mass, st.air_damping = 10, 1.2, 4.0          # heavy down duvet
st.tension_stiffness = st.compression_stiffness = 8.0
st.shear_stiffness, st.bending_stiffness = 3.0, 0.08        # low bending: soft folds
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
so = duv.modifiers.new("Puff", "SOLIDIFY")
so.thickness, so.offset, so.use_even_offset = 0.035, -1.0, False   # even offset shot spikes out of sharp folds
so.thickness_clamp, so.use_quality_normals = 1.0, True
sm = duv.modifiers.new("Smooth", "SUBSURF")
sm.levels = sm.render_levels = 1
folds = bpy.data.textures.get("TX_SZ_Folds") or bpy.data.textures.new("TX_SZ_Folds", "CLOUDS")
folds.noise_scale, folds.noise_depth = 0.12, 2
dp = duv.modifiers.new("Folds", "DISPLACE")
dp.texture, dp.strength, dp.texture_coords = folds, 0.008, "GLOBAL"
dp2 = duv.modifiers.new("Creases", "DISPLACE")
dp2.texture, dp2.strength, dp2.texture_coords = bpy.data.textures["TX_SZ_Crease"], 0.006, "GLOBAL"
sc.frame_set(1)
for o in proxy_parts:
    bpy.data.objects.remove(o, do_unlink=True)

result = {"P0": [round(v, 3) for v in P0], "head": [round(v, 3) for v in to_world(*POSE["joints"]["head"])], "chest_y": round(chest_y, 3)}
