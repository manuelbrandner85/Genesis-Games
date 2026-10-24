"""G7 (runs INSIDE Blender 5.2): set dressing of the R03 workshop, after the mood reference
ArtSource/Reference/G7/R03_Werkstatt_Mood/interior_v1.png (FLUX.2 klein, seed 21).

Three static meshes, all with the room origin (Unreal 5050/0/0, placed like SM_R03_Room):
  SM_R03_ToolWall    perforated steel tool board with hanging tools, wall shelf with tubs, jars and
                     an oil tin, electrical box with Schuko socket and conduit (north wall, over the bench)
  SM_R03_BenchItems  battery charger, radio (the source's optional diegetic motif), screw jar, screwdrivers,
                     rag, spark-plug box on the bench top (0.90 m)
  SM_R03_FloorItems  tool trolley, two 20 l jerrycans next to the generator, cable reel with a cable run,
                     bucket, oil drain pan, cardboard under the generator, broom
Unreal-local coordinates in metres go through ue() (Blender Y = -Unreal Y). No brand names, no text.
Items people could walk into get simple UCX boxes; bench and wall items do not.
"""
import bpy, bmesh, math, os, random
from mathutils import Vector

ROOT = os.path.dirname(__file__)
exec(compile(open(os.path.join(ROOT, "g7_common.py"), encoding="utf8").read(), "g7_common.py", "exec"))
sc = bpy.context.scene
col = bpy.data.collections.get("G7_Dressing")
if col:
    for o in list(col.all_objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    col = bpy.data.collections.new("G7_Dressing")
    sc.collection.children.link(col)
for m in [m for m in bpy.data.materials if m.name.startswith("M_DR_")]:
    bpy.data.materials.remove(m)
rnd = random.Random(2026)


def ue(x, y, z):
    return (x, -y, z)


def rz(deg):
    """Unreal yaw -> Blender rotation_euler (mirrored Y flips the sense of rotation)."""
    return (0.0, 0.0, math.radians(-deg))


def perforated(name, base, rough, metal=1.0, scale=40.0):
    mat = simple_mat(name, base, rough, metal=metal, rough_var=0.10, bump=0.05)
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.voronoi_dimensions = "3D"
    vor.inputs["Scale"].default_value = scale
    vor.inputs["Randomness"].default_value = 0.0
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    hole = _range(nt, vor.outputs["Distance"], 0.20, 0.24, 1.0, 0.0)
    nt.links.new(_mix(nt, hole, bsdf.inputs["Base Color"].links[0].from_socket, (0.01, 0.01, 0.01)), bsdf.inputs["Base Color"])
    return mat


M = {
    "board": simple_mat("M_DR_PegboardZinc", (0.48, 0.49, 0.50), 0.52, metal=1.0, rough_var=0.06, bump=0.03),   # holes are geometry now
    "steel": simple_mat("M_DR_ToolSteel", (0.62, 0.63, 0.64), 0.30, metal=1.0, rough_var=0.12, bump=0.04),
    "chrome": simple_mat("M_DR_ChromeVanadium", (0.55, 0.56, 0.56), 0.18, metal=1.0, rough_var=0.08, bump=0.02),
    "red": paint_mat("M_DR_PaintRed", (0.42, 0.035, 0.025), 0.40, dust=0.3),
    "green": paint_mat("M_DR_PaintGreen", (0.04, 0.12, 0.05), 0.42, dust=0.3),
    "yellow": paint_mat("M_DR_PaintYellow", (0.62, 0.42, 0.04), 0.38, dust=0.3),
    "grey": paint_mat("M_DR_PaintGrey", (0.16, 0.165, 0.17), 0.45, dust=0.3),
    "black": simple_mat("M_DR_PlasticBlack", (0.03, 0.03, 0.032), 0.50, rough_var=0.10, bump=0.03),
    "grip_red": simple_mat("M_DR_GripRed", (0.40, 0.03, 0.02), 0.55, rough_var=0.08, bump=0.06),
    "grip_blue": simple_mat("M_DR_GripBlue", (0.03, 0.08, 0.30), 0.55, rough_var=0.08, bump=0.06),
    "grip_yellow": simple_mat("M_DR_GripYellow", (0.60, 0.40, 0.03), 0.50, rough_var=0.08, bump=0.06),
    "wood": simple_mat("M_DR_AshHandle", (0.42, 0.28, 0.15), 0.55, rough_var=0.10, bump=0.10),
    "tub": simple_mat("M_DR_ClearTubPlastic", (0.80, 0.80, 0.78), 0.35, rough_var=0.08, bump=0.02, grime=0.3),
    "jar": clear_mat("M_DR_ClearJarGlass", (0.95, 0.96, 0.93), 0.05),
    "card": simple_mat("M_DR_Cardboard", (0.31, 0.20, 0.10), 0.86, rough_var=0.05, bump=0.18, grime=0.5),
    "cloth": simple_mat("M_DR_RagCloth", (0.30, 0.27, 0.22), 0.92, rough_var=0.04, bump=0.25, grime=0.8),
    "cable": simple_mat("M_DR_CableOrange", (0.55, 0.16, 0.02), 0.45, rough_var=0.08, bump=0.02),
    "cable_blk": simple_mat("M_DR_CableBlack", (0.025, 0.025, 0.025), 0.45, rough_var=0.08, bump=0.02),
    "rubber": simple_mat("M_DR_Rubber", (0.022, 0.022, 0.022), 0.86, rough_var=0.06, bump=0.08),
    "oil": simple_mat("M_DR_UsedOil", (0.012, 0.009, 0.006), 0.04, rough_var=0.01, bump=0.0, grime=0.0),
    "screws": simple_mat("M_DR_ScrewsZinc", (0.55, 0.56, 0.57), 0.40, metal=1.0, rough_var=0.15, bump=0.6),
    "white": simple_mat("M_DR_PlasticWhite", (0.70, 0.70, 0.67), 0.45, rough_var=0.08, bump=0.02),
    "bristle": simple_mat("M_DR_Bristles", (0.12, 0.09, 0.05), 0.85, rough_var=0.05, bump=0.4),
}


# --- small tool builders (each returns objects; local frame: hangs/lies along +Z/+X) ---------------
def wrench(tag, loc, L, rot):
    """Combination spanner: tapered shank, closed ring end (12-point opening) and open jaw end."""
    w = 0.016 * L / 0.2
    out = [box(f"{tag}_Bar", (0.004, w, L - 0.03), (0, 0, 0), "chrome", bevel=0.001)]
    out.append(ring(f"{tag}_Ring", w * 0.95 + 0.004, w * 0.55, 0.007, (0, 0, L / 2), "chrome"))
    jaw_h = 0.03 * L / 0.2
    for s in (-1, 1):                                    # two jaw prongs around an open gap
        out.append(box(f"{tag}_Jaw{s}", (0.006, w * 0.45, jaw_h), (0, s * w * 0.62, -L / 2 - jaw_h * 0.25), "chrome", bevel=0.001,
                       rot=(s * 0.25, 0, 0)))
    out.append(box(f"{tag}_JawBase", (0.006, w * 1.6, jaw_h * 0.35), (0, 0, -L / 2 + jaw_h * 0.2), "chrome", bevel=0.001))
    return place(out, loc, rot)


def screwdriver(tag, loc, grip, rot):
    out = [fluted(f"{tag}_Grip", 0.014, 0.10, (0, 0, 0.05), grip),
           cyl(f"{tag}_Ferrule", 0.006, 0.012, (0, 0, -0.006), "chrome", verts=12, bevel=0.0008),
           cyl(f"{tag}_Shaft", 0.0028, 0.13, (0, 0, -0.07), "chrome", verts=8, bevel=0.0)]
    return place(out, loc, rot)


def pliers(tag, loc, grip, rot):
    out = []
    for s in (-1, 1):
        out.append(box(f"{tag}_Arm{s}", (0.004, 0.012, 0.13), (0, s * 0.012, -0.04), grip, bevel=0.002, rot=(s * 0.12, 0, 0)))
        out.append(box(f"{tag}_Jaw{s}", (0.005, 0.009, 0.06), (0, s * 0.004, 0.07), "chrome", bevel=0.001, rot=(-s * 0.06, 0, 0)))
    out.append(cyl(f"{tag}_Pivot", 0.006, 0.008, (0, 0, 0.035), "chrome", rot=(0, math.pi / 2, 0), verts=12, bevel=0.0))
    return place(out, loc, rot)


WALL_N = 2.76        # inner face of the north wall (Unreal local y)
TOP = 0.90           # bench top

# ================================================================== tool wall (north wall over the bench)
tw = []
BY = WALL_N - 0.025                            # board 25 mm off the wall on spacers
tw.append(perforated_sheet("Board", 1.20, 0.60, ue(0.80, BY, 1.42), "board"))
for k, (bx, bz) in enumerate([(0.22, 1.14), (1.38, 1.14), (0.22, 1.70), (1.38, 1.70)]):
    tw.append(cyl(f"Spacer_{k}", 0.008, 0.024, ue(bx, WALL_N - 0.012, bz), "steel", rot=(math.pi / 2, 0, 0), verts=12, bevel=0.0))
hook_y = BY - 0.02
grips = ["grip_red", "grip_blue", "grip_yellow", "grip_red"]
for k, L in enumerate((0.16, 0.19, 0.22, 0.25)):                      # combination wrenches 10-19 mm
    x = 0.32 + k * 0.07
    tw.append(cyl(f"Hook_W{k}", 0.002, 0.03, ue(x, BY - 0.015, 1.66), "steel", rot=(math.pi / 2, 0, 0), verts=6, bevel=0.0))
    tw += wrench(f"Wrench{k}", ue(x, hook_y, 1.66 - L / 2), L, rz(0))
for k in range(4):                                                    # screwdrivers in a strip
    x = 0.72 + k * 0.045
    tw += screwdriver(f"Screwdriver{k}", ue(x, hook_y, 1.55), grips[k], (0, 0, 0))
tw.append(box("ScrewdriverRack", (0.20, 0.03, 0.012), ue(0.79, BY - 0.015, 1.60), "steel", bevel=0.001))
for k, g in enumerate(("grip_red", "grip_blue")):                     # pliers
    tw.append(cyl(f"Hook_P{k}", 0.002, 0.03, ue(1.00 + k * 0.08, BY - 0.015, 1.62), "steel", rot=(math.pi / 2, 0, 0), verts=6, bevel=0.0))
    tw += pliers(f"Pliers{k}", ue(1.00 + k * 0.08, hook_y, 1.53), g, rz(0) if k == 0 else (0, 0.08, 0))
tw.append(box("Hammer_Handle", (0.03, 0.022, 0.30), ue(1.27, hook_y, 1.40), "wood", bevel=0.004))
tw.append(box("Hammer_Head", (0.11, 0.028, 0.03), ue(1.27, hook_y, 1.56), "steel", bevel=0.004))
# wall shelf with brackets
tw.append(box("Shelf", (1.50, 0.25, 0.02), ue(0.75, WALL_N - 0.125, 1.95), "steel", bevel=0.002))
for k, bx in enumerate((0.10, 1.40)):
    tw.append(box(f"Bracket_{k}", (0.004, 0.22, 0.20), ue(bx, WALL_N - 0.11, 1.84), "grey", bevel=0.001))
for k, (sx, w) in enumerate([(0.15, 0.20), (0.40, 0.24), (0.68, 0.20)]):   # clear parts tubs
    tw.append(box(f"Tub_{k}", (w, 0.16, 0.09), ue(sx, WALL_N - 0.12, 2.005), "tub", bevel=0.006))
    for j in range(5):
        tw.append(cyl(f"Tub_{k}_Part{j}", 0.006, 0.02, ue(sx + rnd.uniform(-w / 3, w / 3), WALL_N - 0.12 + rnd.uniform(-0.05, 0.05), 2.04),
                      "screws", rot=(rnd.uniform(0, 3), rnd.uniform(0, 3), 0), verts=8, bevel=0.0))
tw.append(cyl("OilTin", 0.055, 0.17, ue(0.95, WALL_N - 0.12, 2.045), "yellow", verts=32, bevel=0.003))
tw.append(cyl("OilTin_Cap", 0.014, 0.02, ue(0.98, WALL_N - 0.12, 2.14), "black", verts=16, bevel=0.002))
for k, jx in enumerate((1.12, 1.24)):
    tw.append(cyl(f"Jar_{k}", 0.045, 0.12, ue(jx, WALL_N - 0.12, 2.02), "jar", verts=32, bevel=0.004))
    tw.append(cyl(f"Jar_{k}_Screws", 0.040, 0.07, ue(jx, WALL_N - 0.12, 1.995), "screws", verts=24, bevel=0.0))
    tw.append(cyl(f"Jar_{k}_Lid", 0.047, 0.015, ue(jx, WALL_N - 0.12, 2.087), "red", verts=32, bevel=0.002))
tw.append(box("Shelf_Carton", (0.18, 0.15, 0.12), ue(1.40, WALL_N - 0.12, 2.02), "card", bevel=0.003))
# electrical box, Schuko socket, conduit to the ceiling
EX = -0.30
tw.append(box("ElecBox", (0.16, 0.06, 0.22), ue(EX, WALL_N - 0.03, 1.25), "white", bevel=0.006))
tw.append(box("SocketPlate", (0.08, 0.012, 0.08), ue(EX, WALL_N - 0.066, 1.20), "white", bevel=0.004))
tw.append(cyl("SocketWell", 0.0195, 0.006, ue(EX, WALL_N - 0.074, 1.20), "grey", rot=(math.pi / 2, 0, 0), verts=24, bevel=0.0))
tw.append(box("Switch", (0.05, 0.012, 0.05), ue(EX, WALL_N - 0.066, 1.31), "white", bevel=0.003))
tw.append(cyl("Conduit", 0.010, 3.46 - 1.36, ue(EX, WALL_N - 0.012, 1.36 + (3.46 - 1.36) / 2), "grey", verts=12, bevel=0.0))
for k in range(4):
    tw.append(box(f"ConduitClip_{k}", (0.03, 0.024, 0.015), ue(EX, WALL_N - 0.012, 1.55 + k * 0.5), "steel", bevel=0.001))
# charger lead from the socket down to the bench
tw.append(tube("ChargerLead", [Vector(ue(EX, WALL_N - 0.08, 1.20)), Vector(ue(EX + 0.05, WALL_N - 0.10, 1.05)),
                               Vector(ue(1.05, WALL_N - 0.12, 0.95)), Vector(ue(1.15, WALL_N - 0.20, TOP + 0.04))], 0.004, "cable_blk"))
toolwall = join_parts("SM_R03_ToolWall", tw)

# ================================================================== bench items
bi = []
bi.append(box("Charger", (0.22, 0.14, 0.10), ue(1.18, 2.48, TOP + 0.05), "grey", bevel=0.008))
for k in range(2):
    bi.append(cyl(f"Charger_Knob{k}", 0.010, 0.012, ue(1.12 + k * 0.08, 2.408, TOP + 0.06), "black", rot=(math.pi / 2, 0, 0), verts=16, bevel=0.002))
bi.append(box("Charger_Meter", (0.06, 0.004, 0.035), ue(1.18, 2.408, TOP + 0.075), "jar", bevel=0.001))
for s, c in ((-1, "red"), (1, "black")):
    bi.append(tube(f"Clamp_Lead{s}", [Vector(ue(1.10 + s * 0.03, 2.41, TOP + 0.03)), Vector(ue(1.00 + s * 0.05, 2.30, TOP + 0.01)),
                                      Vector(ue(0.95 + s * 0.06, 2.22, TOP + 0.008))], 0.0035, "cable_blk"))
    bi.append(box(f"Clamp{s}", (0.07, 0.02, 0.018), ue(0.93 + s * 0.06, 2.20, TOP + 0.01), c, bevel=0.003, rot=rz(30 * s)))
bi.append(box("Radio", (0.24, 0.09, 0.15), ue(0.62, 2.62, TOP + 0.075), "black", bevel=0.01, rot=rz(-8)))
bi.append(box("Radio_Grille", (0.11, 0.002, 0.10), ue(0.58, 2.575, TOP + 0.075), "board", bevel=0.0005, rot=rz(-8)))
bi.append(cyl("Radio_Antenna", 0.002, 0.35, ue(0.72, 2.64, TOP + 0.31), "chrome", rot=(0.25, 0, 0), verts=6, bevel=0.0))
bi.append(cyl("ScrewJar", 0.05, 0.13, ue(0.05, 2.25, TOP + 0.065), "jar", verts=32, bevel=0.004))
bi.append(cyl("ScrewJar_Fill", 0.045, 0.08, ue(0.05, 2.25, TOP + 0.04), "screws", verts=24, bevel=0.0))
for k in range(3):
    bi += screwdriver(f"BenchScrewdriver{k}", ue(0.30 + k * 0.05, 2.20 - k * 0.02, TOP + 0.015), grips[k], (math.pi / 2, 0, math.radians(80 + k * 9)))
rag = bmesh.new()                                   # crumpled shop rag: subdivided plane, displaced
bmesh.ops.create_grid(rag, x_segments=24, y_segments=24, size=0.17)
for v in rag.verts:
    r = (v.co.x ** 2 + v.co.y ** 2) ** 0.5
    v.co.z = max(0.0, 0.05 - r * 0.22) + 0.008 * math.sin(v.co.x * 60) * math.cos(v.co.y * 47) + rnd.uniform(0, 0.004)
bi.append(_obj("Rag", rag, "cloth", ue(0.82, 2.18, TOP + 0.002), rz(15), bevel=None))
bi.append(box("PlugBox", (0.06, 0.03, 0.10), ue(1.40, 2.20, TOP + 0.05), "card", bevel=0.002, rot=rz(-20)))
bi.append(box("OldPlug_Body", (0.02, 0.02, 0.02), ue(1.30, 2.14, TOP + 0.01), "chrome", bevel=0.002))
benchitems = join_parts("SM_R03_BenchItems", bi)

# ================================================================== floor items
fi, fucx = [], []


def fbox(name, size, c, mat, rot=(0, 0, 0), collide=True, bevel=0.004):
    o = box(name, size, c, mat, bevel=bevel, rot=rot)
    fi.append(o)
    if collide:
        fucx.append((size, c, rot))
    return o


# tool trolley, 3 drawers, west of the bench against the north wall
TX, TY = -1.05, 2.48
fbox("Trolley_Body", (0.68, 0.46, 0.72), ue(TX, TY, 0.48), "red")
for k in range(3):
    fi.append(box(f"Trolley_Drawer{k}", (0.62, 0.006, 0.20), ue(TX, TY - 0.233, 0.30 + k * 0.23), "red", bevel=0.002))
    fi.append(box(f"Trolley_Handle{k}", (0.40, 0.02, 0.012), ue(TX, TY - 0.245, 0.37 + k * 0.23), "chrome", bevel=0.002))
fi.append(box("Trolley_Top", (0.70, 0.48, 0.02), ue(TX, TY, 0.85), "black", bevel=0.004))
for k, (dx, dy) in enumerate([(-0.29, -0.18), (0.29, -0.18), (-0.29, 0.18), (0.29, 0.18)]):
    fi.append(cyl(f"Trolley_Caster{k}", 0.05, 0.035, ue(TX + dx, TY + dy, 0.05), "rubber", rot=(math.pi / 2, 0, 0), verts=24, bevel=0.004))
    fi.append(box(f"Trolley_Fork{k}", (0.04, 0.05, 0.06), ue(TX + dx, TY + dy, 0.10), "chrome", bevel=0.002))
fi.append(box("Trolley_Toolbox", (0.42, 0.20, 0.16), ue(TX - 0.08, TY + 0.02, 0.94), "grey", bevel=0.01))
# two 20 l jerrycans (fuel red, diesel green) by the south wall next to the generator: rounded pressed
# body (470 x 345 x 165 mm), embossed X ribs on both faces, three-bar handle, spout with lever cap
for k, (cx, mat) in enumerate(((1.35, "red"), (1.72, "green"))):
    yaw = rnd.uniform(-6, 6)
    c = Vector(ue(cx, -2.58, 0.235))
    parts_k = [box(f"Jerrycan{k}_Body", (0.345, 0.165, 0.43), (0, 0, -0.02), mat, bevel=0.018)]
    for side in (-1, 1):
        for d in (-1, 1):                                   # X ribs, 6 mm proud
            parts_k.append(box(f"Jerrycan{k}_Rib{side}{d}", (0.40, 0.006, 0.022), (0, side * 0.0855, -0.02), mat, bevel=0.003,
                               rot=(0, d * math.atan2(0.36, 0.28), 0)))
        parts_k.append(box(f"Jerrycan{k}_Seam{side}", (0.35, 0.004, 0.012), (0, side * 0.084, 0.19), mat, bevel=0.001))
    for h in range(3):                                      # handle bars between top and the raised grip
        parts_k.append(box(f"Jerrycan{k}_Post{h}", (0.022, 0.03, 0.045), (-0.10 + h * 0.08, 0, 0.215), mat, bevel=0.005))
    parts_k.append(box(f"Jerrycan{k}_Grip", (0.20, 0.03, 0.024), (-0.02, 0, 0.245), mat, bevel=0.008))
    parts_k.append(cyl(f"Jerrycan{k}_Neck", 0.026, 0.03, (0.13, 0, 0.21), mat, verts=24, bevel=0.003))
    parts_k.append(cyl(f"Jerrycan{k}_Cap", 0.030, 0.022, (0.13, 0, 0.235), "black", verts=24, bevel=0.004))
    parts_k.append(box(f"Jerrycan{k}_Lever", (0.07, 0.012, 0.008), (0.10, 0, 0.25), "chrome", bevel=0.002))
    fi += place(parts_k, tuple(c), rz(yaw))
    fucx.append(((0.35, 0.17, 0.47), tuple(c), rz(yaw)))
# cable reel in the north-east corner and the cable running to the bench
RX, RY = 2.75, 2.45
fucx.append(((0.30, 0.26, 0.36), ue(RX, RY, 0.18), (0, 0, 0)))          # collision only: open tube frame
for s in (-1, 1):                                       # side plates + carrying bow
    fi.append(cyl(f"Reel_Side{s}", 0.15, 0.008, ue(RX + s * 0.095, RY, 0.20), "black", rot=(0, math.pi / 2, 0), verts=40, bevel=0.002))
    fi.append(box(f"Reel_Foot{s}", (0.02, 0.26, 0.02), ue(RX + s * 0.095, RY, 0.01), "black", bevel=0.003))
fi.append(tube("Reel_Bow", [Vector(ue(RX - 0.095, RY, 0.33)), Vector(ue(RX - 0.095, RY, 0.40)), Vector(ue(RX + 0.095, RY, 0.40)),
                            Vector(ue(RX + 0.095, RY, 0.33))], 0.009, "black"))
for k in range(5):
    fi.append(cyl(f"Reel_Wind{k}", 0.13 - k * 0.004, 0.17, ue(RX, RY, 0.20), "cable", rot=(0, math.pi / 2, 0), verts=40, bevel=0.01))
fi.append(cyl("Reel_Hub", 0.05, 0.03, ue(RX + 0.10, RY, 0.20), "black", rot=(0, math.pi / 2, 0), verts=24, bevel=0.004))
run = [Vector(ue(RX - 0.12, RY - 0.05, 0.10))]
for k in range(1, 9):                                   # lying cable, gentle S-curves on the floor
    t = k / 8
    run.append(Vector(ue(RX - 0.12 - t * 1.25, RY - 0.25 - 0.25 * math.sin(t * math.pi * 1.5), 0.012)))
run.append(Vector(ue(1.45, 2.20, 0.40)))
run.append(Vector(ue(1.40, 2.35, TOP - 0.02)))
fi.append(tube("Reel_Cable", run, 0.0045, "cable"))
# bucket and oil drain pan in the south-west corner, cardboard under the generator, broom
fbox("Bucket", (0.30, 0.30, 0.30), ue(-2.85, -2.42, 0.15), "grey", collide=True, bevel=0.01)
fi.pop()                                               # replace the box by a real bucket
fi.append(cyl("Bucket", 0.15, 0.30, ue(-2.85, -2.42, 0.15), "grey", verts=40, bevel=0.006, r2=0.13))
fi.append(cyl("Bucket_Rim", 0.153, 0.012, ue(-2.85, -2.42, 0.30), "grey", verts=40, bevel=0.004))
fi.append(cyl("DrainPan", 0.30, 0.06, ue(-2.80, -1.85, 0.03), "black", verts=48, bevel=0.01))   # clear of the cabinet run
fi.append(cyl("DrainPan_Oil", 0.26, 0.004, ue(-2.80, -1.85, 0.035), "oil", verts=48, bevel=0.0))
fi.append(box("Cardboard", (0.95, 0.75, 0.004), ue(0.50, -2.00, 0.012), "card", bevel=0.001, rot=rz(4)))
BX, BY = 3.18, -0.40                                # east wall (the service counter stands at the old west-wall spot)
fi.append(cyl("Broom_Handle", 0.012, 1.30, ue(BX, BY, 0.72), "wood", rot=(math.radians(-14), 0, 0), verts=12, bevel=0.002))
fi.append(box("Broom_Head", (0.40, 0.06, 0.05), ue(BX - 0.005, BY + 0.17, 0.08), "wood", bevel=0.005, rot=(0, 0, math.pi / 2)))
fi.append(box("Broom_Bristles", (0.38, 0.05, 0.07), ue(BX - 0.005, BY + 0.17, 0.035), "bristle", bevel=0.004, rot=(0, 0, math.pi / 2)))
flooritems = join_parts("SM_R03_FloorItems", fi)
for i, (s, c, r) in enumerate(fucx):
    u = collision_box(f"SM_R03_FloorItems_{i:02d}", s, c, flooritems)
    u.rotation_euler = r

for ob in (toolwall, benchitems, flooritems):
    smart_uv(ob)
result = {o.name: {"tris": sum(len(p.vertices) - 2 for p in o.data.polygons), "mats": len(o.data.materials)}
          for o in (toolwall, benchitems, flooritems)}
print("G7_DRESSING", result)
