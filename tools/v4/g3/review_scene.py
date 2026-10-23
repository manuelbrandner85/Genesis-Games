"""G3 review scene: the pallet with its BAKED Unreal textures on a concrete yard slab.

Used for the reality check of the asset hand-off. Call `build(asset_dir)` inside Blender after
the master was built (visible session over MCP, or `blender -b --python` with a wrapper).
Everything here is review dressing and is never exported with the asset.
"""
import math

import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector
from mathutils import noise as mathnoise

ASSET = "SM_TechSmoke_PalletEUR"
RNG = np.random.default_rng(2026)


def nd(nt, kind, loc, **props):
    n = nt.nodes.new(kind)
    n.location = loc
    for k, v in props.items():
        setattr(n, k, v)
    return n


def baked_material(asset_dir):
    """Principled material from the exported textures; DirectX normal converted back to OpenGL."""
    m = bpy.data.materials.new("M_TechSmoke_PalletBaked")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    L = nt.links.new
    out = nd(nt, "ShaderNodeOutputMaterial", (900, 0))
    b = nd(nt, "ShaderNodeBsdfPrincipled", (600, 0))
    L(b.outputs[0], out.inputs[0])

    def img(suffix, cs, y):
        n = nd(nt, "ShaderNodeTexImage", (-600, y))
        n.image = bpy.data.images.load(str(asset_dir / "Textures" / f"T_{ASSET}_{suffix}.png"), check_existing=False)
        n.image.colorspace_settings.name = cs
        return n

    L(img("BC", "sRGB", 300).outputs["Color"], b.inputs["Base Color"])
    so = nd(nt, "ShaderNodeSeparateColor", (-300, 0))
    L(img("ORM", "Non-Color", 0).outputs["Color"], so.inputs[0])
    L(so.outputs["Green"], b.inputs["Roughness"])
    L(so.outputs["Blue"], b.inputs["Metallic"])
    sn = nd(nt, "ShaderNodeSeparateColor", (-300, -300))
    L(img("N", "Non-Color", -300).outputs["Color"], sn.inputs[0])
    inv = nd(nt, "ShaderNodeMath", (-120, -340), operation="SUBTRACT")
    inv.inputs[0].default_value = 1.0
    L(sn.outputs["Green"], inv.inputs[1])
    cn = nd(nt, "ShaderNodeCombineColor", (60, -300))
    L(sn.outputs["Red"], cn.inputs[0]); L(inv.outputs[0], cn.inputs[1]); L(sn.outputs["Blue"], cn.inputs[2])
    nm = nd(nt, "ShaderNodeNormalMap", (300, -300), uv_map="UVMap")
    L(cn.outputs[0], nm.inputs["Color"]); L(nm.outputs[0], b.inputs["Normal"])
    b.inputs["IOR"].default_value = 1.5
    return m


