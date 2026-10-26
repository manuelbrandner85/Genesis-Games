"""CR-001 Phase 3 (runs inside Blender 5.2): human zygote with two pronuclei and the two-cell embryo, after
docs/v4_2/C02_MASSBLATT.md (1 Blender unit = 1 um). Reuses the materials of c02_build_oocyte.py (cytoplasm,
zona, nucleus), so the oocyte must have been built in the same file first.

Zygote (C02-D): cell 115 um, zona 16 um, two pronuclei of 22 um touching in the centre with 5 nucleoli each lined
up at the contact line, two polar bodies (12 um) in the perivitelline space.
Two-cell stage (C02-E/S1): two blastomeres pressed together inside the unchanged zona - each an ellipsoid of
about 60 x 104 x 112 um (the zona confines them; together ~ the volume of the zygote), one 15 um nucleus each,
one polar body.
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

R_CELL = 57.5
R_ZONA_IN, R_ZONA_OUT = 61.5, 77.5
R_PN = 11.0
BLAST_AXES = (30.0, 52.0, 56.0)                # semi-axes: contact axis, across, up (fits the 61.5 um inner zona)


def col(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(c)
    for o in list(c.objects):
        bpy.data.objects.remove(o)
    return c


def sphere_mesh(name, radius, subdiv=5, squash=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=radius)
    if squash:                                           # flatten the side that touches the other blastomere
        axis, plane = squash
        for v in bm.verts:
            d = v.co.dot(axis)
            if d > plane:
                v.co -= axis * (d - plane) * 0.92
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


def zona_mesh(name):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=6, radius=R_ZONA_OUT)
    inner = bmesh.new()
    bmesh.ops.create_icosphere(inner, subdivisions=6, radius=R_ZONA_IN)
    bmesh.ops.reverse_faces(inner, faces=inner.faces)
    tmp = bpy.data.meshes.new("_tmp")
    inner.to_mesh(tmp)
    bm.from_mesh(tmp)
    bm.to_mesh(me)
    bm.free()
    inner.free()
    bpy.data.meshes.remove(tmp)
    for p in me.polygons:
        p.use_smooth = True
    return me


def add(c, name, me, mat, loc=(0, 0, 0)):
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(mat)
    o.location = loc
    c.objects.link(o)
    return o


def main():
    M = bpy.data.materials
    cyto, zona, nucleus = M["M_C02_Oozyte"], M["M_C02_Zona"], M["M_C02_Zellkern"]
    base_z = Vector((0, 600, 0))                          # beside the oocyte stage
    c = col("C02_ZYGOTE")
    add(c, "SM_C02_Zygote", sphere_mesh("SM_C02_Zygote", R_CELL, 6), cyto, base_z)
    add(c, "SM_C02_Zona_Z", zona_mesh("SM_C02_Zona_Z"), zona, base_z)
    for side in (-1, 1):
        pn = add(c, f"SM_C02_Vorkern_{'A' if side < 0 else 'B'}", sphere_mesh("SM_C02_Vorkern", R_PN, 4), nucleus, base_z + Vector((side * R_PN * 0.97, 0, 0)))
        for k in range(5):                               # nucleoli lined up towards the contact line
            nl = add(c, f"SM_C02_Vorkern_Nukleolus_{side}_{k}", sphere_mesh("SM_C02_Nukleolus", 0.8, 2), nucleus,
                     pn.location + Vector((-side * 7.5, (k - 2) * 3.2, math.sin(k) * 1.5)))
    for k, d in enumerate((Vector((0.2, 0.3, 0.93)), Vector((0.35, 0.1, 0.93)))):
        add(c, f"SM_C02_Polkoerper_Z{k}", sphere_mesh("SM_C02_Polkoerper", 6.0, 3), cyto, base_z + d.normalized() * (R_CELL + 3.0 + k * 4))

    base_2 = Vector((0, 1200, 0))
    c2 = col("C02_ZWEIZELL")
    add(c2, "SM_C02_Zona_2Z", zona_mesh("SM_C02_Zona_2Z"), zona, base_2)
    for side in (-1, 1):
        b = add(c2, f"SM_C02_Blastomere_{'A' if side < 0 else 'B'}", sphere_mesh("SM_C02_Blastomere", 1.0, 6), cyto,
                base_2 + Vector((side * BLAST_AXES[0] * 1.02, 0, 0)))
        b.data.transform(Matrix.Diagonal((*BLAST_AXES, 1.0)))   # shape baked into the mesh: textures keep real um
        add(c2, f"SM_C02_Kern_2Z_{'A' if side < 0 else 'B'}", sphere_mesh("SM_C02_Kern", 7.5, 4), nucleus, b.location + Vector((side * 4, 6, 2)))
    add(c2, "SM_C02_Polkoerper_2Z", sphere_mesh("SM_C02_Polkoerper", 6.0, 3), cyto, base_2 + Vector((0, 8, 1)).normalized() * 64)
    total = 2 * BLAST_AXES[0] * BLAST_AXES[1] * BLAST_AXES[2] / R_CELL ** 3
    return {"zygote_objects": len(c.objects), "two_cell_objects": len(c2.objects), "volume_ratio_two_cell": round(total, 2)}


if __name__ == "__main__":
    print(main())
