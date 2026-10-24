"""G7 (runs INSIDE Blender 5.2): build SM_R03_Room, the shell of the 7 x 6 m workshop (R03).

Replaces the graybox walls/floor/ceiling of L_Flussdorf_G6 (tools/v4/g7/g7_room.py layout):
outside 7.0 x 6.0 m, 24 cm walls, inside 6.52 x 5.52 m, 3.48 m clear height.
Modernised old building (user decision 2026-10-24: "moderner und voller"):
- walls: painted brick (Poly Haven painted_brick, CC0, 1.80 m per tile; relief, joints and roughness
  from the scan, the scan's blue paint recoloured): off-white above, grey painted plinth up to 1.20 m
- floor: grey coated concrete, epoxy look (painted_concrete_02, 4.0 m), top 1 cm above the village lawn
- ceiling: boards and three 14 x 20 cm beams painted white (brown_planks_03 recoloured, 1.0 m)
- door and window frames painted anthracite (distressed_painted_planks recoloured)
- door 1.20 x 2.20 m in the west wall (market side), frame + leaf opened outwards against the facade
- window 1.20 x 1.10 m in the east wall, sill at 1.00 m: the morning sun of the level (from the
  north-east) falls in, as in ArtSource/Reference/G7/R03_Werkstatt_Mood/interior_v1.png
Origin: room centre on the floor = Unreal (5050, 0, 0). Unreal's Y is Blender's -Y after FBX import,
so every Unreal-side coordinate goes through ue() below. UVs are world-scale box projections, so the
CC0 textures tile at their real size. Writes UCX boxes for walls, floor, ceiling and door leaf.
"""
import bpy, bmesh, math, os
from mathutils import Vector

NAME = "SM_R03_Room"
COL = "G7_Room"
ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
EXT = os.path.join(ROOT, "ArtSource", "External", "PolyHaven")
exec(compile(open(os.path.join(os.path.dirname(__file__), "g7_common.py"), encoding="utf8").read(), "g7_common.py", "exec"))

