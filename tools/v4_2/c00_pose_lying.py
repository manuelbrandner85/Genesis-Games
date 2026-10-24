"""C00 (runs INSIDE the Unreal Editor): one-frame rest pose for CHR_C00_MANN lying in bed.

The MetaHuman preview figure stands in A-pose (arms ~45 deg out). Lying under the duvet the arms rest along
the body, so this builds A_C00_Mann_Liegen on the body skeleton: both upper arms are swung down around the
character's forward axis until the hands lie ~24 cm beside the body centre, then the elbows bend back
until the hands are level with the back (resting on the mattress when lying). Joint positions -> C00_POSE_JOINTS.json.
The figure itself is laid on its back by the actor rotation in the scene script.
Bone positions come from the man's own body mesh (not the shared skeleton), so the limb lengths stay his.
The asset is bound to the Epic MetaHuman skeleton, so it stays local (gitignored Posen folder).
"""
import math

import unreal

DST, NAME = "/Game/Genesis/Characters/C00/Posen", "A_C00_Mann_Liegen"
PARENT = {"upperarm_l": "clavicle_l", "lowerarm_l": "upperarm_l", "upperarm_r": "clavicle_r", "lowerarm_r": "upperarm_r",
          "neck_01": "spine_05", "neck_02": "neck_01", "head": "neck_02", "foot_l": "calf_l", "foot_r": "calf_r"}
eal = unreal.EditorAssetLibrary
mh = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
MATH = unreal.MathLibrary
CS = unreal.RelativeTransformSpace.RTS_COMPONENT

ch = eal.load_asset("/Game/Genesis/Characters/C00/MHC_C00_Mann")
if not mh.is_object_added_for_editing(ch):
    mh.try_add_object_to_edit(ch)
