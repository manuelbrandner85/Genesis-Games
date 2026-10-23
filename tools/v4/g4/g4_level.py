"""G4 (runs INSIDE the Unreal Editor): technical test level for the pallet hand-off.

Empty level without World Partition, saved before use: sun + sky atmosphere + sky light +
height fog, physical manual exposure (Sunny 16: ISO 100, 1/100 s, f/16), a 60 m concrete slab,
the pallet at the origin and a 50 mm cine camera at eye height that the viewport pilots.
Also sets the Nanite fallback to the full mesh (it is only ~8k triangles), so hardware ray
traced Lumen shadows/reflections use the real geometry.
"""
import unreal

LEVEL = "/Game/Genesis/TechSmoke/Maps/L_TechSmoke"
MESH = "/Game/Genesis/TechSmoke/PalletEUR/SM_TechSmoke_PalletEUR"
FLOOR_MAT = "/Game/Genesis/TechSmoke/Maps/M_Review_Concrete"

eal = unreal.EditorAssetLibrary
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mel = unreal.MaterialEditingLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()

# Nanite fallback = full mesh.
mesh = eal.load_asset(MESH)
ns = mesh.get_editor_property("nanite_settings")
ns.set_editor_property("fallback_percent_triangles", 1.0)
ns.set_editor_property("fallback_relative_error", 0.0)
mesh.set_editor_property("nanite_settings", ns)
eal.save_loaded_asset(mesh)

# Fresh empty level (no World Partition), saved before anything is placed.
if eal.does_asset_exist(LEVEL):
    les.load_level(LEVEL)
    for a in eas.get_all_level_actors():
        eas.destroy_actor(a)
else:
    les.new_level(LEVEL)
les.save_current_level()

# Concrete slab material: albedo ~0.18-0.30 with large and medium variation, rough 0.75-0.9.
if not eal.does_asset_exist(FLOOR_MAT):
    m = at.create_asset("M_Review_Concrete", "/Game/Genesis/TechSmoke/Maps", unreal.Material, unreal.MaterialFactoryNew())
    def noise(scale, x, y):
        n = mel.create_material_expression(m, unreal.MaterialExpressionNoise, x, y)
        n.set_editor_property("scale", scale)
        n.set_editor_property("levels", 5)
        n.set_editor_property("output_min", 0.0)
        n.set_editor_property("output_max", 1.0)
        return n
    big, mid = noise(0.004, -900, -100), noise(0.06, -900, 200)
    lerp = mel.create_material_expression(m, unreal.MaterialExpressionLinearInterpolate, -500, 0)
    a = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -700, -300)
    a.set_editor_property("constant", unreal.LinearColor(0.17, 0.165, 0.155, 1))
    b = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -700, -200)
    b.set_editor_property("constant", unreal.LinearColor(0.31, 0.30, 0.285, 1))
    mul = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -700, 100)
    mel.connect_material_expressions(big, "", mul, "A")
    mel.connect_material_expressions(mid, "", mul, "B")
    mel.connect_material_expressions(a, "", lerp, "A")
    mel.connect_material_expressions(b, "", lerp, "B")
    mel.connect_material_expressions(mul, "", lerp, "Alpha")
    mel.connect_material_property(lerp, "", unreal.MaterialProperty.MP_BASE_COLOR)
    r = mel.create_material_expression(m, unreal.MaterialExpressionLinearInterpolate, -500, 300)
    r.set_editor_property("const_a", 0.9)
    r.set_editor_property("const_b", 0.75)
    mel.connect_material_expressions(mid, "", r, "Alpha")
    mel.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)

V = unreal.Vector
R = unreal.Rotator

floor = eas.spawn_actor_from_object(eal.load_asset("/Engine/BasicShapes/Plane"), V(0, 0, 0))
floor.set_actor_label("Review_Floor")
floor.set_actor_scale3d(V(60, 60, 1))
floor.static_mesh_component.set_material(0, eal.load_asset(FLOOR_MAT))

