"""C00 (runs INSIDE Blender, scene C00_Schlafzimmer, after build_c00_bedroom_decor.py): the things on the nightstand.

Regie/QA 2026-10-25: "die Buecher ragen in die Lampe und sehen aus wie bunte Lego-Kloetze", "das Glas sieht sehr
unrealistisch aus" - measured: the book stack stood 7 cm inside the lamp base and the water glass inside the turned-away
photo frame. Rebuilt with real construction and a collision-free layout (nightstand top x/y relative to its centre):
- lamp (x 0.035..0.165, y -0.005..0.125) and photo frame (x -0.18..-0.04, y -0.108..-0.012) stay as built
- three books across the front, spines toward the room: hardcovers = two 2.5 mm boards overhanging 3 mm at head, tail and
  fore-edge, a rounded cloth spine, a page block set into them; the paperback = flush soft cover with a flat spine.
  Spine titles as real geometry - an easter egg for the game, no story content: "GENESIS", "Der letzte Augenblick"
  (working title of C00), "Atlas 2026" (the year the first life begins)
- a tumbler at the back left: 2.2 mm wall, 8 mm base, rounded rim, water inside with a small meniscus
- the medicine box beside it
Every object is checked against the others (bounding boxes, 2 mm clearance) and the script stops on an overlap.
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

sc = bpy.data.scenes["C00_Schlafzimmer"]
dc = bpy.data.collections["C00_SZ_Deko"]
D = 3.20
BX, BY0 = -0.25, D / 2 - 0.03
NX, NY = BX + 0.75 + 0.27, D / 2 - 0.22
TOP = 0.56
for o in [o for o in dc.objects if o.name.startswith(("SZ_Book", "SZ_Drink", "SZ_Medicine", "SZ_NS_"))]:
    bpy.data.objects.remove(o, do_unlink=True)


def mat(name, rgb, rough=0.6, metal=0.0, trans=0.0, ior=1.45):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Transmission Weight"].default_value = trans
    b.inputs["IOR"].default_value = ior
    return m


def obj(name, bm, m, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    dc.objects.link(o)
    me.materials.append(m)
    return o


def box_bm(size, centre):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0] + centre[0], v.co.y * size[1] + centre[1], v.co.z * size[2] + centre[2]))
    return bm


def bevel(o, w, seg=2):
    b = o.modifiers.new("Bevel", "BEVEL")
    b.width, b.segments, b.limit_method = w, seg, "ANGLE"
    return o


def text_mesh(name, txt, size, m):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body, cu.size, cu.extrude, cu.align_x, cu.align_y = txt, size, 0.00015, "CENTER", "CENTER"
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    sc.collection.objects.link(tmp)
    deps = sc.view_layers[0].depsgraph if sc.view_layers[0].depsgraph else bpy.context.evaluated_depsgraph_get()
    with bpy.context.temp_override(scene=sc, view_layer=sc.view_layers[0]):
        deps = bpy.context.evaluated_depsgraph_get()
        deps.update()
        me = bpy.data.meshes.new_from_object(tmp.evaluated_get(deps), depsgraph=deps)
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.curves.remove(cu)
    me.name = name
    o = bpy.data.objects.new(name, me)
    dc.objects.link(o)
    me.materials.append(m)
    return o


# ------------------------------------------------------------------ materials
M_PAGES = mat("M_SZ_BookPages", (0.80, 0.76, 0.66), 0.85)
M_FOIL = mat("M_SZ_BookFoil", (0.80, 0.62, 0.32), 0.35, metal=1.0)
M_INK = mat("M_SZ_BookInk", (0.05, 0.05, 0.06), 0.55)
M_HEADBAND = mat("M_SZ_BookHeadband", (0.55, 0.12, 0.10), 0.5)
M_RIBBON = mat("M_SZ_BookRibbon", (0.42, 0.06, 0.07), 0.45)
COVERS = [mat("M_SZ_BookCover0", (0.05, 0.08, 0.18), 0.75), mat("M_SZ_BookCover1", (0.62, 0.50, 0.30), 0.55),
          mat("M_SZ_BookCover2", (0.30, 0.06, 0.05), 0.75)]


def flat_text(name, txt, size, m, centre, rot_z=0.0):
    """text lying on a horizontal surface (book cover), centre in book space, reading along +y rotated by rot_z"""
    o = text_mesh(name, txt, size, m)
    o.matrix_world = Matrix.Translation(centre) @ Matrix.Rotation(rot_z, 4, "Z")
    return o


def book(key, w, h, t, origin, rot_deg, cover, hard, title, sub, title_mat, front=None, ribbon=None, bow=0.0):
    """origin = (spine x, centre y, bottom z) in nightstand space; the spine faces -x (toward the bed).
    w = cover width (x), h = height along the spine (y), t = thickness (z).
    Regie 2026-10-25 ("viel huebscher und realistischer"): headbands at head and tail of the spine (hardcovers), front-cover
    title with a foil frame (front), a reading ribbon out of the tail (ribbon = colour), a paperback cover bowing up at
    the fore-edge from use (bow, m), worn rounded corners."""
    parts = []
    ox, oy, oz = origin
    board = 0.0025 if hard else 0.0004
    over = 0.003 if hard else 0.0
    pb_h, pb_w, pb_t = h - 2 * over, w - over - 0.004, t - 2 * board
    # page block: set 4 mm in from the spine (hinge) - fore-edge slightly rounded (bevel)
    pg = obj(f"SZ_Book{key}_Pages", box_bm((pb_w, pb_h, pb_t), (0.004 + pb_w / 2, 0, board + pb_t / 2)), M_PAGES)
    parts.append(bevel(pg, 0.0012, 3))
    for i, z in enumerate((board / 2, t - board / 2)):                     # the two covers
        bmc = box_bm((w, h, board), (w / 2, 0, z))
        if bow and i == 1:                                                 # used paperback: the cover lifts at the fore-edge
            for v in bmc.verts:
                v.co.z += bow * (v.co.x / w) ** 2
        c = obj(f"SZ_Book{key}_Cover{i}", bmc, cover)
        parts.append(bevel(c, min(0.0016, board * 0.45) if hard else 0.0002, 3))
    if hard:                                                               # headbands (Kapitalband), striped silk
        for side in (-1, 1):
            hb = bmesh.new()
            bmesh.ops.create_cone(hb, cap_ends=True, segments=10, radius1=0.0011, radius2=0.0011, depth=pb_t * 0.92)
            for v in hb.verts:
                v.co = Vector((v.co.x + 0.0028, v.co.y + side * (pb_h / 2 + 0.0004), v.co.z + t / 2))
            parts.append(obj(f"SZ_Book{key}_Headband{side}", hb, M_HEADBAND, smooth=True))
    if ribbon:                                                             # reading ribbon out of the tail, lying loose
        rb = bmesh.new()
        pts = [Vector((0.03 + 0.004 * k, -pb_h / 2 + 0.01 - 0.012 * k, max(-0.0008 * k * k, -oz + TOP) + t * 0.5 - 0.0005 * k))
               for k in range(9)]
        rows = [[rb.verts.new(p + Vector((dx, 0, 0))) for dx in (-0.0015, 0.0015)] for p in pts]
        for k in range(len(rows) - 1):
            rb.faces.new((rows[k][0], rows[k][1], rows[k + 1][1], rows[k + 1][0]))
        parts.append(obj(f"SZ_Book{key}_Ribbon", rb, ribbon, smooth=True))
    if front:                                                              # front cover: foil frame + title
        fz = t + 0.00018
        fx0, fx1, fy0, fy1 = 0.012, w - 0.01, -h / 2 + 0.012, h / 2 - 0.012
        for nm, (sx, sy, cx_, cy_) in {"L": (0.0009, fy1 - fy0, fx0, 0), "R": (0.0009, fy1 - fy0, fx1, 0),
                                      "T": (fx1 - fx0, 0.0009, (fx0 + fx1) / 2, fy1), "B": (fx1 - fx0, 0.0009, (fx0 + fx1) / 2, fy0)}.items():
            parts.append(obj(f"SZ_Book{key}_Frame{nm}", box_bm((sx, sy, 0.0002), (cx_, cy_, fz)), title_mat))
        parts.append(flat_text(f"SZ_Book{key}_FrontTitle", front, 0.0105, title_mat, (w / 2, -h * 0.12, fz), -math.pi / 2))   # head at the top for a reader
    bm = bmesh.new()                                                       # spine: half tube (hard) / flat (soft)
    if hard:
        segs, r = 12, t / 2
        rows = []
        for k in range(segs + 1):
            a = math.pi / 2 + math.pi * k / segs
            row = [bm.verts.new((r * 0.55 * math.cos(a) + 0.0015 * math.cos(a), y, t / 2 + r * math.sin(a))) for y in (-h / 2, h / 2)]
            rows.append(row)
        for k in range(segs):
            bm.faces.new((rows[k][0], rows[k + 1][0], rows[k + 1][1], rows[k][1]))
        sp = obj(f"SZ_Book{key}_Spine", bm, cover, smooth=True)
        so = sp.modifiers.new("Thick", "SOLIDIFY")
        so.thickness = 0.0012
        spine_x = -r * 0.55 - 0.0015 - 0.0012              # outside the solidified spine cloth
    else:
        bm.free()
        sp = obj(f"SZ_Book{key}_Spine", box_bm((0.0008, h, t), (0.0, 0, t / 2)), cover)
        spine_x = -0.0004
    parts.append(sp)
    # spine title: reads bottom to top (German convention), laid onto the spine surface
    tt = text_mesh(f"SZ_Book{key}_Title", title, min(t * 0.55, 0.012), title_mat)
    tt.matrix_world = Matrix.Translation((spine_x - 0.0002, h * 0.08, t / 2)) @ Matrix.Rotation(-math.pi / 2, 4, "Y") @ \
        Matrix.Rotation(-math.pi / 2, 4, "Z")
    parts.append(tt)
    if sub:
        st = text_mesh(f"SZ_Book{key}_Sub", sub, min(t * 0.30, 0.006), title_mat)
        st.matrix_world = Matrix.Translation((spine_x - 0.0002, -h * 0.38, t / 2)) @ Matrix.Rotation(-math.pi / 2, 4, "Y") @ \
            Matrix.Rotation(-math.pi / 2, 4, "Z")
        parts.append(st)
    M = Matrix.Translation((NX + ox, NY + oy, oz)) @ Matrix.Rotation(math.radians(rot_deg), 4, "Z")
    for p in parts:
        p.matrix_world = M @ p.matrix_world
    return parts


# ------------------------------------------------------------------ books: across the front, spines toward the room
# (38 cm nightstand depth: 20 cm books lengthwise ran into the lamp and over the front edge - turned 90 deg, the spine
# faces the room / foot end and the stack stays between the photo, the lamp and the front edge)
# CR-002 (draft, Game Director 2026-10-25): the photograph is gone - the books lie where it stood (front left)
SPINE_Y, CX = -0.170, -0.100
z = TOP
stack = (("0", 0.135, 0.205, 0.028, COVERS[0], True, "GENESIS", "Roman", M_FOIL, -2.0, None, None, 0.0),
         ("1", 0.118, 0.186, 0.019, COVERS[1], False, "Atlas 2026", "", M_INK, 3.0, None, None, 0.003),
         ("2", 0.128, 0.198, 0.031, COVERS[2], True, "Der letzte Augenblick", "", M_FOIL, -4.0, "Der letzte Augenblick",
          M_RIBBON, 0.0))
for key, w, h, t, cov, hard, title, sub, tm, rot, front, rib, bow in stack:
    book(key, w, h, t, (CX, SPINE_Y, z), 90.0 + rot, cov, hard, title, sub, tm, front, rib, bow)
    z += t + bow

# ------------------------------------------------------------------ tumbler with water, back left
GX, GY = -0.130, 0.100
R_OUT, WALL, BASE, HGT = 0.034, 0.0022, 0.008, 0.102
prof = [(0.0, 0.0), (R_OUT - 0.002, 0.0), (R_OUT, 0.002), (R_OUT + 0.0006, HGT - 0.0012), (R_OUT - WALL / 2, HGT),
        (R_OUT - WALL, HGT - 0.0012), (R_OUT - WALL, BASE + 0.003), (R_OUT - WALL - 0.003, BASE), (0.0, BASE)]
bm = bmesh.new()
SEG = 64
ring = []
for k in range(SEG):
    a = 2 * math.pi * k / SEG
    ring.append([bm.verts.new((r * math.cos(a), r * math.sin(a), zz)) for r, zz in prof])
for k in range(SEG):
    a, b = ring[k], ring[(k + 1) % SEG]
    for j in range(len(prof) - 1):
        if prof[j][0] == 0.0 and prof[j + 1][0] == 0.0:
            continue
        bm.faces.new((a[j], b[j], b[j + 1], a[j + 1]))
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
glass = obj("SZ_DrinkGlass", bm, mat("M_SZ_DrinkGlass", (0.95, 0.97, 0.97), 0.02, trans=1.0, ior=1.5), smooth=True)
glass.location = (NX + GX, NY + GY, TOP)
# water: fills the inside to 62 mm, its surface rises 1 mm against the wall (meniscus)
WR, WH = R_OUT - WALL - 0.0002, 0.062
bm = bmesh.new()
rings = []
for k in range(SEG):
    a = 2 * math.pi * k / SEG
    rings.append([bm.verts.new((rr * math.cos(a), rr * math.sin(a), zz)) for rr, zz in
                  ((0.0, BASE + 0.0002), (WR - 0.003, BASE + 0.0002), (WR, BASE + 0.003), (WR, WH + 0.001), (WR * 0.85, WH + 0.0002), (0.0, WH))])
for k in range(SEG):
    a, b = rings[k], rings[(k + 1) % SEG]
    for j in range(5):
        if j in (0, 4) and False:
            continue
        bm.faces.new((a[j], b[j], b[j + 1], a[j + 1]))
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
water = obj("SZ_DrinkWater", bm, bpy.data.materials["M_SZ_Water"], smooth=True)
water.location = glass.location.copy()

# ------------------------------------------------------------------ medicine box beside the glass
mb = obj("SZ_MedicineBox", box_bm((0.095, 0.05, 0.022), (0, 0, 0.011)), mat("M_SZ_MedicineBox", (0.80, 0.80, 0.78), 0.5))
bevel(mb, 0.0015, 2)
mb.location, mb.rotation_euler.z = (NX - 0.040, NY + 0.128, TOP), math.radians(14)

# ------------------------------------------------------------------ collision check (bounding boxes, 2 mm)
sc.view_layers[0].update()


def bbox(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return [min(p.x for p in pts), max(p.x for p in pts), min(p.y for p in pts), max(p.y for p in pts),
            min(p.z for p in pts), max(p.z for p in pts)]


groups = {"books": [o for o in dc.objects if o.name.startswith("SZ_Book")], "glass": [glass, water], "medicine": [mb],
          "lamp": [bpy.data.objects["SZ_LampBase"]]}
for n in ("SZ_PhotoFrame", "SZ_PhotoBack"):                    # CR-002: remove the photograph from an already built set
    o = bpy.data.objects.get(n)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
gb = {}
for g, objs in groups.items():
    bs = [bbox(o) for o in objs]
    gb[g] = [min(b[0] for b in bs), max(b[1] for b in bs), min(b[2] for b in bs), max(b[3] for b in bs),
             min(b[4] for b in bs), max(b[5] for b in bs)]
hits = []
names = list(gb)
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b = gb[names[i]], gb[names[j]]
        if a[0] < b[1] - 0.002 and b[0] < a[1] - 0.002 and a[2] < b[3] - 0.002 and b[2] < a[3] - 0.002 and \
                a[4] < b[5] - 0.002 and b[4] < a[5] - 0.002:
            hits.append((names[i], names[j]))
ns = bbox(bpy.data.objects.get("SZ_NightstandTop") or bpy.data.objects["SZ_Nightstand"])   # the top board carries the things
off = [g for g, b in gb.items() if g != "lamp" and (b[0] < ns[0] or b[1] > ns[1] or b[2] < ns[2] or b[3] > ns[3])]
result = {"overlaps": hits, "off_nightstand": off, "stack_top": round(z, 3),
          "books_rel": [round(v, 3) for v in (gb["books"][0] - NX, gb["books"][1] - NX, gb["books"][2] - NY, gb["books"][3] - NY)],
          "nightstand_rel": [round(v, 3) for v in (ns[0] - NX, ns[1] - NX, ns[2] - NY, ns[3] - NY)]}
print("C00_NIGHTSTAND", result)
if hits or off:
    raise RuntimeError(f"nightstand layout collides: {result}")
