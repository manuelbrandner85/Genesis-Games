"""C00 (runs INSIDE the Unreal Editor): import the man's own skinned shirt (tools/v4_2/build_c00_shirt_skinned.py).

Skeletal mesh on metahuman_base_skel with the Fab shirt material (MI_Shirt_01, recoloured light blue-grey by
c00_mh_mann.py). In scenes it is attached to the body with a leader pose, so it follows every pose - unlike the
MetaHuman outfit, which only follows inside the Creator preview. Local only (Content/Genesis/Characters/C00/Kleidung).
"""
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
DST = "/Game/Genesis/Characters/C00/Kleidung"
eal = unreal.EditorAssetLibrary
skel = eal.load_asset("/MetaHumanCharacter/Female/Medium/NormalWeight/Body/metahuman_base_skel")
task = unreal.AssetImportTask()
task.filename = ROOT + "ArtSource/Export/C00/SKM_C00_Mann_Shirt.fbx"
task.destination_path, task.destination_name = DST, "SKM_C00_Mann_Shirt"
task.automated, task.replace_existing, task.save = True, True, True
opt = unreal.FbxImportUI()
opt.import_mesh, opt.import_as_skeletal, opt.import_materials, opt.import_textures, opt.import_animations = True, True, False, False, False
opt.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
opt.skeleton = skel
opt.skeletal_mesh_import_data.set_editor_property("import_morph_targets", False)
opt.skeletal_mesh_import_data.set_editor_property("convert_scene", True)
opt.skeletal_mesh_import_data.set_editor_property("use_t0_as_ref_pose", False)
task.options = opt
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
skm = eal.load_asset(f"{DST}/SKM_C00_Mann_Shirt")
mi = eal.load_asset("/Game/Fab/MetaHuman/Shirt_01/Materials/MI_Shirt_01")
for i in range(len(skm.materials)):
    skm.set_material(i, mi) if hasattr(skm, "set_material") else None
mats = skm.materials
for m in mats:
    m.material_interface = mi
skm.materials = mats
eal.save_loaded_asset(skm)
print("C00_SHIRT", skm.get_path_name() if skm else None, skm.skeleton.get_path_name() if skm else None, len(mats))
