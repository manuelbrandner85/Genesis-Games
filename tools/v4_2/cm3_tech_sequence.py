"""CM3 (runs INSIDE the Unreal Editor): create LS_C00_TechTest, a NON-CANONICAL technical stand-in for C00.

6 s camera move (spawnable cine camera + camera cut) through workshop R03 of L_Flussdorf_G6. No
characters, no text, no story: it only proves the contract chain play -> skip/end -> commit -> hand-back.
The real C00 is produced only after the director's approval of ScriptLock 1.1 ("JA zu Vorschlag 11").
"""
import unreal

PKG, NAME = "/Game/Genesis/Cinematics/Tech", "LS_C00_TechTest"
FPS, SECONDS = 24, 6
eal = unreal.EditorAssetLibrary
if eal.does_asset_exist(f"{PKG}/{NAME}"):
    eal.delete_asset(f"{PKG}/{NAME}")
seq = unreal.AssetToolsHelpers.get_asset_tools().create_asset(NAME, PKG, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
seq.set_display_rate(unreal.FrameRate(FPS, 1))
end = FPS * SECONDS
seq.set_playback_start(0)
seq.set_playback_end(end)

cam = seq.add_spawnable_from_class(unreal.CineCameraActor)
cam.set_display_name("TechCamera")
section = cam.add_track(unreal.MovieScene3DTransformTrack).add_section()
section.set_range(0, end)
V = unreal.Vector
look = unreal.MathLibrary.find_look_at_rotation
keys = [  # (frame, location, look-at target): slow dolly from the door side towards the bench
    (0, V(4760, -150, 165), V(5150, 200, 100)),
    (end, V(4960, 60, 140), V(5150, 240, 95)),
]
ch = section.get_all_channels()          # loc x y z, rot roll pitch yaw, scale x y z
for frame, loc, target in keys:
    rot = look(loc, target)
    for i, v in enumerate((loc.x, loc.y, loc.z, rot.roll, rot.pitch, rot.yaw, 1.0, 1.0, 1.0)):
        ch[i].add_key(unreal.FrameNumber(frame), v, interpolation=unreal.MovieSceneKeyInterpolation.AUTO)

cut = seq.add_track(unreal.MovieSceneCameraCutTrack).add_section()
cut.set_range(0, end)
cut.set_camera_binding_id(seq.get_binding_id(cam))
eal.save_loaded_asset(seq)
print("CM3_SEQUENCE", seq.get_path_name(), "frames", end, "bindings", len(seq.get_bindings()))
