"""G7 check: re-import an exported FBX into an empty scene and compare it with the measure sheet.

    blender -b --factory-startup --python tools/v4/g7/verify_fbx_g7.py -- --fbx F --expect-mm 600,450,460 --tol-mm 15 --out R.json
"""
import argparse, json, sys
from pathlib import Path
import bpy
from mathutils import Vector

ap = argparse.ArgumentParser()
ap.add_argument("--fbx", type=Path, required=True)
ap.add_argument("--expect-mm", required=True)
ap.add_argument("--tol-mm", type=float, default=10.0)
ap.add_argument("--sockets", default="")
ap.add_argument("--out", type=Path, required=True)
a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.import_scene.fbx(filepath=str(a.fbx))
meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith("UCX_")]
ucx = [o for o in bpy.data.objects if o.name.startswith("UCX_")]
sockets = sorted(o.name for o in bpy.data.objects if o.name.startswith("SOCKET_"))
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
dims = [round((max(p[i] for p in pts) - min(p[i] for p in pts)) * 1000, 1) for i in range(3)]
zmin = round(min(p.z for p in pts) * 1000, 2)
exp = [float(x) for x in a.expect_mm.split(",")]
ngons = sum(1 for o in meshes for p in o.data.polygons if len(p.vertices) > 4)
checks = {
    "dimensions_within_tolerance": all(abs(d - e) <= a.tol_mm for d, e in zip(dims, exp)),
    "origin_on_floor": abs(zmin) < 0.5,
    "has_collision": len(ucx) > 0,
    "sockets_present": all(s in sockets for s in a.sockets.split(",") if s),
    "uv_map": all(len(o.data.uv_layers) >= 1 for o in meshes),
    "no_ngons": ngons == 0,
    "unit_scale_1": all(abs(s - 1.0) < 1e-4 for o in meshes for s in o.scale),
}
rep = {"fbx": a.fbx.name, "dimensions_mm": dims, "expected_mm": exp, "tolerance_mm": a.tol_mm, "z_min_mm": zmin,
       "tris": sum(len(p.vertices) - 2 for o in meshes for p in o.data.polygons), "materials": sorted({m.name for o in meshes for m in o.data.materials if m}),
       "collision": [o.name for o in ucx], "sockets": sockets, "checks": checks, "pass": all(checks.values())}
a.out.parent.mkdir(parents=True, exist_ok=True)
a.out.write_text(json.dumps(rep, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
print("VERIFY", json.dumps(rep))
