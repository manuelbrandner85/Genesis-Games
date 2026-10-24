"""G7: bake the procedural Blender materials of one asset into Unreal textures (headless).

    blender -b ArtSource/Blender/G7/R03_Werkstatt_G7.blend -P tools/v4/g7/bake_g7.py -- ASSET SIZE OUTDIR

Every material slot of the asset bakes into one shared texture set (the UVs are one non-overlapping
layout): T_<ASSET>_BC (sRGB), T_<ASSET>_ORM (AO, roughness, metallic; linear), T_<ASSET>_N (DirectX
green). Writes bake_report.json with coverage and value ranges; fails on empty maps.
"""
import bpy, json, sys, time
from pathlib import Path
import numpy as np

asset, size, out = sys.argv[sys.argv.index("--") + 1:][:3]
size = int(size)
out = Path(out)
out.mkdir(parents=True, exist_ok=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
prefs = bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type = "OPTIX"
prefs.get_devices()
for d in prefs.devices:
    d.use = d.type == "OPTIX"
sc.cycles.device = "GPU"
sc.cycles.samples = 64
sc.render.bake.margin = 16
sc.render.bake.margin_type = "EXTEND"

ob = sc.objects[asset]
for o in sc.objects:
    o.select_set(False)
ob.hide_set(False)
ob.hide_render = False
ob.select_set(True)
bpy.context.view_layer.objects.active = ob
mats = [m for m in ob.data.materials if m]

targets = {}
for m in mats:
    nt = m.node_tree
    t = nt.nodes.new("ShaderNodeTexImage")
    for n in nt.nodes:
        n.select = False
    t.select = True
    nt.nodes.active = t
    targets[m.name] = t


def bake(name, kind, non_color, **kw):
    img = bpy.data.images.new(f"T_{asset}_{name}", size, size, alpha=True, float_buffer=False, is_data=non_color)
    img.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
    for t in targets.values():
        t.image = img
    t0 = time.time()
    bpy.ops.object.bake(type=kind, use_clear=True, **kw)
    print(f"BAKE {name} {time.time() - t0:.1f}s")
    a = np.empty(size * size * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    return a.reshape(size, size, 4)


def input_source(m, name):
    """Socket feeding a Principled input (or a Value/RGB node holding its default)."""
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    sock = bsdf.inputs[name]
    if sock.links:
        return sock.links[0].from_socket
    if sock.type == "RGBA":
        v = nt.nodes.new("ShaderNodeRGB")
        v.outputs[0].default_value = sock.default_value
    else:
        v = nt.nodes.new("ShaderNodeValue")
        v.outputs[0].default_value = sock.default_value
    return v.outputs[0]


def emit_bake(name, input_name, non_color):
    """Bake a BSDF input exactly (no lighting): route it through an emission shader.
    Needed for Base Color, because the DIFFUSE pass is black on metals."""
    restore = []
    for m in mats:
        nt = m.node_tree
        surf = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"]
        old = surf.links[0].from_socket
        em = nt.nodes.new("ShaderNodeEmission")
        nt.links.new(input_source(m, input_name), em.inputs["Color"])
        nt.links.new(em.outputs["Emission"], surf)
        restore.append((nt, old, surf, em))
    arr = bake(name, "EMIT", non_color)
    for nt, old, surf, em in restore:
        nt.links.new(old, surf)
        nt.nodes.remove(em)
    return arr


bc = emit_bake("BC", "Base Color", False)
rough = bake("R", "ROUGHNESS", True)
ao = bake("AO", "AO", True)
nrm = bake("N", "NORMAL", True, normal_space="TANGENT")
met = emit_bake("M", "Metallic", True)
for m in mats:
    m.node_tree.nodes.remove(targets[m.name])

covered = bc[..., 3] > 0.5 if bc[..., 3].min() < 0.5 else np.ones(bc.shape[:2], bool)


def save(arr, name, non_color):
    img = bpy.data.images.new(name + "_out", size, size, alpha=False, is_data=non_color)
    img.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
    a = arr.copy()
    a[..., 3] = 1.0
    img.pixels.foreach_set(a.ravel())
    p = out / f"{name}.png"
    img.filepath_raw = str(p)
    img.file_format = "PNG"
    img.save()
    return p.name


orm = np.ones_like(rough)
orm[..., 0] = np.clip(0.35 + 0.65 * ao[..., 0], 0, 1)      # keep baked AO subtle, Lumen adds its own
orm[..., 1] = rough[..., 0]
orm[..., 2] = met[..., 0]
nrm[..., 1] = 1.0 - nrm[..., 1]                             # OpenGL -> DirectX
files = [save(bc, f"T_{asset}_BC", False), save(orm, f"T_{asset}_ORM", True), save(nrm, f"T_{asset}_N", True)]
b = bc[..., :3][covered]
lum = b @ np.array([0.2126, 0.7152, 0.0722])
rep = {"asset": asset, "size": size, "files": files, "uv_coverage": round(float(covered.mean()), 4),
       "basecolor_srgb_lum_p5_mean_p95": [round(float(np.percentile(lum, q)) * 255, 1) for q in (5, 50, 95)],
       "roughness_p5_mean_p95": [round(float(np.percentile(rough[..., 0][covered], q)), 3) for q in (5, 50, 95)],
       "metallic_share_gt_0_5": round(float((met[..., 0][covered] > 0.5).mean()), 3),
       "materials": [m.name for m in mats]}
if lum.mean() < 0.01 or rough[..., 0][covered].mean() < 0.02:
    raise SystemExit("BAKE_EMPTY " + json.dumps(rep))
(out / "bake_report.json").write_text(json.dumps(rep, indent=2) + "\n", encoding="utf8")
print("BAKE_DONE", json.dumps(rep))