def concrete_material():
    """Broom-finished yard slab: cloudy cement tone, aggregate, stains, saw-cut joints every 4 m."""
    m = bpy.data.materials.new("M_Review_Concrete")
    m.use_nodes = True
    ft = m.node_tree
    ft.nodes.clear()
    L = ft.links.new
    o = nd(ft, "ShaderNodeOutputMaterial", (1400, 0))
    p = nd(ft, "ShaderNodeBsdfPrincipled", (1100, 0))
    L(p.outputs[0], o.inputs[0])
    tc = nd(ft, "ShaderNodeTexCoord", (-1200, 0))
    sep = nd(ft, "ShaderNodeSeparateXYZ", (-1000, -500))
    L(tc.outputs["Object"], sep.inputs[0])

    def noise(loc, scale, detail, vec=None):
        n = nd(ft, "ShaderNodeTexNoise", loc)
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        L(vec or tc.outputs["Object"], n.inputs["Vector"])
        return n

    def mr(loc, src, a, b, c=0.0, d=1.0, smooth=False):
        n = nd(ft, "ShaderNodeMapRange", loc, interpolation_type="SMOOTHSTEP" if smooth else "LINEAR")
        for k, v in (("From Min", a), ("From Max", b), ("To Min", c), ("To Max", d)):
            n.inputs[k].default_value = v
        L(src, n.inputs["Value"])
        return n.outputs["Result"]

    def mix(loc, fac, a, b, blend="MIX"):
        n = nd(ft, "ShaderNodeMix", loc, data_type="RGBA", blend_type=blend)
        for sock, v in (("Factor", fac), ("A", a), ("B", b)):
            if isinstance(v, (int, float)):
                n.inputs[sock].default_value = v
            elif isinstance(v, tuple):
                n.inputs[sock].default_value = (*v, 1.0)
            else:
                L(v, n.inputs[sock])
        return n.outputs["Result"]

    big, stn, fine = noise((-800, 300), 0.35, 6), noise((-800, 50), 1.8, 4), noise((-800, -200), 260, 8)
    brush_v = nd(ft, "ShaderNodeVectorMath", (-950, -350), operation="MULTIPLY")
    brush_v.inputs[1].default_value = (1.0, 60.0, 1.0)
    L(tc.outputs["Object"], brush_v.inputs[0])
    brush = noise((-800, -350), 4.0, 3, brush_v.outputs["Vector"])
    agg = nd(ft, "ShaderNodeTexVoronoi", (-800, -500))
    agg.inputs["Scale"].default_value = 180
    L(tc.outputs["Object"], agg.inputs["Vector"])
    c = mix((-300, 300), mr((-550, 300), big.outputs["Fac"], 0.3, 0.7), (0.17, 0.165, 0.155), (0.32, 0.31, 0.295))
    # Mid-scale mottling (curing, wear) and dark tyre/traffic grime - a yard slab is never even.
    mott = noise((-800, 650), 5.0, 6)
    c = mix((-200, 450), mr((-550, 650), mott.outputs["Fac"], 0.35, 0.65, 0.0, 0.3), c, (0.16, 0.155, 0.145))
    lane_v = nd(ft, "ShaderNodeVectorMath", (-950, 850), operation="MULTIPLY")
    lane_v.inputs[1].default_value = (0.08, 2.5, 1.0)
    L(tc.outputs["Object"], lane_v.inputs[0])
    lane = noise((-800, 850), 1.0, 4, lane_v.outputs["Vector"])
    c = mix((-150, 600), mr((-550, 850), lane.outputs["Fac"], 0.58, 0.72, 0.0, 0.35, True), c, (0.10, 0.095, 0.09))
    stain = mr((-550, 50), stn.outputs["Fac"], 0.6, 0.8, 0.0, 0.22, True)
    c = mix((-100, 300), stain, c, (0.11, 0.10, 0.09))
    c = mix((100, 300), 0.3, c, fine.outputs["Color"], "MULTIPLY")
    c = mix((250, 300), 0.12, c, brush.outputs["Color"], "MULTIPLY")
    aggm = mr((-550, -500), agg.outputs["Distance"], 0.0, 0.25, 0.12, 0.0)
    c = mix((400, 300), aggm, c, (0.42, 0.41, 0.39), "LIGHTEN")
    # Micro: air pores (small dark pits) and fine sand grain - visible from about 1 m.
    pores = nd(ft, "ShaderNodeTexVoronoi", (-800, -900))
    pores.inputs["Scale"].default_value = 700.0
    L(tc.outputs["Object"], pores.inputs["Vector"])
    pore_pick = nd(ft, "ShaderNodeSeparateColor", (-650, -1000))
    L(pores.outputs["Color"], pore_pick.inputs[0])
    pore_sel = nd(ft, "ShaderNodeMath", (-500, -1000), operation="GREATER_THAN")
    L(pore_pick.outputs["Red"], pore_sel.inputs[0]); pore_sel.inputs[1].default_value = 0.8
    pore_core = mr((-500, -900), pores.outputs["Distance"], 0.18, 0.08)
    pore = nd(ft, "ShaderNodeMath", (-350, -950), operation="MULTIPLY")
    L(pore_core, pore.inputs[0]); L(pore_sel.outputs[0], pore.inputs[1])
    c = mix((450, 450), pore.outputs[0], c, (0.06, 0.058, 0.055))
    sand = noise((-800, -1150), 1400.0, 2)
    c = mix((500, 300), 0.18, c, sand.outputs["Color"], "MULTIPLY")
    joints = []
    for i, axis in enumerate(("X", "Y")):
        pp = nd(ft, "ShaderNodeMath", (-300 + 300 * i, -700), operation="PINGPONG")
        L(sep.outputs[axis], pp.inputs[0])
        pp.inputs[1].default_value = 2.0
        joints.append(mr((-150 + 300 * i, -700), pp.outputs[0], 0.0025, 0.004, 1.0, 0.0))
    j = nd(ft, "ShaderNodeMath", (300, -700), operation="MAXIMUM")
    L(joints[0], j.inputs[0]); L(joints[1], j.inputs[1])
    L(mix((600, 300), j.outputs[0], c, (0.06, 0.055, 0.05)), p.inputs["Base Color"])
    rs = nd(ft, "ShaderNodeMath", (800, 0), operation="SUBTRACT", use_clamp=True)
    L(mr((600, 0), fine.outputs["Fac"], 0.0, 1.0, 0.6, 0.9), rs.inputs[0]); L(stain, rs.inputs[1])
    L(rs.outputs[0], p.inputs["Roughness"])
    h = nd(ft, "ShaderNodeMath", (600, -400), operation="MULTIPLY_ADD")
    L(fine.outputs["Fac"], h.inputs[0]); h.inputs[1].default_value = 0.4; L(aggm, h.inputs[2])
    h1 = nd(ft, "ShaderNodeMath", (680, -500), operation="MULTIPLY_ADD")
    L(sand.outputs["Fac"], h1.inputs[0]); h1.inputs[1].default_value = 0.5; L(h.outputs[0], h1.inputs[2])
    hp = nd(ft, "ShaderNodeMath", (720, -600), operation="SUBTRACT")
    L(h1.outputs[0], hp.inputs[0]); L(pore.outputs[0], hp.inputs[1])
    h2 = nd(ft, "ShaderNodeMath", (750, -400), operation="SUBTRACT")
    L(hp.outputs[0], h2.inputs[0]); L(j.outputs[0], h2.inputs[1])
    bu = nd(ft, "ShaderNodeBump", (900, -400))
    bu.inputs["Strength"].default_value = 0.35
    bu.inputs["Distance"].default_value = 0.002
    L(h2.outputs[0], bu.inputs["Height"]); L(bu.outputs[0], p.inputs["Normal"])
    return m


