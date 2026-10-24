"""G7 (runs INSIDE the Unreal Editor): import the R03 room shell and set dressing.

- Poly Haven CC0 texture sets (ArtSource/External/PolyHaven, see FA-POLYHAVEN-001) -> /Game/Genesis/Shared/PolyHaven
  (OpenGL normals flipped to DirectX on import).
- M_G7_Tiled: tiling PBR master with the SAME anti-tiling as tools/v4/g7/build_room.py scanned():
  every map sampled twice (second time UV * Scale2, rotated via Cos2/Sin2, + Offset2), blended by the
  height map sampled at 0.09x through a 0.42-0.58 ramp. Bricks/boards: Scale2 1, no rotation (courses stay level).
- SM_R03_Room (world-scale UVs, no bake): MIs of M_G7_Tiled, window glass, zinc sill.
- SM_R03_ToolWall / BenchItems / FloorItems: baked BC/ORM/N on the G4 M_PBR_Master; jar glass translucent.
Writes Saved/G7/room_import_report.json. Run via tools/v4/g4/ue_remote.py.
"""
import json
import math
import os

import unreal

ROOT = unreal.Paths.project_dir()
PH = os.path.join(ROOT, "ArtSource", "External", "PolyHaven")
SRC_FBX = os.path.join(ROOT, "ArtSource", "Export", "G7")
SRC_TEX = os.path.join(ROOT, "ArtSource", "Textures", "G7")
DST = "/Game/Genesis/Flussdorf/R03"
SHARED = "/Game/Genesis/Shared/PolyHaven"
MASTER = "/Game/Genesis/Materials/M_PBR_Master"
TILED = "/Game/Genesis/Materials/M_G7_Tiled"
REPORT = os.path.join(ROOT, "Saved", "G7", "room_import_report.json")

at = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
MP = unreal.MaterialProperty
ST = unreal.MaterialSamplerType


def import_files(files, dest):
    tasks = []
    for f in files:
        t = unreal.AssetImportTask()
        t.filename, t.destination_path = f, dest
        t.automated = t.replace_existing = t.save = True
        tasks.append(t)
    at.import_asset_tasks(tasks)
    return [str(p) for t in tasks for p in t.imported_object_paths]


def load(path):
    a = eal.load_asset(path)
    if a is None:
        raise RuntimeError("missing asset " + path)
    return a


def fresh_material(path):
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    folder, name = path.rsplit("/", 1)
    return at.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())


