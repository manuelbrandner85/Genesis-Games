"""C00 (runs INSIDE the Unreal Editor): MetaHuman character lab for the C00 figures.

Creates L_C00_CharacterLab (neutral studio light, grey backdrop) and renders front portraits of the
given MetaHuman Creator presets (bundled with UE 5.8, no download) so the best base for CHR_C00_MANN /
CHR_C00_TOCHTER can be chosen against the approved references (GD-2026-10-24-02).
Presets are duplicated into /Game/Genesis/Characters/C00/Candidates before editing; engine content
stays untouched. Only local MetaHuman functions are used - no Epic cloud request.

Args via env GENESIS_MH_PRESETS="Walter,Victor" and GENESIS_MH_OUT=<dir for PNGs>.
"""
import os
import unreal

LAB = "/Game/Genesis/Characters/C00/L_C00_CharacterLab"
CAND = "/Game/Genesis/Characters/C00/Candidates"
PRESETS = [p.strip() for p in os.environ.get("GENESIS_MH_PRESETS", "Walter").split(",") if p.strip()]
OUT = os.environ.get("GENESIS_MH_OUT", unreal.Paths.project_saved_dir() + "C00Lab")
V, R = unreal.Vector, unreal.Rotator
EV = float(os.environ.get("GENESIS_MH_EV", "8.9"))
eal = unreal.EditorAssetLibrary
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mh = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)

if eal.does_asset_exist(LAB):
    les.load_level(LAB)
