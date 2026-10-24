"""C00 (runs INSIDE the Unreal Editor): build MHC_C00_Tochter from the bundled MetaHuman preset "Vivian".

Target (approved reference Rev. 2, GD-2026-10-24-02): woman in her mid forties, dark-blond shoulder-length
hair loosely tied back, composed and tired, no makeup, dark top (the grey knitted cardigan is not in the
bundled wardrobe yet - open item). Local MetaHuman Creator functions only (no Epic cloud).
Env GENESIS_TOCHTER_TEX overrides the skin texture index (lab comparison).
"""
import os
import unreal

SRC = "/MetaHumanCharacter/Optional/Presets/Vivian"
DST = "/Game/Genesis/Characters/C00/MHC_C00_Tochter"
GROOMS = "/MetaHumanCharacter/Optional/Grooms/Bindings"
eal = unreal.EditorAssetLibrary
mh = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)

if not eal.does_asset_exist(DST):
    eal.duplicate_asset(SRC, DST)
ch = eal.load_asset(DST)
if not mh.is_object_added_for_editing(ch) and not mh.try_add_object_to_edit(ch):
    raise RuntimeError("cannot edit " + DST)
report = {}

# Face shape (Regie 2026-10-24: lips "etwas duenner"): Vivian's face model blended with a thinner-lipped
# bundled face, like the Creator's blend tool. Always starts from the untouched Vivian preset.
BLEND = os.environ.get("GENESIS_TOCHTER_BLEND", "Jelena:0.35")
CAND = "/Game/Genesis/Characters/C00/Candidates/MHC_"


def coeffs(name):
    if not eal.does_asset_exist(CAND + name):
        eal.duplicate_asset(f"/MetaHumanCharacter/Optional/Presets/{name}", CAND + name)
    c = eal.load_asset(CAND + name)
    if not mh.is_object_added_for_editing(c):
        mh.try_add_object_to_edit(c)
    return list(mh.get_face_model_coefficients(c))


face = coeffs("Vivian")
for part in filter(None, BLEND.split(",")):
    other, w = part.split(":")
    face = [a + float(w) * (b - a) for a, b in zip(face, coeffs(other))]
mh.set_face_model_coefficients(ch, face)
mh.commit_face_state(ch)
report["face_blend"] = BLEND

# Skin: local synthesis texture for 45 years (Regie 2026-10-24: "45 Jahre alt"), light neutral tone
ss = ch.skin_settings
skin = ss.skin
skin.face_texture_index = int(os.environ.get("GENESIS_TOCHTER_TEX", "100"))     # chosen in the C00 lab: looks 45
skin.u, skin.v = 0.18, 0.55
ss.skin = skin
mh.commit_skin_settings(ch, ss)
report["skin"] = skin.face_texture_index

# Makeup (Regie 2026-10-24: "etwas geschminkt, aber huebsch, mit Mascara"): light, natural day makeup
mk = ch.makeup_settings
fd = mk.foundation
fd.apply_foundation, fd.intensity, fd.concealer = True, 0.15, 0.05
mk.foundation = fd
ey = mk.eyes
ey.type = getattr(unreal.MetaHumanCharacterEyeMakeupType, os.environ.get("GENESIS_TOCHTER_EYE", "SOFT_SMOKEY"))
ey.opacity = float(os.environ.get("GENESIS_TOCHTER_EYE_OP", "0.85"))   # Regie: Eyeliner, Kajal, dezenter Lidschatten
ey.roughness = 0.75
ey.primary_color = unreal.LinearColor(0.010, 0.007, 0.006, 1.0)            # kohl: dark brown-black
ey.secondary_color = unreal.LinearColor(0.16, 0.11, 0.09, 1.0)             # Regie: dezenter Lidschatten, soft taupe
mk.eyes = ey
bl = mk.blush
bl.type, bl.intensity = unreal.MetaHumanCharacterBlushMakeupType.APPLE, 0.07
bl.color = unreal.LinearColor(0.55, 0.20, 0.17, 1.0)                        # muted rose
mk.blush = bl
lp = mk.lips
lp.type, lp.opacity, lp.metalness, lp.roughness = unreal.MetaHumanCharacterLipsMakeupType.NATURAL, 0.10, 0.0, 0.55
lp.color = unreal.LinearColor(0.24, 0.10, 0.09, 1.0)                        # subtle nude rose (Regie: "dezenter")
mk.lips = lp
mh.commit_makeup_settings(ch, mk)
# Mascara: long, slightly curled, deep black lashes
hm = ch.head_model_settings
lash = hm.eyelashes
lash.type = unreal.MetaHumanCharacterEyelashesType.LONG_THICK_CURL      # Regie: "fette Lashes"
lash.melanin, lash.lightness, lash.redness, lash.salt_and_pepper, lash.roughness = 1.0, 0.0, 0.05, 0.0, 0.3   # deep black mascara
hm.eyelashes = lash
mh.commit_head_model_settings(ch, hm)
report["makeup"] = "day makeup + mascara"

