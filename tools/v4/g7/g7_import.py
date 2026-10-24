"""G7 (runs INSIDE the Unreal Editor): import the R03 workshop assets of G7 delivery 1/2.

For each asset: baked textures (BC sRGB, ORM masks, N normal) -> material instance of the G4
M_PBR_Master, FBX with UCX collision and SOCKET_ empties, Nanite on, Blender normals/tangents kept.
Special slots: the fuel filter housing gets a translucent clear-plastic material, the light-bar
diffuser an emissive one (the real light is a Rect Light in the level, see g7_level.py).
Writes Saved/G7/import_report.json. Run via tools/v4/g4/ue_remote.py.
"""
import json
import os

import unreal

ROOT = unreal.Paths.project_dir()
SRC_FBX = os.path.join(ROOT, "ArtSource", "Export", "G7")
SRC_TEX = os.path.join(ROOT, "ArtSource", "Textures", "G7")
DST = "/Game/Genesis/Flussdorf/R03"
MASTER = "/Game/Genesis/Materials/M_PBR_Master"
ASSETS = ["SM_R03_Generator_N02", "SM_R03_Workbench", "SM_R03_PartsShelf", "SM_R03_LightBar"]
REPORT = os.path.join(ROOT, "Saved", "G7", "import_report.json")

at = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
MP = unreal.MaterialProperty


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


def new_material(name, folder):
    path = f"{folder}/{name}"
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    return at.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())


def const3(m, rgb, x, y):
    e = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, x, y)
    e.set_editor_property("constant", unreal.LinearColor(*rgb, 1.0))
    return e


