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
          "neck_01": "spine_05", "neck_02": "neck_01", "head": "neck_02", "foot_l": "calf_l", "foot_r": "calf_r",
          "hand_l": "lowerarm_l", "hand_r": "lowerarm_r", "thigh_r": "pelvis"}
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
         "calf_l", "calf_r", "foot_l", "foot_r", "ball_l", "ball_r", "middle_01_l", "middle_01_r",
         "index_01_l", "index_01_r", "pinky_01_l", "pinky_01_r")
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


# ------------------------------------------------------------------ arms resting ON the duvet (Regie 2026-10-25:
# "Haende auf die Decke wie bei einem Sterbenden, anatomisch korrekt"). Two-bone IK on the man's own limb lengths:
# upper arms beside the chest, elbows bent and resting on the duvet, hands flat (palm down) on the belly - the
# right hand a little lower than the left so the fingers do not cross. The duvet surface comes from the Blender
# cloth simulation (C00_BEDROOM_LYING.json "duvet_height_local", local cm; y = up when lying).
import json as _json
import os as _os
_LY = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()) + "docs/v4_2/C00_BEDROOM_LYING.json"
HMAP = _json.load(open(_LY, encoding="utf8")).get("duvet_height_local") if _os.path.exists(_LY) else None
MATTRESS_Y = -7.5                                         # mattress top in local y (body sinks 4.5 cm into it)
V3 = unreal.Vector


def duvet_y(x, z):
    if not HMAP:
        return MATTRESS_Y
    fx, fz = (x - HMAP["x0"]) / HMAP["step"], (z - HMAP["z0"]) / HMAP["step"]
    i, k = int(math.floor(fx)), int(math.floor(fz))
    if not (0 <= i < HMAP["nx"] - 1 and 0 <= k < HMAP["nz"] - 1):
        return MATTRESS_Y
    g = HMAP["y"]
    vals = [g[k][i], g[k][i + 1], g[k + 1][i], g[k + 1][i + 1]]
    vals = [MATTRESS_Y if v is None else v for v in vals]
    tx, tz = fx - i, fz - k
    return (vals[0] * (1 - tx) + vals[1] * tx) * (1 - tz) + (vals[2] * (1 - tx) + vals[3] * tx) * tz


def norm(v):
    l = v.length()
    return v * (1.0 / l) if l > 1e-6 else v


def frame_quat(d, n):
    """Quaternion of the frame with X along d and Z along n (orthogonalised)."""
    return MATH.make_rot_from_xz(norm(d), norm(n)).quaternion()


def qinv(q):
    return unreal.Quat(-q.x, -q.y, -q.z, q.w)          # unit quaternion inverse


def quat_from_to(a, b):
    a, b = norm(a), norm(b)
    c = a.cross(b)
    w = 1.0 + a.dot(b)
    if w < 1e-6:
        return unreal.Quat(0, 0, 1, 0)
    q = unreal.Quat(c.x, c.y, c.z, w)
    q.normalize()
    return q


def arm_ik(side, target):
    sx = 1 if side == "l" else -1
    up, lo, ha = f"upperarm_{side}", f"lowerarm_{side}", f"hand_{side}"
    S, E0, H0 = cs[up].translation, cs[lo].translation, cs[ha].translation
    L1, L2 = (E0 - S).length(), (H0 - E0).length()
    W = target
    d = min((W - S).length(), L1 + L2 - 0.5)
    u = norm(W - S)
    W = S + u * d
    a1 = (L1 * L1 + d * d - L2 * L2) / (2 * d)
    h = math.sqrt(max(L1 * L1 - a1 * a1, 0.0))
    best = None
    for deg in range(-30, 75, 3):                         # pole: outward, tilted down toward the mattress
        a = math.radians(deg)
        P = V3(sx * math.cos(a), -math.sin(a), 0.0)
        v = norm(P - u * P.dot(u))
        E = S + u * a1 + v * h
        pen = 0.0
        for t in (0.35, 0.65, 1.0):                        # upper arm (r 4.5) and forearm (r 4) above the duvet
            p = S + (E - S) * t
            pen += max(0.0, duvet_y(p.x, p.z) + 4.5 - p.y)
        for t in (0.3, 0.6):
            p = E + (W - E) * t
            pen += max(0.0, duvet_y(p.x, p.z) + 4.0 - p.y)
        rest = abs(E.y - (duvet_y(E.x, E.z) + 4.5))       # the elbow rests on the duvet
        score = pen * 10 + rest
        if best is None or score < best[0]:
            best = (score, E, deg)
    _, E, pole_deg = best
    nA = norm((E0 - S).cross(H0 - E0))
    nT = norm((E - S).cross(W - E))
    if nA.dot(nT) < 0:
        nT = nT * -1.0
    q1 = frame_quat(E - S, nT) * qinv(frame_quat(E0 - S, nA))
    chain = {b: spin(cs[b], S, q1) for b in (up, lo, ha, f"middle_01_{side}", f"index_01_{side}", f"pinky_01_{side}")}
    E1 = chain[lo].translation
    f1 = chain[ha].translation - E1
    q2 = quat_from_to(f1, W - E1)                          # hinge about nT (both lie in the bending plane)
    for b in (ha, f"middle_01_{side}", f"index_01_{side}", f"pinky_01_{side}"):
        chain[b] = spin(chain[b], E1, q2)
    chain[lo] = spin(chain[lo], E1, q2)
    Wc = chain[ha].translation
    dir_c = chain[f"middle_01_{side}"].translation - Wc
    across = chain[f"index_01_{side}"].translation - chain[f"pinky_01_{side}"].translation
    palm_c = norm(dir_c.cross(across))
    # A-pose: the palm faces the thigh (medially); keep that sign convention
    dA = cs[f"middle_01_{side}"].translation - H0
    pA = norm(dA.cross(cs[f"index_01_{side}"].translation - cs[f"pinky_01_{side}"].translation))
    if pA.dot(V3(-sx, 0, 0)) < 0:
        palm_c = palm_c * -1.0
    fore = norm(Wc - E1)
    flat = norm(V3(fore.x, 0.0, fore.z))
    dir_t = norm(flat - V3(0, 0.18, 0))                    # fingers relaxed slightly down onto the duvet
    palm_t = V3(0, -1, 0)
    q3 = frame_quat(dir_t, palm_t) * qinv(frame_quat(dir_c, palm_c))
    # swing-twist about the forearm: the twist turns the forearm (no candy-wrap at the wrist), the swing the hand
    proj = fore * V3(q3.x, q3.y, q3.z).dot(fore)
    tw = unreal.Quat(proj.x, proj.y, proj.z, q3.w)
    tw.normalize()
    sw = q3 * qinv(tw)
    chain[lo] = spin(chain[lo], E1, tw)
    for b in (ha, f"middle_01_{side}", f"index_01_{side}", f"pinky_01_{side}"):
        chain[b] = spin(chain[b], E1, tw)
    chain[ha] = spin(chain[ha], chain[ha].translation, sw)
    print("C00_POSE_IK", side, "pole", pole_deg, "elbow", [round(v, 1) for v in E.to_tuple()],
          "duvet@elbow", round(duvet_y(E.x, E.z), 1), "wrist", [round(v, 1) for v in W.to_tuple()])
    return {up: chain[up], lo: chain[lo], ha: chain[ha]}