# Eyes: grey-blue like the reference (iris u = temperature 0 cool..1 warm, v = brightness)
ey = ch.eyes_settings
for side in ("eye_left", "eye_right"):                         # struct copies: write each eye back
    eye = getattr(ey, side)
    iris = eye.iris
    iris.primary_color_u, iris.primary_color_v = 0.22, 0.55
    iris.secondary_color_u, iris.secondary_color_v = 0.25, 0.45
    eye.iris = iris
    setattr(ey, side, eye)
mh.commit_eyes_settings(ch, ey)

# Body: 166 cm, average build
bcs = mh.get_body_constraints(ch, False)
for c in bcs:
    if str(c.name) == "Height":
        c.target_measurement = 166.0
        c.is_active = True
mh.set_body_constraints(ch, bcs)
mh.commit_body_state(ch)

col = mh.get_preview_collection(ch)
inst = col.get_editor_property("default_instance")


def use(slot_dir, slot_name, item):
    wi = eal.load_asset(f"{GROOMS}/{slot_dir}/WI_{item}")
    if wi is None:
        raise RuntimeError("wardrobe item missing: " + item)
    keys = [k for k in col.get_item_keys_for_slot(slot_name) if str(col.get_item_display_name(k)).startswith(item)]
    key = keys[0] if keys else col.try_add_item_from_wardrobe_item(slot_name, wi)
    inst.set_single_slot_selection(slot_name, key)
    return str(col.get_item_display_name(key))


# Regie 2026-10-24: long bob with waves, dirty blond to light brown
HAIR = os.environ.get("GENESIS_TOCHTER_HAIR", "Hair_M_BobCurly")   # Regie: wavy long bob, no centre parting ("own" = generated groom)
if HAIR == "own":       # own groom GR_C00_Tochter_Haar (tools/v4_2/build_c00_hair.py) is attached instead
    inst.set_single_slot_selection("Hair", unreal.MetaHumanPaletteItemKey())
    report["hair"] = "own groom GR_C00_Tochter_Haar"
else:
    report["hair"] = use("Hair", "Hair", HAIR)
# Regie 2026-10-24: blouse with jacket instead of the T-shirt - the bundled outfit is switched off, the
# own garment (SKM_C00_Tochter_Kleidung, tools/v4_2/build_c00_garments.py) is worn instead
inst.set_single_slot_selection("Outfits", unreal.MetaHumanPaletteItemKey())
mh.on_edit_preview_collection(ch)            # rebuild the preview so the new groom exposes its colour parameters
mh.assemble_for_preview(ch)

# Dark blond hair and brows
hair = {"Melanin": 0.62, "Redness": 0.30, "Whiteness": 0.0, "Lightness": 0.42}   # dark brown roots
# Balayage like the director's reference photo (2026-10-24): dark brown at the roots, caramel/honey-blond lengths
balayage_f = {"OmbreShift": 0.42, "OmbreContrast": 0.35, "OmbreIntensity": 0.95,
              "HighlightsBlending": 0.6, "HighlightsIntensity": 0.55, "HighlightsVariation": 0.6}
balayage_c = {"OmbreColor": unreal.LinearColor(0.62, 0.42, 0.22, 1.0), "HighlightsColor": unreal.LinearColor(0.78, 0.58, 0.32, 1.0)}
balayage_b = {"bUseOmbre": True, "bUseHighlights": True}
top = unreal.LinearColor(0.012, 0.012, 0.014, 1.0)
n_hair = n_cloth = 0
for path in inst.get_instance_parameter_item_paths():
    for prm in inst.get_instance_parameters(path):
        n = str(prm.name)
        if n in hair:
            prm.set_float(hair[n])
            n_hair += 1
        elif n in balayage_f:
            prm.set_float(balayage_f[n])
        elif n in balayage_c:
            prm.set_color(balayage_c[n])
        elif n in balayage_b:
            prm.set_bool(balayage_b[n])
        elif n in ("PrimaryColorShirt", "SecondaryColorShirt", "PrimaryColorShort", "SecondaryColorShort"):
            prm.set_color(top)
            n_cloth += 1
report["hair_params"], report["cloth_params"] = n_hair, n_cloth
mh.on_edit_preview_collection(ch)
eal.save_loaded_asset(ch)
print("C00_TOCHTER", report)
