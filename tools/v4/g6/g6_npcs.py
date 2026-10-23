"""G6 WP6.3 (runs INSIDE the Unreal Editor): residents N01-N03, their schedule anchors and the
world start state in L_Flussdorf_G6.

Anchors are TargetPoints tagged like the schedule (Source/Genesis/Private/Npc/GenesisNpcSchedule.cpp):
work places from the source (N01 R03 workbench, N02 R02 market errands, N03 R02 behind the
counter), homes in R07 in front of the three house doors. Which house is whose = Startwert.
"""
import unreal

LEVEL = "/Game/Genesis/Flussdorf/Maps/L_Flussdorf_G6"
V, R = unreal.Vector, unreal.Rotator
eal = unreal.EditorAssetLibrary
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if les.get_current_level().get_path_name().split(":")[0].split(".")[0] != LEVEL:
    les.load_level(LEVEL)

for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    if lbl.startswith(("Anchor_", "NPC_", "WorldSetup")):
        eas.destroy_actor(a)

ANCHORS = {  # tag: (x, y, z, yaw)
    "N01_Work": (5300, 180, 100, 90), "N01_Home": (-1000, 2550, 150, 90),
    "N02_Errands": (2900, -150, 100, 90), "N02_Home": (0, 2700, 150, 90),
    "N03_Work": (3000, 230, 100, -90), "N03_Home": (1000, 2550, 150, 90),
}
for tag, (x, y, z, yaw) in ANCHORS.items():
    tp = eas.spawn_actor_from_class(unreal.TargetPoint, V(x, y, z), R(0, 0, yaw))
    tp.set_actor_label(f"Anchor_{tag}")
    tp.tags = [tag]
    tp.set_folder_path("NPC_Anchors")

MANNY = eal.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple")
QUINN = eal.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple")
ANIM = unreal.load_class(None, "/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed.ABP_Unarmed_C")
NPCS = [  # id, role (source), mesh, walk speed cm/s, start position (= where the schedule has them at 08:30)
    ("N01", "Werkstattbesitzer/in", MANNY, 145.0, "N01_Home"),
    ("N02", "Reparaturkund/in", QUINN, 130.0, "N02_Errands"),
    ("N03", "Marktbetreiber/in", QUINN, 140.0, "N03_Work"),
]
for nid, role, mesh, speed, start in NPCS:
    x, y, z, yaw = ANCHORS[start]
    npc = eas.spawn_actor_from_class(unreal.GenesisNpc, V(x, y, z), R(0, 0, yaw))
    npc.set_actor_label(f"NPC_{nid}")
    npc.set_folder_path("NPCs")
    npc.set_editor_property("npc_id", nid)
    npc.set_editor_property("role_name", role)
    npc.set_editor_property("walk_speed", speed)
    sk = npc.get_editor_property("mesh")
    sk.set_skeletal_mesh_asset(mesh)
    sk.set_anim_instance_class(ANIM)

setup = eas.spawn_actor_from_class(unreal.GenesisWorldSetup, V(0, 0, 300))
setup.set_actor_label("WorldSetup_Flussdorf")
setup.set_editor_property("market_stock", {"ITEM_SPARK_PLUG": 1})
setup.set_editor_property("object_states", {"OBJ_GENERATOR_N02": "Defect", "MARKET_R02": "Open"})
les.save_current_level()
print("G6_NPCS ok", [n[0] for n in NPCS], len(ANCHORS), "anchors")
