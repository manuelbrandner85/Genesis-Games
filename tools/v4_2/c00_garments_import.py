"""C00 (runs INSIDE the Unreal Editor): import blouse + jacket of CHR_C00_TOCHTER and fabric materials.

FBX from tools/v4_2/build_c00_garments.py (skinned to the MetaHuman body skeleton). The garment follows
the daughter's body through a leader-pose component (same bone names), the bundled default T-shirt
outfit is switched off in her preview collection.
"""
import unreal

SRC = r"C:\Users\manue\Desktop\Genesis-Games\ArtSource\Export\C00\SKM_C00_Tochter_Kleidung.fbx"
DST = "/Game/Genesis/Characters/C00/Kleidung"
eal = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary

# Fabric master: base colour, roughness, specular (cloth sheen to be added in the material editor)
MASTER = f"{DST}/M_C00_Fabric"
if not eal.does_asset_exist(MASTER):
    m = at.create_asset("M_C00_Fabric", DST, unreal.Material, unreal.MaterialFactoryNew())
    col = mel.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -400, 0)
    col.set_editor_property("parameter_name", "Color")
    rough = mel.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -400, 200)
    rough.set_editor_property("parameter_name", "Roughness")
    spec = mel.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -400, 350)
    spec.set_editor_property("parameter_name", "Specular")
    mel.connect_material_property(col, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(spec, "", unreal.MaterialProperty.MP_SPECULAR)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
master = eal.load_asset(MASTER)


def fabric(name, rgb, rough, spec):
    path = f"{DST}/{name}"
    mi = eal.load_asset(path) if eal.does_asset_exist(path) else at.create_asset(
        name, DST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, master)
    mel.set_material_instance_vector_parameter_value(mi, "Color", unreal.LinearColor(*rgb, 1))
    mel.set_material_instance_scalar_parameter_value(mi, "Roughness", rough)
    mel.set_material_instance_scalar_parameter_value(mi, "Specular", spec)
    eal.save_loaded_asset(mi)
    return mi


mi_blouse = fabric("MI_C00_Bluse", (0.78, 0.75, 0.69), 0.55, 0.35)       # off-white cotton-silk
mi_jacket = fabric("MI_C00_Jackett", (0.045, 0.045, 0.050), 0.82, 0.25)   # charcoal wool
mi_trousers = fabric("MI_C00_Hose", (0.030, 0.030, 0.034), 0.75, 0.25)    # dark trousers

task = unreal.AssetImportTask()
task.filename, task.destination_path, task.destination_name = SRC, DST, "SKM_C00_Tochter_Kleidung"
task.automated, task.replace_existing, task.save = True, True, True
opt = unreal.FbxImportUI()
opt.import_mesh, opt.import_as_skeletal, opt.import_materials, opt.import_textures, opt.import_animations = True, True, False, False, False
opt.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
opt.skeletal_mesh_import_data.set_editor_property("import_morph_targets", False)
opt.skeletal_mesh_import_data.set_editor_property("convert_scene", True)
task.options = opt
at.import_asset_tasks([task])
skm = eal.load_asset(f"{DST}/SKM_C00_Tochter_Kleidung")
mats = skm.materials
for i, sm in enumerate(mats):
    n = str(sm.material_slot_name)
    sm.material_interface = mi_jacket if "Jackett" in n else mi_trousers if "Hose" in n else mi_blouse
    mats[i] = sm
skm.set_editor_property("materials", mats)
eal.save_loaded_asset(skm)
print("C00_GARMENTS", skm.get_path_name(), [str(m.material_slot_name) for m in skm.materials],
      skm.skeleton.get_path_name() if skm.skeleton else None)
