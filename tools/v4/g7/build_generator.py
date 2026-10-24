"""G7 (runs INSIDE Blender 5.2): build SM_R03_Generator_N02, the customer's portable petrol generator.

Measure sheet docs/design/G7_FLUSSDORF_ASSETS.md: 600 x 450 x 460 mm, open tube frame, origin at the
floor centre, X = length (engine left, alternator right), -Y = front (control panel side), Z up.
The mission inspection points (G6) are real parts here and exported as UE sockets:
  SOCKET_InspectPlug   spark plug + boot on the cylinder head
  SOCKET_InspectFilter transparent inline fuel filter under the tank
  SOCKET_TryStart      recoil starter T-handle
Reference: ArtSource/Reference/G7/SM_R03_Generator_N02/front34_v2.png (FLUX.2 klein, seed 11).
"""
import bpy, bmesh, math
from mathutils import Vector, Matrix, Euler

NAME = "SM_R03_Generator_N02"
COL = "G7_Generator"

# ---------------------------------------------------------------- scene
sc = bpy.context.scene
sc.unit_settings.system = "METRIC"
sc.unit_settings.scale_length = 1.0
sc.unit_settings.length_unit = "METERS"
col = bpy.data.collections.get(COL)
if col:
    for o in list(col.all_objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    col = bpy.data.collections.new(COL)
    sc.collection.children.link(col)
for m in [m for m in bpy.data.materials if m.name.startswith("M_GEN_")]:
    bpy.data.materials.remove(m)


# ---------------------------------------------------------------- materials
def _nodes(mat):
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return nt, bsdf


def _noise(nt, scale, detail=6.0, rough=0.55):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = detail
    nz.inputs["Roughness"].default_value = rough
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    return nz


def _range(nt, src, a, b, lo, hi, smooth=True):
    mr = nt.nodes.new("ShaderNodeMapRange")
    if smooth:
        mr.interpolation_type = "SMOOTHSTEP"
    mr.inputs["From Min"].default_value = a
    mr.inputs["From Max"].default_value = b
    mr.inputs["To Min"].default_value = lo
    mr.inputs["To Max"].default_value = hi
    nt.links.new(src, mr.inputs["Value"])
    return mr.outputs["Result"]


def _mix(nt, fac, c1, c2):
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    nt.links.new(fac, mx.inputs["Factor"])
    for sock, c in ((mx.inputs[6], c1), (mx.inputs[7], c2)):
        if isinstance(c, tuple):
            sock.default_value = c + (1.0,) if len(c) == 3 else c
        else:
            nt.links.new(c, sock)
    return mx.outputs[2]


def _add(nt, a, b, op="ADD"):
    m = nt.nodes.new("ShaderNodeMath")
    m.operation = op
    for i, v in enumerate((a, b)):
        if isinstance(v, (int, float)):
            m.inputs[i].default_value = v
        else:
            nt.links.new(v, m.inputs[i])
    return m.outputs[0]


def _micro_bump(nt, bsdf, scale, strength, extra_height=None):
    nz = _noise(nt, scale, 10.0, 0.7)
    h = nz.outputs["Fac"]
    if extra_height is not None:
        h = _add(nt, h, extra_height)
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = 0.0005
    nt.links.new(h, bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def _edge_mask(nt, radius=0.004):
    """Worn edges: convex edges from the bevel normal vs. true normal, broken up with noise."""
    bev = nt.nodes.new("ShaderNodeBevel")
    bev.samples = 8
    bev.inputs["Radius"].default_value = radius
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    dot = nt.nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    nt.links.new(bev.outputs["Normal"], dot.inputs[0])
    nt.links.new(geo.outputs["Normal"], dot.inputs[1])
    edge = _range(nt, dot.outputs["Value"], 0.995, 0.90, 0.0, 1.0)
    brk = _noise(nt, 90.0, 8.0, 0.65)
    brk_r = _range(nt, brk.outputs["Fac"], 0.48, 0.62, 0.0, 1.0)
    return _add(nt, edge, brk_r, "MULTIPLY")


def _cavity(nt, dist=0.02):
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.samples = 16
    ao.inputs["Distance"].default_value = dist
    return _range(nt, ao.outputs["AO"], 0.55, 0.95, 1.0, 0.0)


def paint_mat(name, base, rough, chip_metal=(0.24, 0.24, 0.235), coat=0.0, dust=True, stains=None):
    """Painted steel: dielectric paint with (macro) fade, (medium) chipped edges to bare/rusty
    steel and dust on top faces, (micro) roughness noise + orange-peel bump."""
    mat = bpy.data.materials.new(name)
    nt, bsdf = _nodes(mat)
    macro = _noise(nt, 3.0, 3.0, 0.5)
    base_var = _mix(nt, _range(nt, macro.outputs["Fac"], 0.3, 0.7, 0.0, 1.0),
                    tuple(c * 0.86 for c in base), tuple(min(1.0, c * 1.10) for c in base))
    chips = _edge_mask(nt)
    # scratches: stretched noise in object space
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (60.0, 2.5, 60.0)
    mp.inputs["Rotation"].default_value = (0.3, 0.2, 0.7)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    sn = nt.nodes.new("ShaderNodeTexNoise")
    sn.inputs["Scale"].default_value = 3.0
    sn.inputs["Detail"].default_value = 2.0
    nt.links.new(mp.outputs["Vector"], sn.inputs["Vector"])
    scr = _range(nt, sn.outputs["Fac"], 0.68, 0.73, 0.0, 0.45)
    wear = _add(nt, chips, scr, "MAXIMUM")
    rust_n = _noise(nt, 40.0, 6.0, 0.6)
    bare = _mix(nt, _range(nt, rust_n.outputs["Fac"], 0.45, 0.65, 0.0, 1.0), chip_metal + (1.0,), (0.17, 0.07, 0.03))
    col = _mix(nt, wear, base_var, bare)
    rough_n = _noise(nt, 25.0, 8.0, 0.6)
    r = _range(nt, rough_n.outputs["Fac"], 0.3, 0.7, rough - 0.08, rough + 0.10)
    r = _mix(nt, wear, r, (0.55, 0.55, 0.55))
    if dust:
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(geo.outputs["Normal"], sep.inputs[0])
        up = _range(nt, sep.outputs["Z"], 0.55, 0.95, 0.0, dust if not isinstance(dust, bool) else 0.55)
        dn = _noise(nt, 14.0, 6.0, 0.6)
        up = _add(nt, up, _range(nt, dn.outputs["Fac"], 0.35, 0.65, 0.4, 1.0), "MULTIPLY")
        col = _mix(nt, up, col, (0.36, 0.33, 0.29))
        r = _mix(nt, up, r, (0.9, 0.9, 0.9))
    if stains:
        col, r = stains(nt, col, r)
    cav = _cavity(nt)
    col = _mix(nt, _add(nt, cav, 0.55, "MULTIPLY"), col, (0.05, 0.045, 0.04))
    nt.links.new(col, bsdf.inputs["Base Color"])
    nt.links.new(r if not isinstance(r, tuple) else r, bsdf.inputs["Roughness"])
    met = _add(nt, wear, _range(nt, rust_n.outputs["Fac"], 0.45, 0.65, 1.0, 0.0), "MULTIPLY")
    nt.links.new(met, bsdf.inputs["Metallic"])
    if coat:
        bsdf.inputs["Coat Weight"].default_value = coat
        bsdf.inputs["Coat Roughness"].default_value = 0.25
    _micro_bump(nt, bsdf, 400.0, 0.05)
    return mat


def fuel_stains(nt, col, r):
    """Dried petrol runs from the filler neck (+X/+Y of the cap), darker and glossier."""
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    # distance from the cap axis (cap at x=+0.10, y=0.0 in tank object space)
    dx = _add(nt, sep.outputs["X"], -0.10)
    d = _add(nt, _add(nt, dx, dx, "MULTIPLY"), _add(nt, sep.outputs["Y"], sep.outputs["Y"], "MULTIPLY"))
    d = _add(nt, d, 0.5, "POWER")
    nz = _noise(nt, 22.0, 8.0, 0.65)
    m = _add(nt, _range(nt, d, 0.03, 0.16, 1.0, 0.0), _range(nt, nz.outputs["Fac"], 0.40, 0.62, 0.0, 1.0), "MULTIPLY")
    col = _mix(nt, _add(nt, m, 0.6, "MULTIPLY"), col, (0.20, 0.07, 0.02))
    r = _mix(nt, m, r, (0.18, 0.18, 0.18))
    return col, r


def simple_mat(name, base, rough, metal=0.0, rough_var=0.12, bump=0.04, grime=0.6, ior=1.5):
    mat = bpy.data.materials.new(name)
    nt, bsdf = _nodes(mat)
    macro = _noise(nt, 4.0, 3.0, 0.5)
    c = _mix(nt, _range(nt, macro.outputs["Fac"], 0.3, 0.7, 0.0, 1.0),
             tuple(x * 0.9 for x in base), tuple(min(1.0, x * 1.08) for x in base))
    cav = _cavity(nt)
    c = _mix(nt, _add(nt, cav, grime, "MULTIPLY"), c, (0.035, 0.03, 0.025))
    rn = _noise(nt, 30.0, 8.0, 0.6)
    r = _range(nt, rn.outputs["Fac"], 0.3, 0.7, rough - rough_var, rough + rough_var)
    r = _add(nt, r, _add(nt, cav, 0.25, "MULTIPLY"))
    nt.links.new(c, bsdf.inputs["Base Color"])
    nt.links.new(r, bsdf.inputs["Roughness"])
    bsdf.inputs["Metallic"].default_value = metal      # binary: grime darkens colour/roughness, never the metalness
    bsdf.inputs["IOR"].default_value = ior
    _micro_bump(nt, bsdf, 300.0, bump)
    return mat


def clear_mat(name, tint, rough):
    mat = bpy.data.materials.new(name)
    nt, bsdf = _nodes(mat)
    bsdf.inputs["Base Color"].default_value = tint + (1.0,)
    bsdf.inputs["Transmission Weight"].default_value = 1.0
    bsdf.inputs["IOR"].default_value = 1.58          # polycarbonate housing
    nz = _noise(nt, 60.0, 6.0, 0.6)
    nt.links.new(_range(nt, nz.outputs["Fac"], 0.3, 0.7, rough, rough + 0.12), bsdf.inputs["Roughness"])
    return mat


def perforated_mat(name):
    """Black heat-resistant paint on a punched steel sheet: hex hole grid in object space."""
    mat = simple_mat(name, (0.04, 0.036, 0.033), 0.62, rough_var=0.10, bump=0.08)
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.voronoi_dimensions = "3D"
    vor.inputs["Scale"].default_value = 110.0
    vor.inputs["Randomness"].default_value = 0.0
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    hole = _range(nt, vor.outputs["Distance"], 0.30, 0.36, 1.0, 0.0)
    col = _mix(nt, hole, bsdf.inputs["Base Color"].links[0].from_socket, (0.004, 0.004, 0.004))
    nt.links.new(col, bsdf.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.6
    bump.inputs["Distance"].default_value = 0.002
    nt.links.new(_add(nt, 1.0, hole, "SUBTRACT"), bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


M = {
    "shield": perforated_mat("M_GEN_MufflerShield"),
    "frame": paint_mat("M_GEN_Frame_PaintGreen", (0.022, 0.065, 0.032), 0.42),
    "tank": paint_mat("M_GEN_Tank_PaintOrange", (0.62, 0.115, 0.022), 0.30, coat=0.35, dust=0.28, stains=fuel_stains),
    "alu": simple_mat("M_GEN_AluCast", (0.78, 0.78, 0.76), 0.60, metal=1.0, rough_var=0.12, bump=0.14, grime=0.45),
    "plastic": simple_mat("M_GEN_PlasticBlack", (0.032, 0.032, 0.034), 0.52, rough_var=0.10, bump=0.03),
    "rubber": simple_mat("M_GEN_Rubber", (0.022, 0.022, 0.022), 0.86, rough_var=0.06, bump=0.08),
    "hose": simple_mat("M_GEN_FuelHose", (0.025, 0.025, 0.026), 0.45, rough_var=0.08, bump=0.02),
    "steel": simple_mat("M_GEN_SteelZinc", (0.62, 0.63, 0.64), 0.52, metal=1.0, rough_var=0.12, bump=0.05),
    "muffler": simple_mat("M_GEN_MufflerBlack", (0.045, 0.040, 0.036), 0.68, metal=0.0, rough_var=0.12, bump=0.12),
    "ceramic": simple_mat("M_GEN_PlugCeramic", (0.80, 0.79, 0.76), 0.22, rough_var=0.05, bump=0.01, grime=0.3),
    "clear": clear_mat("M_GEN_FilterHousing", (0.98, 0.97, 0.90), 0.04),
    "paper": simple_mat("M_GEN_FilterPaper", (0.72, 0.62, 0.42), 0.85, rough_var=0.05, bump=0.2, grime=0.2),
    "label": simple_mat("M_GEN_LabelSilver", (0.70, 0.70, 0.68), 0.35, metal=1.0, rough_var=0.05, bump=0.01),
    "red": simple_mat("M_GEN_SwitchRed", (0.45, 0.03, 0.02), 0.40, rough_var=0.08, bump=0.02),
}


# ---------------------------------------------------------------- geometry helpers
def _obj(name, bm, mat, loc=(0, 0, 0), rot=(0, 0, 0), bevel=None, segs=3, smooth=True):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    me.materials.append(M[mat] if isinstance(mat, str) else mat)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    if bevel:
        bv = ob.modifiers.new("Bevel", "BEVEL")
        bv.width = bevel
        bv.segments = segs
        bv.limit_method = "ANGLE"
        bv.angle_limit = math.radians(30)
        bv.harden_normals = True
        wn = ob.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL")
        wn.keep_sharp = True
    return ob


def box(name, size, loc, mat, bevel=0.0015, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    return _obj(name, bm, mat, loc, rot, bevel)


def cyl(name, r, depth, loc, mat, rot=(0, 0, 0), verts=32, bevel=0.001, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts, radius1=r,
                          radius2=r if r2 is None else r2, depth=depth)
    return _obj(name, bm, mat, loc, rot, bevel)


def tube(name, pts, r, mat, res=6):
    """Bent tube / hose through points (poly curve with round bevel), converted to a mesh."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = res
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    tmp = bpy.data.objects.new(name + "_crv", cu)
    col.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    bpy.data.curves.remove(cu)
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    me.materials.clear()
    me.materials.append(M[mat])
    for p in me.polygons:
        p.use_smooth = True
    return ob


def rounded_loop(cx, w, z0, z1, rad, n=6):
    """Points of a rounded rectangle tube loop in the YZ plane at x = cx (open at the bottom middle)."""
    y0, y1 = -w / 2, w / 2
    pts = []
    corners = [((y1 - rad, z1 - rad), 0), ((y0 + rad, z1 - rad), 90), ((y0 + rad, z0 + rad), 180), ((y1 - rad, z0 + rad), 270)]
    for (cy, cz), a0 in corners:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append(Vector((cx, cy + rad * math.cos(a), cz + rad * math.sin(a))))
    pts.append(pts[0].copy())
    return pts


def tube_poly(name, pts, r, mat):
    """Tube along a polyline (keeps sharp, real bends)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 6
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for p, v in zip(sp.points, pts):
        p.co = (v.x, v.y, v.z, 1.0)
    tmp = bpy.data.objects.new(name + "_crv", cu)
    col.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    bpy.data.curves.remove(cu)
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    me.materials.append(M[mat])
    for p in me.polygons:
        p.use_smooth = True
    return ob


# ---------------------------------------------------------------- frame (25 mm tube)
TR = 0.0125
FX = 0.285          # loop planes
FW = 0.42           # loop width (Y), outside 0.445
Z_BOT, Z_TOP = 0.045, 0.325
parts = []
for i, x in enumerate((-FX, FX)):
    parts.append(tube_poly(f"Frame_Loop_{i}", rounded_loop(x, FW, Z_BOT, Z_TOP, 0.055), TR, "frame"))
for i, y in enumerate((-FW / 2, FW / 2)):
    parts.append(tube_poly(f"Frame_RailBottom_{i}", [Vector((-FX, y, Z_BOT)), Vector((FX, y, Z_BOT))], TR, "frame"))
    parts.append(tube_poly(f"Frame_RailTop_{i}", [Vector((-FX, y, Z_TOP)), Vector((FX, y, Z_TOP))], TR, "frame"))
# cross members carrying the engine/alternator bed
for i, x in enumerate((-0.12, 0.12)):
    parts.append(tube_poly(f"Frame_Cross_{i}", [Vector((x, -FW / 2, Z_BOT)), Vector((x, FW / 2, Z_BOT))], 0.011, "frame"))
# rubber feet under the bottom rail corners
for i, (x, y) in enumerate([(-0.25, -0.21), (0.25, -0.21), (-0.25, 0.21), (0.25, 0.21)]):
    parts.append(box(f"Foot_{i}", (0.055, 0.042, 0.034), (x, y, 0.017), "rubber", bevel=0.004))
# bed plate on the cross members
parts.append(box("BedPlate", (0.34, 0.20, 0.004), (0.0, 0.0, Z_BOT + 0.014), "steel", bevel=0.001))

# ---------------------------------------------------------------- fuel tank (approx. 12 l)
tank = box("Tank", (0.50, 0.375, 0.09), (0.0, 0.0, Z_TOP + 0.0125 + 0.045), "tank", bevel=0.026)
tank.modifiers["Bevel"].segments = 6
tank.modifiers["Bevel"].angle_limit = math.radians(20)
parts.append(tank)
parts.append(box("Tank_Seam", (0.512, 0.387, 0.008), (0.0, 0.0, Z_TOP + 0.0165), "tank", bevel=0.002))
cap_z = Z_TOP + 0.0125 + 0.09
parts.append(cyl("Tank_Neck", 0.026, 0.012, (0.10, 0.0, cap_z + 0.002), "tank", bevel=0.002))
cap = cyl("Tank_Cap", 0.037, 0.022, (0.10, 0.0, cap_z + 0.019), "plastic", verts=48, bevel=0.003)
parts.append(cap)
for k in range(24):                                   # grip ribs around the cap
    a = 2 * math.pi * k / 24
    parts.append(box(f"Cap_Rib_{k}", (0.004, 0.005, 0.018),
                     (0.10 + 0.0375 * math.cos(a), 0.0375 * math.sin(a), cap_z + 0.019), "plastic", bevel=0.0008, rot=(0, 0, a)))
# fuel level gauge window (simple domed lens)
parts.append(cyl("Tank_Gauge", 0.016, 0.006, (-0.12, -0.04, cap_z + 0.002), "clear", verts=32, bevel=0.003))
# fuel tap under the tank, front left
parts.append(box("FuelTap_Body", (0.030, 0.024, 0.026), (-0.04, -0.13, Z_TOP - 0.008), "alu", bevel=0.002))
parts.append(box("FuelTap_Lever", (0.030, 0.006, 0.010), (-0.04, -0.145, Z_TOP - 0.006), "plastic", bevel=0.0015, rot=(0, 0.3, 0)))

# ---------------------------------------------------------------- engine (left half)
EX = -0.13
parts.append(box("Crankcase", (0.20, 0.23, 0.15), (EX, 0.0, 0.135), "alu", bevel=0.012))
parts.append(cyl("Crankcase_Cover", 0.085, 0.02, (EX + 0.108, 0.0, 0.135), "alu", rot=(0, math.pi / 2, 0), verts=48, bevel=0.004))
for k, (bx, bz) in enumerate([(-0.08, 0.075), (0.08, 0.075), (-0.08, 0.195), (0.08, 0.195), (0.0, 0.07)]):
    parts.append(cyl(f"Crank_Bolt_{k}", 0.0055, 0.008, (EX + bx, -0.118, bz), "steel", rot=(math.pi / 2, 0, 0), verts=6, bevel=0.0006))
# cylinder + fins, inclined 25 deg towards the back
cyl_piv = Vector((EX + 0.01, 0.04, 0.205))
tilt = Euler((math.radians(25), 0, 0))
for k in range(7):
    off = Vector((0, 0, 0.010 + k * 0.0105))
    off.rotate(tilt)
    parts.append(box(f"Cyl_Fin_{k}", (0.115, 0.115, 0.0035), tuple(cyl_piv + off), "alu", bevel=0.0012, rot=tilt))
off = Vector((0, 0, 0.045)); off.rotate(tilt)
parts.append(cyl("Cyl_Barrel", 0.040, 0.09, tuple(cyl_piv + off), "alu", rot=tilt, verts=32))
off = Vector((0, 0, 0.092)); off.rotate(tilt)
head_c = cyl_piv + off
parts.append(box("Cyl_Head", (0.12, 0.12, 0.028), tuple(head_c), "alu", bevel=0.006, rot=tilt))
# spark plug on the FRONT face of the head, pointing forward/up -> accessible from the panel side
plug_dir = Vector((-0.15, -1, 0.25)).normalized()
plug_base = head_c + Vector((0.0, -0.06, -0.004))
rot_plug = plug_dir.to_track_quat("Z", "Y").to_euler()
parts.append(cyl("Plug_Hex", 0.0105, 0.012, tuple(plug_base + plug_dir * 0.006), "steel", rot=rot_plug, verts=6, bevel=0.0006))
parts.append(cyl("Plug_Insulator", 0.0055, 0.026, tuple(plug_base + plug_dir * 0.025), "ceramic", rot=rot_plug, verts=24, bevel=0.0008))
parts.append(cyl("Plug_Boot", 0.0095, 0.045, tuple(plug_base + plug_dir * 0.050), "rubber", rot=rot_plug, verts=24, bevel=0.002, r2=0.008))
boot_end = plug_base + plug_dir * 0.072
parts.append(tube("Plug_HTLead", [boot_end, boot_end + Vector((-0.03, -0.01, 0.02)), Vector((EX - 0.075, -0.07, 0.24)),
                                  Vector((EX - 0.085, -0.03, 0.20))], 0.0035, "rubber"))
plug_tip = plug_base + plug_dir * 0.03
# recoil starter on the engine end (-X)
RS_X = EX - 0.125
parts.append(cyl("Recoil_Housing", 0.105, 0.05, (RS_X, 0.0, 0.15), "plastic", rot=(0, math.pi / 2, 0), verts=64, bevel=0.008))
for k in range(7):                                    # cooling-air slots in the housing face
    parts.append(box(f"Recoil_Slot_{k}", (0.006, 0.014, 0.07 - abs(k - 3) * 0.012),
                     (RS_X - 0.026, -0.045 + k * 0.015, 0.15), "muffler", bevel=0.001))
grip_c = Vector((RS_X - 0.01, -0.075, 0.245))
parts.append(tube("Recoil_Rope", [Vector((RS_X - 0.005, -0.055, 0.21)), grip_c + Vector((0, 0.004, -0.012))], 0.0022, "hose", res=3))
parts.append(cyl("Recoil_Grip", 0.012, 0.085, tuple(grip_c), "plastic", rot=(0, math.pi / 2, 0), verts=24, bevel=0.004))
# air filter box (front, above the carburettor)
parts.append(box("AirFilter_Box", (0.075, 0.06, 0.11), (EX - 0.085, -0.13, 0.225), "plastic", bevel=0.008))
parts.append(box("AirFilter_Clip", (0.012, 0.008, 0.03), (EX - 0.085, -0.162, 0.25), "steel", bevel=0.001))
# carburettor + choke lever
carb = Vector((EX + 0.05, -0.12, 0.215))
parts.append(box("Carb_Body", (0.045, 0.04, 0.045), tuple(carb), "alu", bevel=0.004))
parts.append(cyl("Carb_Bowl", 0.018, 0.022, tuple(carb + Vector((0, 0, -0.03))), "alu", verts=32, bevel=0.002))
parts.append(box("Choke_Lever", (0.05, 0.006, 0.012), tuple(carb + Vector((0.02, -0.024, 0.012))), "plastic", bevel=0.002, rot=(0, -0.2, 0)))
# transparent inline fuel filter in the hose tap -> carburettor (mission point)
f_top = Vector((-0.04, -0.135, Z_TOP - 0.025))
f_c = Vector((-0.02, -0.15, 0.27))
f_dir = Vector((0.15, -0.05, -1.0)).normalized()
rot_f = f_dir.to_track_quat("Z", "Y").to_euler()
parts.append(cyl("Filter_Housing", 0.011, 0.046, tuple(f_c), "clear", rot=rot_f, verts=32, bevel=0.003))
parts.append(cyl("Filter_Element", 0.0075, 0.034, tuple(f_c), "paper", rot=rot_f, verts=24, bevel=0.0))
for s in (-1, 1):
    parts.append(cyl(f"Filter_Nipple_{s}", 0.0035, 0.012, tuple(f_c + f_dir * (0.029 * s)), "clear", rot=rot_f, verts=16, bevel=0.0))
parts.append(tube("FuelHose_In", [f_top, f_top + Vector((0.0, -0.01, -0.01)), f_c - f_dir * 0.034], 0.0045, "hose"))
parts.append(tube("FuelHose_Out", [f_c + f_dir * 0.034, f_c + f_dir * 0.05 + Vector((0.02, 0.0, 0.0)),
                                   carb + Vector((0.0, -0.022, 0.0))], 0.0045, "hose"))
# muffler with perforated heat shield at the back
parts.append(box("Muffler", (0.15, 0.07, 0.10), (EX + 0.02, 0.165, 0.23), "muffler", bevel=0.01))
parts.append(box("Muffler_Shield", (0.17, 0.006, 0.12), (EX + 0.02, 0.205, 0.23), "shield", bevel=0.002))
parts.append(cyl("Muffler_Outlet", 0.012, 0.03, (EX + 0.10, 0.19, 0.20), "muffler", rot=(0, math.pi / 2, 0), verts=24, bevel=0.0015))

# ---------------------------------------------------------------- alternator (right half)
AX = 0.12
parts.append(cyl("Alternator", 0.105, 0.15, (AX, 0.02, 0.15), "alu", rot=(0, math.pi / 2, 0), verts=64, bevel=0.006))
parts.append(cyl("Alternator_EndCap", 0.095, 0.03, (AX + 0.088, 0.02, 0.15), "alu", rot=(0, math.pi / 2, 0), verts=64, bevel=0.006))
for k in range(12):                                   # cooling slots on the end cap
    a = 2 * math.pi * k / 12
    parts.append(box(f"Alt_Vent_{k}", (0.004, 0.009, 0.030), (AX + 0.104, 0.02 + 0.055 * math.cos(a), 0.15 + 0.055 * math.sin(a)),
                     "muffler", bevel=0.0008, rot=(a + math.pi / 2, 0, 0)))
for k, a in enumerate((0, math.pi / 2, math.pi, 1.5 * math.pi)):  # through-bolts
    parts.append(cyl(f"Alt_Bolt_{k}", 0.004, 0.012, (AX + 0.106, 0.02 + 0.08 * math.cos(a), 0.15 + 0.08 * math.sin(a)),
                     "steel", rot=(0, math.pi / 2, 0), verts=6, bevel=0.0005))
for k, x in enumerate((EX - 0.06, EX + 0.06, AX - 0.03, AX + 0.05)):  # anti-vibration mounts
    parts.append(cyl(f"Mount_{k}", 0.014, 0.018, (x, 0.0 if k < 2 else 0.02, Z_BOT + 0.025), "rubber", verts=24, bevel=0.002))

# ---------------------------------------------------------------- control panel with two Schuko sockets
PX, PZ, PY = 0.13, 0.215, -0.17
parts.append(box("Panel_Box", (0.20, 0.07, 0.15), (PX, PY + 0.035, PZ), "plastic", bevel=0.006))
parts.append(box("Panel_Face", (0.19, 0.004, 0.14), (PX, PY - 0.001, PZ), "plastic", bevel=0.001))
for k, x in enumerate((PX - 0.045, PX + 0.045)):
    sc_c = Vector((x, PY - 0.004, PZ + 0.025))
    parts.append(cyl(f"Schuko_Rim_{k}", 0.030, 0.012, tuple(sc_c), "plastic", rot=(math.pi / 2, 0, 0), verts=48, bevel=0.003))
    parts.append(cyl(f"Schuko_Well_{k}", 0.0195, 0.006, tuple(sc_c + Vector((0, -0.004, 0))), "muffler", rot=(math.pi / 2, 0, 0), verts=48, bevel=0.0))
    for s in (-1, 1):
        parts.append(cyl(f"Schuko_Pin_{k}_{s}", 0.0024, 0.004, tuple(sc_c + Vector((0.0095 * s, -0.008, 0))), "rubber",
                         rot=(math.pi / 2, 0, 0), verts=12, bevel=0.0))
        parts.append(box(f"Schuko_Earth_{k}_{s}", (0.004, 0.003, 0.006), tuple(sc_c + Vector((0, -0.0075, 0.0175 * s))), "steel", bevel=0.0004))
    # hinged spring cover, flipped up
    parts.append(box(f"Schuko_Cover_{k}", (0.056, 0.006, 0.040), tuple(sc_c + Vector((0, -0.018, 0.045))), "plastic", bevel=0.003, rot=(-1.2, 0, 0)))
parts.append(box("Panel_Switch_Base", (0.026, 0.006, 0.018), (PX - 0.05, PY - 0.004, PZ - 0.045), "plastic", bevel=0.001))
parts.append(box("Panel_Switch", (0.012, 0.010, 0.010), (PX - 0.05, PY - 0.009, PZ - 0.043), "red", bevel=0.0015, rot=(0.3, 0, 0)))
parts.append(cyl("Panel_Breaker", 0.008, 0.012, (PX + 0.02, PY - 0.008, PZ - 0.045), "plastic", rot=(math.pi / 2, 0, 0), verts=24, bevel=0.0015))
parts.append(box("Panel_RatingPlate", (0.06, 0.002, 0.022), (PX + 0.055, PY - 0.004, PZ - 0.045), "label", bevel=0.0005))
parts.append(cyl("Panel_EarthStud", 0.005, 0.014, (PX - 0.085, PY - 0.009, PZ - 0.05), "steel", rot=(math.pi / 2, 0, 0), verts=6, bevel=0.0006))

# ---------------------------------------------------------------- sockets for Unreal (mission points)
def socket(name, loc):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = "ARROWS"
    e.empty_display_size = 0.04
    e.location = loc
    col.objects.link(e)
    return e

sockets = [socket("SOCKET_InspectPlug", tuple(plug_tip)), socket("SOCKET_InspectFilter", tuple(f_c)),
           socket("SOCKET_TryStart", tuple(grip_c))]

# ---------------------------------------------------------------- join into one mesh + collision
for o in parts:
    o.select_set(False)
vl = bpy.context.view_layer
dg = bpy.context.evaluated_depsgraph_get()
bm_all = bmesh.new()
mats = []
for o in parts:
    ev = o.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev)
    me.transform(o.matrix_world)
    idx_map = []
    for m in me.materials:
        if m not in mats:
            mats.append(m)
        idx_map.append(mats.index(m))
    for p in me.polygons:
        p.material_index = idx_map[p.material_index] if idx_map else 0
    bm_all.from_mesh(me)
    bpy.data.meshes.remove(me)
for o in parts:
    bpy.data.objects.remove(o, do_unlink=True)
# n-gons (cylinder caps, tube caps) break tangent export for Unreal -> triangulate only those
bmesh.ops.triangulate(bm_all, faces=[f for f in bm_all.faces if len(f.verts) > 4])
old = bpy.data.meshes.get(NAME)
if old:
    bpy.data.meshes.remove(old)
me = bpy.data.meshes.new(NAME)
bm_all.to_mesh(me)
bm_all.free()
for m in mats:
    me.materials.append(m)
gen = bpy.data.objects.new(NAME, me)
col.objects.link(gen)
for s in sockets:
    s.parent = gen
# simple convex collision (UE: UCX_), slightly inside the frame silhouette
ucx = box("UCX_" + NAME + "_00", (0.60, 0.445, 0.44), (0, 0, 0.22), "rubber", bevel=None)
ucx.data.materials.clear()
ucx.display_type = "WIRE"
ucx.hide_render = True
ucx.parent = gen

# UV: smart project per material island (procedural looks are object-space; UVs are for the later bake)
vl.objects.active = gen
for o in bpy.context.selected_objects:
    o.select_set(False)
gen.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003, scale_to_bounds=False)
bpy.ops.object.mode_set(mode="OBJECT")

bb = [gen.matrix_world @ Vector(c) for c in gen.bound_box]
dims = [round(max(v[i] for v in bb) - min(v[i] for v in bb), 4) for i in range(3)]
result = {"object": NAME, "dims_m": dims, "z_min": round(min(v.z for v in bb), 4), "tris": sum(len(p.vertices) - 2 for p in me.polygons),
          "materials": [m.name for m in me.materials], "sockets": [s.name for s in sockets]}
print("G7_GENERATOR", result)