probe = mh.spawn_meta_human_actor(ch, True)
mh.assemble_for_preview(ch)
body = next(c for c in probe.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Body")
skel = body.get_skeletal_mesh_asset().skeleton
BONES = ("pelvis", "spine_03", "spine_05", "neck_01", "neck_02", "head", "clavicle_l", "clavicle_r", "upperarm_l", "upperarm_r",
         "lowerarm_l", "lowerarm_r", "hand_l", "hand_r", "middle_03_l", "middle_03_r", "thigh_l", "thigh_r",
         "calf_l", "calf_r", "foot_l", "foot_r", "ball_l", "ball_r")
cs = {b: body.get_socket_transform(b, CS) for b in BONES}
a_pose = {b: list(cs[b].translation.to_tuple()) for b in BONES}            # for the duvet proxy (Blender)
eas.destroy_actor(probe)


def spin(tf, pivot, q):
    """Component-space transform tf rotated by quaternion q about point pivot."""
    loc = pivot + q.rotate_vector(tf.translation - pivot)
    return unreal.Transform(location=loc, rotation=(q * tf.rotation).rotator(), scale=tf.scale3d)


def about_y(deg):
    """Quaternion for a rotation of deg degrees about component Y (the character's forward axis)."""
    a = math.radians(deg) / 2
    return unreal.Quat(0.0, math.sin(a), 0.0, math.cos(a))


def about_x(deg):
    """Quaternion for a rotation of deg degrees about component X (the character's left-right axis)."""
    a = math.radians(deg) / 2
    return unreal.Quat(math.sin(a), 0.0, 0.0, math.cos(a))


def swing(side, target_abs_x):
    """Rotation about the forward axis (component Y) that lowers the hand to |x| = target."""
    sh, hp = cs[f"upperarm_{side}"].translation, cs[f"hand_{side}"].translation
    best = None
    for deg in range(-89, 90):
        q = about_y(deg)
        moved = sh + q.rotate_vector(hp - sh)
        if moved.z >= hp.z:
            continue
        err = abs(abs(moved.x) - target_abs_x)
        if best is None or err < best[0]:
            best = (err, deg, q, moved)
    return best


joints = {}
new = {}
for side in ("l", "r"):
    err, deg, q, moved = swing(side, 24.0)
    up, lo = f"upperarm_{side}", f"lowerarm_{side}"
    new[up] = spin(cs[up], cs[up].translation, q)
    lo_cs = spin(cs[lo], cs[up].translation, q)
    hand_cs = spin(cs[f"hand_{side}"], cs[up].translation, q)
    # A-pose hands sit ~15 cm in front of the body; lying on the back they would float. Bend the elbow
    # backwards about component X until the hand is level with the back of the arm (rests on the mattress).
    best = min((abs((lo_cs.translation + about_x(b).rotate_vector(hand_cs.translation - lo_cs.translation)).y - cs[up].translation.y), b)
               for b in range(-60, 61))
    bend = about_x(best[1])
    new[lo] = spin(lo_cs, lo_cs.translation, bend)
    hand = lo_cs.translation + bend.rotate_vector(hand_cs.translation - lo_cs.translation)
    joints[side] = {"shoulder": list(cs[up].translation.to_tuple()), "elbow": list(lo_cs.translation.to_tuple()),
                    "hand": list(hand.to_tuple())}
    print("C00_POSE", side, "swing", deg, "elbow", best[1], "hand", [round(v, 1) for v in hand.to_tuple()])



def bend_chain(chain, degrees, probe, want_more):
    """Rotate a bone chain about component X; each joint pivots at its own (already moved) position.
    The sign is chosen so the probe point moves in the wanted direction of component Y (+1 forward / -1 back)."""
    cur = {b: cs[b] for b in chain}
    for k, b in enumerate(chain):
        cands = []
        for sgn in (1, -1):
            q = about_x(sgn * degrees[k])
            moved = cur[b].translation + q.rotate_vector(probe(cur).translation - cur[b].translation)
            cands.append((moved.y * want_more, sgn))
        sgn = max(cands)[1]
        q = about_x(sgn * degrees[k])
        pivot = cur[b].translation
        for b2 in chain[k:]:
            cur[b2] = spin(cur[b2], pivot, q)
    return cur


# Regie 2026-10-25: anatomically flat on the mattress, head raised on the pillow: neck flexed ~30 deg
# (chin toward the chest, as on a pillow); feet relaxed in plantar flexion (~35 deg) so the toes do not
# stand straight up under the duvet.
neck = bend_chain(["neck_01", "neck_02", "head"], [11, 11, 8], lambda c: c["head"], 1)
new.update(neck)
for side in ("l", "r"):
    f = f"foot_{side}"
    ball = cs[f"ball_{side}"]
    best = min((abs((cs[f].translation + about_x(b).rotate_vector(ball.translation - cs[f].translation)).y - 2.0), b) for b in range(-50, 51))
    q = about_x(best[1])
    new[f] = spin(cs[f], cs[f].translation, q)
    joints[side]["ball"] = list((cs[f].translation + q.rotate_vector(ball.translation - cs[f].translation)).to_tuple())
joints["head"] = list(neck["head"].translation.to_tuple())
print("C00_POSE head", [round(v, 1) for v in neck["head"].translation.to_tuple()], "ball_l", [round(v, 1) for v in joints["l"]["ball"]])

if eal.does_asset_exist(f"{DST}/{NAME}"):
    eal.delete_asset(f"{DST}/{NAME}")
fac = unreal.AnimSequenceFactory()
fac.set_editor_property("target_skeleton", skel)
anim = unreal.AssetToolsHelpers.get_asset_tools().create_asset(NAME, DST, unreal.AnimSequence, fac)
ctrl = anim.controller
ctrl.open_bracket("C00 lying pose", True)
ctrl.set_frame_rate(unreal.FrameRate(30, 1), True)
ctrl.set_number_of_frames(unreal.FrameNumber(1), True)
for bone in ("upperarm_l", "lowerarm_l", "upperarm_r", "lowerarm_r", "neck_01", "neck_02", "head", "foot_l", "foot_r"):
    par = PARENT[bone]
    local = MATH.make_relative_transform(new[bone], new.get(par, cs[par]))
    ctrl.add_bone_curve(bone, True)
    ctrl.set_bone_track_keys(bone, [local.translation] * 2, [local.rotation] * 2, [local.scale3d] * 2, True)
ctrl.close_bracket(True)
eal.save_loaded_asset(anim)
import json
with open(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()) + "docs/v4_2/C00_POSE_JOINTS.json", "w") as f:
    json.dump({"note": "MetaHuman component space (cm); joints = arms in A_C00_Mann_Liegen, a_pose = all bones", "joints": joints, "a_pose": a_pose}, f, indent=1)
print("C00_POSE_ASSET", anim.get_path_name())
