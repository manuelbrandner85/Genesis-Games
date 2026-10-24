"""C00 (runs INSIDE Blender 5.2 after build_c00_bedroom.py, scene "C00_Schlafzimmer"): bedding, rain, exterior.

Regie 2026-10-25 ("Bettwaesche, Regen, Aussenansicht"):
- duvet 155 x 220 cm (German standard) dropped by cloth simulation onto mattress and pillows, then given
  its filling thickness and fine fabric creases
- rain on the outside of the window: a few thousand water drops (real refraction, IOR 1.33) of different
  sizes plus some run-down trails; thin rain streaks falling between the house and the street
- view out: dusk sky gradient, the apartment block across the street (4 storeys, plaster, some windows
  warmly lit behind curtains), a wet street with an LED street lamp
Origin and axes as in build_c00_bedroom.py (+X = window wall).
"""
import bmesh
import bpy
import math
import random
from mathutils import Vector

sc = bpy.data.scenes["C00_Schlafzimmer"]
col = bpy.data.collections["C00_Schlafzimmer"]
W, D, H = 3.60, 3.20, 2.55
WIN_W, WIN_H, SILL, WIN_Y = 1.50, 1.40, 0.85, 0.35
BX, BY0 = -0.25, D / 2 - 0.03
rng = random.Random(2610)


def sub(name):
    c = bpy.data.collections.get(name)
    if c:
        for o in list(c.all_objects):
            bpy.data.objects.remove(o, do_unlink=True)
    else:
        c = bpy.data.collections.new(name)
        col.children.link(c)
    return c


def mat(name, build):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(build(nt), out.inputs[0])
    return m


def principled(nt, color, rough, **kw):
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    for k, v in kw.items():
        b.inputs[k].default_value = v
    return b.outputs[0]


def emission(nt, color, strength):
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs[0].default_value = (*color, 1)
    e.inputs[1].default_value = strength
    return e.outputs[0]


def mesh_obj(name, bm, c, m, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    c.objects.link(o)
    me.materials.append(m)
    return o


def cube(bm, size, loc):
    r = bmesh.ops.create_cube(bm, size=1.0)
    for v in r["verts"]:
        v.co = Vector((v.co.x * size[0] + loc[0], v.co.y * size[1] + loc[1], v.co.z * size[2] + loc[2]))


# ------------------------------------------------------------------ bedding: cloth-simulated duvet
for n in ("SZ_Duvet", "SZ_DuvetCloth"):
    o = bpy.data.objects.get(n)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=78, y_segments=74, size=0.5)
waves = [(rng.uniform(4, 11), rng.uniform(3, 9), rng.uniform(0, 6.28), rng.uniform(0.01, 0.03)) for _ in range(6)]
for v in bm.verts:
    x, y = v.co.x * 1.55 * 1.06, v.co.y * 1.48
    v.co = Vector((x, y, sum(a * math.sin(fx * x + fy * y + ph) for fx, fy, ph, a in waves)))
duv = mesh_obj("SZ_DuvetCloth", bm, col, bpy.data.materials["M_SZ_BedLinenWhite"], smooth=True)
duv.location = (BX, BY0 - 0.10 - 2.0 + 0.76, 0.70)
duv.rotation_euler = (0, 0, math.radians(1.5))
for n in ("SZ_Mattress", "SZ_Pillow-0.36", "SZ_Pillow0.36", "SZ_BedBase", "SZ_Headboard"):
    c = bpy.data.objects[n]
    if not any(m.type == "COLLISION" for m in c.modifiers):
        c.modifiers.new("Collision", "COLLISION")
    c.collision.thickness_outer = 0.004
    c.collision.cloth_friction = 8
cl = duv.modifiers.new("Cloth", "CLOTH")
s = cl.settings
s.quality, s.mass, s.air_damping = 8, 0.6, 2
s.tension_stiffness = s.compression_stiffness = 12
s.shear_stiffness, s.bending_stiffness, s.shrink_min = 6, 0.6, 0.03
cl.collision_settings.use_self_collision = True
cl.collision_settings.distance_min = cl.collision_settings.self_distance_min = 0.004
cl.point_cache.frame_start, cl.point_cache.frame_end = 1, 80
sc.frame_start, sc.frame_end = 1, 80
for f in range(1, 81):
    sc.frame_set(f)
# freeze the simulated shape, then filling thickness and fabric creases
with bpy.context.temp_override(object=duv, active_object=duv, selected_objects=[duv], scene=sc):
    bpy.ops.object.modifier_apply(modifier="Cloth")
