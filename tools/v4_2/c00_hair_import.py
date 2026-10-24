"""C00 (runs INSIDE the Unreal Editor): import the daughter's own long-bob groom and its balayage material.

Alembic from tools/v4_2/build_c00_hair.py (Blender, metres, Z-up). The hair material uses Unreal's hair
shading model; the colour runs from dark brown at the root to caramel/honey blond in the lengths along the
strand coordinate (HairAttributes U), with a per-strand seed variation like a real balayage.
"""
import unreal

SRC = r"C:\Users\manue\Desktop\Genesis-Games\ArtSource\Export\C00\GR_C00_Tochter_Haar.abc"
DST = "/Game/Genesis/Characters/C00/Haar"
eal = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary

MAT = f"{DST}/M_C00_Haar_Balayage"
if eal.does_asset_exist(MAT):
    eal.delete_asset(MAT)
m = at.create_asset("M_C00_Haar_Balayage", DST, unreal.Material, unreal.MaterialFactoryNew())
m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_HAIR)
m.set_editor_property("used_with_hair_strands", True)
attrs = mel.create_material_expression(m, unreal.MaterialExpressionHairAttributes, -900, 0)
root = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -700, -200)
root.set_editor_property("constant", unreal.LinearColor(0.045, 0.024, 0.012, 1))      # dark brown roots
tip = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -700, -80)
tip.set_editor_property("constant", unreal.LinearColor(0.34, 0.20, 0.085, 1))          # caramel / honey lengths
light = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -700, 40)
light.set_editor_property("constant", unreal.LinearColor(0.52, 0.34, 0.15, 1))         # lighter balayage strands
# U along the strand -> smooth transition below the ears
sstep = mel.create_material_expression(m, unreal.MaterialExpressionSmoothStep, -500, 120)
sstep.set_editor_property("const_min", 0.30)
sstep.set_editor_property("const_max", 0.78)
mel.connect_material_expressions(attrs, "U", sstep, "Value")
mix = mel.create_material_expression(m, unreal.MaterialExpressionLinearInterpolate, -300, -120)
mel.connect_material_expressions(root, "", mix, "A")
# per strand: some strands get the lighter balayage colour
seed_step = mel.create_material_expression(m, unreal.MaterialExpressionSmoothStep, -500, 260)
seed_step.set_editor_property("const_min", 0.55)
seed_step.set_editor_property("const_max", 0.80)
mel.connect_material_expressions(attrs, "Seed", seed_step, "Value")
tipmix = mel.create_material_expression(m, unreal.MaterialExpressionLinearInterpolate, -500, -20)
mel.connect_material_expressions(tip, "", tipmix, "A")
mel.connect_material_expressions(light, "", tipmix, "B")
mel.connect_material_expressions(seed_step, "", tipmix, "Alpha")
mel.connect_material_expressions(tipmix, "", mix, "B")
mel.connect_material_expressions(sstep, "", mix, "Alpha")
mel.connect_material_property(mix, "", unreal.MaterialProperty.MP_BASE_COLOR)
rough = mel.create_material_expression(m, unreal.MaterialExpressionConstant, -300, 200)
rough.set_editor_property("r", 0.35)
mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
spec = mel.create_material_expression(m, unreal.MaterialExpressionConstant, -300, 300)
spec.set_editor_property("r", 0.35)
mel.connect_material_property(spec, "", unreal.MaterialProperty.MP_SPECULAR)
mel.recompile_material(m)
eal.save_loaded_asset(m)

task = unreal.AssetImportTask()
task.filename, task.destination_path, task.destination_name = SRC, DST, "GR_C00_Tochter_Haar"
task.automated, task.replace_existing, task.save = True, True, True
opt = unreal.GroomImportOptions()
conv = opt.conversion_settings
conv.set_editor_property("rotation", unreal.Vector(90.0, 0.0, 0.0))      # Alembic Y-up -> Unreal Z-up
conv.set_editor_property("scale", unreal.Vector(100.0, -100.0, 100.0))   # metres -> cm, Blender -> Unreal handedness
opt.set_editor_property("conversion_settings", conv)
task.options = opt
task.factory = unreal.HairStrandsFactory()                   # otherwise the Alembic static-mesh importer is used
at.import_asset_tasks([task])
groom = eal.load_asset(f"{DST}/GR_C00_Tochter_Haar")
print("C00_HAIR", groom.get_path_name() if groom else None)
