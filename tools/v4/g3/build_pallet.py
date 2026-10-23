"""G3 tech smoke asset: used EUR pallet (EN 13698-1 outer dimensions 1200 x 800 x 144 mm).

Background:
    blender -b --factory-startup --python tools/v4/g3/build_pallet.py -- --out <DIR> [--bake 4096]
Visible session (step by step over MCP): import this file as a module and call
    reset_scene(), build_geometry(), unwrap(), build_material(), enable_gpu(), bake_maps(), save_and_export().

Builds the master mesh with real dimensions, bevels, varied nail heads, chipped edges, end
cracks, raised splinters and pressed-chip blocks; a procedural used-spruce material with wear
(fork scuffs, grime in joints, deck dust, darker end grain, fresh wood in breaks); unwraps UVs,
bakes BaseColor / ORM / Normal (DirectX) for Unreal, saves the .blend master and exports the
FBX. Neutral technical asset, no GENESIS canon content.
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
from mathutils import Euler, Matrix, Vector

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
NAIL_D = 7.0            # nominal nail head diameter

FLOAT_ATTRS = ("grain_axis", "part_rand", "is_nail", "is_chip", "fresh", "nail_rand")
VECTOR_ATTRS = ("pith", "tilt")

RNG = np.random.default_rng(13698)


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--bake", type=int, default=4096)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return ap.parse_args(argv)


def reset_scene():
    if bpy.app.background:
        bpy.ops.wm.read_factory_settings(use_empty=True)
    else:
        bpy.ops.wm.read_homefile(use_empty=True)
    s = bpy.context.scene
    s.unit_settings.system = "METRIC"
    s.unit_settings.scale_length = 1.0
    s.unit_settings.length_unit = "METERS"
    return s


# --- Attributes ----------------------------------------------------------------------------------
def set_attrs(me, values):
    """Write one value per face for every material attribute (missing ones default to 0)."""
    n = len(me.polygons)
    for name in FLOAT_ATTRS:
        attr = me.attributes.get(name) or me.attributes.new(name, "FLOAT", "FACE")
        attr.data.foreach_set("value", [float(values.get(name, 0.0))] * n)
    for name in VECTOR_ATTRS:
        attr = me.attributes.get(name) or me.attributes.new(name, "FLOAT_VECTOR", "FACE")
        attr.data.foreach_set("vector", list(values.get(name, (0.0, 0.0, 0.0))) * n)


def attrs_of(ob):
    me = ob.data
    return {**{n: me.attributes[n].data[0].value for n in FLOAT_ATTRS},
            **{n: tuple(me.attributes[n].data[0].vector) for n in VECTOR_ATTRS}}


def new_object(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def bake_modifiers(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    new = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    old = ob.data
    ob.modifiers.clear()
    ob.data = new
    bpy.data.meshes.remove(old)


def bounds_mm(ob):
    co = np.empty(len(ob.data.vertices) * 3)
    ob.data.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3) / MM
    return co.min(0), co.max(0)


# --- Parts ---------------------------------------------------------------------------------------
def box(name, cx, cy, z0, sx, sy, sz, grain_axis, bevel=BEVEL, is_chip=0.0):
    """Box in mm with bevel baked in; tagged with face attributes for the material.

    Hand-built pallets are not CAD-exact: each part gets a small width deviation, offset and
    twist about Z (inside the EN 13698-1 tolerance of +-3 mm on length and width). Heights stay
    nominal so the deck stays flat and the measured height is exact.
    """
    d_w = float(np.clip(RNG.normal(0, 0.4), -0.6, 0.6))
    off = RNG.normal(0, 0.5, 2).clip(-0.8, 0.8)
    twist = math.radians(float(np.clip(RNG.normal(0, 0.05), -0.08, 0.08)))
    if grain_axis == 0.0:
        sy += d_w
    else:
        sx += d_w
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    c, s = math.cos(twist), math.sin(twist)
    for v in bm.verts:
        x, y = v.co.x * sx, v.co.y * sy
        v.co.x = (cx + off[0] + x * c - y * s) * MM
        v.co.y = (cy + off[1] + x * s + y * c) * MM
        v.co.z = (z0 + (v.co.z + 0.5) * sz) * MM
    ob = new_object(name, bm)
    mod = ob.modifiers.new("Bevel", "BEVEL")
    mod.width = bevel * MM
    mod.segments = 3
    mod.limit_method = "NONE"
    bake_modifiers(ob)
    # Grain space (length on X): pith of the log 1-6 cm beside and 4-20 cm below/above the
    # board centre, plus a slight fibre slope - together they give the arched (cathedral) figure.
    centre_across = cy if grain_axis == 0.0 else cx
    pith = (RNG.uniform(-5, 5), (centre_across + RNG.choice((-1, 1)) * RNG.uniform(10, 60)) * MM,
            (z0 + sz * 0.5 + RNG.choice((-1, 1)) * RNG.uniform(40, 200)) * MM)
    tilt = (0.0, RNG.normal(0, 0.025), RNG.normal(0, 0.025))
    set_attrs(ob.data, {"grain_axis": grain_axis, "part_rand": RNG.random(), "is_chip": is_chip, "pith": pith, "tilt": tilt})
    return ob


def nail(name, cx, cy, top):
    """Nail head: diameter, height above the deck, tilt and corrosion differ from nail to nail."""
    d = RNG.uniform(6.4, 7.6)
    proud = float(np.clip(RNG.gamma(1.6, 0.35), 0.05, 1.8))
    tilt = math.radians(abs(RNG.normal(0, 3.5)))
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=16, radius1=d * 0.5 * MM, radius2=d * 0.47 * MM, depth=(1.2 + proud) * MM)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, (proud - (1.2 + proud) * 0.5) * MM))
    rot = Euler((tilt, 0.0, RNG.uniform(0, math.tau))).to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation((cx * MM, cy * MM, top * MM)) @ rot, verts=bm.verts)
    ob = new_object(name, bm)
    for p in ob.data.polygons:
        p.use_smooth = abs(p.normal.z) < 0.5
    set_attrs(ob.data, {"is_nail": 1.0, "part_rand": RNG.random(), "nail_rand": RNG.random()})
    return ob


# --- Damage: chipped edges, end cracks, raised splinters -----------------------------------------
def cutter_from(bm, part, fresh):
    ob = new_object("cutter", bm)
    vals = attrs_of(part)
    vals["fresh"] = fresh
    set_attrs(ob.data, vals)
    return ob


def chip_cutter(part, centre, radii):
    """Irregular, faceted lump on an edge: removed by boolean, its faces become fresh wood.
    Low subdivision + strong radial jitter gives the angular facets of split wood."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
    for v in bm.verts:
        v.co *= RNG.uniform(0.55, 1.2)
    rot = Euler(RNG.uniform(-0.45, 0.45, 3)).to_matrix().to_4x4()
    scale = Matrix.Diagonal((*[r * MM for r in radii], 1.0))
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(centre) * MM) @ rot @ scale, verts=bm.verts)
    return cutter_from(bm, part, 1.0)


