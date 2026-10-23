"""G4 (runs INSIDE the Unreal Editor): concrete yard slab from the Blender-baked 4 x 4 m tile.

World-aligned (UV = world XY / 400 cm), so the floor size does not matter; a second, much larger
sample of the same tile modulates the tone (0.85-1.15) so the 4 m repeat does not read as a grid.
Replaces the earlier noise-only floor material.
"""
import os

import unreal

ROOT = unreal.Paths.project_dir()
SRC = os.path.join(ROOT, "ArtSource", "TechSmoke", "Concrete_YardSlab", "Textures")
DST = "/Game/Genesis/TechSmoke/Concrete"
MAT = f"{DST}/M_Concrete_YardSlab"
TILE_CM = 400.0
MACRO_CM = 2300.0

at = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

tasks = []
for s in ("BC", "ORM", "N"):
    t = unreal.AssetImportTask()
    t.filename = os.path.join(SRC, f"T_Concrete_YardSlab_{s}.png")
    t.destination_path = DST
    t.automated = t.replace_existing = t.save = True
    tasks.append(t)
at.import_asset_tasks(tasks)
bc, orm, nrm = (eal.load_asset(f"{DST}/T_Concrete_YardSlab_{s}") for s in ("BC", "ORM", "N"))
orm.set_editor_property("srgb", False)
orm.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
nrm.set_editor_property("srgb", False)
nrm.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
for t in (bc, orm, nrm):
    eal.save_loaded_asset(t)

if eal.does_asset_exist(MAT):
    eal.delete_asset(MAT)
m = at.create_asset("M_Concrete_YardSlab", DST, unreal.Material, unreal.MaterialFactoryNew())

def expr(cls, x, y, **props):
    e = mel.create_material_expression(m, cls, x, y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    return e

wp = expr(unreal.MaterialExpressionWorldPosition, -1400, 0)
xy = expr(unreal.MaterialExpressionComponentMask, -1200, 0, r=True, g=True, b=False, a=False)
mel.connect_material_expressions(wp, "", xy, "")
uv = expr(unreal.MaterialExpressionDivide, -1000, -100, const_b=TILE_CM)
mel.connect_material_expressions(xy, "", uv, "A")
uv_macro = expr(unreal.MaterialExpressionDivide, -1000, 300, const_b=MACRO_CM)
mel.connect_material_expressions(xy, "", uv_macro, "A")

def sample(tex, sampler, x, y, uvs):
    e = expr(unreal.MaterialExpressionTextureSample, x, y, texture=tex, sampler_type=sampler)
    mel.connect_material_expressions(uvs, "", e, "UVs")
    return e

s_bc = sample(bc, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, -700, -300, uv)
s_orm = sample(orm, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS, -700, 0, uv)
s_n = sample(nrm, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL, -700, 250, uv)
s_macro = sample(bc, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, -700, 550, uv_macro)
# Tone modulation 0.85..1.15 from the macro sample, centred on the tile's mean grey (~0.17 linear).
macro = expr(unreal.MaterialExpressionLinearInterpolate, -400, 500, const_a=0.85, const_b=1.15)
norm = expr(unreal.MaterialExpressionMultiply, -500, 600, const_b=2.9)
mel.connect_material_expressions(s_macro, "R", norm, "A")
mel.connect_material_expressions(norm, "", macro, "Alpha")
col = expr(unreal.MaterialExpressionMultiply, -300, -200)
mel.connect_material_expressions(s_bc, "RGB", col, "A")
mel.connect_material_expressions(macro, "", col, "B")
mel.connect_material_property(col, "", unreal.MaterialProperty.MP_BASE_COLOR)
mel.connect_material_property(s_orm, "G", unreal.MaterialProperty.MP_ROUGHNESS)
mel.connect_material_property(s_n, "RGB", unreal.MaterialProperty.MP_NORMAL)
mel.recompile_material(m)
eal.save_loaded_asset(m)

floor = next(a for a in eas.get_all_level_actors() if a.get_actor_label() == "Review_Floor")
floor.static_mesh_component.set_material(0, m)
old = "/Game/Genesis/TechSmoke/Maps/M_Review_Concrete"
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
if eal.does_asset_exist(old):
    eal.delete_asset(old)
print("G4_FLOOR ok", m.get_path_name())
