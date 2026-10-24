"""G7 shared helpers (exec'd inside Blender by the build_* scripts): procedural PBR materials with
macro / medium / micro detail in object space and mesh helpers with real-size bevels.
The calling script must define `col` (target collection) and `M` (material dict) before building."""
import bpy, bmesh, math
from mathutils import Vector

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




def join_parts(name, parts):
    """Bake modifiers, join all part objects into one mesh `name` (n-gons triangulated for UE tangents)."""
    dg = bpy.context.evaluated_depsgraph_get()
    bm_all = bmesh.new()
    mats = []
    for o in parts:
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        me.transform(o.matrix_world)
        idx = []
        for m in me.materials:
            if m not in mats:
                mats.append(m)
            idx.append(mats.index(m))
        for p in me.polygons:
            p.material_index = idx[p.material_index] if idx else 0
        bm_all.from_mesh(me)
        bpy.data.meshes.remove(me)
    for o in parts:
        bpy.data.objects.remove(o, do_unlink=True)
    bmesh.ops.triangulate(bm_all, faces=[f for f in bm_all.faces if len(f.verts) > 4])
    old = bpy.data.meshes.get(name)
    if old:
        bpy.data.meshes.remove(old)
    me = bpy.data.meshes.new(name)
    bm_all.to_mesh(me)
    bm_all.free()
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    return ob


def collision_box(name, size, loc, parent):
    u = box("UCX_" + name, size, loc, list(M)[0], bevel=None)
    u.data.materials.clear()
    u.display_type = "WIRE"
    u.parent = parent
    for attr in ("visible_camera", "visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission"):
        setattr(u, attr, False)
    return u


def smart_uv(ob):
    vl = bpy.context.view_layer
    for o in bpy.context.selected_objects:
        o.select_set(False)
    vl.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")
