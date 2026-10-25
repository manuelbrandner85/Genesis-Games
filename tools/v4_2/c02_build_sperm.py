"""CR-001 Phase 3 (runs inside Blender 5.2): human spermatozoon after docs/v4_2/C02_MASSBLATT.md.

Scale: 1 Blender unit = 1 um, scene scale_length 0.01 (1 unit shows and exports as 1 cm = 1 uu in Unreal).
Head at the origin pointing +X, tail along -X (same as AGenesisSpermPawn). One mesh lofted from
cross-sections: flattened paddle head with acrosome cap, neck, midpiece with the mitochondrial helix,
tapering principal piece and hair-fine end piece. UV1 = surface, UV2.x = tail coordinate 0 (neck) .. 1
(tip) for the flagellar wave in Unreal (World Position Offset). SM_C02_Spermium is exported straight;
SM_C02_Spermium_Pose is a non-exported copy bent into one beat phase for look renders.
"""
import math
import bmesh
import bpy

HEAD_L, HEAD_W, HEAD_T = 4.1, 2.8, 1.2
NECK_END = -HEAD_L / 2 - 0.35
MID_END = NECK_END - 4.5
PRINCIPAL_END = MID_END - 45.0
TIP = PRINCIPAL_END - 4.0
WAVELENGTH, TIP_AMPLITUDE = 25.0, 5.0


def profile(x):
    """(half width, half thickness, ring segments) of the cross-section at x."""
    h = HEAD_L / 2
    if x >= -h:
        u = x / h                                         # +1 front .. -1 back
        e = math.sqrt(max(0.0, 1 - u * u))
        w = HEAD_W / 2 * e ** 0.85 * (1.0 + 0.06 * u)    # paddle: slightly wider in the front half
        t = HEAD_T / 2 * e ** 0.9 * (0.82 + 0.18 * (1 - u) / 2)   # thinner at the tip
        # back of the head flows into the neck instead of closing (smooth max with the neck radius)
        k = min(1.0, max(0.0, (-u - 0.55) / 0.45))
        k = k * k * (3 - 2 * k)
        neck = 0.55 * k
        w = (w ** 4 + neck ** 4) ** 0.25
        t = (t ** 4 + (neck * 0.9) ** 4) ** 0.25
        return max(w, 0.02), max(t, 0.02), 32
    if x >= NECK_END:                                     # neck: head base narrows into the midpiece
        a = (x - (-h)) / (NECK_END - (-h))
        a = a * a * (3 - 2 * a)
        r = 0.55 * (1 - a) + 0.36 * a
        return r, r * (0.9 + 0.1 * a), 24
    if x >= MID_END:                                      # midpiece with mitochondrial sheath
        return 0.35, 0.35, 24
    if x >= PRINCIPAL_END:
        a = (x - MID_END) / (PRINCIPAL_END - MID_END)
        r = 0.25 * (1 - a) + 0.075 * a
        return r, r, 12
    a = (x - PRINCIPAL_END) / (TIP - PRINCIPAL_END)
    r = 0.05 * (1 - a) + 0.012 * a
    return r, r, 8


def stations():
    xs, x = [], HEAD_L / 2
    while x > TIP:
        xs.append(x)
        if x > -HEAD_L / 2:
            step = 0.06 if abs(x) > HEAD_L / 2 - 0.4 else 0.12
        elif x > MID_END:
            step = 0.06                                  # helix needs fine rings
        else:
            step = 0.35
        x -= step
    xs.append(TIP)
    return xs


def build_mesh(name):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    tail_uv = bm.loops.layers.uv.new("TailWave")
    rings, coords = [], []
    xs = stations()
    seg = 32
    for x in xs:
        w, t, _ = profile(x)
        ring = []
        for k in range(seg):
            ang = 2 * math.pi * k / seg
            rw, rt = w, t
            if MID_END <= x <= NECK_END:                # left-handed helix of mitochondria, pitch 0.45 um
                bump = 0.012 * math.sin(ang * 1 + x * 2 * math.pi / 0.45)
                rw += bump
                rt += bump
            if x > -HEAD_L / 2 and x > 0.1:              # acrosome cap: a slight swelling over the front 60 %
                cap = 0.035 * math.sin(math.pi * min(1.0, (x - 0.1) / (HEAD_L / 2 - 0.1)))
                rt += cap * abs(math.sin(ang))
            ring.append(bm.verts.new((x, rw * math.cos(ang), rt * math.sin(ang))))
        rings.append(ring)
        coords.append(x)
    tip = bm.verts.new((TIP - 0.02, 0, 0))
    nose = bm.verts.new((HEAD_L / 2 + 0.01, 0, 0))
    total = HEAD_L / 2 - TIP
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for k in range(seg):
            f = bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
            for loop in f.loops:
                vx = loop.vert.co.x
                ang = math.atan2(loop.vert.co.z, loop.vert.co.y) / (2 * math.pi) % 1.0
                loop[uv].uv = ((HEAD_L / 2 - vx) / total, ang)
                loop[tail_uv].uv = (max(0.0, (NECK_END - vx) / (NECK_END - TIP)), 0.0)
    for k in range(seg):
        bm.faces.new((rings[0][(k + 1) % seg], rings[0][k], nose))
        bm.faces.new((rings[-1][k], rings[-1][(k + 1) % seg], tip))
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


