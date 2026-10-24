"""CM2 (runs INSIDE the Unreal Editor): build L_MainMenu, the background of the main menu.

The menu background is a non-persistent shot of the G7 workshop R03 (same meshes, LED bars, sun and
exposure as in L_Flussdorf_G6) seen by a slowly drifting camera (tag MenuCamera, driven by
AGenesisMenuPlayerController). No world setup, NPCs or player start: nothing simulates or saves here.
World settings use AGenesisMenuGameMode. Idempotent: an existing map is cleared and rebuilt.
"""
import unreal

MAP = "/Game/Genesis/UI/Maps/L_MainMenu"
R03 = "/Game/Genesis/Flussdorf/R03"
V, R = unreal.Vector, unreal.Rotator
eal = unreal.EditorAssetLibrary
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

if eal.does_asset_exist(MAP):
    les.load_level(MAP)
    for a in eas.get_all_level_actors():
        if not isinstance(a, unreal.WorldSettings):
            eas.destroy_actor(a)
else:
    les.new_level(MAP)

CX = 5050.0
CEILING = 346.0


def mesh(label, asset, loc, yaw=0.0):
    m = eal.load_asset(f"{R03}/{asset}")
    if m is None:
        raise RuntimeError("asset missing: " + asset)
    a = eas.spawn_actor_from_object(m, V(*loc), R(0, 0, yaw))
    a.set_actor_label(label)
    a.set_folder_path("R03_Werkstatt")
    return a


# Workshop as placed by tools/v4/g7/g7_level.py
for label, asset in (("R03_Room", "Room/SM_R03_Room"), ("R03_ToolWall", "Dressing/ToolWall/SM_R03_ToolWall"),
                     ("R03_BenchItems", "Dressing/BenchItems/SM_R03_BenchItems"), ("R03_FloorItems", "Dressing/FloorItems/SM_R03_FloorItems"),
                     ("R03_Cabinets", "Dressing/Cabinets/SM_R03_Cabinets"), ("R03_Equipment", "Dressing/Equipment/SM_R03_Equipment"),
                     ("R03_ServiceCounter", "Dressing/ServiceCounter/SM_R03_ServiceCounter"), ("R03_LiftTable", "Dressing/LiftTable/SM_R03_LiftTable")):
    mesh(label, asset, (CX, 0, 0))
mesh("Workbench", "Workbench/SM_R03_Workbench", (5100, 238, 0), 180)
mesh("PartsShelf", "PartsShelf/SM_R03_PartsShelf", (5354, -120, 0), 90)
mesh("Generator_N02", "Generator_N02/SM_R03_Generator_N02", (5100, -200, 0), 90)
for i, (bx, by) in enumerate(((5115, 218), (4970, -30), (5280, -60))):
    bar = mesh(f"LightStrip{i + 1}", "LightBar/SM_R03_LightBar", (bx, by, CEILING))
    sock = bar.static_mesh_component.get_socket_location("Light")
    lt = eas.spawn_actor_from_class(unreal.RectLight, sock - V(0, 0, 0.5), R(-90, 0, 0))
    lt.set_actor_label(f"R03_LightBar_Light{i + 1}")
    lc = lt.get_component_by_class(unreal.RectLightComponent)
    for k, v in (("intensity_units", unreal.LightUnits.LUMENS), ("intensity", 4000.0), ("use_temperature", True),
                 ("temperature", 4000.0), ("source_width", 148.0), ("source_height", 5.0), ("barn_door_angle", 0.0),
                 ("attenuation_radius", 900.0)):
        lc.set_editor_property(k, v)

# Outside: ground, roof over the plank ceiling, daylight model of the village (sun 38 deg, sky, fog)
cube = eal.load_asset("/Engine/BasicShapes/Cube")
ground_mi = eal.load_asset("/Game/Genesis/Flussdorf/Graybox/MI_Graybox_Ground")
roof_mi = eal.load_asset("/Game/Genesis/Flussdorf/Graybox/MI_Graybox_Roof")
for label, loc, size, mi in (("Ground", (CX, 0, -11), (12000, 12000, 20), ground_mi), ("Roof", (CX, 0, 362), (760, 660, 20), roof_mi)):
    a = eas.spawn_actor_from_object(cube, V(*loc), R(0, 0, 0))
    a.set_actor_label(label)
    a.set_actor_scale3d(V(size[0] / 100, size[1] / 100, size[2] / 100))
    if mi:
        a.static_mesh_component.set_material(0, mi)
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

# Interior exposure as in the game (EV ~6: ISO 800, 1/60 s, f/2.8), no motion blur on the drift shot
ppv = eas.spawn_actor_from_class(unreal.PostProcessVolume, V(CX, 0, 0))
ppv.set_actor_label("PPV_Menu")
ppv.set_editor_property("unbound", True)
st = ppv.settings
for prop, val in (("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL), ("auto_exposure_apply_physical_camera_exposure", True),
                  ("camera_iso", 800.0), ("camera_shutter_speed", 60.0), ("depth_of_field_fstop", 2.8),
                  ("vignette_intensity", 0.35), ("bloom_intensity", 0.15), ("motion_blur_amount", 0.0)):
    st.set_editor_property(prop, val)
    st.set_editor_property("override_" + prop, True)
ppv.set_editor_property("settings", st)

# Camera: south-west corner at eye height, looking at the bench, tool wall and generator
cam_loc = V(4775, -240, 158)
target = V(5180, 120, 95)
cam = eas.spawn_actor_from_class(unreal.CineCameraActor, cam_loc, unreal.MathLibrary.find_look_at_rotation(cam_loc, target))
cam.set_actor_label("MenuCamera")
cam.tags = ["MenuCamera"]
cc = cam.get_cine_camera_component()
cc.set_editor_property("current_focal_length", 24.0)
cc.set_editor_property("current_aperture", 2.8)
cc.set_editor_property("constrain_aspect_ratio", False)                       # any window shape, no black bars
fs = cc.focus_settings
fs.focus_method = unreal.CameraFocusMethod.MANUAL
fs.manual_focus_distance = (target - cam_loc).length()
cc.set_editor_property("focus_settings", fs)

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
ws = world.get_world_settings()
ws.set_editor_property("default_game_mode", unreal.load_class(None, "/Script/Genesis.GenesisMenuGameMode"))
les.save_current_level()
print("CM2_MENU_MAP", MAP, len(eas.get_all_level_actors()), "actors, game mode", ws.get_editor_property("default_game_mode").get_name())
