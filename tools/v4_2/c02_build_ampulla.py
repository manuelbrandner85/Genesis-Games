"""CR-001 Phase 3 (runs inside Blender 5.2): tileable segment of the human fallopian tube (ampulla) with its
branched longitudinal mucosal folds, after docs/v4_2/C02_MASSBLATT.md (1 Blender unit = 1 um).

SM_C02_Eileiter: inner surface of a tube segment, 1400 um long (periodic along X, so segments chain without a
seam), lumen radius 520 um. 22 primary folds (plates 40-80 um thick, 140-320 um high) and low secondary ridges meander gently along
the tube; each carries side folds that branch off and rejoin, as in the ampulla's labyrinth. The geometry is a
radial displacement of a dense tube (ridges as narrow plates); epithelial cells and cilia are surface detail
(material), not geometry. Normals face the lumen (camera inside).
"""
import math
import random

import bmesh
import bpy

LENGTH = 1400.0
RADIUS = 520.0
SEG_THETA = 960               # ~3.4 um around the circumference
SEG_X = 160                   # ~8.8 um along the tube


def folds(seed=11):
    """22 primary folds (40-80 um thick, 140-320 um high: the labyrinth leaves a lumen of ~0.2-0.4 mm), each with
    2-4 side folds, plus low secondary ridges on the wall between them."""
    rnd = random.Random(seed)
    out = []
    for k in range(22):
        base = 2 * math.pi * k / 22 + rnd.uniform(-0.06, 0.06)
        out.append({
            "theta": base,
            "meander": rnd.uniform(0.02, 0.06), "phase": rnd.uniform(0, 2 * math.pi), "waves": rnd.choice((1, 2)),
            "height": rnd.uniform(140.0, 320.0), "thick": rnd.uniform(40.0, 80.0),
            "hwaves": rnd.choice((1, 2, 3)), "hphase": rnd.uniform(0, 2 * math.pi),
            "lean": rnd.uniform(-0.38, 0.38), "lwaves": rnd.choice((1, 2)), "lphase": rnd.uniform(0, 2 * math.pi),
            "branches": [{"side": rnd.choice((-1, 1)), "x0": rnd.uniform(0, LENGTH), "span": rnd.uniform(450, 800),
                          "spread": rnd.uniform(50.0, 120.0), "height": rnd.uniform(0.45, 0.7)} for _ in range(rnd.randint(2, 4))],
        })
    for k in range(40):                                  # low secondary ridges
        out.append({
            "theta": rnd.uniform(0, 2 * math.pi), "meander": rnd.uniform(0.02, 0.05), "phase": rnd.uniform(0, 2 * math.pi),
            "waves": rnd.choice((1, 2, 3)), "height": rnd.uniform(25.0, 60.0), "thick": rnd.uniform(18.0, 30.0),
            "hwaves": rnd.choice((2, 3, 4)), "hphase": rnd.uniform(0, 2 * math.pi), "branches": [],
            "lean": 0.0, "lwaves": 1, "lphase": 0.0,
        })
    return out


def ridge(d_arc, thick):
    """Cross-section of one fold: a plate with a rounded crest and a broader base (1 at the centre line)."""
    a = abs(d_arc) / (thick * 0.5)
    return (1.0 - a ** 3.0) ** 0.45 if a < 1.0 else 0.0           # flatter, rounder crest than a blade


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def depth(theta, x, F):
    """How far the mucosa reaches into the lumen at (theta, x): union (max) of all folds and side folds.
    Returns (depth, lean): lean of the fold that wins here - folds bend over to one side, as soft tissue does."""
    best, wsum, lsum = 0.0, 0.0, 0.0
    u = 2 * math.pi * x / LENGTH                       # periodic along X -> tileable segment
    for f in F:
        c = f["theta"] + f["meander"] * math.sin(f["waves"] * u + f["phase"])
        h = f["height"] * (0.8 + 0.2 * math.sin(f["hwaves"] * u + f["hphase"]))
        v = h * ridge(wrap(theta - c) * RADIUS, f["thick"])
        fl = f["lean"] * math.sin(f["lwaves"] * u + f["lphase"])
        best = max(best, v)
        wsum += v * v
        lsum += v * v * fl
        for b in f["branches"]:
            t = ((x - b["x0"]) % LENGTH) / b["span"]     # 0..1 over the branch, periodic
            if t > 1.0:
                continue
            off = b["side"] * b["spread"] * math.sin(math.pi * t)       # leaves the fold and rejoins it
            hb = h * b["height"] * math.sin(math.pi * t) ** 0.8          # side folds rise and sink gently
            v = hb * ridge(wrap(theta - c) * RADIUS - off, f["thick"] * 0.8)
            best = max(best, v)
            wsum += v * v
            lsum += v * v * fl * 0.7
    # lean blended by each fold's share: where a side fold merges into its fold the lean changes smoothly
    # (winner-takes-all made the vertices jump sideways and tore the mesh)
    return best, (lsum / wsum if wsum > 0.0 else 0.0)