def edge_point(lo, hi, axis, ends, t):
    """Point on the box edge running along `axis`, at the given min/max of the other two axes."""
    p = [0.0, 0.0, 0.0]
    others = [a for a in range(3) if a != axis]
    for a, e in zip(others, ends):
        p[a] = hi[a] if e else lo[a]
    p[axis] = lo[axis] + t * (hi[axis] - lo[axis])
    return p


def chips(part, count, edges, along=(6, 20), across=(3, 8), t_range=(0.02, 0.98)):
    lo, hi = bounds_mm(part)
    out = []
    for _ in range(count):
        axis, ends = edges[RNG.integers(len(edges))]
        t = RNG.uniform(*t_range) if RNG.random() < 0.5 else 1.0 - RNG.uniform(*t_range)
        r = [0.0, 0.0, 0.0]
        r[axis] = RNG.uniform(*along)
        for a in range(3):
            if a != axis:
                r[a] = RNG.uniform(*across)
        if attrs_of(part)["is_chip"] < 0.5:      # solid wood splits along the fibre
            g = int(attrs_of(part)["grain_axis"])
            r[g] = max(r[g], RNG.uniform(*along)) * RNG.uniform(1.4, 2.4)
        out.append(chip_cutter(part, edge_point(lo, hi, axis, ends, t), r))
    return out


def end_crack(part):
    """Drying/nailing crack running in from a board end along the grain, open at the top."""
    lo, hi = bounds_mm(part)
    sign = RNG.choice((-1, 1))
    x_end = hi[0] if sign > 0 else lo[0]
    y = lo[1] + RNG.uniform(0.25, 0.75) * (hi[1] - lo[1])
    length, depth, gap = RNG.uniform(40, 170), RNG.uniform(6, 13), RNG.uniform(0.8, 1.8)
    top = hi[2]
    x_o, x_i = x_end + sign * 2.0, x_end - sign * length
    bm = bmesh.new()
    vs = [bm.verts.new(Vector(p) * MM) for p in (
        (x_o, y - gap / 2, top + 1), (x_o, y + gap / 2, top + 1), (x_o, y, top - depth),
        (x_i, y - 0.05, top + 1), (x_i, y + 0.05, top + 1), (x_i, y, top - 0.5))]
    for f in ((0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)):
        bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return cutter_from(bm, part, 0.35)


