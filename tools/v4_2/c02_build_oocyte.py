"""CR-001 Phase 3 (runs inside Blender 5.2): human oocyte with zona pellucida, polar body, corona
radiata and cumulus oophorus after docs/v4_2/C02_MASSBLATT.md (1 Blender unit = 1 um).

SM_C02_Oozyte        : egg cell (oolemma 115 um), slightly irregular, granular cytoplasm (volume)
SM_C02_Zona          : zona pellucida, 16 um thick glassy shell (two surfaces, real thickness), fibrous
SM_C02_Polkoerper    : first polar body (12 um) in the perivitelline space
SM_C02_CumulusZelle  : one cumulus/corona cell (12 um, nucleus inside) - instanced
C02_CUMULUS_Verteilung: corona (dense, 1-3 layers on the zona) + cumulus cloud out to ~400 um, as a
                        point cloud with per-instance scale/rotation for Unreal (exported positions JSON)
"""
import json
import math
import random

import bmesh
import bpy
from mathutils import Vector, noise as Noise

R_OOCYTE = 57.5
PVS = 4.0
R_ZONA_IN = R_OOCYTE + PVS
R_ZONA_OUT = R_ZONA_IN + 16.0
R_POLAR = 6.0
R_CELL = 6.0


def col(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(c)
    return c


def sphere(name, radius, subdiv=5, wobble=0.0, seed=0):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=radius)
    if wobble:
        off = Vector((seed * 13.1, seed * 7.7, seed * 3.3))
        for v in bm.verts:
            n = Noise.noise((v.co / radius) * 1.6 + off)
            v.co *= 1.0 + wobble * n
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


def principled(nt, color, ior, transmission, rough, sss=0.0, sss_radius=(4, 3.5, 3)):
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["IOR"].default_value = ior
    p.inputs["Transmission Weight"].default_value = transmission
    p.inputs["Roughness"].default_value = rough
    p.inputs["Subsurface Weight"].default_value = sss
    p.inputs["Subsurface Radius"].default_value = sss_radius
    return p


def mat_cytoplasm():
    """Oocyte: clear membrane, cytoplasm full of fine granules (organelles) - a scattering volume."""
    m = bpy.data.materials.get("M_C02_Oozyte") or bpy.data.materials.new("M_C02_Oozyte")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    surf = principled(nt, (0.86, 0.84, 0.80), 1.04, 0.92, 0.12)       # IOR relative to the fluid (1.37/1.335, raised)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")              # granule density, ~1-3 um clusters
    noise.inputs["Scale"].default_value = 0.9           # granules and clusters of ~1 um
    noise.inputs["Detail"].default_value = 10.0
    noise.inputs["Roughness"].default_value = 0.7
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["From Min"].default_value = 0.42
    ramp.inputs["From Max"].default_value = 0.7
    ramp.inputs["To Min"].default_value = 0.0008       # measured: higher densities turn the 115 um cell dark grey
    ramp.inputs["To Max"].default_value = 0.009
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Value"])
    gran = nt.nodes.new("ShaderNodeTexVoronoi")                # organelles / yolk-like granules ~1 um
    gran.inputs["Scale"].default_value = 0.55
    nt.links.new(tc.outputs["Object"], gran.inputs["Vector"])
    spot = nt.nodes.new("ShaderNodeMapRange")
    spot.inputs["From Min"].default_value = 0.22
    spot.inputs["From Max"].default_value = 0.08
    spot.inputs["To Min"].default_value = 0.0
    spot.inputs["To Max"].default_value = 0.05
    nt.links.new(gran.outputs["Distance"], spot.inputs["Value"])
    dens = nt.nodes.new("ShaderNodeMath")
    dens.operation = "ADD"
    nt.links.new(ramp.outputs["Result"], dens.inputs[0])
    nt.links.new(spot.outputs["Result"], dens.inputs[1])
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (0.82, 0.78, 0.70, 1)
    vol.inputs["Absorption Color"].default_value = (0.92, 0.88, 0.80, 1)
    vol.inputs["Anisotropy"].default_value = 0.6           # small organelles scatter forward
    nt.links.new(dens.outputs["Value"], vol.inputs["Density"])
    nt.links.new(surf.outputs["BSDF"], out.inputs["Surface"])
    nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])
    return m