so = duv.modifiers.new("Puff", "SOLIDIFY")
so.thickness, so.offset, so.use_even_offset = 0.045, 1.0, True
sm = duv.modifiers.new("Smooth", "SUBSURF")
sm.levels = sm.render_levels = 1
crease = bpy.data.textures.get("TX_SZ_Crease") or bpy.data.textures.new("TX_SZ_Crease", "CLOUDS")
crease.noise_scale, crease.noise_depth, crease.noise_basis = 0.06, 2, "VORONOI_F2_F1"
dp = duv.modifiers.new("Creases", "DISPLACE")
dp.texture, dp.strength, dp.texture_coords = crease, 0.006, "GLOBAL"
for p in ("SZ_Pillow-0.36", "SZ_Pillow0.36"):
    o = bpy.data.objects[p]
    d = o.modifiers.get("Wrinkle") or o.modifiers.new("Wrinkle", "DISPLACE")
    d.texture, d.strength, d.texture_coords = crease, 0.008, "GLOBAL"
sc.frame_set(1)

# ------------------------------------------------------------------ rain on the window (outside surface)
rc = sub("C00_SZ_Regen")
def _water(nt):
    g = nt.nodes.new("ShaderNodeBsdfGlass")
    g.inputs["IOR"].default_value = 1.33
    g.inputs["Roughness"].default_value = 0.0
    return g.outputs[0]


water = mat("M_SZ_Water", _water)
GX = W / 2 + 0.06 + 0.004             # outer face of the panes
fr = 0.075
bm = bmesh.new()
n_drops = 0
for pane_y in (WIN_Y - WIN_W / 4, WIN_Y + WIN_W / 4):
    half = WIN_W / 4 - fr * 0.6
    for _ in range(1600):
        r = min(0.0045, rng.lognormvariate(math.log(0.0011), 0.55))
        y = pane_y + rng.uniform(-half, half)
        z = SILL + fr + rng.uniform(0, WIN_H - 2 * fr)
        ico = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        stretch = 1.0 + (rng.random() < 0.15) * rng.uniform(0.3, 1.2)       # some drops start to run
        for v in ico["verts"]:
            v.co = Vector((GX + max(0.0, v.co.x) * r * 0.45, y + v.co.y * r, z + v.co.z * r * stretch))
        n_drops += 1
    for _ in range(14):                                                        # run-down trails
        y = pane_y + rng.uniform(-half, half)
        z0 = SILL + fr + rng.uniform(0.3, WIN_H - 2 * fr)
        length = rng.uniform(0.08, 0.35)
        steps = int(length / 0.004)
        for k in range(steps):
            t = k / steps
            r = 0.0007 + 0.0012 * t
            ico = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
            yy = y + 0.004 * math.sin(k * 0.35 + y * 50)
            for v in ico["verts"]:
                v.co = Vector((GX + max(0.0, v.co.x) * r * 0.4, yy + v.co.y * r, z0 - t * length + v.co.z * r * 1.6))
mesh_obj("SZ_RainDrops", bm, rc, water, smooth=True)

# falling rain streaks outside (thin water cylinders, motion-blur length)
bm = bmesh.new()
for _ in range(900):
    x = rng.uniform(W / 2 + 0.6, W / 2 + 12.0)
    y = rng.uniform(-6, 7)
    z = rng.uniform(-3.0, 6.0)
    length = rng.uniform(0.25, 0.45)
    c = bmesh.ops.create_cone(bm, cap_ends=False, segments=4, radius1=0.0012, radius2=0.0012, depth=length)
    for v in c["verts"]:
        v.co = Vector((v.co.x + x, v.co.y + y + v.co.z * 0.08, v.co.z + z))
def _streak(nt):
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.1
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = 0.35
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(gl.outputs[0], mix.inputs[2])
    return mix.outputs[0]


streak = mat("M_SZ_RainStreak", _streak)
mesh_obj("SZ_RainStreaks", bm, rc, streak)
# the window pane: no more fake drop bump, the drops are real geometry now
g = bpy.data.materials["M_SZ_Glass"]
for n in g.node_tree.nodes:
    if n.type == "BUMP":
        n.inputs["Strength"].default_value = 0.0

# ------------------------------------------------------------------ exterior: dusk, house across the street, street
ec = sub("C00_SZ_Aussen")
for n in ("SZ_DuskSky",):
    o = bpy.data.objects.get(n)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
FLOOR_Z = -3.0 * 2 - 0.5               # the flat is on the 2nd upper floor: street level about 6.5 m below


