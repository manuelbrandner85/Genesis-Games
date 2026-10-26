"""C00 (runs INSIDE the Unreal Editor, level L_C00_Schlafzimmer with MH_C00_Mann): the daughter's seated pose for the
technical test of shot 00-B.

Regie 2026-10-25: "Tochter sitzt auf dem Stuhl an der Fensterseite des Betts auf Hueftoehe, beugt sich vor und haelt
seine Hand" (the man's window-side hand is his LEFT one, lying beside his hip on the duvet - c00_pose_lying.py).
Chair: tools/v4_2/place_c00_chair.py (seat centre Blender (0.88, 0.48), top 0.48 m, facing the bed = Unreal -X).

Built from the built MetaHuman's own reference skeleton (one frame, every body bone keyed in component space):
- pelvis on the seat (hip joints ~10 cm above the seat top), spine leaning ~40 deg toward the bed
- hips and knees bent so the feet stand flat on the floor (searched, not guessed: ankle 8.6 cm above the floor)
- right hand: two-bone IK onto the back of his hand, palm down, fingers wrapped around it (her thumb along his)
- left hand: resting on her left thigh
- neck and head bowed toward his hand
Outputs A_C00_Tochter_Sitzen_Built (body), A_C00_Tochter_Gesicht_00B_Built (face: same spine/neck/head tracks plus a
quiet, tired expression through the face rig) and docs/v4_2/C00_TOCHTER_SITZ.json (actor transform for the scene).
"""
import json
import math

import unreal

POSEN = "/Game/Genesis/Characters/C00/Posen"
eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
AL = unreal.AnimationLibrary
MATH = unreal.MathLibrary
CS, W = unreal.RelativeTransformSpace.RTS_COMPONENT, unreal.RelativeTransformSpace.RTS_WORLD
V = unreal.Vector
ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())

SEAT_TOP = 48.0                                          # Unreal cm (Blender 0.48 m)
PELVIS_WORLD = V(89.0, -48.0, SEAT_TOP + 10.0)           # sits forward on the seat (seat centre x 102): she holds his hand
YAW = 90.0                                               # component +Y (face) -> world -X (toward the bed)
FLOOR = 0.0


def norm(v):
    l = v.length()
    return v * (1.0 / l) if l > 1e-6 else v


def q_axis(axis, deg):
    n = norm(axis)
    a = math.radians(deg) / 2
    return unreal.Quat(n.x * math.sin(a), n.y * math.sin(a), n.z * math.sin(a), math.cos(a))


def qinv(q):
    return unreal.Quat(-q.x, -q.y, -q.z, q.w)


def frame_quat(d, n):
    return MATH.make_rot_from_xz(norm(d), norm(n)).quaternion()


def quat_from_to(a, b):
    a, b = norm(a), norm(b)
    c = a.cross(b)
    w = 1.0 + a.dot(b)
    if w < 1e-6:
        return unreal.Quat(0, 0, 1, 0)
    q = unreal.Quat(c.x, c.y, c.z, w)
    q.normalize()
    return q


