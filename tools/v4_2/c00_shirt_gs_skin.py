"""C00 (runs INSIDE the Unreal Editor): skin the man's fitted shirt in Unreal with Geometry Script.

A Blender round trip of the MetaHuman skeleton changes bone orientations ("ungueltige Bindeposen"): under the
leader pose the shirt's torso collapsed onto the spine. So only the fitted shirt shape comes from Blender
(SM_C00_Shirt_fitted.fbx, tools/v4_2/build_c00_shirt_skinned.py); the skeleton and bind pose come straight from the
man's body (UE -> FBX -> UE, SKM_C00_Mann_Body.fbx) and the weights are transferred here from that body:
1. import the body FBX as skeletal mesh SKM_C00_Mann_Shirt (container with the body's exact ref skeleton)
2. import the fitted shirt as static mesh, copy both into dynamic meshes
3. transfer bone weights body -> shirt (closest point on surface), write the shirt into the container
Result: /Game/Genesis/Characters/C00/Kleidung/SKM_C00_Mann_Shirt with MI_Shirt_01 (local only, Fab content).
"""
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
DST = "/Game/Genesis/Characters/C00/Kleidung"
eal = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
GS = unreal.GeometryScript_AssetUtils
BW = unreal.GeometryScript_BoneWeights
skel = eal.load_asset("/MetaHumanCharacter/Female/Medium/NormalWeight/Body/metahuman_base_skel")


def fbx_task(fbx, name, skeletal):
    t = unreal.AssetImportTask()
    t.filename, t.destination_path, t.destination_name = ROOT + "ArtSource/Export/C00/" + fbx, DST, name
    t.automated, t.replace_existing, t.save = True, True, True
    o = unreal.FbxImportUI()
    o.import_mesh, o.import_materials, o.import_textures, o.import_animations = True, False, False, False
    o.import_as_skeletal = skeletal
    o.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH if skeletal else unreal.FBXImportType.FBXIT_STATIC_MESH
    if skeletal:
        o.skeleton = skel
        o.skeletal_mesh_import_data.set_editor_property("import_morph_targets", False)
    else:
        o.static_mesh_import_data.set_editor_property("combine_meshes", True)
        o.static_mesh_import_data.set_editor_property("auto_generate_collision", False)
    t.options = o
    return t


for p in (f"{DST}/SKM_C00_Mann_Shirt", f"{DST}/SM_C00_Shirt_fitted"):
    if eal.does_asset_exist(p):
        eal.delete_asset(p)
at.import_asset_tasks([fbx_task("SKM_C00_Mann_Body.fbx", "SKM_C00_Mann_Shirt", True),
                       fbx_task("SM_C00_Shirt_fitted.fbx", "SM_C00_Shirt_fitted", False)])
container = eal.load_asset(f"{DST}/SKM_C00_Mann_Shirt")
shirt_sm = eal.load_asset(f"{DST}/SM_C00_Shirt_fitted")

opts = unreal.GeometryScriptCopyMeshFromAssetOptions()
lod = unreal.GeometryScriptMeshReadLOD()
body_dm, out1 = GS.copy_mesh_from_skeletal_mesh(container, unreal.DynamicMesh(), opts, lod)
shirt_dm, out2 = GS.copy_mesh_from_static_mesh(shirt_sm, unreal.DynamicMesh(), opts, lod)
print("C00_GS_COPY", out1, out2, body_dm.get_triangle_count(), shirt_dm.get_triangle_count())
bb_b = unreal.GeometryScript_MeshQueries.get_mesh_bounding_box(body_dm)
bb_s = unreal.GeometryScript_MeshQueries.get_mesh_bounding_box(shirt_dm)
print("C00_GS_BOUNDS body", [round(v) for v in bb_b.min.to_tuple()], [round(v) for v in bb_b.max.to_tuple()],
      "shirt", [round(v) for v in bb_s.min.to_tuple()], [round(v) for v in bb_s.max.to_tuple()])
BW.copy_bones_from_mesh(body_dm, shirt_dm)
topt = unreal.GeometryScriptTransferBoneWeightsOptions()
topt.set_editor_property("transfer_method", unreal.TransferBoneWeightsMethod.CLOSEST_POINT_ON_SURFACE)
BW.transfer_bone_weights_from_mesh(body_dm, shirt_dm, topt)
wopt = unreal.GeometryScriptCopyMeshToAssetOptions() if hasattr(unreal, "GeometryScriptCopyMeshToAssetOptions") else None
target_lod = unreal.GeometryScriptMeshWriteLOD()
_, out3 = GS.copy_mesh_to_skeletal_mesh(shirt_dm, container, wopt, target_lod)
mi = eal.load_asset("/Game/Fab/MetaHuman/Shirt_01/Materials/MI_Shirt_01")
mats = container.materials
for m in mats:
    m.material_interface = mi
container.materials = mats
eal.save_loaded_asset(container)
print("C00_GS_SKIN", out3, len(mats))
