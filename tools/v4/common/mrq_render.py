"""Runs INSIDE the Unreal Editor: render review cameras with Movie Render Queue.

Reads Saved/MRQ/request.json:
  {"level": "/Game/...", "out_dir": "<abs dir>", "resolution": [1920, 1080],
   "cameras": {"Name": {"loc": [x,y,z], "target": [x,y,z], "focal": 24, "fstop": 16}}}
Creates/updates a CineCameraActor and a one-frame level sequence per camera, then renders all
of them with the PIE executor (Lumen warm-up, 16 temporal samples). Output: <out_dir>/LS_<Name>.png
"""
import json
import os

import unreal

ROOT = unreal.Paths.project_dir()
req = json.load(open(os.path.join(ROOT, "Saved", "MRQ", "request.json"), encoding="utf-8"))
LEVEL = req["level"]
SEQ_DIR = LEVEL.rsplit("/", 2)[0] + "/Review"

at = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.eject_pilot_level_actor()
if les.get_current_level().get_path_name().split(":")[0].split(".")[0] != LEVEL:
    les.load_level(LEVEL)

sequences = []
for name, c in req["cameras"].items():
    label = f"ReviewCam_{name}"
    cam = next((a for a in eas.get_all_level_actors() if a.get_actor_label() == label), None)
    if cam is None:
        cam = eas.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(0, 0, 0))
        cam.set_actor_label(label)
        cam.set_folder_path("Review")
    loc, tgt = unreal.Vector(*c["loc"]), unreal.Vector(*c["target"])
    cam.set_actor_location(loc, False, False)
    cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(loc, tgt), False)
    cc = cam.get_cine_camera_component()
    fb = cc.get_editor_property("filmback")
    res = req.get("resolution", [1920, 1080])
    fb.set_editor_property("sensor_width", 36.0)
    fb.set_editor_property("sensor_height", 36.0 * res[1] / res[0])     # match the image: no letterbox bars
    cc.set_editor_property("filmback", fb)
    cc.set_editor_property("current_focal_length", float(c.get("focal", 35)))
    cc.set_editor_property("current_aperture", float(c.get("fstop", 16)))
    fs = cc.get_editor_property("focus_settings")
    fs.set_editor_property("focus_method", unreal.CameraFocusMethod.MANUAL)
    fs.set_editor_property("manual_focus_distance", unreal.MathLibrary.vector_distance(loc, tgt))
    cc.set_editor_property("focus_settings", fs)

    seq_name = f"LS_{name}"
    path = f"{SEQ_DIR}/{seq_name}"
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    seq = at.create_asset(seq_name, SEQ_DIR, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    seq.set_display_rate(unreal.FrameRate(24, 1))
    seq.set_playback_start(0)
    seq.set_playback_end(1)
    binding = seq.add_possessable(cam)
    section = seq.add_track(unreal.MovieSceneCameraCutTrack).add_section()
    section.set_range(0, 1)
    section.set_camera_binding_id(seq.get_binding_id(binding))
    eal.save_loaded_asset(seq)
    sequences.append(seq)
les.save_current_level()

mqs = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
queue = mqs.get_queue()
queue.delete_all_jobs()
os.makedirs(req["out_dir"], exist_ok=True)
for seq in sequences:
    job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
    job.job_name = seq.get_name()
    job.map = unreal.SoftObjectPath(f"{LEVEL}.{LEVEL.split('/')[-1]}")
    job.sequence = unreal.SoftObjectPath(seq.get_path_name())
    cfg = job.get_configuration()
    out = cfg.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
    out.output_directory = unreal.DirectoryPath(req["out_dir"])
    out.output_resolution = unreal.IntPoint(*req.get("resolution", [1920, 1080]))
    out.file_name_format = "{sequence_name}"
    out.override_existing_output = True
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
    aa = cfg.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
    aa.override_anti_aliasing = True
    aa.anti_aliasing_method = unreal.AntiAliasingMethod.AAM_NONE
    aa.spatial_sample_count = 1
    aa.temporal_sample_count = 16
    aa.engine_warm_up_count = 90
    aa.render_warm_up_count = 32
    aa.use_camera_cut_for_warm_up = False
mqs.render_queue_with_executor(unreal.MoviePipelinePIEExecutor)
print("MRQ queued", [s.get_name() for s in sequences], req["out_dir"])
