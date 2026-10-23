"""G4 (runs INSIDE the Unreal Editor): pilot a review camera and request a high-res screenshot.

Reads Saved/G4/shot_request.txt: "<camera label> <width>x<height> [console commands separated by ;]".
The screenshot is written asynchronously by the engine to Saved/Screenshots/WindowsEditor/.
"""
import os

import unreal

ROOT = unreal.Paths.project_dir()
req = open(os.path.join(ROOT, "Saved", "G4", "shot_request.txt"), encoding="utf-8").read().strip().split(" ", 2)
label, res = req[0], req[1]
extra = req[2] if len(req) > 2 else ""
CAMERAS = {  # label: (location cm, look-at target cm) - same framing as the Blender review
    "Review_Cam": ((175.0, -195.0, 145.0), (0.0, 0.0, 6.0)),
    "Review_Detail": ((98.0, -95.0, 42.0), (52.0, -36.0, 7.0)),
}
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
cam = next(a for a in eas.get_all_level_actors() if a.get_actor_label() == label)
# Piloting moves the actor with the viewport, so eject first, re-place the camera, then pilot.
les.eject_pilot_level_actor()
loc, tgt = (unreal.Vector(*v) for v in CAMERAS[label])
cam.set_actor_location(loc, False, False)
cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(loc, tgt), False)
eas.select_nothing()
ues.set_level_viewport_camera_info(loc, cam.get_actor_rotation())
les.pilot_level_actor(cam)
world = ues.get_editor_world()
view_loc, view_rot = ues.get_level_viewport_camera_info()
print("G4_VIEW", label, view_loc, view_rot)
# Clean capture: no editor sprites, grid, selection outline or widgets.
for flag in ("BillboardSprites", "Grid", "Selection", "ModeWidgets", "Volumes", "Bounds", "CameraFrustums"):
    unreal.SystemLibrary.execute_console_command(world, f"ShowFlag.{flag} 0")
for cmd in [c.strip() for c in extra.split(";") if c.strip()]:
    unreal.SystemLibrary.execute_console_command(world, cmd)
unreal.SystemLibrary.execute_console_command(world, f"HighResShot {res}")
print("G4_SHOT requested", label, res, extra)
