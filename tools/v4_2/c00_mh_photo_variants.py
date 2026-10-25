"""C00 (runs INSIDE the Unreal Editor): photo variants of the C00 figures for the framed photo above the bed.

Regie 2026-10-25: on the photo both are about 10 years younger, dressed more elegantly; she has longer hair,
he a little more hair. The approved game figures stay untouched: MHC_C00_Mann/Tochter are copied to
MHC_C00_Mann_Foto / MHC_C00_Tochter_Foto (same face, local functions only) and only the copies change:
- skin: the younger local synthesis texture of their base preset (Walter 151 for him, Vivian 17 for her)
- hair: him Hair_S_Clean in mostly white salt-and-pepper (fuller than the thinning crown today), her Hair_L_StraightBangs
  (long layers, no centre parting - Regie 2026-10-24) in her balayage (dark roots, caramel/honey lengths)
- clothes: her the Altena blouse (QuingKhaos, Standard licence); him (Regie: "ein schoenes weisses Hemd") the
  collared button shirt 'Shirt longsleeve with pockets' (Nyanpasinka, Standard licence) recoloured plain white
"""
import unreal

eal = unreal.EditorAssetLibrary
mh = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
C00 = "/Game/Genesis/Characters/C00"
GROOMS = "/MetaHumanCharacter/Optional/Grooms/Bindings"
FAB = "/Game/Fab/MetaHuman"
LC = unreal.LinearColor

SPEC = {
    "Mann": {"tex": 151, "uv": (0.20, 0.44), "hair": "Hair_S_Clean", "outfit": ["WI_OA_Shirt_04"],
             "hair_f": {"Melanin": 0.22, "Redness": 0.04, "Whiteness": 0.82, "Lightness": 0.72}, "hair_b": {}, "hair_c": {}},
    "Tochter": {"tex": 17, "uv": (0.18, 0.55), "hair": "Hair_L_StraightBangs", "outfit": ["WI_KhaosMDF492"],
                "hair_f": {"Melanin": 0.62, "Redness": 0.30, "Whiteness": 0.0, "Lightness": 0.42,
                           "OmbreShift": 0.42, "OmbreContrast": 0.35, "OmbreIntensity": 0.95,
                           "HighlightsBlending": 0.6, "HighlightsIntensity": 0.55, "HighlightsVariation": 0.6},
                "hair_b": {"bUseOmbre": True, "bUseHighlights": True},
                "hair_c": {"OmbreColor": LC(0.62, 0.42, 0.22, 1), "HighlightsColor": LC(0.78, 0.58, 0.32, 1)}},
}
# the shirt's own plaid is replaced by the material's custom colours: a plain white shirt, light buttons
mel = unreal.MaterialEditingLibrary
mi = eal.load_asset(f"{FAB}/Shirt_04/Materials/MI_Shirt_04")
if mi:
    white = LC(0.86, 0.86, 0.84, 1)
    for prm in ("Color_Left_side", "Color_right_side", "Color_left_pocket", "Color_right_pocket"):
        mel.set_material_instance_vector_parameter_value(mi, prm, white)
    mel.set_material_instance_vector_parameter_value(mi, "Color_buttons", LC(0.70, 0.69, 0.66, 1))
    mel.set_material_instance_static_switch_parameter_value(mi, "UseCustomColors", True)
    mel.update_material_instance(mi)
    eal.save_loaded_asset(mi)
report = {}
for name, sp in SPEC.items():
    src, dst = f"{C00}/MHC_C00_{name}", f"{C00}/MHC_C00_{name}_Foto"
    if not eal.does_asset_exist(dst):
        eal.duplicate_asset(src, dst)
    ch = eal.load_asset(dst)
    if not mh.is_object_added_for_editing(ch) and not mh.try_add_object_to_edit(ch):
        raise RuntimeError("cannot edit " + dst)
    ss = ch.skin_settings
    skin = ss.skin
    skin.face_texture_index = sp["tex"]
    skin.u, skin.v = sp["uv"]
    ss.skin = skin
    mh.commit_skin_settings(ch, ss)
    col = mh.get_preview_collection(ch)
    inst = col.get_editor_property("default_instance")
    wi = eal.load_asset(f"{GROOMS}/Hair/WI_{sp['hair']}")
    keys = [k for k in col.get_item_keys_for_slot("Hair") if str(col.get_item_display_name(k)).startswith(sp["hair"])]
    inst.set_single_slot_selection("Hair", keys[0] if keys else col.try_add_item_from_wardrobe_item("Hair", wi))
    inst.set_single_slot_selection("Outfits", unreal.MetaHumanPaletteItemKey())
    for item in sp["outfit"]:
        w = eal.load_asset(f"{FAB}/{item}")
        ks = list(col.get_item_keys_for_wardrobe_item(w))
        sel = unreal.MetaHumanPipelineSlotSelection()
        sel.set_editor_property("slot_name", "Outfits")
        sel.set_editor_property("selected_item", ks[0] if ks else col.try_add_item_from_wardrobe_item("Outfits", w))
        inst.try_add_slot_selection(sel)
    mh.on_edit_preview_collection(ch)
    mh.assemble_for_preview(ch)
    n = 0
    for path in inst.get_instance_parameter_item_paths():
        for prm in inst.get_instance_parameters(path):
            pn = str(prm.name)
            if pn in sp["hair_f"]:
                prm.set_float(sp["hair_f"][pn])
                n += 1
            elif pn in sp["hair_b"]:
                prm.set_bool(sp["hair_b"][pn])
            elif pn in sp["hair_c"]:
                prm.set_color(sp["hair_c"][pn])
    mh.on_edit_preview_collection(ch)
    eal.save_loaded_asset(ch)
    report[name] = {"tex": sp["tex"], "hair": sp["hair"], "outfit": sp["outfit"], "hair_params": n}
# the henley in deep navy for the photo (material instance of the local Fab copy is shared: restore after the shot)
print("C00_PHOTO_VARIANTS", report)