def expr(m, cls, x, y, **props):
    e = mel.create_material_expression(m, cls, x, y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    return e


def link(a, a_out, b, b_in):
    if not mel.connect_material_expressions(a, a_out, b, b_in):
        raise RuntimeError(f"cannot link {a.get_name()}.{a_out} -> {b.get_name()}.{b_in}")


# ---------------------------------------------------------------- tiled master with anti-tiling
def build_tiled_master(defaults):
    """defaults: {param: texture}. A texture parameter without a texture is a compile error, and the
    instances would silently fall back to the engine checker grid."""
    m = fresh_material(TILED)
    uv = expr(m, unreal.MaterialExpressionTextureCoordinate, -1800, 0)
    scale2 = expr(m, unreal.MaterialExpressionScalarParameter, -1800, 200, parameter_name="Scale2", default_value=1.0)
    # rotation as plain arithmetic (CustomRotator is not exposed to Python): Cos2/Sin2 set per instance
    cos2 = expr(m, unreal.MaterialExpressionScalarParameter, -1800, 300, parameter_name="Cos2", default_value=1.0)
    sin2 = expr(m, unreal.MaterialExpressionScalarParameter, -1800, 350, parameter_name="Sin2", default_value=0.0)
    off2 = expr(m, unreal.MaterialExpressionVectorParameter, -1800, 400, parameter_name="Offset2",
                default_value=unreal.LinearColor(0.37, 0.61, 0, 0))
    mul = expr(m, unreal.MaterialExpressionMultiply, -1650, 200)
    link(uv, "", mul, "A"); link(scale2, "", mul, "B")
    u_ = expr(m, unreal.MaterialExpressionComponentMask, -1550, 150, r=True, g=False, b=False, a=False)
    v_ = expr(m, unreal.MaterialExpressionComponentMask, -1550, 250, r=False, g=True, b=False, a=False)
    link(mul, "", u_, ""); link(mul, "", v_, "")
    def prod(a_, b_, y):
        e = expr(m, unreal.MaterialExpressionMultiply, -1450, y)
        link(a_, "", e, "A"); link(b_, "", e, "B")
        return e
    uc, vs, us, vc = prod(u_, cos2, 120), prod(v_, sin2, 170), prod(u_, sin2, 220), prod(v_, cos2, 270)
    x_ = expr(m, unreal.MaterialExpressionSubtract, -1350, 140)
    link(uc, "", x_, "A"); link(vs, "", x_, "B")
    y_ = expr(m, unreal.MaterialExpressionAdd, -1350, 240)
    link(us, "", y_, "A"); link(vc, "", y_, "B")
    rot = expr(m, unreal.MaterialExpressionAppendVector, -1250, 200)
    link(x_, "", rot, "A"); link(y_, "", rot, "B")
    off_rg = expr(m, unreal.MaterialExpressionComponentMask, -1550, 400, r=True, g=True, b=False, a=False)
    link(off2, "", off_rg, "")
    uv2 = expr(m, unreal.MaterialExpressionAdd, -1150, 250)
    link(rot, "", uv2, "A"); link(off_rg, "", uv2, "B")
    # blend mask: height map at 0.09x, ramp 0.42..0.58
    muv = expr(m, unreal.MaterialExpressionMultiply, -1550, 650)
    link(uv, "", muv, "A")
    c009 = expr(m, unreal.MaterialExpressionConstant, -1800, 700, r=0.09)
    link(c009, "", muv, "B")
    mtex = expr(m, unreal.MaterialExpressionTextureSampleParameter2D, -1300, 650, parameter_name="Mask", sampler_type=ST.SAMPLERTYPE_MASKS,
                texture=defaults["Mask"])
    link(muv, "", mtex, "UVs")
    sub = expr(m, unreal.MaterialExpressionSubtract, -1050, 650)
    link(mtex, "R", sub, "A")
    sub.set_editor_property("const_b", 0.42)
    div = expr(m, unreal.MaterialExpressionDivide, -900, 650)
    link(sub, "", div, "A")
    div.set_editor_property("const_b", 0.16)
    alpha = expr(m, unreal.MaterialExpressionSaturate, -750, 650)
    link(div, "", alpha, "")

    def pair(name, sampler, y):
        a = expr(m, unreal.MaterialExpressionTextureSampleParameter2D, -900, y, parameter_name=name, sampler_type=sampler, texture=defaults[name])
        b = expr(m, unreal.MaterialExpressionTextureSampleParameter2D, -900, y + 180, parameter_name=name, sampler_type=sampler, texture=defaults[name])
        link(uv, "", a, "UVs"); link(uv2, "", b, "UVs")
        lerp = expr(m, unreal.MaterialExpressionLinearInterpolate, -550, y + 90)
        link(a, "RGB", lerp, "A"); link(b, "RGB", lerp, "B"); link(alpha, "", lerp, "Alpha")
        return lerp

    bc = pair("BaseColor", ST.SAMPLERTYPE_COLOR, -900)
    # repaint (same as build_room.scanned(recolor=...)): Tint * (0.55 + 0.9 * luminance), blended by Recolor
    desat = expr(m, unreal.MaterialExpressionDesaturation, -400, -1100)
    link(bc, "", desat, "")
    lum = expr(m, unreal.MaterialExpressionMultiply, -300, -1100)
    link(desat, "", lum, "A")
    lum.set_editor_property("const_b", 0.9)
    lum2 = expr(m, unreal.MaterialExpressionAdd, -200, -1100)
    link(lum, "", lum2, "A")
    lum2.set_editor_property("const_b", 0.55)
    tint = expr(m, unreal.MaterialExpressionVectorParameter, -400, -1250, parameter_name="Tint", default_value=unreal.LinearColor(1, 1, 1, 1))
    tint_rgb = expr(m, unreal.MaterialExpressionComponentMask, -300, -1250, r=True, g=True, b=True, a=False)
    link(tint, "", tint_rgb, "")
    painted = expr(m, unreal.MaterialExpressionMultiply, -100, -1150)
    link(tint_rgb, "", painted, "A"); link(lum2, "", painted, "B")
    recolor = expr(m, unreal.MaterialExpressionScalarParameter, -100, -1300, parameter_name="Recolor", default_value=0.0)
    bc_final = expr(m, unreal.MaterialExpressionLinearInterpolate, 50, -1000)
    link(bc, "", bc_final, "A"); link(painted, "", bc_final, "B"); link(recolor, "", bc_final, "Alpha")
    arm = pair("ARM", ST.SAMPLERTYPE_MASKS, -500)
    nrm = pair("Normal", ST.SAMPLERTYPE_NORMAL, -100)
    mel.connect_material_property(bc_final, "", MP.MP_BASE_COLOR)
    for ch, prop, x in (("R", MP.MP_AMBIENT_OCCLUSION, -350), ("G", MP.MP_ROUGHNESS, -300), ("B", MP.MP_METALLIC, -250)):
        mask = expr(m, unreal.MaterialExpressionComponentMask, x, -500, r=ch == "R", g=ch == "G", b=ch == "B", a=False)
        link(arm, "", mask, "")
        mel.connect_material_property(mask, "", prop)
    nn = expr(m, unreal.MaterialExpressionNormalize, -350, -100)
    link(nrm, "", nn, "")
    mel.connect_material_property(nn, "", MP.MP_NORMAL)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    stats = mel.get_statistics(m)
    print("TILED_MASTER", "instructions", stats.num_pixel_shader_instructions, "samplers", stats.num_samplers)
    return m


def const_material(path, rgb, rough, metal=0.0, translucent_opacity=None):
    m = fresh_material(path)
    if translucent_opacity is not None:
        m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
        m.set_editor_property("translucency_lighting_mode", unreal.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
        m.set_editor_property("two_sided", True)
        mel.connect_material_property(expr(m, unreal.MaterialExpressionConstant, -400, 100, r=translucent_opacity), "", MP.MP_OPACITY)
    mel.connect_material_property(expr(m, unreal.MaterialExpressionConstant3Vector, -400, -100,
                                        constant=unreal.LinearColor(*rgb, 1)), "", MP.MP_BASE_COLOR)
    mel.connect_material_property(expr(m, unreal.MaterialExpressionConstant, -400, 200, r=rough), "", MP.MP_ROUGHNESS)
    mel.connect_material_property(expr(m, unreal.MaterialExpressionConstant, -400, 300, r=metal), "", MP.MP_METALLIC)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    return m


glass = const_material(f"{DST}/Materials/M_G7_WindowGlass", (0.90, 0.96, 0.93), 0.04, translucent_opacity=0.10)
zinc = const_material(f"{DST}/Materials/M_G7_Zinc", (0.58, 0.59, 0.60), 0.45, metal=1.0)
clear = load(f"{DST}/Materials/M_G7_ClearPolycarbonate")

# ---------------------------------------------------------------- Poly Haven sets -> MIs
SETS = {   # slot material: (asset, res, directional, paint colour or None) - must match build_room.py M
    "M_RM_PaintedBrickWhite": ("painted_brick", "4k", True, (0.78, 0.77, 0.74)),
    "M_RM_PaintedBrickGrey": ("painted_brick", "4k", True, (0.20, 0.21, 0.22)),
    "M_RM_EpoxyFloor": ("painted_concrete_02", "4k", False, None),
    "M_RM_CeilingWhite": ("brown_planks_03", "4k", True, (0.80, 0.79, 0.76)),
    "M_RM_FrameAnthracite": ("distressed_painted_planks", "2k", True, (0.05, 0.055, 0.06)),
}
room_mats = {}
tiled = None
for slot, (asset, res, directional, paint) in SETS.items():
    folder = f"{SHARED}/{asset}"
    files = {k: os.path.join(PH, asset, f"{asset}_{k}_{res}.{ext}") for k, ext in (("diff", "jpg"), ("arm", "jpg"), ("nor_gl", "png"), ("disp", "jpg"))}
    import_files(list(files.values()), folder)
    t = {k: load(f"{folder}/{asset}_{k}_{res}") for k in files}
    t["diff"].set_editor_property("srgb", True)
    for k in ("arm", "disp"):
        t[k].set_editor_property("srgb", False)
        t[k].set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
    t["nor_gl"].set_editor_property("srgb", False)
    t["nor_gl"].set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
    t["nor_gl"].set_editor_property("flip_green_channel", True)       # OpenGL -> DirectX
    for x in t.values():
        eal.save_loaded_asset(x)
    if tiled is None:
        tiled = build_tiled_master({"BaseColor": t["diff"], "ARM": t["arm"], "Normal": t["nor_gl"], "Mask": t["disp"]})
    mi_name = "MI_" + slot[2:]
    mi_path = f"{DST}/Room/{mi_name}"
    mi = load(mi_path) if eal.does_asset_exist(mi_path) else at.create_asset(
        mi_name, f"{DST}/Room", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, tiled)
    for p, k in (("BaseColor", "diff"), ("ARM", "arm"), ("Normal", "nor_gl"), ("Mask", "disp")):
        mel.set_material_instance_texture_parameter_value(mi, p, t[k])
    mel.set_material_instance_scalar_parameter_value(mi, "Scale2", 1.0 if directional else 0.73)
    ang = 0.0 if directional else math.radians(37.0)
    mel.set_material_instance_scalar_parameter_value(mi, "Cos2", math.cos(ang))
    mel.set_material_instance_scalar_parameter_value(mi, "Sin2", math.sin(ang))
    mel.set_material_instance_scalar_parameter_value(mi, "Recolor", 1.0 if paint else 0.0)
    if paint:
        mel.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(*paint, 1.0))
    mel.update_material_instance(mi)
    eal.save_loaded_asset(mi)
    room_mats[slot] = mi
room_mats["M_RM_WindowGlass"] = glass
room_mats["M_RM_ZincSill"] = zinc


# ---------------------------------------------------------------- meshes
def import_mesh(asset, folder, slot_map, nanite):
    path = f"{folder}/{asset}"
    if eal.does_asset_exist(path):
        sms.remove_collisions(load(path))
    imported = import_files([os.path.join(SRC_FBX, f"{asset}.fbx")], folder)
    mesh = load(path)
    used = []
    for i, s in enumerate(mesh.get_editor_property("static_materials")):
        name = str(s.get_editor_property("material_slot_name"))
        mat = slot_map(name)
        mesh.set_material(i, mat)
        used.append((name, mat.get_name()))
    bs = sms.get_lod_build_settings(mesh, 0)
    bs.set_editor_property("recompute_normals", False)
    bs.set_editor_property("recompute_tangents", False)
    bs.set_editor_property("use_mikk_t_space", True)
    sms.set_lod_build_settings(mesh, 0, bs)
    ns = mesh.get_editor_property("nanite_settings")
    ns.set_editor_property("enabled", nanite)
    mesh.set_editor_property("nanite_settings", ns)
    eal.save_loaded_asset(mesh)
    for p in imported:
        obj = p.split(".")[0]
        if "/M_" in obj and eal.does_asset_exist(obj) and obj not in (TILED,):
            eal.delete_asset(obj)
    mesh = load(path)
    box = mesh.get_bounding_box()
    return {"size_cm": [round(box.max.x - box.min.x, 1), round(box.max.y - box.min.y, 1), round(box.max.z - box.min.z, 1)],
            "z_min_cm": round(box.min.z, 1), "nanite": nanite, "simple_collision": sms.get_simple_collision_count(mesh),
            "slots": used}


report = {"engine": unreal.SystemLibrary.get_engine_version(), "assets": {}}
report["assets"]["SM_R03_Room"] = import_mesh("SM_R03_Room", f"{DST}/Room", lambda n: room_mats[n], nanite=False)

master = load(MASTER)
TRANSLUCENT = ("ClearJarGlass", "ClockGlass")      # see-through slots of the dressing meshes
for asset, nanite in (("SM_R03_ToolWall", False), ("SM_R03_BenchItems", False), ("SM_R03_FloorItems", True),
                      ("SM_R03_Cabinets", True), ("SM_R03_Equipment", False), ("SM_R03_ServiceCounter", True),
                      ("SM_R03_LiftTable", True)):
    folder = f"{DST}/Dressing/{asset.replace('SM_R03_', '')}"
    import_files([os.path.join(SRC_TEX, asset, f"T_{asset}_{s}.png") for s in ("BC", "ORM", "N")], folder + "/Textures")
    bc, orm, nrm = (load(f"{folder}/Textures/T_{asset}_{s}") for s in ("BC", "ORM", "N"))
    bc.set_editor_property("srgb", True)
    orm.set_editor_property("srgb", False)
    orm.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
    nrm.set_editor_property("srgb", False)
    nrm.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
    nrm.set_editor_property("flip_green_channel", False)
    for x in (bc, orm, nrm):
        eal.save_loaded_asset(x)
    mi_path = f"{folder}/MI_{asset[3:]}"
    mi = load(mi_path) if eal.does_asset_exist(mi_path) else at.create_asset(
        f"MI_{asset[3:]}", folder, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, master)
    for p, x in (("BaseColor", bc), ("ORM", orm), ("Normal", nrm)):
        mel.set_material_instance_texture_parameter_value(mi, p, x)
    mel.update_material_instance(mi)
    eal.save_loaded_asset(mi)
    report["assets"][asset] = import_mesh(asset, folder, lambda n, mi=mi: clear if any(t in n for t in TRANSLUCENT) else mi, nanite)

os.makedirs(os.path.dirname(REPORT), exist_ok=True)
with open(REPORT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, default=str)
print("G7_ROOM_IMPORT " + json.dumps(report, default=str))
