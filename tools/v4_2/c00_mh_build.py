"""C00 (runs INSIDE the Unreal Editor): build (assemble) the rigged C00 MetaHumans for cinematics.

After FA-METAHUMAN-CLOUD-001 (4K textures + auto-rig, 2026-10-25) the characters can be built. Cinematic pipeline,
cinematic quality, into /Game/Genesis/Characters/C00/Built/<Name> (local only, gitignored - Epic content).
"""
import os

import unreal

eal = unreal.EditorAssetLibrary
# one character per run, in an empty level (building with spawned preview actors around crashed the editor)
NAMES = [n for n in os.environ.get("GENESIS_BUILD_CHAR", "Mann").split(",") if n]
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).new_level("/Temp/C00_BuildEmpty")
mh = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
for name in NAMES:
    ch = eal.load_asset(f"/Game/Genesis/Characters/C00/MHC_C00_{name}")
    if not mh.is_object_added_for_editing(ch):
        mh.try_add_object_to_edit(ch)
    p = unreal.MetaHumanCharacterEditorBuildParameters()
    p.set_editor_property("pipeline_type", unreal.MetaHumanDefaultPipelineType.CINEMATIC)
    p.set_editor_property("pipeline_quality", unreal.MetaHumanQualityLevel.CINEMATIC)
    p.set_editor_property("absolute_build_path", f"/Game/Genesis/Characters/C00/Built/{name}")
    p.set_editor_property("common_folder_path", "/Game/Genesis/Characters/C00/Built/Common")
    ok = mh.can_build_meta_human(ch, True)
    if ok:
        mh.build_meta_human(ch, p)
    built = [a for a in eal.list_assets(f"/Game/Genesis/Characters/C00/Built/{name}", recursive=True)]
    print("C00_BUILD", name, "can_build", ok, "assets", len(built), [b for b in built if "/BP_" in b][:3])