def scalar(m, name, value, x, y):
    e = mel.create_material_expression(m, unreal.MaterialExpressionScalarParameter, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("default_value", value)
    return e


def clear_plastic():
    """Slightly yellowed polycarbonate housing of the inline fuel filter (thin, translucent)."""
    m = new_material("M_G7_ClearPolycarbonate", DST + "/Materials")
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property("translucency_lighting_mode", unreal.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
    m.set_editor_property("two_sided", True)
    mel.connect_material_property(const3(m, (0.85, 0.80, 0.62), -400, -100), "", MP.MP_BASE_COLOR)
    mel.connect_material_property(scalar(m, "Opacity", 0.28, -400, 50), "", MP.MP_OPACITY)
    mel.connect_material_property(scalar(m, "Roughness", 0.08, -400, 150), "", MP.MP_ROUGHNESS)
    mel.connect_material_property(scalar(m, "Specular", 0.6, -400, 250), "", MP.MP_SPECULAR)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    return m


def led_diffuser():
    """Opal LED diffuser: lit milky plastic plus emission. ~4000 K; strength in physical units
    (exposure is physical in this project), tuned so the strip reads as lit but not clipping."""
    m = new_material("M_G7_LEDDiffuser", DST + "/Materials")
    mel.connect_material_property(const3(m, (0.78, 0.78, 0.76), -400, -100), "", MP.MP_BASE_COLOR)
    mul = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -200, 100)
    mel.connect_material_expressions(const3(m, (1.0, 0.91, 0.80), -400, 50), "", mul, "A")
    mel.connect_material_expressions(scalar(m, "EmissiveNits", 2500.0, -400, 200), "", mul, "B")
    mel.connect_material_property(mul, "", MP.MP_EMISSIVE_COLOR)
    mel.connect_material_property(scalar(m, "Roughness", 0.35, -400, 300), "", MP.MP_ROUGHNESS)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    return m


master = load(MASTER)
special = {"FilterHousing": clear_plastic(), "Diffuser": led_diffuser()}
report = {"engine": unreal.SystemLibrary.get_engine_version(), "assets": {}}

for asset in ASSETS:
    folder = f"{DST}/{asset.replace('SM_R03_', '')}"
    texs = import_files([os.path.join(SRC_TEX, asset, f"T_{asset}_{s}.png") for s in ("BC", "ORM", "N")], folder + "/Textures")
    bc, orm, nrm = (load(f"{folder}/Textures/T_{asset}_{s}") for s in ("BC", "ORM", "N"))
    bc.set_editor_property("srgb", True)
    orm.set_editor_property("srgb", False)
    orm.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
    nrm.set_editor_property("srgb", False)
    nrm.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
    nrm.set_editor_property("flip_green_channel", False)          # baked DirectX already
    for t in (bc, orm, nrm):
        eal.save_loaded_asset(t)
    mi_name = "MI_" + asset[3:]
    mi_path = f"{folder}/{mi_name}"
    mi = load(mi_path) if eal.does_asset_exist(mi_path) else at.create_asset(
        mi_name, folder, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, master)
    for p, t in (("BaseColor", bc), ("ORM", orm), ("Normal", nrm)):
        mel.set_material_instance_texture_parameter_value(mi, p, t)
    mel.update_material_instance(mi)
    eal.save_loaded_asset(mi)

    mesh_path = f"{folder}/{asset}"
    if eal.does_asset_exist(mesh_path):
        sms.remove_collisions(load(mesh_path))
    imported = import_files([os.path.join(SRC_FBX, f"{asset}.fbx")], folder)
    mesh = load(mesh_path)
    slots = mesh.get_editor_property("static_materials")
    used = []
    for i, s in enumerate(slots):
        name = str(s.get_editor_property("material_slot_name"))
        mat = next((m for key, m in special.items() if key in name), mi)
        mesh.set_material(i, mat)
        used.append((name, mat.get_name()))
    bs = sms.get_lod_build_settings(mesh, 0)
    bs.set_editor_property("recompute_normals", False)
    bs.set_editor_property("recompute_tangents", False)
    bs.set_editor_property("use_mikk_t_space", True)
    sms.set_lod_build_settings(mesh, 0, bs)
    ns = mesh.get_editor_property("nanite_settings")
    # Translucent slots are not drawn by Nanite: keep the generator a regular mesh (36k tris is cheap).
    ns.set_editor_property("enabled", asset != "SM_R03_Generator_N02")
    ns.set_editor_property("fallback_target", unreal.NaniteFallbackTarget.PERCENT_TRIANGLES)
    ns.set_editor_property("fallback_percent_triangles", 1.0)
    mesh.set_editor_property("nanite_settings", ns)
    eal.save_loaded_asset(mesh)
    # remove placeholder materials the FBX importer created
    for p in imported:
        obj = p.split(".")[0]
        if "/M_" in obj and eal.does_asset_exist(obj):
            eal.delete_asset(obj)

    mesh = load(mesh_path)
    box = mesh.get_bounding_box()
    expected = {"SM_R03_Generator_N02": ["InspectPlug", "InspectFilter", "TryStart"], "SM_R03_LightBar": ["Light"]}.get(asset, [])
    sockets = [n for n in expected if mesh.find_socket(n) or mesh.find_socket("SOCKET_" + n)]
    report["assets"][asset] = {
        "size_cm": [round(box.max.x - box.min.x, 2), round(box.max.y - box.min.y, 2), round(box.max.z - box.min.z, 2)],
        "z_min_cm": round(box.min.z, 2),
        "verts_lod0": sms.get_number_verts(mesh, 0),
        "nanite": bool(mesh.get_editor_property("nanite_settings").get_editor_property("enabled")),
        "simple_collision": sms.get_simple_collision_count(mesh),
        "convex_collision": sms.get_convex_collision_count(mesh),
        "sockets": [str(s) for s in sockets],
        "slots": used,
        "textures": {t.get_name(): [t.blueprint_get_size_x(), t.blueprint_get_size_y(), t.get_editor_property("srgb")] for t in (bc, orm, nrm)},
    }

os.makedirs(os.path.dirname(REPORT), exist_ok=True)
with open(REPORT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, default=str)
print("G7_IMPORT_REPORT " + json.dumps(report, default=str))
