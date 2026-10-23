"""G4 (runs INSIDE the Unreal Editor): import the G3 pallet and verify it.

Imports FBX + baked textures, builds a small PBR master material + instance, enables Nanite,
adds collision, keeps the imported normals/tangents (they match the Blender bake), saves,
then reads everything back and writes Saved/G4/import_report.json. Run via ue_remote.py.
"""
import json
import os

import unreal

ROOT = os.path.normpath(os.path.join(unreal.Paths.project_dir(), ""))
SRC = os.path.join(ROOT, "ArtSource", "TechSmoke", "SM_TechSmoke_PalletEUR")
DST = "/Game/Genesis/TechSmoke/PalletEUR"
MASTER = "/Game/Genesis/Materials/M_PBR_Master"
ASSET = "SM_TechSmoke_PalletEUR"
REPORT = os.path.join(ROOT, "Saved", "G4", "import_report.json")

at = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)


def import_files(files, dest):
    tasks = []
    for f in files:
        t = unreal.AssetImportTask()
        t.filename = f
        t.destination_path = dest
        t.automated = True
        t.replace_existing = True
        t.save = True
        tasks.append(t)
    at.import_asset_tasks(tasks)
    return [str(p) for t in tasks for p in t.imported_object_paths]


def load(path):
    a = eal.load_asset(path)
    if a is None:
        raise RuntimeError("missing asset " + path)
    return a


# --- Textures ---------------------------------------------------------------------------------
tex_files = [os.path.join(SRC, "Textures", f"T_{ASSET}_{s}.png") for s in ("BC", "ORM", "N")]
imported_tex = import_files(tex_files, DST + "/Textures")
bc = load(f"{DST}/Textures/T_{ASSET}_BC")
orm = load(f"{DST}/Textures/T_{ASSET}_ORM")
nrm = load(f"{DST}/Textures/T_{ASSET}_N")
bc.set_editor_property("srgb", True)
orm.set_editor_property("srgb", False)
orm.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
nrm.set_editor_property("srgb", False)
nrm.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
nrm.set_editor_property("flip_green_channel", False)      # already DirectX from the bake
for t in (bc, orm, nrm):
    eal.save_loaded_asset(t)

# --- Master material + instance -------------------------------------------------------------------
if eal.does_asset_exist(MASTER):
    master = load(MASTER)