# ------------------------------------------------------------------ reference skeleton of the built daughter
bp = eal.load_blueprint_class("/Game/Genesis/Characters/C00/Built/Tochter/MHC_C00_Tochter/BP_MHC_C00_Tochter")
probe = eas.spawn_actor_from_class(bp, V(0, 0, -500), unreal.Rotator(0, 0, 0))
body = next(c for c in probe.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Body")
names = [str(body.get_bone_name(i)) for i in range(body.get_num_bones())]
parent = {b: str(body.get_parent_bone(b)) for b in names}
cur = {b: body.get_socket_transform(b, CS) for b in names}
# The built body's post-process graph (RigLogic, body DNA) ADDS a fixed per-joint offset to every translation the
# animation provides (template -> her real proportions: pelvis +10 cm, forearm +4.6 cm ...). The pose is therefore
# SOLVED on the rendered lengths (template + DNA offset, measured on the daughter standing in the level: live minus
# keyed) but KEYED with the template translations; the runtime adds the offset back. (Solving on the template put her
# hand 13 cm off; keying the rendered lengths made her grow by the offset on every run.)
TEMPLATE_T = {}
for b in names:
    pr = parent[b]
    TEMPLATE_T[b] = (MATH.make_relative_transform(cur[b], cur[pr]) if pr in cur else cur[b]).translation
_live = next((a for a in eas.get_all_level_actors() if a.get_actor_label() == "MH_C00_Tochter"), None)
_prev = eal.load_asset(f"{POSEN}/A_C00_Tochter_Sitzen_Built") if eal.does_asset_exist(f"{POSEN}/A_C00_Tochter_Sitzen_Built") else None
if _live and _prev:
    _lb = next(c for c in _live.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Body")
    _PB = unreal.RelativeTransformSpace.RTS_PARENT_BONE_SPACE
    _tmpl = dict(cur)
    for b in names:                                       # bone index order: parents first
        pr = parent[b]
        rl = MATH.make_relative_transform(_tmpl[b], _tmpl[pr]) if pr in _tmpl else _tmpl[b]
        dna = _lb.get_socket_transform(b, _PB).translation - AL.get_bone_pose_for_frame(_prev, b, 0, False).translation
        loc = unreal.Transform(location=TEMPLATE_T[b] + dna, rotation=rl.rotation.rotator(), scale=rl.scale3d)
        cur[b] = MATH.compose_transforms(loc, cur[pr]) if pr in cur else loc
    print("C00_TOCHTER_DNA_LENGTHS pelvis", round(cur["pelvis"].translation.z, 1), "head", round(cur["head"].translation.z, 1))
ref = dict(cur)
skel = body.get_skeletal_mesh_asset().skeleton
eas.destroy_actor(probe)
children = {b: [] for b in names}
for b in names:
    if parent[b] in children:
        children[parent[b]].append(b)


def subtree(b):
    out, stack = [], [b]
    while stack:
        x = stack.pop()
        out.append(x)
        stack.extend(children[x])
    return out


def rotate(b, q, pivot=None):
    piv = cur[b].translation if pivot is None else pivot
    for d in subtree(b):
        t = cur[d]
        cur[d] = unreal.Transform(location=piv + q.rotate_vector(t.translation - piv),
                                  rotation=(q * t.rotation).rotator(), scale=t.scale3d)


def p(b):
    return cur[b].translation


def bend(b, axis, deg, probe_fn):
    """rotate bone b about axis by +-deg, choosing the sign that maximises probe_fn() afterwards"""
    best = None
    snap = {d: cur[d] for d in subtree(b)}
    for sg in (1, -1):
        rotate(b, q_axis(axis, sg * deg))
        score = probe_fn()
        for d, t in snap.items():
            cur[d] = t
        if best is None or score > best[0]:
            best = (score, sg)
    rotate(b, q_axis(axis, best[1] * deg))
    return best[1]


X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
# ------------------------------------------------------------------ actor placement: pelvis onto the seat
yaw_q = unreal.Rotator(0, 0, YAW).quaternion()
pel = ref["pelvis"].translation
actor_loc = PELVIS_WORLD - yaw_q.rotate_vector(pel)
floor_cs = FLOOR - actor_loc.z                           # floor height in component space


def to_cs(world):
    return qinv(yaw_q).rotate_vector(world - actor_loc)


# ------------------------------------------------------------------ torso leaning toward the bed
for b, deg in (("spine_01", 16), ("spine_02", 15), ("spine_03", 11), ("spine_04", 7), ("spine_05", 4)):
    if b in cur:
        bend(b, X, deg, lambda: p("head").y)
# reaching for his hand: the right shoulder blade slides forward (protraction ~16 deg at the clavicle), the upper
# body turns a little into the reach
if "clavicle_r" in cur:
    bend("clavicle_r", Z, 20, lambda: p("upperarm_r").y)
for b, deg in (("spine_03", 4), ("spine_04", 4), ("spine_05", 3)):
    if b in cur:
        bend(b, Z, deg, lambda: p("upperarm_r").y - p("upperarm_l").y)

# ------------------------------------------------------------------ legs: thighs forward, shins down, feet flat
for side, sx in (("l", 1), ("r", -1)):
    th, ca, ft, ba = f"thigh_{side}", f"calf_{side}", f"foot_{side}", f"ball_{side}"
    snap = {d: cur[d] for d in subtree(th)}
    best = None
    for hip in range(66, 98, 2):
        for d, t in snap.items():
            cur[d] = t
        bend(th, X, hip, lambda: p(ca).y)
        rotate(th, q_axis(Y, sx * 5.0))                 # knees a little apart
        kn = p(ca)
        # knee: shin down and slightly forward of the knee
        knee_best = None
        snap2 = {d: cur[d] for d in subtree(ca)}
        for k in range(50, 130, 2):
            for d, t in snap2.items():
                cur[d] = t
            bend(ca, X, k, lambda: -p(ft).y)
            err = abs(p(ft).y - (kn.y + 4.0))
            if knee_best is None or err < knee_best[0]:
                knee_best = (err, k)
        for d, t in snap2.items():
            cur[d] = t
        bend(ca, X, knee_best[1], lambda: -p(ft).y)
        err = abs(p(ft).z - (floor_cs + 8.6))
        if best is None or err < best[0]:
            best = (err, hip, knee_best[1])
    for d, t in snap.items():
        cur[d] = t
    bend(th, X, best[1], lambda: p(ca).y)
    rotate(th, q_axis(Y, sx * 5.0))
    bend(ca, X, best[2], lambda: -p(ft).y)
    # foot flat: ball at the floor too
    fb = None
    snapf = {d: cur[d] for d in subtree(ft)}
    for a in range(-40, 41, 2):
        for d, t in snapf.items():
            cur[d] = t
        rotate(ft, q_axis(X, a))
        e = abs(p(ba).z - (floor_cs + 2.0)) + (0 if p(ba).y > p(ft).y else 50)
        if fb is None or e < fb[0]:
            fb = (e, a)
    for d, t in snapf.items():
        cur[d] = t
    rotate(ft, q_axis(X, fb[1]))
    print("C00_TOCHTER_LEG", side, "hip", best[1], "knee", best[2], "ankle_err", round(best[0], 1),
          "ball_z", round(p(ba).z - floor_cs, 1))

# ------------------------------------------------------------------ arms (two-bone IK + hand frame)
man = next(a for a in eas.get_all_level_actors() if a.get_actor_label() == "MH_C00_Mann")
mbody = next(c for c in man.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Body")
m_hand, m_mid = mbody.get_socket_transform("hand_l", W).translation, mbody.get_socket_transform("middle_01_l", W).translation
m_idx, m_pky = mbody.get_socket_transform("index_01_l", W).translation, mbody.get_socket_transform("pinky_01_l", W).translation
# her palm joint above his palm centre: his back of hand (+1.5) + her palm (+1.5) + clearance for the skinned skin
# surfaces (Regie 2026-10-25: at +3.0 "die Hand ... in der Hand des Mannes" - her fingers sank into his hand)
m_palm = (m_hand + m_mid) * 0.5 + V(0, 0, 4.2)


def arm_ik(side, wrist_w, pole, d_t, p_t):
    sx = 1 if side == "l" else -1
    up, lo, ha = f"upperarm_{side}", f"lowerarm_{side}", f"hand_{side}"
    S, E0, H0 = p(up), p(lo), p(ha)
    L1, L2 = (E0 - S).length(), (H0 - E0).length()
    Wt = wrist_w
    d = min((Wt - S).length(), L1 + L2 - 0.5)
    print("C00_TOCHTER_ARM", side, "need", round((Wt - S).length(), 1), "max", round(L1 + L2 - 0.5, 1))
    u = norm(Wt - S)
    Wt = S + u * d
    a1 = (L1 * L1 + d * d - L2 * L2) / (2 * d)
    h = math.sqrt(max(L1 * L1 - a1 * a1, 0.0))
    v = norm(pole - u * pole.dot(u))
    E = S + u * a1 + v * h
    nA = norm((E0 - S).cross(H0 - E0))
    nT = norm((E - S).cross(Wt - E))
    if nA.dot(nT) < 0:
        nT = nT * -1.0
    rotate(up, frame_quat(E - S, nT) * qinv(frame_quat(E0 - S, nA)), S)
    E1 = p(lo)
    rotate(lo, quat_from_to(p(ha) - E1, Wt - E1), E1)
    # hand frame: fingers along d_t, palm normal p_t
    Wc = p(ha)
    dir_c = p(f"middle_01_{side}") - Wc
    across = p(f"index_01_{side}") - p(f"pinky_01_{side}")
    palm_c = norm(dir_c.cross(across))
    dA = ref[f"middle_01_{side}"].translation - ref[ha].translation
    pA = norm(dA.cross(ref[f"index_01_{side}"].translation - ref[f"pinky_01_{side}"].translation))
    if pA.dot(V(-sx, 0, 0)) < 0:                        # A-pose: palm toward the thigh (medial)
        palm_c = palm_c * -1.0
    q3 = frame_quat(norm(d_t), norm(p_t)) * qinv(frame_quat(dir_c, palm_c))
    # pronation: not the whole forearm (that wrung the elbow and sleeve, Regie 2026-10-25) - the hand takes the full
    # rotation, the forearm twist joints their share by distance from the elbow
    fore = norm(Wc - E1)
    proj = fore * V(q3.x, q3.y, q3.z).dot(fore)
    tw = unreal.Quat(proj.x, proj.y, proj.z, q3.w)
    tw.normalize()
    ang = 2.0 * math.acos(max(-1.0, min(1.0, tw.w)))
    sn = math.sin(ang / 2)
    axis = V(tw.x / sn, tw.y / sn, tw.z / sn) if sn > 1e-6 else fore
    L = max((Wc - E1).length(), 1e-3)
    for tb in (f"lowerarm_twist_01_{side}", f"lowerarm_twist_02_{side}"):
        if tb in cur:
            f = max(0.0, min(1.0, (p(tb) - E1).dot(fore) / L))
            rotate(tb, q_axis(axis, math.degrees(ang * f)), p(tb))
    rotate(ha, q3, Wc)
    return E


def curl(side, base_deg):
    """fingers wrap around: with the palm facing down, each joint bends so that its tip moves down"""
    for f, scale in (("index", 1.0), ("middle", 1.05), ("ring", 1.1), ("pinky", 1.15)):
        for k, part in enumerate(("01", "02", "03")):
            b = f"{f}_{part}_{side}"
            if b not in cur or not children[b]:
                continue
            tip = children[b][0]
            across = p(f"index_01_{side}") - p(f"pinky_01_{side}")
            bend(b, across, base_deg[k] * scale, lambda tip=tip: -p(tip).z)


def curl_up(side, base_deg):
    """palm up: fingers bend so that their tips rise (cupping under something)"""
    for f, scale in (("index", 1.0), ("middle", 1.05), ("ring", 1.1), ("pinky", 1.15)):
        for k, part in enumerate(("01", "02", "03")):
            b = f"{f}_{part}_{side}"
            if b not in cur or not children[b]:
                continue
            tip = children[b][0]
            across = p(f"index_01_{side}") - p(f"pinky_01_{side}")
            sg = 1.0 if base_deg[k] >= 0 else -1.0                  # negative: the tips go down (straighten)
            bend(b, across, abs(base_deg[k]) * scale, lambda tip=tip, sg=sg: sg * p(tip).z)


def thumb_over(side, target):
    """thumb from the upturned palm over the edge of his hand onto its back: thumb_01 searched over two axes so the
    thumb tip lands on target (component space), then the end joints bend gently onto the surface"""
    t1, t2, t3 = f"thumb_01_{side}", f"thumb_02_{side}", f"thumb_03_{side}"
    if t1 not in cur or t3 not in cur:
        return
    tip_b = children[t3][0] if children[t3] else t3
    snap = {d: cur[d] for d in subtree(t1)}
    ix = f"index_01_{side}"
    across = norm(p(ix) - p(f"pinky_01_{side}"))
    palm_n = norm((p(f"middle_01_{side}") - p(f"hand_{side}")).cross(p(ix) - p(f"pinky_01_{side}")))
    ax3 = norm(across.cross(palm_n))
    reach = (p(t1) - target).length()
    tlen = (p(t2) - p(t1)).length() + (p(t3) - p(t2)).length() + (p(tip_b) - p(t3)).length()

    def pose(a, b, c):
        for d, t in snap.items():
            cur[d] = t
        rotate(t1, q_axis(across, a))
        rotate(t1, q_axis(palm_n, b))
        rotate(t1, q_axis(ax3, c))
    best = None
    for a in range(-120, 121, 10):                          # coarse, then fine around the best
        for b in range(-90, 91, 10):
            for c in range(-60, 61, 20):
                pose(a, b, c)
                e = (p(tip_b) - target).length()
                if best is None or e < best[0]:
                    best = (e, a, b, c)
    _, A, B, C = best
    for a in range(A - 10, A + 11, 2):
        for b in range(B - 10, B + 11, 2):
            for c in range(C - 20, C + 21, 4):
                pose(a, b, c)
                e = (p(tip_b) - target).length()
                if e < best[0]:
                    best = (e, a, b, c)
    pose(*best[1:])
    print("C00_TOCHTER_THUMB reach", round(reach, 1), "len", round(tlen, 1))
    for tb, deg in ((t2, 8), (t3, 10)):                     # end joints settle onto his hand
        if tb in cur and children[tb]:
            tip = children[tb][0]
            bend(tb, across, deg, lambda tip=tip: -p(tip).z)
    print("C00_TOCHTER_THUMB err", round(best[0], 2), "cm", best[1:], "tip", [round(v, 1) for v in p(tip_b).to_tuple()])


def thumb_alongside(side):
    """Regie 2026-10-25 ("Daumen sehr kurz, anatomisch falsch"): curled with the fingers, the thumb pointed down under
    the hand and read stubby. A resting thumb lies stretched beside the hand: a little abducted from the index finger
    (in the palm plane) and lifted so its tip stays on top instead of digging in."""
    t1, t3, ix = f"thumb_01_{side}", f"thumb_03_{side}", f"index_01_{side}"
    if t1 not in cur or t3 not in cur:
        return
    palm_n = norm((p(f"middle_01_{side}") - p(f"hand_{side}")).cross(p(ix) - p(f"pinky_01_{side}")))
    bend(t1, palm_n, 14, lambda: (p(t3) - p(ix)).length())          # away from the index finger
    across = p(ix) - p(f"pinky_01_{side}")
    bend(t1, across, 8, lambda: p(t3).z)                            # tip up, not into his hand / her thigh


# her right hand HOLDS his hand (ScriptLock 00-B: "Die Hand des Mannes ruht in der Hand seiner Tochter"; Regie QA
# 2026-10-26): palm up, her fingers slid under his palm from his little-finger side (they press into the soft down duvet,
# which gets a matching dent in build_c00_bedroom_occupied.py), her thumb lies on the back of his hand - where it moves.
m_c = (m_hand + m_mid) * 0.5                               # his palm centre (hand joint level)
m_side = norm(m_pky - m_idx)                                # toward his little finger = toward her
m_fing = norm(m_mid - m_hand)                               # his finger direction
knuckle_w = m_c + V(0, 0, -3.8)                            # her finger roots under his palm centre, 3.8 cm below his hand joints
m_side_h, m_fing_h = norm(V(m_side.x, m_side.y, 0)), norm(V(m_fing.x, m_fing.y, 0))   # his hand tilts with the duvet
d_w = norm(m_side_h * -1.0 + m_fing_h * 0.15 + V(0, 0, -0.08))        # her fingers across under his palm, nearly level
d_r = norm(to_cs(knuckle_w + d_w) - to_cs(knuckle_w))
up_cs = qinv(yaw_q).rotate_vector(V(0, 0, 1))
wrist_r = to_cs(knuckle_w) - d_r * 8.5
E_r = arm_ik("r", wrist_r, V(-1.0, 0.0, -0.6), d_r, up_cs)
curl_up("r", (-7, -7, -4))                                 # the rest pose curl would lift the tips into his palm: straighten flat
thumb_over("r", to_cs(m_c + m_side_h * 0.8 + m_fing_h * 1.5 + V(0, 0, 1.9)))   # thumb over his little-finger edge onto the back of his hand
# left hand on her left thigh, fingers toward the knee
th_l, kn_l = p("thigh_l"), p("calf_l")
wrist_l = th_l + (kn_l - th_l) * 0.45 + V(0, 0, 12.0)      # on the thigh (at +9 the hand sank into it)
E_l = arm_ik("l", wrist_l, V(1.0, -0.3, -0.5), norm(kn_l - th_l) + V(-0.15, 0, 0), V(0, 0, -1))
curl("l", (6, 8, 5))
thumb_alongside("l")

# ------------------------------------------------------------------ neck and head bowed toward his hand
bend("neck_01", X, 10, lambda: p("head").y)
bend("neck_02", X, 8, lambda: p("head").y)
_up_l = qinv(ref["head"].rotation).rotate_vector(Z)      # head-local "crown" and "face" axes from the reference pose
_fw_l = qinv(ref["head"].rotation).rotate_vector(Y)
bend("head", X, 12, lambda: cur["head"].rotation.rotate_vector(_up_l).y)          # crown forward = chin down
bend("neck_02", Z, 12, lambda: -cur["head"].rotation.rotate_vector(_fw_l).x)      # face turns toward his face (-X)

# ------------------------------------------------------------------ write the body pose (every bone)
def write(name, bones, extra_curves=None, skeleton=None):
    path = f"{POSEN}/{name}"
    anim = eal.load_asset(path) if eal.does_asset_exist(path) else None
    if anim is None:
        fac = unreal.AnimSequenceFactory()
        fac.set_editor_property("target_skeleton", skeleton)
        anim = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, POSEN, unreal.AnimSequence, fac)
    ctrl = anim.controller
    ctrl.open_bracket(name, True)
    ctrl.remove_all_bone_tracks(True)
    ctrl.remove_all_curves_of_type(unreal.RawCurveTrackTypes.RCT_FLOAT, True)
    ctrl.set_frame_rate(unreal.FrameRate(30, 1), True)
    ctrl.set_number_of_frames(unreal.FrameNumber(1), True)
    n = 0
    for b in bones:
        par = parent.get(b, "None")
        local = MATH.make_relative_transform(cur[b], cur[par]) if par in cur else cur[b]
        if b in TEMPLATE_T:                              # template translation: the runtime adds the DNA offset
            local = unreal.Transform(location=TEMPLATE_T[b], rotation=local.rotation.rotator(), scale=local.scale3d)
        try:
            ctrl.add_bone_curve(b, False)
        except RuntimeError:
            continue
        ctrl.set_bone_track_keys(b, [local.translation] * 2, [local.rotation] * 2, [local.scale3d] * 2, True)
        n += 1
    ctrl.close_bracket(True)
    for cname, val in (extra_curves or {}).items():
        AL.add_curve(anim, cname, unreal.RawCurveTrackTypes.RCT_FLOAT, False)
        AL.add_float_curve_keys(anim, cname, [0.0, 1 / 30], [val, val])
    eal.save_loaded_asset(anim, False)
    return n


nb = write("A_C00_Tochter_Sitzen_Built", names, skeleton=skel)
# face: shared spine/neck/head tracks + a quiet, tired, attentive face (ScriptLock: "gefasst, muede Augen")
face_skel = eal.load_asset("/Game/Genesis/Characters/C00/Built/Common/Face/Face_Archetype_Skeleton")
FACE = {"eyeBlink": 0.18, "eyeLookDown": 0.35, "eyeRelax": 0.25, "browRaiseIn": 0.22, "browLateral": 0.05,
        "mouthCornerDepress": 0.10, "mouthLipsPress": 0.12, "eyeSquintInner": 0.08}
curves = {f"CTRL_expressions_{k}{s}": v for k, v in FACE.items() for s in ("L", "R")}
shared = [b for b in names if b in ("root", "pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "spine_05",
                                    "neck_01", "neck_02", "head")]
nf = write("A_C00_Tochter_Gesicht_00B_Built", shared, curves, skeleton=face_skel)
out = {"note": "Unreal world cm / deg; actor of BP_MHC_C00_Tochter (tools/v4_2/c00_pose_tochter.py)",
       "location": list(actor_loc.to_tuple()), "yaw": YAW,
       "hand_r_world": list((actor_loc + yaw_q.rotate_vector(p("hand_r"))).to_tuple()),
       "man_hand_l_world": list(m_hand.to_tuple()),
       # her finger and thumb joints in world space: the duvet dents under her fingers (build_c00_bedroom_occupied.py)
       "hand_bones": {b: list((actor_loc + yaw_q.rotate_vector(p(b))).to_tuple()) for b in names
                      if b.endswith("_r") and b.startswith(("hand", "index", "middle", "ring", "pinky", "thumb"))},
       "expected_world": {b: list((actor_loc + yaw_q.rotate_vector(p(b))).to_tuple())
                          for b in ("pelvis", "spine_05", "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r", "calf_l", "foot_l")}}
with open(ROOT + "docs/v4_2/C00_TOCHTER_SITZ.json", "w", encoding="utf8") as f:
    json.dump(out, f, indent=1)
print("C00_TOCHTER_POSE", nb, "body bones", nf, "face tracks", "actor", [round(v, 1) for v in actor_loc.to_tuple()],
      "her hand_r", [round(v, 1) for v in out["hand_r_world"]], "his hand_l", [round(v, 1) for v in m_hand.to_tuple()])
