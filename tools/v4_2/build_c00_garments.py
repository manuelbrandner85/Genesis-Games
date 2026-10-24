"""C00 (runs INSIDE Blender, scene "C00_Tochter" with the imported MetaHuman preview body + face):
clothing v2 for CHR_C00_TOCHTER (Regie 2026-10-24: blouse with jacket; jacket half closed, correct collar,
buttons, much more realistic).

All garments are cut from the daughter's own surface (body mesh + lower neck of the head mesh joined), so
they keep her skin weights to the MetaHuman body skeleton and follow every pose.
- blouse: off-white, long sleeves, closed round stand collar on the neck
- jacket: charcoal wool blazer, closed below the chest (two buttons), open V above with notched lapels
  folded back over the chest, rolled collar at the back of the neck, three cuff buttons per sleeve
- trousers: dark, straight, waist to ankle
Front of the body is -Y, units metres in world space; the MetaHuman FBX imports in centimetres under a
0.01-scaled root, so modifier distances are converted with LOCAL.
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

SC = bpy.data.scenes["C00_Tochter"]
BODY = SC.objects["BodyMesh_15.002"]
FACE = SC.objects["FaceMesh_14.001"]
ARM = SC.objects["root.001"]
LOCAL = 1.0 / BODY.matrix_world.to_scale().x
OUT = r"C:\Users\manue\Desktop\Genesis-Games\ArtSource\Export\C00\SKM_C00_Tochter_Kleidung.fbx"

BREAK = 1.20          # lapel break point: jacket closed below, V opening above
BUTTONS = (1.045, 1.125)
COLLAR_TOP = 1.468    # blouse stand collar height on the neck


def bone_head(name):
    return ARM.matrix_world @ ARM.data.bones[name].head_local


SHOULDER = {s: bone_head(f"upperarm_{s}") for s in "lr"}
WRIST = {s: bone_head(f"hand_{s}") for s in "lr"}


def arm_param(p):
    """0 at the shoulder, 1 at the wrist (projection on the arm line), None for torso vertices."""
    side = "l" if p.x > 0 else "r"
    s, w = SHOULDER[side], WRIST[side]
    if abs(p.x) < abs(s.x) - 0.01:
        return None
    d = w - s
    return (p - s).dot(d) / d.length_squared


def surface():
    """Body mesh + the lower neck of the head mesh, merged into one skinned surface in body space."""
    name = "C00_Surface"
    if name in SC.objects:
        bpy.data.objects.remove(SC.objects[name])
    ob = BODY.copy()
    ob.data = BODY.data.copy()
    ob.name = ob.data.name = name
    SC.collection.objects.link(ob)
    neck = FACE.copy()
    neck.data = FACE.data.copy()
    SC.collection.objects.link(neck)
    bm = bmesh.new()
    bm.from_mesh(neck.data)
    mw = FACE.matrix_world
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if (mw @ v.co).z > COLLAR_TOP + 0.01], context="VERTS")
    bm.to_mesh(neck.data)
    bm.free()
    neck.matrix_world = FACE.matrix_world
    with bpy.context.temp_override(window=bpy.context.window_manager.windows[0], scene=SC, view_layer=SC.view_layers[0],
                                   active_object=ob, selected_editable_objects=[ob, neck], object=ob):
        bpy.ops.object.join()
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0015 * LOCAL)          # close the body/head seam
    bm.to_mesh(ob.data)
    bm.free()
    ob.hide_set(True)
    ob.hide_render = True
    return ob


def cut(src, name, keep, extra=None):
    ob = src.copy()
    ob.data = src.data.copy()
    ob.name = ob.data.name = name
    SC.collection.objects.link(ob)
    ob.hide_set(False)
    ob.hide_render = False
    wrap = ob.vertex_groups.new(name="Wrap")
    lapel = ob.vertex_groups.new(name="Lapel")
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    mw = ob.matrix_world
    dl = bm.verts.layers.deform.verify()
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not keep(mw @ v.co)], context="VERTS")
    for v in bm.verts:
        v[dl][wrap.index] = 1.0
    if extra:
        extra(bm, mw, dl, wrap.index, lapel.index)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.materials.clear()
    return ob


# --- blouse ---------------------------------------------------------------------------------------------
def blouse_keep(p):
    if p.z < 0.985 or p.z > COLLAR_TOP:
        return False
    t = arm_param(p)
    return t is None or t < 0.96


# --- jacket ---------------------------------------------------------------------------------------------
def v_half(z):
    """Half width of the V opening at height z (0 below the break point)."""
    if z <= BREAK:
        return 0.0
    return 0.010 + (min(z, 1.43) - BREAK) / (1.43 - BREAK) * 0.075


def jacket_keep(p):
    if p.z < 0.925 or p.z > 1.455:
        return False
    t = arm_param(p)
    if t is not None:
        return t < 0.90
    if p.y < -0.02 and abs(p.x) < v_half(p.z):
        return False
    if p.z > 1.41 and p.y < 0.0 and abs(p.x) < 0.075:                            # front of the neck stays free
        return False
    return True


def lapels(bm, mw, dl, wrap_i, lapel_i):
    """Notched lapels: the V edges are extended sideways over the chest; tapered from 0 at the break point
    to 8 cm, with a notch at the top where the collar starts."""
    inv = mw.inverted()
    edges = [e for e in bm.edges if e.is_boundary and all(
        (mw @ v.co).z > BREAK - 0.005 and (mw @ v.co).z < 1.43 and (mw @ v.co).y < -0.02 and abs((mw @ v.co).x) < 0.13
        for v in e.verts)]
    if not edges:
        return
    new = bmesh.ops.extrude_edge_only(bm, edges=edges)["geom"]
    for v in [g for g in new if isinstance(g, bmesh.types.BMVert)]:
        p = mw @ v.co
        k = max(0.0, min(1.0, (p.z - BREAK) / (1.40 - BREAK)))
        width = 0.080 * math.sin(k * math.pi / 2) ** 0.8
        if p.z > 1.38:                                                          # notch: lapel narrows into the collar
            width *= 0.55
        side = 1.0 if p.x > 0 else -1.0
        q = Vector((p.x + side * width, p.y - 0.004, p.z - width * 0.18))       # lapels fall slightly outwards/down
        v.co = inv @ q
        if wrap_i in v[dl]:
            del v[dl][wrap_i]
        v[dl][lapel_i] = 1.0


def trouser_keep(p):
    return 0.085 < p.z < 1.005 and abs(p.x) < 0.24


def material(name, rgb, rough, sheen):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Sheen Weight"].default_value = sheen
    b.inputs["Sheen Tint"].default_value = (*[min(1.0, c * 2.5) for c in rgb], 1)
    return mat


def finish(ob, offset, thick, smooth, rgb, rough, sheen):
    for m in list(ob.modifiers):
        if m.type != "ARMATURE":
            ob.modifiers.remove(m)
    # wash out body details, refine, then hold the cloth outside the skin; lapels get their own lift
    sm = ob.modifiers.new("Drape", "LAPLACIANSMOOTH")
    sm.iterations, sm.lambda_factor, sm.use_volume_preserve = smooth, 0.8, True
    sm.vertex_group = "Wrap"
    sub = ob.modifiers.new("Subdiv", "SUBSURF")
    sub.levels = sub.render_levels = 1
    sw = ob.modifiers.new("OffSkin", "SHRINKWRAP")
    sw.target, sw.wrap_method, sw.wrap_mode, sw.offset = SURF, "NEAREST_SURFACEPOINT", "OUTSIDE_SURFACE", offset * LOCAL
    sw.vertex_group = "Wrap"
    lw = ob.modifiers.new("LapelLift", "SHRINKWRAP")
    lw.target, lw.wrap_method, lw.wrap_mode, lw.offset = SURF, "NEAREST_SURFACEPOINT", "OUTSIDE_SURFACE", (offset + 0.005) * LOCAL
    lw.vertex_group = "Lapel"
    sol = ob.modifiers.new("Thickness", "SOLIDIFY")
    sol.thickness, sol.offset, sol.use_rim = thick * LOCAL, 1.0, True
    arm_mod = next(m for m in ob.modifiers if m.type == "ARMATURE")
    ob.modifiers.move(ob.modifiers.find(arm_mod.name), len(ob.modifiers) - 1)
    ob.data.materials.append(material(ob.name + "_MAT", rgb, rough, sheen))
    for poly in ob.data.polygons:
        poly.use_smooth = True
    return ob


# --- buttons ----------------------------------------------------------------------------------------------
def buttons(jacket):
    """Dark horn buttons (20 mm front, 14 mm cuffs), each skinned rigidly to one bone."""
    name = "C00_Knoepfe"
    if name in SC.objects:
        bpy.data.objects.remove(SC.objects[name])
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    SC.collection.objects.link(ob)
    ob.parent = ARM
    ob.matrix_world = BODY.matrix_world
    inv = ob.matrix_world.inverted()
    deps = bpy.context.evaluated_depsgraph_get()
    jev = jacket.evaluated_get(deps)
    jinv = jacket.matrix_world.inverted()
    bm = bmesh.new()
    groups = {}

    def surface_point(origin, direction):
        ok, loc, nrm, _ = jev.ray_cast(jinv @ origin, (jinv.to_3x3() @ direction).normalized())
        if not ok:
            return None, None
        return jacket.matrix_world @ loc, (jacket.matrix_world.to_3x3() @ nrm).normalized()

    def add(center, normal, radius, bone):
        geom = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=radius * LOCAL,
                                     radius2=radius * 0.88 * LOCAL, depth=0.0035 * LOCAL)
        verts = geom["verts"]
        rot = normal.to_track_quat("Z", "Y").to_matrix().to_4x4()
        world = Matrix.Translation(center + normal * 0.002) @ rot @ Matrix.Scale(1.0 / LOCAL, 4)
        bmesh.ops.transform(bm, matrix=inv @ world, verts=verts)
        groups.setdefault(bone, []).extend(verts)

    for z in BUTTONS:                       # front closure on the wearer's left panel edge (+X)
        p, n = surface_point(Vector((0.012, -0.6, z)), Vector((0, 1, 0)))
        if p:
            add(p, n, 0.010, "spine_02" if z > 1.08 else "spine_01")
    for s, sign in (("l", 1), ("r", -1)):  # cuffs: three buttons on the outside of each sleeve
        sh, wr = SHOULDER[s], WRIST[s]
        for t in (0.78, 0.81, 0.84):
            c = sh.lerp(wr, t)
            out = Vector((sign * 0.3, 0.6, 0.35)).normalized()
            p, n = surface_point(c + out * 0.25, -out)
            if p:
                add(p, n, 0.007, f"lowerarm_{s}")
    bm.verts.index_update()
    ids = {bone: [v.index for v in verts] for bone, verts in groups.items()}
    bm.to_mesh(me)
    bm.free()
    for bone, idx in ids.items():
        g = ob.vertex_groups.get(bone) or ob.vertex_groups.new(name=bone)
        g.add(idx, 1.0, "REPLACE")
    mod = ob.modifiers.new("Armature", "ARMATURE")
    mod.object = ARM
    me.materials.append(material("C00_Knoepfe_MAT", (0.020, 0.016, 0.012), 0.35, 0.0))
    for poly in me.polygons:
        poly.use_smooth = True
    return ob


for n in ("C00_Bluse", "C00_Jackett", "C00_Hose", "C00_Knoepfe"):
    if n in SC.objects:
        bpy.data.objects.remove(SC.objects[n])
SURF = surface()
blouse = finish(cut(SURF, "C00_Bluse", blouse_keep), 0.0045, 0.0015, 10, (0.80, 0.77, 0.71), 0.55, 0.35)
jacket = finish(cut(SURF, "C00_Jackett", jacket_keep, lapels), 0.0140, 0.0035, 14, (0.045, 0.045, 0.050), 0.85, 0.25)
trousers = finish(cut(SURF, "C00_Hose", trouser_keep), 0.0130, 0.0020, 28, (0.030, 0.030, 0.034), 0.75, 0.15)
knoepfe = buttons(jacket)
BODY.hide_set(False)
result = {n: len(SC.objects[n].data.vertices) for n in ("C00_Bluse", "C00_Jackett", "C00_Hose", "C00_Knoepfe")}
