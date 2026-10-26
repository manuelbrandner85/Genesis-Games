"""C00 (runs INSIDE the Unreal Editor): step 3 of 3 - the softened body albedo onto the man (Regie 2026-10-26).

Imports Saved/SkinWork/T_Body_BC_Mann_soft.png (tools/v4_2/c00_skin_spots_soften_blender.py) as
/Game/Genesis/Characters/C00/Built/Mann/Skin/T_C00_Mann_Body_BC_Soft (sRGB, virtual texture like the baked one) and
makes, for every body material instance that used the baked albedo (Saved/SkinWork/skin_spots.json), a child
instance MI_C00_Mann_Body_SoftSpots_<slot> overriding only that texture. c00_scene_bedroom.py puts these onto the
man's Body component. All local (Built/ is MetaHuman-derived content, not in the repo); a rebuild of the man keeps
working - the children follow their parents.
"""
import json
import os

import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
WORK = os.path.join(ROOT, "Saved", "SkinWork")
DEST = "/Game/Genesis/Characters/C00/Built/Mann/Skin"
eal = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
with open(os.path.join(WORK, "skin_spots.json"), encoding="utf8") as f:
    info = json.load(f)

task = unreal.AssetImportTask()
task.filename = os.path.join(WORK, "T_Body_BC_Mann_soft.png")
task.destination_path = DEST
task.destination_name = "T_C00_Mann_Body_BC_Soft"
task.replace_existing = True
task.automated = True
task.save = False
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
tex = eal.load_asset(f"{DEST}/T_C00_Mann_Body_BC_Soft")
tex.set_editor_property("srgb", info.get("srgb", True))
tex.set_editor_property("virtual_texture_streaming", info.get("vt", True))
tex.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_CHARACTER)
eal.save_loaded_asset(tex, False)

made = []
for u in info["uses"]:
    name = f"MI_C00_Mann_Body_SoftSpots_{u['slot']}"
    path = f"{DEST}/{name}"
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    mi = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, DEST, unreal.MaterialInstanceConstant,
                                                                  unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, eal.load_asset(u["mi"].split(".")[0]))
    MEL.set_material_instance_texture_parameter_value(mi, u["param"], tex)
    MEL.update_material_instance(mi)
    eal.save_loaded_asset(mi, False)
    made.append({"slot": u["slot"], "mi": mi.get_path_name()})
with open(os.path.join(WORK, "skin_spots_applied.json"), "w", encoding="utf8") as f:
    json.dump(made, f, indent=1)
print("C00_SKIN_APPLY", tex.get_path_name(), made)