def material(name, color, ior, transmission, rough, sss=0.0, grain=0.12):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["IOR"].default_value = ior
    p.inputs["Transmission Weight"].default_value = transmission
    p.inputs["Roughness"].default_value = rough
    p.inputs["Subsurface Weight"].default_value = sss
    p.inputs["Subsurface Radius"].default_value = (0.9, 0.8, 0.7)      # um: light travels ~1 um inside the cell
    p.inputs["Subsurface Scale"].default_value = 1.0
    # Micro variation: granular chromatin / sheath irregularity in object space (no UV seams)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 4.0
    noise.inputs["Detail"].default_value = 6.0
    rng = nt.nodes.new("ShaderNodeMapRange")
    rng.inputs["To Min"].default_value = rough * 0.6
    rng.inputs["To Max"].default_value = rough * 1.4
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 0.02
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], rng.inputs["Value"])
    nt.links.new(rng.outputs["Result"], p.inputs["Roughness"])
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    grains = nt.nodes.new("ShaderNodeTexNoise")               # irregular granules ~0.2-0.4 um
    grains.inputs["Scale"].default_value = 7.0
    grains.inputs["Detail"].default_value = 8.0
    grains.inputs["Roughness"].default_value = 0.65
    nt.links.new(tc.outputs["Object"], grains.inputs["Vector"])
    shade = nt.nodes.new("ShaderNodeMix")
    shade.data_type = "RGBA"
    shade.blend_type = "MULTIPLY"
    shade.inputs["Factor"].default_value = grain
    shade.inputs["A"].default_value = (*color, 1)
    nt.links.new(grains.outputs["Fac"], shade.inputs["B"])
    nt.links.new(shade.outputs["Result"], p.inputs["Base Color"])
    nt.links.new(p.outputs["BSDF"], out.inputs["Surface"])
    return m


