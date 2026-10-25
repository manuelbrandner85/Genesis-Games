"""C00 (runs INSIDE the Unreal Editor): dying face for the BUILT, auto-rigged MetaHuman, driven through the face rig.

c00_face_dying.py moves facial joints directly - fine for the preview face, but the built face is driven by RigLogic,
which overwrites those joints (open mouth, head thrown back). This one-frame pose A_C00_Mann_Gesicht_Sterbend_Built
instead carries:
- every bone track of the body pose A_C00_Mann_Liegen_Built that the face skeleton shares (spine, neck, head), so the
  face follows the body exactly - the old asset only flexed the neck and lost the spine lift of the pillow, which made
  the head tip backwards
- CTRL_expressions_* curves for RigLogic: heavy half-closed lids looking down, lips nearly closed, sagging mouth
  corners, hollow cheeks, deepened nasolabial folds, weary inner brows. Values stay low: exhausted, not grimacing.
"""
import unreal

POSEN = "/Game/Genesis/Characters/C00/Posen"
NAME = "A_C00_Mann_Gesicht_Sterbend_Built"
eal = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary

CURVES = {
    "eyeBlink": 0.55, "eyeRelax": 0.45, "eyeLookDown": 0.25, "eyeUpperLidUp": 0.0,
    "eyeLowerLidUp": 0.10,
    "jawOpen": 0.05, "mouthLipsTogetherU": 0.30, "mouthLipsTogetherD": 0.30,
    "mouthCornerDepress": 0.28, "mouthCornerDown": 0.15,
    "mouthCheekSuck": 0.22, "noseNasolabialDeepen": 0.20,
    "browRaiseIn": 0.12, "browDown": 0.05,
}


def curve_names():
    for k, v in CURVES.items():                          # every control is split per side (...L / ...R)
        for s in ("L", "R"):
            yield f"CTRL_expressions_{k}{s}", v


body_anim = eal.load_asset(f"{POSEN}/A_C00_Mann_Liegen_Built")
skel = eal.load_asset("/Game/Genesis/Characters/C00/Built/Common/Face/Face_Archetype_Skeleton")
tracks = [str(t) for t in AL.get_animation_track_names(body_anim)]

path = f"{POSEN}/{NAME}"
anim = eal.load_asset(path) if eal.does_asset_exist(path) else None
if anim is None:
    fac = unreal.AnimSequenceFactory()
    fac.set_editor_property("target_skeleton", skel)
    anim = unreal.AssetToolsHelpers.get_asset_tools().create_asset(NAME, POSEN, unreal.AnimSequence, fac)
ctrl = anim.controller
ctrl.open_bracket("C00 dying face (rig)", True)
ctrl.remove_all_bone_tracks(True)                   # in place: the asset is referenced by the open level
ctrl.remove_all_curves_of_type(unreal.RawCurveTrackTypes.RCT_FLOAT, True)
ctrl.set_frame_rate(unreal.FrameRate(30, 1), True)
ctrl.set_number_of_frames(unreal.FrameNumber(1), True)
bones = 0
for b in tracks:
    tf = AL.get_bone_pose_for_frame(body_anim, b, 0, False)
    try:                                            # body-only bones (arms, legs) are not in the face skeleton
        ctrl.add_bone_curve(b, False)
    except RuntimeError:
        continue
    ctrl.set_bone_track_keys(b, [tf.translation] * 2, [tf.rotation] * 2, [tf.scale3d] * 2, True)
    bones += 1
ctrl.close_bracket(True)
ncurves = 0
for cname, val in curve_names():
    AL.add_curve(anim, cname, unreal.RawCurveTrackTypes.RCT_FLOAT, False)
    AL.add_float_curve_keys(anim, cname, [0.0, 1 / 30], [val, val])
    ncurves += 1
eal.save_loaded_asset(anim)
print("C00_FACE_RIG", path, bones, "bones of", len(tracks), ncurves, "curves")
