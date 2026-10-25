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
# Regie 2026-10-25: "der Kopf ist zu dicht am Kopfende" - 10 cm lower in the bed than before (head now mid-pillow)
FEET_Y = BY0 - 0.10 - 2.0 + 0.10                       # 10 cm from the foot end: relaxed toes stay under the duvet

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
# Regie 2026-10-25 ("der Kopf schwebt ueber dem Kissen"): the back of the skull from the real head pose - the head is
# flexed ~20 deg (chin to the chest, c00_pose_lying.py; measured in Unreal: nose 20 deg toward the feet), which lifts
# the occiput off a dent made for an unflexed head. Back of skull = head joint - 9 cm along the face axis + 4 cm along
# the crown axis (local cm, y = face, z = crown); the pillow is filled up to it, minus 5 mm of sinking in.
_hf = math.radians(20.0)
_hj = POSE["joints"]["head"]
head_back = to_world(_hj[0], _hj[1] - 9.0 * math.cos(_hf) + 4.0 * math.sin(_hf), _hj[2] + 9.0 * math.sin(_hf) + 4.0 * math.cos(_hf))
head_back.z -= 0.005


def pillow(name, cx, cy, dent=None, seed=0):
    import random
    rnd = random.Random(seed)
    W2, D2, H2 = 0.40, 0.20, 0.10                        # half sizes: 80 x 40 cm, up to 20 cm thick (Regie: "Kissen dicker")
    lumps = [(rnd.uniform(-W2, W2), rnd.uniform(-D2, D2), rnd.uniform(0.08, 0.16), rnd.uniform(-0.012, 0.012)) for _ in range(7)]
    bm = bmesh.new()
    nu, nv = 48, 26
    rows = {}
    for side in (1, -1):                                  # top and bottom shell, joined at the seam
        for j in range(nv + 1):
            for i in range(nu + 1):
                u, v = -1 + 2 * i / nu, -1 + 2 * j / nv
                # Regie 2026-10-25 (close-up): the steep 0.55 profile read as a flat mat with a vertical edge - a
                # filled down pillow rolls out round from the middle to the piped seam
                fill = max(0.0, (1 - abs(u) ** 2.2)) ** 0.8 * max(0.0, (1 - abs(v) ** 2.0)) ** 0.85
                x, y = cx + u * W2, cy + v * D2
                h = H2 * fill
                for lx, ly, lr, la in lumps:               # uneven down filling
                    h += la * fill * math.exp(-((x - cx - lx) ** 2 + (y - cy - ly) ** 2) / (lr * lr))
                if side > 0:
                    z = MATTRESS_TOP + 0.012 + h
                    if dent:                                # head dent: smooth bowl, filling pushed to the sides
                        d2 = ((x - dent.x) / 0.17) ** 2 + ((y - dent.y) / 0.14) ** 2   # wide soft hollow, no crater rim
                        floor = dent.z
                        push = math.exp(-d2 * 1.4)
                        z = z * (1 - push) + min(z, floor) * push + 0.012 * math.exp(-(math.sqrt(d2) - 1.4) ** 2 / 0.3) * fill
                else:
                    z = MATTRESS_TOP + 0.012 - min(h, 0.012)  # flat underside resting on the sheet
                rows[(side, j, i)] = bm.verts.new((x, y, z))
    for side in (1, -1):
        for j in range(nv):
            for i in range(nu):
                q = (rows[(side, j, i)], rows[(side, j, i + 1)], rows[(side, j + 1, i + 1)], rows[(side, j + 1, i)])
                bm.faces.new(q if side > 0 else q[::-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    uvl = bm.loops.layers.uv.new("UVMap")              # 1 UV unit = 1 m: woven linen in Unreal (M_C00_SetFabric)
    for f in bm.faces:
        for loop in f.loops:
            loop[uvl].uv = (loop.vert.co.x - cx + W2, loop.vert.co.y - cy + D2)
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
# Regie 2026-10-25 (close-up "Decke und Hemd"): the cloth solver pinched the duvet into a funnel at the hip and the
# relax pass ironed every fold flat - a heavy down duvet does neither. It bridges the body like a tent and, by its
# weight, settles onto the mattress a hand's width beside it: constrained smoothing with a small gravity term per pass
# (never below body/mattress + duvet thickness), so concave spots (waist, between the legs) are spanned, not followed.
# the posed body has holes where the arms were cut away (shoulders, armpits): rays fall through to the mattress and the
# duvet sank into pits - a morphological closing (max then min, 7 x 7 cells = 14 cm) fills holes narrower than that
def _win(field, fn, r):
    out = [row[:] for row in field]
    for j in range(ny + 1):
        for i in range(nx + 1):
            if field[j][i] < -1:
                continue
            vals = [field[jj][ii] for jj in range(max(0, j - r), min(ny, j + r) + 1)
                    for ii in range(max(0, i - r), min(nx, i + r) + 1) if field[jj][ii] > -1]
            out[j][i] = fn(vals)
    return out


_closed = _win(_win(floor_z, max, 3), min, 3)
for j in range(ny + 1):
    for i in range(nx + 1):
        if floor_z[j][i] > -1:
            floor_z[j][i] = max(floor_z[j][i], _closed[j][i])
            grid[j][i].z = max(grid[j][i].z, floor_z[j][i])
SAG = 0.0011
for _ in range(160):
    nxt = [[v.copy() for v in row] for row in grid]
    for j in range(ny + 1):
        for i in range(nx + 1):
            if floor_z[j][i] < -1:
                continue
            nb = [grid[jj][ii].z for jj, ii in ((j - 1, i), (j + 1, i), (j, i - 1), (j, i + 1))
                  if 0 <= jj <= ny and 0 <= ii <= nx and floor_z[jj][ii] > -1]      # edge rows too (one-sided)
            if nb:
                nxt[j][i].z = max(floor_z[j][i], grid[j][i].z * 0.5 + sum(nb) / len(nb) * 0.5 - SAG)
    grid = nxt
# folds of a real duvet (three scales; the finest comes from the woven normal map in Unreal):
# - drape folds on the slopes from the body down to the mattress: crests run downhill, ~18-24 cm apart,
#   irregular in spacing and strength (low-frequency phase/amplitude noise, no visible pattern)
# - hanging folds where the duvet falls over the bed side and the foot end
# - faint compression folds over the top of the body
import random as _rnd
_r = _rnd.Random(11)
_waves = [(_r.uniform(0, math.pi), _r.uniform(3.0, 7.0), _r.uniform(0, 2 * math.pi)) for _ in range(5)]


def lowfreq(x, y):
    return sum(math.sin(k * (x * math.cos(a) + y * math.sin(a)) + ph) for a, k, ph in _waves) / len(_waves) * 1.6


def smoothstep(e0, e1, v):
    t = min(1.0, max(0.0, (v - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


TAU = 2 * math.pi
_z = [[grid[j][i].z for i in range(nx + 1)] for j in range(ny + 1)]
for j in range(ny + 1):
    for i in range(nx + 1):
        p = grid[j][i]
        if floor_z[j][i] < -1:                               # hanging part: folds bulge outward from the bed
            amp = 0.016 * (0.6 + 0.4 * lowfreq(p.y * 1.3, p.x))
            if abs(p.x - BX) > HALF_W:                       # long sides
                f = 0.5 + 0.5 * math.sin(TAU * p.y / 0.23 + 1.4 * lowfreq(p.x, p.y))
                p.x += math.copysign(amp * f, p.x - BX)
            else:                                            # foot end
                f = 0.5 + 0.5 * math.sin(TAU * p.x / 0.21 + 1.4 * lowfreq(p.y, p.x))
                p.y -= amp * f
            continue
        jj0, jj1, ii0, ii1 = max(0, j - 1), min(ny, j + 1), max(0, i - 1), min(nx, i + 1)
        gx = (_z[j][ii1] - _z[j][ii0]) / max(STEP, (ii1 - ii0) * STEP)
        gy = (_z[jj1][i] - _z[jj0][i]) / max(STEP, (jj1 - jj0) * STEP)
        mag = math.hypot(gx, gy)
        mask = smoothstep(0.10, 0.75, mag)
        wx = gx * gx / (mag * mag + 1e-9)                    # slope toward the bed side vs. toward the foot end
        side = math.sin(TAU * p.y / 0.20 + 1.5 * lowfreq(p.x, p.y))
        foot = math.sin(TAU * p.x / 0.22 + 1.5 * lowfreq(p.y, p.x))
        amp = 0.018 * (0.55 + 0.45 * lowfreq(p.x * 1.7, p.y * 1.3))
        dz = amp * mask * (wx * side + (1 - wx) * foot)
        dz += 0.004 * (1 - mask) * math.sin(TAU * (p.x * 0.6 + p.y * 0.8) / 0.30 + 1.5 * lowfreq(p.y, p.x))
        p.z = max(floor_z[j][i], p.z + dz)
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

# Regie 2026-10-25: "realistisch an den Koerper ... realistische Falten, nicht wie gegossen". Folds come from the drape
# above (no cloth solver any more - it pinched a funnel at the hip). Safety pass: nothing of the duvet top may come
# closer to body, pillows or mattress than 60 % of its thickness (the Solidify grows downward).
# (straight down from above: nearest-point normals flip inward at the open arm cuts of the posed body and dug pits)
for v in duv.data.vertices:
    if abs(v.co.x - BX) <= HALF_W and v.co.y >= FOOT:
        v.co.z = max(v.co.z, surface(v.co.x, v.co.y) + THICK * 0.6)
duv.data.update()
# Regie 2026-10-25 ("harte Kante an der Brust"): a duvet is sewn flat at its seams - the filling thickness runs
# from 0 at every border to full ~12 cm inside (vertex group drives the Solidify thickness)
import bmesh as _bm2
_b = _bm2.new()
_b.from_mesh(duv.data)
_edge = [v.co.copy() for v in _b.verts if v.is_boundary]
_b.free()
from mathutils.kdtree import KDTree
_kd = KDTree(len(_edge))
for k, c in enumerate(_edge):
    _kd.insert(c, k)
_kd.balance()
seam = duv.vertex_groups.new(name="Filling")
for v in duv.data.vertices:
    d = _kd.find(v.co)[2]
    seam.add([v.index], 0.15 + 0.85 * min(1.0, d / 0.12) ** 0.6, "REPLACE")
so = duv.modifiers.new("Puff", "SOLIDIFY")
so.vertex_group, so.thickness_vertex_group = "Filling", 0.15
so.thickness, so.offset, so.use_even_offset = 0.045, -1.0, False   # even offset shot spikes out of sharp folds
so.thickness_clamp, so.use_quality_normals = 1.0, True
sm = duv.modifiers.new("Smooth", "SUBSURF")
sm.levels = sm.render_levels = 2                      # 5 mm: the crinkles need the density
folds = bpy.data.textures.get("TX_SZ_Folds") or bpy.data.textures.new("TX_SZ_Folds", "CLOUDS")
folds.noise_scale, folds.noise_depth = 0.12, 2
dp = duv.modifiers.new("Folds", "DISPLACE")
dp.texture, dp.strength, dp.texture_coords = folds, 0.0035, "GLOBAL"
crk = bpy.data.textures.get("TX_SZ_Crinkle") or bpy.data.textures.new("TX_SZ_Crinkle", "STUCCI")
crk.noise_scale, crk.turbulence = 0.035, 3.0
_emp = bpy.data.objects.get("SZ_CrinkleSpace") or bpy.data.objects.new("SZ_CrinkleSpace", None)
if _emp.name not in col.objects:
    col.objects.link(_emp)
_emp.scale = (1.0, 2.6, 1.0)                                # stretched along the bed: cover wrinkles run lengthwise
_emp.hide_render = _emp.hide_viewport = True
ck = duv.modifiers.new("Crinkle", "DISPLACE")
ck.texture, ck.strength, ck.texture_coords, ck.texture_coords_object = crk, 0.0022, "OBJECT", _emp
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

# ------------------------------------------------------------------ the arms press into the duvet
# Regie 2026-10-25 (close-up): forearms and hands lay *in* the duvet - its geometry cut through them and cast dark
# shadow patches onto the skin. Real arms resting on a down duvet sink in: the duvet top under each forearm and hand
# (pose from c00_pose_lying.py, written after the height map above, which stays the undented surface the IK uses)
# is pressed down to the underside of the limb plus a soft 4 cm shoulder of compressed filling around it.
_posed = POSE.get("posed", {})


def _cap(a, b, r):
    return to_world(*a), to_world(*b), r / 100


_caps = []
for side in ("l", "r"):
    el, ha = _posed.get(f"lowerarm_{side}"), _posed.get(f"hand_{side}")
    if el and ha:
        e, h = Vector(el["new"][0]), Vector(ha["new"][0])
        tip = h + (h - e).normalized() * 9.0
        _caps += [_cap(e, h, 4.0), _cap(h, tip, 3.0)]
FALL = 0.04
for v in duv.data.vertices:
    w = duv.matrix_world @ v.co
    for a, b, r in _caps:
        ab = Vector((b.x - a.x, b.y - a.y))
        t = max(0.0, min(1.0, (Vector((w.x - a.x, w.y - a.y))).dot(ab) / max(ab.length_squared, 1e-9)))
        c = a.lerp(b, t)
        d = math.hypot(w.x - c.x, w.y - c.y)
        if d > r + FALL:
            continue
        under = c.z - math.sqrt(max(0.0, r * r - min(d, r) ** 2)) - 0.003
        target = under if d <= r else under + (w.z - under) * smoothstep(0.0, 1.0, (d - r) / FALL)
        target = max(target, w.z - 0.025)                 # down filling compresses ~2.5 cm, never through to the body
        if target < w.z:
            v.co.z -= (w.z - target)
duv.data.update()

result = {"P0": [round(v, 3) for v in P0], "head": [round(v, 3) for v in to_world(*POSE["joints"]["head"])], "chest_y": round(chest_y, 3)}
