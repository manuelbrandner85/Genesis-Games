"""G7 (runs INSIDE the Unreal Editor): shrink the R03 workshop from 10 x 8 m to 7 x 6 m (user decision
2026-10-24: a small engine-repair workshop reads more real when it is compact and full).

The west wall with the door stays where it was (x = 4700, path from the market unchanged); the room
loses 3 m to the east and 2 m in depth. Rebuilds the graybox walls/roof with the same rules as
tools/v4/g6/g6_level.py building(), moves the region volume and the N01 work anchor, then rebuilds
navigation. The furniture is placed afterwards by g7_level.py.
"""
import unreal

LEVEL = "/Game/Genesis/Flussdorf/Maps/L_Flussdorf_G6"
MAT_DIR = "/Game/Genesis/Flussdorf/Graybox"
V, R = unreal.Vector, unreal.Rotator
eal = unreal.EditorAssetLibrary
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if les.get_current_level().get_path_name().split(":")[0].split(".")[0] != LEVEL:
    les.load_level(LEVEL)
CUBE = eal.load_asset("/Engine/BasicShapes/Cube")
M = {n: eal.load_asset(f"{MAT_DIR}/MI_Graybox_{n}") for n in ("Wall", "Roof", "Paving")}
F = "R03_Werkstatt"
CX, CY, W, D, H, WALL = 5050.0, 0.0, 700.0, 600.0, 350.0, 24.0


def on_ground(label, x, y, sx, sy, h, mat, z0=0.0):
    a = eas.spawn_actor_from_object(CUBE, V(x, y, z0 + h / 2.0), R(0, 0, 0))
    a.set_actor_label(label)
    a.set_actor_scale3d(V(sx / 100.0, sy / 100.0, h / 100.0))
    a.static_mesh_component.set_material(0, M[mat])
    a.set_folder_path(F)
    return a


for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("Workshop_"):
        eas.destroy_actor(a)
# four walls, 120 x 220 cm door in the west wall, flat roof slab (as g6_level.building)
hx, hy = W / 2.0, D / 2.0
door_w, door_h = 120.0, 220.0
on_ground("Workshop_Wall_S", CX, CY - hy + WALL / 2, W, WALL, H, "Wall")
on_ground("Workshop_Wall_N", CX, CY + hy - WALL / 2, W, WALL, H, "Wall")
on_ground("Workshop_Wall_E", CX + hx - WALL / 2, CY, WALL, D, H, "Wall")
x = CX - hx + WALL / 2
seg = (D - door_w) / 2.0
for k, sgn in (("L", -1), ("R", 1)):
    on_ground(f"Workshop_Wall_W{k}", x, CY + sgn * (door_w / 2.0 + seg / 2.0), WALL, seg, H, "Wall")
on_ground("Workshop_Lintel_W", x, CY, WALL, door_w, H - door_h, "Wall", door_h)
on_ground("Workshop_Roof", CX, CY, W + 40, D + 40, 20, "Roof", H)
# Inside ceiling: whitewashed, neutral. The red-brown graybox roof lit by the LED bar hanging 60 cm below
# bounced a strong red tint into every shadowed corner (Lumen GI measured in the G7 review renders).
on_ground("Workshop_Ceiling", CX, CY, W - 2 * WALL, D - 2 * WALL, 2, "Wall", H - 2)
# Concrete floor slab (12 cm, top 1 cm above the lawn): the room stood on the village lawn, and the thin lower
# shelf of the bench on that single ground block leaked orange light at the floor line.
on_ground("Workshop_Floor", CX, CY, W - 2 * WALL, D - 2 * WALL, 12, "Paving", -11)   # 1 cm proud: no z-fight with the lawn

actors = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
reg = actors["Region_R03"]
reg.set_actor_location(V(CX, CY, 180), False, True)
reg.collision_component.set_editor_property("box_extent", V(hx - 20, hy - 20, 200))
actors["Anchor_N01_Work"].set_actor_location_and_rotation(V(5100, 130, 100), R(0, 0, 90), False, True)
les.save_current_level()
unreal.SystemLibrary.execute_console_command(None, "RebuildNavigation")

inner = [CX - hx + WALL, CX + hx - WALL, CY - hy + WALL, CY + hy - WALL]
print("G7_ROOM", {"inner_x": inner[:2], "inner_y": inner[2:], "region": [CX, CY, hx - 20, hy - 20],
                  "n01_work": [5100, 130, 100]})
