"""G7 (runs INSIDE Blender 5.2): build SM_R03_Workbench, the workbench of the R03 workshop.

Measure sheet docs/design/G7_FLUSSDORF_ASSETS.md: 2000 x 750 x 900 mm, 40 mm beech multiplex top,
grey powder-coated steel frame with lower shelf, 125 mm bench vise front left.
Origin floor centre, X = length, -Y = front (worker side), Z up.
Reference: ArtSource/Reference/G7/SM_R03_Workbench/front34_v1.png (FLUX.2 klein, seed 5).
"""
import bpy, bmesh, math, os
from mathutils import Vector

NAME = "SM_R03_Workbench"
COL = "G7_Workbench"
exec(compile(open(os.path.join(os.path.dirname(__file__), "g7_common.py"), encoding="utf8").read(), "g7_common.py", "exec"))

sc = bpy.context.scene
col = bpy.data.collections.get(COL)
if col:
    for o in list(col.all_objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    col = bpy.data.collections.new(COL)
    sc.collection.children.link(col)
for m in [m for m in bpy.data.materials if m.name.startswith("M_WB_")]:
    bpy.data.materials.remove(m)


def beech_multiplex(name):
    """Oiled beech multiplex: (macro) colour drift and darker oiled zones, (medium) oil stains,
    knife cuts, polished front edge, plywood plies on the cut edges, (micro) grain bump."""
    mat = bpy.data.materials.new(name)
    nt, bsdf = _nodes(mat)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    # grain: bands along X, distorted
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.25, 9.0, 9.0)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "Y"
    wave.inputs["Scale"].default_value = 2.2
    wave.inputs["Distortion"].default_value = 6.0
    wave.inputs["Detail"].default_value = 4.0
    wave.inputs["Detail Scale"].default_value = 1.6
    nt.links.new(mp.outputs["Vector"], wave.inputs["Vector"])
    grain = _range(nt, wave.outputs["Fac"], 0.2, 0.9, 0.0, 1.0)
    fleck = _noise(nt, 160.0, 4.0, 0.6)                       # beech pith flecks
    flk = _range(nt, fleck.outputs["Fac"], 0.62, 0.70, 0.0, 0.5)
    wood = _mix(nt, grain, (0.46, 0.28, 0.15), (0.33, 0.19, 0.095))
    wood = _mix(nt, flk, wood, (0.30, 0.16, 0.08))
    macro = _noise(nt, 1.4, 3.0, 0.5)
    wood = _mix(nt, _range(nt, macro.outputs["Fac"], 0.35, 0.65, 0.0, 0.55), wood, (0.26, 0.15, 0.075))
    # plies on vertical cut faces: alternating veneers every 2.7 mm
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    nsep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], nsep.inputs[0])
    absz = _add(nt, nsep.outputs["Z"], 0.0, "ABSOLUTE")
    side = _range(nt, absz, 0.5, 0.3, 0.0, 1.0)
    osep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], osep.inputs[0])
    ply = _add(nt, _add(nt, osep.outputs["Z"], 2 * math.pi / 0.0027, "MULTIPLY"), 0.0, "SINE")
    ply = _range(nt, ply, -0.2, 0.2, 0.0, 1.0)
    plies = _mix(nt, ply, (0.50, 0.33, 0.19), (0.30, 0.18, 0.09))
    wood = _mix(nt, side, wood, plies)
    # top-only wear: oil stains and knife cuts
    top = _range(nt, nsep.outputs["Z"], 0.6, 0.9, 0.0, 1.0)
    oil_n = _noise(nt, 3.5, 6.0, 0.62)
    oil = _add(nt, _range(nt, oil_n.outputs["Fac"], 0.60, 0.66, 0.0, 1.0), top, "MULTIPLY")
    wood = _mix(nt, _add(nt, oil, 0.85, "MULTIPLY"), wood, (0.07, 0.045, 0.025))
    cmp = nt.nodes.new("ShaderNodeMapping")
    cmp.inputs["Scale"].default_value = (3.0, 90.0, 3.0)
    cmp.inputs["Rotation"].default_value = (0.0, 0.0, 0.35)
    nt.links.new(tc.outputs["Object"], cmp.inputs["Vector"])
    cn = nt.nodes.new("ShaderNodeTexNoise")
    cn.inputs["Scale"].default_value = 2.0
    cn.inputs["Detail"].default_value = 1.0
    nt.links.new(cmp.outputs["Vector"], cn.inputs["Vector"])
    cuts = _add(nt, _range(nt, cn.outputs["Fac"], 0.66, 0.69, 0.0, 0.7), top, "MULTIPLY")
    wood = _mix(nt, cuts, wood, (0.55, 0.38, 0.23))
    # hand-polished front edge (y < -0.33 in object space)
    front = _range(nt, osep.outputs["Y"], -0.30, -0.37, 0.0, 1.0)
    cav = _cavity(nt, 0.03)
    wood = _mix(nt, _add(nt, cav, 0.6, "MULTIPLY"), wood, (0.05, 0.035, 0.02))
    nt.links.new(wood, bsdf.inputs["Base Color"])
    rn = _noise(nt, 40.0, 8.0, 0.6)
    r = _range(nt, rn.outputs["Fac"], 0.3, 0.7, 0.58, 0.72)
    r = _mix(nt, _add(nt, grain, 0.3, "MULTIPLY"), r, (0.78, 0.78, 0.78))
    r = _mix(nt, oil, r, (0.28, 0.28, 0.28))
    r = _mix(nt, front, r, (0.42, 0.42, 0.42))
    nt.links.new(r, bsdf.inputs["Roughness"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.0008
    nt.links.new(_add(nt, _add(nt, grain, 0.4, "MULTIPLY"), cuts, "SUBTRACT"), bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


M = {
    "wood": beech_multiplex("M_WB_BeechMultiplex"),
    "frame": paint_mat("M_WB_Frame_PaintGrey", (0.12, 0.125, 0.13), 0.48, dust=0.18),
    "vise": paint_mat("M_WB_Vise_CastIron", (0.035, 0.045, 0.06), 0.50, chip_metal=(0.30, 0.30, 0.30)),
    "steel": simple_mat("M_WB_SteelBright", (0.60, 0.61, 0.62), 0.32, metal=1.0, rough_var=0.10, bump=0.05),
    "rubber": simple_mat("M_WB_Rubber", (0.022, 0.022, 0.022), 0.86, rough_var=0.06, bump=0.08),
}

L, D, H, T = 2.0, 0.75, 0.90, 0.04
TOPZ = H - T / 2
parts = [box("Top", (L, D, T), (0, 0, TOPZ), "wood", bevel=0.003)]
# square tube 50 x 50 legs, inset so the top overhangs 60 mm at the ends and 40 mm front/back
LX, LY = L / 2 - 0.09, D / 2 - 0.065
LEG_H = H - T - 0.012
for i, (x, y) in enumerate([(-LX, -LY), (LX, -LY), (-LX, LY), (LX, LY)]):
    parts.append(box(f"Leg_{i}", (0.05, 0.05, LEG_H), (x, y, 0.012 + LEG_H / 2), "frame", bevel=0.003))
    parts.append(box(f"FootPlate_{i}", (0.07, 0.07, 0.006), (x, y, 0.015), "frame", bevel=0.0015))
    parts.append(cyl(f"Leveller_{i}", 0.022, 0.012, (x, y, 0.006), "rubber", verts=32, bevel=0.002))
# top apron (40 x 40) under the top, lower shelf frame at 150 mm
APZ = H - T - 0.02
for i, y in enumerate((-LY, LY)):
    parts.append(box(f"Apron_Long_{i}", (2 * LX, 0.04, 0.04), (0, y, APZ), "frame", bevel=0.0025))
    parts.append(box(f"Shelf_Long_{i}", (2 * LX, 0.04, 0.04), (0, y, 0.15), "frame", bevel=0.0025))
for i, x in enumerate((-LX, LX)):
    parts.append(box(f"Apron_Short_{i}", (0.04, 2 * LY, 0.04), (x, 0, APZ), "frame", bevel=0.0025))
    parts.append(box(f"Shelf_Short_{i}", (0.04, 2 * LY, 0.04), (x, 0, 0.15), "frame", bevel=0.0025))
parts.append(box("Shelf_Sheet", (2 * LX - 0.04, 2 * LY - 0.02, 0.0025), (0, 0, 0.1712), "frame", bevel=0.001))
for k in range(8):                                   # top fixing screws through the apron
    x = -LX + 0.12 + k * (2 * LX - 0.24) / 7
    parts.append(cyl(f"TopScrew_{k}", 0.0045, 0.003, (x, -LY - 0.0201, APZ), "steel", rot=(math.pi / 2, 0, 0), verts=16, bevel=0.0006))

# 125 mm bench vise, front left, fixed jaw flush with the front edge of the top
VX, VY, VZ = -0.72, -D / 2 + 0.02, H
parts.append(box("Vise_Base", (0.17, 0.20, 0.03), (VX, VY + 0.06, VZ + 0.015), "vise", bevel=0.006))
for k, (bx, by) in enumerate([(-0.06, 0.13), (0.06, 0.13), (-0.06, 0.0), (0.06, 0.0)]):
    parts.append(cyl(f"Vise_Bolt_{k}", 0.008, 0.008, (VX + bx, VY + by, VZ + 0.032), "steel", verts=6, bevel=0.001))
parts.append(box("Vise_FixedBody", (0.14, 0.07, 0.10), (VX, VY + 0.035, VZ + 0.08), "vise", bevel=0.008))
parts.append(box("Vise_Slide", (0.075, 0.20, 0.055), (VX, VY - 0.07, VZ + 0.06), "vise", bevel=0.006))
parts.append(box("Vise_MovingJaw", (0.14, 0.06, 0.09), (VX, VY - 0.10, VZ + 0.085), "vise", bevel=0.008))
for k, y in enumerate((VY - 0.002, VY - 0.068)):          # hardened jaw plates with grip grooves
    parts.append(box(f"Vise_JawPlate_{k}", (0.125, 0.008, 0.035), (VX, y, VZ + 0.112), "steel", bevel=0.0008))
    for g in range(10):
        parts.append(box(f"Vise_Groove_{k}_{g}", (0.125, 0.0012, 0.0012), (VX, y + (0.0042 if k == 1 else -0.0042), VZ + 0.098 + g * 0.003),
                         "vise", bevel=None))
parts.append(cyl("Vise_Spindle", 0.010, 0.10, (VX, VY - 0.17, VZ + 0.06), "steel", rot=(math.pi / 2, 0, 0), verts=24, bevel=0.001))
parts.append(cyl("Vise_SpindleBoss", 0.022, 0.03, (VX, VY - 0.205, VZ + 0.06), "vise", rot=(math.pi / 2, 0, 0), verts=32, bevel=0.003))
parts.append(cyl("Vise_Handle", 0.0065, 0.20, (VX, VY - 0.215, VZ + 0.06), "steel", rot=(0, math.pi / 2, 0.0), verts=16, bevel=0.0008))
for s in (-1, 1):
    parts.append(cyl(f"Vise_HandleKnob_{s}", 0.011, 0.016, (VX + 0.104 * s, VY - 0.215, VZ + 0.06), "steel", rot=(0, math.pi / 2, 0), verts=24, bevel=0.003))
parts.append(box("Vise_Anvil", (0.07, 0.05, 0.02), (VX, VY + 0.10, VZ + 0.14), "vise", bevel=0.004))

bench = join_parts(NAME, parts)
collision_box(NAME + "_00", (L, D, 0.045), (0, 0, TOPZ), bench)
collision_box(NAME + "_01", (2 * LX + 0.05, 2 * LY + 0.05, 0.18), (0, 0, 0.09), bench)
for i, (x, y) in enumerate([(-LX, -LY), (LX, -LY), (-LX, LY), (LX, LY)]):
    collision_box(f"{NAME}_{2 + i:02d}", (0.05, 0.05, H - T), (x, y, (H - T) / 2), bench)
collision_box(NAME + "_06", (0.17, 0.26, 0.15), (VX, VY - 0.05, VZ + 0.075), bench)
smart_uv(bench)
bench.location.x = 1.6          # stand next to the generator in the look-dev scene
bb = [bench.matrix_world @ Vector(c) for c in bench.bound_box]
dims = [round(max(v[i] for v in bb) - min(v[i] for v in bb), 4) for i in range(3)]
result = {"object": NAME, "dims_m": dims, "z_min": round(min(v.z for v in bb), 4),
          "tris": sum(len(p.vertices) - 2 for p in bench.data.polygons), "materials": [m.name for m in bench.data.materials]}
print("G7_WORKBENCH", result)
