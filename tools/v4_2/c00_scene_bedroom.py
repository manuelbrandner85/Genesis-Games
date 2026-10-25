"""C00 (runs INSIDE the Unreal Editor): SET_C00_SCHLAFZIMMER with CHR_C00_MANN in bed (look test).

- imports ArtSource/Export/C00/SET_C00_Schlafzimmer.fbx (tools/v4_2/export_c00_bedroom.py, world space)
  into /Game/Genesis/Sets/C00_Schlafzimmer and places every mesh at the origin of L_C00_Schlafzimmer
- material instances per Blender slot name (M_SZ_*) from two masters: opaque surface and thin glass/water
- light like the approved mood: warm 2700 K bedside lamp, cool dusk through the window, dark sky light
- the man: MetaHuman preview actor in the lying transform written by build_c00_bedroom_occupied.py
  (docs/v4_2/C00_BEDROOM_LYING.json), body in pose A_C00_Mann_Liegen, face in A_C00_Mann_Gesicht_Sterbend,
  outfit cloth simulation off
- renders through the real viewport: env GENESIS_SZ_SHOT = "bett" (bed-edge height, ScriptLock 00-A) or
  "raum" (door corner) or "wand" (foot end, photo above the bed); output docs/evidence/V42/C00_Schlafzimmer_UE_<shot>.png
Blender metres -> Unreal cm: (100x, -100y, 100z).
"""
import json
import os
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
FBX = ROOT + "ArtSource/Export/C00/SET_C00_Schlafzimmer.fbx"
SET = "/Game/Genesis/Sets/C00_Schlafzimmer"
LEVEL = SET + "/L_C00_Schlafzimmer"
SHOT = os.environ.get("GENESIS_SZ_SHOT", "bett")
V, R = unreal.Vector, unreal.Rotator
eal = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mh = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)


def ue(p):
    return V(p[0] * 100, -p[1] * 100, p[2] * 100)


def ue_dir(d):
    return V(d[0], -d[1], d[2])