if HMAP:
    for side, hx, hz in (("l", 10.5, 105.0), ("r", -10.5, 95.0)):
        new.update(arm_ik(side, V3(hx, duvet_y(hx, hz) + 3.0, hz)))

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
# Regie 2026-10-25: one foot looks out of the duvet - lying relaxed, the right leg falls ~25 deg outward
# (external rotation about the thigh axis); the duvet corner over it is turned back (build_c00_bedroom_occupied.py)
_th, _ca, _ba = cs["thigh_r"].translation, cs["calf_r"].translation, cs["ball_r"].translation
_ax = (_ca - _th)
_ax = _ax * (1.0 / _ax.length())


def _about(axis, deg):
    a = math.radians(deg) / 2
    return unreal.Quat(axis.x * math.sin(a), axis.y * math.sin(a), axis.z * math.sin(a), math.cos(a))


_q = min((_about(_ax, sg * 25.0) for sg in (1, -1)), key=lambda q: (_th + q.rotate_vector(_ba - _th)).x)  # toes outward (-x)
new["thigh_r"] = spin(cs["thigh_r"], _th, _q)
joints["r"]["ball_out"] = list((_th + _q.rotate_vector(_ba - _th)).to_tuple())
joints["r"]["foot_out"] = list((_th + _q.rotate_vector(cs["foot_r"].translation - _th)).to_tuple())
joints["head"] = list(neck["head"].translation.to_tuple())
print("C00_POSE head", [round(v, 1) for v in neck["head"].translation.to_tuple()], "ball_l", [round(v, 1) for v in joints["l"]["ball"]])

if eal.does_asset_exist(f"{DST}/{NAME}"):                 # in use by open scenes: rewrite in place, do not delete
    anim = eal.load_asset(f"{DST}/{NAME}")
else:
    fac = unreal.AnimSequenceFactory()
    fac.set_editor_property("target_skeleton", skel)
    anim = unreal.AssetToolsHelpers.get_asset_tools().create_asset(NAME, DST, unreal.AnimSequence, fac)
ctrl = anim.controller
ctrl.open_bracket("C00 lying pose", True)
ctrl.remove_all_bone_tracks(True)
ctrl.set_frame_rate(unreal.FrameRate(30, 1), True)
ctrl.set_number_of_frames(unreal.FrameNumber(1), True)
for bone in ("upperarm_l", "lowerarm_l", "upperarm_r", "lowerarm_r", "neck_01", "neck_02", "head", "foot_l", "foot_r") + (("hand_l", "hand_r") if HMAP else ()) + ("thigh_r",):
    par = PARENT[bone]
    local = MATH.make_relative_transform(new[bone], new.get(par, cs[par]))
    ctrl.add_bone_curve(bone, True)
    ctrl.set_bone_track_keys(bone, [local.translation] * 2, [local.rotation] * 2, [local.scale3d] * 2, True)
ctrl.close_bracket(True)
eal.save_loaded_asset(anim)
import json
with open(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()) + "docs/v4_2/C00_POSE_JOINTS.json", "w") as f:
    def _tq(t):
        q = t.rotation
        return [list(t.translation.to_tuple()), [q.x, q.y, q.z, q.w]]
    posed = {b: {"ref": _tq(cs[b]), "new": _tq(new[b])} for b in new}     # Blender reproduces the posed body
    json.dump({"note": "MetaHuman component space (cm); joints = arms in A_C00_Mann_Liegen, a_pose = all bones, "
                       "posed = component-space ref/new transforms of every posed bone (parents first in PARENT order)",
               "joints": joints, "a_pose": a_pose, "posed": posed, "parent": PARENT}, f, indent=1)
print("C00_POSE_ASSET", anim.get_path_name())
