"""G4 (runs INSIDE the Unreal Editor): render the review cameras with Movie Render Queue.

One level sequence per cine camera (camera cut, 1 frame), rendered by the PIE executor with
Lumen warm-up and temporal anti-aliasing. Independent of the editor viewport, so navigating
in the editor while it runs does not change the picture. Output: Saved/G4/Render/<sequence>.png
"""
import os

import unreal

LEVEL = "/Game/Genesis/TechSmoke/Maps/L_TechSmoke"
SEQ_DIR = "/Game/Genesis/TechSmoke/Maps"
OUT_DIR = os.path.join(unreal.Paths.project_dir(), "Saved", "G4", "Render")
CAMERAS = {  # label: (location cm, look-at target cm, focal length mm, aperture f)
    "Review_Cam": ((175.0, -195.0, 145.0), (0.0, 0.0, 6.0), 50.0, 8.0),
    "Review_Detail": ((98.0, -95.0, 42.0), (52.0, -36.0, 7.0), 50.0, 5.6),
}

at = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

les.eject_pilot_level_actor()
if les.get_current_level().get_path_name().split(":")[0].split(".")[0] != LEVEL:
    les.load_level(LEVEL)

sequences = []
for label, (loc, tgt, focal, fstop) in CAMERAS.items():
    cam = next(a for a in eas.get_all_level_actors() if a.get_actor_label() == label)
    loc, tgt = unreal.Vector(*loc), unreal.Vector(*tgt)
    cam.set_actor_location(loc, False, False)
    cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(loc, tgt), False)
    cc = cam.get_cine_camera_component()
    cc.set_editor_property("current_focal_length", focal)
    cc.set_editor_property("current_aperture", fstop)
    fs = cc.get_editor_property("focus_settings")
    fs.set_editor_property("focus_method", unreal.CameraFocusMethod.MANUAL)
    fs.set_editor_property("manual_focus_distance", unreal.MathLibrary.vector_distance(loc, tgt))
    cc.set_editor_property("focus_settings", fs)

    name = f"LS_{label}"
    path = f"{SEQ_DIR}/{name}"
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    seq = at.create_asset(name, SEQ_DIR, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    seq.set_display_rate(unreal.FrameRate(24, 1))
    seq.set_playback_start(0)
    seq.set_playback_end(1)
    binding = seq.add_possessable(cam)
    track = seq.add_track(unreal.MovieSceneCameraCutTrack)
    section = track.add_section()
    section.set_range(0, 1)
    section.set_camera_binding_id(seq.get_binding_id(binding))
    eal.save_loaded_asset(seq)
    sequences.append(seq)

les.save_current_level()

mqs = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
queue = mqs.get_queue()
queue.delete_all_jobs()
os.makedirs(OUT_DIR, exist_ok=True)
for seq in sequences:
    job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
    job.job_name = seq.get_name()
    job.map = unreal.SoftObjectPath(f"{LEVEL}.{LEVEL.split('/')[-1]}")
    job.sequence = unreal.SoftObjectPath(seq.get_path_name())
    cfg = job.get_configuration()
    out = cfg.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
    out.output_directory = unreal.DirectoryPath(OUT_DIR)
    out.output_resolution = unreal.IntPoint(1920, 1280)
    out.file_name_format = "{sequence_name}"
    out.override_existing_output = True
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
    aa = cfg.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
    aa.override_anti_aliasing = True
    aa.anti_aliasing_method = unreal.AntiAliasingMethod.AAM_NONE
    aa.spatial_sample_count = 1
    aa.temporal_sample_count = 16          # accumulated temporal samples instead of TSR history
    aa.engine_warm_up_count = 90           # let Lumen and VSM converge before the frame
    aa.render_warm_up_count = 32
    aa.use_camera_cut_for_warm_up = False
mqs.render_queue_with_executor(unreal.MoviePipelinePIEExecutor)
print("G4_RENDER queued", [s.get_name() for s in sequences], OUT_DIR)
