"""C00 (runs INSIDE the Unreal Editor): Epic-Cloud steps for the C00 MetaHumans (FA-METAHUMAN-CLOUD-001, approved
in chat 2026-10-25: 4K textures + auto-rig). Env GENESIS_CLOUD_STEP = "textures" | "rig" | "status",
GENESIS_CLOUD_CHAR = "Mann" | "Tochter". Requests are non-blocking; the result is polled with "status".
Backups of the MHC assets: Saved/C00_MHC_Backup_20261025.
"""
import os
import unreal

STEP = os.environ.get("GENESIS_CLOUD_STEP", "status")
NAME = os.environ.get("GENESIS_CLOUD_CHAR", "Mann")
eal = unreal.EditorAssetLibrary
mh = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
ch = eal.load_asset(f"/Game/Genesis/Characters/C00/MHC_C00_{NAME}")
if not mh.is_object_added_for_editing(ch) and not mh.try_add_object_to_edit(ch):
    raise RuntimeError("cannot edit " + NAME)

if STEP == "textures":
    ss = ch.skin_settings
    res = ss.desired_texture_sources_resolutions
    R4 = unreal.MetaHumanCharacterTextureSourceResolution.RES4K if hasattr(unreal, "MetaHumanCharacterTextureSourceResolution") else None
    for f in ("face_albedo", "face_normal", "face_cavity", "face_animated_maps", "body_albedo", "body_normal", "body_cavity", "body_masks"):
        cur = getattr(res, f)
        setattr(res, f, R4 if R4 is not None else type(cur).RES4K)
    ss.desired_texture_sources_resolutions = res
    mh.commit_skin_settings(ch, ss)
    p = unreal.MetaHumanCharacterTextureRequestParams() if hasattr(unreal, "MetaHumanCharacterTextureRequestParams") else None
    if p:
        p.set_editor_property("blocking", False)
        p.set_editor_property("report_progress", True)
        mh.request_texture_sources(ch, p)
    else:
        mh.request_texture_sources(ch)
    print("C00_CLOUD textures requested", NAME, ch.skin_settings.desired_texture_sources_resolutions)
elif STEP == "rig":
    p = unreal.MetaHumanCharacterAutoRiggingRequestParams()
    p.set_editor_property("rig_type", unreal.MetaHumanRigType.JOINTS_AND_BLEND_SHAPES)
    p.set_editor_property("blocking", False)
    p.set_editor_property("report_progress", True)
    mh.request_auto_rigging(ch, p)
    print("C00_CLOUD rig requested", NAME)
props = [x for x in dir(ch) if any(k in x.lower() for k in ("rig", "texture", "synth", "state"))]
info = {}
for x in props:
    try:
        v = getattr(ch, x)
        if not callable(v):
            info[x] = str(v)[:120]
    except Exception:
        pass
print("C00_CLOUD status", NAME, "can_build", mh.can_build_meta_human(ch, True), info)