def head_material():
    """Acrosome (front 60 %, lighter, more transparent) over the dense nucleus, midpiece slightly darker."""
    m = bpy.data.materials.get("M_C02_Spermium") or bpy.data.materials.new("M_C02_Spermium")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])

    def region(lo, hi, curve=0.0):
        """Smooth 0..1 along X; curve > 0 bends the boundary (x + curve * y^2), like the cap edge."""
        r = nt.nodes.new("ShaderNodeMapRange")
        r.interpolation_type = "SMOOTHSTEP"
        r.inputs["From Min"].default_value = lo
        r.inputs["From Max"].default_value = hi
        if curve:
            sq = nt.nodes.new("ShaderNodeMath")
            sq.operation = "MULTIPLY"
            nt.links.new(sep.outputs["Y"], sq.inputs[0])
            nt.links.new(sep.outputs["Y"], sq.inputs[1])
            add = nt.nodes.new("ShaderNodeMath")
            add.operation = "MULTIPLY_ADD"
            nt.links.new(sq.outputs[0], add.inputs[0])
            add.inputs[1].default_value = curve
            nt.links.new(sep.outputs["X"], add.inputs[2])
            nt.links.new(add.outputs[0], r.inputs["Value"])
        else:
            nt.links.new(sep.outputs["X"], r.inputs["Value"])
        return r.outputs["Result"]

    acro = material("M_C02_Spermium_Akrosom", (0.86, 0.85, 0.82), 1.38, 0.80, 0.18, sss=0.20, grain=0.06)
    nucleus = material("M_C02_Spermium_Kern", (0.55, 0.49, 0.40), 1.43, 0.08, 0.28, sss=0.92, grain=0.40)
    mid = material("M_C02_Spermium_Mittelstueck", (0.64, 0.59, 0.48), 1.40, 0.35, 0.32, sss=0.60)
    tail = material("M_C02_Spermium_Schwanz", (0.76, 0.74, 0.69), 1.38, 0.45, 0.28, sss=0.50)
    groups = []
    for src in (acro, nucleus, mid, tail):
        g = nt.nodes.new("ShaderNodeGroup")
        grp = bpy.data.node_groups.get("G_" + src.name) or bpy.data.node_groups.new("G_" + src.name, "ShaderNodeTree")
        grp.nodes.clear()
        grp.interface.clear()
        grp.interface.new_socket("BSDF", in_out="OUTPUT", socket_type="NodeSocketShader")
        go = grp.nodes.new("NodeGroupOutput")
        mapping = {}
        for n in src.node_tree.nodes:
            if n.bl_idname == "ShaderNodeOutputMaterial":
                continue
            c = grp.nodes.new(n.bl_idname)
            for prop in ("data_type", "blend_type", "interpolation_type", "clamp_result"):
                if hasattr(n, prop):
                    setattr(c, prop, getattr(n, prop))
            for i, inp in enumerate(n.inputs):
                if i < len(c.inputs) and hasattr(inp, "default_value") and hasattr(c.inputs[i], "default_value"):
                    try:
                        c.inputs[i].default_value = inp.default_value
                    except (TypeError, AttributeError):
                        pass
            mapping[n.name] = c
        for l in src.node_tree.links:
            if l.to_node.bl_idname == "ShaderNodeOutputMaterial":
                grp.links.new(mapping[l.from_node.name].outputs[l.from_socket.name], go.inputs[0])
            else:
                src_out = next(o for o in mapping[l.from_node.name].outputs if o.identifier == l.from_socket.identifier)
                dst_in = next(i for i in mapping[l.to_node.name].inputs if i.identifier == l.to_socket.identifier)
                grp.links.new(src_out, dst_in)
        g.node_tree = grp
        groups.append(g)
    # front 60 % of the head = acrosome; back of head = nucleus; neck..MID_END midpiece; rest tail
    m1 = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(region(-0.45, 0.35, curve=0.35), m1.inputs[0])   # 0 nucleus .. 1 acrosome: soft, curved cap edge
    nt.links.new(groups[1].outputs[0], m1.inputs[1])
    nt.links.new(groups[0].outputs[0], m1.inputs[2])
    m2 = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(region(NECK_END - 0.1, -HEAD_L / 2 + 0.05), m2.inputs[0])   # 0 midpiece .. 1 head
    nt.links.new(groups[2].outputs[0], m2.inputs[1])
    nt.links.new(m1.outputs[0], m2.inputs[2])
    m3 = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(region(MID_END - 0.4, MID_END + 0.2), m3.inputs[0])         # 0 tail .. 1 midpiece/head
    nt.links.new(groups[3].outputs[0], m3.inputs[1])
    nt.links.new(m2.outputs[0], m3.inputs[2])
    nt.links.new(m3.outputs[0], out.inputs["Surface"])
    return m


def bend(obj, phase=0.0):
    """One beat phase: travelling wave along the tail, amplitude growing to the tip."""
    for v in obj.data.vertices:
        s = NECK_END - v.co.x
        if s <= 0:
            continue
        a = TIP_AMPLITUDE * min(1.0, s / (NECK_END - TIP)) ** 1.3
        v.co.y += a * math.sin(2 * math.pi * s / WAVELENGTH - phase)
        v.co.z += 0.25 * a * math.sin(2 * math.pi * s / WAVELENGTH * 0.5 - phase)   # slight 3D component


def main():
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 0.01
    sc.unit_settings.length_unit = "MICROMETERS"
    col = bpy.data.collections.get("C02_SPERMIUM") or bpy.data.collections.new("C02_SPERMIUM")
    if col.name not in sc.collection.children:
        sc.collection.children.link(col)
    for n in ("SM_C02_Spermium", "SM_C02_Spermium_Pose"):
        if n in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[n])
    mat = head_material()
    obj = bpy.data.objects.new("SM_C02_Spermium", build_mesh("SM_C02_Spermium"))
    obj.data.materials.append(mat)
    col.objects.link(obj)
    pose = bpy.data.objects.new("SM_C02_Spermium_Pose", obj.data.copy())
    pose.data.name = "SM_C02_Spermium_Pose"
    bend(pose, 0.6)
    pose.location = (0, 12, 0)
    col.objects.link(pose)
    dims = obj.dimensions
    return {"verts": len(obj.data.vertices), "length_um": round(dims.x, 2), "head_w": round(dims.y, 2), "head_t": round(dims.z, 2)}


if __name__ == "__main__":
    print(main())