def mat_zona():
    """Zona pellucida: glassy glycoprotein shell, faint fibrous texture, IOR ~1.34."""
    m = bpy.data.materials.get("M_C02_Zona") or bpy.data.materials.new("M_C02_Zona")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    p = principled(nt, (0.93, 0.93, 0.91), 1.015, 0.97, 0.06)          # zona 1.34 in fluid 1.335: nearly invisible in reality
    tc = nt.nodes.new("ShaderNodeTexCoord")
    wave = nt.nodes.new("ShaderNodeTexWave")                 # fibre network
    wave.wave_type = "RINGS"
    wave.inputs["Scale"].default_value = 0.4
    wave.inputs["Distortion"].default_value = 18.0
    wave.inputs["Detail"].default_value = 6.0
    nt.links.new(tc.outputs["Object"], wave.inputs["Vector"])
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = 0.03
    rr.inputs["To Max"].default_value = 0.14
    nt.links.new(wave.outputs["Fac"], rr.inputs["Value"])
    nt.links.new(rr.outputs["Result"], p.inputs["Roughness"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.08
    bump.inputs["Distance"].default_value = 0.3
    nt.links.new(wave.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    vol = nt.nodes.new("ShaderNodeVolumeScatter")            # faint haze inside the glycoprotein
    vol.inputs["Density"].default_value = 0.0015
    nt.links.new(p.outputs["BSDF"], out.inputs["Surface"])
    nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])
    return m


def mat_cell():
    """Cumulus/corona cell: translucent, scattering cytoplasm; the nucleus is a separate denser sphere."""
    m = bpy.data.materials.get("M_C02_CumulusZelle") or bpy.data.materials.new("M_C02_CumulusZelle")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    p = principled(nt, (0.92, 0.91, 0.88), 1.035, 0.96, 0.08)
    nt.links.new(p.outputs["BSDF"], out.inputs["Surface"])
    cv = nt.nodes.new("ShaderNodeVolumePrincipled")
    cv.inputs["Color"].default_value = (0.86, 0.84, 0.79, 1)
    cv.inputs["Density"].default_value = 0.035
    cv.inputs["Anisotropy"].default_value = 0.5
    nt.links.new(cv.outputs["Volume"], out.inputs["Volume"])
    k = bpy.data.materials.get("M_C02_Zellkern") or bpy.data.materials.new("M_C02_Zellkern")
    k.use_nodes = True
    kt = k.node_tree
    kt.nodes.clear()
    ko = kt.nodes.new("ShaderNodeOutputMaterial")
    kp = principled(kt, (0.9, 0.88, 0.84), 1.06, 0.97, 0.12)
    kt.links.new(kp.outputs["BSDF"], ko.inputs["Surface"])
    kv = kt.nodes.new("ShaderNodeVolumePrincipled")              # chromatin: denser, slightly darker
    kv.inputs["Color"].default_value = (0.7, 0.66, 0.6, 1)
    kv.inputs["Density"].default_value = 0.22
    kv.inputs["Absorption Color"].default_value = (0.75, 0.7, 0.62, 1)
    kv.inputs["Anisotropy"].default_value = 0.3
    kt.links.new(kv.outputs["Volume"], ko.inputs["Volume"])
    return m, k


def cumulus_cell():
    cell = sphere("SM_C02_CumulusZelle", R_CELL, 3, wobble=0.10, seed=3)
    nuc = sphere("SM_C02_CumulusZelle_Kern", 2.5, 2, wobble=0.12, seed=5)
    me = bpy.data.meshes.new("SM_C02_CumulusZelle_Geo")
    bm = bmesh.new()
    bm.from_mesh(cell)
    bm2 = bmesh.new()
    bm2.from_mesh(nuc)
    bmesh.ops.translate(bm2, verts=bm2.verts, vec=(0.8, -0.5, 0.3))   # nucleus slightly eccentric
    for f in bm2.faces:
        f.material_index = 1
    tmp = bpy.data.meshes.new("_tmp")
    bm2.to_mesh(tmp)
    bm.from_mesh(tmp)
    bm.to_mesh(me)
    bm.free()
    bm2.free()
    for d in (cell, nuc, tmp):
        bpy.data.meshes.remove(d)
    for p in me.polygons:
        p.use_smooth = True
    m, k = mat_cell()
    me.materials.append(m)
    me.materials.append(k)
    return me


def distribution(seed=2026):
    """Corona: dense radial layers on the zona; cumulus: looser cloud in a gel out to ~400 um."""
    rnd = random.Random(seed)
    pts = []

    def unit():
        while True:
            v = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)))
            if 0.05 < v.length <= 1:
                return v.normalized()

    for _ in range(900):                                   # corona radiata, 1-3 layers, elongated radially
        n = unit()
        r = R_ZONA_OUT + R_CELL * rnd.uniform(0.85, 3.2)
        pts.append((n * r, n, rnd.uniform(0.85, 1.15), 1.35))
    placed = 0
    while placed < 1600:                                   # cumulus cloud, density falls off outwards
        n = unit()
        r = rnd.uniform(R_ZONA_OUT + 3 * R_CELL, 400)
        if rnd.random() > (1.0 - (r - R_ZONA_OUT) / (400 - R_ZONA_OUT)) ** 1.6:
            continue
        pts.append((n * r, unit(), rnd.uniform(0.8, 1.2), 1.0))
        placed += 1
    return pts


