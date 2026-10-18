# WK-M03-002: builds the daily-life StateTree, the activity Smart Object definitions and places
# activity spots, three test NPCs and a nav mesh volume in the test level.
# Run: UnrealEditor-Cmd.exe Genesis.uproject -run=pythonscript -script="<this file>"
import unreal

EAL = unreal.EditorAssetLibrary
ELL = unreal.EditorLevelLibrary
MAP_PATH = "/Game/Maps/L_GenesisTest"
AI_DIR = "/Game/Genesis/AI"
CUBE = "/Engine/BasicShapes/Cube.Cube"

# Activity spots in the graybox level (test layout, not canon).
# name, activity, location, visual scale (cube = 1 m), visual z, slot offsets, slot yaw
# Slots mindestens 80 cm auseinander: eine Figur (Kapsel) ist 68 cm breit.
SPOTS = [
    ("Wohnhaus_Betten", "Sleep", (-1500, 1500, 0), (2.0, 4.6, 0.5), 25, [(150, -150, 0), (150, 0, 0), (150, 150, 0)], 180.0),
    ("Werkstatt_Werkbank", "Work", (1500, -1500, 0), (2.0, 0.8, 0.9), 45, [(-55, 90, 0), (55, 90, 0)], -90.0),
    ("Markt_Stand", "Market", (1500, 1500, 0), (3.0, 1.2, 1.0), 50, [(-100, -110, 0), (0, -110, 0), (100, -110, 0)], 90.0),
    ("Bank_Platz", "Leisure", (-1500, -1500, 0), (2.4, 0.5, 0.45), 22, [(-85, 70, 0), (0, 70, 0), (85, 70, 0)], -90.0),
]

NPCS = [
    ("NPC_TEST_01", (300, 400, 95)),
    ("NPC_TEST_02", (300, -400, 95)),
    ("NPC_TEST_03", (-200, 1300, 95)),
]


def log(msg):
    unreal.log("GENESIS_BUILD " + msg)


def build_assets():
    # Alte Plaetze und Figuren entfernen, damit der Neubau keine Verweise auf alte Assets hinterlaesst.
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level(MAP_PATH)
    for a in ELL.get_all_level_actors():
        if a.get_class().get_name() in ("GenesisActivitySpot", "GenesisNpcCharacter"):
            ELL.destroy_actor(a)
    les.save_current_level()
    tree = unreal.GenesisNpcAssetBuilder.build_daily_life_state_tree(AI_DIR + "/ST_GenesisDailyLife")
    if not tree:
        raise RuntimeError("StateTree build failed")
    log("statetree %s" % tree.get_path_name())
    defs = {}
    for name, activity, _loc, _scale, _z, slots, yaw in SPOTS:
        path = AI_DIR + "/SOD_" + activity
        d = unreal.GenesisNpcAssetBuilder.build_activity_definition(
            path, activity, [unreal.Vector(*s) for s in slots], [yaw] * len(slots))
        if not d:
            raise RuntimeError("definition failed: " + activity)
        defs[activity] = d
        log("smartobject %s slots=%d" % (d.get_path_name(), len(slots)))
    return defs


def place_in_level(defs):
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level(MAP_PATH)
    for a in ELL.get_all_level_actors():
        if a.get_class().get_name() in ("GenesisActivitySpot", "GenesisNpcCharacter", "NavMeshBoundsVolume", "RecastNavMesh"):
            ELL.destroy_actor(a)

    cube = unreal.load_asset(CUBE)
    for name, activity, loc, scale, z, _slots, _yaw in SPOTS:
        spot = ELL.spawn_actor_from_class(unreal.GenesisActivitySpot, unreal.Vector(*loc), unreal.Rotator(0, 0, 0))
        spot.set_actor_label(name)
        visual = spot.get_component_by_class(unreal.StaticMeshComponent)
        visual.set_static_mesh(cube)
        visual.set_relative_location(unreal.Vector(0, 0, z), False, False)
        visual.set_relative_scale3d(unreal.Vector(*scale))
        spot.set_editor_property("definition", defs[activity])
        spot.apply_definition()

    for npc_id, loc in NPCS:
        npc = ELL.spawn_actor_from_class(unreal.GenesisNpcCharacter, unreal.Vector(*loc), unreal.Rotator(0, 0, 0))
        npc.set_actor_label(npc_id)
        npc.set_editor_property("character_asset_id", npc_id)
        npc.apply_appearance(npc_id)

    nav = ELL.spawn_actor_from_class(unreal.NavMeshBoundsVolume, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    nav.set_actor_label("Navigation")
    nav.set_actor_scale3d(unreal.Vector(30.0, 30.0, 5.0))  # Brush 200 cm -> 60 x 60 x 10 m

    les.save_current_level()
    log("level saved actors=%d" % len(ELL.get_all_level_actors()))


def main():
    defs = build_assets()
    place_in_level(defs)
    log("done")


main()
