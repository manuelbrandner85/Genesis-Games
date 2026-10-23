"""G3 check: re-import the exported FBX into an empty Blender scene and measure it.

    blender -b --factory-startup --python tools/v4/g3/verify_fbx.py -- --fbx <FILE> --out <REPORT.json>

Expected for SM_TechSmoke_PalletEUR: 1200 x 800 mm footprint, wood height 144.0 mm,
nail heads 0.3 mm proud (bbox 144.3 mm), origin bottom centre, unit scale, one UV map.
Length/width tolerance +-3 mm (EN 13698-1); the boards are deliberately not CAD-exact.
"""
import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np

EXPECTED_MM = (1200.0, 800.0, 144.0)
TOL_MM = 3.0          # footprint tolerance
TOL_EXACT_MM = 0.5    # height and origin are built exactly


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fbx", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(a.fbx))
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    ob = meshes[0]
    me = ob.data
    co = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    m = np.array(ob.matrix_world)
    w = (np.c_[co.reshape(-1, 3), np.ones(len(me.vertices))] @ m.T)[:, :3] * 1000.0
    size = w.max(0) - w.min(0)
    wood_top = float(w[:, 2][w[:, 2] <= EXPECTED_MM[2] + 0.05].max())
    me.calc_loop_triangles()
    areas = np.empty(len(me.loop_triangles))
    me.loop_triangles.foreach_get("area", areas)
    checks = {
        "single_mesh": len(meshes) == 1,
        "length_x": abs(size[0] - EXPECTED_MM[0]) <= TOL_MM,
        "width_y": abs(size[1] - EXPECTED_MM[1]) <= TOL_MM,
        "wood_height_z": abs(wood_top - EXPECTED_MM[2]) <= TOL_EXACT_MM,
        "origin_bottom_centre": bool(np.allclose([(w[:, 0].max() + w[:, 0].min()) / 2, (w[:, 1].max() + w[:, 1].min()) / 2, w[:, 2].min()], 0, atol=TOL_EXACT_MM)),
        "unit_transform": bool(np.allclose(ob.scale, 1) and np.allclose(ob.rotation_euler, 0, atol=1e-5)),
        "uv_map": len(me.uv_layers) == 1,
        "no_degenerate_triangles": bool((areas > 1e-10).all()),
        "max_4_corners": max(len(p.vertices) for p in me.polygons) <= 4,
        "one_material": len(me.materials) == 1 and me.materials[0] is not None,
    }
    checks = {k: bool(v) for k, v in checks.items()}
    report = {
        "fbx": str(a.fbx), "blender": bpy.app.version_string, "object": ob.name,
        "size_mm": [round(float(v), 2) for v in size], "wood_top_mm": round(wood_top, 2),
        "verts": len(me.vertices), "faces": len(me.polygons), "triangles": len(me.loop_triangles),
        "uv_layers": [u.name for u in me.uv_layers], "custom_normals": me.has_custom_normals,
        "checks": checks, "passed": all(checks.values()),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("G3_VERIFY " + json.dumps(report))


if __name__ == "__main__":
    main()