def main():
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 0.01
    c = col("C02_OOZYTE")
    for o in list(c.objects):
        bpy.data.objects.remove(o)
    egg = bpy.data.objects.new("SM_C02_Oozyte", sphere("SM_C02_Oozyte", R_OOCYTE, 6, wobble=0.012, seed=1))
    egg.data.materials.append(mat_cytoplasm())
    zona_me = bpy.data.meshes.new("SM_C02_Zona")
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=6, radius=R_ZONA_OUT)
    inner = bmesh.new()
    bmesh.ops.create_icosphere(inner, subdivisions=6, radius=R_ZONA_IN)
    bmesh.ops.reverse_faces(inner, faces=inner.faces)       # inner surface faces inwards: closed shell
    tmp = bpy.data.meshes.new("_tmp")
    inner.to_mesh(tmp)
    bm.from_mesh(tmp)
    bm.to_mesh(zona_me)
    bm.free()
    inner.free()
    bpy.data.meshes.remove(tmp)
    for p in zona_me.polygons:
        p.use_smooth = True
    zona = bpy.data.objects.new("SM_C02_Zona", zona_me)
    zona.data.materials.append(mat_zona())
    polar = bpy.data.objects.new("SM_C02_Polkoerper", sphere("SM_C02_Polkoerper", R_POLAR, 3, wobble=0.08, seed=9))
    polar.data.materials.append(mat_cytoplasm())
    polar.location = Vector((0.3, 0.2, 0.93)).normalized() * (R_OOCYTE + R_POLAR * 0.55)
    for o in (egg, zona, polar):
        c.objects.link(o)
    cell = bpy.data.objects.new("SM_C02_CumulusZelle", cumulus_cell())
    cell.location = (0, -520, 0)                            # template, off to the side
    c.objects.link(cell)
    pts = distribution()
    # Instances for the preview (Blender) and as data for Unreal (Hierarchical Instanced Static Mesh)
    me = bpy.data.meshes.new("C02_CUMULUS_Verteilung")
    me.from_pydata([p for p, *_ in pts], [], [])
    me.attributes.new("orient", "FLOAT_VECTOR", "POINT").data.foreach_set("vector", [x for _, n, *_ in pts for x in n])
    me.attributes.new("scale", "FLOAT", "POINT").data.foreach_set("value", [s for *_, s, _ in pts])
    me.attributes.new("stretch", "FLOAT", "POINT").data.foreach_set("value", [st for *_, st in pts])
    dist = bpy.data.objects.new("C02_CUMULUS_Verteilung", me)
    c.objects.link(dist)
    gn = dist.modifiers.new("Instanzen", "NODES")
    tree = bpy.data.node_groups.get("GN_C02_Cumulus") or bpy.data.node_groups.new("GN_C02_Cumulus", "GeometryNodeTree")
    tree.nodes.clear()
    tree.interface.clear()
    tree.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    tree.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    gi = tree.nodes.new("NodeGroupInput")
    go = tree.nodes.new("NodeGroupOutput")
    inst = tree.nodes.new("GeometryNodeInstanceOnPoints")
    oi = tree.nodes.new("GeometryNodeObjectInfo")
    oi.inputs["Object"].default_value = cell
    oi.transform_space = "ORIGINAL"
    a_or = tree.nodes.new("GeometryNodeInputNamedAttribute")
    a_or.data_type = "FLOAT_VECTOR"
    a_or.inputs["Name"].default_value = "orient"
    a_sc = tree.nodes.new("GeometryNodeInputNamedAttribute")
    a_sc.data_type = "FLOAT"
    a_sc.inputs["Name"].default_value = "scale"
    a_st = tree.nodes.new("GeometryNodeInputNamedAttribute")
    a_st.data_type = "FLOAT"
    a_st.inputs["Name"].default_value = "stretch"
    align = tree.nodes.new("FunctionNodeAlignRotationToVector")
    align.axis = "Z"
    comb = tree.nodes.new("ShaderNodeCombineXYZ")
    mul = tree.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    tree.links.new(a_or.outputs["Attribute"], align.inputs["Vector"])
    tree.links.new(a_sc.outputs["Attribute"], comb.inputs["X"])
    tree.links.new(a_sc.outputs["Attribute"], comb.inputs["Y"])
    tree.links.new(a_sc.outputs["Attribute"], mul.inputs[0])
    tree.links.new(a_st.outputs["Attribute"], mul.inputs[1])
    tree.links.new(mul.outputs[0], comb.inputs["Z"])
    tree.links.new(gi.outputs[0], inst.inputs["Points"])
    tree.links.new(oi.outputs["Geometry"], inst.inputs["Instance"])
    tree.links.new(align.outputs["Rotation"], inst.inputs["Rotation"])
    tree.links.new(comb.outputs["Vector"], inst.inputs["Scale"])
    tree.links.new(inst.outputs["Instances"], go.inputs[0])
    gn.node_group = tree
    out = bpy.path.abspath("//C02_Cumulus_Instanzen.json")
    with open(out, "w", encoding="utf8") as f:
        json.dump({"unit": "um (= uu)", "template": "SM_C02_CumulusZelle", "instances": [
            {"p": [round(v, 2) for v in p], "z": [round(v, 4) for v in n], "s": round(s, 3), "stretch": st} for p, n, s, st in pts]}, f)
    return {"cells": len(pts), "zona_outer_d": round(zona.dimensions.x, 1), "oocyte_d": round(egg.dimensions.x, 1), "json": out}


if __name__ == "__main__":
    print(main())
