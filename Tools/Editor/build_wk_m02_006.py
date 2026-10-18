# WK-M02-006: imports the NASA SVS star map and builds the sky material (atmosphere + stars + airglow).
# Run: UnrealEditor-Cmd.exe Genesis.uproject -run=pythonscript -script="<this file>"
import json
import os

import unreal

MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
SKY_DIR = "/Game/Genesis/Sky"
TEX_NAME = "T_StarMap_2020_8k"
MAT_NAME = "M_GenesisSky"

# Reference values for the natural night sky (Leinert et al. 1998, "The 1997 reference of diffuse night sky
# brightness"): integrated starlight ~23.0 mag/arcsec^2, airglow at zenith ~22.4 mag/arcsec^2 (V band).
# L[cd/m^2] = 10.8e4 * 10^(-0.4 m)
INTEGRATED_STARLIGHT_CDM2 = 10.8e4 * 10 ** (-0.4 * 23.0)
AIRGLOW_ZENITH_CDM2 = 10.8e4 * 10 ** (-0.4 * 22.4)
EXTINCTION_MAG_PER_AIRMASS = 0.2

UV_CODE = """float3 d = -normalize(D);
float lx = dot(d, A0.xyz);
float ly = dot(d, A18.xyz);
float lz = dot(d, P.xyz);
float ra = atan2(-ly, lx);
float dec = asin(clamp(lz, -1.0, 1.0));
return float2(frac(0.5 - ra / (2.0 * PI)), 0.5 - dec / PI);"""

NIGHT_CODE = """float3 d = -normalize(D);
if (d.z <= 0.0) { return float3(0.0, 0.0, 0.0); }
float X = 1.0 / max(d.z, 0.03);
float T = pow(10.0, -0.4 * ExtMag * X);
float vr = rsqrt(1.0 - 0.9693 * (1.0 - d.z * d.z));
float3 tint = float3(0.75, 1.0, 0.6) / 0.918;
float3 night = Stars * StarScale * T + Airglow * vr * T * tint;
// Tiefe Daemmerung: Zenitwert, zum Horizont und Richtung Sonne heller; Zenit blau (Ozon), sonnenseitig waermer.
float2 dh = normalize(d.xy + float2(1e-5, 0.0));
float toSun = max(dot(dh, normalize(SunDir.xy + float2(1e-5, 0.0))), 0.0);
float horizon = 1.0 - d.z;
float shape = (1.0 + horizon) * (1.0 + 2.0 * toSun * toSun * horizon * horizon);
float3 blue = float3(0.55, 0.75, 1.0) / 0.7255;
float3 warm = float3(1.0, 0.72, 0.45) / 0.7600;
float3 twilightColor = lerp(blue, warm, saturate(toSun * horizon * horizon));
return night + Twilight * shape * twilightColor;"""


def log(msg):
    unreal.log("GENESIS_BUILD " + msg)


def import_star_map(project_dir):
    src = os.path.join(project_dir, "SourceArt", "Sky", "starmap_2020_8k.exr")
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", src)
    task.set_editor_property("destination_path", SKY_DIR)
    task.set_editor_property("destination_name", TEX_NAME)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", False)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    tex = unreal.load_asset(SKY_DIR + "/" + TEX_NAME)
    tex.set_editor_property("srgb", False)
    tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_HDR_COMPRESSED)
    tex.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_SKYBOX)
    tex.set_editor_property("address_x", unreal.TextureAddress.TA_WRAP)
    tex.set_editor_property("address_y", unreal.TextureAddress.TA_CLAMP)
    EAL.save_loaded_asset(tex)
    log("texture %s %dx%d" % (tex.get_path_name(), tex.blueprint_get_size_x(), tex.blueprint_get_size_y()))
    return tex


def custom(mat, x, y, code, out_type, inputs):
    node = MEL.create_material_expression(mat, unreal.MaterialExpressionCustom, x, y)
    node.set_editor_property("code", code)
    node.set_editor_property("output_type", out_type)
    ins = []
    for name in inputs:
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", name)
        ins.append(ci)
    node.set_editor_property("inputs", ins)
    return node


def vector_param(mat, name, x, y, value):
    node = MEL.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, x, y)
    node.set_editor_property("parameter_name", name)
    node.set_editor_property("default_value", unreal.LinearColor(*value))
    return node


def scalar_param(mat, name, x, y, value):
    node = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, x, y)
    node.set_editor_property("parameter_name", name)
    node.set_editor_property("default_value", value)
    return node


