"""G6 WP6.2 (runs INSIDE the Unreal Editor): Flussdorf graybox - R01, R02, R03, R07.

Regions, landmarks and the path order come from WELTBIBEL_FLUSSDORF (working canon):
Werkstatt (R03) <-> Markt (R02) <-> Dorfplatz (R01); Wohnhaeuser (R07) attached to the square.
Layout and all measures are Startwerte (the source says geometry is measured only after graybox).
Real-world sizes: 3 m paths, 17 cm stair risers, 2.2 m doors, 2.6 m market canopy.
Region volumes (TriggerBox "Region_Rxx", tag "Rxx") let tests and NPCs check where someone is.
"""
import math

import unreal

LEVEL = "/Game/Genesis/Flussdorf/Maps/L_Flussdorf_G6"
MAT_DIR = "/Game/Genesis/Flussdorf/Graybox"
V, R = unreal.Vector, unreal.Rotator

eal = unreal.EditorAssetLibrary
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mel = unreal.MaterialEditingLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
CUBE = eal.load_asset("/Engine/BasicShapes/Cube")          # 100 cm, pivot in the centre
CYL = eal.load_asset("/Engine/BasicShapes/Cylinder")       # 100 cm diameter/height, pivot centre
SPHERE = eal.load_asset("/Engine/BasicShapes/Sphere")


# --- Graybox materials: one parent with a colour parameter, an instance per category ---------
def graybox_materials():
    parent_path = f"{MAT_DIR}/M_Graybox"
    if eal.does_asset_exist(parent_path):
        parent = eal.load_asset(parent_path)
    else:
        parent = at.create_asset("M_Graybox", MAT_DIR, unreal.Material, unreal.MaterialFactoryNew())
        col = mel.create_material_expression(parent, unreal.MaterialExpressionVectorParameter, -400, 0)
        col.set_editor_property("parameter_name", "Color")
        col.set_editor_property("default_value", unreal.LinearColor(0.3, 0.3, 0.3, 1))
        rough = mel.create_material_expression(parent, unreal.MaterialExpressionScalarParameter, -400, 200)
        rough.set_editor_property("parameter_name", "Roughness")
        rough.set_editor_property("default_value", 0.8)
        mel.connect_material_property(col, "", unreal.MaterialProperty.MP_BASE_COLOR)
        mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
        mel.recompile_material(parent)
        eal.save_loaded_asset(parent)
    out = {}
    # linear albedo kept in real ranges: grass 0.06-0.1, gravel 0.2, paving 0.25, walls 0.45
    for name, rgb, rough in (("Ground", (0.07, 0.09, 0.05), 0.9), ("Path", (0.20, 0.19, 0.17), 0.85),
                             ("Paving", (0.26, 0.25, 0.23), 0.8), ("Wall", (0.45, 0.43, 0.40), 0.85),
                             ("Roof", (0.12, 0.07, 0.06), 0.7), ("Wood", (0.30, 0.20, 0.11), 0.75),
                             ("Metal", (0.35, 0.36, 0.37), 0.5), ("Foliage", (0.05, 0.09, 0.03), 0.9)):
        path = f"{MAT_DIR}/MI_Graybox_{name}"
        mi = eal.load_asset(path) if eal.does_asset_exist(path) else at.create_asset(
            f"MI_Graybox_{name}", MAT_DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi, parent)
        mel.set_material_instance_vector_parameter_value(mi, "Color", unreal.LinearColor(*rgb, 1))
        mel.set_material_instance_scalar_parameter_value(mi, "Roughness", rough)
        eal.save_loaded_asset(mi)
        out[name] = mi
    return out


M = graybox_materials()


def block(label, centre, size, mat, folder, yaw=0.0, mesh=CUBE):
    """Box/cylinder by real size in cm (centre, full extents)."""
    a = eas.spawn_actor_from_object(mesh, V(*centre), R(0, 0, yaw))
    a.set_actor_label(label)
    a.set_actor_scale3d(V(size[0] / 100.0, size[1] / 100.0, size[2] / 100.0))
    a.static_mesh_component.set_material(0, M[mat])
    a.set_folder_path(folder)
    return a


def on_ground(label, x, y, sx, sy, h, mat, folder, z0=0.0, yaw=0.0, mesh=CUBE):
    return block(label, (x, y, z0 + h / 2.0), (sx, sy, h), mat, folder, yaw, mesh)


def region(rid, centre, extent):
    tb = eas.spawn_actor_from_class(unreal.TriggerBox, V(*centre))
    tb.set_actor_label(f"Region_{rid}")
    tb.tags = [rid]
    tb.collision_component.set_editor_property("box_extent", V(*extent))
    tb.set_folder_path("Regions")
    return tb


