"""C00 (runs INSIDE the Unreal Editor): render LS_C00_00B with the Movie Render Queue (technical master test of 00-B).

1920x1080, 24 fps, PNG sequence to Saved/MovieRenders/C00_00B/ (local), temporal anti-aliasing 8 samples (hair
strands and the slow thumb motion resolve cleanly), 48 warm-up frames (Lumen, hair binding, texture streaming), and
the cinematic console variables of the bedroom stills (strands LOD forced, hair samples, texture pool).
The render runs in PIE in the background; the host polls the frame count (tools/v4_2/c00_render_bedroom_shots.py is
for stills). An MP4 preview is encoded on the host with ffmpeg afterwards.
"""
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
SEQ = "/Game/Genesis/Cinematics/C00/LS_C00_00B.LS_C00_00B"
MAP = "/Game/Genesis/Sets/C00_Schlafzimmer/L_C00_Schlafzimmer.L_C00_Schlafzimmer"
OUT = ROOT + "Saved/MovieRenders/C00_00B"

mrq = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
queue = mrq.get_queue()
for j in list(queue.get_jobs()):
    queue.delete_job(j)
job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
job.job_name = "C00_00B"
job.sequence = unreal.SoftObjectPath(SEQ)
job.map = unreal.SoftObjectPath(MAP)
cfg = job.get_configuration()
out = cfg.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
out.output_directory = unreal.DirectoryPath(OUT)
out.output_resolution = unreal.IntPoint(1920, 1080)
out.file_name_format = "C00_00B.{frame_number}"
out.use_custom_frame_rate = True
out.output_frame_rate = unreal.FrameRate(24, 1)
out.override_existing_output = True
cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
aa = cfg.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
aa.spatial_sample_count = 1
aa.temporal_sample_count = 8
aa.override_anti_aliasing = True
aa.anti_aliasing_method = unreal.AntiAliasingMethod.AAM_NONE
aa.engine_warm_up_count = 48
aa.render_warm_up_count = 48
cv = cfg.find_or_add_setting_by_class(unreal.MoviePipelineConsoleVariableSetting)
for name, val in (("r.HairStrands.ForceLOD", 0), ("r.HairStrands.Visibility.MSAA.SamplePerPixel", 4),
                  ("r.HairStrands.DeepShadow.Resolution", 2048), ("r.Streaming.PoolSize", 3000)):
    cv.add_or_update_console_variable(name, float(val))
executor = mrq.render_queue_with_executor(unreal.MoviePipelinePIEExecutor)
print("C00_MRQ_00B started", OUT)
