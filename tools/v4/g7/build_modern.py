"""G7 (runs INSIDE Blender 5.2): modern equipment for the R03 workshop (user decision 2026-10-24:
"moderner und voller"). Two static meshes with the room origin (Unreal 5050/0/0, like SM_R03_Room):

  SM_R03_Cabinets   2.0 m run of anthracite base cabinets with drawers and a beech worktop on the south
                    wall, slotted tool panel and wall cabinets above; on the worktop a diagnosis laptop,
                    a cordless drill on its charger, a socket set case, a chainsaw waiting for repair,
                    spray cans and an oil bottle
  SM_R03_Equipment  50 l compressor with wall hose reel, fire extinguisher and first-aid box by the door,
                    lawnmower (repair job) on the lift table under the window, line trimmer against the east wall,
                    waste bin, rubber mat in front of the workbench, wall clock
The walking routes door -> N02 spot (-1.0/-1.1), door -> workbench (0.5/1.3) and the inspection spot
1.2 m west of the generator stay free. No brand names, no text.
"""
import bpy, bmesh, math, os, random
from mathutils import Vector

exec(compile(open(os.path.join(os.path.dirname(__file__), "g7_common.py"), encoding="utf8").read(), "g7_common.py", "exec"))
sc = bpy.context.scene
col = bpy.data.collections.get("G7_Modern")
if col:
    for o in list(col.all_objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    col = bpy.data.collections.new("G7_Modern")
    sc.collection.children.link(col)
for m in [m for m in bpy.data.materials if m.name.startswith("M_MO_")]:
    bpy.data.materials.remove(m)
rnd = random.Random(7)


def ue(x, y, z):
    return (x, -y, z)


def rz(deg):
    return (0.0, 0.0, math.radians(-deg))


M = {
    "cab": paint_mat("M_MO_PowderAnthracite", (0.035, 0.038, 0.042), 0.45, chip_metal=(0.30, 0.30, 0.30), dust=0.15),
    "alu": simple_mat("M_MO_AluBrushed", (0.80, 0.80, 0.79), 0.32, metal=1.0, rough_var=0.05, bump=0.02, grime=0.3),
    "beech": simple_mat("M_MO_BeechWorktop", (0.45, 0.30, 0.17), 0.45, rough_var=0.08, bump=0.08, grime=0.5),
    "steel": simple_mat("M_MO_Steel", (0.60, 0.61, 0.62), 0.35, metal=1.0, rough_var=0.10, bump=0.04),
    "black": simple_mat("M_MO_PlasticBlack", (0.03, 0.03, 0.032), 0.48, rough_var=0.08, bump=0.03),
    "screen": simple_mat("M_MO_ScreenGlass", (0.012, 0.014, 0.018), 0.06, rough_var=0.01, bump=0.0, grime=0.0),
    "red": paint_mat("M_MO_SignalRed", (0.50, 0.03, 0.02), 0.35, dust=0.2),
    "green": paint_mat("M_MO_MowerGreen", (0.06, 0.20, 0.05), 0.40, dust=0.4),
    "orange": paint_mat("M_MO_ToolOrange", (0.62, 0.17, 0.02), 0.40, dust=0.3),
    "blue": simple_mat("M_MO_CaseBlue", (0.03, 0.09, 0.30), 0.40, rough_var=0.06, bump=0.02),
    "white": simple_mat("M_MO_PlasticWhite", (0.72, 0.72, 0.70), 0.42, rough_var=0.06, bump=0.02),
    "firstaid": simple_mat("M_MO_FirstAidGreen", (0.02, 0.25, 0.10), 0.40, rough_var=0.06, bump=0.02),
    "rubber": simple_mat("M_MO_Rubber", (0.022, 0.022, 0.022), 0.86, rough_var=0.06, bump=0.10),
    "hose": simple_mat("M_MO_AirHoseBlue", (0.02, 0.12, 0.40), 0.40, rough_var=0.06, bump=0.02),
    "chain": simple_mat("M_MO_SawChain", (0.25, 0.25, 0.26), 0.45, metal=1.0, rough_var=0.10, bump=0.4),
    "spray_y": paint_mat("M_MO_SprayYellow", (0.60, 0.42, 0.03), 0.30, dust=0.1),
    "spray_b": paint_mat("M_MO_SprayBlue", (0.04, 0.10, 0.35), 0.30, dust=0.1),
    "bottle": simple_mat("M_MO_OilBottle", (0.55, 0.45, 0.10), 0.35, rough_var=0.05, bump=0.02, grime=0.3),
    "grass": simple_mat("M_MO_GrassClippings", (0.06, 0.10, 0.03), 0.9, rough_var=0.05, bump=0.6),
    "glass": clear_mat("M_MO_ClockGlass", (0.96, 0.97, 0.96), 0.03),
}

cab, eq, cab_ucx, eq_ucx = [], [], [], []


def add(lst, o):
    lst.append(o)
    return o


# ======================================================================= cabinet run, south wall
WALL_S = -2.76
X0, X1 = -2.25, -0.25
DEPTH, BASE_H, TOP_T = 0.60, 0.86, 0.04
cy = WALL_S + DEPTH / 2
add(cab, box("Cab_Plinth", (X1 - X0 - 0.02, DEPTH - 0.08, 0.10), ue((X0 + X1) / 2, cy + 0.03, 0.05), "black", bevel=0.003))
for k in range(4):                                         # four 0.5 m units: drawers, door, drawers, door
    ux = X0 + 0.25 + k * 0.5
    add(cab, box(f"Cab_Body{k}", (0.49, DEPTH - 0.02, BASE_H - 0.10), ue(ux, cy, 0.10 + (BASE_H - 0.10) / 2), "cab", bevel=0.003))
    front_y = WALL_S + DEPTH + 0.001
    if k % 2 == 0:
        hs = [0.12, 0.12, 0.16, 0.18, 0.18]
        z = 0.105
        for j, h in enumerate(hs):
            add(cab, box(f"Cab_Drawer{k}_{j}", (0.47, 0.018, h - 0.006), ue(ux, front_y, z + h / 2), "cab", bevel=0.002))
            add(cab, box(f"Cab_Grip{k}_{j}", (0.30, 0.02, 0.012), ue(ux, front_y + 0.015, z + h - 0.03), "alu", bevel=0.003))
            z += h
    else:
        add(cab, box(f"Cab_Door{k}", (0.47, 0.018, BASE_H - 0.12), ue(ux, front_y, 0.11 + (BASE_H - 0.12) / 2), "cab", bevel=0.002))
        add(cab, box(f"Cab_DoorGrip{k}", (0.012, 0.02, 0.30), ue(ux + 0.18, front_y + 0.015, 0.62), "alu", bevel=0.003))
add(cab, box("Cab_Worktop", (X1 - X0 + 0.02, DEPTH + 0.02, TOP_T), ue((X0 + X1) / 2, cy + 0.01, BASE_H + TOP_T / 2), "beech", bevel=0.003))
cab_ucx.append(((X1 - X0, DEPTH, BASE_H + TOP_T), ue((X0 + X1) / 2, cy, (BASE_H + TOP_T) / 2)))
TOP = BASE_H + TOP_T
# slotted tool panel (louvred panel look: horizontal slots) and wall cabinets
add(cab, perforated_sheet("Cab_SlotPanel", 1.90, 0.70, ue((X0 + X1) / 2, WALL_S + 0.02, TOP + 0.50), "cab", pitch=0.038, hole=0.008))
for k, (tx, L) in enumerate([(-2.05, 0.30), (-1.95, 0.25), (-1.85, 0.20)]):
    add(cab, box(f"Panel_Hook{k}", (0.006, 0.05, 0.006), ue(tx, WALL_S + 0.045, TOP + 0.62), "steel", bevel=0.001))
    add(cab, box(f"Panel_Clamp{k}", (0.03, 0.05, L), ue(tx, WALL_S + 0.07, TOP + 0.62 - L / 2), "orange" if k == 0 else "steel", bevel=0.004))
for k in range(2):
    ux = X0 + 0.5 + k * 1.0
    add(cab, box(f"Wall_Cab{k}", (0.98, 0.35, 0.60), ue(ux, WALL_S + 0.175, 2.15), "cab", bevel=0.003))
    add(cab, box(f"Wall_CabGrip{k}", (0.30, 0.02, 0.012), ue(ux, WALL_S + 0.36, 1.90), "alu", bevel=0.003))
# worktop items: laptop (diagnosis), drill on charger, socket case, chainsaw, spray cans, oil bottle
LX, LY = -0.65, WALL_S + 0.33
add(cab, box("Laptop_Base", (0.33, 0.23, 0.018), ue(LX, LY, TOP + 0.009), "alu", bevel=0.004, rot=rz(-8)))
lid = box("Laptop_Lid", (0.33, 0.008, 0.22), (0, 0, 0), "alu", bevel=0.003)
scr = box("Laptop_Screen", (0.30, 0.002, 0.19), (0, -0.005, 0.0), "screen", bevel=0.0005)
cab += place([lid, scr], ue(LX - 0.016, LY - 0.13, TOP + 0.115), (math.radians(-15), 0, math.radians(8)))   # hinge on the wall side, opened ~105 deg
add(cab, box("Laptop_Keys", (0.28, 0.12, 0.002), ue(LX, LY - 0.02, TOP + 0.019), "black", bevel=0.0005, rot=rz(-8)))
add(cab, box("Diag_Cable", (0.02, 0.02, 0.01), ue(LX - 0.2, LY, TOP + 0.005), "black", bevel=0.002))
DX, DY = -1.55, WALL_S + 0.30
add(cab, box("Charger_Base", (0.13, 0.10, 0.05), ue(DX, DY, TOP + 0.025), "black", bevel=0.008))
add(cab, box("Battery", (0.075, 0.11, 0.07), ue(DX, DY, TOP + 0.085), "orange", bevel=0.008))
drill = [box("Drill_Body", (0.20, 0.06, 0.07), (0, 0, 0.17), "orange", bevel=0.012),
         box("Drill_Grip", (0.05, 0.05, 0.14), (-0.03, 0, 0.07), "black", bevel=0.01),
         box("Drill_Battery", (0.08, 0.11, 0.06), (-0.03, 0, -0.01), "orange", bevel=0.008),
         cyl("Drill_Chuck", 0.018, 0.05, (0.125, 0, 0.17), "steel", rot=(0, math.pi / 2, 0), verts=16, bevel=0.002)]
cab += place(drill, ue(DX + 0.22, DY + 0.02, TOP + 0.04), rz(25))
add(cab, box("SocketCase", (0.40, 0.28, 0.075), ue(-2.0, WALL_S + 0.33, TOP + 0.0375), "blue", bevel=0.012, rot=rz(5)))
add(cab, box("SocketCase_Latch", (0.05, 0.01, 0.02), ue(-2.0, WALL_S + 0.19, TOP + 0.05), "steel", bevel=0.002))
saw = [box("Saw_Body", (0.30, 0.18, 0.20), (0, 0, 0.10), "orange", bevel=0.02),
       box("Saw_Cover", (0.16, 0.185, 0.08), (-0.05, 0, 0.17), "black", bevel=0.01),
       box("Saw_Bar", (0.38, 0.006, 0.07), (0.33, 0.06, 0.07), "steel", bevel=0.02),
       box("Saw_Chain", (0.40, 0.009, 0.082), (0.33, 0.06, 0.07), "chain", bevel=0.025),
       tube("Saw_Handle", [Vector((-0.02, -0.10, 0.06)), Vector((0.02, -0.12, 0.25)), Vector((0.06, 0.0, 0.29)),
                           Vector((0.02, 0.12, 0.25)), Vector((-0.02, 0.10, 0.06))], 0.012, "black")]
cab += place(saw, ue(-1.25, WALL_S + 0.32, TOP), rz(-12))
for k, (sx, m) in enumerate(((-0.30, "spray_y"), (-0.24, "spray_b"), (-0.18, "spray_y"))):
    add(cab, cyl(f"Spray{k}", 0.033, 0.20, ue(sx, WALL_S + 0.12, TOP + 0.10), m, verts=24, bevel=0.004))
    add(cab, cyl(f"Spray{k}_Cap", 0.030, 0.05, ue(sx, WALL_S + 0.12, TOP + 0.225), "white", verts=24, bevel=0.004))
add(cab, box("OilBottle", (0.10, 0.06, 0.22), ue(-0.42, WALL_S + 0.10, TOP + 0.11), "bottle", bevel=0.012))
add(cab, cyl("OilBottle_Cap", 0.015, 0.03, ue(-0.40, WALL_S + 0.10, TOP + 0.235), "black", verts=16, bevel=0.002))
cabinets = join_parts("SM_R03_Cabinets", cab)
for i, (s_, c_) in enumerate(cab_ucx):
    collision_box(f"SM_R03_Cabinets_{i:02d}", s_, c_, cabinets)

# ======================================================================= equipment
WALL_W = -3.26
# 50 l compressor in the north-west corner, hose reel above it on the west wall
CX, CY = -2.72, 2.30
add(eq, cyl("Comp_Tank", 0.18, 0.62, ue(CX, CY, 0.30), "red", rot=(0, math.pi / 2, 0), verts=48, bevel=0.01))
for s in (-1, 1):
    add(eq, cyl(f"Comp_Cap{s}", 0.17, 0.03, ue(CX + s * 0.31, CY, 0.30), "red", rot=(0, math.pi / 2, 0), verts=48, bevel=0.012))
add(eq, box("Comp_Motor", (0.30, 0.20, 0.18), ue(CX - 0.05, CY, 0.57), "black", bevel=0.02))
add(eq, cyl("Comp_Head", 0.07, 0.12, ue(CX + 0.16, CY, 0.60), "alu", verts=24, bevel=0.006))
add(eq, cyl("Comp_Gauge", 0.03, 0.02, ue(CX + 0.20, CY - 0.11, 0.55), "white", rot=(math.pi / 2, 0, 0), verts=24, bevel=0.003))
for s in (-1, 1):
    add(eq, cyl(f"Comp_Wheel{s}", 0.07, 0.04, ue(CX - 0.22, CY + s * 0.17, 0.07), "rubber", rot=(math.pi / 2, 0, 0), verts=32, bevel=0.006))
add(eq, box("Comp_Foot", (0.04, 0.30, 0.10), ue(CX + 0.24, CY, 0.05), "black", bevel=0.005))
add(eq, tube("Comp_Handle", [Vector(ue(CX - 0.32, CY - 0.12, 0.40)), Vector(ue(CX - 0.40, CY - 0.12, 0.78)),
                             Vector(ue(CX - 0.40, CY + 0.12, 0.78)), Vector(ue(CX - 0.32, CY + 0.12, 0.40))], 0.012, "black"))
eq_ucx.append(((0.75, 0.40, 0.80), ue(CX, CY, 0.40), (0, 0, 0)))
RX, RY, RZ = WALL_W + 0.09, 1.65, 1.45
add(eq, cyl("Reel_Back", 0.26, 0.02, ue(WALL_W + 0.01, RY, RZ), "cab", rot=(0, math.pi / 2, 0), verts=48, bevel=0.004))
for k in range(6):
    add(eq, cyl(f"Reel_Hose{k}", 0.20 - k * 0.012, 0.13, ue(RX, RY, RZ), "hose", rot=(0, math.pi / 2, 0), verts=48, bevel=0.01))
add(eq, cyl("Reel_Front", 0.26, 0.015, ue(RX + 0.075, RY, RZ), "cab", rot=(0, math.pi / 2, 0), verts=48, bevel=0.004))
add(eq, tube("Reel_Out", [Vector(ue(RX + 0.05, RY + 0.20, RZ - 0.15)), Vector(ue(RX + 0.20, RY + 0.35, 0.95)),
                          Vector(ue(CX - 0.10, CY - 0.05, 0.70))], 0.006, "hose"))
# fire extinguisher (6 kg) and first-aid box on the west wall south of the door
FY = -1.05
add(eq, box("Ext_Bracket", (0.02, 0.08, 0.20), ue(WALL_W + 0.01, FY, 0.95), "steel", bevel=0.003))
add(eq, cyl("Ext_Body", 0.08, 0.50, ue(WALL_W + 0.10, FY, 0.80), "red", verts=40, bevel=0.02))
add(eq, cyl("Ext_Valve", 0.025, 0.08, ue(WALL_W + 0.10, FY, 1.09), "black", verts=16, bevel=0.003))
add(eq, box("Ext_Lever", (0.10, 0.02, 0.012), ue(WALL_W + 0.13, FY, 1.13), "steel", bevel=0.002))
add(eq, tube("Ext_Hose", [Vector(ue(WALL_W + 0.10, FY + 0.03, 1.10)), Vector(ue(WALL_W + 0.18, FY + 0.06, 1.0)),
                          Vector(ue(WALL_W + 0.18, FY + 0.09, 0.70))], 0.008, "black"))
add(eq, box("FirstAid", (0.10, 0.32, 0.24), ue(WALL_W + 0.05, -1.70, 1.45), "firstaid", bevel=0.01))
add(eq, box("FirstAid_CrossH", (0.006, 0.12, 0.04), ue(WALL_W + 0.10, -1.70, 1.45), "white", bevel=0.002))
add(eq, box("FirstAid_CrossV", (0.006, 0.04, 0.12), ue(WALL_W + 0.10, -1.70, 1.45), "white", bevel=0.002))
# lawnmower under the window (repair job), handle towards the room
mow = [box("Mow_Deck", (0.50, 0.55, 0.16), (0, 0, 0.14), "green", bevel=0.05),
       cyl("Mow_Engine", 0.12, 0.16, (0.0, 0.0, 0.29), "black", verts=32, bevel=0.02),
       cyl("Mow_Tank", 0.05, 0.05, (0.08, 0.08, 0.38), "red", verts=24, bevel=0.01),
       box("Mow_Bag", (0.30, 0.40, 0.28), (-0.42, 0, 0.26), "black", bevel=0.04)]
for sx in (-1, 1):
    for sy in (-1, 1):
        mow.append(cyl(f"Mow_Wheel{sx}{sy}", 0.09 if sx < 0 else 0.075, 0.045, (sx * 0.20, sy * 0.29, 0.09 if sx < 0 else 0.075), "rubber",
                       rot=(math.pi / 2, 0, 0), verts=32, bevel=0.008))
mow.append(tube("Mow_Handle", [Vector((-0.25, -0.22, 0.20)), Vector((-0.55, -0.22, 0.70)), Vector((-0.70, -0.22, 0.98)),
                               Vector((-0.70, 0.22, 0.98)), Vector((-0.55, 0.22, 0.70)), Vector((-0.25, 0.22, 0.20))], 0.013, "black"))
mow.append(box("Mow_Clippings", (0.30, 0.40, 0.01), (0.05, 0.0, 0.005), "grass", bevel=0.002))
eq += place(mow, ue(1.70, -0.10, 0.608), rz(0))          # standing on the lift table (build_service.py)
# line trimmer leaning against the east wall
trim = [cyl("Trim_Shaft", 0.014, 1.45, (0, 0, 0), "alu", verts=12, bevel=0.002),
        box("Trim_Engine", (0.20, 0.14, 0.18), (0, 0, 0.78), "orange", bevel=0.03),
        cyl("Trim_Head", 0.07, 0.06, (0, 0, -0.74), "black", verts=24, bevel=0.01),
        box("Trim_Guard", (0.22, 0.006, 0.10), (0.04, 0, -0.68), "orange", bevel=0.01),
        box("Trim_Bar", (0.04, 0.50, 0.03), (0, 0, 0.30), "black", bevel=0.01)]
eq += place(trim, ue(3.05, 0.30, 0.76), (0, math.radians(-10), 0))
# waste bin, anti-fatigue mat, wall clock
add(eq, cyl("Bin", 0.20, 0.60, ue(2.95, -2.40, 0.30), "cab", verts=48, bevel=0.01, r2=0.18))
add(eq, cyl("Bin_Lid", 0.205, 0.04, ue(2.95, -2.40, 0.62), "black", verts=48, bevel=0.01))
add(eq, cyl("Bin_Pedal", 0.04, 0.02, ue(2.95, -2.18, 0.02), "black", verts=16, bevel=0.004))
eq_ucx.append(((0.42, 0.42, 0.64), ue(2.95, -2.40, 0.32), (0, 0, 0)))
add(eq, box("Mat", (1.50, 0.60, 0.012), ue(0.50, 1.75, 0.006), "rubber", bevel=0.004))
add(eq, cyl("Clock_Rim", 0.16, 0.04, ue(-1.25, WALL_S + 0.02, 2.62), "black", rot=(math.pi / 2, 0, 0), verts=48, bevel=0.006))
add(eq, cyl("Clock_Face", 0.15, 0.005, ue(-1.25, WALL_S + 0.042, 2.62), "white", rot=(math.pi / 2, 0, 0), verts=48, bevel=0.0))
for k in range(12):
    a = 2 * math.pi * k / 12
    add(eq, box(f"Clock_Tick{k}", (0.006, 0.003, 0.02 if k % 3 else 0.03), ue(-1.25 + 0.125 * math.sin(a), WALL_S + 0.046, 2.62 + 0.125 * math.cos(a)),
                "black", bevel=0.0, rot=(0, a, 0)))
add(eq, box("Clock_HandH", (0.008, 0.003, 0.07), ue(-1.25 + 0.02, WALL_S + 0.05, 2.62 + 0.03), "black", bevel=0.0, rot=(0, math.radians(50), 0)))
add(eq, box("Clock_HandM", (0.006, 0.003, 0.11), ue(-1.25 + 0.0, WALL_S + 0.052, 2.62 + 0.055), "black", bevel=0.0))
add(eq, cyl("Clock_Glass", 0.152, 0.004, ue(-1.25, WALL_S + 0.058, 2.62), "glass", rot=(math.pi / 2, 0, 0), verts=48, bevel=0.0))
equipment = join_parts("SM_R03_Equipment", eq)
for i, (s_, c_, r_) in enumerate(eq_ucx):
    u = collision_box(f"SM_R03_Equipment_{i:02d}", s_, c_, equipment)
    u.rotation_euler = r_
for ob in (cabinets, equipment):
    smart_uv(ob)
result = {o.name: {"tris": sum(len(p.vertices) - 2 for p in o.data.polygons), "mats": len(o.data.materials)} for o in (cabinets, equipment)}
print("G7_MODERN", result)
