"""C00 (runs INSIDE the Unreal Editor, lab level open): sweep the local MetaHuman texture-synthesis skins.

The bundled synthesis model (TS-1.3, 153 scanned identities, 1024 px) is local - no cloud. For one
candidate character every FaceTextureIndex is applied and the face is captured as base color
(albedo: age spots, skin structure, no exposure dependence). Output: <out>/skin_<index>.png.

Env: GENESIS_MH_CHAR (asset path), GENESIS_MH_OUT, GENESIS_MH_RANGE "start,stop".
"""
import os
import unreal

CHAR = os.environ["GENESIS_MH_CHAR"]
OUT = os.environ["GENESIS_MH_OUT"]
START, STOP = (int(x) for x in os.environ.get("GENESIS_MH_RANGE", "0,153").split(","))
V = unreal.Vector
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mh = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

ch = unreal.EditorAssetLibrary.load_asset(CHAR)
if not mh.is_object_added_for_editing(ch) and not mh.try_add_object_to_edit(ch):
    raise RuntimeError("cannot edit " + CHAR)
actor = mh.spawn_meta_human_actor(ch, True)                     # own transient preview actor
actor.set_actor_location_and_rotation(V(0, 400, 0), unreal.Rotator(yaw=-90), False, True)   # beside the lab figure, face +X
mh.assemble_for_preview(ch)
height = next(float(c.target_measurement) for c in mh.get_body_constraints(ch, False) if str(c.name) == "Height")
head = actor.get_actor_location() + V(0, 0, height * 0.93)
cam_loc = head + V(110, 0, 2)
cap = eas.spawn_actor_from_class(unreal.SceneCapture2D, cam_loc, unreal.MathLibrary.find_look_at_rotation(cam_loc, head))
comp = cap.capture_component2d
comp.set_editor_property("fov_angle", 16.0)
comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_BASE_COLOR)
comp.set_editor_property("capture_every_frame", False)
rt = unreal.RenderingLibrary.create_render_target2d(world, 384, 480, unreal.TextureRenderTargetFormat.RTF_RGBA8)
comp.set_editor_property("texture_target", rt)
original = ch.skin_settings
os.makedirs(OUT, exist_ok=True)
done = []
for i in range(START, STOP):
    ss = ch.skin_settings
    skin = ss.skin
    skin.face_texture_index = i
    ss.skin = skin
    mh.commit_skin_settings(ch, ss)
    for _ in range(2):
        comp.capture_scene()
    unreal.RenderingLibrary.export_render_target(world, rt, OUT, f"skin_{i:03d}.png")
    done.append(i)
mh.commit_skin_settings(ch, original)
eas.destroy_actor(cap)
eas.destroy_actor(actor)
print("SKIN_SWEEP", CHAR, done[0], done[-1], len(done))
