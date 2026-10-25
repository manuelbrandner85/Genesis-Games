"""CR-001 phase 2 (runs inside the Unreal Editor or headless with -run=pythonscript): build L_C02_Swim,
the graybox map of the mandatory C02-B swim.

The course (oviduct, oocyte, other cells, lights) is built at runtime by AGenesisSwimDirector from the
analytic FGenesisOviduct (1 uu = 1 um), so the map only holds the world settings (AGenesisSwimGameMode)
and a player start at the beginning of the course. Idempotent: an existing map is replaced.
"""
import math
import unreal

MAP = "/Game/Genesis/Cinematics/C02/Maps/L_C02_Swim"
eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def center(s):
    """Same centre line as FGenesisOviduct::Center."""
    return unreal.Vector(s, 220.0 * math.sin(s / 900.0), 160.0 * math.sin(s / 1300.0 + 0.7))


def tangent_rotation(s):
    t = unreal.Vector(1.0, 220.0 / 900.0 * math.cos(s / 900.0), 160.0 / 1300.0 * math.cos(s / 1300.0 + 0.7))
    return unreal.MathLibrary.make_rot_from_x(t)


if eal.does_asset_exist(MAP):
    eal.delete_asset(MAP)
world = unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
start = eas.spawn_actor_from_class(unreal.PlayerStart, center(150.0), tangent_rotation(150.0))
start.set_actor_label("C02_SwimStart")
ws = world.get_world_settings()
ws.set_editor_property("default_game_mode", unreal.load_class(None, "/Script/Genesis.GenesisSwimGameMode"))
if not unreal.EditorLoadingAndSavingUtils.save_map(world, MAP):
    raise RuntimeError("save failed: " + MAP)
print("CR001_SWIM_MAP", MAP, "game mode", ws.get_editor_property("default_game_mode").get_name())
