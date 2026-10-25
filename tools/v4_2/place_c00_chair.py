"""C00 (runs INSIDE Blender after build_c00_bedroom_decor.py): the daughter's chair for shot 00-B.

Regie 2026-10-25 (technical test 00-B): the daughter sits on the chair at the window side of the bed at the height of
his hip, leans forward and holds his right hand. build_c00_bedroom.py placed the chair at the foot end facing the
headboard; here it is turned 90 deg (backrest to the window, seat facing the bed) and moved to the man's hip
(world y ~0.48, from C00_BEDROOM_LYING.json / C00_POSE_JOINTS.json). The knitted throw over the backrest moves with it
rigidly (its draped shape stays valid: rotation about the vertical axis, floor contact unchanged).
"""
import math

import bpy
from mathutils import Matrix, Vector

sc = bpy.data.scenes["C00_Schlafzimmer"]
PARTS = [o for o in sc.objects if o.name.startswith(("SZ_ChairSeat", "SZ_ChairBack", "SZ_ChairLeg", "SZ_Throw"))]
OLD_C = Vector((0.70, -0.15, 0.0))                       # build_c00_bedroom.py: chair centre, facing +y
NEW_C = Vector((1.02, 0.48, 0.0))                        # seat front ~36 cm from the mattress edge (x 0.45): her knees
                                                         # (thighs ~45 cm) end at the bed side, not over the mattress
YAW = math.radians(90.0)                                 # +y (headboard) -> -x (toward the bed)
seat = bpy.data.objects["SZ_ChairSeat"]
_c = seat.matrix_world.translation.copy()
if abs(_c.x - OLD_C.x) < 0.05 and abs(_c.y - OLD_C.y) < 0.05:          # still where build_c00_bedroom.py put it
    M = Matrix.Translation(NEW_C) @ Matrix.Rotation(YAW, 4, "Z") @ Matrix.Translation(-OLD_C)
else:                                                    # already turned by an earlier run: only move it
    M = Matrix.Translation(Vector((NEW_C.x - _c.x, NEW_C.y - _c.y, 0.0)))
for o in PARTS:
    o.matrix_world = M @ o.matrix_world
moved = round(seat.matrix_world.translation.x, 3), round(seat.matrix_world.translation.y, 3)
result = {"parts": [o.name for o in PARTS], "seat_centre": moved}
print("C00_CHAIR", result)
