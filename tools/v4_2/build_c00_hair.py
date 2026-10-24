"""C00 (runs INSIDE Blender, scene "C00_Tochter"): own hair groom for CHR_C00_TOCHTER.

Regie 2026-10-24 (reference photo "50 elegante Long Bob Frisuren"): long bob to just above the collarbone,
centre parting, voluminous loose waves, balayage (dark brown roots, caramel/honey lengths).
None of the bundled MetaHuman grooms has a centre parting with this volume, so the strands are generated:
- roots sampled on the scalp of the daughter's head mesh (hairline front/sides/nape), centre parting at x = 0
- each strand leaves the scalp along its normal, flows sideways from the parting and then down the head
  shape, kept outside the scalp by a growing volume layer; below the ears it falls freely
- strands are grouped into clumps that share an S-wave (amplitude growing towards the ends), the ends
  turn slightly outwards like a blow-dried long bob; front lengths are 3 cm longer than the back (A-line)
Output: Curves object "C00_Haar" with per-point radius and "strand_t" (0 root .. 1 tip) for the balayage,
exported as Alembic for the Unreal groom importer.
"""
import math
import random

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

SC = bpy.data.scenes["C00_Tochter"]
HEAD = SC.objects["C00_Tochter_Kopf_v2"]
OUT = r"C:\Users\manue\Desktop\Genesis-Games\ArtSource\Export\C00\GR_C00_Tochter_Haar.abc"
N_STRANDS = 60000
N_CLUMPS = 320
POINTS = 28
SEED = 1101

rng = random.Random(SEED)
deps = bpy.context.evaluated_depsgraph_get()
mw = HEAD.matrix_world
mesh = HEAD.evaluated_get(deps).to_mesh()
verts = [mw @ v.co for v in mesh.vertices]
polys = [tuple(p.vertices) for p in mesh.polygons]
bvh = BVHTree.FromPolygons(verts, polys)
HEAD.evaluated_get(deps).to_mesh_clear()

TOP = max(v.z for v in verts)
CENTER = Vector((0.0, -0.015, TOP - 0.115))         # inside the skull, a little behind the face
EAR_Z = TOP - 0.135                                   # below this the hair hangs free
FACE_HALF = 0.083                                     # half width of the face the hair frames


def scalp_point(direction):
    """Ray from outside towards the skull centre: first hit on the head surface."""
    origin = CENTER + direction * 0.4
    hit, nrm, _, _ = bvh.ray_cast(origin, -direction, 0.5)
    return (hit, nrm) if hit else (None, None)


def on_scalp(d):
    """Hairline: forehead (front, -Y), above the ears at the sides, down to the nape at the back."""
    elev = math.degrees(math.asin(max(-1, min(1, d.z))))
    az = math.degrees(math.atan2(d.x, -d.y))          # 0 front, +-90 sides, 180 back
    a = abs(az)
    if a < 60:                                        # forehead hairline, a little higher at the temples
        limit = 32 + (a / 60) * 6
    elif a < 110:                                     # temples and above the ears
        limit = 38 - (a - 60) / 50 * 30
    else:                                             # behind the ears down to the nape
        limit = 8 - (a - 110) / 70 * 38
    return elev > limit


def push_out(p, minimum):
    """Keep p at least `minimum` outside the scalp."""
    loc, nrm, _, dist = bvh.find_nearest(p)
    if loc is None:
        return p
    inside = (p - loc).dot(nrm) < 0
    if inside or dist < minimum:
        return loc + nrm * minimum
    return p


# --- roots --------------------------------------------------------------------------------------------
roots = []
while len(roots) < N_STRANDS:
    d = Vector((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1))).normalized()
    if not on_scalp(d) or abs(d.x) < 0.012:          # centre parting: a thin bare line along x = 0 on top
        continue
    p, n = scalp_point(d)
    if p is not None:
        roots.append((p, n.normalized(), d))

# clumps: nearest seed on the scalp, same side of the parting
seeds = [r for r in rng.sample(roots, N_CLUMPS)]
clump_of = []
for p, n, d in roots:
    best = min(range(N_CLUMPS), key=lambda i: (seeds[i][0] - p).length_squared + (0 if (seeds[i][0].x > 0) == (p.x > 0) else 1.0))
    clump_of.append(best)
clump_phase = [rng.uniform(0, 2 * math.pi) for _ in range(N_CLUMPS)]
clump_amp = [rng.uniform(0.020, 0.032) for _ in range(N_CLUMPS)]