pallet = eas.spawn_actor_from_object(mesh, V(0, 0, 0))
pallet.set_actor_label("SM_TechSmoke_PalletEUR")

# Daylight: sun 38 deg high, ~90 000 lx direct; physical sky; real-time sky light capture.
sun = eas.spawn_actor_from_class(unreal.DirectionalLight, V(0, 0, 500), R(0, -38, 215))
sun.set_actor_label("Sun")
lc = sun.light_component
lc.set_editor_property("intensity", 90000.0)
lc.set_editor_property("light_source_angle", 0.53)
lc.set_editor_property("atmosphere_sun_light", True)
lc.set_editor_property("temperature", 5600.0)
lc.set_editor_property("use_temperature", True)
eas.spawn_actor_from_class(unreal.SkyAtmosphere, V(0, 0, 0)).set_actor_label("SkyAtmosphere")
sky = eas.spawn_actor_from_class(unreal.SkyLight, V(0, 0, 300))
sky.set_actor_label("SkyLight")
sky.light_component.set_editor_property("real_time_capture", True)
fog = eas.spawn_actor_from_class(unreal.ExponentialHeightFog, V(0, 0, 0))
fog.set_actor_label("HeightFog")
fog.component.set_editor_property("fog_density", 0.004)

# Manual physical exposure (Sunny 16), filmic defaults, no game-look effects.
ppv = eas.spawn_actor_from_class(unreal.PostProcessVolume, V(0, 0, 0))
ppv.set_actor_label("PPV_Exposure")
ppv.set_editor_property("unbound", True)
s = ppv.settings
for prop, val in (("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL),
                  ("auto_exposure_apply_physical_camera_exposure", True),
                  ("camera_iso", 100.0), ("camera_shutter_speed", 100.0), ("depth_of_field_fstop", 16.0),
                  ("bloom_intensity", 0.1), ("lens_flare_intensity", 0.0), ("scene_fringe_intensity", 0.0),
                  ("vignette_intensity", 0.15), ("film_grain_intensity", 0.0)):
    s.set_editor_property(prop, val)
    s.set_editor_property("override_" + prop, True)
ppv.set_editor_property("settings", s)

# Cine camera: 50 mm on full frame at 1.45 m, looking at the pallet corner from 3 m.
cam = eas.spawn_actor_from_class(unreal.CineCameraActor, V(175, -195, 145))
cam.set_actor_label("Review_Cam")
target = V(0, 0, 6)
cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(cam.get_actor_location(), target), False)
cc = cam.get_cine_camera_component()
fb = cc.get_editor_property("filmback")
fb.set_editor_property("sensor_width", 36.0)
fb.set_editor_property("sensor_height", 24.0)
cc.set_editor_property("filmback", fb)
cc.set_editor_property("current_focal_length", 50.0)
cc.set_editor_property("current_aperture", 16.0)
fs = cc.get_editor_property("focus_settings")
fs.set_editor_property("manual_focus_distance", unreal.MathLibrary.vector_distance(cam.get_actor_location(), target))
cc.set_editor_property("focus_settings", fs)

detail = eas.spawn_actor_from_class(unreal.CineCameraActor, V(98, -95, 42))
detail.set_actor_label("Review_Detail")
dt = V(52, -36, 7)
detail.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(detail.get_actor_location(), dt), False)
dc = detail.get_cine_camera_component()
dc.set_editor_property("filmback", fb)
dc.set_editor_property("current_focal_length", 50.0)
dc.set_editor_property("current_aperture", 16.0)
dfs = dc.get_editor_property("focus_settings")
dfs.set_editor_property("manual_focus_distance", unreal.MathLibrary.vector_distance(detail.get_actor_location(), dt))
dc.set_editor_property("focus_settings", dfs)

les.save_current_level()
les.pilot_level_actor(cam)
print("G4_LEVEL ok", LEVEL, [a.get_actor_label() for a in eas.get_all_level_actors()])
