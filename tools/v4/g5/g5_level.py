"""G5 (runs INSIDE the Unreal Editor): player start in the tech smoke level.

The player starts 4 m behind and 2 m beside the pallet, facing +X, so the walk/run path of the
PIE playthrough passes the pallet without touching it and the camera has it in view.
"""
import unreal

LEVEL = "/Game/Genesis/TechSmoke/Maps/L_TechSmoke"
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if les.get_current_level().get_path_name().split(":")[0].split(".")[0] != LEVEL:
    les.load_level(LEVEL)
for a in eas.get_all_level_actors():
    if isinstance(a, unreal.PlayerStart):
        eas.destroy_actor(a)
ps = eas.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(-400.0, -200.0, 100.0), unreal.Rotator(0.0, 0.0, 0.0))
ps.set_actor_label("PlayerStart_TechSmoke")
les.save_current_level()
print("G5_LEVEL player start", ps.get_actor_location())
