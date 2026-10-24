"""G7 (runs INSIDE Blender 5.2): service counter and lift table for the R03 workshop (user decision
2026-10-24). Two static meshes with the room origin (Unreal 5050/0/0, like SM_R03_Room):

  SM_R03_ServiceCounter  1.26 x 0.60 m counter by the door (north side, staff behind it, compressor stays
                         in the corner), payment terminal, order folder, spark-plug display; on the north
                         wall above the compressor a pick-up shelf with finished repair jobs and blank tags
  SM_R03_LiftTable       2.1 x 0.7 m electro-hydraulic scissor lift for motorcycles and garden machines,
                         raised to 0.60 m, in the east half under the window (a car lift would need ~4.2 m
                         of ceiling height, the room has 3.48 m, and the workshop does small-engine work)
Customer route door -> counter front stays free; staff reach the back of the counter through a 0.60 m
gap from the east. No brand names, no text.
"""
import bpy, bmesh, math, os, random
from mathutils import Vector

exec(compile(open(os.path.join(os.path.dirname(__file__), "g7_common.py"), encoding="utf8").read(), "g7_common.py", "exec"))
sc = bpy.context.scene
col = bpy.data.collections.get("G7_Service")
if col:
    for o in list(col.all_objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    col = bpy.data.collections.new("G7_Service")
    sc.collection.children.link(col)
for m in [m for m in bpy.data.materials if m.name.startswith("M_SV_")]:
    bpy.data.materials.remove(m)
rnd = random.Random(11)


def ue(x, y, z):
    return (x, -y, z)


def rz(deg):
    return (0.0, 0.0, math.radians(-deg))


M = {
    "cab": paint_mat("M_SV_PowderAnthracite", (0.035, 0.038, 0.042), 0.45, chip_metal=(0.30, 0.30, 0.30), dust=0.15),
    "beech": simple_mat("M_SV_BeechTop", (0.45, 0.30, 0.17), 0.45, rough_var=0.08, bump=0.08, grime=0.5),
    "steel": simple_mat("M_SV_Steel", (0.60, 0.61, 0.62), 0.35, metal=1.0, rough_var=0.10, bump=0.04),
    "lift": paint_mat("M_SV_LiftGrey", (0.16, 0.17, 0.18), 0.40, chip_metal=(0.32, 0.32, 0.32), dust=0.3),
    "yellow": paint_mat("M_SV_SafetyYellow", (0.62, 0.45, 0.02), 0.40, dust=0.2),
    "black": simple_mat("M_SV_PlasticBlack", (0.03, 0.03, 0.032), 0.48, rough_var=0.08, bump=0.03),
    "screen": simple_mat("M_SV_TerminalScreen", (0.015, 0.02, 0.025), 0.08, rough_var=0.01, bump=0.0, grime=0.0),
    "rubber": simple_mat("M_SV_Rubber", (0.022, 0.022, 0.022), 0.86, rough_var=0.06, bump=0.12),
    "paper": simple_mat("M_SV_Paper", (0.76, 0.75, 0.70), 0.80, rough_var=0.05, bump=0.04, grime=0.2),
    "card": simple_mat("M_SV_Cardboard", (0.31, 0.20, 0.10), 0.86, rough_var=0.05, bump=0.18, grime=0.5),
    "red": paint_mat("M_SV_FolderRed", (0.40, 0.03, 0.02), 0.40, dust=0.1),
    "orange": paint_mat("M_SV_ToolOrange", (0.62, 0.17, 0.02), 0.40, dust=0.3),
    "green": paint_mat("M_SV_HedgeGreen", (0.07, 0.22, 0.05), 0.40, dust=0.3),
    "hydraulic": simple_mat("M_SV_ChromeRod", (0.70, 0.71, 0.72), 0.12, metal=1.0, rough_var=0.03, bump=0.01, grime=0.2),
}

ct, lt, ct_ucx, lt_ucx = [], [], [], []


def add(lst, o):
    lst.append(o)
    return o


# =========================================================================== service counter
CX0, CX1, CY0, CY1, CH = -3.26, -2.00, 1.30, 1.90, 1.00
ccx, ccy = (CX0 + CX1) / 2, (CY0 + CY1) / 2
add(ct, box("Ctr_Body", (CX1 - CX0, CY1 - CY0, CH - 0.10), ue(ccx, ccy, 0.10 + (CH - 0.10) / 2), "cab", bevel=0.004))
add(ct, box("Ctr_Plinth", (CX1 - CX0 - 0.04, CY1 - CY0 - 0.06, 0.10), ue(ccx, ccy + 0.02, 0.05), "black", bevel=0.003))
add(ct, box("Ctr_Top", (CX1 - CX0 + 0.04, CY1 - CY0 + 0.08, 0.04), ue(ccx, ccy - 0.02, CH + 0.02), "beech", bevel=0.003))
for k in range(3):                                         # customer-side panel grooves
    add(ct, box(f"Ctr_Groove{k}", (CX1 - CX0 - 0.10, 0.004, 0.006), ue(ccx, CY0 - 0.001, 0.35 + k * 0.22), "black", bevel=0.0))
ct_ucx.append(((CX1 - CX0, CY1 - CY0, CH + 0.04), ue(ccx, ccy, (CH + 0.04) / 2)))
TOP = CH + 0.04
# payment terminal on a stand, order folder with sheets, spark-plug display box, pen
add(ct, box("Term_Base", (0.08, 0.10, 0.02), ue(-2.35, 1.45, TOP + 0.01), "black", bevel=0.005))
term = [box("Term_Body", (0.08, 0.025, 0.16), (0, 0, 0.08), "black", bevel=0.008),
        box("Term_Screen", (0.06, 0.002, 0.05), (0, -0.013, 0.12), "screen", bevel=0.001),
        box("Term_Keys", (0.06, 0.002, 0.06), (0, -0.013, 0.05), "steel", bevel=0.001)]
ct += place(term, ue(-2.35, 1.45, TOP + 0.02), (math.radians(-20), 0, 0))
add(ct, box("Folder", (0.24, 0.32, 0.03), ue(-2.80, 1.55, TOP + 0.015), "red", bevel=0.004, rot=rz(-6)))
for k in range(3):
    add(ct, box(f"Folder_Sheet{k}", (0.21, 0.297, 0.001), ue(-2.80 + 0.005 * k, 1.55, TOP + 0.031 + k * 0.0012), "paper", bevel=0.0, rot=rz(-6 + k * 2)))
add(ct, box("Pen", (0.14, 0.009, 0.009), ue(-2.62, 1.48, TOP + 0.005), "black", bevel=0.003, rot=rz(30)))
add(ct, box("PlugDisplay", (0.26, 0.16, 0.06), ue(-3.05, 1.70, TOP + 0.03), "card", bevel=0.003))
for i in range(4):
    for j in range(2):
        add(ct, box(f"PlugBox{i}{j}", (0.05, 0.05, 0.09), ue(-3.14 + i * 0.06, 1.66 + j * 0.06, TOP + 0.075), "orange", bevel=0.002))
# pick-up shelf on the north wall above the compressor: two boards with tagged repair jobs
WALL_N = 2.76
for k, z in enumerate((1.35, 1.85)):
    add(ct, box(f"Pickup_Board{k}", (1.10, 0.35, 0.025), ue(-2.65, WALL_N - 0.175, z), "steel", bevel=0.002))
    for s in (-1, 1):
        add(ct, box(f"Pickup_Bracket{k}{s}", (0.004, 0.30, 0.18), ue(-2.65 + s * 0.50, WALL_N - 0.15, z - 0.10), "cab", bevel=0.001))
jobs = [("Job_HedgeTrimmer", (0.55, 0.12, 0.12), "green", -2.85, 1.35), ("Job_Chainsaw", (0.40, 0.18, 0.20), "orange", -2.40, 1.35),
        ("Job_Box1", (0.30, 0.25, 0.20), "card", -2.95, 1.85), ("Job_Leafblower", (0.30, 0.22, 0.30), "orange", -2.45, 1.85)]
for name, size, mat, jx, jz in jobs:
    add(ct, box(name, size, ue(jx, WALL_N - 0.18, jz + 0.0125 + size[2] / 2), mat, bevel=0.015))
    add(ct, box(name + "_Tag", (0.06, 0.002, 0.09), ue(jx + size[0] / 2 - 0.05, WALL_N - 0.18 - size[1] / 2 - 0.002, jz + 0.06), "paper", bevel=0.0,
                rot=(0, rnd.uniform(-0.2, 0.2), 0)))
    add(ct, box(name + "_TagString", (0.002, 0.002, 0.05), ue(jx + size[0] / 2 - 0.05, WALL_N - 0.18 - size[1] / 2, jz + 0.12), "paper", bevel=0.0))
counter = join_parts("SM_R03_ServiceCounter", ct)
for i, (s_, c_) in enumerate(ct_ucx):
    collision_box(f"SM_R03_ServiceCounter_{i:02d}", s_, c_, counter)

# =========================================================================== scissor lift table
LX, LY, LH = 1.85, -0.10, 0.60             # centre (Unreal local) and platform top height
PL, PW, PT = 2.10, 0.70, 0.06
add(lt, box("Lift_Base", (2.00, 0.62, 0.08), ue(LX, LY, 0.04), "lift", bevel=0.006))
for s in (-1, 1):                          # base rails with yellow/black edge markings
    for k in range(10):
        add(lt, box(f"Lift_BaseStripe{s}_{k}", (0.20, 0.004, 0.06), ue(LX - 0.90 + k * 0.20, LY + s * 0.312, 0.04),
                    "yellow" if k % 2 == 0 else "black", bevel=0.0))
arm_len = math.hypot(1.40, LH - PT - 0.10)
ang = math.atan2(LH - PT - 0.10, 1.40)
for s in (-1, 1):                          # two scissor pairs on each side
    for d in (-1, 1):
        add(lt, box(f"Lift_Arm{s}{d}", (arm_len, 0.04, 0.06), ue(LX, LY + s * 0.24, 0.08 + (LH - PT - 0.10) / 2), "lift", bevel=0.006,
                    rot=(0, d * ang, 0)))
    add(lt, cyl(f"Lift_Pivot{s}", 0.022, 0.06, ue(LX, LY + s * 0.24, 0.08 + (LH - PT - 0.10) / 2), "steel", rot=(math.pi / 2, 0, 0), verts=16, bevel=0.002))
add(lt, cyl("Lift_CrossTube", 0.02, 0.50, ue(LX, LY, 0.08 + (LH - PT - 0.10) / 2), "steel", rot=(math.pi / 2, 0, 0), verts=16, bevel=0.002))
add(lt, cyl("Lift_Cylinder", 0.04, 0.55, ue(LX - 0.25, LY, 0.30), "lift", rot=(0, math.radians(70), 0), verts=24, bevel=0.004))
add(lt, cyl("Lift_Rod", 0.018, 0.30, ue(LX + 0.03, LY, 0.42), "hydraulic", rot=(0, math.radians(70), 0), verts=16, bevel=0.002))
add(lt, box("Lift_Platform", (PL, PW, PT), ue(LX, LY, LH - PT / 2), "lift", bevel=0.008))
add(lt, box("Lift_Mat", (PL - 0.10, PW - 0.10, 0.008), ue(LX, LY, LH + 0.004), "rubber", bevel=0.003))
for s in (-1, 1):                          # platform edge markings
    for k in range(11):
        add(lt, box(f"Lift_EdgeStripe{s}_{k}", (0.19, 0.004, 0.05), ue(LX - 0.95 + k * 0.19, LY + s * (PW / 2 + 0.002), LH - PT / 2),
                    "yellow" if k % 2 == 0 else "black", bevel=0.0))
# drive-on ramp: removed while the table is raised (it would need ~1.2 m to reach 0.60 m), lying flat on
# the floor beside the west end
add(lt, box("Lift_Ramp", (0.45, PW - 0.06, 0.03), ue(LX - PL / 2 - 0.30, LY + 0.05, 0.015), "lift", bevel=0.004, rot=rz(8)))
add(lt, box("Lift_WheelClamp", (0.12, 0.18, 0.22), ue(LX + PL / 2 - 0.10, LY, LH + 0.11), "lift", bevel=0.01))
add(lt, box("Lift_PumpUnit", (0.30, 0.25, 0.35), ue(LX + PL / 2 + 0.20, LY + 0.20, 0.175), "lift", bevel=0.01))
add(lt, tube("Lift_Hose", [Vector(ue(LX + PL / 2 + 0.10, LY + 0.20, 0.12)), Vector(ue(LX + 0.6, LY + 0.25, 0.04)),
                           Vector(ue(LX - 0.25, LY + 0.05, 0.12))], 0.008, "black"))
add(lt, box("Lift_Pendant", (0.06, 0.04, 0.12), ue(LX + PL / 2 + 0.20, LY - 0.02, 0.85), "yellow", bevel=0.008))
add(lt, tube("Lift_PendantCable", [Vector(ue(LX + PL / 2 + 0.20, LY + 0.10, 0.35)), Vector(ue(LX + PL / 2 + 0.25, LY + 0.02, 0.60)),
                                   Vector(ue(LX + PL / 2 + 0.20, LY - 0.02, 0.79))], 0.004, "black"))
lt_ucx.append(((PL + 0.45, PW, LH), ue(LX - 0.20, LY, LH / 2), (0, 0, 0)))
lt_ucx.append(((0.30, 0.25, 0.35), ue(LX + PL / 2 + 0.20, LY + 0.20, 0.175), (0, 0, 0)))
lift = join_parts("SM_R03_LiftTable", lt)
for i, (s_, c_, r_) in enumerate(lt_ucx):
    collision_box(f"SM_R03_LiftTable_{i:02d}", s_, c_, lift)

for ob in (counter, lift):
    smart_uv(ob)
result = {o.name: {"tris": sum(len(p.vertices) - 2 for p in o.data.polygons), "mats": len(o.data.materials)} for o in (counter, lift)}
print("G7_SERVICE", result)
