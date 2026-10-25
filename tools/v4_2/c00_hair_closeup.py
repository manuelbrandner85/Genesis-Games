"""C00 (runs INSIDE the Unreal Editor): the man's thinning hair for the bed close-up (Regie 2026-10-25: "verbessere die
Haare des Mannes fuer die Nahaufnahme").

The built groom Hair_S_HairLoss rendered as a dense grey mat with a cut-out hairline:
- stable rasterization widens every strand to at least one pixel - correct for distant game cameras, but at 35 mm from
  the bedside the ~90 um strands then cover the scalp like felt. Off: strands keep their real width (the shots are
  supersampled 2x, tools/v4_2/c00_render_bedroom_shots.py, so they do not alias)
- old, thin hair tapers strongly: tip scale 0.65 -> 0.35, root 0.9 -> 0.85
- shadow density 0.5 -> 0.35: sparse grey hair lets light through to the scalp
Same for the stubble and eyebrows. Run again after c00_mh_build.py (a rebuild resets the built grooms).
"""
import unreal

eal = unreal.EditorAssetLibrary
G = "/Game/Genesis/Characters/C00/Built/Mann/MHC_C00_Mann/Grooms/"
SPEC = {"Hair_S_HairLoss": (0.85, 0.35, 0.35), "Beard_S_Stubble": (None, None, None), "Eyebrows_M_Messy": (None, 0.4, None)}
for name, (root, tip, density) in SPEC.items():
    g = eal.load_asset(G + name)
    if not g:
        continue
    groups = g.get_editor_property("hair_groups_rendering")
    for r in groups:
        geo, sh, adv = (r.get_editor_property(k) for k in ("geometry_settings", "shadow_settings", "advanced_settings"))
        if root is not None:
            geo.set_editor_property("hair_root_scale", root)
        if tip is not None:
            geo.set_editor_property("hair_tip_scale", tip)
        if density is not None:
            sh.set_editor_property("hair_shadow_density", density)
        adv.set_editor_property("use_stable_rasterization", False)
        r.set_editor_property("geometry_settings", geo)
        r.set_editor_property("shadow_settings", sh)
        r.set_editor_property("advanced_settings", adv)
    g.set_editor_property("hair_groups_rendering", groups)
    eal.save_loaded_asset(g)
    print("C00_HAIR", name, len(groups))
