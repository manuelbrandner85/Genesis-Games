# WK-M02-002/003: creates the proxy character appearances and the test level.
# Run: UnrealEditor-Cmd.exe Genesis.uproject -run=pythonscript -script="<this file>"
# Writes measurements to Saved/Automation/WK-M02-002/measurements.json.
import json
import os

import unreal

ASSET_TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary

APPEARANCE_DIR = "/Game/Genesis/Characters/Appearances"
MAP_PATH = "/Game/Maps/L_GenesisTest"
ANIM_CLASS = "/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed.ABP_Unarmed_C"
SKELETON = "/Game/Characters/Mannequins/Meshes/SK_Mannequin.SK_Mannequin"

PROXIES = {
    "DA_Proxy_Adult_M": "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
    "DA_Proxy_Adult_F": "/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple",
}


def log(msg):
    unreal.log("GENESIS_BUILD " + msg)


def create_or_load(name, path, cls, factory):
    full = path + "/" + name
    if EAL.does_asset_exist(full):
        return EAL.load_asset(full)
    return ASSET_TOOLS.create_asset(name, path, cls, factory)


def build_appearances():
    anim_class = unreal.load_class(None, ANIM_CLASS)
    measurements = {}
    for name, mesh_path in PROXIES.items():
        mesh = unreal.load_asset(mesh_path)
        m = unreal.GenesisCharacterLibrary.measure_skeletal_mesh(mesh, "head")
        half = round(m.height_cm / 2.0, 1)

        factory = unreal.DataAssetFactory()
        factory.set_editor_property("data_asset_class", unreal.GenesisCharacterAppearance)
        da = create_or_load(name, APPEARANCE_DIR, unreal.GenesisCharacterAppearance, factory)
        da.set_editor_property("release_state", "PROXY")
        da.set_editor_property("mesh", mesh)
        da.set_editor_property("anim_class", anim_class)
        da.set_editor_property("capsule_radius", 34.0)
        da.set_editor_property("capsule_half_height", half)
        da.set_editor_property(
            "mesh_relative_transform",
            unreal.Transform(
                location=unreal.Vector(0.0, 0.0, -half - m.foot_z_cm),
                rotation=unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0),
                scale=unreal.Vector(1.0, 1.0, 1.0),
            ),
        )
        EAL.save_loaded_asset(da)
        measurements[name] = {
            "mesh": mesh_path,
            "height_cm": round(m.height_cm, 2),
            "anchor_height_cm": round(m.anchor_height_cm, 2),
            "foot_z_cm": round(m.foot_z_cm, 2),
            "capsule_half_height": half,
        }
        log("%s height=%.2f anchor=%.2f foot=%.2f" % (name, m.height_cm, m.anchor_height_cm, m.foot_z_cm))
    return measurements


def spawn_mesh(mesh_path, location, scale, rotation=(0.0, 0.0, 0.0), label=None):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*location), unreal.Rotator(*rotation))
    comp = actor.static_mesh_component
    comp.set_static_mesh(unreal.load_asset(mesh_path))
    actor.set_actor_scale3d(unreal.Vector(*scale))
    if label:
        actor.set_actor_label(label)
    return actor


def build_level():
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if EAL.does_asset_exist(MAP_PATH):
        les.load_level(MAP_PATH)
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            unreal.EditorLevelLibrary.destroy_actor(a)
    else:
        les.new_level(MAP_PATH)

    cube = "/Engine/BasicShapes/Cube.Cube"
    plane = "/Engine/BasicShapes/Plane.Plane"

    # 120 x 120 m Boden.
    spawn_mesh(plane, (0, 0, 0), (120, 120, 1), label="Boden")
    # Treppe: 8 Stufen, 17 cm Steigung, 29 cm Auftritt, 2 m breit.
    for i in range(8):
        h = 17.0 * (i + 1)
        spawn_mesh(cube, (600 + i * 29, 0, h / 2.0), (0.29, 2.0, h / 100.0), label="Treppe_%02d" % (i + 1))
    spawn_mesh(cube, (600 + 8 * 29 + 150, 0, 136 / 2.0), (3.0, 2.0, 1.36), label="Treppe_Podest")
    # Rampe 10 Grad.
    spawn_mesh(cube, (0, 700, 40), (6.0, 2.5, 0.2), rotation=(0.0, -10.0, 0.0), label="Rampe_10Grad")
    # Wand 2,5 m fuer Kamerakollision.
    spawn_mesh(cube, (-500, 0, 125), (0.25, 8.0, 2.5), label="Wand_Kamera")
    # Durchgang 1 m breit, 2,1 m hoch.
    spawn_mesh(cube, (-200, -600, 105), (0.25, 1.5, 2.1), label="Durchgang_L")
    spawn_mesh(cube, (-200, -350, 105), (0.25, 1.5, 2.1), label="Durchgang_R")
    spawn_mesh(cube, (-200, -475, 222), (0.25, 4.0, 0.25), label="Durchgang_Sturz")

    start = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0, 0, 100), unreal.Rotator(0, 0, 0))
    start.set_actor_label("PlayerStart")

    # Licht: Sonne + Atmosphaere + Himmel, physikalische Einheiten.
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 1000), unreal.Rotator(0.0, -42.0, 35.0))
    sun.set_actor_label("Sonne")
    sc = sun.light_component
    sc.set_editor_property("intensity", 90000.0)
    sc.set_editor_property("atmosphere_sun_light", True)
    sc.set_editor_property("light_source_angle", 0.5357)
    sc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)

    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0)).set_actor_label("Atmosphaere")
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 500))
    sky.set_actor_label("Himmelslicht")
    sky.light_component.set_editor_property("real_time_capture", True)
    sky.light_component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.VolumetricCloud, unreal.Vector(0, 0, 0)).set_actor_label("Wolken")
    fog = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0))
    fog.set_actor_label("Hoehennebel")
    fc = fog.component
    fc.set_editor_property("fog_density", 0.004)
    fc.set_editor_property("enable_volumetric_fog", True)

    # Manuelle physikalische Belichtung, Sunny-16: ISO 100, 1/100 s, f/16 -> EV100 ~ 14,6.
    ppv = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0))
    ppv.set_actor_label("Belichtung")
    ppv.set_editor_property("unbound", True)
    s = ppv.settings
    s.set_editor_property("override_auto_exposure_method", True)
    s.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    s.set_editor_property("override_auto_exposure_bias", True)
    s.set_editor_property("auto_exposure_bias", 0.0)
    s.set_editor_property("override_auto_exposure_apply_physical_camera_exposure", True)
    s.set_editor_property("auto_exposure_apply_physical_camera_exposure", True)
    s.set_editor_property("override_camera_iso", True)
    s.set_editor_property("camera_iso", 100.0)
    s.set_editor_property("override_camera_shutter_speed", True)
    s.set_editor_property("camera_shutter_speed", 100.0)
    s.set_editor_property("override_depth_of_field_fstop", True)
    s.set_editor_property("depth_of_field_fstop", 16.0)
    ppv.set_editor_property("settings", s)

    les.save_current_level()
    log("level saved %s actors=%d" % (MAP_PATH, len(unreal.EditorLevelLibrary.get_all_level_actors())))


def main():
    out_dir = os.path.join(unreal.Paths.project_saved_dir(), "Automation", "WK-M02-002")
    os.makedirs(out_dir, exist_ok=True)
    measurements = build_appearances()
    with open(os.path.join(out_dir, "measurements.json"), "w", encoding="utf-8") as f:
        json.dump(measurements, f, indent=2)
    build_level()
    log("done")


main()
