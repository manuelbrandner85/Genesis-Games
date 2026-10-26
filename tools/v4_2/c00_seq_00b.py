"""C00 (runs INSIDE the Unreal Editor): Level Sequence LS_C00_00B - shot 00-B (approved shot list, 2026-10-25).

00-B, 18 s at 24 fps, 85 mm, static with a minimal drift: his hand in his daughter's hand, her thumb moves; focus pull
to the book stack on the nightstand (CR-004 draft, Game Director 2026-10-25; ScriptLock 1.3 still names the photograph).
Run after c00_scene_bedroom.py with GENESIS_SZ_SHOT=00b (that run leaves both figures, the shirt and SZ_Cam_00b in the
saved level L_C00_Schlafzimmer) and c00_anim_00b.py (the 432-frame animations).
- camera cut on SZ_Cam_00b; 1.5 cm drift toward the hands over the shot; manual focus on the hands, pulled to the
  photo between 10 s and 14 s (eased), held to the end
- animation tracks: his body + shirt (same skeleton, the shirt does not rely on leader pose in PIE), his face; her
  body, her outfit pieces, her face
Output: /Game/Genesis/Cinematics/C00/LS_C00_00B (local; the sequence holds references to Epic/MetaHuman content).
"""
import unreal

eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
LEVEL = "/Game/Genesis/Sets/C00_Schlafzimmer/L_C00_Schlafzimmer"
FOLDER, NAME = "/Game/Genesis/Cinematics/C00", "LS_C00_00B"
POSEN = "/Game/Genesis/Characters/C00/Posen"
FPS, END = 24, 432
# focus target: the book stack on the nightstand (CR-004 draft, books instead of the photograph; build_c00_nightstand.py)
PHOTO = unreal.Vector(67.0, -127.0, 62.5)
DISPLAY = unreal.MovieSceneTimeUnit.DISPLAY_RATE

les.load_level(LEVEL)
acts = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
man, tochter, cam = acts["MH_C00_Mann"], acts["MH_C00_Tochter"], acts["SZ_Cam_00b"]
shirt = acts.get("MH_C00_Mann_Shirt")

path = f"{FOLDER}/{NAME}"
if eal.does_asset_exist(path):
    eal.delete_asset(path)
seq = unreal.AssetToolsHelpers.get_asset_tools().create_asset(NAME, FOLDER, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
seq.set_display_rate(unreal.FrameRate(FPS, 1))
seq.set_playback_start(0)
seq.set_playback_end(END)


def comps(actor):
    return {c.get_name(): c for c in actor.get_components_by_class(unreal.SkeletalMeshComponent)}


def anim_track(obj, anim_name):
    b = seq.add_possessable(obj)
    tr = b.add_track(unreal.MovieSceneSkeletalAnimationTrack)
    sec = tr.add_section()
    sec.set_range(0, END)
    pr = sec.get_editor_property("params")
    pr.set_editor_property("animation", eal.load_asset(f"{POSEN}/{anim_name}"))
    sec.set_editor_property("params", pr)
    return b


seq.add_possessable(man)
mc = comps(man)
anim_track(mc["Body"], "A_C00_Mann_Liegen_00B_Built")
anim_track(mc["Face"], "A_C00_Mann_Gesicht_00B_Built")
if shirt:
    seq.add_possessable(shirt)
    anim_track(shirt.skeletal_mesh_component, "A_C00_Mann_Liegen_00B_Built")
seq.add_possessable(tochter)
tc = comps(tochter)
anim_track(tc["Body"], "A_C00_Tochter_Sitzen_00B_Built")
anim_track(tc["Face"], "A_C00_Tochter_Gesicht_00B_Anim_Built")
for n, c in tc.items():                                   # outfit pieces (sweater, jeans, flats) follow her body
    if n not in ("Body", "Face"):
        anim_track(c, "A_C00_Tochter_Sitzen_00B_Built")

# camera: cut, drift, focus pull
cam_b = seq.add_possessable(cam)
cut = seq.add_track(unreal.MovieSceneCameraCutTrack)
cs = cut.add_section()
cs.set_range(0, END)
cs.set_camera_binding_id(seq.get_binding_id(cam_b) if hasattr(seq, "get_binding_id") else cam_b.get_binding_id())
loc, rot = cam.get_actor_location(), cam.get_actor_rotation()
fwd = rot.get_forward_vector()
xf = cam_b.add_track(unreal.MovieScene3DTransformTrack)
xs = xf.add_section()
xs.set_range(0, END)
ch = xs.get_all_channels()                                # Location X Y Z, Rotation X Y Z, Scale X Y Z
end_loc = loc + fwd * 1.5
for i, (a, b) in enumerate(((loc.x, end_loc.x), (loc.y, end_loc.y), (loc.z, end_loc.z),
                            (rot.roll, rot.roll), (rot.pitch, rot.pitch), (rot.yaw, rot.yaw), (1, 1), (1, 1), (1, 1))):
    ch[i].add_key(unreal.FrameNumber(0), a, 0.0, DISPLAY)
    ch[i].add_key(unreal.FrameNumber(END), b, 0.0, DISPLAY)
cc = cam.get_cine_camera_component()
d_hands = cc.focus_settings.manual_focus_distance
d_photo = (PHOTO - loc).length()
cc_b = seq.add_possessable(cc)
ft = cc_b.add_track(unreal.MovieSceneFloatTrack)
ft.set_property_name_and_path("ManualFocusDistance", "FocusSettings.ManualFocusDistance")
fs = ft.add_section()
fs.set_range(0, END)
fch = fs.get_all_channels()[0]
for frame, val in ((0, d_hands), (240, d_hands), (336, d_photo), (END, d_photo)):
    k = fch.add_key(unreal.FrameNumber(frame), val, 0.0, DISPLAY)
    k.set_interpolation_mode(unreal.RichCurveInterpMode.RCIM_CUBIC)
eal.save_loaded_asset(seq, False)
les.save_current_level()
print("C00_SEQ_00B", seq.get_path_name(), "focus", round(d_hands, 1), "->", round(d_photo, 1), "bindings", len(seq.get_bindings()))
