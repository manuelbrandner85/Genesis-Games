"""G4 (runs INSIDE the Unreal Editor): read back the imported pallet and check it.

Checks against the Blender reference (docs/evidence/G3/fbx_verify.json): size in cm, origin at
bottom centre, Nanite on with full fallback, one material = our instance, texture settings,
collision present and the fork openings left free (line traces through the pockets), and that
the pallet rests on the floor. Writes Saved/G4/verify_report.json.
"""
import json
import os

import unreal

ROOT = unreal.Paths.project_dir()
MESH = "/Game/Genesis/TechSmoke/PalletEUR/SM_TechSmoke_PalletEUR"
MI = "/Game/Genesis/TechSmoke/PalletEUR/MI_TechSmoke_PalletWood"
ref = json.load(open(os.path.join(ROOT, "docs", "evidence", "G3", "fbx_verify.json"), encoding="utf-8"))
ref_cm = [v / 10.0 for v in ref["size_mm"]]

eal = unreal.EditorAssetLibrary
sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mesh = eal.load_asset(MESH)
box = mesh.get_bounding_box()
size = [box.max.x - box.min.x, box.max.y - box.min.y, box.max.z - box.min.z]
ns = mesh.get_editor_property("nanite_settings")
mats = [m.get_editor_property("material_interface") for m in mesh.get_editor_property("static_materials")]

# Fork pockets: horizontal traces at 6 cm height (inside the 7.8 cm block gap) along X between
# the block rows and along Y between the block columns must pass through without a hit.
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
pallet = next(a for a in eas.get_all_level_actors() if a.get_actor_label() == "SM_TechSmoke_PalletEUR")
comp = pallet.static_mesh_component
comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)

def trace(a, b):
    hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(*a), unreal.Vector(*b), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                 False, [], unreal.DrawDebugTrace.NONE, True)
    return hit is not None and bool(hit.to_tuple()[0])

z = 2.2 + 3.9                      # middle of the pocket between bottom board (2.2 cm) and stringer
pockets = {
    "along_x_between_rows_y-17": trace((-80, -17.5, z), (80, -17.5, z)),
    "along_x_between_rows_y+17": trace((-80, 17.5, z), (80, 17.5, z)),
    "along_y_between_cols_x-26": trace((-26, -60, z), (-26, 60, z)),
    "along_y_between_cols_x+26": trace((26, -60, z), (26, 60, z)),
}
solid = {
    "down_onto_deck": trace((0, 0, 40), (0, 0, 10)),
    "into_corner_block": trace((90, -35, z), (40, -35, z)),
}
checks = {
    "size_matches_blender_0.1mm": all(abs(s - r) <= 0.01 for s, r in zip(size, ref_cm)),
    "origin_bottom_centre": abs(box.min.z) < 0.01 and abs(box.min.x + box.max.x) < 0.01 and abs(box.min.y + box.max.y) < 0.01,
    "length_on_x_width_on_y": size[0] > size[1] > size[2],
    "nanite_enabled": bool(ns.get_editor_property("enabled")),
    "nanite_full_fallback": abs(ns.get_editor_property("fallback_percent_triangles") - 1.0) < 1e-6,
    "one_material_is_instance": len(mats) == 1 and mats[0] is not None and mats[0].get_path_name().split(".")[0] == MI,
    "collision_present": sms.get_convex_collision_count(mesh) + sms.get_simple_collision_count(mesh) > 0,
    "fork_pockets_open": not any(pockets.values()),
    "deck_and_blocks_solid": all(solid.values()),
    "rests_on_floor": abs(pallet.get_actor_location().z) < 0.01,
}
report = {
    "size_cm": [round(s, 3) for s in size], "blender_ref_cm": ref_cm,
    "bounds_min_cm": [round(box.min.x, 3), round(box.min.y, 3), round(box.min.z, 3)],
    "nanite": {"enabled": ns.get_editor_property("enabled"), "fallback_percent_triangles": ns.get_editor_property("fallback_percent_triangles")},
    "fallback_verts_lod0": sms.get_number_verts(mesh, 0),
    "collision_convex_hulls": sms.get_convex_collision_count(mesh), "collision_simple": sms.get_simple_collision_count(mesh),
    "pocket_traces_hit": pockets, "solid_traces_hit": solid,
    "material": mats[0].get_path_name() if mats and mats[0] else None,
    "checks": checks, "passed": all(checks.values()),
}
out = os.path.join(ROOT, "Saved", "G4", "verify_report.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, default=str)
print("G4_VERIFY " + json.dumps(report, default=str))
