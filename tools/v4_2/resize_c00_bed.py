"""C00 (runs INSIDE Blender, scene C00_Schlafzimmer): lengthen the bed from 2.00 m to 2.10 m (comfort length).

Regie 2026-10-25: "verlaengere das Bett auf 2,10 m (Matratze, Rahmen, Decke) und leg den Mann 5 cm tiefer ins Kissen".
The man (1.78 m) lies ~1.88 m from crown to the pointed toe tips; with the 40 cm pillow at the headboard a 2.00 m
mattress left 1.5 cm at the foot end. In place on the built set (build_c00_bedroom.py builds 2.10 m from now on): every
vertex of mattress and bed base beyond the middle of the bed moves 10 cm toward the foot end (bevels stay exact), the
two foot-end legs move with it. The headboard end stays put. The duvet is rebuilt by build_c00_bedroom_occupied.py.
Idempotent: a mattress already 2.10 m long is left alone.
"""
import bpy
from mathutils import Vector

sc = bpy.data.scenes["C00_Schlafzimmer"]
D = 3.20
BX, BY0 = -0.25, D / 2 - 0.03
EXTRA = 0.10
MID = BY0 - 1.10                                    # middle of the bed: only the foot half stretches


def world_ys(o):
    return [(o.matrix_world @ v.co).y for v in o.data.vertices]


mat = bpy.data.objects["SZ_Mattress"]
length = max(world_ys(mat)) - min(world_ys(mat))
moved = []
if length < 2.05:
    for n in ("SZ_Mattress", "SZ_BedBase"):
        o = bpy.data.objects[n]
        inv = o.matrix_world.inverted()
        for v in o.data.vertices:
            w = o.matrix_world @ v.co
            if w.y < MID:
                v.co = inv @ Vector((w.x, w.y - EXTRA, w.z))
        o.data.update()
        moved.append(n)
    for o in sc.objects:
        if o.name.startswith("SZ_BedFoot") and o.matrix_world.translation.y < MID:
            o.location.y -= EXTRA
            moved.append(o.name)
ys = world_ys(mat)
result = {"mattress_y": [round(min(ys), 3), round(max(ys), 3)], "length": round(max(ys) - min(ys), 3), "moved": moved}
print("C00_BED", result)