# ------------------------------------------------------------------ masters
def master(name, translucent=False):
    path = f"{SET}/Materials/{name}"
    if eal.does_asset_exist(path):
        return eal.load_asset(path)
    m = at.create_asset(name, f"{SET}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    p = {}
    for i, (pn, kind, default) in enumerate((("Color", "v", (0.5, 0.5, 0.5)), ("Roughness", "s", 0.6), ("Metallic", "s", 0.0),
                                             ("Specular", "s", 0.5), ("Emissive", "v", (0, 0, 0)), ("Opacity", "s", 0.1))):
        cls = unreal.MaterialExpressionVectorParameter if kind == "v" else unreal.MaterialExpressionScalarParameter
        e = mel.create_material_expression(m, cls, -500, i * 140)
        e.set_editor_property("parameter_name", pn)
        if kind == "v":
            e.set_editor_property("default_value", unreal.LinearColor(*default, 1))
        else:
            e.set_editor_property("default_value", default)
        p[pn] = e
    mel.connect_material_property(p["Color"], "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(p["Roughness"], "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(p["Metallic"], "", unreal.MaterialProperty.MP_METALLIC)
    mel.connect_material_property(p["Specular"], "", unreal.MaterialProperty.MP_SPECULAR)
    mel.connect_material_property(p["Emissive"], "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    if translucent:
        m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
        m.set_editor_property("translucency_lighting_mode", unreal.TranslucencyLightingMode.TLM_SURFACE)
        mel.connect_material_property(p["Opacity"], "", unreal.MaterialProperty.MP_OPACITY)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    return m


OPAQUE, GLASS = master("M_C00_SetSurface"), master("M_C00_SetGlass", True)
WEAVE_N = "/Game/Fab/MetaHuman/Jeans/Materials/Textures/Clothing/Micros/micro_weave_plain_normal"   # Fab, local only
WEAVE_A = "/Game/Fab/MetaHuman/Jeans/Materials/Textures/Clothing/Micros/micro_weave_plain"


def fabric_master():
    """Regie 2026-10-25 ("Decke und Hemd fuer die Nahaufnahme"): textiles were flat colours - a plastic balloon up close.
    Fibre sheen (grazing-angle brightening, as on cotton/linen; the Cloth shading model's input is not reachable from
    Python) with three detail levels: plain-weave normal + thread shading (micro, UV-tiled,
    1 UV unit = 1 m on the set meshes), a soft mottling of colour and roughness (medium, world noise ~15 cm) and the
    geometry folds from Blender (macro)."""
    path = f"{SET}/Materials/M_C00_SetFabric"
    if eal.does_asset_exist(path):
        return eal.load_asset(path)
    m = at.create_asset("M_C00_SetFabric", f"{SET}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    E = lambda cls, x, y: mel.create_material_expression(m, cls, x, y)
    C = mel.connect_material_expressions

    def scalar(name, val, x, y):
        e = E(unreal.MaterialExpressionScalarParameter, x, y)
        e.set_editor_property("parameter_name", name)
        e.set_editor_property("default_value", val)
        return e

    def mul(a, b, x, y, ao="", bo=""):
        e = E(unreal.MaterialExpressionMultiply, x, y)
        C(a, ao, e, "A")
        C(b, bo, e, "B")
        return e

    def lerp(a, b, alpha, x, y, alpha_out=""):
        e = E(unreal.MaterialExpressionLinearInterpolate, x, y)
        C(a, "", e, "A")
        C(b, "", e, "B")
        C(alpha, alpha_out, e, "Alpha")
        return e

    def const(v, x, y):
        e = E(unreal.MaterialExpressionConstant, x, y)
        e.set_editor_property("r", v)
        return e

    col = E(unreal.MaterialExpressionVectorParameter, -1400, 0)
    col.set_editor_property("parameter_name", "Color")
    col.set_editor_property("default_value", unreal.LinearColor(0.5, 0.5, 0.5, 1))
    uv = E(unreal.MaterialExpressionTextureCoordinate, -1600, 300)
    uvs = mul(uv, scalar("WeaveScale", 40.0, -1600, 420), -1400, 300)
    wn = E(unreal.MaterialExpressionTextureSampleParameter2D, -1200, 300)
    wn.set_editor_property("parameter_name", "WeaveNormal")
    wn.set_editor_property("texture", eal.load_asset(WEAVE_N))
    wn.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    C(uvs, "", wn, "UVs")
    flat = E(unreal.MaterialExpressionConstant3Vector, -1200, 520)
    flat.set_editor_property("constant", unreal.LinearColor(0, 0, 1, 1))
    nrm = lerp(flat, wn, scalar("WeaveNormalStrength", 0.6, -1200, 620), -900, 400)
    nn = E(unreal.MaterialExpressionNormalize, -700, 400)
    C(nrm, "", nn, "VectorInput")
    mel.connect_material_property(nn, "", unreal.MaterialProperty.MP_NORMAL)
    wa = E(unreal.MaterialExpressionTextureSampleParameter2D, -1200, 0)
    wa.set_editor_property("parameter_name", "WeaveThreads")
    wa.set_editor_property("texture", eal.load_asset(WEAVE_A))
    C(uvs, "", wa, "UVs")
    thread = lerp(const(0.86, -1000, -120), const(1.0, -1000, -60), wa, -850, -60, "R")   # thread/gap shading
    noise = E(unreal.MaterialExpressionNoise, -1200, 160)                                     # soft mottling, worn spots
    noise.set_editor_property("scale", 6.0)
    noise.set_editor_property("levels", 4)
    noise.set_editor_property("output_min", 0.0)
    noise.set_editor_property("output_max", 1.0)
    mott = lerp(const(0.92, -1000, 100), const(1.05, -1000, 160), noise, -850, 120)
    fres = E(unreal.MaterialExpressionFresnel, -850, 200)                                     # fibre sheen at grazing angles
    fres.set_editor_property("exponent", 3.0)
    fres.set_editor_property("base_reflect_fraction", 0.0)
    sheen = lerp(const(1.0, -700, 160), scalar("Sheen", 1.25, -700, 200), fres, -600, 160)
    base = mul(mul(mul(col, thread, -650, 0), mott, -450, 40), sheen, -300, 60)
    mel.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
    rough = mul(scalar("Roughness", 0.85, -700, 220), lerp(const(0.95, -900, 260), const(1.04, -900, 320), noise, -700, 300), -450, 240)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    sp = scalar("Specular", 0.4, -450, 360)
    mel.connect_material_property(sp, "", unreal.MaterialProperty.MP_SPECULAR)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    return m


FABRIC = fabric_master()
# slot name -> (master, colour, roughness, metallic, emissive, opacity); colours are the Blender values
LOOK = {
    "M_SZ_WallWhite": (OPAQUE, (0.80, 0.79, 0.76), 0.9, 0, None, None),
    "M_SZ_Ceiling": (OPAQUE, (0.82, 0.82, 0.80), 0.92, 0, None, None),
    "M_SZ_OakLaminate": (OPAQUE, (0.45, 0.31, 0.19), 0.45, 0, None, None),
    "M_SZ_SkirtingWhite": (OPAQUE, (0.82, 0.82, 0.80), 0.45, 0, None, None),
    "M_SZ_PVCAnthracite": (OPAQUE, (0.055, 0.058, 0.062), 0.35, 0, None, None),
    "M_SZ_Glass": (GLASS, (0.9, 0.93, 0.93), 0.02, 0, None, 0.06),
    "M_SZ_Water": (GLASS, (0.95, 0.97, 1.0), 0.0, 0, None, 0.25),
    "M_SZ_RainStreak": (GLASS, (0.8, 0.85, 0.9), 0.1, 0, None, 0.15),
    "M_SZ_SillWhite": (OPAQUE, (0.78, 0.78, 0.76), 0.25, 0, None, None),
    "M_SZ_RadiatorWhite": (OPAQUE, (0.80, 0.80, 0.78), 0.35, 0, None, None),
    "M_SZ_ShutterAlu": (OPAQUE, (0.06, 0.065, 0.07), 0.45, 1, None, None),
    "M_SZ_CurtainGrey": (OPAQUE, (0.42, 0.42, 0.41), 0.9, 0, None, None),
    "M_SZ_BedUpholstery": (OPAQUE, (0.30, 0.30, 0.31), 0.9, 0, None, None),
    "M_SZ_BedLinenWhite": (FABRIC, (0.78, 0.78, 0.76), 0.8, 0, None, None),
    "M_SZ_DuvetSage": (FABRIC, (0.30, 0.38, 0.29), 0.85, 0, None, None),      # Regie: washed sage-green linen
    "M_SZ_PillowLinen": (FABRIC, (0.74, 0.70, 0.63), 0.85, 0, None, None),
    # the man's sleep shirt: light blue-grey cotton jersey (replaces the Fab MI, whose vertex-colour layer masks
    # broke into patches on the fitted, subdivided shirt)
    "M_C00_ShirtFabric": (FABRIC, (0.36, 0.42, 0.50), 0.8, 0, None, None),
    "M_SZ_OakVeneer": (OPAQUE, (0.42, 0.29, 0.17), 0.45, 0, None, None),
    "M_SZ_LampShadeLinen": (OPAQUE, (0.85, 0.80, 0.70), 0.8, 0, (1.0, 0.62, 0.32), None),
    "M_SZ_LampCeramic": (OPAQUE, (0.62, 0.60, 0.56), 0.3, 0, None, None),
    "M_SZ_FrameBack": (OPAQUE, (0.33, 0.24, 0.16), 0.9, 0, None, None),
    "M_SZ_FrameWood": (OPAQUE, (0.20, 0.13, 0.08), 0.5, 0, None, None),
    "M_SZ_DoorWhite": (OPAQUE, (0.80, 0.80, 0.78), 0.35, 0, None, None),
    "M_SZ_BrushedSteel": (OPAQUE, (0.55, 0.55, 0.56), 0.3, 1, None, None),
    "M_SZ_SwitchWhite": (OPAQUE, (0.84, 0.84, 0.82), 0.3, 0, None, None),
    "M_SZ_DuskSky": (OPAQUE, (0, 0, 0), 1.0, 0, (0.035, 0.06, 0.14), None),
    "M_SZ_FacadePlaster": (OPAQUE, (0.30, 0.29, 0.27), 0.85, 0, None, None),
    "M_SZ_RoofDark": (OPAQUE, (0.04, 0.04, 0.045), 0.6, 0, None, None),
    "M_SZ_FacadeGlassDark": (OPAQUE, (0.01, 0.012, 0.016), 0.05, 0, None, None),
    "M_SZ_FacadeWindowWarm": (OPAQUE, (0, 0, 0), 1.0, 0, (3.5, 2.17, 1.05), None),
    "M_SZ_FacadeWindowTV": (OPAQUE, (0, 0, 0), 1.0, 0, (0.54, 0.66, 1.2), None),
    "M_SZ_WetAsphalt": (OPAQUE, (0.02, 0.02, 0.022), 0.08, 0, None, None),
    "M_SZ_LampPole": (OPAQUE, (0.05, 0.05, 0.05), 0.4, 1, None, None),
    "M_SZ_StreetLED": (OPAQUE, (0, 0, 0), 1.0, 0, (25.0, 21.0, 16.0), None),
    # lived-in decor (build_c00_bedroom_decor.py)
    "M_SZ_PassepartoutWhite": (OPAQUE, (0.82, 0.80, 0.76), 0.85, 0, None, None),
    "M_SZ_BookCover0": (OPAQUE, (0.08, 0.13, 0.30), 0.55, 0, None, None),
    "M_SZ_BookCover1": (OPAQUE, (0.55, 0.42, 0.18), 0.55, 0, None, None),
    "M_SZ_BookCover2": (OPAQUE, (0.38, 0.10, 0.08), 0.55, 0, None, None),
    "M_SZ_BookPages": (OPAQUE, (0.78, 0.74, 0.64), 0.8, 0, None, None),
    "M_SZ_DrinkGlass": (GLASS, (0.92, 0.95, 0.95), 0.02, 0, None, 0.12),
    "M_SZ_MedicineBox": (OPAQUE, (0.80, 0.80, 0.78), 0.5, 0, None, None),
    "M_SZ_RugWool": (OPAQUE, (0.55, 0.47, 0.38), 0.95, 0, None, None),
    "M_SZ_ThrowWool": (OPAQUE, (0.55, 0.36, 0.08), 0.95, 0, None, None),
    "M_SZ_Rahmen_Familie": (OPAQUE, (0.42, 0.29, 0.17), 0.5, 0, None, None),
    "M_SZ_Rahmen_Ehefrau": (OPAQUE, (0.42, 0.29, 0.17), 0.5, 0, None, None),
    "M_SZ_Rahmen_Strand": (OPAQUE, (0.20, 0.13, 0.08), 0.5, 0, None, None),
}


# weave repeats per UV unit: set meshes have 1 UV unit = 1 m; the shirt's Fab UVs span ~1.4 m of fabric
# (first test at 30/m read as coarse knitting: one tile of the weave map holds ~25 threads -> ~0.25 mm linen threads)
WEAVE_SCALE = {"M_SZ_DuvetSage": 160.0, "M_SZ_PillowLinen": 180.0, "M_SZ_BedLinenWhite": 180.0, "M_C00_ShirtFabric": 260.0}


def photo_material(key="VaterTochter"):
    """Framed prints: father and daughter (tools/v4_2/c00_photo_vater_tochter.py) and the family photos
    (local FLUX.2 klein, ArtSource/Reference/C00/PROPS_C00_FOTOS) - texture T_C00_Foto_<key>."""
    tex_path = f"{SET}/Textures/T_C00_Foto_{key}"
    task = unreal.AssetImportTask()
    task.filename = ROOT + f"ArtSource/Export/C00/T_C00_Foto_{key}.png"
    task.destination_path, task.automated, task.replace_existing, task.save = f"{SET}/Textures", True, True, True
    at.import_asset_tasks([task])
    tex = eal.load_asset(tex_path)
    name = "M_C00_SetPhoto" if key == "VaterTochter" else f"M_C00_SetPhoto_{key}"
    path = f"{SET}/Materials/{name}"
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    m = at.create_asset(name, f"{SET}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    t = mel.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -500, 0)
    t.set_editor_property("parameter_name", "Photo")
    t.set_editor_property("texture", tex)
    mel.connect_material_property(t, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    r = mel.create_material_expression(m, unreal.MaterialExpressionConstant, -300, 200)
    r.set_editor_property("r", 0.38)                              # satin photo paper
    mel.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    return m


def instance(slot):
    if slot == "M_SZ_FotoVaterTochter":
        return photo_material()
    if slot.startswith("M_SZ_Foto_"):
        return photo_material(slot[len("M_SZ_Foto_"):])
    name = "MI_" + slot[2:]
    path = f"{SET}/Materials/{name}"
    parent, rgb, rough, metal, emis, opac = LOOK.get(slot, (OPAQUE, (0.5, 0.5, 0.5), 0.6, 0, None, None))
    mi = eal.load_asset(path) if eal.does_asset_exist(path) else at.create_asset(
        name, f"{SET}/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, parent)
    mel.set_material_instance_vector_parameter_value(mi, "Color", unreal.LinearColor(*rgb, 1))
    mel.set_material_instance_scalar_parameter_value(mi, "Roughness", rough)
    mel.set_material_instance_scalar_parameter_value(mi, "Metallic", float(metal))
    if emis:
        mel.set_material_instance_vector_parameter_value(mi, "Emissive", unreal.LinearColor(*emis, 1))
    if opac is not None:
        mel.set_material_instance_scalar_parameter_value(mi, "Opacity", opac)
    if parent == FABRIC and slot in WEAVE_SCALE:
        mel.set_material_instance_scalar_parameter_value(mi, "WeaveScale", WEAVE_SCALE[slot])
        mel.set_material_instance_scalar_parameter_value(mi, "WeaveNormalStrength", 0.35)
    eal.save_loaded_asset(mi)
    return mi


# ------------------------------------------------------------------ import (once) + level
MESHES = f"{SET}/Meshes"
if os.environ.get("GENESIS_SZ_REIMPORT") or not eal.list_assets(MESHES, recursive=False):
    task = unreal.AssetImportTask()
    task.filename, task.destination_path = FBX, MESHES
    task.automated, task.replace_existing, task.save = True, True, True
    opt = unreal.FbxImportUI()
    opt.import_mesh, opt.import_materials, opt.import_textures, opt.import_animations = True, False, False, False
    opt.import_as_skeletal = False
    opt.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    sm = opt.static_mesh_import_data
    sm.set_editor_property("combine_meshes", False)
    sm.set_editor_property("auto_generate_collision", False)
    sm.set_editor_property("generate_lightmap_u_vs", False)
    sm.set_editor_property("convert_scene", True)
    sm.set_editor_property("transform_vertex_to_absolute", True)
    task.options = opt
    at.import_asset_tasks([task])
    for p in eal.list_assets(MESHES, recursive=False):
        mesh = eal.load_asset(p.split(".")[0])
        if isinstance(mesh, unreal.StaticMesh):
            for i, slot in enumerate(mesh.static_materials):
                mesh.set_material(i, instance(str(slot.material_slot_name)))
            eal.save_loaded_asset(mesh)

if eal.does_asset_exist(LEVEL):
    les.load_level(LEVEL)
else:
    les.new_level(LEVEL)
for a in eas.get_all_level_actors():
    eas.destroy_actor(a)
for p in eal.list_assets(MESHES, recursive=False):
    mesh = eal.load_asset(p.split(".")[0])
    if isinstance(mesh, unreal.StaticMesh):
        a = eas.spawn_actor_from_object(mesh, V(0, 0, 0), R(0, 0, 0))
        a.set_actor_label(mesh.get_name())

# ------------------------------------------------------------------ lived-in decor from Epic's ArchViz Interior
# (Fab, Epic content, local only: Content/Meshes|Plants|Materials|textures are gitignored). Regie 2026-10-25:
# "viel wohnlicher, nicht so kalt ... alles muss passen". Positions in Blender metres; the mesh is set down on
# the given surface height by its bounds; yaw turns pictures to face into the room.
ARCHVIZ = (
    # Regie 2026-10-25: the plants stand in real pots (36 cm ceramic pot + soil), no loose decorative pillow
    ("/Game/Meshes/SM_Pot_04", (1.40, -1.25), 0.0, 0.0),
    ("/Game/Meshes/SM_Soil", (1.40, -1.25), 0.315, 0.0),
    ("/Game/Plants/SM_Dracaena_01", (1.40, -1.25), 0.30, 0.0),         # window corner, beside the curtain
    ("/Game/Meshes/SM_Pot_04", (-1.45, 1.05), 0.0, 30.0),
    ("/Game/Meshes/SM_Soil", (-1.45, 1.05), 0.315, 0.0),
    ("/Game/Plants/SM_SnakePlant_02", (-1.45, 1.05), 0.30, 30.0),       # beside the door, near the headboard wall
    ("/Game/Meshes/SM_Rug_01", (0.95, 0.10), 0.0, 90.0),                # wool rug along the bed, window side
    # (the ArchViz picture frames lost their materials - own framed family photos, build_c00_bedroom_decor.py)
)
for path, (bx, by), surface, yaw in ARCHVIZ:
    mesh = eal.load_asset(path)
    if not mesh:
        continue
    bb = mesh.get_bounding_box()
    c = (bb.min + bb.max) * 0.5
    off = unreal.MathLibrary.greater_greater_vector_rotator(V(c.x, c.y, 0), unreal.Rotator(0, 0, yaw))   # rotate the pivot offset
    loc = ue((bx, by, surface)) - off - V(0, 0, bb.min.z)
    if path.endswith(("Picture_03", "Picture_04")):                     # hang by the centre, not the bottom
        loc = ue((bx, by, surface)) - off - V(0, 0, c.z)
    a = eas.spawn_actor_from_object(mesh, loc, R(0, 0, yaw))
    a.set_actor_label("AV_" + path.rsplit("/", 1)[-1])
for a in eas.get_all_level_actors():                                   # the ArchViz rug replaces the plain one
    if a.get_actor_label() == "UE_SZ_Rug":
        eas.destroy_actor(a)

# ------------------------------------------------------------------ light
blender_lamp = (-0.25 + 0.75 + 0.27 + 0.10, 3.20 / 2 - 0.22 + 0.06, 0.88)
lamp = eas.spawn_actor_from_class(unreal.PointLight, ue(blender_lamp))
lamp.set_actor_label("SZ_LampLight")
lc = lamp.point_light_component
lc.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
lc.set_editor_property("intensity", 450.0)                       # 40 W-equivalent bulb behind a linen shade
lc.set_editor_property("use_temperature", True)
lc.set_editor_property("temperature", 2700.0)
lc.set_editor_property("source_radius", 6.0)
lc.set_editor_property("attenuation_radius", 900.0)
win = eas.spawn_actor_from_class(unreal.RectLight, ue((3.6 / 2 + 0.05, 0.35, 1.55)), R(0, 0, 180))
win.set_actor_label("SZ_WindowDusk")
wc = win.get_component_by_class(unreal.RectLightComponent)
wc.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
wc.set_editor_property("intensity", 120.0)
wc.set_editor_property("use_temperature", True)
wc.set_editor_property("temperature", 9000.0)
wc.set_editor_property("source_width", 140.0)
wc.set_editor_property("source_height", 130.0)
sky = eas.spawn_actor_from_class(unreal.SkyLight, V(0, 0, 200))
sky.light_component.set_editor_property("intensity", 0.05)
sky.light_component.set_editor_property("light_color", unreal.Color(70, 90, 140, 255))
ppv = eas.spawn_actor_from_class(unreal.PostProcessVolume, V(0, 0, 0))
ppv.set_editor_property("unbound", True)
st = ppv.settings
for prop, val in (("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL), ("auto_exposure_apply_physical_camera_exposure", True),
                  ("camera_iso", 400.0), ("camera_shutter_speed", 50.0), ("depth_of_field_fstop", 2.0),
                  ("film_grain_intensity", 0.15), ("vignette_intensity", 0.35),
                  # camera white balance 5000 K (3700 K made the dusk-lit room moon-blue; 6500 K turned skin orange), as a photographer would set it:
                  # the room stays warm, but skin is no longer orange and the blue-grey shirt no longer reads brown
                  ("white_temp", 5000.0)):
    st.set_editor_property(prop, val)
    st.set_editor_property("override_" + prop, True)
ppv.set_editor_property("settings", st)

# ------------------------------------------------------------------ the man in bed
with open(ROOT + "docs/v4_2/C00_BEDROOM_LYING.json", encoding="utf8") as f:
    lying = json.load(f)
BUILT = os.environ.get("GENESIS_SZ_MAN", "built") == "built"
rot = unreal.MathLibrary.make_rot_from_yz(ue_dir(lying["local_y"]), ue_dir(lying["local_z"]))
if BUILT:
    # 2026-10-25: the built, animatable MetaHuman (4K textures, auto-rigged face; tools/v4_2/c00_mh_build.py).
    # Its skeletons are copies under Built/Common, so it uses the *_Built pose assets (same bone names).
    man = eas.spawn_actor_from_class(eal.load_blueprint_class(
        "/Game/Genesis/Characters/C00/Built/Mann/MHC_C00_Mann/BP_MHC_C00_Mann"), ue(lying["P0"]), rot)
    SUF = "_Built"
else:
    ch = eal.load_asset("/Game/Genesis/Characters/C00/MHC_C00_Mann")
    if not mh.is_object_added_for_editing(ch):
        mh.try_add_object_to_edit(ch)
    man = mh.spawn_meta_human_actor(ch, True)
    mh.assemble_for_preview(ch)
    SUF = ""
man.set_actor_label("MH_C00_Mann")
man.set_actor_location_and_rotation(ue(lying["P0"]), rot, False, True)
body = next(c for c in man.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Body")
body.set_update_animation_in_editor(True)
body.override_animation_data(eal.load_asset(f"/Game/Genesis/Characters/C00/Posen/A_C00_Mann_Liegen{SUF}"), False, True, 0.0, 0.0)
face = next(c for c in man.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Face")
face.set_update_animation_in_editor(True)                 # Regie: the features of a dying man (c00_face_dying.py)
face.override_animation_data(eal.load_asset(f"/Game/Genesis/Characters/C00/Posen/A_C00_Mann_Gesicht_Sterbend{SUF}"), False, True, 0.0, 0.0)
# own skinned shirt (tools/v4_2/c00_shirt_gs_skin.py) follows the posed body - the MetaHuman outfit would not
shirt_skm = eal.load_asset("/Game/Genesis/Characters/C00/Kleidung/SKM_C00_Mann_Shirt")
if shirt_skm:
    wear = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, man.get_actor_location(), man.get_actor_rotation())
    wear.set_actor_label("MH_C00_Mann_Shirt")
    wc_ = wear.skeletal_mesh_component
    wc_.set_skeletal_mesh_asset(shirt_skm)
    wc_.attach_to_component(body, "", unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET,
                            unreal.AttachmentRule.SNAP_TO_TARGET, False)
    wc_.set_leader_pose_component(body)
    for i in range(wc_.get_num_materials()):
        wc_.set_material(i, instance("M_C00_ShirtFabric"))
for cloth in man.get_components_by_class(unreal.ChaosClothComponent):
    cloth.set_enable_simulation(False)

# ------------------------------------------------------------------ camera + render
head = ue(lying["head_world"])
if SHOT == "tuer":                                       # from the window corner toward the door / west wall
    cam_loc, target, focal = ue((1.55, 1.30, 1.65)), ue((-1.70, -0.10, 1.30)), 18.0
elif SHOT == "weit":                                       # wide overview from above the door corner
    cam_loc, target, focal = ue((-1.65, -1.50, 2.05)), ue((0.70, 0.50, 0.75)), 14.0
elif SHOT == "wand":                                       # from the foot end: bed, man and the photo above the bed
    cam_loc, target, focal = ue((0.55, -1.30, 1.40)), ue((-0.20, 1.40, 1.20)), 22.0
elif SHOT == "raum":
    cam_loc, target, focal = ue((-1.55, -1.45, 1.25)), ue((0.30, 0.95, 0.70)), 24.0
else:                                                    # bed-edge height, window side, looking at his face
    cam_loc, target, focal = ue((1.30, 0.15, 1.30)), head + V(0, 22, -8), 35.0
cam = eas.spawn_actor_from_class(unreal.CineCameraActor, cam_loc, unreal.MathLibrary.find_look_at_rotation(cam_loc, target))
cam.set_actor_label("SZ_Cam_" + SHOT)
cc = cam.get_cine_camera_component()
cc.set_editor_property("current_focal_length", focal)
cc.set_editor_property("current_aperture", 2.0)
cc.set_editor_property("constrain_aspect_ratio", False)
fs = cc.focus_settings
fs.focus_method = unreal.CameraFocusMethod.MANUAL
fs.manual_focus_distance = (target - cam_loc).length()
cc.set_editor_property("focus_settings", fs)
les.save_current_level()
out = ROOT + f"docs/evidence/V42/C00_Schlafzimmer_UE_{SHOT}.png"
eas.select_nothing()                                     # no selection outline / gizmo in the shot
unreal.EditorLevelLibrary.editor_set_game_view(True)      # hide editor billboards (light icons)
unreal.AutomationLibrary.take_high_res_screenshot(1600, 900, out, cam, False, False, unreal.ComparisonTolerance.LOW, "", 1.0)
print("C00_SZ_SCENE", {"shot": SHOT, "man": [round(v) for v in ue(lying["P0"]).to_tuple()], "rot": str(rot), "png": out})