else:
    les.new_level(LAB)
    # studio: grey cyclorama, soft key/fill/rim, sky light for ambient
    cube = eal.load_asset("/Engine/BasicShapes/Plane")
    box = eal.load_asset("/Engine/BasicShapes/Cube")
    back = eas.spawn_actor_from_object(box, V(-250, 0, 150), R(0, 0, 0))   # backdrop wall behind the head
    back.set_actor_scale3d(V(0.1, 8, 4))
    bl = eas.spawn_actor_from_class(unreal.RectLight, V(-60, 0, 320), unreal.MathLibrary.find_look_at_rotation(V(-60, 0, 320), V(-245, 0, 150)))
    bl.set_actor_label("BackdropLight")
    blc = bl.get_component_by_class(unreal.RectLightComponent)
    blc.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    blc.set_editor_property("intensity", 6000.0)
    blc.set_editor_property("source_width", 200.0)
    blc.set_editor_property("source_height", 100.0)
    back.set_actor_label("Backdrop")
    floor = eas.spawn_actor_from_object(cube, V(0, 0, 0), R(0, 0, 0))
    floor.set_actor_scale3d(V(10, 10, 1))
    floor.set_actor_label("Floor")
    look = unreal.MathLibrary.find_look_at_rotation
    head_target = V(0, 0, 160)
    # soft studio daylight like the approved references: big key front-left, fill front-right, rim behind
    for label, loc, lm, k, size in (("Key", V(150, -110, 200), 16000.0, 5200.0, 120.0),
                                    ("Fill", V(170, 130, 160), 7000.0, 5600.0, 150.0),
                                    ("Rim", V(-110, 80, 210), 2500.0, 6000.0, 60.0)):
        lt = eas.spawn_actor_from_class(unreal.RectLight, loc, look(loc, head_target))
        lt.set_actor_label(label)
        lc = lt.get_component_by_class(unreal.RectLightComponent)
        lc.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
        lc.set_editor_property("intensity", lm)
        lc.set_editor_property("use_temperature", True)
        lc.set_editor_property("temperature", k)
        lc.set_editor_property("source_width", size)
        lc.set_editor_property("source_height", size)
    sky = eas.spawn_actor_from_class(unreal.SkyLight, V(0, 0, 400))
    sky.light_component.set_editor_property("intensity", 0.6)
    ppv = eas.spawn_actor_from_class(unreal.PostProcessVolume, V(0, 0, 0))
    ppv.set_editor_property("unbound", True)
    st = ppv.settings
    for prop, val in (("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL), ("auto_exposure_apply_physical_camera_exposure", True),
                      ("camera_iso", 1600.0), ("camera_shutter_speed", 60.0), ("depth_of_field_fstop", 5.6)):
        st.set_editor_property(prop, val)
        st.set_editor_property("override_" + prop, True)
    ppv.set_editor_property("settings", st)
    les.save_current_level()

os.makedirs(OUT, exist_ok=True)
results = {}
for name in PRESETS:
    src = f"/MetaHumanCharacter/Optional/Presets/{name}"
    dst = name if name.startswith("/Game/") else f"{CAND}/MHC_{name}"       # a full path renders a built C00 figure
    name = name.rsplit("/", 1)[-1]
    if not eal.does_asset_exist(dst):
        if not eal.duplicate_asset(src, dst):
            results[name] = "duplicate failed"
            continue
    ch = eal.load_asset(dst)
    if not mh.is_object_added_for_editing(ch) and not mh.try_add_object_to_edit(ch):
        results[name] = "edit failed"
        continue
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("MH_"):
            eas.destroy_actor(a)
    if os.environ.get("GENESIS_MH_FACE_TEX"):                    # try another local synthesis skin on this face
        ss = ch.skin_settings
        skin = ss.skin
        skin.face_texture_index = int(os.environ["GENESIS_MH_FACE_TEX"])
        if os.environ.get("GENESIS_MH_SKIN_UV"):
            skin.u, skin.v = (float(x) for x in os.environ["GENESIS_MH_SKIN_UV"].split(","))
        ss.skin = skin
        mh.commit_skin_settings(ch, ss)
    actor = mh.spawn_meta_human_actor(ch, True)
    actor.set_actor_label("MH_" + name)
    actor.set_actor_location_and_rotation(V(0, 0, 0), R(0, 0, -90), False, True)  # MetaHuman faces +Y at yaw 0: yaw -90 turns the face to +X (camera side)
    mh.assemble_for_preview(ch)
    if os.environ.get("GENESIS_MH_GARMENT"):                    # own clothing follows the body (leader pose)
        body = next(c for c in actor.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Body")
        wear = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, actor.get_actor_location(), actor.get_actor_rotation())
        wear.set_actor_label("MH_Garment")
        garment = wear.skeletal_mesh_component
        garment.set_skeletal_mesh_asset(eal.load_asset(os.environ["GENESIS_MH_GARMENT"]))
        garment.attach_to_component(body, "", unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET,
                                    unreal.AttachmentRule.SNAP_TO_TARGET, False)
        garment.set_leader_pose_component(body)
    if os.environ.get("GENESIS_MH_GROOM"):                      # own hair groom on the head (rest pose)
        face = next(c for c in actor.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Face")
        ga = eas.spawn_actor_from_class(unreal.GroomActor, actor.get_actor_location(), actor.get_actor_rotation())
        ga.set_actor_label("MH_Groom")
        gc = ga.get_component_by_class(unreal.GroomComponent)
        gc.set_editor_property("groom_asset", eal.load_asset(os.environ["GENESIS_MH_GROOM"]))
        if os.environ.get("GENESIS_MH_GROOM_MAT"):
            gc.set_material(0, eal.load_asset(os.environ["GENESIS_MH_GROOM_MAT"]))
        ga.attach_to_component(face, "", unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET,
                               unreal.AttachmentRule.KEEP_WORLD, False)
    bc = {str(c.name): round(float(c.target_measurement), 1) for c in mh.get_body_constraints(ch, False)
          if str(c.name) in ("Height", "Masculine/Feminine", "Fat", "Muscularity")}
    sk = ch.skin_settings.skin
    results[name] = {"body": bc, "skin_uv": [round(sk.u, 2), round(sk.v, 2)], "face_tex": sk.face_texture_index}
    # head portrait through the real viewport renderer (level PPV exposure applies): 85 mm cine camera.
    # The screenshot is written a few frames later, so the actor stays until the next lab run.
    head = actor.get_actor_location() + V(0, 0, bc.get("Height", 175.0) * 0.93)
    cam_loc = head + V(130, 0, 2)
    if os.environ.get("GENESIS_MH_WIDE"):                       # waist-up framing for clothing checks
        head = actor.get_actor_location() + V(0, 0, 125)
        cam_loc = head + V(330, -60, 10)
    cam = eas.spawn_actor_from_class(unreal.CineCameraActor, cam_loc, unreal.MathLibrary.find_look_at_rotation(cam_loc, head))
    cam.set_actor_label("MH_Cam")
    cc = cam.get_cine_camera_component()
    cc.set_editor_property("current_focal_length", 85.0)
    cc.set_editor_property("current_aperture", 5.6)
    cc.set_editor_property("constrain_aspect_ratio", False)
    fs = cc.focus_settings
    fs.focus_method = unreal.CameraFocusMethod.MANUAL
    fs.manual_focus_distance = (head - cam_loc).length()
    cc.set_editor_property("focus_settings", fs)
    shot = name + os.environ.get("GENESIS_MH_SUFFIX", "")
    if os.environ.get("GENESIS_MH_EYES") != "only":
      unreal.AutomationLibrary.take_high_res_screenshot(1024, 1280, f"{OUT}/{shot}.png", cam, False, False,
                                                        unreal.ComparisonTolerance.LOW, "", 1.0)
    results[name]["png"] = f"{OUT}/{name}.png"
    if os.environ.get("GENESIS_MH_EYES"):                       # close-up of the eyes (iris colour check), own run
        eyes = head + V(8, 0, float(os.environ.get("GENESIS_MH_EYE_DZ", "4")))
        cam2_loc = eyes + (V(32, -38, 2) if os.environ.get("GENESIS_MH_EYE_SIDE") else V(55, 0, 0))   # side view shows lash length
        cam2 = eas.spawn_actor_from_class(unreal.CineCameraActor, cam2_loc, unreal.MathLibrary.find_look_at_rotation(cam2_loc, eyes))
        cam2.set_actor_label("MH_CamEyes")
        c2 = cam2.get_cine_camera_component()
        c2.set_editor_property("current_focal_length", 100.0)
        c2.set_editor_property("constrain_aspect_ratio", False)
        f2 = c2.focus_settings
        f2.focus_method = unreal.CameraFocusMethod.MANUAL
        f2.manual_focus_distance = 55.0
        c2.set_editor_property("focus_settings", f2)
        unreal.AutomationLibrary.take_high_res_screenshot(1280, 512, f"{OUT}/{shot}_augen.png", cam2, False, False,
                                                          unreal.ComparisonTolerance.LOW, "", 1.0)
print("MH_LAB", results)
