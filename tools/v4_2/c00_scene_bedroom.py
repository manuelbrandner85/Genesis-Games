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


def glass_object_master():
    """QA 2026-10-25: the drinking glass on the nightstand rendered as a sharp-edged ghost box inside the out-of-focus
    background (translucency composited after depth of field) and without refraction. Own master for small glass
    objects: composited before DOF (blurs with the scene), refraction by pixel normal offset (bends what is behind it
    along the curved walls), fresnel-driven opacity (rim reads, faces stay clear)."""
    # v2 (QA 2026-10-25, "das Glas sieht sehr unrealistisch aus"): v1 read milky - light base colour plus opacity
    # made it look frosted. Clear glass is nearly invisible: dark base, low facing opacity, strong grazing reflection
    path = f"{SET}/Materials/M_C00_SetGlassObject_v2"
    if eal.does_asset_exist(path):
        return eal.load_asset(path)
    m = at.create_asset("M_C00_SetGlassObject_v2", f"{SET}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property("translucency_lighting_mode", unreal.TranslucencyLightingMode.TLM_SURFACE)
    m.set_editor_property("translucency_pass", unreal.MaterialTranslucencyPass.MTP_BEFORE_DOF)
    m.set_editor_property("refraction_method", unreal.RefractionMode.RM_PIXEL_NORMAL_OFFSET)
    E = lambda cls, x, y: mel.create_material_expression(m, cls, x, y)
    col = E(unreal.MaterialExpressionVectorParameter, -600, 0)
    col.set_editor_property("parameter_name", "Color")
    col.set_editor_property("default_value", unreal.LinearColor(0.04, 0.045, 0.045, 1))
    mel.connect_material_property(col, "", unreal.MaterialProperty.MP_BASE_COLOR)
    for pn, val, prop, y in (("Roughness", 0.03, unreal.MaterialProperty.MP_ROUGHNESS, 120),
                             ("Specular", 0.5, unreal.MaterialProperty.MP_SPECULAR, 220),
                             ("Refraction", 1.25, unreal.MaterialProperty.MP_REFRACTION, 320)):
        e = E(unreal.MaterialExpressionScalarParameter, -600, y)
        e.set_editor_property("parameter_name", pn)
        e.set_editor_property("default_value", val)
        mel.connect_material_property(e, "", prop)
    fr = E(unreal.MaterialExpressionFresnel, -600, 440)
    fr.set_editor_property("exponent", 5.0)
    base = E(unreal.MaterialExpressionScalarParameter, -600, 560)
    base.set_editor_property("parameter_name", "Opacity")
    base.set_editor_property("default_value", 0.03)
    lp = E(unreal.MaterialExpressionLinearInterpolate, -350, 480)
    mel.connect_material_expressions(base, "", lp, "A")
    one = E(unreal.MaterialExpressionConstant, -600, 660)
    one.set_editor_property("r", 0.85)
    mel.connect_material_expressions(one, "", lp, "B")
    mel.connect_material_expressions(fr, "", lp, "Alpha")
    mel.connect_material_property(lp, "", unreal.MaterialProperty.MP_OPACITY)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    return m


GLASS_OBJ = glass_object_master()
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

WOOD_HLSL = r"""
// v2 (QA 2026-10-25): v1 read as regular corrugated stripes, and the grain ran across the chair legs. Grain direction now
// follows the surface: lying surfaces along the board axis (Along), standing surfaces (legs, sides) vertical.
float3 n = normalize(Nrm);
float3 al = abs(n.z) > 0.7 ? normalize(Along) : float3(0, 0, 1);
float3 ac = normalize(cross(n, al));
float3 p = Pos * 0.01;
float a = dot(p, al);
float c = dot(p, ac);
float rowH = Plank.y;
float row = floor(c / rowH);
float u = a / Plank.x + frac(row * 0.37);
float plank = floor(u);
float h = frac(sin(row * 12.9898 + plank * 78.233) * 43758.5453);
float h2 = frac(sin(row * 3.17 + plank * 19.41) * 1731.13);
// soft, irregular growth figure: low-frequency bands warped along the grain, never periodic-looking
float w1 = sin(a * 1.7 + h * 6.28) * 0.020 + sin(a * 5.3 + h2 * 6.28) * 0.006 + sin(a * 13.0 + c * 40.0) * 0.0015;
float band = sin((c + w1) * (55.0 + 30.0 * h2) + h * 6.28) * 0.5 + 0.5;
band = band * band * (3.0 - 2.0 * band);
float band2 = sin((c + w1 * 1.7) * (140.0 + 60.0 * h) + h2 * 6.28) * 0.5 + 0.5;
// fine pore streaks along the grain
float cell = floor(c * 2500.0);
float pr = frac(sin(cell * 91.7 + floor(a * 30.0) * 13.1) * 43758.5453);
float pores = step(0.82, pr) * (0.6 + 0.4 * sin(a * 300.0 + cell));
float t = saturate(0.45 * h + 0.18 * band + 0.10 * band2 + 0.12);
float3 col = lerp(Dark.rgb, Light.rgb, t) * (1.0 - 0.18 * pores);
float ju = min(frac(u), 1.0 - frac(u)) * Plank.x;
float jv = min(frac(c / rowH), 1.0 - frac(c / rowH)) * rowH;
float joint = 1.0 - saturate(min(ju, jv) / 0.0012);
col *= lerp(1.0, 0.35, joint * Plank.z);
return col;
"""


def wood_master():
    """QA 2026-10-25 ("Lego-Kloetze"): oak in Unreal was a flat colour - the Blender grain does not travel through FBX
    and the box furniture has no UVs. Procedural oak from the world position (no UVs needed): growth rings warped
    along the grain, per-plank tone, pores; optional plank layout with darkened joints (floor laminate). Parameters:
    Along/Across (grain and plank-width directions), Plank (length m, width m, joints 0/1), Dark/Light, Roughness."""
    path = f"{SET}/Materials/M_C00_SetWood_v2"
    if eal.does_asset_exist(path):
        return eal.load_asset(path)
    m = at.create_asset("M_C00_SetWood_v2", f"{SET}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    E = lambda cls, x, y: mel.create_material_expression(m, cls, x, y)
    cus = E(unreal.MaterialExpressionCustom, -400, 0)
    cus.set_editor_property("code", WOOD_HLSL)
    cus.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    names = ["Pos", "Nrm", "Along", "Across", "Plank", "Dark", "Light"]
    ins = []
    for n in names:
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", n)
        ins.append(ci)
    cus.set_editor_property("inputs", ins)
    wp = E(unreal.MaterialExpressionWorldPosition, -800, -100)
    mel.connect_material_expressions(wp, "", cus, "Pos")
    vn = E(unreal.MaterialExpressionVertexNormalWS, -800, -200)
    mel.connect_material_expressions(vn, "", cus, "Nrm")
    for k, (n, dv) in enumerate((("Along", (1, 0, 0)), ("Across", (0, 1, 0)), ("Plank", (100, 100, 0)),
                                ("Dark", (0.30, 0.19, 0.10)), ("Light", (0.52, 0.37, 0.22)))):
        e = E(unreal.MaterialExpressionVectorParameter, -800, k * 110)
        e.set_editor_property("parameter_name", n)
        e.set_editor_property("default_value", unreal.LinearColor(*dv, 1))
        mel.connect_material_expressions(e, "", cus, n)
    mel.connect_material_property(cus, "", unreal.MaterialProperty.MP_BASE_COLOR)
    r = E(unreal.MaterialExpressionScalarParameter, -400, 300)
    r.set_editor_property("parameter_name", "Roughness")
    r.set_editor_property("default_value", 0.45)
    mel.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    return m


WOOD = wood_master()
# slot -> (Along, Across, Plank(length, width, joints), Dark, Light, roughness)
WOOD_LOOK = {
    "M_SZ_OakLaminate": ((1, 0, 0), (0, 1, 0), (1.38, 0.193, 1), (0.34, 0.23, 0.13), (0.55, 0.40, 0.25), 0.42),
    "M_SZ_OakVeneer": ((1, 0, 0), (0, 0, 1), (100, 100, 0), (0.30, 0.19, 0.10), (0.50, 0.35, 0.21), 0.45),
    "M_SZ_FrameWood": ((0, 0, 1), (1, 0, 0), (100, 100, 0), (0.12, 0.07, 0.04), (0.26, 0.16, 0.09), 0.5),
}
# slot name -> (master, colour, roughness, metallic, emissive, opacity); colours are the Blender values
LOOK = {
    "M_SZ_WallWhite": (OPAQUE, (0.80, 0.79, 0.76), 0.9, 0, None, None),
    "M_SZ_Ceiling": (OPAQUE, (0.82, 0.82, 0.80), 0.92, 0, None, None),
    "M_SZ_OakLaminate": (OPAQUE, (0.45, 0.31, 0.19), 0.45, 0, None, None),
    "M_SZ_SkirtingWhite": (OPAQUE, (0.82, 0.82, 0.80), 0.45, 0, None, None),
    "M_SZ_PVCAnthracite": (OPAQUE, (0.055, 0.058, 0.062), 0.35, 0, None, None),
    "M_SZ_Glass": (GLASS, (0.9, 0.93, 0.93), 0.02, 0, None, 0.06),
    "M_SZ_Water": (GLASS_OBJ, (0.95, 0.97, 1.0), 0.0, 0, None, 0.10),
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
    # books (build_c00_nightstand.py): cloth-bound hardcovers, a soft paper cover, gold foil and ink spine titles
    "M_SZ_BookCover0": (FABRIC, (0.05, 0.08, 0.18), 0.8, 0, None, None),
    "M_SZ_BookCover1": (OPAQUE, (0.62, 0.50, 0.30), 0.55, 0, None, None),
    "M_SZ_BookCover2": (FABRIC, (0.30, 0.06, 0.05), 0.8, 0, None, None),
    "M_SZ_BookPages": (OPAQUE, (0.80, 0.76, 0.66), 0.85, 0, None, None),
    "M_SZ_BookFoil": (OPAQUE, (0.80, 0.62, 0.32), 0.35, 1, None, None),
    "M_SZ_BookInk": (OPAQUE, (0.05, 0.05, 0.06), 0.55, 0, None, None),
    "M_SZ_BookHeadband": (FABRIC, (0.55, 0.12, 0.10), 0.5, 0, None, None),
    "M_SZ_BookRibbon": (FABRIC, (0.42, 0.06, 0.07), 0.45, 0, None, None),
    "M_SZ_DrinkGlass": (GLASS_OBJ, (0.92, 0.95, 0.95), 0.02, 0, None, 0.06),
    "M_SZ_MedicineBox": (OPAQUE, (0.80, 0.80, 0.78), 0.5, 0, None, None),
    "M_SZ_RugWool": (FABRIC, (0.55, 0.47, 0.38), 0.95, 0, None, None),
    "M_SZ_ThrowWool": (FABRIC, (0.55, 0.36, 0.08), 0.95, 0, None, None),     # chunky knit (WEAVE_SCALE 28)
    "M_SZ_Rahmen_Familie": (OPAQUE, (0.42, 0.29, 0.17), 0.5, 0, None, None),
    "M_SZ_Rahmen_Ehefrau": (OPAQUE, (0.42, 0.29, 0.17), 0.5, 0, None, None),
    "M_SZ_Rahmen_Strand": (OPAQUE, (0.20, 0.13, 0.08), 0.5, 0, None, None),
}


# weave repeats per UV unit: set meshes have 1 UV unit = 1 m; the shirt's Fab UVs span ~1.4 m of fabric
# (first test at 30/m read as coarse knitting: one tile of the weave map holds ~25 threads -> ~0.25 mm linen threads)
WEAVE_SCALE = {"M_SZ_ThrowWool": 70.0, "M_SZ_RugWool": 60.0, "M_SZ_BookCover0": 600.0, "M_SZ_BookCover2": 600.0, "M_SZ_DuvetSage": 160.0, "M_SZ_PillowLinen": 180.0, "M_SZ_BedLinenWhite": 180.0, "M_C00_ShirtFabric": 260.0}


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
    if slot in WOOD_LOOK:
        al, ac, pl, dk, lt, rg = WOOD_LOOK[slot]
        mi = eal.load_asset(f"{SET}/Materials/MI_{slot[2:]}") if eal.does_asset_exist(f"{SET}/Materials/MI_{slot[2:]}") else             at.create_asset(f"MI_{slot[2:]}", f"{SET}/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi, WOOD)
        for pn, v in (("Along", al), ("Across", ac), ("Plank", pl), ("Dark", dk), ("Light", lt)):
            mel.set_material_instance_vector_parameter_value(mi, pn, unreal.LinearColor(*v, 1))
        mel.set_material_instance_scalar_parameter_value(mi, "Roughness", rg)
        eal.save_loaded_asset(mi)
        return mi
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
        mel.set_material_instance_scalar_parameter_value(mi, "WeaveNormalStrength", 1.0 if slot in ("M_SZ_ThrowWool", "M_SZ_RugWool") else 0.35)
    eal.save_loaded_asset(mi)
    return mi


# ------------------------------------------------------------------ import (once) + level
MESHES = f"{SET}/Meshes"
if os.environ.get("GENESIS_SZ_REIMPORT") or not eal.list_assets(MESHES, recursive=False):
    # QA 2026-10-25: meshes whose Blender objects were removed or renamed (old books, the CR-004 photo) stayed in the
    # folder and were spawned again - clear the folder first (from an empty level, nothing references it then)
    les.new_level("/Temp/C00_ReimportEmpty")
    for _p in eal.list_assets(MESHES, recursive=False):
        eal.delete_asset(_p.split(".")[0])
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
    # QA 2026-10-25: the ArchViz rug (SM_Rug_01) read as a game checkerboard - the own wool rug (SZ_Rug, M_C00_SetFabric
    # with mottled wool and UVs from build_c00_nightstand.py) stays instead
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
                  ("camera_iso", 1600.0 if SHOT == "00b" else 400.0),   # 00-B at f/4: two stops more ISO, same exposure
                  ("camera_shutter_speed", 50.0), ("depth_of_field_fstop", 4.0 if SHOT == "00b" else 2.0),
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

# ------------------------------------------------------------------ the daughter at the bedside (technical test 00-B)
# Regie 2026-10-25: she sits on the chair at the window side at the height of his hip, leans forward and holds his
# (window-side, left) hand - pose and placement from tools/v4_2/c00_pose_tochter.py (docs/v4_2/C00_TOCHTER_SITZ.json)
_sitz = ROOT + "docs/v4_2/C00_TOCHTER_SITZ.json"
# (not in the "bett" close-up of the man: that camera stands where her chair is - she would fill the frame with her back)
if os.environ.get("GENESIS_SZ_TOCHTER", "1") == "1" and SHOT != "bett" and BUILT and os.path.exists(_sitz):
    with open(_sitz, encoding="utf8") as f:
        sitz = json.load(f)
    tochter = eas.spawn_actor_from_class(eal.load_blueprint_class(
        "/Game/Genesis/Characters/C00/Built/Tochter/MHC_C00_Tochter/BP_MHC_C00_Tochter"), V(*sitz["location"]), R(0, 0, sitz["yaw"]))
    tochter.set_actor_label("MH_C00_Tochter")
    t_comps = {c.get_name(): c for c in tochter.get_components_by_class(unreal.SkeletalMeshComponent)}
    for cname, asset in (("Body", "A_C00_Tochter_Sitzen_Built"), ("Face", "A_C00_Tochter_Gesicht_00B_Built")):
        c = t_comps[cname]
        c.set_update_animation_in_editor(True)
        c.override_animation_data(eal.load_asset(f"/Game/Genesis/Characters/C00/Posen/{asset}"), False, True, 0.0, 0.0)
    for cname, c in t_comps.items():                     # outfit pieces follow the posed body
        if cname not in ("Body", "Face"):
            c.set_leader_pose_component(t_comps["Body"])
    for cloth in tochter.get_components_by_class(unreal.ChaosClothComponent):
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
elif SHOT == "00b":                                      # test 00-B: 85 mm on the held hands, near bed-edge height
    # from the foot end, ~90 cm before the hands: her forearm comes in from behind them (+x, +y), not in front
    # aimed between the hands and the old photo on the nightstand, so the focus pull (c00_seq_00b.py) lands in frame
    # re-aimed 2026-10-26 (bed 2.10 m, man 5 cm lower, CR-004 books where the photo stood): between the held hands
    # (~0.33, 0.40, 0.66) and the book stack (~0.67, 1.27, 0.62); tilted down 2026-10-26 (MRQ check): both hands
    # whole in frame - her palm under his hand, her thumb on its back - and the books still upper right
    cam_loc, target, focal = ue((0.22, -0.78, 0.98)), ue((0.40, 0.62, 0.645)), 85.0
elif SHOT == "nacht":                                    # QA: the nightstand close (books, glass, lamp, photo back)
    cam_loc, target, focal = ue((0.30, 0.70, 0.98)), ue((0.78, 1.30, 0.63)), 40.0
elif SHOT == "stuhl":                                    # QA: chair, knitted throw, rug, radiator
    cam_loc, target, focal = ue((0.10, -0.60, 1.20)), ue((1.05, 0.40, 0.45)), 28.0
elif SHOT == "arme":                                     # QA: both of his arms from above (elbows, sleeves, wrists)
    cam_loc, target, focal = ue((-0.40, 0.30, 1.60)), ue((0.15, 0.62, 0.62)), 30.0   # wall side: she cannot block it
elif SHOT == "tochter":                                  # test: the daughter at the bedside, from the foot end (wall side)
    cam_loc, target, focal = ue((-0.35, -0.95, 1.40)), ue((0.72, 0.45, 0.95)), 24.0
else:                                                    # bed-edge height, window side, looking at his face
    cam_loc, target, focal = ue((1.30, 0.15, 1.30)), head + V(0, 22, -8), 35.0
cam = eas.spawn_actor_from_class(unreal.CineCameraActor, cam_loc, unreal.MathLibrary.find_look_at_rotation(cam_loc, target))
cam.set_actor_label("SZ_Cam_" + SHOT)
cc = cam.get_cine_camera_component()
cc.set_editor_property("current_focal_length", focal)
cc.set_editor_property("current_aperture", 4.0 if SHOT == "00b" else 2.0)   # 00-B: both hands sharp at 85 mm
cc.set_editor_property("constrain_aspect_ratio", False)
fs = cc.focus_settings
fs.focus_method = unreal.CameraFocusMethod.MANUAL
fs.manual_focus_distance = (target - cam_loc).length()
if SHOT == "00b":                                        # 00-B opens focused on the hands
    fs.manual_focus_distance = (ue((0.34, 0.40, 0.69)) - cam_loc).length()
cc.set_editor_property("focus_settings", fs)
les.save_current_level()
out = ROOT + f"docs/evidence/V42/C00_Schlafzimmer_UE_{SHOT}.png"
# Regie 2026-10-25 ("Haare fuer die Nahaufnahme"): a still has no temporal history, so 0.1 mm hair strands alias into
# grain and the hairline reads as a cut-out patch. More visibility samples per pixel for the strands, and the shot is
# taken at 2x (3200 x 1800) and filtered down to 1600 x 900 by tools/v4_2/c00_render_bedroom_shots.py (supersampling).
# (8 samples + 4096 deep shadows with two MetaHumans exhausted the 12 GB card - "Video memory has been exhausted" - and
# the engine then dropped the grooms: both figures rendered bald. 4 samples x 2x supersampling = 16 per output pixel)
# The texture pool is capped as well: streaming filled the card and the grooms were dropped at random (bald figures).
for cv in ("r.HairStrands.Visibility.MSAA.SamplePerPixel 4", "r.HairStrands.DeepShadow.Resolution 2048",
           "r.Streaming.PoolSize 3000",
           # always the full strands LOD: at medium distance (shot "raum") the grooms switched to their card LODs,
           # which these built figures render as blocky red geometry or not at all (bald figures, red bounce light)
           "r.HairStrands.ForceLOD 0"):
    unreal.SystemLibrary.execute_console_command(None, cv)
SS = int(os.environ.get("GENESIS_SZ_SS", "2"))
shot_png = out if SS == 1 else ROOT + f"Saved/Shots/C00_Schlafzimmer_UE_{SHOT}_{SS}x.png"
eas.select_nothing()                                     # no selection outline / gizmo in the shot
unreal.EditorLevelLibrary.editor_set_game_view(True)      # hide editor billboards (light icons)
# the viewport looks through the shot camera first and the still is taken 15 s later (the freshly spawned figures'
# grooms bind to the skin over several seconds; at 6 s they were missing at random): hair LODs, virtual textures and
# Lumen settle for this distance (taken at once, the strands came from a distant LOD and the stubble was missing)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam_loc, unreal.MathLibrary.find_look_at_rotation(cam_loc, target))
unreal.AutomationLibrary.take_high_res_screenshot(1600 * SS, 900 * SS, shot_png, cam, False, False, unreal.ComparisonTolerance.LOW, "", 15.0)
print("C00_SZ_SHOT", shot_png)
print("C00_SZ_SCENE", {"shot": SHOT, "man": [round(v) for v in ue(lying["P0"]).to_tuple()], "rot": str(rot), "png": out})