def building(label, cx, cy, w, d, h, door_side, folder, z0=0.0, wall=24.0):
    """Four walls with a 120 x 220 cm door opening on one side, flat roof slab."""
    hx, hy = w / 2.0, d / 2.0
    door_w, door_h = 120.0, 220.0
    walls = {"S": (cx, cy - hy + wall / 2, w, wall), "N": (cx, cy + hy - wall / 2, w, wall),
             "W": (cx - hx + wall / 2, cy, wall, d), "E": (cx + hx - wall / 2, cy, wall, d)}
    for side, (x, y, sx, sy) in walls.items():
        if side != door_side:
            on_ground(f"{label}_Wall_{side}", x, y, sx, sy, h, "Wall", folder, z0)
            continue
        along_x = side in ("S", "N")
        length = sx if along_x else sy
        seg = (length - door_w) / 2.0
        for k, sgn in (("L", -1), ("R", 1)):
            off = sgn * (door_w / 2.0 + seg / 2.0)
            px, py = (x + off, y) if along_x else (x, y + off)
            on_ground(f"{label}_Wall_{side}{k}", px, py, seg if along_x else sx, sy if along_x else seg, h, "Wall", folder, z0)
        on_ground(f"{label}_Lintel_{side}", x, y, door_w if along_x else sx, sy if along_x else door_w, h - door_h, "Wall", folder, z0 + door_h)
    on_ground(f"{label}_Roof", cx, cy, w + 40, d + 40, 20, "Roof", folder, z0 + h)


# --- Level ---------------------------------------------------------------------------------------
if eal.does_asset_exist(LEVEL):
    les.load_level(LEVEL)
    for a in eas.get_all_level_actors():
        eas.destroy_actor(a)
else:
    les.new_level(LEVEL)
les.save_current_level()

# Terrain and paths (paths 3 m wide, 2 cm proud of the grass).
block("Ground", (1500, 800, -10), (16000, 12000, 20), "Ground", "Terrain")
block("Path_R01_R02", (1900, 0, 1), (1400, 300, 2), "Path", "Terrain")          # square edge -> market
block("Path_R02_R03", (3950, 0, 1), (1500, 300, 2), "Path", "Terrain")          # market -> workshop door
block("Path_R01_R07", (0, 1450, 1), (300, 500, 2), "Path", "Terrain")           # square -> houses (to the stair)

# R01 Dorfplatz: paved square 24 x 18 m, village tree, notice board, stone stair to the houses.
F = "R01_Dorfplatz"
block("Square_Paving", (0, 0, 1), (2400, 1800, 2), "Paving", F)
on_ground("VillageTree_Trunk", 400, 300, 50, 50, 420, "Wood", F, mesh=CYL)
block("VillageTree_Crown", (400, 300, 650), (520, 520, 420), "Foliage", F, mesh=SPHERE)
on_ground("NoticeBoard_PostL", -700, -700, 10, 10, 210, "Wood", F)
on_ground("NoticeBoard_PostR", -580, -700, 10, 10, 210, "Wood", F)
on_ground("NoticeBoard", -640, -700, 130, 6, 90, "Wood", F, z0=110)
# Stone stair: 3 steps of 17 x 35 cm from the square up to the house terrace (51 cm).
for i in range(3):
    on_ground(f"StoneStair_Step{i + 1}", 0, 1700 + i * 35, 400, 35, 17 * (i + 1), "Paving", F)
region("R01", (0, 0, 150), (1250, 950, 200))

# R07 Wohnhaeuser: terrace +51 cm, three houses 8 x 7 m, doors to the square (closed: no access
# without invitation), gardens and letter boxes.
F = "R07_Wohnhaeuser"
block("HouseTerrace", (0, 2900, 25.5), (3200, 2300, 51), "Ground", F)
for i, (hx, hy) in enumerate(((-1000, 3000), (0, 3150), (1000, 3000))):
    building(f"House{i + 1}", hx, hy, 800, 700, 560, "S", F, z0=51)
    on_ground(f"House{i + 1}_Door", hx, hy - 350 + 5, 110, 6, 215, "Wood", F, z0=51)       # closed door leaf
    on_ground(f"House{i + 1}_Garden", hx + 250, hy - 600, 300, 200, 30, "Foliage", F, z0=51)
    on_ground(f"House{i + 1}_Letterbox", hx - 300, hy - 520, 35, 25, 110, "Metal", F, z0=51)
