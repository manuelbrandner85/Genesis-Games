"""C00 (runs INSIDE Blender 5.2 after the bedroom scripts): make SET_C00_SCHLAFZIMMER lived-in.

Regie 2026-10-25: "mehr Gegenstaende, viel wohnlicher, nicht so kalt, ein paar Bilder ... das Bild ueber dem
Bett soll den Mann mit seiner Tochter zeigen". Own geometry for the personal things (the bigger decor -
plants, further prints - comes from Epic's ArchViz Interior once it is added to the project):
- framed photo above the bed: father and daughter (T_C00_Foto_VaterTochter.png, rendered from the two C00
  MetaHumans by tools/v4_2/c00_photo_vater_tochter.py), 80 x 60 print, white mat, 100 x 78 oak frame
- nightstand: stack of three books, a glass of water, a small medicine box
- the daughter's chair: a knitted throw in warm mustard over the backrest (cloth simulation)
- a wool rug beside the bed on the window side
The nightstand photo stays turned away from the camera (ScriptLock 00-B).
"""
import bmesh
import bpy
import math
import os
from mathutils import Vector

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
sc = bpy.data.scenes["C00_Schlafzimmer"]
col = bpy.data.collections["C00_Schlafzimmer"]
W, D, H = 3.60, 3.20, 2.55
BX, BY0 = -0.25, D / 2 - 0.03
NX, NY = BX + 0.75 + 0.27, D / 2 - 0.22
NS_TOP = 0.56
dc = bpy.data.collections.get("C00_SZ_Deko")
if dc:
    for o in list(dc.objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    dc = bpy.data.collections.new("C00_SZ_Deko")
    col.children.link(dc)


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


def block(name, size, loc, m, rot_z=0.0, bevel=0.002):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    dc.objects.link(o)
    o.location, o.rotation_euler.z = loc, rot_z
    me.materials.append(m)
    if bevel:
        bv = o.modifiers.new("Bevel", "BEVEL")
        bv.width, bv.segments = bevel, 2
    return o


def cylinder(name, r, h, loc, m, segs=40, cap_bottom=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r, radius2=r, depth=h)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    dc.objects.link(o)
    o.location = loc
    me.materials.append(m)
    return o


# ------------------------------------------------------------------ framed photo above the bed
oak = bpy.data.materials["M_SZ_OakVeneer"]
mat_white = mat("M_SZ_PassepartoutWhite", (0.82, 0.80, 0.76), 0.85)
photo = mat("M_SZ_FotoVaterTochter", (0.6, 0.5, 0.4), 0.35)          # Unreal maps the photo texture onto this slot
FW, FH, PROF, DEPTH = 1.00, 0.78, 0.04, 0.035          # Regie: "viel groesser"
wall_y = D / 2 - 0.004
cx, cz = BX, 1.66
for name, size, off in (("Top", (FW, DEPTH, PROF), (0, FH / 2 - PROF / 2)), ("Bot", (FW, DEPTH, PROF), (0, -FH / 2 + PROF / 2)),
                        ("L", (PROF, DEPTH, FH), (-FW / 2 + PROF / 2, 0)), ("R", (PROF, DEPTH, FH), (FW / 2 - PROF / 2, 0))):
    block(f"SZ_WallFrame{name}", size, (cx + off[0], wall_y - DEPTH / 2, cz + off[1]), oak, bevel=0.003)
block("SZ_WallFrameMat", (FW - 2 * PROF, 0.004, FH - 2 * PROF), (cx, wall_y - 0.012, cz), mat_white, bevel=0)
# the print: 4:3, UVs span the whole photo; normal faces into the room (-Y)
PW, PH = 0.80, 0.60
bm = bmesh.new()
vs = [bm.verts.new((cx + x, wall_y - 0.0145, cz + z)) for x, z in ((-PW / 2, -PH / 2), (PW / 2, -PH / 2), (PW / 2, PH / 2), (-PW / 2, PH / 2))]
f = bm.faces.new(vs)
uv = bm.loops.layers.uv.new("UVMap")
for loop, (u, v) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):     # reads correctly after the Unreal Y flip
    loop[uv].uv = (u, v)
