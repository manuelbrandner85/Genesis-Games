"""C00 (runs INSIDE the Unreal Editor): the framed photo above the bed - the man with his daughter.

Regie 2026-10-25: "das Bild ueber dem Bett soll den Mann mit seiner Tochter zeigen"; both ~10 years younger,
more elegant clothes, her hair longer, his fuller (MHC_C00_*_Foto from c00_mh_photo_variants.py), smiling more. Made from the two C00
MetaHumans themselves (no image AI), as a warm studio portrait from some years ago: both chest-up, side by
side, turned a little toward each other, with a gentle smile set through local face joints
(A_C00_<Name>_Laecheln: mouth corners up and out, cheeks lifted, lower lids slightly raised).
Rendered through the real viewport in L_C00_CharacterLab; output ArtSource/Export/C00/T_C00_Foto_VaterTochter.png
(also copied as evidence). Clothes and hair: see c00_mh_photo_variants.py.
"""
import math
import os

import unreal

eal = unreal.EditorAssetLibrary
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mh = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
MATH = unreal.MathLibrary
CS = unreal.RelativeTransformSpace.RTS_COMPONENT
V, R = unreal.Vector, unreal.Rotator
ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
POSEN = "/Game/Genesis/Characters/C00/Posen"


def smile_anim(name, face):
    names = [str(face.get_bone_name(i)) for i in range(face.get_num_bones())]
    cs = {b: face.get_socket_transform(b, CS) for b in names}
    parent = {b: str(face.get_parent_bone(b)) for b in names}
    new = {}

    def nudge(b, dx=0.0, dy=0.0, dz=0.0):
        if b in cs:
            t = cs[b]
            new[b] = unreal.Transform(location=t.translation + V(dx, dy, dz), rotation=t.rotation.rotator(), scale=t.scale3d)

    for side, sx in (("L", 1), ("R", -1)):
        nudge(f"FACIAL_{side}_LipCorner", dx=0.75 * sx, dy=-0.35, dz=1.25)   # Regie: "etwas mehr laecheln"          # corners up, out, back
        for k in ("1", "2", "3"):
            nudge(f"FACIAL_{side}_LipCorner{k}", dx=0.50 * sx, dy=-0.22, dz=0.80)
        for b in (f"FACIAL_{side}_CheekInner", f"FACIAL_{side}_CheekOuter", f"FACIAL_{side}_CheekLower"):
            nudge(b, dz=0.65, dy=0.18)                                              # cheeks lifted
        lo = f"FACIAL_{side}_EyelidLowerA"
        if lo in cs:                                                                # warm eyes: lower lid up a little
            piv = cs[lo].translation
            a = math.radians(10) / 2
            q = unreal.Quat(math.sin(a), 0, 0, math.cos(a))
            tip = cs[[c for c in names if parent[c] == lo][0]].translation if any(parent[c] == lo for c in names) else piv + V(0, 1, 0)
            if (piv + q.rotate_vector(tip - piv)).z < tip.z:
                q = unreal.Quat(-math.sin(a), 0, 0, math.cos(a))
            new[lo] = unreal.Transform(location=piv, rotation=(q * cs[lo].rotation).rotator(), scale=cs[lo].scale3d)
    jaw = "FACIAL_C_Jaw"                                                            # lips parted a little
    if jaw in cs:
        piv = cs[jaw].translation
        chin = cs["FACIAL_C_UnderChin"].translation if "FACIAL_C_UnderChin" in cs else piv + V(0, 6, -4)
        a = math.radians(3) / 2
        q = unreal.Quat(math.sin(a), 0, 0, math.cos(a))
        if (piv + q.rotate_vector(chin - piv)).z > chin.z:
            q = unreal.Quat(-math.sin(a), 0, 0, math.cos(a))
        new[jaw] = unreal.Transform(location=piv, rotation=(q * cs[jaw].rotation).rotator(), scale=cs[jaw].scale3d)
    path = f"{POSEN}/{name}"
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    fac = unreal.AnimSequenceFactory()
    fac.set_editor_property("target_skeleton", face.get_skeletal_mesh_asset().skeleton)
    anim = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, POSEN, unreal.AnimSequence, fac)
    ctrl = anim.controller
    ctrl.open_bracket("smile", True)
    ctrl.set_frame_rate(unreal.FrameRate(30, 1), True)
    ctrl.set_number_of_frames(unreal.FrameNumber(1), True)
    for b, tf in new.items():
        local = MATH.make_relative_transform(tf, cs[parent[b]])
        ctrl.add_bone_curve(b, True)
        ctrl.set_bone_track_keys(b, [local.translation] * 2, [local.rotation] * 2, [local.scale3d] * 2, True)
    ctrl.close_bracket(True)
    eal.save_loaded_asset(anim)
    return anim


