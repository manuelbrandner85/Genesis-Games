"""G3 tech smoke asset: EUR pallet (EN 13698-1 outer dimensions 1200 x 800 x 144 mm).

Run inside Blender (background):
    blender -b --factory-startup --python tools/v4/g3/build_pallet.py -- --out <DIR> [--bake 4096]

Builds the master mesh with real dimensions, bevels, nail heads and a procedural used-spruce
material, unwraps UVs, bakes BaseColor / Roughness / Metallic / Normal for Unreal, saves the
.blend master and exports the FBX. Neutral technical asset, no GENESIS canon content.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np

ASSET = "SM_TechSmoke_PalletEUR"
MM = 0.001

# --- Dimensions in mm (X = 1200 length, Y = 800 width, Z up, origin bottom centre) -------------
L, W, H = 1200.0, 800.0, 144.0
T_BOARD = 22.0          # deck and stringer board thickness
H_BLOCK = 78.0          # block height
X_ROWS = (-527.5, 0.0, 527.5)                       # stringer / block centre lines (145 wide)
TOP_BOARDS = ((-327.5, 145.0), (-163.75, 100.0), (0.0, 145.0), (163.75, 100.0), (327.5, 145.0))
BOTTOM_BOARDS = ((-350.0, 100.0), (0.0, 145.0), (350.0, 100.0))
BLOCK_ROWS_Y = ((-350.0, 100.0), (0.0, 145.0), (350.0, 100.0))
BEVEL = 1.5             # mm, sawn and handled softwood edges
NAIL_D, NAIL_PROUD = 7.0, 0.3   # nail head diameter, height above the deck surface


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--bake", type=int, default=4096)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return ap.parse_args(argv)


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.unit_settings.system = "METRIC"
    s.unit_settings.scale_length = 1.0
    s.unit_settings.length_unit = "METERS"
    return s


RNG = np.random.default_rng(13698)


def box(name, cx, cy, z0, sx, sy, sz, grain_axis, rnd, bevel=BEVEL, is_nail=0.0, jitter=True):
    """Box in mm with bevel baked in; tagged with face attributes for the material.

    Hand-built pallets are not CAD-exact: each part gets a small width deviation, offset and
    twist about Z (all inside the EN 13698-1 tolerance of +-3 mm on length and width).
    Heights stay nominal so the deck stays flat and the measured height is exact.
    """
    across = sy if grain_axis == 0.0 else sx
    d_w = float(np.clip(RNG.normal(0, 0.4), -0.6, 0.6)) if jitter else 0.0
    off = RNG.normal(0, 0.5, 2).clip(-0.8, 0.8) if jitter else (0.0, 0.0)
    twist = math.radians(float(np.clip(RNG.normal(0, 0.05), -0.08, 0.08))) if jitter else 0.0
    if grain_axis == 0.0:
        sy += d_w
    else:
        sx += d_w
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    c, s = math.cos(twist), math.sin(twist)
    for v in bm.verts:
        x, y = v.co.x * sx, v.co.y * sy
        v.co.x = (cx + off[0] + x * c - y * s) * MM
        v.co.y = (cy + off[1] + x * s + y * c) * MM
        v.co.z = (z0 + (v.co.z + 0.5) * sz) * MM
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if bevel > 0:
        mod = ob.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel * MM
        mod.segments = 3
        mod.limit_method = "NONE"
        mod.harden_normals = True
        bake_modifiers(ob)
    tag(ob, grain_axis, rnd, is_nail)
    # Grain space (length on X): pith of the log 4-20 cm beside/below the board centre, and a
    # slight fibre slope along the length, which together give the arched (cathedral) figure.
    centre_across = cy if grain_axis == 0.0 else cx
    side = RNG.choice((-1.0, 1.0))
    pith = (RNG.uniform(-5, 5), (centre_across + side * RNG.uniform(10, 60)) * MM, (z0 + sz * 0.5 + RNG.choice((-1, 1)) * RNG.uniform(40, 200)) * MM)
    tilt = (0.0, RNG.normal(0, 0.025), RNG.normal(0, 0.025))
    for name_, value in (("pith", pith), ("tilt", tilt)):
        attr = ob.data.attributes.new(name_, "FLOAT_VECTOR", "FACE")
        attr.data.foreach_set("vector", list(value) * len(ob.data.polygons))
    return ob


def cylinder(name, cx, cy, z0, d, h, rnd):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=16, radius1=d * 0.5 * MM, radius2=d * 0.5 * MM, depth=h * MM)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(cx * MM, cy * MM, (z0 + h * 0.5) * MM))
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = abs(p.normal.z) < 0.5
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    tag(ob, 0.0, rnd, 1.0)
    for name_ in ("pith", "tilt"):
        attr = me.attributes.new(name_, "FLOAT_VECTOR", "FACE")
        attr.data.foreach_set("vector", [0.0, 0.0, 0.0] * len(me.polygons))
    return ob


def bake_modifiers(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    new = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    old = ob.data
    ob.modifiers.clear()
    ob.data = new
    bpy.data.meshes.remove(old)


def tag(ob, grain_axis, rnd, is_nail):
    me = ob.data
    for name, value in (("grain_axis", grain_axis), ("part_rand", rnd), ("is_nail", is_nail)):
        attr = me.attributes.new(name, "FLOAT", "FACE")
        attr.data.foreach_set("value", [value] * len(me.polygons))


def build_geometry():
    rng = RNG
    parts = []
    z_top = H - T_BOARD
    z_str = z_top - T_BOARD
    z_blk = z_str - H_BLOCK
    for i, (y, w) in enumerate(TOP_BOARDS):
        parts.append(box(f"top_{i}", 0, y, z_top, L, w, T_BOARD, 0.0, rng.random()))
    for i, x in enumerate(X_ROWS):
        parts.append(box(f"stringer_{i}", x, 0, z_str, 145.0, W, T_BOARD, 1.0, rng.random()))
        for j, (y, w) in enumerate(BLOCK_ROWS_Y):
            parts.append(box(f"block_{i}{j}", x, y, z_blk, 145.0, w, H_BLOCK, 0.0, rng.random(), bevel=2.5))
    for i, (y, w) in enumerate(BOTTOM_BOARDS):
        parts.append(box(f"bottom_{i}", 0, y, 0.0, L, w, T_BOARD, 0.0, rng.random()))
    # Nail heads on the top deck: two per board/stringer crossing, slightly staggered.
    for bi, (y, w) in enumerate(TOP_BOARDS):
        for x in X_ROWS:
            for k, (dx, dy) in enumerate(((-38.0, -0.22 * w), (38.0, 0.22 * w))):
                jitter = rng.normal(0, 1.5, 2)
                parts.append(cylinder(f"nail_{bi}_{x}_{k}", x + dx + jitter[0], y + dy + jitter[1], H - 0.2, NAIL_D, 0.2 + NAIL_PROUD, rng.random()))
    with bpy.context.temp_override(active_object=parts[0], selected_editable_objects=parts, object=parts[0]):
        bpy.ops.object.join()
    ob = parts[0]
    ob.name = ob.data.name = ASSET
    # Origin = bottom centre of the actual (slightly irregular) footprint.
    co = np.empty(len(ob.data.vertices) * 3)
    ob.data.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    co[:, :2] -= (co[:, :2].max(0) + co[:, :2].min(0)) / 2
    ob.data.vertices.foreach_set("co", co.ravel())
    ob.data.update()
    return ob


def unwrap(ob):
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.0015, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.pack_islands(rotate=True, margin=0.0015)
    bpy.ops.object.mode_set(mode="OBJECT")
    ob.data.uv_layers[0].name = "UVMap"


# --- Material -----------------------------------------------------------------------------------
def node(nt, kind, loc, **props):
    n = nt.nodes.new(kind)
    n.location = loc
    for k, v in props.items():
        setattr(n, k, v)
    return n


def build_material():
    mat = bpy.data.materials.new("M_TechSmoke_PalletWood")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    ln = nt.links.new
    out = node(nt, "ShaderNodeOutputMaterial", (1600, 0))
    bsdf = node(nt, "ShaderNodeBsdfPrincipled", (1300, 0))
    bsdf.inputs["IOR"].default_value = 1.5
    ln(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tex = node(nt, "ShaderNodeTexCoord", (-1800, 0))
    sep = node(nt, "ShaderNodeSeparateXYZ", (-1600, 0))
    ln(tex.outputs["Object"], sep.inputs[0])
    attr = {n: node(nt, "ShaderNodeAttribute", (-1800, -300 - 150 * i), attribute_name=n, attribute_type="GEOMETRY")
            for i, n in enumerate(("grain_axis", "part_rand", "is_nail"))}

    # Grain space: board length always on X; each part gets its own offset so boards differ.
    swapped = node(nt, "ShaderNodeCombineXYZ", (-1400, 100))
    ln(sep.outputs["Y"], swapped.inputs["X"]); ln(sep.outputs["X"], swapped.inputs["Y"]); ln(sep.outputs["Z"], swapped.inputs["Z"])
    gsel = node(nt, "ShaderNodeMix", (-1200, 0), data_type="VECTOR")
    ln(attr["grain_axis"].outputs["Fac"], gsel.inputs["Factor"])
    ln(tex.outputs["Object"], gsel.inputs["A"]); ln(swapped.outputs["Vector"], gsel.inputs["B"])
    # Grain space relative to the log's pith, with fibre slope: p' = p - pith + x * tilt.
    pith = node(nt, "ShaderNodeAttribute", (-1400, -300), attribute_name="pith", attribute_type="GEOMETRY")
    tilt = node(nt, "ShaderNodeAttribute", (-1400, -450), attribute_name="tilt", attribute_type="GEOMETRY")
    rel = node(nt, "ShaderNodeVectorMath", (-1100, 0), operation="SUBTRACT")
    ln(gsel.outputs["Result"], rel.inputs[0]); ln(pith.outputs["Vector"], rel.inputs[1])
    gsep = node(nt, "ShaderNodeSeparateXYZ", (-1100, -250))
    ln(gsel.outputs["Result"], gsep.inputs[0])
    slope = node(nt, "ShaderNodeVectorMath", (-950, -250), operation="SCALE")
    ln(tilt.outputs["Vector"], slope.inputs[0]); ln(gsep.outputs["X"], slope.inputs["Scale"])
    gpos = node(nt, "ShaderNodeVectorMath", (-850, 0), operation="ADD")
    ln(rel.outputs["Vector"], gpos.inputs[0]); ln(slope.outputs["Vector"], gpos.inputs[1])

    # Medium: annual rings of spruce about 4-5 mm apart around the pith; where the sawn face
    # cuts them at a shallow angle they open into arches. Distortion is stretched along the
    # length so it wanders slowly, as in sawn timber.
    ring_noise_v = node(nt, "ShaderNodeVectorMath", (-700, 450), operation="MULTIPLY")
    ring_noise_v.inputs[1].default_value = (0.6, 4.0, 4.0)
    ln(gpos.outputs["Vector"], ring_noise_v.inputs[0])
    ring_noise = node(nt, "ShaderNodeTexNoise", (-550, 450))
    ring_noise.inputs["Scale"].default_value = 1.5
    ring_noise.inputs["Detail"].default_value = 2.0
    ln(ring_noise_v.outputs["Vector"], ring_noise.inputs["Vector"])
    warp = node(nt, "ShaderNodeVectorMath", (-400, 450), operation="MULTIPLY_ADD")
    warp.inputs[1].default_value = (0.0, 0.006, 0.006)
    ln(ring_noise.outputs["Color"], warp.inputs[0]); ln(gpos.outputs["Vector"], warp.inputs[2])
    rings = node(nt, "ShaderNodeTexWave", (-800, 200), wave_type="RINGS", rings_direction="X")
    rings.inputs["Scale"].default_value = 70.0
    rings.inputs["Distortion"].default_value = 0.0
    ln(warp.outputs["Vector"], rings.inputs["Vector"])
    ring_sharp = node(nt, "ShaderNodeMapRange", (-600, 200), interpolation_type="SMOOTHSTEP")
    ring_sharp.inputs["From Min"].default_value = 0.35
    ring_sharp.inputs["From Max"].default_value = 0.85
    ln(rings.outputs["Fac"], ring_sharp.inputs["Value"])

    # Micro: fibres stretched along the grain.
    fib_vec = node(nt, "ShaderNodeVectorMath", (-800, -50), operation="MULTIPLY")
    fib_vec.inputs[1].default_value = (3.0, 90.0, 90.0)
    ln(gpos.outputs["Vector"], fib_vec.inputs[0])
    fibres = node(nt, "ShaderNodeTexNoise", (-600, -50))
    fibres.inputs["Scale"].default_value = 4.0
    fibres.inputs["Detail"].default_value = 6.0
    fibres.inputs["Roughness"].default_value = 0.6
    ln(fib_vec.outputs["Vector"], fibres.inputs["Vector"])

    # Wood colour: early/late wood of spruce, per-part tone shift.
    wood = node(nt, "ShaderNodeMix", (-300, 250), data_type="RGBA")
    wood.inputs["A"].default_value = (0.43, 0.32, 0.20, 1)   # early wood, linear
    wood.inputs["B"].default_value = (0.33, 0.235, 0.135, 1)  # late wood, low contrast as in spruce
    ln(ring_sharp.outputs["Result"], wood.inputs["Factor"])
    fibre_tone = node(nt, "ShaderNodeMix", (-100, 250), data_type="RGBA", blend_type="MULTIPLY")
    fibre_tone.inputs["Factor"].default_value = 0.18
    ln(wood.outputs["Result"], fibre_tone.inputs["A"]); ln(fibres.outputs["Color"], fibre_tone.inputs["B"])
    part_tone = node(nt, "ShaderNodeHueSaturation", (100, 250))
    pr_hue = node(nt, "ShaderNodeMapRange", (-100, 450))
    pr_hue.inputs["To Min"].default_value = 0.485
    pr_hue.inputs["To Max"].default_value = 0.515
    ln(attr["part_rand"].outputs["Fac"], pr_hue.inputs["Value"])
    pr_val = node(nt, "ShaderNodeMapRange", (-100, 600))
    pr_val.inputs["To Min"].default_value = 0.85
    pr_val.inputs["To Max"].default_value = 1.12
    ln(attr["part_rand"].outputs["Fac"], pr_val.inputs["Value"])
    ln(pr_hue.outputs["Result"], part_tone.inputs["Hue"]); ln(pr_val.outputs["Result"], part_tone.inputs["Value"])
    ln(fibre_tone.outputs["Result"], part_tone.inputs["Color"])

    # Macro weathering: UV-greyed softwood, patchy, stronger on some boards.
    weather_n = node(nt, "ShaderNodeTexNoise", (-300, -350))
    weather_n.inputs["Scale"].default_value = 2.2
    weather_n.inputs["Detail"].default_value = 4.0
    ln(gpos.outputs["Vector"], weather_n.inputs["Vector"])
    weather = node(nt, "ShaderNodeMapRange", (-100, -350))
    weather.inputs["From Min"].default_value = 0.35
    weather.inputs["From Max"].default_value = 0.75
    weather.inputs["To Min"].default_value = 0.08
    weather.inputs["To Max"].default_value = 0.42
    ln(weather_n.outputs["Fac"], weather.inputs["Value"])
    # Boards of a used pallet differ in age (repairs): some greyed far more than others.
    age = node(nt, "ShaderNodeMath", (100, -450), operation="MULTIPLY_ADD", use_clamp=True)
    ln(attr["part_rand"].outputs["Fac"], age.inputs[0])
    age.inputs[1].default_value = 0.35
    ln(weather.outputs["Result"], age.inputs[2])

    # Medium: knots - small dark ovals, stretched along the grain, sparse.
    knot_v = node(nt, "ShaderNodeVectorMath", (-700, 700), operation="MULTIPLY")
    knot_v.inputs[1].default_value = (5.0, 24.0, 24.0)
    ln(gpos.outputs["Vector"], knot_v.inputs[0])
    vor = node(nt, "ShaderNodeTexVoronoi", (-550, 700))
    vor.inputs["Scale"].default_value = 1.0
    ln(knot_v.outputs["Vector"], vor.inputs["Vector"])
    knot_core = node(nt, "ShaderNodeMapRange", (-350, 700), interpolation_type="SMOOTHSTEP")
    knot_core.inputs["From Min"].default_value = 0.16
    knot_core.inputs["From Max"].default_value = 0.08
    ln(vor.outputs["Distance"], knot_core.inputs["Value"])
    knot_pick = node(nt, "ShaderNodeSeparateColor", (-350, 850))
    ln(vor.outputs["Color"], knot_pick.inputs[0])
    knot_sel = node(nt, "ShaderNodeMath", (-200, 850), operation="GREATER_THAN")
    knot_sel.inputs[1].default_value = 0.88
    ln(knot_pick.outputs["Red"], knot_sel.inputs[0])
    knot = node(nt, "ShaderNodeMath", (-50, 750), operation="MULTIPLY")
    ln(knot_core.outputs["Result"], knot.inputs[0]); ln(knot_sel.outputs["Value"], knot.inputs[1])
    knot_mix = node(nt, "ShaderNodeMix", (200, 400), data_type="RGBA")
    knot_mix.inputs["B"].default_value = (0.13, 0.065, 0.03, 1)
    ln(knot.outputs["Value"], knot_mix.inputs["Factor"]); ln(part_tone.outputs["Color"], knot_mix.inputs["A"])

    grey = node(nt, "ShaderNodeMix", (300, 250), data_type="RGBA")
    grey.inputs["B"].default_value = (0.25, 0.24, 0.225, 1)
    ln(age.outputs["Value"], grey.inputs["Factor"])
    ln(knot_mix.outputs["Result"], grey.inputs["A"])

    # Medium: ground dirt rising from the bottom deck, plus scattered stains.
    zfade = node(nt, "ShaderNodeMapRange", (-100, -600))
    zfade.inputs["From Min"].default_value = 0.0
    zfade.inputs["From Max"].default_value = 0.11
    zfade.inputs["To Min"].default_value = 0.55
    zfade.inputs["To Max"].default_value = 0.0
    ln(sep.outputs["Z"], zfade.inputs["Value"])
    stain_n = node(nt, "ShaderNodeTexNoise", (-300, -800))
    stain_n.inputs["Scale"].default_value = 9.0
    stain_n.inputs["Detail"].default_value = 3.0
    ln(tex.outputs["Object"], stain_n.inputs["Vector"])
    stain = node(nt, "ShaderNodeMapRange", (-100, -800), interpolation_type="SMOOTHSTEP")
    stain.inputs["From Min"].default_value = 0.56
    stain.inputs["From Max"].default_value = 0.70
    stain.inputs["To Max"].default_value = 0.4
    ln(stain_n.outputs["Fac"], stain.inputs["Value"])
    dirt_amt = node(nt, "ShaderNodeMath", (100, -650), operation="ADD", use_clamp=True)
    ln(zfade.outputs["Result"], dirt_amt.inputs[0]); ln(stain.outputs["Result"], dirt_amt.inputs[1])
    dirt = node(nt, "ShaderNodeMix", (500, 250), data_type="RGBA")
    dirt.inputs["B"].default_value = (0.085, 0.068, 0.05, 1)
    ln(dirt_amt.outputs["Value"], dirt.inputs["Factor"]); ln(grey.outputs["Result"], dirt.inputs["A"])

    # Nails: plain steel with light rust.
    rust_n = node(nt, "ShaderNodeTexNoise", (300, -1000))
    rust_n.inputs["Scale"].default_value = 900.0
    rust_n.inputs["Detail"].default_value = 2.0
    ln(tex.outputs["Object"], rust_n.inputs["Vector"])
    rust = node(nt, "ShaderNodeMapRange", (500, -1000))
    rust.inputs["From Min"].default_value = 0.45
    rust.inputs["From Max"].default_value = 0.65
    ln(rust_n.outputs["Fac"], rust.inputs["Value"])
    steel = node(nt, "ShaderNodeMix", (700, -800), data_type="RGBA")
    steel.inputs["A"].default_value = (0.56, 0.57, 0.58, 1)
    steel.inputs["B"].default_value = (0.20, 0.085, 0.035, 1)
    ln(rust.outputs["Result"], steel.inputs["Factor"])
    base = node(nt, "ShaderNodeMix", (900, 250), data_type="RGBA")
    ln(attr["is_nail"].outputs["Fac"], base.inputs["Factor"])
    ln(dirt.outputs["Result"], base.inputs["A"]); ln(steel.outputs["Result"], base.inputs["B"])
    ln(base.outputs["Result"], bsdf.inputs["Base Color"])

    not_rust = node(nt, "ShaderNodeMath", (700, -1100), operation="SUBTRACT")
    not_rust.inputs[0].default_value = 1.0
    ln(rust.outputs["Result"], not_rust.inputs[1])
    metallic = node(nt, "ShaderNodeMath", (900, -1100), operation="MULTIPLY")
    ln(attr["is_nail"].outputs["Fac"], metallic.inputs[0]); ln(not_rust.outputs["Value"], metallic.inputs[1])
    ln(metallic.outputs["Value"], bsdf.inputs["Metallic"])

    # Roughness: raw softwood 0.62-0.85, matter where weathered/dirty, nails 0.45 (rust 0.85).
    rough_w = node(nt, "ShaderNodeMapRange", (500, -300))
    rough_w.inputs["From Min"].default_value = 0.38
    rough_w.inputs["From Max"].default_value = 0.62
    rough_w.inputs["To Min"].default_value = 0.56
    rough_w.inputs["To Max"].default_value = 0.80
    ln(fibres.outputs["Fac"], rough_w.inputs["Value"])
    rough_d = node(nt, "ShaderNodeMath", (700, -300), operation="MULTIPLY_ADD", use_clamp=True)
    ln(weather.outputs["Result"], rough_d.inputs[0])
    rough_d.inputs[1].default_value = 0.15
    ln(rough_w.outputs["Result"], rough_d.inputs[2])
    rough_n = node(nt, "ShaderNodeMix", (700, -500), data_type="FLOAT")
    rough_n.inputs["A"].default_value = 0.45
    rough_n.inputs["B"].default_value = 0.85
    ln(rust.outputs["Result"], rough_n.inputs["Factor"])
    rough = node(nt, "ShaderNodeMix", (900, -300), data_type="FLOAT")
    ln(attr["is_nail"].outputs["Fac"], rough.inputs["Factor"])
    ln(rough_d.outputs["Value"], rough.inputs["A"]); ln(rough_n.outputs["Result"], rough.inputs["B"])
    ln(rough.outputs["Result"], bsdf.inputs["Roughness"])

    # Surface relief: fibres + ring edges (sawn softwood), nothing on the nails.
    height = node(nt, "ShaderNodeMath", (700, -1300), operation="MULTIPLY_ADD")
    ln(fibres.outputs["Fac"], height.inputs[0])
    height.inputs[1].default_value = 0.7
    ln(ring_sharp.outputs["Result"], height.inputs[2])
    bump_amt = node(nt, "ShaderNodeMath", (900, -1500), operation="SUBTRACT")
    bump_amt.inputs[0].default_value = 0.35
    ln(attr["is_nail"].outputs["Fac"], bump_amt.inputs[1])
    bump = node(nt, "ShaderNodeBump", (1100, -1300))
    bump.inputs["Distance"].default_value = 0.0004
    ln(bump_amt.outputs["Value"], bump.inputs["Strength"])
    ln(height.outputs["Value"], bump.inputs["Height"])
    ln(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat, metallic


# --- Bake --------------------------------------------------------------------------------------
def enable_gpu(scene):
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for kind in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = kind
            prefs.get_devices()
            gpus = [d for d in prefs.devices if d.type == kind]
            if gpus:
                for d in prefs.devices:
                    d.use = d.type == kind
                scene.cycles.device = "GPU"
                return kind, [d.name for d in gpus]
        except TypeError:
            continue
    scene.cycles.device = "CPU"
    return "CPU", []


def bake_maps(scene, ob, mat, metallic_node, size, tex_dir):
    nt = mat.node_tree
    target = nt.nodes.new("ShaderNodeTexImage")
    target.location = (1600, -600)
    nt.nodes.active = target
    scene.cycles.samples = 16
    scene.render.bake.margin = 16
    scene.render.bake.margin_type = "EXTEND"
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    out = {}

    def run(name, kind, non_color, **kw):
        img = bpy.data.images.new(f"T_{ASSET}_{name}", size, size, alpha=False, float_buffer=False, is_data=non_color)
        img.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
        target.image = img
        bpy.ops.object.bake(type=kind, use_clear=True, **kw)
        out[name] = img

    run("BC", "DIFFUSE", False, pass_filter={"COLOR"})
    run("R", "ROUGHNESS", True)
    run("N_GL", "NORMAL", True, normal_space="TANGENT")
    # Metallic via a temporary emission route.
    surface = nt.nodes["Material Output"].inputs["Surface"]
    old = surface.links[0].from_socket
    emit = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(metallic_node.outputs["Value"], emit.inputs["Color"])
    nt.links.new(emit.outputs["Emission"], surface)
    run("M", "EMIT", True)
    nt.links.new(old, surface)
    nt.nodes.remove(emit)
    nt.nodes.remove(target)

    def px(img):
        a = np.empty(size * size * 4, dtype=np.float32)
        img.pixels.foreach_get(a)
        return a.reshape(size, size, 4)

    def save(arr, name, non_color):
        img = bpy.data.images.new(name, size, size, alpha=False, is_data=non_color)
        img.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
        img.pixels.foreach_set(arr.ravel())
        path = tex_dir / f"{name}.png"
        img.filepath_raw = str(path)
        img.file_format = "PNG"
        img.save()
        return path

    files = {}
    files["BC"] = save(px(out["BC"]), f"T_{ASSET}_BC", False)
    rgh, met = px(out["R"]), px(out["M"])
    covered = uv_coverage(ob, size)
    orm = np.ones_like(rgh)
    orm[..., 1] = rgh[..., 0]
    orm[..., 2] = met[..., 0]
    files["ORM"] = save(orm, f"T_{ASSET}_ORM", True)
    n = px(out["N_GL"])
    n[..., 1] = 1.0 - n[..., 1]          # OpenGL -> DirectX (Unreal) green channel
    files["N"] = save(n, f"T_{ASSET}_N", True)
    bc = px(bpy.data.images[f"T_{ASSET}_BC"])[..., :3][covered]
    r = rgh[..., 0][covered]
    stats = {
        "uv_coverage": round(float(covered.mean()), 4),
        "basecolor_srgb8_p5_mean_p95": [np.percentile(bc.mean(1), 5).round(3) * 255, bc.mean(1).mean().round(3) * 255, np.percentile(bc.mean(1), 95).round(3) * 255],
        "roughness_p5_mean_p95": [round(float(np.percentile(r, 5)), 3), round(float(r.mean()), 3), round(float(np.percentile(r, 95)), 3)],
        "metallic_texel_share": round(float((met[..., 0][covered] > 0.5).mean()), 5),
    }
    stats = {k: ([round(float(x), 2) for x in v] if isinstance(v, list) else v) for k, v in stats.items()}
    return files, stats


def uv_coverage(ob, size):
    """Boolean mask of texels covered by UV triangles (rasterised in numpy)."""
    me = ob.data
    me.calc_loop_triangles()
    uv = np.empty(len(me.loops) * 2, dtype=np.float32)
    me.uv_layers[0].data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2) * size
    tris = np.empty(len(me.loop_triangles) * 3, dtype=np.int32)
    me.loop_triangles.foreach_get("loops", tris)
    mask = np.zeros((size, size), dtype=bool)
    for a, b, c in uv[tris.reshape(-1, 3)]:
        x0, y0 = np.floor(np.minimum(np.minimum(a, b), c)).astype(int).clip(0, size - 1)
        x1, y1 = np.ceil(np.maximum(np.maximum(a, b), c)).astype(int).clip(0, size - 1)
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(d) < 1e-12:
            continue
        l1 = ((b[1] - c[1]) * (xs - c[0]) + (c[0] - b[0]) * (ys - c[1])) / d
        l2 = ((c[1] - a[1]) * (xs - c[0]) + (a[0] - c[0]) * (ys - c[1])) / d
        inside = (l1 >= 0) & (l2 >= 0) & (l1 + l2 <= 1)
        mask[y0:y1 + 1, x0:x1 + 1] |= inside
    return mask


def main():
    args = parse_args()
    out = args.out.resolve()
    tex_dir = out / "Textures"
    exp_dir = out / "Export"
    for d in (out, tex_dir, exp_dir):
        d.mkdir(parents=True, exist_ok=True)
    scene = reset_scene()
    ob = build_geometry()
    unwrap(ob)
    mat, metallic_node = build_material()
    ob.data.materials.append(mat)
    device, gpus = enable_gpu(scene)
    files, stats = bake_maps(scene, ob, mat, metallic_node, args.bake, tex_dir)

    blend = out / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
    fbx = exp_dir / f"{ASSET}.fbx"
    for o in bpy.context.view_layer.objects:
        o.select_set(o == ob)
    bpy.ops.export_scene.fbx(filepath=str(fbx), use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
                             mesh_smooth_type="FACE", use_tspace=True, use_custom_props=False, add_leaf_bones=False,
                             object_types={"MESH"}, path_mode="STRIP", bake_anim=False)

    dims = [round(v / MM, 2) for v in ob.dimensions]
    report = {
        "asset_id": ASSET, "blender": bpy.app.version_string, "device": device, "gpus": gpus,
        "dimensions_mm_xyz": dims, "origin": "bottom centre (0,0,0)",
        "verts": len(ob.data.vertices), "faces": len(ob.data.polygons), "uv_layers": [u.name for u in ob.data.uv_layers],
        "bake_size": args.bake, "texture_stats": stats,
        "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [blend, fbx, *files.values()]},
    }
    (out / "build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("G3_BUILD_REPORT " + json.dumps(report))


if __name__ == "__main__":
    main()