def splinter(part, extras):
    """A sliver peeled up from a top edge: the groove it left is cut out, the sliver is added."""
    lo, hi = bounds_mm(part)
    sign_y = RNG.choice((-1, 1))
    y_edge = hi[1] if sign_y > 0 else lo[1]
    length, width, thick = RNG.uniform(60, 140), RNG.uniform(4, 8), RNG.uniform(1.0, 1.6)
    from_end = RNG.choice((-1, 1))
    x0 = (hi[0] if from_end > 0 else lo[0]) - from_end * RNG.uniform(0, 30)
    x1 = x0 - from_end * length
    y0, y1 = sorted((y_edge, y_edge - sign_y * width))
    top = hi[2]
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = ((x0 + x1) / 2 + v.co.x * abs(x1 - x0)) * MM
        v.co.y = ((y0 + y1) / 2 + v.co.y * (y1 - y0 + 0.6)) * MM
        v.co.z = (top - thick + (v.co.z + 0.5) * (thick + 1.0)) * MM
    groove = cutter_from(bm, part, 1.0)
    # The sliver itself: same footprint, lifted at the free end (towards the board end).
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = ((x0 + x1) / 2 + v.co.x * abs(x1 - x0)) * MM
        v.co.y = ((y0 + y1) / 2 + v.co.y * (y1 - y0) * 0.92) * MM
        v.co.z = (top - thick + (v.co.z + 0.5) * thick) * MM
    lift = RNG.uniform(1.0, 2.2) / length
    pivot = Vector((x1 * MM, (y0 + y1) / 2 * MM, top * MM))
    rot = Matrix.Rotation(-from_end * math.atan(lift), 4, "Y") @ Matrix.Rotation(sign_y * math.radians(RNG.uniform(2, 6)), 4, "X")
    bmesh.ops.transform(bm, matrix=Matrix.Translation(pivot) @ rot @ Matrix.Translation(-pivot), verts=bm.verts)
    sliver = new_object("splinter", bm)
    vals = attrs_of(part)
    set_attrs(sliver.data, vals)
    fresh = sliver.data.attributes["fresh"]
    fresh.data.foreach_set("value", [1.0 if p.normal.z < -0.5 else 0.15 for p in sliver.data.polygons])
    extras.append(sliver)
    return groove


def cut(part, cutters):
    for c in cutters:
        mod = part.modifiers.new("cut", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.solver = "EXACT"
        mod.object = c
        bake_modifiers(part)
        bpy.data.objects.remove(c)


# --- Assembly ------------------------------------------------------------------------------------
def build_geometry():
    parts, extras = [], []
    z_top = H - T_BOARD
    z_str = z_top - T_BOARD
    z_blk = z_str - H_BLOCK
    # Edge sets: (axis the edge runs along, (min/max of the other two axes in order)).
    long_top = [(0, (y, 1)) for y in (0, 1)]
    long_all = [(0, (y, z)) for y in (0, 1) for z in (0, 1)]
    ends = [(1, (x, 1)) for x in (0, 1)] + [(2, (x, y)) for x in (0, 1) for y in (0, 1)]
    for i, (y, w) in enumerate(TOP_BOARDS):
        p = box(f"top_{i}", 0, y, z_top, L, w, T_BOARD, 0.0)
        cuts = chips(p, RNG.integers(1, 4), long_top, t_range=(0.0, 0.12)) + chips(p, RNG.integers(1, 3), ends)
        if RNG.random() < 0.55:
            cuts.append(end_crack(p))
        if RNG.random() < 0.5:
            cuts.append(splinter(p, extras))
        cut(p, cuts)
        parts.append(p)
    for i, x in enumerate(X_ROWS):
        p = box(f"stringer_{i}", x, 0, z_str, 145.0, W, T_BOARD, 1.0)
        cut(p, chips(p, RNG.integers(0, 2), [(1, (x_, 0)) for x_ in (0, 1)]))
        parts.append(p)
        for j, (y, w) in enumerate(BLOCK_ROWS_Y):
            b = box(f"block_{i}{j}", x, y, z_blk, 145.0, w, H_BLOCK, 0.0, bevel=2.0, is_chip=1.0)
            # Pressed-chip blocks crumble at corners and along the bottom where forks hit them.
            edges = [(2, (a, c)) for a in (0, 1) for c in (0, 1)] + [(0, (c, 0)) for c in (0, 1)] + [(1, (c, 0)) for c in (0, 1)]
            cut(b, chips(b, RNG.integers(2, 5), edges, along=(5, 14), across=(2.5, 6)))
            parts.append(b)
    for i, (y, w) in enumerate(BOTTOM_BOARDS):
        p = box(f"bottom_{i}", 0, y, 0.0, L, w, T_BOARD, 0.0)
        cuts = chips(p, RNG.integers(2, 5), long_all) + chips(p, RNG.integers(0, 2), ends)
        if RNG.random() < 0.35:
            cuts.append(end_crack(p))
        cut(p, cuts)
        parts.append(p)
    # Nail heads on the top deck: two per board/stringer crossing, slightly staggered.
    for bi, (y, w) in enumerate(TOP_BOARDS):
        for x in X_ROWS:
            for k, (dx, dy) in enumerate(((-38.0, -0.22 * w), (38.0, 0.22 * w))):
                j = RNG.normal(0, 1.5, 2)
                parts.append(nail(f"nail_{bi}_{x}_{k}", x + dx + j[0], y + dy + j[1], H))
    parts += extras
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
    # Boolean seams leave slivers: weld near-duplicate points and dissolve zero-area faces.
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.02 * MM)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=0.02 * MM)
    bm.to_mesh(ob.data)
    bm.free()
    # Clean shading: n-gons from the booleans triangulated (needed for tangents), sharp by
    # angle, weighted normals so the large flat faces stay flat next to the bevels and breaks.
    tri = ob.modifiers.new("Triangulate", "TRIANGULATE")
    tri.min_vertices = 5
    bake_modifiers(ob)
    ob.data.set_sharp_from_angle(angle=math.radians(35))
    wn = ob.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL")
    wn.keep_sharp = True
    wn.weight = 50
    bake_modifiers(ob)
    ob.data.calc_loop_triangles()
    areas = np.empty(len(ob.data.loop_triangles))
    ob.data.loop_triangles.foreach_get("area", areas)
    if (areas <= 1e-10).any():
        raise RuntimeError(f"{int((areas <= 1e-10).sum())} degenerate triangles left after cleanup")
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


