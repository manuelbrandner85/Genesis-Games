"""G6 WP6.4c (runs INSIDE the Unreal Editor): make the customer's generator usable and give N02
a place in the workshop for the acceptance (appointment anchor N02_Workshop)."""
import unreal

LEVEL = "/Game/Genesis/Flussdorf/Maps/L_Flussdorf_G6"
V, R = unreal.Vector, unreal.Rotator
eal = unreal.EditorAssetLibrary
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if les.get_current_level().get_path_name().split(":")[0].split(".")[0] != LEVEL:
    les.load_level(LEVEL)

for a in eas.get_all_level_actors():
    if a.get_actor_label() in ("Generator", "Generator_N02", "Anchor_N02_Workshop"):
        eas.destroy_actor(a)

# Generator 70 x 50 x 55 cm (a portable 2-3 kW unit), as an interactable object.
gen = eas.spawn_actor_from_class(unreal.GenesisInteractableProp, V(5100, -200, 27.5), R(0, 0, 0))
gen.set_actor_label("Generator_N02")
gen.set_folder_path("R03_Werkstatt")
gen.static_mesh_component.set_static_mesh(eal.load_asset("/Engine/BasicShapes/Cube"))
gen.static_mesh_component.set_material(0, eal.load_asset("/Game/Genesis/Flussdorf/Graybox/MI_Graybox_Metal"))
gen.set_actor_scale3d(V(0.70, 0.50, 0.55))
gen.set_editor_property("interaction_id", "OBJ_GENERATOR_N02")
gen.set_editor_property("label", "Generator der Kundin")

tp = eas.spawn_actor_from_class(unreal.TargetPoint, V(4950, -110, 100), R(0, 0, -20))
tp.set_actor_label("Anchor_N02_Workshop")
tp.tags = ["N02_Workshop"]
tp.set_folder_path("NPC_Anchors")
les.save_current_level()
print("G6_INTERACTION ok")
