"""C00 (runs INSIDE the Unreal Editor): the moving animations for shot 00-B (18 s, 24 fps = 432 frames).

Shot list 00-B (approved by the Game Director 2026-10-25): his hand in his daughter's hand, her thumb moves; rain, sheets,
breathing; no forced sobbing. Built on the approved single-frame poses (A_C00_Mann_Liegen_Built,
A_C00_Mann_Gesicht_Sterbend_Built, A_C00_Tochter_Sitzen_Built, A_C00_Tochter_Gesicht_00B_Built), every frame keyed:
- her thumb strokes the back of his hand: three slow strokes (~3.2 s each, eased in/out), about the palm normal
- his breath: slow, heavy, ~6.5 s per breath with a longer exhale - shoulders rise a little (clavicles), the jaw
  opens a hair on the inhale (face rig curve); his spine stays as posed so face and body never part at the neck
- her breath: calm, ~4.2 s, a gentle lift through the upper spine - applied identically to her body and face
  animations (they share the spine/neck/head joints)
- she blinks twice (natural, ~150 ms)
Outputs *_00B_Built next to the poses. Translations stay as keyed in the poses (the built figures' runtime adds
their DNA offsets on top, see c00_pose_tochter.py).
"""
import math

import unreal

POSEN = "/Game/Genesis/Characters/C00/Posen"
FPS, SECONDS = 24, 18.0
N = int(FPS * SECONDS)                       # frames; keys = N + 1
eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
AL = unreal.AnimationLibrary
MATH = unreal.MathLibrary
CS = unreal.RelativeTransformSpace.RTS_COMPONENT
V = unreal.Vector
FLOAT = unreal.RawCurveTrackTypes.RCT_FLOAT


def q_axis(axis, deg):
    l = axis.length()
    n = axis * (1.0 / l) if l > 1e-6 else V(1, 0, 0)
    a = math.radians(deg) / 2
    return unreal.Quat(n.x * math.sin(a), n.y * math.sin(a), n.z * math.sin(a), math.cos(a))


def qinv(q):
    return unreal.Quat(-q.x, -q.y, -q.z, q.w)


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def base_tracks(anim):
    names = [str(n) for n in AL.get_animation_track_names(anim)]
    return {n: AL.get_bone_pose_for_frame(anim, n, 0, False) for n in names}


def base_curves(anim):
    out = {}
    for c in AL.get_animation_curve_names(anim, FLOAT):
        times, values = AL.get_float_keys(anim, c)
        out[str(c)] = values[0] if values else 0.0
    return out


def write(name, skeleton, frames_tracks, frames_curves):
    """frames_tracks: list (N+1) of {bone: Transform local}; frames_curves: list (N+1) of {curve: value}"""
    path = f"{POSEN}/{name}"
    anim = eal.load_asset(path) if eal.does_asset_exist(path) else None
    if anim is None:
        fac = unreal.AnimSequenceFactory()
        fac.set_editor_property("target_skeleton", skeleton)
        anim = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, POSEN, unreal.AnimSequence, fac)
    ctrl = anim.controller
    ctrl.open_bracket(name, True)
    ctrl.remove_all_bone_tracks(True)
    ctrl.remove_all_curves_of_type(FLOAT, True)
    ctrl.set_frame_rate(unreal.FrameRate(FPS, 1), True)
    ctrl.set_number_of_frames(unreal.FrameNumber(N), True)
    for b in frames_tracks[0]:
        try:
            ctrl.add_bone_curve(b, False)
        except RuntimeError:
            continue
        ctrl.set_bone_track_keys(b, [f[b].translation for f in frames_tracks], [f[b].rotation for f in frames_tracks],
                                 [f[b].scale3d for f in frames_tracks], True)
    ctrl.close_bracket(True)
    times = [i / FPS for i in range(N + 1)]
    for c in frames_curves[0]:
        AL.add_curve(anim, c, FLOAT, False)
        AL.add_float_curve_keys(anim, c, times, [f[c] for f in frames_curves])
    eal.save_loaded_asset(anim, False)
    return anim


def fk(locals_, parent, order):
    cs = {}
    for b in order:
        if b not in locals_:
            continue
        p = parent.get(b)
        cs[b] = MATH.compose_transforms(locals_[b], cs[p]) if p in cs else locals_[b]
    return cs


def rotate_local(local, parent_cs_rot, q_cs):
    """rotate a bone by q_cs (component space, about its own joint) - parent unchanged"""
    rot = qinv(parent_cs_rot) * q_cs * parent_cs_rot * local.rotation
    return unreal.Transform(location=local.translation, rotation=rot.rotator(), scale=local.scale3d)


