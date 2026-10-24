"""C00 (runs INSIDE the Unreal Editor): build MHC_C00_Mann from the bundled MetaHuman preset "Walter".

Target (approved reference Rev. 2, GD-2026-10-24-02): man around 88, very thin, short thin white hair
with hair loss, white stubble instead of goatee/moustache, pale skin with strong age texture.
Local MetaHuman Creator functions only (no Epic cloud). Idempotent: an existing asset is edited again.
"""
import os
import unreal

SRC = "/MetaHumanCharacter/Optional/Presets/Walter"
DST = "/Game/Genesis/Characters/C00/MHC_C00_Mann"
GROOMS = "/MetaHumanCharacter/Optional/Grooms/Bindings"
eal = unreal.EditorAssetLibrary
mh = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)

if not eal.does_asset_exist(DST):
    eal.duplicate_asset(SRC, DST)
ch = eal.load_asset(DST)
if not mh.is_object_added_for_editing(ch) and not mh.try_add_object_to_edit(ch):
    raise RuntimeError("cannot edit " + DST)
report = {}

# Face shape: like the Creator's blend tool - Walter's face model coefficients mixed with thinner/older
# faces of other bundled presets (same 1397-value model). Always starts from the untouched Walter preset.
BLEND = os.environ.get("GENESIS_MANN_BLEND", "Lorenzo:0.6")         # chosen in the C00 lab (blend2): European, gaunter, older
CAND = "/Game/Genesis/Characters/C00/Candidates/MHC_"


def coeffs(name):
    c = eal.load_asset(CAND + name) if eal.does_asset_exist(CAND + name) else None
    if c is None:
        eal.duplicate_asset(f"/MetaHumanCharacter/Optional/Presets/{name}", CAND + name)
        c = eal.load_asset(CAND + name)
    if not mh.is_object_added_for_editing(c):
        mh.try_add_object_to_edit(c)
    return list(mh.get_face_model_coefficients(c))


face = coeffs("Walter")
for part in filter(None, BLEND.split(",")):
    other, w = part.split(":")
    oc = coeffs(other)
    face = [a + float(w) * (b - a) for a, b in zip(face, oc)]
mh.set_face_model_coefficients(ch, face)
mh.commit_face_state(ch)
report["face_blend"] = BLEND

# Skin: strongest local age texture (index 47, found in the C00 lab), pale cool-neutral tone
ss = ch.skin_settings
skin = ss.skin
skin.face_texture_index = 47
skin.u, skin.v = 0.20, 0.42
ss.skin = skin
mh.commit_skin_settings(ch, ss)
report["skin"] = (skin.face_texture_index, skin.u, skin.v)

# Eyes: pale blue like the reference (iris u = temperature 0 cool..1 warm, v = brightness)
ey = ch.eyes_settings
for side in ("eye_left", "eye_right"):                         # struct copies: write each eye back
    eye = getattr(ey, side)
    iris = eye.iris
    iris.primary_color_u, iris.primary_color_v = 0.0, 1.0
    iris.secondary_color_u, iris.secondary_color_v = 0.04, 0.92
    eye.iris = iris
    setattr(ey, side, eye)
mh.commit_eyes_settings(ch, ey)
report["eyes"] = "pale blue"

# Body: 172 cm, very lean, little muscle (frail, but not emaciated)
bcs = mh.get_body_constraints(ch, False)
for c in bcs:
    n = str(c.name)
    lo, hi = float(c.min_measurement), float(c.max_measurement)
    if n == "Height":
        c.target_measurement = 172.0
    elif n == "Fat":
        c.target_measurement = lo + 0.15 * (hi - lo)
    elif n == "Muscularity":
        c.target_measurement = lo + 0.12 * (hi - lo)
    else:
        continue
    c.is_active = True
    report[n] = round(float(c.target_measurement), 2)
mh.set_body_constraints(ch, bcs)
mh.commit_body_state(ch)                                          # persist the parametric body

# Grooms: swap wardrobe items in the character's own palette
col = mh.get_preview_collection(ch)                               # the collection the editor preview builds from
inst = col.get_editor_property("default_instance")


def use(slot, item):
    wi = eal.load_asset(f"{GROOMS}/{slot}/WI_{item}" if slot != "Beards" else f"{GROOMS}/Beards/WI_{item}")
    if wi is None:
        raise RuntimeError("wardrobe item missing: " + item)
    slot_name = {"Hair": "Hair", "Beards": "Beard"}[slot]
    keys = [k for k in col.get_item_keys_for_slot(slot_name) if str(col.get_item_display_name(k)).startswith(item)]
    key = keys[0] if keys else col.try_add_item_from_wardrobe_item(slot_name, wi)
    inst.set_single_slot_selection(slot_name, key)
    return str(col.get_item_display_name(key))


report["hair"] = use("Hair", "Hair_S_HairLoss")
report["beard"] = use("Beards", "Beard_S_Stubble")
inst.set_single_slot_selection("Mustache", unreal.MetaHumanPaletteItemKey())     # no moustache
# Groom colour: white hair, stubble and brows of a man around 88 (little melanin, high whiteness)
colours = {"Melanin": 0.08, "Redness": 0.05, "Whiteness": 0.92, "Lightness": 0.85}
changed = 0
for path in inst.get_instance_parameter_item_paths():
    for prm in inst.get_instance_parameters(path):
        n = str(prm.name)
        if n in colours:
            prm.set_float(colours[n])
            changed += 1
report["groom_colour_params"] = changed

# Clothing: dark navy sleep shirt and dark trousers (approved reference)
navy, dark = unreal.LinearColor(0.012, 0.016, 0.040, 1.0), unreal.LinearColor(0.010, 0.010, 0.014, 1.0)
cloth = 0
for path in inst.get_instance_parameter_item_paths():
    for prm in inst.get_instance_parameters(path):
        n = str(prm.name)
        if n in ("PrimaryColorShirt", "SecondaryColorShirt"):
            prm.set_color(navy)
            cloth += 1
        elif n in ("PrimaryColorShort", "SecondaryColorShort"):
            prm.set_color(dark)
            cloth += 1
report["cloth_colour_params"] = cloth
mh.on_edit_preview_collection(ch)                                 # propagate palette/selection edits to the asset
eal.save_loaded_asset(ch)
print("C00_MANN", report)
