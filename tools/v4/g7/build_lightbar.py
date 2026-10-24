"""G7 (runs INSIDE Blender 5.2): build SM_R03_LightBar, the LED batten hanging over the workbench.

Measure sheet docs/design/G7_FLUSSDORF_ASSETS.md: 1500 x 60 x 40 mm aluminium profile with opal diffuser,
hanging on two chains (600 mm) with ceiling hooks and a supply cable. Origin at the ceiling (top of
the hooks), so the asset is placed against the ceiling and the bar hangs 600 mm lower.
The real light source (4000 K, ~4000 lm) is a Rect Light added in Unreal at SOCKET_Light.
"""
import bpy, bmesh, math, os
from mathutils import Vector

NAME = "SM_R03_LightBar"
COL = "G7_LightBar"
exec(compile(open(os.path.join(os.path.dirname(__file__), "g7_common.py"), encoding="utf8").read(), "g7_common.py", "exec"))

sc = bpy.context.scene
col = bpy.data.collections.get(COL)
if col:
    for o in list(col.all_objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    col = bpy.data.collections.new(COL)
    sc.collection.children.link(col)
for m in [m for m in bpy.data.materials if m.name.startswith("M_LB_")]:
    bpy.data.materials.remove(m)


def diffuser(name):
    """Opal polycarbonate cover: light-scattering white, emissive in Unreal via its own slot."""
    mat = simple_mat(name, (0.80, 0.80, 0.78), 0.35, rough_var=0.05, bump=0.01, grime=0.4)
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Coat Weight"].default_value = 0.3                          # glossy PC skin over the milky body
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.93, 0.84, 1.0)     # ~4000 K
    bsdf.inputs["Emission Strength"].default_value = 0.0                      # off in the look-dev
    return mat


M = {
    "alu": simple_mat("M_LB_AluAnodised", (0.80, 0.80, 0.79), 0.38, metal=1.0, rough_var=0.06, bump=0.02, grime=0.6),
    "diffuser": diffuser("M_LB_Diffuser"),
    "endcap": simple_mat("M_LB_EndCapGrey", (0.30, 0.30, 0.30), 0.55, rough_var=0.08, bump=0.03),
    "chain": simple_mat("M_LB_ChainZinc", (0.58, 0.59, 0.60), 0.42, metal=1.0, rough_var=0.12, bump=0.05),
    "cable": simple_mat("M_LB_CableWhite", (0.62, 0.62, 0.60), 0.50, rough_var=0.08, bump=0.02, grime=0.7),
}

L, DROP = 1.50, 0.60
BZ = -DROP - 0.02                        # bar centre below the ceiling (origin)
parts = [box("Profile", (L, 0.06, 0.028), (0, 0, BZ + 0.006), "alu", bevel=0.002),
         box("Diffuser", (L - 0.01, 0.054, 0.016), (0, 0, BZ - 0.014), "diffuser", bevel=0.006)]
for s in (-1, 1):
    parts.append(box(f"EndCap_{s}", (0.008, 0.062, 0.042), (s * (L / 2 + 0.004), 0, BZ), "endcap", bevel=0.003))
    parts.append(box(f"Clip_{s}", (0.03, 0.064, 0.004), (s * 0.55, 0, BZ + 0.021), "chain", bevel=0.0008))

# chains: 2.5 mm wire, 20 mm links, alternating orientation
def chain(x):
    n = int((DROP - 0.03) / 0.017)
    for k in range(n):
        z = -0.03 - k * 0.017
        bm = bmesh.new()
        seg, R, r = 16, 0.0065, 0.00125
        for i in range(seg):
            a = 2 * math.pi * i / seg
            c = Vector((0, R * math.cos(a) * 0.6, R * math.sin(a) * 1.4))
            for j in range(6):
                b = 2 * math.pi * j / 6
                n_ = Vector((0, math.cos(a), math.sin(a)))
                bm.verts.new(c + (n_ * math.cos(b) + Vector((1, 0, 0)) * math.sin(b)) * r)
        bm.verts.ensure_lookup_table()
        for i in range(seg):
            for j in range(6):
                a1, a2 = i * 6 + j, i * 6 + (j + 1) % 6
                b1, b2 = ((i + 1) % seg) * 6 + j, ((i + 1) % seg) * 6 + (j + 1) % 6
                bm.faces.new((bm.verts[a1], bm.verts[b1], bm.verts[b2], bm.verts[a2]))
        parts.append(_obj(f"Chain_{x:+.2f}_{k}", bm, "chain", (x, 0, z), (0, 0, (k % 2) * math.pi / 2)))
    # ceiling hook
    parts.append(cyl(f"Hook_Plate_{x:+.2f}", 0.018, 0.004, (x, 0, -0.002), "chain", verts=24, bevel=0.0008))
    parts.append(tube(f"Hook_{x:+.2f}", [Vector((x, 0, -0.004)), Vector((x, 0, -0.018)), Vector((x, 0.008, -0.026)),
                                         Vector((x, 0.0, -0.032)), Vector((x, -0.006, -0.026))], 0.0022, "chain", res=3))


for s in (-1, 1):
    chain(s * 0.55)
# supply cable from the right end up to the ceiling, hanging in a soft curve
parts.append(tube("Cable", [Vector((L / 2 + 0.008, 0, BZ)), Vector((L / 2 + 0.05, 0.0, BZ + 0.05)),
                            Vector((L / 2 + 0.09, 0.01, -0.35)), Vector((L / 2 + 0.11, 0.0, -0.08)),
                            Vector((L / 2 + 0.11, 0.0, -0.004))], 0.0035, "cable"))
parts.append(cyl("Cable_Rose", 0.03, 0.012, (L / 2 + 0.11, 0, -0.006), "cable", verts=32, bevel=0.003))

bar = join_parts(NAME, parts)
collision_box(NAME + "_00", (L + 0.02, 0.07, 0.05), (0, 0, BZ), bar)
s = bpy.data.objects.new("SOCKET_Light", None)
s.empty_display_type = "SINGLE_ARROW"
s.location = (0, 0, BZ - 0.023)
s.rotation_euler = (math.pi, 0, 0)                 # pointing down
col.objects.link(s)
s.parent = bar
smart_uv(bar)
bar.location = (0.0, -0.9, 2.4)            # hang above the look-dev floor
bb = [bar.matrix_world @ Vector(c) for c in bar.bound_box]
dims = [round(max(v[i] for v in bb) - min(v[i] for v in bb), 4) for i in range(3)]
result = {"object": NAME, "dims_m": dims, "tris": sum(len(p.vertices) - 2 for p in bar.data.polygons),
          "materials": [m.name for m in bar.data.materials]}
print("G7_LIGHTBAR", result)
