"""C00 (runs INSIDE the Unreal Editor): build MHC_C00_Mann from the bundled MetaHuman preset "Walter".

Target (approved reference Rev. 2, GD-2026-10-24-02): man around 88, very thin, short thin white hair
with hair loss, white stubble instead of goatee/moustache, pale skin with strong age texture.
Local MetaHuman Creator functions only (no Epic cloud). Idempotent: an existing asset is edited again.
"""
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

# Skin: strongest local age texture (index 47, found in the C00 lab), pale cool-neutral tone
ss = ch.skin_settings
skin = ss.skin
skin.face_texture_index = 47
skin.u, skin.v = 0.20, 0.42
ss.skin = skin
mh.commit_skin_settings(ch, ss)
report["skin"] = (skin.face_texture_index, skin.u, skin.v)

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
mh.on_edit_preview_collection(ch)                                 # propagate palette/selection edits to the asset
eal.save_loaded_asset(ch)
print("C00_MANN", report)
