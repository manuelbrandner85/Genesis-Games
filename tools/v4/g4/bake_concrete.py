"""Bake the review concrete slab (tools/v4/g3/review_scene.py) into a 4 x 4 m texture tile.

The tile spans one slab panel: the saw-cut joints (every 4 m) lie exactly on the tile border,
so the seam of the repeat disappears inside the joint and neighbouring panels may differ in
tone like separate pours. Output (4096^2, ~1 mm per pixel): T_Concrete_YardSlab_BC (sRGB),
_ORM (R = 1, G = roughness, B = 0, linear), _N (DirectX). Call bake(out_dir) inside Blender.
"""
import importlib.util
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
NAME = "T_Concrete_YardSlab"


def _review_module():
    spec = importlib.util.spec_from_file_location("g3_review", HERE.parent / "g3" / "review_scene.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def bake(out_dir, size=4096, tile_m=4.0, samples=32):
    out_dir = Path(out_dir)
    (out_dir / "Textures").mkdir(parents=True, exist_ok=True)
    rv = _review_module()
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "GPU"
    sc.cycles.samples = samples
    sc.render.bake.margin = 0                 # the tile has no UV islands, nothing to pad
    me = bpy.data.meshes.new("Concrete_Tile")
    me.from_pydata([(0, 0, 0), (tile_m, 0, 0), (tile_m, tile_m, 0), (0, tile_m, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name="UVMap")
    for loop, co in zip(uv.data, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop.uv = co
    ob = bpy.data.objects.new("Concrete_Tile", me)
    sc.collection.objects.link(ob)
    mat = rv.concrete_material()
    me.materials.append(mat)
    nt = mat.node_tree
    target = nt.nodes.new("ShaderNodeTexImage")
    for n in nt.nodes:
        n.select = False
    target.select = True
    nt.nodes.active = target
    for o in sc.objects:
        o.select_set(o == ob)
    bpy.context.view_layer.objects.active = ob

    maps = {}
    for key, kind, non_color, kw in (("BC", "DIFFUSE", False, {"pass_filter": {"COLOR"}}), ("R", "ROUGHNESS", True, {}),
                                     ("N", "NORMAL", True, {"normal_space": "TANGENT"})):
        img = bpy.data.images.new(f"{NAME}_{key}_bake", size, size, alpha=False, is_data=non_color)
        img.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
        target.image = img
        bpy.ops.object.bake(type=kind, use_clear=True, **kw)
        a = np.empty(size * size * 4, dtype=np.float32)
        img.pixels.foreach_get(a)
        maps[key] = a.reshape(size, size, 4)
    if maps["BC"][..., :3].mean() < 0.05:
        raise RuntimeError("concrete bake produced an empty base colour map")

    def save(arr, suffix, non_color):
        img = bpy.data.images.new(f"{NAME}_{suffix}", size, size, alpha=False, is_data=non_color)
        img.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
        img.pixels.foreach_set(arr.ravel())
        path = out_dir / "Textures" / f"{NAME}_{suffix}.png"
        img.filepath_raw = str(path)
        img.file_format = "PNG"
        img.save()
        return path

    files = [save(maps["BC"], "BC", False)]
    orm = np.ones_like(maps["R"])
    orm[..., 1] = maps["R"][..., 0]
    orm[..., 2] = 0.0
    files.append(save(orm, "ORM", True))
    n = maps["N"].copy()
    n[..., 1] = 1.0 - n[..., 1]               # OpenGL -> DirectX for Unreal
    files.append(save(n, "N", True))
    bc = maps["BC"][..., :3]
    return {"files": [str(f) for f in files], "tile_m": tile_m, "px_per_mm": size / (tile_m * 1000),
            "basecolor_srgb_mean": round(float(bc.mean()) * 255, 1), "roughness_mean": round(float(maps["R"][..., 0].mean()), 3)}
