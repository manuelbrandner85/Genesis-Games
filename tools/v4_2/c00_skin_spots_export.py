"""C00 (runs INSIDE the Unreal Editor): step 1 of 3 - softer age spots on the man's arms (Regie 2026-10-26).

Regie: "mach die Altersflecken am Unterarm des Mannes weicher und unauffälliger, damit sie wie echte Pigmentflecken
wirken" - the baked body albedo of the built man (MetaHuman cloud texture) has hard, saturated orange-brown spots on
forearms and backs of the hands. This exports that albedo (and reports which body material slot / parameter uses it)
to Saved/SkinWork/ (local: MetaHuman-derived content stays out of the repo).
Next: tools/v4_2/c00_skin_spots_soften_blender.py (Blender, background), then tools/v4_2/c00_skin_spots_apply.py.
"""
import json
import os

import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
TEX = "/Game/Genesis/Characters/C00/Built/Mann/MHC_C00_Mann/Body/Baked/T_Body_BC_VT"
OUT = os.path.join(ROOT, "Saved", "SkinWork")
os.makedirs(OUT, exist_ok=True)
eal = unreal.EditorAssetLibrary
tex = eal.load_asset(TEX)
task = unreal.AssetExportTask()
task.object = tex
task.filename = os.path.join(OUT, "T_Body_BC_Mann.png")
task.automated = True
task.replace_identical = True
task.prompt = False
task.exporter = unreal.TextureExporterPNG()
ok = unreal.Exporter.run_asset_export_task(task)

# which material instance / parameter carries the albedo (searched in the built man's body materials)
uses = []
bp = eal.load_blueprint_class("/Game/Genesis/Characters/C00/Built/Mann/MHC_C00_Mann/BP_MHC_C00_Mann")
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
probe = eas.spawn_actor_from_class(bp, unreal.Vector(0, 0, -600), unreal.Rotator(0, 0, 0))
body = next(c for c in probe.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Body")
for i, slot in enumerate(body.get_material_slot_names()):
    mi = body.get_material(i)
    if not isinstance(mi, unreal.MaterialInstance):
        continue
    for p in unreal.MaterialEditingLibrary.get_texture_parameter_names(mi):
        t = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(mi, p)
        if t and t.get_path_name().split(".")[0] == TEX:
            uses.append({"slot": i, "slot_name": str(slot), "mi": mi.get_path_name(), "param": str(p)})
eas.destroy_actor(probe)
info = {"png": task.filename, "ok": bool(ok), "size": [tex.blueprint_get_size_x(), tex.blueprint_get_size_y()],
        "srgb": tex.srgb, "vt": tex.virtual_texture_streaming, "uses": uses}
with open(os.path.join(OUT, "skin_spots.json"), "w", encoding="utf8") as f:
    json.dump(info, f, indent=1)
print("C00_SKIN_EXPORT", json.dumps(info))
