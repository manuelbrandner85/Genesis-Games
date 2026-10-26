"""GD-2026-10-26-03 Phase B (runs headless with -run=pythonscript or inside the editor): build L_Pregnancy,
the graybox map of the playable pregnancy. Everything (uterine wall, child, cord, light) is built at runtime by
AGenesisPregnancyDirector, so the map only holds the world settings (AGenesisPregnancyGameMode) and a player
start. Idempotent: an existing map is replaced.
"""
import unreal

MAP = "/Game/Genesis/Pregnancy/Maps/L_Pregnancy"
eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

if eal.does_asset_exist(MAP):
    eal.delete_asset(MAP)
world = unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
start = eas.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
start.set_actor_label("Pregnancy_Start")
ws = world.get_world_settings()
ws.set_editor_property("default_game_mode", unreal.load_class(None, "/Script/Genesis.GenesisPregnancyGameMode"))
if not unreal.EditorLoadingAndSavingUtils.save_map(world, MAP):
    raise RuntimeError("save failed: " + MAP)
print("PREGNANCY_MAP", MAP)
