"""G5 (runs INSIDE the visible Unreal Editor): start the Play-in-Editor playthrough test.
The result is written to the editor log (LogAutomationController ... PIEPlaythrough)."""
import unreal

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(world, "Automation RunTests Genesis.Gameplay.PIEPlaythrough")
print("G5_PIE started")