def map_range(nt, loc, src, a, b, c=0.0, d=1.0, smooth=False):
    n = node(nt, "ShaderNodeMapRange", loc, interpolation_type="SMOOTHSTEP" if smooth else "LINEAR")
    for k, v in (("From Min", a), ("From Max", b), ("To Min", c), ("To Max", d)):
        n.inputs[k].default_value = v
    nt.links.new(src, n.inputs["Value"])
    return n.outputs["Result"]


def math_op(nt, loc, op, a, b=None, c=None, clamp=False):
    n = node(nt, "ShaderNodeMath", loc, operation=op, use_clamp=clamp)
    for i, v in enumerate((a, b, c)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            nt.links.new(v, n.inputs[i])
    return n.outputs["Value"]


def mix(nt, loc, fac, a, b, kind="RGBA", blend="MIX"):
    n = node(nt, "ShaderNodeMix", loc, data_type=kind, blend_type=blend)
    for sock, v in (("Factor", fac), ("A", a), ("B", b)):
        if isinstance(v, (int, float, tuple)):
            n.inputs[sock].default_value = (*v, 1.0) if isinstance(v, tuple) and len(v) == 3 else v
        else:
            nt.links.new(v, n.inputs[sock])
    return n.outputs["Result"]


def noise(nt, loc, vec, scale, detail=4.0, rough=0.5):
    n = node(nt, "ShaderNodeTexNoise", loc)
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    n.inputs["Roughness"].default_value = rough
    nt.links.new(vec, n.inputs["Vector"])
    return n


def vmul(nt, loc, vec, factors):
    n = node(nt, "ShaderNodeVectorMath", loc, operation="MULTIPLY")
    n.inputs[1].default_value = factors
    nt.links.new(vec, n.inputs[0])
    return n.outputs["Vector"]


def assign_material(ob, mat):
    """Exactly one material slot, every face on it (the UI session can leave an empty slot)."""
    ob.data.materials.clear()
    ob.data.materials.append(mat)
    ob.data.polygons.foreach_set("material_index", [0] * len(ob.data.polygons))
    ob.data.update()


def build_material():
    mat = bpy.data.materials.new("M_TechSmoke_PalletWood")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    ln = nt.links.new
    out = node(nt, "ShaderNodeOutputMaterial", (2600, 0))
    bsdf = node(nt, "ShaderNodeBsdfPrincipled", (2300, 0))
    bsdf.inputs["IOR"].default_value = 1.5
    ln(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tex = node(nt, "ShaderNodeTexCoord", (-2000, 0))
    geo = node(nt, "ShaderNodeNewGeometry", (-2000, -400))
    sep = node(nt, "ShaderNodeSeparateXYZ", (-1800, 0))
    ln(tex.outputs["Object"], sep.inputs[0])
    A = {n: node(nt, "ShaderNodeAttribute", (-2000, -700 - 150 * i), attribute_name=n, attribute_type="GEOMETRY")
         for i, n in enumerate(FLOAT_ATTRS + VECTOR_ATTRS)}
    fac = {n: A[n].outputs["Fac"] for n in FLOAT_ATTRS}

    # Grain space: board length always on X, relative to the log's pith, with fibre slope.
    swapped = node(nt, "ShaderNodeCombineXYZ", (-1600, 100))
    ln(sep.outputs["Y"], swapped.inputs["X"]); ln(sep.outputs["X"], swapped.inputs["Y"]); ln(sep.outputs["Z"], swapped.inputs["Z"])
    gsel = mix(nt, (-1400, 0), fac["grain_axis"], tex.outputs["Object"], swapped.outputs["Vector"], "VECTOR")
    rel = node(nt, "ShaderNodeVectorMath", (-1250, 0), operation="SUBTRACT")
    ln(gsel, rel.inputs[0]); ln(A["pith"].outputs["Vector"], rel.inputs[1])
    gsep = node(nt, "ShaderNodeSeparateXYZ", (-1250, -250))
    ln(gsel, gsep.inputs[0])
    slope = node(nt, "ShaderNodeVectorMath", (-1100, -250), operation="SCALE")
    ln(A["tilt"].outputs["Vector"], slope.inputs[0]); ln(gsep.outputs["X"], slope.inputs["Scale"])
    gpos_n = node(nt, "ShaderNodeVectorMath", (-1000, 0), operation="ADD")
    ln(rel.outputs["Vector"], gpos_n.inputs[0]); ln(slope.outputs["Vector"], gpos_n.inputs[1])
    gpos = gpos_n.outputs["Vector"]

    # Medium: annual rings of spruce ~4.5 mm apart around the pith, slowly wandering.
    rn = noise(nt, (-800, 450), vmul(nt, (-900, 450), gpos, (0.6, 4.0, 4.0)), 1.5, 2.0)
    warp = node(nt, "ShaderNodeVectorMath", (-650, 450), operation="MULTIPLY_ADD")
    warp.inputs[1].default_value = (0.0, 0.006, 0.006)
    ln(rn.outputs["Color"], warp.inputs[0]); ln(gpos, warp.inputs[2])
    rings = node(nt, "ShaderNodeTexWave", (-500, 300), wave_type="RINGS", rings_direction="X")
    rings.inputs["Scale"].default_value = 70.0
    rings.inputs["Distortion"].default_value = 0.0
    ln(warp.outputs["Vector"], rings.inputs["Vector"])
    ring = map_range(nt, (-350, 300), rings.outputs["Fac"], 0.35, 0.85, smooth=True)

    # Micro: fibres stretched along the grain.
    fibres = noise(nt, (-650, 0), vmul(nt, (-800, 0), gpos, (3.0, 90.0, 90.0)), 4.0, 6.0, 0.6)

    # Spruce colour, per-part tone, knots.
    wood = mix(nt, (-150, 300), ring, (0.43, 0.32, 0.20), (0.33, 0.235, 0.135))
    wood = mix(nt, (0, 300), 0.18, wood, fibres.outputs["Color"], blend="MULTIPLY")
    tone = node(nt, "ShaderNodeHueSaturation", (150, 300))
    ln(map_range(nt, (0, 500), fac["part_rand"], 0, 1, 0.485, 0.515), tone.inputs["Hue"])
    ln(map_range(nt, (0, 650), fac["part_rand"], 0, 1, 0.85, 1.12), tone.inputs["Value"])
    ln(wood, tone.inputs["Color"])
    vor = node(nt, "ShaderNodeTexVoronoi", (-500, 800))
    ln(vmul(nt, (-650, 800), gpos, (5.0, 24.0, 24.0)), vor.inputs["Vector"])
    kpick = node(nt, "ShaderNodeSeparateColor", (-350, 950))
    ln(vor.outputs["Color"], kpick.inputs[0])
    knot = math_op(nt, (-50, 850), "MULTIPLY", map_range(nt, (-200, 800), vor.outputs["Distance"], 0.16, 0.08, smooth=True),
                   math_op(nt, (-200, 950), "GREATER_THAN", kpick.outputs["Red"], 0.88))
    spruce = mix(nt, (300, 400), knot, tone.outputs["Color"], (0.13, 0.065, 0.03))

    # Pressed-chip blocks: dense small flakes (4-12 mm), flattened by the press so they read
    # elongated on the side faces; two flake layers, low contrast, rare dark bark bits.
    cn = noise(nt, (-800, 1200), tex.outputs["Object"], 60.0, 3.0)
    cwarp = node(nt, "ShaderNodeVectorMath", (-700, 1300), operation="MULTIPLY_ADD")
    cwarp.inputs[1].default_value = (0.0025, 0.0025, 0.0025)
    ln(cn.outputs["Color"], cwarp.inputs[0]); ln(vmul(nt, (-850, 1350), tex.outputs["Object"], (1.0, 1.0, 2.6)), cwarp.inputs[2])
    chipv = node(nt, "ShaderNodeTexVoronoi", (-550, 1200))
    chipv.inputs["Scale"].default_value = 140.0
    ln(cwarp.outputs["Vector"], chipv.inputs["Vector"])
    chipv2 = node(nt, "ShaderNodeTexVoronoi", (-550, 1400))
    chipv2.inputs["Scale"].default_value = 260.0
    ln(cwarp.outputs["Vector"], chipv2.inputs["Vector"])
    cpick = node(nt, "ShaderNodeSeparateColor", (-400, 1250))
    ln(chipv.outputs["Color"], cpick.inputs[0])
    cpick2 = node(nt, "ShaderNodeSeparateColor", (-400, 1450))
    ln(chipv2.outputs["Color"], cpick2.inputs[0])
    # One dominant flake layer with hard cell borders (each flake its own tone), the finer
    # layer only nudges it; a thin dark seam where flakes meet (glue line / gap).
    flake = math_op(nt, (-250, 1300), "MULTIPLY_ADD", cpick.outputs["Red"], 0.8, math_op(nt, (-250, 1450), "MULTIPLY", cpick2.outputs["Red"], 0.2))
    chipcol = mix(nt, (-100, 1250), flake, (0.24, 0.17, 0.10), (0.52, 0.40, 0.25))
    seam = map_range(nt, (-250, 1150), chipv.outputs["Distance"], 0.0, 0.06, 0.45, 0.0)
    chipcol = mix(nt, (-50, 1150), seam, chipcol, (0.12, 0.085, 0.05))
    bark = math_op(nt, (-150, 1500), "GREATER_THAN", cpick2.outputs["Green"], 0.965)
    chipcol = mix(nt, (0, 1300), math_op(nt, (-50, 1500), "MULTIPLY", bark, 0.8), chipcol, (0.13, 0.095, 0.06))
    chipcol = mix(nt, (150, 1300), 0.12, chipcol, noise(nt, (0, 1450), tex.outputs["Object"], 900.0, 2.0).outputs["Color"], blend="MULTIPLY")
    species = mix(nt, (450, 500), fac["is_chip"], spruce, chipcol)

    # End grain: faces looking along the grain soak up dirt and read darker and rougher.
    nsep = node(nt, "ShaderNodeSeparateXYZ", (-1800, -400))
    ln(geo.outputs["Normal"], nsep.inputs[0])
    n_along = mix(nt, (-1600, -400), fac["grain_axis"], nsep.outputs["X"], nsep.outputs["Y"], "FLOAT")
    endgrain = math_op(nt, (-1250, -500), "MULTIPLY", map_range(nt, (-1400, -400), math_op(nt, (-1500, -400), "ABSOLUTE", n_along), 0.75, 0.92),
                       math_op(nt, (-1400, -550), "SUBTRACT", 1.0, fac["is_chip"]))
    species = mix(nt, (600, 500), math_op(nt, (450, 650), "MULTIPLY", endgrain, 0.32), species, (0.0, 0.0, 0.0))

    # Macro weathering: greyed softwood, patchy, boards differ in age (repairs).
    weather = map_range(nt, (-100, -350), noise(nt, (-300, -350), gpos, 2.2, 4.0).outputs["Fac"], 0.35, 0.75, 0.08, 0.42)
    age = node(nt, "ShaderNodeMath", (100, -450), operation="MULTIPLY_ADD", use_clamp=True)
    ln(fac["part_rand"], age.inputs[0]); age.inputs[1].default_value = 0.35; ln(weather, age.inputs[2])
    col = mix(nt, (750, 400), age.outputs["Value"], species, (0.25, 0.24, 0.225))

    # Ground dirt rising from the bottom, stains, grime in joints and corners (AO).
    zfade = map_range(nt, (-100, -600), sep.outputs["Z"], 0.0, 0.11, 0.55, 0.0)
    stain = map_range(nt, (-100, -800), noise(nt, (-300, -800), tex.outputs["Object"], 9.0, 3.0).outputs["Fac"], 0.56, 0.70, 0.0, 0.4, smooth=True)
    ao = node(nt, "ShaderNodeAmbientOcclusion", (-300, -1050), samples=16, only_local=True)
    ao.inputs["Distance"].default_value = 0.035
    grime = map_range(nt, (-100, -1050), ao.outputs["AO"], 0.85, 0.35, 0.0, 0.65)
    dirt_amt = math_op(nt, (150, -800), "ADD", math_op(nt, (100, -650), "ADD", zfade, stain, clamp=True), grime, clamp=True)
    col = mix(nt, (900, 400), dirt_amt, col, (0.075, 0.06, 0.045))

    # Vertical faces: rain/drip streaks running down; low down: fork-tine scuffs (rubber/steel).
    vertical = map_range(nt, (-1400, -700), math_op(nt, (-1500, -700), "ABSOLUTE", nsep.outputs["Z"]), 0.35, 0.15)
    drips = map_range(nt, (-100, -1250), noise(nt, (-300, -1250), vmul(nt, (-450, -1250), tex.outputs["Object"], (28.0, 28.0, 1.2)), 3.0, 3.0).outputs["Fac"], 0.55, 0.7, 0.0, 0.3)
    col = mix(nt, (1050, 400), math_op(nt, (150, -1250), "MULTIPLY", drips, vertical), col, (0.12, 0.10, 0.08))
    low = map_range(nt, (-100, -1450), sep.outputs["Z"], 0.115, 0.09)
    scuff_n = map_range(nt, (-100, -1600), noise(nt, (-300, -1600), vmul(nt, (-450, -1600), tex.outputs["Object"], (1.5, 1.5, 45.0)), 4.0, 5.0).outputs["Fac"], 0.6, 0.72, 0.0, 0.75)
    scuff = math_op(nt, (300, -1500), "MULTIPLY", math_op(nt, (150, -1500), "MULTIPLY", scuff_n, low), vertical)
    col = mix(nt, (1200, 400), scuff, col, (0.075, 0.073, 0.07))

    # Top deck: dust and boot traffic, lighter and matter.
    up = map_range(nt, (-1400, -850), nsep.outputs["Z"], 0.8, 0.95)
    high = map_range(nt, (-100, -1800), sep.outputs["Z"], 0.13, 0.14)
    dust_n = map_range(nt, (-100, -1950), noise(nt, (-300, -1950), tex.outputs["Object"], 3.5, 5.0, 0.6).outputs["Fac"], 0.5, 0.7, 0.0, 0.45, smooth=True)
    dust = math_op(nt, (300, -1850), "MULTIPLY", math_op(nt, (150, -1850), "MULTIPLY", up, high), dust_n)
    col = mix(nt, (1350, 400), dust, col, (0.33, 0.315, 0.29))

    # Convex edges rubbed by handling: slightly lighter and smoother.
    ao_in = node(nt, "ShaderNodeAmbientOcclusion", (-300, -2150), samples=16, inside=True, only_local=True)
    ao_in.inputs["Distance"].default_value = 0.006
    edge = math_op(nt, (300, -2150), "MULTIPLY", map_range(nt, (-100, -2150), ao_in.outputs["AO"], 0.9, 0.6, 0.0, 0.5), math_op(nt, (150, -2250), "SUBTRACT", 1.0, fac["is_chip"]))
    col = mix(nt, (1500, 400), edge, col, (0.40, 0.33, 0.24))

    # Fresh wood in chips, cracks and under splinters: little weathering, brighter, rougher.
    fresh_col = mix(nt, (1500, 650), 0.6, species, (0.50, 0.38, 0.24))
    fresh_dirty = mix(nt, (1650, 650), math_op(nt, (1500, 800), "MULTIPLY", dirt_amt, 0.5), fresh_col, (0.10, 0.08, 0.06))
    col = mix(nt, (1700, 400), math_op(nt, (1550, 250), "MULTIPLY", fac["fresh"], 0.9), col, fresh_dirty)

    # Nails: steel, corrosion differs per nail.
    rust_n = noise(nt, (1300, -1000), tex.outputs["Object"], 900.0, 2.0).outputs["Fac"]
    rust_in = math_op(nt, (1450, -1100), "ADD", rust_n, math_op(nt, (1450, -1200), "MULTIPLY", math_op(nt, (1350, -1250), "SUBTRACT", fac["nail_rand"], 0.5), 0.4))
    rust = map_range(nt, (1600, -1000), rust_in, 0.5, 0.72)
    steel = mix(nt, (1750, -800), rust, (0.56, 0.57, 0.58), (0.14, 0.075, 0.04))
    base = mix(nt, (1900, 250), fac["is_nail"], col, steel)
    ln(base, bsdf.inputs["Base Color"])
    metallic = math_op(nt, (1900, -1100), "MULTIPLY", fac["is_nail"], math_op(nt, (1750, -1100), "SUBTRACT", 1.0, rust))
    ln(metallic, bsdf.inputs["Metallic"])

    # Roughness: raw softwood 0.56-0.80 + weathering; chip blocks 0.85; end grain and fresh
    # breaks rougher; rubbed edges and scuffs smoother; dust matter; nails 0.45 / rust 0.85.
    r = node(nt, "ShaderNodeMath", (900, -300), operation="MULTIPLY_ADD", use_clamp=True)
    ln(weather, r.inputs[0]); r.inputs[1].default_value = 0.15
    ln(map_range(nt, (700, -300), fibres.outputs["Fac"], 0.38, 0.62, 0.56, 0.80), r.inputs[2])
    r = mix(nt, (1050, -300), fac["is_chip"], r.outputs["Value"], 0.86, "FLOAT")
    r = math_op(nt, (1150, -400), "ADD", r, math_op(nt, (1050, -450), "MULTIPLY", endgrain, 0.08), clamp=True)
    r = mix(nt, (1250, -300), fac["fresh"], r, 0.84, "FLOAT")
    r = mix(nt, (1350, -300), edge, r, 0.5, "FLOAT")
    r = mix(nt, (1450, -300), scuff, r, 0.45, "FLOAT")
    r = math_op(nt, (1550, -300), "ADD", r, math_op(nt, (1450, -450), "MULTIPLY", dust, 0.25), clamp=True)
    r_nail = mix(nt, (1650, -500), rust, 0.45, 0.85, "FLOAT")
    ln(mix(nt, (1900, -300), fac["is_nail"], r, r_nail, "FLOAT"), bsdf.inputs["Roughness"])

    # Relief: fibres + ring edges; torn fibres in fresh breaks; flake edges on chip blocks.
    h = math_op(nt, (1500, -1300), "MULTIPLY_ADD", fibres.outputs["Fac"], 0.7, ring)
    h = mix(nt, (1650, -1300), fac["is_chip"], h, map_range(nt, (1500, -1450), chipv.outputs["Distance"], 0.0, 0.08), "FLOAT")
    strength = math_op(nt, (1800, -1500), "SUBTRACT", math_op(nt, (1650, -1500), "MULTIPLY_ADD", fac["fresh"], 0.45, 0.35), fac["is_nail"], clamp=True)
    bump = node(nt, "ShaderNodeBump", (2100, -1300))
    bump.inputs["Distance"].default_value = 0.0005
    ln(strength, bump.inputs["Strength"]); ln(h, bump.inputs["Height"])
    ln(bump.outputs["Normal"], bsdf.inputs["Normal"])
    metallic_node = metallic.node
    return mat, metallic_node


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
    target.location = (2600, -600)
    for n in nt.nodes:
        n.select = False
    target.select = True                 # the UI session needs it selected as well as active
    nt.nodes.active = target
    ob.active_material_index = list(ob.data.materials).index(mat)
    scene.cycles.samples = 64          # AO grime and edge masks need more than a few samples
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
    surface = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"]   # name is localised in the UI
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
        img = bpy.data.images.get(name + "_out") or bpy.data.images.new(name + "_out", size, size, alpha=False, is_data=non_color)
        img.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
        img.pixels.foreach_set(arr.ravel())
        path = tex_dir / f"{name}.png"
        img.filepath_raw = str(path)
        img.file_format = "PNG"
        img.save()
        return path

    files = {}
    bc_px = px(out["BC"])
    files["BC"] = save(bc_px, f"T_{ASSET}_BC", False)
    rgh, met = px(out["R"]), px(out["M"])
    covered = uv_coverage(ob, size)
    orm = np.ones_like(rgh)
    orm[..., 1] = rgh[..., 0]
    orm[..., 2] = met[..., 0]
    files["ORM"] = save(orm, f"T_{ASSET}_ORM", True)
    n = px(out["N_GL"])
    n[..., 1] = 1.0 - n[..., 1]          # OpenGL -> DirectX (Unreal) green channel
    files["N"] = save(n, f"T_{ASSET}_N", True)
    bc = bc_px[..., :3][covered]
    r = rgh[..., 0][covered]
    if bc.mean() < 0.05 or r.mean() < 0.05:
        raise RuntimeError("Bake produced empty maps (no active image node?) - textures not valid")
    stats = {
        "uv_coverage": round(float(covered.mean()), 4),
        "basecolor_srgb8_p5_mean_p95": [np.percentile(bc.mean(1), 5) * 255, bc.mean(1).mean() * 255, np.percentile(bc.mean(1), 95) * 255],
        "roughness_p5_mean_p95": [np.percentile(r, 5), r.mean(), np.percentile(r, 95)],
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


def save_and_export(ob, out, files, stats, device, gpus, bake_size):
    blend = out / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
    fbx = out / "Export" / f"{ASSET}.fbx"
    for o in bpy.context.view_layer.objects:
        o.select_set(o == ob)
    bpy.ops.export_scene.fbx(filepath=str(fbx), use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
                             mesh_smooth_type="FACE", use_tspace=True, use_custom_props=False, add_leaf_bones=False,
                             object_types={"MESH"}, path_mode="STRIP", bake_anim=False)
    me = ob.data
    fresh = np.empty(len(me.polygons))
    me.attributes["fresh"].data.foreach_get("value", fresh)
    report = {
        "asset_id": ASSET, "blender": bpy.app.version_string, "device": device, "gpus": gpus,
        "dimensions_mm_xyz": [round(v / MM, 2) for v in ob.dimensions], "origin": "bottom centre (0,0,0)",
        "verts": len(me.vertices), "faces": len(me.polygons), "fresh_break_faces": int((fresh > 0.5).sum()),
        "uv_layers": [u.name for u in me.uv_layers], "bake_size": bake_size, "texture_stats": stats,
        "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [blend, fbx, *files.values()]},
    }
    (out / "build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("G3_BUILD_REPORT " + json.dumps(report))
    return report


def main():
    args = parse_args()
    out = args.out.resolve()
    for d in (out, out / "Textures", out / "Export"):
        d.mkdir(parents=True, exist_ok=True)
    scene = reset_scene()
    ob = build_geometry()
    unwrap(ob)
    mat, metallic_node = build_material()
    assign_material(ob, mat)
    device, gpus = enable_gpu(scene)
    files, stats = bake_maps(scene, ob, mat, metallic_node, args.bake, out / "Textures")
    save_and_export(ob, out, files, stats, device, gpus, args.bake)


if __name__ == "__main__":
    main()