me = bpy.data.meshes.new("SZ_WallPhoto")
bm.to_mesh(me)
bm.free()
o = bpy.data.objects.new("SZ_WallPhoto", me)
dc.objects.link(o)
me.materials.append(photo)
img_path = os.path.join(ROOT, "ArtSource", "Export", "C00", "T_C00_Foto_VaterTochter.png")
if os.path.exists(img_path):                                    # Blender preview shows the real photo too
    img = bpy.data.images.load(img_path, check_existing=True)
    nt = photo.node_tree
    tex = next((n for n in nt.nodes if n.type == "TEX_IMAGE"), None) or nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    nt.links.new(tex.outputs["Color"], next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"])
# glass in front of the print (thin, subtle reflections)
block("SZ_WallFrameGlass", (FW - 2 * PROF, 0.002, FH - 2 * PROF), (cx, wall_y - 0.022, cz), bpy.data.materials["M_SZ_Glass"], bevel=0)

# ------------------------------------------------------------------ more family photos (Regie 2026-10-25: "Bilder in die
# leeren Rahmen: die Frau des Mannes, die Tochter sehr klein mit Vater und Mutter, ein schoenes Strandbild").
# Prints from the local FLUX.2 klein 4B (Apache-2.0, ArtSource/Reference/C00/PROPS_C00_FOTOS, provenance JSON there),
# old-film look so the faces need not match the MetaHumans exactly. Frames are own geometry (the ArchViz picture
# meshes lost their materials). u runs along the viewer's right (forward x up), as for the photo above the bed.


def framed(key, center, n, fw, fh, pw, ph, color=(0.20, 0.13, 0.08)):
    n, up = Vector(n), Vector((0, 0, 1))
    right = (-n).cross(up)
    c = Vector(center)
    fr_mat = mat(f"M_SZ_Rahmen_{key}", color, 0.5)
    prof, depth = 0.025, 0.025

    def at(u, v, d):
        return c + right * u + up * v + n * d

    def bar(nm, u, v, su, sv):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for vv in bm.verts:
            vv.co = at(u + vv.co.x * su, v + vv.co.z * sv, depth / 2 + vv.co.y * depth)
        me = bpy.data.meshes.new(nm)
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new(nm, me)
        dc.objects.link(o)
        me.materials.append(fr_mat)
        b = o.modifiers.new("Bevel", "BEVEL")
        b.width, b.segments = 0.002, 2

    bar(f"SZ_Frame_{key}_T", 0, fh / 2 - prof / 2, fw, prof)
    bar(f"SZ_Frame_{key}_B", 0, -fh / 2 + prof / 2, fw, prof)
    bar(f"SZ_Frame_{key}_L", -fw / 2 + prof / 2, 0, prof, fh)
    bar(f"SZ_Frame_{key}_R", fw / 2 - prof / 2, 0, prof, fh)
    for nm, w2, h2, d, m, uvs in ((f"SZ_FrameMat_{key}", fw - 2 * prof, fh - 2 * prof, 0.008, mat_white, False),
                                  (f"SZ_Photo_{key}", pw, ph, 0.010, None, True)):
        bm = bmesh.new()
        f = bm.faces.new([bm.verts.new(at(x, z, d)) for x, z in ((-w2 / 2, -h2 / 2), (w2 / 2, -h2 / 2), (w2 / 2, h2 / 2), (-w2 / 2, h2 / 2))])
        if uvs:
            uv = bm.loops.layers.uv.new("UVMap")
            for loop, (u, v) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
                loop[uv].uv = (u, v)
        me = bpy.data.meshes.new(nm)
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new(nm, me)
        dc.objects.link(o)
        if uvs:
            pm = mat(f"M_SZ_Foto_{key}", (0.6, 0.5, 0.4), 0.35)        # Unreal maps T_C00_Foto_<key> onto this slot
            img_path = os.path.join(ROOT, "ArtSource", "Export", "C00", f"T_C00_Foto_{key}.png")
            if os.path.exists(img_path):
                nt = pm.node_tree
                tex = next((x for x in nt.nodes if x.type == "TEX_IMAGE"), None) or nt.nodes.new("ShaderNodeTexImage")
                tex.image = bpy.data.images.load(img_path, check_existing=True)
                nt.links.new(tex.outputs["Color"], next(x for x in nt.nodes if x.type == "BSDF_PRINCIPLED").inputs["Base Color"])
            me.materials.append(pm)
        else:
            me.materials.append(m)


# east wall, between the window and the corner: the young family (1984), 50 x 42 frame
framed("Familie", (W / 2 - 0.002, -1.05, 1.42), (-1, 0, 0), 0.50, 0.42, 0.40, 0.336, (0.42, 0.29, 0.17))
# west wall, beside the door: the beach, 92 x 58 frame
framed("Strand", (-W / 2 + 0.002, 0.55, 1.45), (1, 0, 0), 0.92, 0.58, 0.82, 0.488)
# north wall above the nightstand: his wife, 40 x 40 frame
framed("Ehefrau", (1.22, D / 2 - 0.004, 1.50), (0, -1, 0), 0.40, 0.40, 0.30, 0.30, (0.42, 0.29, 0.17))

# ------------------------------------------------------------------ nightstand: books, water glass, medicine
books = (((0.15, 0.22, 0.028), (0.08, 0.13, 0.30)), ((0.14, 0.21, 0.022), (0.55, 0.42, 0.18)), ((0.13, 0.20, 0.032), (0.38, 0.10, 0.08)))
z = NS_TOP
for i, (size, rgb) in enumerate(books):
    block(f"SZ_Book{i}", size, (NX + 0.10, NY - 0.05, z + size[2] / 2), mat(f"M_SZ_BookCover{i}", rgb, 0.55),
          rot_z=math.radians((-6, 4, -2)[i]), bevel=0.003)
    block(f"SZ_BookPages{i}", (size[0] - 0.008, size[1] - 0.006, size[2] - 0.004), (NX + 0.10 + 0.004, NY - 0.05, z + size[2] / 2),
          mat("M_SZ_BookPages", (0.78, 0.74, 0.64), 0.8), rot_z=math.radians((-6, 4, -2)[i]), bevel=0.001)
    z += size[2]
glass = mat("M_SZ_DrinkGlass", (0.95, 0.97, 0.97), 0.02, trans=1.0, ior=1.5)
water = bpy.data.materials["M_SZ_Water"]                              # same water as the rain drops (glass BSDF, IOR 1.33)
cylinder("SZ_DrinkGlass", 0.034, 0.105, (NX - 0.13, NY - 0.10, NS_TOP + 0.0525), glass)
cylinder("SZ_DrinkWater", 0.031, 0.062, (NX - 0.13, NY - 0.10, NS_TOP + 0.034), water)
block("SZ_MedicineBox", (0.095, 0.05, 0.022), (NX - 0.02, NY - 0.15, NS_TOP + 0.011), mat("M_SZ_MedicineBox", (0.80, 0.80, 0.78), 0.5),
      rot_z=math.radians(18), bevel=0.0015)

# ------------------------------------------------------------------ wool rug beside the bed (window side)
rug = block("SZ_Rug", (0.80, 1.40, 0.012), (0.85, 0.15, 0.006), mat("M_SZ_RugWool", (0.55, 0.47, 0.38), 0.95), bevel=0.004)

# ------------------------------------------------------------------ knitted throw over the daughter's chair
CX, CY = BX + 0.95, -0.15
for n in ("SZ_ChairSeat", "SZ_ChairBack", "SZ_Floor"):          # floor too: the throw fell through it
    c = bpy.data.objects[n]
    if not any(m.type == "COLLISION" for m in c.modifiers):
        c.modifiers.new("Collision", "COLLISION")
    c.collision.thickness_outer = 0.004
    c.collision.cloth_friction = 15
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=40, y_segments=50, size=0.5)
for v in bm.verts:
    v.co = Vector((v.co.x * 1.1, v.co.y * 1.3, 0))
