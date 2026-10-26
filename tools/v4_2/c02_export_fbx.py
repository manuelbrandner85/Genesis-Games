"""CR-001 Phase 3 (background Blender): FBX export of the C02 micro assets for Unreal.

    blender -b ArtSource/Blender/C02/C02_Mikrowelt.blend -P tools/v4_2/c02_export_fbx.py

1 Blender unit = 1 um = 1 Unreal unit: the scene has scale_length 0.01 (metric), FBX_SCALE_UNITS writes the file in
centimetres, so Unreal imports at 1:1. Forward +X, up +Z (as the swim pawn). Transforms are applied in the export
(the two-cell blastomeres are scaled unit spheres). The posed sperm copy and the instancing helper are not exported;
the cumulus distribution goes to Unreal as C02_Cumulus_Instanzen.json (instanced static mesh).
"""
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "ArtSource/Blender/C02/Export"
OUT.mkdir(parents=True, exist_ok=True)

GROUPS = {
    "SM_C02_Spermium": ["SM_C02_Spermium"],
    "SM_C02_Oozyte": ["SM_C02_Oozyte", "SM_C02_Zona", "SM_C02_Polkoerper"],
    "SM_C02_CumulusZelle": ["SM_C02_CumulusZelle"],
    "SM_C02_Eileiter": ["SM_C02_Eileiter"],
    "SM_C02_Zygote": None,          # all objects of the collection
    "SM_C02_Zweizell": None,
}
COLLECTIONS = {"SM_C02_Zygote": "C02_ZYGOTE", "SM_C02_Zweizell": "C02_ZWEIZELL"}


def export(name, objects):
    bpy.ops.object.select_all(action="DESELECT")
    origin = objects[0].matrix_world.translation.copy()
    saved = {}
    for o in objects:                                     # each asset around its own origin
        saved[o.name] = o.location.copy()
        o.location = o.location - origin
        o.hide_set(False)
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    path = OUT / f"{name}.fbx"
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={"MESH"}, apply_unit_scale=True,
                             apply_scale_options="FBX_SCALE_UNITS", axis_forward="X", axis_up="Z", use_mesh_modifiers=True,
                             mesh_smooth_type="FACE", add_leaf_bones=False, bake_space_transform=True)
    for o in objects:
        o.location = saved[o.name]
    print("EXPORTED", path.name, len(objects), "objects")


for name, names in GROUPS.items():
    if names is None:
        objs = list(bpy.data.collections[COLLECTIONS[name]].objects)
    else:
        objs = [bpy.data.objects[n] for n in names]
    export(name, objs)