def probe_skeleton(bp_path):
    bp = eal.load_blueprint_class(bp_path)
    a = eas.spawn_actor_from_class(bp, V(0, 0, -800), unreal.Rotator(0, 0, 0))
    body = next(c for c in a.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Body")
    names = [str(body.get_bone_name(i)) for i in range(body.get_num_bones())]
    parent = {b: str(body.get_parent_bone(b)) for b in names}
    ref_cs = {b: body.get_socket_transform(b, CS) for b in names}
    skel = body.get_skeletal_mesh_asset().skeleton
    eas.destroy_actor(a)
    ref_local = {b: (MATH.make_relative_transform(ref_cs[b], ref_cs[parent[b]]) if parent[b] in ref_cs else ref_cs[b]) for b in names}
    return names, parent, ref_local, skel


t_of = [i / FPS for i in range(N + 1)]
X = V(1, 0, 0)

# ------------------------------------------------------------------ the man: breath in the shoulders and the jaw
m_names, m_parent, m_ref, m_skel = probe_skeleton("/Game/Genesis/Characters/C00/Built/Mann/MHC_C00_Mann/BP_MHC_C00_Mann")
m_body = eal.load_asset(f"{POSEN}/A_C00_Mann_Liegen_Built")
m_face = eal.load_asset(f"{POSEN}/A_C00_Mann_Gesicht_Sterbend_Built")
mb, mf, mfc = base_tracks(m_body), base_tracks(m_face), base_curves(m_face)
m_loc = dict(m_ref)
m_loc.update(mb)
m_cs = fk(m_loc, m_parent, m_names)


def breath_man(t):
    """0..1 inhale; 6.5 s cycle: 2.4 s in, 4.1 s out (a dying, heavy breath)"""
    ph = (t % 6.5)
    return smooth(ph / 2.4) if ph < 2.4 else 1.0 - smooth((ph - 2.4) / 4.1)


frames_mb, frames_mf, curves_mf = [], [], []
for t in t_of:
    b = breath_man(t)
    f = dict(mb)
    for side, sx in (("l", 1), ("r", -1)):
        cl = f"clavicle_{side}"
        if cl in m_loc:
            par = m_cs[m_parent[cl]].rotation
            # shoulders lift toward the head (component +Z when standing = toward the headboard when lying)
            f[cl] = rotate_local(m_loc[cl], par, q_axis(V(0, 1, 0), sx * 1.6 * b))
    frames_mb.append(f)
    frames_mf.append(dict(mf))
    c = dict(mfc)
    c["CTRL_expressions_jawOpenL"] = c.get("CTRL_expressions_jawOpenL", 0.05) + 0.05 * b
    c["CTRL_expressions_jawOpenR"] = c.get("CTRL_expressions_jawOpenR", 0.05) + 0.05 * b
    for s in ("L", "R"):
        c[f"CTRL_expressions_noseNostrilDilate{s}"] = 0.15 * b
    curves_mf.append(c)
write("A_C00_Mann_Liegen_00B_Built", m_skel, frames_mb, [{} for _ in t_of])
face_skel = eal.load_asset("/Game/Genesis/Characters/C00/Built/Common/Face/Face_Archetype_Skeleton")
write("A_C00_Mann_Gesicht_00B_Built", face_skel, frames_mf, curves_mf)

# ------------------------------------------------------------------ the daughter: thumb stroke, breath, blinks
t_names, t_parent, t_ref, t_skel = probe_skeleton("/Game/Genesis/Characters/C00/Built/Tochter/MHC_C00_Tochter/BP_MHC_C00_Tochter")
t_body = eal.load_asset(f"{POSEN}/A_C00_Tochter_Sitzen_Built")
t_face = eal.load_asset(f"{POSEN}/A_C00_Tochter_Gesicht_00B_Built")
tb, tf, tfc = base_tracks(t_body), base_tracks(t_face), base_curves(t_face)
t_loc = dict(t_ref)
t_loc.update(tb)
t_cs = fk(t_loc, t_parent, t_names)
hand = t_cs["hand_r"]
palm_n = (t_cs["middle_01_r"].translation - hand.translation).cross(t_cs["index_01_r"].translation - t_cs["pinky_01_r"].translation)


def stroke(t):
    """three slow thumb strokes between 2.0 s and 15.6 s (0..1 out-and-back each 3.2 s, eased at the ends)"""
    if t < 2.0 or t > 2.0 + 3 * 3.2 + 1.6:
        return 0.0
    env = smooth((t - 2.0) / 0.8) * (1.0 - smooth((t - (2.0 + 3 * 3.2)) / 1.6))
    return env * (0.5 - 0.5 * math.cos(2 * math.pi * (t - 2.0) / 3.2))


def breath_daughter(t):
    return 0.5 - 0.5 * math.cos(2 * math.pi * t / 4.2)


def blink(t):
    v = 0.0
    for tc in (4.2, 11.8):
        d = abs(t - tc)
        if d < 0.09:
            v = max(v, 1.0 - d / 0.09)
    return v


SPINE = (("spine_03", 0.35), ("spine_04", 0.45), ("spine_05", 0.35))
frames_tb, frames_tf, curves_tf = [], [], []
for t in t_of:
    f = dict(tb)
    s = stroke(t)
    for th, w in (("thumb_01_r", 1.0), ("thumb_02_r", 0.45)):
        if th in t_loc:
            f[th] = rotate_local(t_loc[th], t_cs[t_parent[th]].rotation, q_axis(palm_n, 11.0 * w * s))
    br = breath_daughter(t)
    spine_new = {}
    for sb, deg in SPINE:
        if sb in t_loc:
            # upper body lifts and opens a little on the inhale (extension about component X)
            spine_new[sb] = rotate_local(t_loc[sb], t_cs[t_parent[sb]].rotation, q_axis(X, -deg * br))
            f[sb] = spine_new[sb]
    frames_tb.append(f)
    g = dict(tf)
    for sb, tr in spine_new.items():
        if sb in g:
            g[sb] = tr
    frames_tf.append(g)
    c = dict(tfc)
    bl = blink(t)
    for side in ("L", "R"):
        k = f"CTRL_expressions_eyeBlink{side}"
        c[k] = c.get(k, 0.18) + (1.0 - c.get(k, 0.18)) * bl
    curves_tf.append(c)
write("A_C00_Tochter_Sitzen_00B_Built", t_skel, frames_tb, [{} for _ in t_of])
write("A_C00_Tochter_Gesicht_00B_Anim_Built", face_skel, frames_tf, curves_tf)
print("C00_ANIM_00B", N, "frames", "man tracks", len(frames_mb[0]), "daughter tracks", len(frames_tb[0]))
