"""C00 (runs INSIDE the Unreal Editor): export the man's assembled preview body and the Fab shirt mesh to FBX.

MetaHuman outfits only follow a pose inside the MetaHuman Creator preview, not in a level (verified 2026-10-25:
sleeves stay in A-pose). The shirt is therefore rebuilt as an own skinned mesh in Blender
(tools/v4_2/build_c00_shirt_skinned.py) on the man's real body + skeleton exported here.
Outputs (local only, Epic/Fab content): ArtSource/Export/C00/SKM_C00_Mann_Body.fbx, SM_C00_Shirt01_man.fbx
"""
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
OUT = ROOT + "ArtSource/Export/C00/"
eal = unreal.EditorAssetLibrary
mh = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

ch = eal.load_asset("/Game/Genesis/Characters/C00/MHC_C00_Mann")
if not mh.is_object_added_for_editing(ch):
    mh.try_add_object_to_edit(ch)
a = mh.spawn_meta_human_actor(ch, True)
mh.assemble_for_preview(ch)
body = next(c for c in a.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Body")
skm = body.get_skeletal_mesh_asset()


def export(obj, path):
    t = unreal.AssetExportTask()
    t.object, t.filename, t.automated, t.prompt, t.replace_identical = obj, path, True, False, True
    t.exporter = unreal.SkeletalMeshExporterFBX() if isinstance(obj, unreal.SkeletalMesh) else unreal.StaticMeshExporterFBX()
    opt = unreal.FbxExportOption()
    opt.set_editor_property("collision", False)
    opt.set_editor_property("level_of_detail", False)
    t.options = opt
    ok = unreal.Exporter.run_asset_export_task(t)
    print("C00_EXPORT", path, ok, [str(e) for e in t.errors] if hasattr(t, "errors") else "")


export(skm, OUT + "SKM_C00_Mann_Body.fbx")
export(eal.load_asset("/Game/Fab/MetaHuman/Shirt_01/Meshes/SM_Shirt_01_man"), OUT + "SM_C00_Shirt01_man.fbx")
print("C00_SKEL", skm.skeleton.get_path_name())
eas.destroy_actor(a)