me = bpy.data.meshes.new("SZ_Throw")
bm.to_mesh(me)
bm.free()
for p in me.polygons:
    p.use_smooth = True
throw = bpy.data.objects.new("SZ_Throw", me)
dc.objects.link(throw)
throw.location = (CX + 0.05, CY - 0.10, 1.05)
throw.rotation_euler = (math.radians(90), 0, math.radians(8))          # hangs vertically, falls over the backrest
me.materials.append(mat("M_SZ_ThrowWool", (0.55, 0.36, 0.08), 0.95))  # warm mustard knit
cl = throw.modifiers.new("Cloth", "CLOTH")
st = cl.settings
st.quality, st.mass, st.air_damping = 10, 0.5, 2.0
st.bending_stiffness = 0.3
cl.collision_settings.use_self_collision = True
cl.collision_settings.distance_min = cl.collision_settings.self_distance_min = 0.004
cl.point_cache.frame_start, cl.point_cache.frame_end = 1, 60
sc.frame_set(1)
for fr in range(1, 61):
    sc.frame_set(fr)
with bpy.context.temp_override(object=throw, active_object=throw, selected_objects=[throw], scene=sc):
    bpy.ops.object.modifier_apply(modifier="Cloth")
sc.frame_set(1)
so = throw.modifiers.new("Knit", "SOLIDIFY")
so.thickness, so.use_even_offset = 0.008, False
throw.modifiers.new("Soft", "SUBSURF").levels = 1
zs = [(throw.matrix_world @ v.co).z for v in throw.data.vertices]
result = {"deko": len(dc.objects), "throw_z": [round(min(zs), 2), round(max(zs), 2)]}
