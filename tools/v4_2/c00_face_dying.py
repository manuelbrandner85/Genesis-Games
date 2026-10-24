"""C00 (runs INSIDE the Unreal Editor): facial pose of the dying man (CHR_C00_MANN), local joints only.

Regie 2026-10-25: "ein Sterbender hat andere Gesichtszuege". The preview face has the full MetaHuman
joint rig (no RigLogic needed, no cloud), so a one-frame pose A_C00_Mann_Gesicht_Sterbend sets:
- heavy, half-closed upper lids (rotated down about the eye centre), lower lids slightly raised
- slack jaw, mouth a little open; mouth corners sagging
- sunken cheeks and temples (soft tissue pushed into the face)
- the same neck/head flexion as the body pose A_C00_Mann_Liegen, so head and neck stay joined
Signs are chosen from the joint geometry (e.g. the lid edge must move down), not guessed.
The asset is bound to the Epic face skeleton and stays local (gitignored Posen folder).
"""
import math

import unreal

DST, NAME = "/Game/Genesis/Characters/C00/Posen", "A_C00_Mann_Gesicht_Sterbend"
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
face = next(c for c in probe.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Face")
skel = face.get_skeletal_mesh_asset().skeleton
names = [str(face.get_bone_name(i)) for i in range(face.get_num_bones())]
cs = {b: face.get_socket_transform(b, CS) for b in names}
parent = {b: str(face.get_parent_bone(b)) for b in names}
eas.destroy_actor(probe)


def about_x(deg):
    a = math.radians(deg) / 2
    return unreal.Quat(math.sin(a), 0.0, 0.0, math.cos(a))


def spin(tf, pivot, q):
    loc = pivot + q.rotate_vector(tf.translation - pivot)
    return unreal.Transform(location=loc, rotation=(q * tf.rotation).rotator(), scale=tf.scale3d)


def children(b):
    return [c for c in names if parent[c] == b]


def rotate_down(bone, deg, probe_bone=None, down=True):
    """Rotate bone about component X at its own position so that its first child (lid edge / chin) moves
    down (or up). Returns the new component transform."""
    tip = cs[probe_bone or (children(bone) or [bone])[0]].translation
    piv = cs[bone].translation
    best = None
    for sgn in (1, -1):
        moved = piv + about_x(sgn * deg).rotate_vector(tip - piv)
        score = -moved.z if down else moved.z
        if best is None or score > best[0]:
            best = (score, sgn)
    return spin(cs[bone], piv, about_x(best[1] * deg))


def nudge(bone, dx=0.0, dy=0.0, dz=0.0):
    t = cs[bone]
    return unreal.Transform(location=t.translation + unreal.Vector(dx, dy, dz), rotation=t.rotation.rotator(), scale=t.scale3d)


new = {}
# eyes: heavy, half-closed lids (A and B upper lid joints), lower lids raised a little
for side in ("L", "R"):
    for lid in ("A", "B"):
        up, lo = f"FACIAL_{side}_EyelidUpper{lid}", f"FACIAL_{side}_EyelidLower{lid}"
        if up in cs:
            new[up] = rotate_down(up, 16.0, down=True)
        if lo in cs:
            new[lo] = rotate_down(lo, 3.0, down=False)
# slack jaw: mouth slightly open
new["FACIAL_C_Jaw"] = rotate_down("FACIAL_C_Jaw", 10.0, probe_bone="FACIAL_C_UnderChin" if "FACIAL_C_UnderChin" in cs else None)
# sagging mouth corners, sunken cheeks and temples (cm; face looks along +Y)
for side, sx in (("L", 1), ("R", -1)):
    new[f"FACIAL_{side}_LipCorner"] = nudge(f"FACIAL_{side}_LipCorner", dz=-0.22, dy=-0.05)
    for b in (f"FACIAL_{side}_CheekInner", f"FACIAL_{side}_CheekLower", f"FACIAL_{side}_CheekOuter"):
        if b in cs:
            new[b] = nudge(b, dx=-0.12 * sx, dy=-0.30)
    if f"FACIAL_{side}_Temple" in cs:
        new[f"FACIAL_{side}_Temple"] = nudge(f"FACIAL_{side}_Temple", dx=-0.18 * sx)

# neck/head flexion identical to the body pose (11, 11, 8 deg, head moves forward)
chain = ["neck_01", "neck_02", "head"]
cur = {b: cs[b] for b in chain}
for k, (b, deg) in enumerate(zip(chain, (11, 11, 8))):
    tip = cur["head"].translation + unreal.Vector(0, 0, 10)
    cands = []
    for sgn in (1, -1):
        moved = cur[b].translation + about_x(sgn * deg).rotate_vector(tip - cur[b].translation)
        cands.append((moved.y, sgn))
    q = about_x(max(cands)[1] * deg)
    piv = cur[b].translation
    for b2 in chain[k:]:
        cur[b2] = spin(cur[b2], piv, q)
neck = cur

if eal.does_asset_exist(f"{DST}/{NAME}"):
    eal.delete_asset(f"{DST}/{NAME}")
fac = unreal.AnimSequenceFactory()
fac.set_editor_property("target_skeleton", skel)
anim = unreal.AssetToolsHelpers.get_asset_tools().create_asset(NAME, DST, unreal.AnimSequence, fac)
ctrl = anim.controller
ctrl.open_bracket("C00 dying face", True)
ctrl.set_frame_rate(unreal.FrameRate(30, 1), True)
ctrl.set_number_of_frames(unreal.FrameNumber(1), True)
keyed = []
for bone in chain:
    par = parent[bone]
    local = MATH.make_relative_transform(neck[bone], neck.get(par, cs[par]))
    ctrl.add_bone_curve(bone, True)
    ctrl.set_bone_track_keys(bone, [local.translation] * 2, [local.rotation] * 2, [local.scale3d] * 2, True)
    keyed.append(bone)
for bone, tf in new.items():                      # facial joints: relative to their unchanged (reference) parent
    local = MATH.make_relative_transform(tf, cs[parent[bone]])
    ctrl.add_bone_curve(bone, True)
    ctrl.set_bone_track_keys(bone, [local.translation] * 2, [local.rotation] * 2, [local.scale3d] * 2, True)
    keyed.append(bone)
ctrl.close_bracket(True)
eal.save_loaded_asset(anim)
print("C00_FACE_ASSET", anim.get_path_name(), len(keyed), "joints")
