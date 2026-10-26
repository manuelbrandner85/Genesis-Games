"""C00 (runs INSIDE Blender 5.2): SET_C00_SCHLAFZIMMER_2026 - small bedroom in a German new-build flat.

Approved look (GD-2026-10-24-02, reference wide_neubau_s64 / mood_00B_neubau / mood_00D_neubau_s66):
smooth white walls, flat ceiling, light oak laminate, large window with slim anthracite PVC frame and an
exterior roller shutter half down, flat panel radiator under the window, light grey curtain, modern bed
with upholstered headboard and white bedding, oak nightstand with warm lamp and an old picture frame
(seen from its back), a chair for the daughter at the bedside. Evening, rain.

Real dimensions (DIN new build): room 3.60 x 3.20 m, clear height 2.55 m; window 1.50 x 1.40 m, sill at
0.85 m; bed 1.40 x 2.00 m, mattress top 0.52 m (camera at bed edge height, ScriptLock 00-A).
Origin: room centre on the floor; +Y = headboard wall (north), +X = window wall (east).
"""
import bmesh
import bpy
import math
import os
from mathutils import Vector

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
COL = "C00_Schlafzimmer"
exec(compile(open(os.path.join(ROOT, "tools", "v4", "g7", "g7_common.py"), encoding="utf8").read(), "g7_common.py", "exec"))

W, D, H = 3.60, 3.20, 2.55          # inside dimensions
WALL = 0.175                         # masonry + plaster
WIN_W, WIN_H, SILL = 1.50, 1.40, 0.85
WIN_Y = 0.35                         # window centre on the east wall

