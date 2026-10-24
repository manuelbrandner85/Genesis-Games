"""G7 (runs INSIDE Blender 5.2): build SM_R03_PartsShelf, the parts store of the R03 workshop.

Measure sheet docs/design/G7_FLUSSDORF_ASSETS.md: 1000 x 400 x 2000 mm, five galvanised steel shelves on
slotted angle posts, open-front plastic parts bins with blank labels, cardboard boxes, a fuel-hose coil.
Origin floor centre, X = width, -Y = front, Z up. Contents are part of the mesh (static set dressing).
Reference: ArtSource/Reference/G7/SM_R03_PartsShelf/front34_v1.png (FLUX.2 klein, seed 8).
"""
import bpy, bmesh, math, os, random
from mathutils import Vector

NAME = "SM_R03_PartsShelf"
COL = "G7_PartsShelf"
exec(compile(open(os.path.join(os.path.dirname(__file__), "g7_common.py"), encoding="utf8").read(), "g7_common.py", "exec"))

sc = bpy.context.scene
col = bpy.data.collections.get(COL)
if col:
    for o in list(col.all_objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    col = bpy.data.collections.new(COL)
    sc.collection.children.link(col)
for m in [m for m in bpy.data.materials if m.name.startswith("M_SH_")]:
    bpy.data.materials.remove(m)
rnd = random.Random(2026)


def galvanised(name):
    """Hot-dip galvanised sheet: zinc spangle cells (medium), white-rust bloom near the floor, finger
    marks on shelf fronts are covered by the roughness noise (micro)."""
    mat = simple_mat(name, (0.50, 0.51, 0.52), 0.50, metal=1.0, rough_var=0.06, bump=0.03, grime=0.5)   # aged zinc: dull grey, white rust
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 45.0
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    spangle = _range(nt, vor.outputs["Color"], 0.0, 1.0, 0.28, 0.50, smooth=False)
    old = bsdf.inputs["Roughness"].links[0].from_socket
    nt.links.new(_add(nt, _add(nt, old, spangle), 0.5, "MULTIPLY"), bsdf.inputs["Roughness"])
    return mat


def cardboard(name):
    mat = simple_mat(name, (0.31, 0.20, 0.10), 0.86, rough_var=0.05, bump=0.18, grime=0.5)
    return mat


M = {
    "zinc": galvanised("M_SH_GalvanisedSteel"),
    "bin": paint_mat("M_SH_BinPlasticBlue", (0.030, 0.055, 0.21), 0.42, chip_metal=(0.05, 0.08, 0.25), dust=0.4),
    "label": simple_mat("M_SH_LabelPaper", (0.74, 0.73, 0.69), 0.80, rough_var=0.05, bump=0.05, grime=0.3),
    "card": cardboard("M_SH_Cardboard"),
    "tape": simple_mat("M_SH_PackingTape", (0.55, 0.45, 0.30), 0.30, rough_var=0.05, bump=0.02),
    "hose": simple_mat("M_SH_FuelHose", (0.025, 0.025, 0.026), 0.45, rough_var=0.08, bump=0.02),
    "steel": simple_mat("M_SH_PartsSteel", (0.55, 0.56, 0.57), 0.40, metal=1.0, rough_var=0.12, bump=0.06),
    "rubber": simple_mat("M_SH_Rubber", (0.022, 0.022, 0.022), 0.86, rough_var=0.06, bump=0.08),
}

W, D, H = 1.0, 0.40, 2.0
SHELF_Z = [0.08, 0.50, 0.92, 1.34, 1.76]          # top surfaces of the five boards (approx. 420 mm pitch)
parts = []
# slotted angle posts 40 x 40 x 2 mm, open sides facing inwards
for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
    x, y = sx * (W / 2 - 0.02), sy * (D / 2 - 0.02)
    parts.append(box(f"Post_{i}_A", (0.040, 0.002, H), (x, y + sy * 0.019, H / 2), "zinc", bevel=0.0006))
    parts.append(box(f"Post_{i}_B", (0.002, 0.040, H), (x + sx * 0.019, y, H / 2), "zinc", bevel=0.0006))
    for k in range(int(H / 0.025)):                 # key-hole slots every 25 mm on the front flange
        if k % 2 == 0:
            parts.append(box(f"Post_{i}_Slot_{k}", (0.006, 0.0025, 0.014), (x, y + sy * 0.019, 0.02 + k * 0.025), "rubber", bevel=None))
    parts.append(box(f"Post_{i}_Foot", (0.045, 0.045, 0.004), (x, y, 0.002), "rubber", bevel=0.001))
# shelf boards: 0.7 mm sheet with 30 mm folded edges + bolts into the posts
for k, z in enumerate(SHELF_Z):
    parts.append(box(f"Board_{k}", (W - 0.004, D - 0.004, 0.0015), (0, 0, z), "zinc", bevel=None))
    for s in (-1, 1):
        parts.append(box(f"Board_{k}_LipY_{s}", (W - 0.004, 0.0015, 0.03), (0, s * (D / 2 - 0.0035), z - 0.015), "zinc", bevel=0.0004))
        parts.append(box(f"Board_{k}_LipX_{s}", (0.0015, D - 0.004, 0.03), (s * (W / 2 - 0.0035), 0, z - 0.015), "zinc", bevel=0.0004))
        for sy in (-1, 1):
            parts.append(cyl(f"Board_{k}_Bolt_{s}_{sy}", 0.004, 0.004, (s * (W / 2 - 0.02), sy * (D / 2 + 0.0002), z - 0.012), "steel",
                             rot=(math.pi / 2, 0, 0), verts=6, bevel=0.0005))


def open_bin(name, w, d, h, loc, rot_z=0.0):
    """Open-front stackable parts bin: shell with a lowered front opening, 2 mm walls, blank label."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((w, d, h)), verts=bm.verts)
    top = [f for f in bm.faces if f.normal.z > 0.9]
    bmesh.ops.delete(bm, geom=top, context="FACES")
    ob = _obj(name, bm, "bin", loc, (0, 0, rot_z), bevel=None)
    sol = ob.modifiers.new("Wall", "SOLIDIFY")
    sol.thickness = 0.002
    sol.offset = -1.0
    bv = ob.modifiers.new("Bevel", "BEVEL")
    bv.width = 0.0012
    bv.segments = 2
    bv.limit_method = "ANGLE"
    parts.append(ob)
    lb = box(name + "_Label", (w * 0.55, 0.0006, h * 0.32), (0, 0, 0), "label", bevel=None)
    lb.location = Vector(loc) + Vector((rnd.uniform(-0.01, 0.01), -d / 2 - 0.0012, h * 0.08))
    lb.rotation_euler = (0, rnd.uniform(-0.04, 0.04), rot_z)
    parts.append(lb)
    # some small parts showing over the rim
    for j in range(rnd.randint(2, 5)):
        p = Vector(loc) + Vector((rnd.uniform(-w / 3, w / 3), rnd.uniform(-d / 4, d / 4), h * 0.18 + j * 0.004))
        if rnd.random() < 0.5:
            parts.append(cyl(f"{name}_Part_{j}", rnd.uniform(0.006, 0.012), rnd.uniform(0.015, 0.04), tuple(p), "steel",
                             rot=(rnd.uniform(0, 3), rnd.uniform(0, 3), 0), verts=12, bevel=0.0006))
        else:
            parts.append(box(f"{name}_Part_{j}", (rnd.uniform(0.012, 0.03), rnd.uniform(0.01, 0.02), 0.008), tuple(p), "rubber",
                             bevel=0.001, rot=(0, 0, rnd.uniform(0, 3))))


def carton(name, size, loc, rot_z, open_top=False):
    parts.append(box(name, size, loc, "card", bevel=0.002, rot=(0, 0, rot_z)))
    tape_w = 0.048
    t = box(name + "_Tape", (size[0] + 0.0012, tape_w, 0.0006), (0, 0, 0), "tape", bevel=None)
    t.location = Vector(loc) + Vector((0, 0, size[2] / 2 + 0.0003))
    t.rotation_euler = (0, 0, rot_z)
    parts.append(t)
    if open_top:                                      # one flap folded back
        f = box(name + "_Flap", (size[0], 0.002, size[1] * 0.45), (0, 0, 0), "card", bevel=0.001)
        f.location = Vector(loc) + Vector((0, size[1] / 2 + 0.06, size[2] / 2 + 0.03))
        f.rotation_euler = (-0.5, 0, rot_z)
        parts.append(f)


# contents per board (top to bottom roughly like the reference: bins, mixed, cartons, bins + hose)
bins_small = (0.16, 0.24, 0.12)
bins_large = (0.21, 0.30, 0.15)
for k, z in enumerate(SHELF_Z[1:], start=1):
    x = -W / 2 + 0.03
    if k in (4, 2):
        while x + bins_small[0] < W / 2 - 0.03:
            open_bin(f"Bin_{k}_{x:.2f}", *bins_small, (x + bins_small[0] / 2, -0.04, z + bins_small[2] / 2), rnd.uniform(-0.03, 0.03))
            x += bins_small[0] + rnd.uniform(0.004, 0.015)
    elif k == 3:
        carton(f"Carton_{k}_0", (0.30, 0.26, 0.18), (-0.30, 0.0, z + 0.09), rnd.uniform(-0.08, 0.08), open_top=True)
        carton(f"Carton_{k}_1", (0.22, 0.20, 0.14), (0.02, 0.02, z + 0.07), rnd.uniform(-0.1, 0.1))
        carton(f"Carton_{k}_2", (0.24, 0.30, 0.20), (0.32, -0.01, z + 0.10), rnd.uniform(-0.06, 0.06))
    elif k == 1:
        for j in range(3):
            open_bin(f"Bin_{k}_{j}", *bins_large, (-W / 2 + 0.14 + j * 0.23, -0.03, z + bins_large[2] / 2), rnd.uniform(-0.03, 0.03))
# bottom board: fuel hose coil and a heavy carton
for ring in range(5):                                # coiled hose: stacked torus rings, slightly offset
    bm = bmesh.new()
    seg = 64
    R, r = 0.13 - ring * 0.006, 0.0065
    for i in range(seg):
        a = 2 * math.pi * i / seg
        c = Vector((R * math.cos(a), R * math.sin(a), 0))
        for j in range(10):
            b = 2 * math.pi * j / 10
            bm.verts.new(c + Vector((math.cos(a) * math.cos(b), math.sin(a) * math.cos(b), math.sin(b))) * r)
    bm.verts.ensure_lookup_table()
    for i in range(seg):
        for j in range(10):
            a1, a2 = i * 10 + j, i * 10 + (j + 1) % 10
            b1, b2 = ((i + 1) % seg) * 10 + j, ((i + 1) % seg) * 10 + (j + 1) % 10
            bm.faces.new((bm.verts[a1], bm.verts[b1], bm.verts[b2], bm.verts[a2]))
    parts.append(_obj(f"Hose_Ring_{ring}", bm, "hose", (0.26, 0.02, SHELF_Z[0] + 0.0065 + ring * 0.0125), (0.03 * ring, 0.02, ring * 0.7)))
carton("Carton_0_0", (0.40, 0.30, 0.24), (-0.22, 0.0, SHELF_Z[0] + 0.12), 0.05)

shelf = join_parts(NAME, parts)
collision_box(NAME + "_00", (W, D, H), (0, 0, H / 2), shelf)
smart_uv(shelf)
shelf.location.x = -1.2         # next to the generator in the look-dev scene
bb = [shelf.matrix_world @ Vector(c) for c in shelf.bound_box]
dims = [round(max(v[i] for v in bb) - min(v[i] for v in bb), 4) for i in range(3)]
result = {"object": NAME, "dims_m": dims, "z_min": round(min(v.z for v in bb), 4),
          "tris": sum(len(p.vertices) - 2 for p in shelf.data.polygons), "materials": [m.name for m in shelf.data.materials]}
print("G7_SHELF", result)