region("R07", (0, 2950, 300), (1600, 1150, 350))

# R02 Markt: canopy 8 x 5 m at 2.6 m, counter, crates, scale.
F = "R02_Markt"
mx, my = 3000, 0
for dx, dy in ((-380, -230), (380, -230), (-380, 230), (380, 230)):
    on_ground(f"Canopy_Post_{dx}_{dy}", mx + dx, my + dy, 10, 10, 260, "Wood", F)
block("Canopy_Roof", (mx, my, 265), (820, 520, 10), "Roof", F)
on_ground("Counter", mx, my + 120, 300, 70, 95, "Wood", F)
on_ground("Scale", mx - 90, my + 120, 35, 30, 18, "Metal", F, z0=95)
for i, (dx, dy, h) in enumerate(((180, 160, 40), (240, 160, 80), (-260, 150, 40), (300, -150, 40))):
    on_ground(f"Crate{i + 1}", mx + dx, my + dy, 60, 40, h, "Wood", F)
region("R02", (mx, my, 200), (700, 600, 250))

# R03 Werkstatt: 7 x 6 m (G7: shrunk from 10 x 8 m), 3.5 m high, door facing the market (west), workbench, light strip,
# parts shelf and the generator of the repair order.
F = "R03_Werkstatt"
wx, wy = 5050, 0
building("Workshop", wx, wy, 700, 600, 350, "W", F)
on_ground("Workbench", wx + 50, wy + 238, 200, 80, 90, "Wood", F)
block("LightStrip", (wx + 50, wy + 218, 320), (200, 10, 4), "Metal", F)
on_ground("PartsShelf", wx + 304, wy - 120, 50, 200, 200, "Metal", F)
on_ground("Generator", wx + 50, wy - 200, 70, 50, 55, "Metal", F)                           # repair object
region("R03", (wx, wy, 180), (330, 280, 200))

# Navigation: whole village; nav mesh rebuilt automatically in the editor.
nav = eas.spawn_actor_from_class(unreal.NavMeshBoundsVolume, V(2000, 1200, 200))
nav.set_actor_label("NavMeshBounds_Flussdorf")
nav.set_actor_scale3d(V(50, 40, 6))                      # brush is 200 cm -> 100 x 80 x 12 m

# Light: same daylight model as the tech smoke level (sun 38 deg, sky, fog, Sunny 16).
sun = eas.spawn_actor_from_class(unreal.DirectionalLight, V(0, 0, 800), R(0, -38, 215))
sun.set_actor_label("Sun")
for k, v in (("intensity", 90000.0), ("light_source_angle", 0.53), ("atmosphere_sun_light", True),
             ("temperature", 5600.0), ("use_temperature", True)):
    sun.light_component.set_editor_property(k, v)
eas.spawn_actor_from_class(unreal.SkyAtmosphere, V(0, 0, 0)).set_actor_label("SkyAtmosphere")
sky = eas.spawn_actor_from_class(unreal.SkyLight, V(0, 0, 500))
sky.set_actor_label("SkyLight")
sky.light_component.set_editor_property("real_time_capture", True)
fog = eas.spawn_actor_from_class(unreal.ExponentialHeightFog, V(0, 0, 0))
fog.set_actor_label("HeightFog")
fog.component.set_editor_property("fog_density", 0.004)
ppv = eas.spawn_actor_from_class(unreal.PostProcessVolume, V(0, 0, 0))
ppv.set_actor_label("PPV_Exposure")
ppv.set_editor_property("unbound", True)
s = ppv.settings
for prop, val in (("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL), ("auto_exposure_apply_physical_camera_exposure", True),
                  ("camera_iso", 100.0), ("camera_shutter_speed", 100.0), ("depth_of_field_fstop", 16.0),
                  ("bloom_intensity", 0.1), ("lens_flare_intensity", 0.0), ("scene_fringe_intensity", 0.0),
                  ("vignette_intensity", 0.15), ("film_grain_intensity", 0.0)):
    s.set_editor_property(prop, val)
    s.set_editor_property("override_" + prop, True)
ppv.set_editor_property("settings", s)

ps = eas.spawn_actor_from_class(unreal.PlayerStart, V(-300, -500, 100), R(0, 0, 0))
ps.set_actor_label("PlayerStart_Dorfplatz")

# Build the nav mesh now (it is saved with the level; at runtime it regenerates dynamically).
unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(), "RebuildNavigation")
les.save_current_level()
labels = [a.get_actor_label() for a in eas.get_all_level_actors()]
print("G6_LEVEL ok", LEVEL, len(labels), "actors")