sc = bpy.context.scene
col = bpy.data.collections.get(COL)
if col:
    for o in list(col.all_objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    col = bpy.data.collections.new(COL)
    sc.collection.children.link(col)
for m in [m for m in bpy.data.materials if m.name.startswith("M_SZ_")]:
    bpy.data.materials.remove(m)


# ---------------------------------------------------------------- materials
def paint(name, base, rough):
    """Matte wall paint: faint roller stipple and very soft tone variation."""
    mat = bpy.data.materials.new(name)
    nt, bsdf = _nodes(mat)
    macro = _noise(nt, 1.5, 3.0, 0.5)
    c = _mix(nt, _range(nt, macro.outputs["Fac"], 0.35, 0.65, 0.0, 1.0),
             tuple(x * 0.975 for x in base), base)
    nt.links.new(c, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    _micro_bump(nt, bsdf, 900.0, 0.02)
    return mat


def oak_laminate(name):
    """Light oak laminate, 19.3 x 138 cm planks with offset joints, grain along X."""
    mat = bpy.data.materials.new(name)
    nt, bsdf = _nodes(mat)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeMapping")
    sep.inputs["Scale"].default_value = (1 / 1.38, 1 / 0.193, 1.0)
    nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.offset = 0.37
    brick.offset_frequency = 1
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Mortar Size"].default_value = 0.004
    brick.inputs["Brick Width"].default_value = 1.0
    brick.inputs["Row Height"].default_value = 1.0
    brick.inputs["Color1"].default_value = (0.47, 0.33, 0.20, 1)
    brick.inputs["Color2"].default_value = (0.53, 0.38, 0.24, 1)
    brick.inputs["Mortar"].default_value = (0.20, 0.13, 0.08, 1)
    nt.links.new(sep.outputs["Vector"], brick.inputs["Vector"])
    wave = nt.nodes.new("ShaderNodeTexWave")                  # grain
    wave.wave_type = "BANDS"
    wave.bands_direction = "Y"
    wave.inputs["Scale"].default_value = 28.0
    wave.inputs["Distortion"].default_value = 9.0
    wave.inputs["Detail"].default_value = 6.0
    nt.links.new(tc.outputs["Object"], wave.inputs["Vector"])
    grain = _range(nt, wave.outputs["Fac"], 0.2, 0.9, 0.0, 1.0)
    c = _mix(nt, _add(nt, grain, 0.35, "MULTIPLY"), brick.outputs["Color"], (0.36, 0.24, 0.14))
    nt.links.new(c, bsdf.inputs["Base Color"])
    nt.links.new(_range(nt, grain, 0.0, 1.0, 0.38, 0.52), bsdf.inputs["Roughness"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.25
    bump.inputs["Distance"].default_value = 0.0008
    nt.links.new(brick.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def fabric(name, base, rough=0.85, sheen=0.4, scale=900.0):
    mat = bpy.data.materials.new(name)
    nt, bsdf = _nodes(mat)
    macro = _noise(nt, 6.0, 4.0, 0.5)
    c = _mix(nt, _range(nt, macro.outputs["Fac"], 0.3, 0.7, 0.0, 1.0),
             tuple(x * 0.94 for x in base), base)
    nt.links.new(c, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Sheen Weight"].default_value = sheen
    _micro_bump(nt, bsdf, scale, 0.05)
    return mat


M = {
    "wall": paint("M_SZ_WallWhite", (0.80, 0.79, 0.76), 0.9),
    "ceiling": paint("M_SZ_Ceiling", (0.82, 0.82, 0.80), 0.92),
    "floor": oak_laminate("M_SZ_OakLaminate"),
    "skirting": simple_mat("M_SZ_SkirtingWhite", (0.82, 0.82, 0.80), 0.45, grime=0.1),
    "pvc": simple_mat("M_SZ_PVCAnthracite", (0.055, 0.058, 0.062), 0.35, grime=0.1),
    "glass": clear_mat("M_SZ_Glass", (0.95, 0.97, 0.97), 0.02),
    "sill": simple_mat("M_SZ_SillWhite", (0.78, 0.78, 0.76), 0.25, grime=0.1),
    "radiator": simple_mat("M_SZ_RadiatorWhite", (0.80, 0.80, 0.78), 0.35, grime=0.15),
    "shutter": simple_mat("M_SZ_ShutterAlu", (0.06, 0.065, 0.07), 0.45, metal=1.0, grime=0.2),
    "curtain": fabric("M_SZ_CurtainGrey", (0.42, 0.42, 0.41), 0.9, 0.5),
    "upholstery": fabric("M_SZ_BedUpholstery", (0.30, 0.30, 0.31), 0.9, 0.6),
    "linen": fabric("M_SZ_BedLinenWhite", (0.78, 0.78, 0.76), 0.8, 0.3, 1400.0),
    "oak": simple_mat("M_SZ_OakVeneer", (0.42, 0.29, 0.17), 0.45, grime=0.2),
    "shade": fabric("M_SZ_LampShadeLinen", (0.85, 0.80, 0.70), 0.8, 0.2),
    "ceramic": simple_mat("M_SZ_LampCeramic", (0.62, 0.60, 0.56), 0.3, grime=0.1),
    "cardboard": simple_mat("M_SZ_FrameBack", (0.33, 0.24, 0.16), 0.9, grime=0.2),
    "frame": simple_mat("M_SZ_FrameWood", (0.20, 0.13, 0.08), 0.5, grime=0.2),
    "door": simple_mat("M_SZ_DoorWhite", (0.80, 0.80, 0.78), 0.35, grime=0.1),
    "steel": simple_mat("M_SZ_BrushedSteel", (0.55, 0.55, 0.56), 0.3, metal=1.0, grime=0.1),
    "switch": simple_mat("M_SZ_SwitchWhite", (0.84, 0.84, 0.82), 0.3, grime=0.05),
}

# ---------------------------------------------------------------- shell
parts = []
fl = box("SZ_Floor", (W, D, 0.02), (0, 0, -0.01), "floor", bevel=None)
parts.append(fl)
parts.append(box("SZ_Ceiling", (W, D, 0.02), (0, 0, H + 0.01), "ceiling", bevel=None))
# walls as slabs; the east wall is split around the window opening
parts.append(box("SZ_WallN", (W + 2 * WALL, WALL, H), (0, D / 2 + WALL / 2, H / 2), "wall", bevel=None))
parts.append(box("SZ_WallS", (W + 2 * WALL, WALL, H), (0, -D / 2 - WALL / 2, H / 2), "wall", bevel=None))
parts.append(box("SZ_WallW", (WALL, D, H), (-W / 2 - WALL / 2, 0, H / 2), "wall", bevel=None))
x_e = W / 2 + WALL / 2
y0, y1 = WIN_Y - WIN_W / 2, WIN_Y + WIN_W / 2
parts.append(box("SZ_WallE_S", (WALL, y0 + D / 2, H), (x_e, (y0 - D / 2) / 2, H / 2), "wall", bevel=None))
parts.append(box("SZ_WallE_N", (WALL, D / 2 - y1, H), (x_e, (y1 + D / 2) / 2, H / 2), "wall", bevel=None))
parts.append(box("SZ_WallE_Below", (WALL, WIN_W, SILL), (x_e, WIN_Y, SILL / 2), "wall", bevel=None))
top = SILL + WIN_H
parts.append(box("SZ_WallE_Above", (WALL, WIN_W, H - top), (x_e, WIN_Y, (H + top) / 2), "wall", bevel=None))
# skirting boards 6 cm
for name, size, loc in (("N", (W, 0.012, 0.06), (0, D / 2 - 0.006, 0.03)), ("S", (W, 0.012, 0.06), (0, -D / 2 + 0.006, 0.03)),
                        ("W", (0.012, D, 0.06), (-W / 2 + 0.006, 0, 0.03)), ("E", (0.012, D, 0.06), (W / 2 - 0.006, 0, 0.03))):
    parts.append(box("SZ_Skirting" + name, size, loc, "skirting", bevel=0.002))

# ---------------------------------------------------------------- window (east)
FX = W / 2 + 0.06                    # frame plane inside the reveal
fr = 0.075                           # PVC profile width
for name, size, loc in (("Top", (0.07, WIN_W, fr), (FX, WIN_Y, top - fr / 2)), ("Bot", (0.07, WIN_W, fr), (FX, WIN_Y, SILL + fr / 2)),
                        ("L", (0.07, fr, WIN_H), (FX, y0 + fr / 2, SILL + WIN_H / 2)), ("R", (0.07, fr, WIN_H), (FX, y1 - fr / 2, SILL + WIN_H / 2)),
                        ("Mid", (0.07, fr * 0.9, WIN_H - 2 * fr), (FX, WIN_Y, SILL + WIN_H / 2))):
    parts.append(box("SZ_WinFrame" + name, size, loc, "pvc", bevel=0.003))
for k, yc in enumerate((WIN_Y - WIN_W / 4, WIN_Y + WIN_W / 4)):
    pane = box(f"SZ_Glass{k}", (0.008, WIN_W / 2 - fr * 1.2, WIN_H - 2 * fr), (FX, yc, SILL + WIN_H / 2), "glass", bevel=None)
    pane["glass"] = True
parts.append(box("SZ_WinHandle", (0.03, 0.012, 0.11), (FX - 0.05, WIN_Y + 0.06, SILL + WIN_H / 2), "steel", bevel=0.003))
parts.append(box("SZ_InnerSill", (0.20, WIN_W + 0.06, 0.02), (W / 2 + 0.005 - 0.07, WIN_Y, SILL + 0.01), "sill", bevel=0.002))
# exterior roller shutter, half down: slats outside the glass
SH_X = W / 2 + WALL - 0.02
for i in range(int(0.60 / 0.039)):
    z = top - 0.03 - i * 0.039
    s = box(f"SZ_Slat{i:02d}", (0.012, WIN_W + 0.04, 0.036), (SH_X, WIN_Y, z), "shutter", bevel=0.004)
    parts.append(s)
parts.append(box("SZ_ShutterBox", (0.02, WIN_W + 0.10, 0.20), (SH_X, WIN_Y, top + 0.10), "shutter", bevel=0.004))

# ---------------------------------------------------------------- radiator (flat panel, type 22)
parts.append(box("SZ_Radiator", (0.10, 1.20, 0.60), (W / 2 - 0.09, WIN_Y, 0.15 + 0.30), "radiator", bevel=0.006))
for k in range(30):                                           # vertical profile lines on the front panel
    parts.append(box(f"SZ_RadRib{k}", (0.004, 0.006, 0.56), (W / 2 - 0.142, WIN_Y - 0.58 + k * 0.04, 0.45), "radiator", bevel=None))

# ---------------------------------------------------------------- curtain (pleated panel left of the window)
def curtain(name, y_center, width, folds=9):
    bm = bmesh.new()
    nu, nv = 60, 24
    verts = []
    for j in range(nv + 1):
        z = 0.02 + (top + 0.12 - 0.02) * j / nv
        row = []
        for i in range(nu + 1):
            u = i / nu
            y = y_center - width / 2 + width * u
            x = W / 2 - 0.16 + 0.035 * math.sin(u * folds * 2 * math.pi) * (0.8 + 0.2 * (1 - j / nv))
            row.append(bm.verts.new((x, y, z)))
        verts.append(row)
    for j in range(nv):
        for i in range(nu):
            bm.faces.new((verts[j][i], verts[j][i + 1], verts[j + 1][i + 1], verts[j + 1][i]))
    o = _obj(name, bm, "curtain", bevel=None)
    sol = o.modifiers.new("Fabric", "SOLIDIFY")
    sol.thickness = 0.002
    return o


parts.append(curtain("SZ_CurtainL", y0 - 0.25, 0.55))
parts.append(curtain("SZ_CurtainR", y1 + 0.25, 0.55))
parts.append(cyl("SZ_CurtainRod", 0.010, W - 0.4, (W / 2 - 0.16, WIN_Y, top + 0.16), "steel", rot=(math.pi / 2, 0, 0)))

# ---------------------------------------------------------------- bed (1.40 x 2.10 comfort length, headboard north)
# Regie 2026-10-25: 2.10 m - the man lies ~1.88 m from crown to pointed toes, plus the pillow at the headboard
BX, BY0 = -0.25, D / 2 - 0.03                   # bed centre x, headboard face y
parts.append(box("SZ_BedBase", (1.50, 2.18, 0.30), (BX, BY0 - 1.09, 0.15 + 0.03), "upholstery", bevel=0.02))
for fx in (-0.65, 0.65):
    for fy in (-0.08, -2.08):
        parts.append(cyl(f"SZ_BedFoot{fx}{fy}", 0.02, 0.06, (BX + fx, BY0 + fy, 0.03), "oak"))
parts.append(box("SZ_Headboard", (1.56, 0.10, 0.75), (BX, BY0 - 0.05, 0.33 + 0.375), "upholstery", bevel=0.035))
parts.append(box("SZ_Mattress", (1.40, 2.10, 0.20), (BX, BY0 - 0.10 - 1.05, 0.33 + 0.10), "linen", bevel=0.04))
# duvet: soft slab over 2/3 of the mattress, hanging over the sides a little
duv = box("SZ_Duvet", (1.52, 1.40, 0.08), (BX, BY0 - 0.10 - 1.32, 0.53 + 0.035), "linen", bevel=0.035)
sub = duv.modifiers.new("Soft", "SUBSURF")
sub.levels = sub.render_levels = 2
parts.append(duv)
for px in (-0.36, 0.36):
    p = box(f"SZ_Pillow{px}", (0.62, 0.40, 0.14), (BX + px, BY0 - 0.32, 0.53 + 0.07), "linen", bevel=0.05)
    sp = p.modifiers.new("Soft", "SUBSURF")
    sp.levels = sp.render_levels = 2
    parts.append(p)

# ---------------------------------------------------------------- nightstand, lamp, picture frame (window side)
NX, NY = BX + 0.75 + 0.27, D / 2 - 0.22
parts.append(box("SZ_Nightstand", (0.45, 0.38, 0.50), (NX, NY, 0.06 + 0.25), "oak", bevel=0.004))
parts.append(box("SZ_NightstandDrawerGap", (0.42, 0.004, 0.003), (NX, NY - 0.191, 0.45), "frame", bevel=None))
for fx in (-0.19, 0.19):
    for fy in (-0.15, 0.15):
        parts.append(cyl(f"SZ_NSLeg{fx}{fy}", 0.012, 0.06, (NX + fx, NY + fy, 0.03), "oak", r2=0.008))
parts.append(cyl("SZ_LampBase", 0.065, 0.24, (NX + 0.10, NY + 0.06, 0.56 + 0.12), "ceramic", r2=0.045))
parts.append(cyl("SZ_LampShade", 0.16, 0.20, (NX + 0.10, NY + 0.06, 0.80 + 0.10), "shade", r2=0.12, verts=48))
# old picture frame on the nightstand, turned so the camera at the bed sees only its back (ScriptLock 1.3, 00-B).
# CR-004 (draft, Game Director 2026-10-25): books instead of the photograph - set to True to restore it
NIGHTSTAND_PHOTO = False
if NIGHTSTAND_PHOTO:
    fr_obj = box("SZ_PhotoFrame", (0.13, 0.018, 0.18), (NX - 0.11, NY - 0.06, 0.56 + 0.09), "frame", bevel=0.003,
                 rot=(math.radians(-12), 0, math.radians(200)))
    parts.append(fr_obj)
    parts.append(box("SZ_PhotoBack", (0.115, 0.004, 0.165), (NX - 0.11 - 0.003, NY - 0.06 - 0.010, 0.56 + 0.09), "cardboard",
                     bevel=None, rot=(math.radians(-12), 0, math.radians(200))))

# ---------------------------------------------------------------- chair for the daughter (bedside, window side)
CX, CY = BX + 0.95, -0.15
parts.append(box("SZ_ChairSeat", (0.44, 0.42, 0.04), (CX, CY, 0.46), "oak", bevel=0.006))
parts.append(box("SZ_ChairBack", (0.44, 0.03, 0.42), (CX, CY - 0.20, 0.46 + 0.23), "oak", bevel=0.006, rot=(math.radians(-8), 0, 0)))
for fx in (-0.19, 0.19):
    for fy in (-0.18, 0.18):
        parts.append(cyl(f"SZ_ChairLeg{fx}{fy}", 0.015, 0.44, (CX + fx, CY + fy, 0.22), "oak", r2=0.012))

# ---------------------------------------------------------------- door (west wall, south), switch, sockets, ceiling light
parts.append(box("SZ_Door", (0.04, 0.86, 2.01), (-W / 2 + 0.03, -D / 2 + 0.70, 1.005), "door", bevel=0.003))
parts.append(box("SZ_DoorFrame", (0.06, 0.98, 2.08), (-W / 2 + 0.035, -D / 2 + 0.70, 1.04), "door", bevel=0.004))
parts.append(cyl("SZ_DoorHandle", 0.010, 0.13, (-W / 2 + 0.075, -D / 2 + 0.36, 1.05), "steel", rot=(math.pi / 2, 0, 0)))
parts.append(box("SZ_Switch", (0.012, 0.08, 0.08), (-W / 2 + 0.006, -D / 2 + 1.25, 1.05), "switch", bevel=0.004))
for sx in (NX - 0.30, BX - 0.95):
    parts.append(box(f"SZ_Socket{sx:.2f}", (0.08, 0.012, 0.08), (sx, D / 2 - 0.006, 0.30), "switch", bevel=0.004))
parts.append(cyl("SZ_CeilingLight", 0.17, 0.06, (0, -0.1, H - 0.03), "shade", verts=48))

result = {"objects": len(col.all_objects), "materials": len(M)}