def build_material(tex, star_scale):
    path = SKY_DIR + "/" + MAT_NAME
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(MAT_NAME, SKY_DIR, unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property("two_sided", True)
    mat.set_editor_property("is_sky", True)

    cam = MEL.create_material_expression(mat, unreal.MaterialExpressionCameraVectorWS, -1400, 0)
    a0 = vector_param(mat, "AxisRA0", -1400, 150, (1, 0, 0, 0))
    a18 = vector_param(mat, "AxisRA18", -1400, 300, (0, 1, 0, 0))
    pole = vector_param(mat, "AxisPole", -1400, 450, (0, 0, 1, 0))

    uv = custom(mat, -1000, 150, UV_CODE, unreal.CustomMaterialOutputType.CMOT_FLOAT2, ["D", "A0", "A18", "P"])
    MEL.connect_material_expressions(cam, "", uv, "D")
    MEL.connect_material_expressions(a0, "", uv, "A0")
    MEL.connect_material_expressions(a18, "", uv, "A18")
    MEL.connect_material_expressions(pole, "", uv, "P")

    sample = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -700, 150)
    sample.set_editor_property("texture", tex)
    sample.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    sample.set_editor_property("mip_value_mode", unreal.TextureMipValueMode.TMVM_MIP_LEVEL)
    sample.set_editor_property("const_mip_value", 0)
    MEL.connect_material_expressions(uv, "", sample, "UVs")

    scale = scalar_param(mat, "StarLuminanceScale", -700, 400, star_scale)
    glow = scalar_param(mat, "AirglowZenithLuminance", -700, 500, AIRGLOW_ZENITH_CDM2)
    ext = scalar_param(mat, "ExtinctionMagPerAirmass", -700, 600, EXTINCTION_MAG_PER_AIRMASS)

    night = custom(mat, -350, 250, NIGHT_CODE, unreal.CustomMaterialOutputType.CMOT_FLOAT3, ["D", "Stars", "StarScale", "Airglow", "ExtMag", "Twilight", "SunDir"])
    MEL.connect_material_expressions(cam, "", night, "D")
    MEL.connect_material_expressions(sample, "RGB", night, "Stars")
    MEL.connect_material_expressions(scale, "", night, "StarScale")
    MEL.connect_material_expressions(glow, "", night, "Airglow")
    MEL.connect_material_expressions(ext, "", night, "ExtMag")
    twilight = scalar_param(mat, "TwilightZenithLuminance", -700, 700, 0.0)
    sun_dir = vector_param(mat, "SunHorizontalDir", -700, 800, (1, 0, 0, 0))
    MEL.connect_material_expressions(twilight, "", night, "Twilight")
    MEL.connect_material_expressions(sun_dir, "", night, "SunDir")

    view_lum = MEL.create_material_expression(mat, unreal.MaterialExpressionSkyAtmosphereViewLuminance, -350, -100)
    disk_sun = MEL.create_material_expression(mat, unreal.MaterialExpressionSkyAtmosphereLightDiskLuminance, -350, 0)
    disk_sun.set_editor_property("light_index", 0)
    disk_moon = MEL.create_material_expression(mat, unreal.MaterialExpressionSkyAtmosphereLightDiskLuminance, -350, 100)
    disk_moon.set_editor_property("light_index", 1)

    add1 = MEL.create_material_expression(mat, unreal.MaterialExpressionAdd, -100, 0)
    MEL.connect_material_expressions(view_lum, "", add1, "A")
    MEL.connect_material_expressions(night, "", add1, "B")
    add2 = MEL.create_material_expression(mat, unreal.MaterialExpressionAdd, 50, 0)
    MEL.connect_material_expressions(add1, "", add2, "A")
    MEL.connect_material_expressions(disk_sun, "", add2, "B")
    add3 = MEL.create_material_expression(mat, unreal.MaterialExpressionAdd, 200, 0)
    MEL.connect_material_expressions(add2, "", add3, "A")
    MEL.connect_material_expressions(disk_moon, "", add3, "B")
    MEL.connect_material_property(add3, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    MEL.recompile_material(mat)
    EAL.save_loaded_asset(mat)
    log("material %s nodes=%d" % (mat.get_path_name(), MEL.get_num_material_expressions(mat)))
    return mat


def main():
    project_dir = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
    out_dir = os.path.join(project_dir, "Saved", "Automation", "WK-M02-006")
    os.makedirs(out_dir, exist_ok=True)

    tex = import_star_map(project_dir)
    mean = unreal.GenesisSkyLibrary.measure_equirect_mean_luminance(tex)
    if mean <= 0:
        raise RuntimeError("star map mean luminance could not be measured")
    star_scale = INTEGRATED_STARLIGHT_CDM2 / mean
    log("starmap mean=%.6g -> scale=%.6g (target %.3g cd/m2)" % (mean, star_scale, INTEGRATED_STARLIGHT_CDM2))
    build_material(tex, star_scale)

    with open(os.path.join(out_dir, "sky_calibration.json"), "w", encoding="utf-8") as f:
        json.dump({
            "starmap_mean_raw": mean,
            "star_luminance_scale": star_scale,
            "integrated_starlight_cd_m2": INTEGRATED_STARLIGHT_CDM2,
            "airglow_zenith_cd_m2": AIRGLOW_ZENITH_CDM2,
            "extinction_mag_per_airmass": EXTINCTION_MAG_PER_AIRMASS,
            "source": "Leinert et al. 1998, A&AS 127, 1",
        }, f, indent=2)
    log("done")


main()
