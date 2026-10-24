"""G7 (runs INSIDE the Unreal Editor): replace the R03 graybox objects in L_Flussdorf_G6 with the
G7 assets and add the light of the LED bar.

Positions follow the G6 graybox (tools/v4/g6/g6_level.py: workshop centre 5200/0, 10 x 8 m inside
walls of 24 cm, ceiling at 350 cm), shrunk to 7 x 6 m by g7_room.py (centre 5050/0). The generator keeps its G6 place and interaction id; it is
turned so its control panel, spark plug and fuel filter face the door side (-X), where the player
stands for the inspection (GenesisFlussdorfMissionTest stands 120 cm on -X).
"""
import unreal

LEVEL = "/Game/Genesis/Flussdorf/Maps/L_Flussdorf_G6"
DST = "/Game/Genesis/Flussdorf/R03"
V, R = unreal.Vector, unreal.Rotator
eal = unreal.EditorAssetLibrary
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if les.get_current_level().get_path_name().split(":")[0].split(".")[0] != LEVEL:
    les.load_level(LEVEL)
actors = {a.get_actor_label(): a for a in eas.get_all_level_actors()}

CEILING = 346.0                     # underside of the plank ceiling (SM_R03_Room)
PLACE = {   # label: (asset, location, yaw)
    "Workbench": ("Workbench/SM_R03_Workbench", (5100.0, 238.0, 0.0), 180.0),          # back to the north wall (FBX front is +Y in UE)
    "LightStrip": ("LightBar/SM_R03_LightBar", (5115.0, 218.0, CEILING), 0.0),          # hangs 60 cm over the bench front, hooks clear of the beams
    "PartsShelf": ("PartsShelf/SM_R03_PartsShelf", (5354.0, -120.0, 0.0), 90.0),       # against the east wall, front west
    "Generator_N02": ("Generator_N02/SM_R03_Generator_N02", (5100.0, -200.0, 0.0), 90.0),   # panel side faces the door
}
done = {}
for label, (asset, loc, yaw) in PLACE.items():
    a = actors.get(label)
    if a is None:
        raise RuntimeError("graybox actor missing: " + label)
    mesh = eal.load_asset(f"{DST}/{asset}")
    if mesh is None:
        raise RuntimeError("asset missing: " + asset)
    smc = a.static_mesh_component
    smc.set_static_mesh(mesh)
    smc.set_editor_property("override_materials", [])
    a.set_actor_scale3d(V(1, 1, 1))
    a.set_actor_location_and_rotation(V(*loc), R(0, 0, yaw), False, True)
    a.set_folder_path("R03_Werkstatt")
    done[label] = {"mesh": mesh.get_name(), "loc": loc, "yaw": yaw}

# Room shell and set dressing (all share the room origin = workshop centre on the floor) replace the
# graybox walls, lintel, inner ceiling and floor slab of g7_room.py; the graybox roof stays as the outer roof.
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    if lbl.startswith("Workshop_") and lbl != "Workshop_Roof":
        eas.destroy_actor(a)
for label, asset in (("R03_Room", "Room/SM_R03_Room"), ("R03_ToolWall", "Dressing/ToolWall/SM_R03_ToolWall"),
                     ("R03_BenchItems", "Dressing/BenchItems/SM_R03_BenchItems"), ("R03_FloorItems", "Dressing/FloorItems/SM_R03_FloorItems")):
    mesh = eal.load_asset(f"{DST}/{asset}")
    if mesh is None:
        raise RuntimeError("asset missing: " + asset)
    a = actors.get(label) or eas.spawn_actor_from_object(mesh, V(5050, 0, 0), R(0, 0, 0))
    a.set_actor_label(label)
    a.static_mesh_component.set_static_mesh(mesh)
    a.set_actor_location_and_rotation(V(5050, 0, 0), R(0, 0, 0), False, True)
    a.set_folder_path("R03_Werkstatt")
    done[label] = {"mesh": mesh.get_name()}

# LED bar light: rect light under the diffuser, 4000 K, 4000 lm, pointing down
old = actors.get("R03_LightBar_Light")
if old:
    eas.destroy_actor(old)
bar = actors["LightStrip"]
sock = bar.static_mesh_component.get_socket_location("Light")
lt = eas.spawn_actor_from_class(unreal.RectLight, sock - V(0, 0, 0.5), R(-90, 0, 0))
lt.set_actor_label("R03_LightBar_Light")
lt.set_folder_path("R03_Werkstatt")
lc = lt.get_component_by_class(unreal.RectLightComponent)
lc.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
lc.set_editor_property("intensity", 4000.0)
lc.set_editor_property("use_temperature", True)
lc.set_editor_property("temperature", 4000.0)
lc.set_editor_property("source_width", 148.0)
lc.set_editor_property("source_height", 5.0)
lc.set_editor_property("barn_door_angle", 0.0)
lc.set_editor_property("attenuation_radius", 900.0)
lc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
# Interior exposure: the village PPV is Sunny 16 (EV 15) everywhere; a workshop lit by ~300 lux needs
# about EV 6 (ISO 800, 1/60 s, f/2.8). Bounded volume over the R03 interior, soft blend at the door.
old = actors.get("PPV_R03_Interior")
if old:
    eas.destroy_actor(old)
ppv = eas.spawn_actor_from_class(unreal.PostProcessVolume, V(5050, 0, 175))
ppv.set_actor_label("PPV_R03_Interior")
ppv.set_folder_path("R03_Werkstatt")
ppv.set_actor_scale3d(V(3.26, 2.76, 1.75))          # default brush 200 cm -> inner 652 x 552 x 350 cm
ppv.set_editor_property("unbound", False)
ppv.set_editor_property("priority", 1.0)
ppv.set_editor_property("blend_radius", 150.0)
st = ppv.settings
for prop, val in (("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL), ("auto_exposure_apply_physical_camera_exposure", True),
                  ("camera_iso", 800.0), ("camera_shutter_speed", 60.0), ("depth_of_field_fstop", 2.8)):
    st.set_editor_property(prop, val)
    st.set_editor_property("override_" + prop, True)
ppv.set_editor_property("settings", st)
les.save_current_level()

# read back what is really set
rb = {}
for label in PLACE:
    a = [x for x in eas.get_all_level_actors() if x.get_actor_label() == label][0]
    l, r = a.get_actor_location(), a.get_actor_rotation()
    rb[label] = {"mesh": a.static_mesh_component.static_mesh.get_name(), "loc": [round(l.x, 1), round(l.y, 1), round(l.z, 1)],
                 "yaw": round(r.yaw, 1), "scale": a.get_actor_scale3d().x}
lc = [x for x in eas.get_all_level_actors() if x.get_actor_label() == "R03_LightBar_Light"][0].get_component_by_class(unreal.RectLightComponent)
rb["light"] = {"lumens": lc.get_editor_property("intensity"), "units": str(lc.get_editor_property("intensity_units")),
               "kelvin": lc.get_editor_property("temperature"), "loc": [round(v, 1) for v in (sock.x, sock.y, sock.z)]}
print("G7_LEVEL", rb)
