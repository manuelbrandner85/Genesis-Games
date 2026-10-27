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
    grid, depths = [], []
    for i in range(SEG_X + 1):
        x = LENGTH * i / SEG_X
        row = []
        for j in range(SEG_THETA):
            th = 2 * math.pi * j / SEG_THETA
            d, lean = depth(th, x, F)
            depths.append(min(d / 320.0, 1.0))
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
    # fold height as a vertex colour (0 = groove between the folds, 1 = high crest): the material darkens and
    # reddens the deep, wet, less lit grooves; travels to Unreal with the FBX as vertex colour
    att = me.color_attributes.new("Tiefe", "FLOAT_COLOR", "POINT")
    for k, d in enumerate(depths):
        att.data[k].color = (d, d, d, 1.0)
    return me


def material():
    """Mucosa: moist, strong subsurface (light travels tens of um in the tissue). Three levels: fold height
    (vertex colour: deep red grooves, pale crests) and wet/dry patches of the mucus film; ~10 um epithelial
    cells, each either ciliated (matte, rough cilia carpet combed along the tube) or secretory (smooth, domed,
    glossy); cilia tufts as bump. All in object space (no UV seams)."""
    m = bpy.data.materials.get("M_C02_Schleimhaut") or bpy.data.materials.new("M_C02_Schleimhaut")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    p.inputs["Subsurface Weight"].default_value = 0.85
    p.inputs["Subsurface Radius"].default_value = (40.0, 18.0, 12.0)
    p.inputs["Subsurface Scale"].default_value = 1.0
    p.inputs["IOR"].default_value = 1.38
    p.inputs["Coat Roughness"].default_value = 0.05
    L = nt.links.new
    tc = nt.nodes.new("ShaderNodeTexCoord")

    def node(kind, **inputs):
        n = nt.nodes.new(kind)
        for k, v in inputs.items():
            n.inputs[k].default_value = v
        return n

    def maprange(src, a, b, c, d):
        n = node("ShaderNodeMapRange")
        n.inputs["From Min"].default_value, n.inputs["From Max"].default_value = a, b
        n.inputs["To Min"].default_value, n.inputs["To Max"].default_value = c, d
        L(src, n.inputs["Value"])
        return n.outputs["Result"]

    def mix(fac, a, b, blend="MIX"):
        """Colour mix; a/b are RGB tuples or sockets (Mix node colour sockets: inputs 6/7, output 2)."""
        n = nt.nodes.new("ShaderNodeMix")
        n.data_type = "RGBA"
        n.blend_type = blend
        if isinstance(fac, float):
            n.inputs[0].default_value = fac
        else:
            L(fac, n.inputs[0])
        for idx, v in ((6, a), (7, b)):
            if isinstance(v, tuple):
                n.inputs[idx].default_value = (*v, 1)
            else:
                L(v, n.inputs[idx])
        return n.outputs[2]

    # macro: fold height (vertex colour) - grooves deep red and dark, crests pale pink
    depth = nt.nodes.new("ShaderNodeAttribute")
    depth.attribute_name = "Tiefe"
    crest = maprange(depth.outputs["Fac"], 0.0, 0.75, 0.0, 1.0)
    # epithelium: one ~10 um Voronoi cell per epithelial cell; each cell is ciliated (~60 %) or secretory
    cells = node("ShaderNodeTexVoronoi", Scale=0.1)
    L(tc.outputs["Object"], cells.inputs["Vector"])
    edge = node("ShaderNodeTexVoronoi", Scale=0.1)
    edge.feature = "DISTANCE_TO_EDGE"
    L(tc.outputs["Object"], edge.inputs["Vector"])
    cid = nt.nodes.new("ShaderNodeSeparateColor")
    L(cells.outputs["Color"], cid.inputs["Color"])
    cil = maprange(cid.outputs["Red"], 0.38, 0.42, 0.0, 1.0)          # 1 = ciliated cell, 0 = secretory cell
    # medium: large wet/dry and colour patches (~80-150 um) - mucus film thicker in places
    patch = node("ShaderNodeTexNoise", Scale=0.008, Detail=3.0)
    L(tc.outputs["Object"], patch.inputs["Vector"])
    # micro: cilia carpet (~0.3 um tufts, combed along the tube by the beat) and the secretory cell dome
    cmap = node("ShaderNodeMapping")
    cmap.inputs["Scale"].default_value = (0.35, 1.0, 1.0)            # tufts stretched along X (flow direction)
    L(tc.outputs["Object"], cmap.inputs["Vector"])
    cilia = node("ShaderNodeTexNoise", Scale=3.2, Detail=12.0, Roughness=0.75)
    L(cmap.outputs["Vector"], cilia.inputs["Vector"])
    dome = maprange(edge.outputs["Distance"], 0.0, 0.5, 0.0, 1.0)

    base = mix(crest, (0.56, 0.20, 0.24), (0.90, 0.66, 0.66))
    base = mix(maprange(cid.outputs["Green"], 0.0, 1.0, 0.0, 0.35), base, (0.88, 0.62, 0.58))   # cell-to-cell tint
    base = mix(0.06, base, cells.outputs["Color"], "MULTIPLY")      # faint per-cell value jitter
    L(base, p.inputs["Base Color"])

    # roughness: cilia carpet matte and rough, secretory domes smooth and glossy, thin film wetter on the crests
    r_cil = maprange(cilia.outputs["Fac"], 0.3, 0.7, 0.42, 0.68)
    rough = nt.nodes.new("ShaderNodeMix")                           # float mix: inputs 0/2/3, output 0
    L(cil, rough.inputs[0])
    rough.inputs[2].default_value = 0.18
    L(r_cil, rough.inputs[3])
    L(rough.outputs[0], p.inputs["Roughness"])
    coat = maprange(patch.outputs["Fac"], 0.35, 0.65, 0.12, 0.6)
    L(coat, p.inputs["Coat Weight"])

    # height: cell borders as fine grooves, domed secretory cells, cilia tufts on ciliated cells
    h_cil = node("ShaderNodeMath")
    h_cil.operation = "MULTIPLY"
    L(cilia.outputs["Fac"], h_cil.inputs[0])
    L(cil, h_cil.inputs[1])
    h = node("ShaderNodeMath")
    h.operation = "MULTIPLY_ADD"
    L(dome, h.inputs[0])
    h.inputs[1].default_value = 0.6
    L(h_cil.outputs[0], h.inputs[2])
    bump = node("ShaderNodeBump", Strength=0.5, Distance=1.2)
    L(h.outputs[0], bump.inputs["Height"])
    L(bump.outputs["Normal"], p.inputs["Normal"])
    L(p.outputs["BSDF"], out.inputs["Surface"])
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