def build():
    F = folds()
    me = bpy.data.meshes.new("SM_C02_Eileiter")
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    grid = []
    for i in range(SEG_X + 1):
        x = LENGTH * i / SEG_X
        row = []
        for j in range(SEG_THETA):
            th = 2 * math.pi * j / SEG_THETA
            d, lean = depth(th, x, F)
            r = RADIUS - d
            tl = th + lean * (d / RADIUS) ** 1.5            # the higher the tissue, the further it leans over
            row.append(bm.verts.new((x, r * math.cos(tl), r * math.sin(tl))))
        grid.append(row)
    for i in range(SEG_X):
        for j in range(SEG_THETA):
            j2 = (j + 1) % SEG_THETA
            f = bm.faces.new((grid[i][j], grid[i][j2], grid[i + 1][j2], grid[i + 1][j]))   # winding: normals into the lumen
            for loop, (a, b) in zip(f.loops, ((i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j))):
                loop[uv].uv = (a / SEG_X * (LENGTH / 1000.0), b / SEG_THETA * (2 * math.pi * RADIUS / 1000.0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:                                  # recalc points outwards for an open tube; we look from inside
        f.normal_flip()
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


def material():
    """Mucosa: pale pink, moist, strong subsurface (light travels tens of um in the tissue); epithelial cells
    (~10 um) and the cilia carpet as bump/roughness in object space."""
    m = bpy.data.materials.get("M_C02_Schleimhaut") or bpy.data.materials.new("M_C02_Schleimhaut")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = (0.80, 0.58, 0.56, 1)
    p.inputs["Subsurface Weight"].default_value = 0.85
    p.inputs["Subsurface Radius"].default_value = (40.0, 18.0, 12.0)
    p.inputs["Subsurface Scale"].default_value = 1.0
    p.inputs["IOR"].default_value = 1.38
    p.inputs["Coat Weight"].default_value = 0.35           # the thin fluid film on the epithelium
    p.inputs["Coat Roughness"].default_value = 0.06
    tc = nt.nodes.new("ShaderNodeTexCoord")
    cells = nt.nodes.new("ShaderNodeTexVoronoi")
    cells.feature = "DISTANCE_TO_EDGE"
    cells.inputs["Scale"].default_value = 0.1               # cells ~10 um
    cilia = nt.nodes.new("ShaderNodeTexNoise")
    cilia.inputs["Scale"].default_value = 3.0               # ~0.3 um tufts
    cilia.inputs["Detail"].default_value = 10.0
    mix = nt.nodes.new("ShaderNodeMath")
    mix.operation = "MULTIPLY_ADD"
    mix.inputs[1].default_value = 0.4
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 1.5
    rough = nt.nodes.new("ShaderNodeMapRange")
    rough.inputs["To Min"].default_value = 0.28
    rough.inputs["To Max"].default_value = 0.55
    for n in (cells, cilia):
        nt.links.new(tc.outputs["Object"], n.inputs["Vector"])
    nt.links.new(cilia.outputs["Fac"], mix.inputs[0])
    nt.links.new(cells.outputs["Distance"], mix.inputs[2])
    nt.links.new(mix.outputs[0], bump.inputs["Height"])
    nt.links.new(cilia.outputs["Fac"], rough.inputs["Value"])
    nt.links.new(rough.outputs["Result"], p.inputs["Roughness"])
    nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    nt.links.new(p.outputs["BSDF"], out.inputs["Surface"])
    return m


def main():
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 0.01
    col = bpy.data.collections.get("C02_EILEITER") or bpy.data.collections.new("C02_EILEITER")
    if col.name not in sc.collection.children:
        sc.collection.children.link(col)
    for o in list(col.objects):
        bpy.data.objects.remove(o)
    obj = bpy.data.objects.new("SM_C02_Eileiter", build())
    obj.data.materials.append(material())
    obj.location = (0, 0, 3000)                           # away from the oocyte stage
    col.objects.link(obj)
    return {"verts": len(obj.data.vertices), "length": round(obj.dimensions.x, 1), "outer_d": round(obj.dimensions.y, 1)}


if __name__ == "__main__":
    print(main())