sc = bpy.context.scene
col = bpy.data.collections.get(COL)
if col:
    for o in list(col.all_objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    col = bpy.data.collections.new(COL)
    sc.collection.children.link(col)
for m in [m for m in bpy.data.materials if m.name.startswith("M_RM_")]:
    bpy.data.materials.remove(m)


def ue(x, y, z):
    """Unreal-local (cm-free metres, Unreal Y) -> Blender."""
    return (x, -y, z)


def img(asset, kind, res, ext, non_color):
    p = os.path.join(EXT, asset, f"{asset}_{kind}_{res}.{ext}")
    im = bpy.data.images.load(p, check_existing=True)
    im.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
    return im


def scanned(name, asset, res, tile_m, bump=0.4, directional=True, recolor=None):
    """Poly Haven PBR set on world-scale UVs (UV unit = tile_m metres): diffuse, ARM
    (AO/rough/metal), OpenGL normal, height as fine bump.
    Anti-tiling (same method as M_G7_Tiled in Unreal): every map is sampled twice, the second time
    shifted by a non-integer offset (bricks, boards: same size and direction, so courses stay level),
    for isotropic materials (concrete) additionally scaled 0.73 and rotated 37 deg; a low-frequency
    mask (the height map itself, sampled at 0.09x) blends the two, so no tile repeats as a whole."""
    mat = bpy.data.materials.new(name)
    mat["tile_m"] = tile_m
    mat["polyhaven"] = asset
    nt, bsdf = _nodes(mat)
    uvn = nt.nodes.new("ShaderNodeUVMap")
    m2 = nt.nodes.new("ShaderNodeMapping")
    if not directional:
        m2.inputs["Scale"].default_value = (0.73, 0.73, 1.0)
        m2.inputs["Rotation"].default_value = (0.0, 0.0, math.radians(37.0))
    m2.inputs["Location"].default_value = (0.37, 0.61, 0.0)
    nt.links.new(uvn.outputs["UV"], m2.inputs["Vector"])
    mm = nt.nodes.new("ShaderNodeMapping")
    mm.inputs["Scale"].default_value = (0.09, 0.09, 1.0)
    nt.links.new(uvn.outputs["UV"], mm.inputs["Vector"])
    mask_t = nt.nodes.new("ShaderNodeTexImage")
    mask_t.image = img(asset, "disp", res, "jpg", True)
    nt.links.new(mm.outputs["Vector"], mask_t.inputs["Vector"])
    mask = _range(nt, mask_t.outputs["Color"], 0.42, 0.58, 0.0, 1.0)

    def pair(kind, ext, nc):
        a_, b_ = nt.nodes.new("ShaderNodeTexImage"), nt.nodes.new("ShaderNodeTexImage")
        a_.image = b_.image = img(asset, kind, res, ext, nc)
        nt.links.new(uvn.outputs["UV"], a_.inputs["Vector"])
        nt.links.new(m2.outputs["Vector"], b_.inputs["Vector"])
        return _mix(nt, mask, a_.outputs["Color"], b_.outputs["Color"])

    d = pair("diff", "jpg", False)
    arm = pair("arm", "jpg", True)
    nrm = pair("nor_gl", "png", True)
    disp = pair("disp", "jpg", True)
    if recolor:
        # repaint: keep the scan's light/dark structure (luminance), replace its hue by the paint colour
        # (same formula as M_G7_Tiled in Unreal: Tint * (0.55 + 0.9 * luminance))
        bw = nt.nodes.new("ShaderNodeRGBToBW")
        nt.links.new(d, bw.inputs["Color"])
        lum = _add(nt, _add(nt, bw.outputs["Val"], 0.9, "MULTIPLY"), 0.55)
        tint = nt.nodes.new("ShaderNodeMix")
        tint.data_type = "RGBA"
        tint.blend_type = "MULTIPLY"
        tint.inputs["Factor"].default_value = 1.0
        tint.inputs[6].default_value = recolor + (1.0,)
        nt.links.new(lum, tint.inputs[7])
        d = tint.outputs[2]
        mat["recolor"] = list(recolor)
    nt.links.new(d, bsdf.inputs["Base Color"])
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(arm, sep.inputs["Color"])
    nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(nrm, nm.inputs["Color"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    bp.inputs["Distance"].default_value = 0.002
    nt.links.new(disp, bp.inputs["Height"])
    nt.links.new(nm.outputs["Normal"], bp.inputs["Normal"])
    nt.links.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def glass(name):
    mat = bpy.data.materials.new(name)
    nt, bsdf = _nodes(mat)
    bsdf.inputs["Base Color"].default_value = (0.93, 0.97, 0.95, 1)   # float glass, faint green
    bsdf.inputs["Transmission Weight"].default_value = 1.0
    bsdf.inputs["IOR"].default_value = 1.52
    dust = _noise(nt, 18.0, 6.0, 0.6)
    nt.links.new(_range(nt, dust.outputs["Fac"], 0.35, 0.75, 0.02, 0.18), bsdf.inputs["Roughness"])
    # Shadow rays pass the glazing (as translucent glass does in Unreal): the sun is near point-like,
    # refracted paths never find it, so without this the window would block all direct sunlight.
    # Two 4 mm panes of float glass transmit ~0.92 of the light.
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    lp = nt.nodes.new("ShaderNodeLightPath")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    tr.inputs["Color"].default_value = (0.96, 0.97, 0.96, 1)
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Shadow Ray"], mix.inputs["Fac"])
    nt.links.new(bsdf.outputs["BSDF"], mix.inputs[1])
    nt.links.new(tr.outputs["BSDF"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return mat


M = {
    "plaster": scanned("M_RM_PaintedBrickWhite", "painted_brick", "4k", 1.80, 0.5, recolor=(0.78, 0.77, 0.74)),
    "plinth": scanned("M_RM_PaintedBrickGrey", "painted_brick", "4k", 1.80, 0.5, recolor=(0.20, 0.21, 0.22)),
    "floor": scanned("M_RM_EpoxyFloor", "painted_concrete_02", "4k", 4.0, 0.2, directional=False),
    "planks": scanned("M_RM_CeilingWhite", "brown_planks_03", "4k", 1.0, 0.3, recolor=(0.80, 0.79, 0.76)),
    "frame": scanned("M_RM_FrameAnthracite", "distressed_painted_planks", "2k", 1.6, 0.3, recolor=(0.05, 0.055, 0.06)),
    "glass": glass("M_RM_WindowGlass"),
    "metal": simple_mat("M_RM_ZincSill", (0.58, 0.59, 0.60), 0.45, metal=1.0, rough_var=0.12, bump=0.05),
}

W2, D2, H, T = 3.50, 3.00, 3.50, 0.24          # half outer length/depth, wall height, wall thickness
IX, IY = W2 - T, D2 - T                        # half inner
parts, ucx = [], []


DADO = 1.20                                   # top of the grey painted plinth


def wall(name, x0, x1, y0, y1, z0, z1, mat="plaster", collide=True):
    """Axis-aligned block by Unreal-local extents (metres). Brick walls crossing the plinth height are
    split into a grey plinth part and a white upper part (one collision box for the whole)."""
    if mat == "plaster" and z0 < DADO < z1:
        wall(name + "_Plinth", x0, x1, y0, y1, z0, DADO, "plinth", collide=False)
        o = wall(name, x0, x1, y0, y1, DADO, z1, "plaster", collide=False)
        if collide:
            ucx.append(((abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), ue((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)))
        return o
    if mat == "plaster" and z1 <= DADO:
        mat = "plinth"
    c = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    s = (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
    o = box(name, s, ue(*c), mat, bevel=0.004)
    parts.append(o)
    if collide:
        ucx.append((s, ue(*c)))
    return o


# --- shell ------------------------------------------------------------------------------------------
wall("Wall_N", -W2, W2, IY, D2, 0, H)
wall("Wall_S", -W2, W2, -D2, -IY, 0, H)
DOOR_Y, DOOR_H = 0.60, 2.20
wall("Wall_W_S", -W2, -IX, -IY, -DOOR_Y, 0, H)
wall("Wall_W_N", -W2, -IX, DOOR_Y, IY, 0, H)
wall("Wall_W_Lintel", -W2, -IX, -DOOR_Y, DOOR_Y, DOOR_H, H)
WIN_Y0, WIN_Y1, SILL, WIN_TOP = 0.80, 2.00, 1.00, 2.10
wall("Wall_E_S", IX, W2, -IY, WIN_Y0, 0, H)
wall("Wall_E_N", IX, W2, WIN_Y1, IY, 0, H)
wall("Wall_E_Below", IX, W2, WIN_Y0, WIN_Y1, 0, SILL)
wall("Wall_E_Above", IX, W2, WIN_Y0, WIN_Y1, WIN_TOP, H)
wall("Floor", -IX, IX, -IY, IY, -0.11, 0.01, "floor")
wall("Ceiling", -IX, IX, -IY, IY, H - 0.04, H, "planks")
for k, bx in enumerate((-1.6, 0.0, 1.6)):
    wall(f"Beam_{k}", bx - 0.07, bx + 0.07, -IY, IY, H - 0.24, H - 0.04, "planks", collide=False)

# --- window: painted wooden frame, two casements, double glazing, inner board, zinc outer sill ------
FR = 0.07
wx_in, wx_out = IX + 0.02, W2 - 0.08                   # frame sits 2 cm into the reveal from inside
fx = (wx_in + wx_out) / 2
for nm, (ya, yb, za, zb) in {"Head": (WIN_Y0, WIN_Y1, WIN_TOP - FR, WIN_TOP), "Foot": (WIN_Y0, WIN_Y1, SILL, SILL + FR),
                             "JambS": (WIN_Y0, WIN_Y0 + FR, SILL, WIN_TOP), "JambN": (WIN_Y1 - FR, WIN_Y1, SILL, WIN_TOP),
                             "Mullion": ((WIN_Y0 + WIN_Y1) / 2 - 0.035, (WIN_Y0 + WIN_Y1) / 2 + 0.035, SILL, WIN_TOP)}.items():
    wall(f"Win_{nm}", wx_in, wx_out, ya, yb, za, zb, "frame", collide=False)
for k, (ya, yb) in enumerate(((WIN_Y0 + FR, (WIN_Y0 + WIN_Y1) / 2 - 0.035), ((WIN_Y0 + WIN_Y1) / 2 + 0.035, WIN_Y1 - FR))):
    for g, gx in enumerate((fx - 0.010, fx + 0.010)):     # 4 mm panes, 16 mm gap
        wall(f"Win_Glass_{k}_{g}", gx - 0.002, gx + 0.002, ya, yb, SILL + FR, WIN_TOP - FR, "glass", collide=False)
wall("Win_Board", IX - 0.05, wx_in, WIN_Y0 - 0.05, WIN_Y1 + 0.05, SILL - 0.03, SILL, "frame", collide=False)
wall("Win_OuterSill", wx_out, W2 + 0.05, WIN_Y0 - 0.03, WIN_Y1 + 0.03, SILL - 0.04, SILL - 0.03, "metal", collide=False)

# --- door: frame in the west opening, leaf (1.10 x 2.15 x 0.045) opened 90 deg outwards ---------------
dx = -IX - 0.02
for nm, (ya, yb, za, zb) in {"Head": (-DOOR_Y, DOOR_Y, DOOR_H - 0.06, DOOR_H), "JambS": (-DOOR_Y, -DOOR_Y + 0.06, 0, DOOR_H),
                             "JambN": (DOOR_Y - 0.06, DOOR_Y, 0, DOOR_H)}.items():
    wall(f"Door_{nm}", dx - 0.06, dx + 0.06, ya, yb, za, zb, "frame", collide=False)
HINGE_Y = -DOOR_Y + 0.07
wall("Door_Leaf", -W2 - 0.01 - 1.10, -W2 - 0.01, HINGE_Y - 0.045, HINGE_Y, 0.01, 2.16, "frame")
for k, z in enumerate((0.35, 1.80)):
    wall(f"Door_Hinge_{k}", -W2 - 0.03, -W2 + 0.005, HINGE_Y - 0.06, HINGE_Y + 0.005, z, z + 0.12, "metal", collide=False)
wall("Door_Handle", -W2 - 1.03, -W2 - 1.0, HINGE_Y + 0.0, HINGE_Y + 0.07, 1.04, 1.06, "metal", collide=False)

room = join_parts(NAME, parts)

# world-scale UVs: project every face on its dominant axis, divide by the material's tile size
bm = bmesh.new()
bm.from_mesh(room.data)
uv = bm.loops.layers.uv.new("UVMap") if not bm.loops.layers.uv else bm.loops.layers.uv[0]
mats = list(room.data.materials)
for f in bm.faces:
    t = float(mats[f.material_index].get("tile_m", 1.0)) if mats[f.material_index] else 1.0
    n = f.normal
    ax = max(range(3), key=lambda i: abs(n[i]))
    for l in f.loops:
        v = l.vert.co
        u_, v_ = {(0): (v.y, v.z), (1): (v.x, v.z), (2): (v.x, v.y)}[ax]
        l[uv].uv = (u_ / t, v_ / t)
bm.to_mesh(room.data)
bm.free()
for i, (s, c) in enumerate(ucx):
    collision_box(f"{NAME}_{i:02d}", s, c, room)
bb = [room.matrix_world @ Vector(c) for c in room.bound_box]
dims = [round(max(v[i] for v in bb) - min(v[i] for v in bb), 3) for i in range(3)]
result = {"object": NAME, "dims_m": dims, "z_min": round(min(v.z for v in bb), 3), "tris": sum(len(p.vertices) - 2 for p in room.data.polygons),
          "materials": [m.name for m in room.data.materials], "collision": len(ucx)}
print("G7_ROOM", result)