else:
    master = at.create_asset("M_PBR_Master", "/Game/Genesis/Materials", unreal.Material, unreal.MaterialFactoryNew())
    def param(name, tex, sampler, x, y):
        e = mel.create_material_expression(master, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
        e.set_editor_property("parameter_name", name)
        e.set_editor_property("texture", tex)
        e.set_editor_property("sampler_type", sampler)
        return e
    e_bc = param("BaseColor", bc, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, -600, -200)
    e_orm = param("ORM", orm, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS, -600, 100)
    e_n = param("Normal", nrm, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL, -600, 400)
    mel.connect_material_property(e_bc, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(e_orm, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
    mel.connect_material_property(e_orm, "G", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(e_orm, "B", unreal.MaterialProperty.MP_METALLIC)
    mel.connect_material_property(e_n, "RGB", unreal.MaterialProperty.MP_NORMAL)
    mel.recompile_material(master)
    eal.save_loaded_asset(master)

mi_path = f"{DST}/MI_TechSmoke_PalletWood"
mi = load(mi_path) if eal.does_asset_exist(mi_path) else at.create_asset(
    "MI_TechSmoke_PalletWood", DST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
mel.set_material_instance_parent(mi, master)
mel.set_material_instance_texture_parameter_value(mi, "BaseColor", bc)
mel.set_material_instance_texture_parameter_value(mi, "ORM", orm)
mel.set_material_instance_texture_parameter_value(mi, "Normal", nrm)
mel.update_material_instance(mi)
eal.save_loaded_asset(mi)

# --- Static mesh ---------------------------------------------------------------------------------
if eal.does_asset_exist(f"{DST}/{ASSET}"):
    sms.remove_collisions(load(f"{DST}/{ASSET}"))     # old automatic hulls must not survive the reimport
imported_mesh = import_files([os.path.join(SRC, "Export", f"{ASSET}.fbx")], DST)
mesh = load(f"{DST}/{ASSET}")
# The importer may create a placeholder material from the FBX slot; replace it with ours.
created_mats = [p for p in imported_mesh if "Material" in p or "/M_" in p]
mesh.set_material(0, mi)

bs = sms.get_lod_build_settings(mesh, 0)
bs.set_editor_property("recompute_normals", False)        # keep Blender's weighted normals
bs.set_editor_property("recompute_tangents", False)       # keep MikkTSpace tangents of the bake
bs.set_editor_property("use_mikk_t_space", True)
sms.set_lod_build_settings(mesh, 0, bs)

ns = mesh.get_editor_property("nanite_settings")
ns.set_editor_property("enabled", True)
ns.set_editor_property("fallback_target", unreal.NaniteFallbackTarget.PERCENT_TRIANGLES)  # AUTO ignores the percentage
ns.set_editor_property("fallback_percent_triangles", 1.0)   # ~8k tris: ray tracing uses the real mesh
ns.set_editor_property("fallback_relative_error", 0.0)
mesh.set_editor_property("nanite_settings", ns)

# Collision comes with the FBX as UCX_ boxes (one per board/stringer/block), which keeps the
# fork pockets open. Only if they are missing fall back to an automatic decomposition.
collision_kind = "ucx_from_fbx"
if sms.get_simple_collision_count(mesh) == 0 and sms.get_convex_collision_count(mesh) == 0:
    unreal.log_warning("no UCX collision imported; using convex decomposition")
    sms.set_convex_decomposition_collisions(mesh, 24, 24, 200000)
    collision_kind = "convex_decomposition"
eal.save_loaded_asset(mesh)

for p in created_mats:
    obj = p.split(".")[0]
    if obj != mi_path and eal.does_asset_exist(obj) and not obj.endswith("MI_TechSmoke_PalletWood"):
        eal.delete_asset(obj)

# --- Read back -----------------------------------------------------------------------------------
mesh = load(f"{DST}/{ASSET}")
box = mesh.get_bounding_box()
mn, mx = box.min, box.max
size = [round(mx.x - mn.x, 3), round(mx.y - mn.y, 3), round(mx.z - mn.z, 3)]
bs = sms.get_lod_build_settings(mesh, 0)
report = {
    "engine": unreal.SystemLibrary.get_engine_version(),
    "mesh": mesh.get_path_name(),
    "bounds_min_cm": [round(mn.x, 3), round(mn.y, 3), round(mn.z, 3)],
    "bounds_max_cm": [round(mx.x, 3), round(mx.y, 3), round(mx.z, 3)],
    "size_cm": size,
    "nanite_enabled": bool(mesh.get_editor_property("nanite_settings").get_editor_property("enabled")),
    "lods": sms.get_lod_count(mesh),
    "verts_lod0": sms.get_number_verts(mesh, 0),
    "material_slots": [str(m.get_editor_property("material_interface").get_path_name()) if m.get_editor_property("material_interface") else None
                       for m in mesh.get_editor_property("static_materials")],
    "collision": collision_kind,
    "simple_collision_count": sms.get_simple_collision_count(mesh),
    "convex_collision_count": sms.get_convex_collision_count(mesh),
    "recompute_normals": bs.get_editor_property("recompute_normals"),
    "recompute_tangents": bs.get_editor_property("recompute_tangents"),
    "textures": {t.get_name(): {"srgb": t.get_editor_property("srgb"), "compression": str(t.get_editor_property("compression_settings")),
                                "size": [t.blueprint_get_size_x(), t.blueprint_get_size_y()]} for t in (bc, orm, nrm)},
    "imported": imported_tex + imported_mesh,
    "removed_placeholder_materials": created_mats,
}
os.makedirs(os.path.dirname(REPORT), exist_ok=True)
with open(REPORT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print("G4_IMPORT_REPORT " + json.dumps(report))