les.load_level("/Game/Genesis/Characters/C00/L_C00_CharacterLab")
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith(("MH_", "PH_")):
        eas.destroy_actor(a)

# father left, daughter right (seen from the camera at +X); both turned ~10 deg toward each other;
# she stands slightly lower (her approved height is 166 cm, the preview body is taller - see open items)
cast = (("Mann", V(-6, -24, 0), -90 + 16), ("Tochter", V(6, 24, -7), -90 - 14))   # turned toward each other, her shoulder slightly in front of his: no arms through each other
actors = {}
for name, loc, yaw in cast:
    ch = eal.load_asset(f"/Game/Genesis/Characters/C00/MHC_C00_{name}_Foto")   # younger photo variant (c00_mh_photo_variants.py)
    if not mh.is_object_added_for_editing(ch):
        mh.try_add_object_to_edit(ch)
    a = mh.spawn_meta_human_actor(ch, True)
    a.set_actor_label("PH_" + name)
    a.set_actor_location_and_rotation(loc, R(0, 0, yaw), False, True)
    mh.assemble_for_preview(ch)
    face = next(c for c in a.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Face")
    anim = smile_anim(f"A_C00_{name}_Foto_Laecheln", face)
    face.set_update_animation_in_editor(True)
    face.override_animation_data(anim, False, True, 0.0, 0.0)
    actors[name] = a

# warm, softly lit living-room tone behind them instead of the black studio (a family photo, not a test shot)
back = eas.spawn_actor_from_object(eal.load_asset("/Engine/BasicShapes/Cube"), V(-110, 0, 150), R(0, 0, 0))
back.set_actor_label("PH_Backdrop")
back.set_actor_scale3d(V(0.05, 6, 4))
# own neutral warm-grey backdrop (the shared set material drifted to a saturated peach and tinted the skin via GI)
_bp = "/Game/Genesis/Characters/C00/Posen/MI_C00_Foto_Backdrop"
bmi = eal.load_asset(_bp) if eal.does_asset_exist(_bp) else unreal.AssetToolsHelpers.get_asset_tools().create_asset(
    "MI_C00_Foto_Backdrop", "/Game/Genesis/Characters/C00/Posen", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
unreal.MaterialEditingLibrary.set_material_instance_parent(bmi, eal.load_asset("/Game/Genesis/Sets/C00_Schlafzimmer/Materials/M_C00_SetSurface"))
unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(bmi, "Color", unreal.LinearColor(0.42, 0.40, 0.37, 1))
unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(bmi, "Emissive", unreal.LinearColor(0, 0, 0, 1))
unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(bmi, "Roughness", 0.9)
eal.save_loaded_asset(bmi)
back.static_mesh_component.set_material(0, bmi)
warm = eas.spawn_actor_from_class(unreal.RectLight, V(60, -160, 220), MATH.find_look_at_rotation(V(60, -160, 220), V(0, 0, 150)))
warm.set_actor_label("PH_WarmKey")
wl = warm.get_component_by_class(unreal.RectLightComponent)
wl.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
wl.set_editor_property("intensity", 5500.0)
wl.set_editor_property("use_temperature", True)
wl.set_editor_property("temperature", 4300.0)
wl.set_editor_property("source_width", 150.0)
wl.set_editor_property("source_height", 150.0)
target = V(0, 0, 155)
cam_loc = target + V(380, 0, 4)
cam = eas.spawn_actor_from_class(unreal.CineCameraActor, cam_loc, MATH.find_look_at_rotation(cam_loc, target))
cam.set_actor_label("PH_Cam")
cc = cam.get_cine_camera_component()
cc.set_editor_property("current_focal_length", 100.0)   # chest-up crop: the A-pose arms stay out of frame
cc.set_editor_property("current_aperture", 5.6)
cc.set_editor_property("constrain_aspect_ratio", False)
fs = cc.focus_settings
fs.focus_method = unreal.CameraFocusMethod.MANUAL
fs.manual_focus_distance = (target - cam_loc).length() - 8.0
cc.set_editor_property("focus_settings", fs)
out = ROOT + "ArtSource/Export/C00/T_C00_Foto_VaterTochter.png"
eas.select_nothing()
unreal.EditorLevelLibrary.editor_set_game_view(True)
unreal.AutomationLibrary.take_high_res_screenshot(1500, 1125, out, cam, False, False, unreal.ComparisonTolerance.LOW, "", 1.0)
print("C00_PHOTO", out)