def strand(p, n, d, phase, amp):
    side = 1.0 if p.x > 0 else -1.0
    front = max(0.0, -d.y)                            # 1 at the face, 0 at the back
    end_z = 1.495 - 0.030 * front + rng.uniform(-0.018, 0.012)   # above the collarbone; A-line; uneven ends
    pts = [p.copy()]
    q = p + n * 0.006
    seg = 0.018
    for k in range(1, 200):
        if q.z <= end_z or len(pts) > 400:
            break
        t_len = max(0.0, (p.z - q.z) / max(0.05, p.z - end_z))
        free = q.z < EAR_Z
        outward = (q - CENTER)
        outward.z = 0
        outward = outward.normalized() if outward.length > 1e-6 else Vector((side, 0, 0))
        # flow: away from the parting at the top, then downwards along the head
        # near the parting the strand swings sideways (front strands also a little back, over the temples);
        # above the ears it lies on the head at a fixed volume offset, below it falls freely
        near_part = q.z > TOP - 0.05 or (front > 0.45 and q.z > TOP - 0.115)   # front hairline swings sideways too: no fringe
        sweep = (0.8 + 0.6 * front) if near_part else 0.0
        flow = Vector((side * sweep, 0.25 * front * near_part, -1.0))
        if free:
            flow += outward * 0.16                       # body: the lengths spread out a little
        q = q + flow.normalized() * seg * 0.35
        volume = 0.010 + 0.014 * min(1.0, t_len * 1.8)     # lift at the roots, more body at mid lengths
        if not free:
            loc, nrm, _, _ = bvh.find_nearest(q)
            if loc is not None:
                q = loc + nrm * volume                   # hugs the head shape
        else:
            q = push_out(q, volume)
        # frame the face: strands ease past the face instead of hanging in front of it
        if q.y < CENTER.y - 0.035 and q.z < TOP - 0.075 and abs(q.x) < FACE_HALF:
            q.x += side * (FACE_HALF - abs(q.x)) * 0.45
        pts.append(q.copy())
    # resample to POINTS, add the S-wave and the outward flick of the ends
    total = sum((pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)) or 1e-6
    out, acc, j = [], 0.0, 0
    for i in range(POINTS):
        target = total * i / (POINTS - 1)
        while j < len(pts) - 2 and acc + (pts[j + 1] - pts[j]).length < target:
            acc += (pts[j + 1] - pts[j]).length
            j += 1
        segl = (pts[j + 1] - pts[j]).length or 1e-6
        f = min(1.0, max(0.0, (target - acc) / segl))
        out.append(pts[j].lerp(pts[j + 1], f))
    result = []
    for i, q in enumerate(out):
        t = i / (POINTS - 1)
        r = (q - CENTER)
        r.z = 0
        r = r.normalized() if r.length > 1e-6 else Vector((side, 0, 0))
        tangent = Vector((-r.y, r.x, 0))
        below = max(0.0, (TOP - 0.09 - q.z) / 0.12)   # waves start at cheek height
        wave = amp * min(1.0, below) * math.sin(phase + (p.z - q.z) / 0.13 * 2 * math.pi)   # loose, large waves (S-bend every ~13 cm)
        flick = 0.018 * max(0.0, t - 0.82) / 0.18      # ends turn outwards
        result.append(q + tangent * wave + r * (abs(wave) * 0.35 + flick))
    return result


strands = []
for (p, n, d), c in zip(roots, clump_of):
    s = strand(p, n, d, clump_phase[c], clump_amp[c])
    strands.append(s)

# clumping: pull each strand towards its clump's mean shape (stronger towards the tips)
clump_mean = {}
for s, c in zip(strands, clump_of):
    m = clump_mean.setdefault(c, [Vector() for _ in range(POINTS)] + [0])
    for i in range(POINTS):
        m[i] += s[i]
    m[POINTS] += 1
for c, m in clump_mean.items():
    for i in range(POINTS):
        m[i] /= m[POINTS]
for idx, (s, c) in enumerate(zip(strands, clump_of)):
    m = clump_mean[c]
    root_off = s[0] - m[0]
    for i in range(1, POINTS):
        t = i / (POINTS - 1)
        k = 0.55 * t ** 1.4
        target = m[i] + root_off * (1 - t)            # clump shape, root stays where it grows
        s[i] = s[i].lerp(target, k)
        s[i] = push_out(s[i], 0.003)

# --- Curves object ----------------------------------------------------------------------------------------
if "C00_Haar" in SC.objects:
    bpy.data.objects.remove(SC.objects["C00_Haar"])
cd = bpy.data.hair_curves.new("C00_Haar") if hasattr(bpy.data, "hair_curves") else bpy.data.curves.new("C00_Haar", "CURVE")
cd.add_curves([POINTS] * len(strands))
co = [c for s in strands for v in s for c in v]
cd.position_data.foreach_set("vector", co)
radius = []
strand_t = []
for s in strands:
    for i in range(POINTS):
        t = i / (POINTS - 1)
        radius.append(0.000045 * (1 - t) + 0.000020 * t)   # 90 um root -> 40 um tip (diameter)
        strand_t.append(t)
cd.attributes["radius"].data.foreach_set("value", radius) if "radius" in cd.attributes else \
    cd.attributes.new("radius", "FLOAT", "POINT").data.foreach_set("value", radius)
cd.attributes.new("strand_t", "FLOAT", "POINT").data.foreach_set("value", strand_t)
ob = bpy.data.objects.new("C00_Haar", cd)
SC.collection.objects.link(ob)
mat = bpy.data.materials.get("C00_Haar_MAT") or bpy.data.materials.new("C00_Haar_MAT")
mat.use_nodes = True
nt = mat.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
hair = nt.nodes.new("ShaderNodeBsdfHairPrincipled")
attr = nt.nodes.new("ShaderNodeAttribute")
attr.attribute_name = "strand_t"
ramp = nt.nodes.new("ShaderNodeMapRange")
nt.links.new(attr.outputs["Fac"], ramp.inputs[0])
ramp.inputs[1].default_value, ramp.inputs[2].default_value = 0.30, 0.75     # balayage starts below the ears
mel = nt.nodes.new("ShaderNodeMix")
mel.data_type = "FLOAT"
nt.links.new(ramp.outputs[0], mel.inputs["Factor"])
mel.inputs["A"].default_value, mel.inputs["B"].default_value = 0.72, 0.30   # dark brown root -> caramel/honey
hair.parametrization = "MELANIN"
nt.links.new(mel.outputs["Result"], hair.inputs["Melanin"])
hair.inputs["Melanin Redness"].default_value = 0.42
hair.inputs["Roughness"].default_value = 0.28
outn = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(hair.outputs[0], outn.inputs[0])
cd.materials.append(mat)
result = {"strands": len(strands), "points": POINTS, "top": round(TOP, 3)}