def _sky(nt):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[0].color = 0.0, (0.11, 0.09, 0.12, 1)   # city glow at the horizon
    ramp.color_ramp.elements[1].position, ramp.color_ramp.elements[1].color = 1.0, (0.012, 0.022, 0.055, 1)  # deep blue
    e = ramp.color_ramp.elements.new(0.35)
    e.color = (0.04, 0.06, 0.12, 1)
    nt.links.new(sep.outputs["Z"], ramp.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[1].default_value = 1.0
    nt.links.new(ramp.outputs[0], em.inputs[0])
    return em.outputs[0]


bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
for v in bm.verts:
    v.co = Vector((W / 2 + 40.0, v.co.x * 60.0, 8.0 + v.co.y * 25.0))
bm.faces.ensure_lookup_table()
mesh_obj("SZ_DuskSky", bm, ec, mat("M_SZ_DuskSky", _sky))

plaster = mat("M_SZ_FacadePlaster", lambda nt: principled(nt, (0.30, 0.29, 0.27), 0.85))
roof = mat("M_SZ_RoofDark", lambda nt: principled(nt, (0.04, 0.04, 0.045), 0.6))
win_dark = mat("M_SZ_FacadeGlassDark", lambda nt: principled(nt, (0.01, 0.012, 0.016), 0.05, **{"Specular IOR Level": 0.8}))
win_warm = mat("M_SZ_FacadeWindowWarm", lambda nt: emission(nt, (1.0, 0.62, 0.30), 3.5))
win_cool = mat("M_SZ_FacadeWindowTV", lambda nt: emission(nt, (0.45, 0.55, 1.0), 1.2))
asphalt = mat("M_SZ_WetAsphalt", lambda nt: principled(nt, (0.02, 0.02, 0.022), 0.08))
pole_m = mat("M_SZ_LampPole", lambda nt: principled(nt, (0.05, 0.05, 0.05), 0.4, **{"Metallic": 1.0}))
led_m = mat("M_SZ_StreetLED", lambda nt: emission(nt, (1.0, 0.85, 0.65), 25.0))

HX = W / 2 + 18.0                       # facade of the house across the street (street 12 m + front yards)
bm_f, bm_d, bm_w, bm_c, bm_r = bmesh.new(), bmesh.new(), bmesh.new(), bmesh.new(), bmesh.new()
cube(bm_f, (1.0, 34.0, 15.5), (HX + 0.5, 1.0, FLOOR_Z + 7.75))
cube(bm_r, (1.6, 34.4, 0.4), (HX + 0.4, 1.0, FLOOR_Z + 15.7))
storey, nwin = 3.0, 11
for fl_i in range(5):
    for k in range(nwin):
        y = 1.0 - 15.0 + k * 3.0
        z = FLOOR_Z + 1.0 + fl_i * storey + 0.9 + 0.7
        roll = rng.random()
        target = bm_w if roll < 0.28 else (bm_c if roll < 0.33 else bm_d)
        cube(target, (0.05, 1.3, 1.4), (HX - 0.01, y, z))
        cube(bm_r, (0.12, 1.4, 0.05), (HX - 0.06, y, z - 0.72))        # sills
mesh_obj("SZ_FacadeHouse", bm_f, ec, plaster)
mesh_obj("SZ_FacadeRoofSills", bm_r, ec, roof)
mesh_obj("SZ_FacadeWindowsDark", bm_d, ec, win_dark)
mesh_obj("SZ_FacadeWindowsWarm", bm_w, ec, win_warm)
mesh_obj("SZ_FacadeWindowsTV", bm_c, ec, win_cool)
bm = bmesh.new()
cube(bm, (24.0, 60.0, 0.1), (W / 2 + 10.0, 1.0, FLOOR_Z - 0.05))
mesh_obj("SZ_StreetWet", bm, ec, asphalt)
# own house facade below/around the window from outside is not visible; street lamp on the near pavement
LX, LY = W / 2 + 4.0, -2.5
bm = bmesh.new()
c = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.07, radius2=0.05, depth=7.0)
for v in c["verts"]:
    v.co += Vector((LX, LY, FLOOR_Z + 3.5))
cube(bm, (0.9, 0.12, 0.08), (LX + 0.45, LY, FLOOR_Z + 7.0))
mesh_obj("SZ_StreetLampPole", bm, ec, pole_m)
bm = bmesh.new()
cube(bm, (0.5, 0.18, 0.02), (LX + 0.7, LY, FLOOR_Z + 6.95))
mesh_obj("SZ_StreetLampLED", bm, ec, led_m)
sl = bpy.data.lights.new("SZ_StreetLight", "SPOT")
sl.energy, sl.spot_size, sl.spot_blend, sl.color = 3000, math.radians(120), 0.6, (1.0, 0.85, 0.65)
slo = bpy.data.objects.new("SZ_StreetLight", sl)
ec.objects.link(slo)
slo.location = (LX + 0.7, LY, FLOOR_Z + 6.9)

result = {"drops": n_drops, "duvet_verts": len(duv.data.vertices)}