def simple_material(name, base, rough, var):
    """Per-object tinted material for debris (Object Info random drives tone variation)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    info = nd(nt, "ShaderNodeObjectInfo", (-600, 200))
    mixn = nd(nt, "ShaderNodeMix", (-300, 200), data_type="RGBA")
    mixn.inputs["A"].default_value = (*[c * (1 - var) for c in base], 1.0)
    mixn.inputs["B"].default_value = (*[min(c * (1 + var), 1.0) for c in base], 1.0)
    nt.links.new(info.outputs["Random"], mixn.inputs["Factor"])
    nt.links.new(mixn.outputs["Result"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    return m


def scatter_debris(floor_z=0.0):
    """Loose gravel grains, wood splinters and chips near the pallet - what really lies in a yard."""
    coll = bpy.data.collections.new("Review_Debris")
    bpy.context.scene.collection.children.link(coll)
    stone = simple_material("M_Review_Gravel", (0.19, 0.18, 0.165), 0.9, 0.45)
    wood = simple_material("M_Review_Splinter", (0.27, 0.22, 0.16), 0.82, 0.3)
    stones = 0
    for i in range(420):
        # Grit collects where things are moved and where it gets trapped: around the pallet
        # footprint and along the saw-cut joints; little lies on the open slab.
        kind = RNG.random()
        if kind < 0.55:
            side = RNG.integers(4)
            d = abs(RNG.normal(0, 0.12))
            x, y = (RNG.uniform(-0.62, 0.62), (0.42 + d) * (1 if side == 0 else -1)) if side < 2 else ((0.62 + d) * (1 if side == 2 else -1), RNG.uniform(-0.42, 0.42))
        elif kind < 0.85:
            if RNG.random() < 0.5:
                x, y = -0.9 + RNG.normal(0, 0.02), RNG.uniform(-2.0, 2.5)
            else:
                x, y = RNG.uniform(-2.5, 2.5), 1.25 + RNG.normal(0, 0.02)
        else:
            x, y = RNG.uniform(-2.5, 2.5), RNG.uniform(-2.0, 2.5)
        if abs(x) < 0.62 and abs(y) < 0.42:
            continue
        size = RNG.lognormal(math.log(0.0022), 0.55)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.0, location=(x, y, floor_z))
        ob = bpy.context.active_object
        # Crushed grit: irregular, with broad flat-ish facets - 3D noise displacement plus a
        # few planar cuts, smooth shaded so it is not low-poly.
        seed = Vector(RNG.uniform(-50, 50, 3))
        planes = [Vector(RNG.normal(0, 1, 3)).normalized() for _ in range(3)]
        cuts = RNG.uniform(0.55, 0.85, 3)
        for v in ob.data.vertices:
            v.co *= 1.0 + 0.35 * mathnoise.noise(v.co * 1.6 + seed)
            for pn, c in zip(planes, cuts):
                d = v.co.dot(pn)
                if d > c:
                    v.co -= pn * (d - c)
        for p in ob.data.polygons:
            p.use_smooth = True
        ob.scale = (size * RNG.uniform(0.8, 1.3), size * RNG.uniform(0.7, 1.1), size * RNG.uniform(0.45, 0.7))
        ob.rotation_euler = Euler(RNG.uniform(0, math.tau, 3))
        ob.location.z = floor_z + ob.scale.z * 0.55
        ob.data.materials.append(stone)
        ob.name = f"Gravel_{i:03d}"
        for c in ob.users_collection:
            c.objects.unlink(ob)
        coll.objects.link(ob)
        stones += 1
    splinters = 0
    for i in range(26):
        side = RNG.choice((-1, 1))
        x = RNG.uniform(-0.75, 0.75)
        y = side * RNG.uniform(0.43, 0.75)
        if RNG.random() < 0.4:
            x, y = side * RNG.uniform(0.63, 0.9), RNG.uniform(-0.5, 0.5)
        length, width, thick = RNG.uniform(0.012, 0.07), RNG.uniform(0.002, 0.007), RNG.uniform(0.0008, 0.002)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, floor_z + thick / 2))
        ob = bpy.context.active_object
        for v in ob.data.vertices:          # torn splinters taper to a point at one end
            if v.co.x > 0:
                v.co.y *= RNG.uniform(0.1, 0.35)
                v.co.z *= 0.5
        ob.scale = (length, width, thick)
        ob.rotation_euler = (0.0, RNG.normal(0, 0.05), RNG.uniform(0, math.tau))
        ob.data.materials.append(wood)
        ob.name = f"Splinter_{i:02d}"
        for c in ob.users_collection:
            c.objects.unlink(ob)
        coll.objects.link(ob)
        splinters += 1
    return {"gravel": stones, "splinters": splinters}


def detail_camera(target=(0.52, -0.36, 0.07), eye=(0.98, -0.95, 0.42), lens=50.0, fstop=5.6):
    """Second camera for the 100 % check of a corner: block, board ends, nails, breaks."""
    cam_d = bpy.data.cameras.get("Review_Detail") or bpy.data.cameras.new("Review_Detail")
    cam = bpy.data.objects.get("Review_Detail") or bpy.data.objects.new("Review_Detail", cam_d)
    if cam.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(cam)
    cam_d.lens, cam_d.sensor_width = lens, 36.0
    cam_d.dof.use_dof, cam_d.dof.aperture_fstop = True, fstop
    cam.location = eye
    d = Vector(target) - Vector(eye)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam_d.dof.focus_distance = d.length
    return cam


def build(asset_dir, pallet):
    sc = bpy.context.scene
    pallet.data.materials.clear()
    pallet.data.materials.append(baked_material(asset_dir))
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(-0.9, 1.25, 0.0))
    floor = bpy.context.active_object
    floor.name = "Review_Floor"
    for v in floor.data.vertices:
        v.co.x *= 60.0
        v.co.y *= 60.0
    floor.data.materials.append(concrete_material())
    debris = scatter_debris()

    w = bpy.data.worlds.new("Review_Sky")
    sc.world = w
    w.use_nodes = True
    wt = w.node_tree
    wt.nodes.clear()
    sky = nd(wt, "ShaderNodeTexSky", (0, 0), sky_type="MULTIPLE_SCATTERING")
    sky.sun_elevation = math.radians(38)
    sky.sun_rotation = math.radians(215)
    bg = nd(wt, "ShaderNodeBackground", (250, 0))
    wo = nd(wt, "ShaderNodeOutputWorld", (450, 0))
    wt.links.new(sky.outputs[0], bg.inputs[0]); wt.links.new(bg.outputs[0], wo.inputs[0])

    cam_d = bpy.data.cameras.new("Review_Cam")
    cam = bpy.data.objects.new("Review_Cam", cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam_d.lens, cam_d.sensor_width = 50.0, 36.0
    cam_d.dof.use_dof, cam_d.dof.aperture_fstop = True, 8.0
    cam.location = (1.75, -1.95, 1.45)
    d = Vector((0.0, 0.02, 0.06)) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam_d.dof.focus_distance = d.length

    sc.render.engine = "CYCLES"
    sc.cycles.device = "GPU"
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.01
    sc.cycles.samples = 1024
    sc.cycles.use_denoising = True
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.exposure = -4.7          # measured: concrete mid-tone ~0.5 display value
    return debris
