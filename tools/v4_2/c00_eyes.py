"""C00 (runs INSIDE the Unreal Editor): brighter, clearer eyes for father and daughter (Regie 2026-10-25: "die Augen von
Vater und Tochter sind immer noch zu dunkel").

The bundled presets darken the iris with a global tint of ~0.35 and strong shadow details - in the warm, dim bedroom
light the eyes read almost black. For all four C00 assets (game figures + photo variants):
- iris global tint near white (keeps the chosen hue), less shadow detail, slightly smaller limbal ring
- pupil a little smaller (calm, light-adapted eye), iris brightness up (him pale blue, her grey-blue)
Run c00_mh_build.py afterwards for the built figures and c00_photo_vater_tochter.py for the photo.
"""
import unreal

eal = unreal.EditorAssetLibrary
mh = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
LC = unreal.LinearColor
SPEC = {
    "Mann": {"v": (1.0, 0.95), "tint": LC(0.95, 0.97, 1.0, 1)},
    "Tochter": {"v": (0.82, 0.72), "tint": LC(0.93, 0.95, 0.98, 1)},
}
for base, sp in SPEC.items():
    for suffix in ("", "_Foto"):
        path = f"/Game/Genesis/Characters/C00/MHC_C00_{base}{suffix}"
        if not eal.does_asset_exist(path):
            continue
        ch = eal.load_asset(path)
        if not mh.is_object_added_for_editing(ch):
            mh.try_add_object_to_edit(ch)
        es = ch.eyes_settings
        for side in ("eye_left", "eye_right"):
            eye = getattr(es, side)
            iris = eye.iris
            iris.primary_color_v, iris.secondary_color_v = sp["v"]
            iris.global_tint = sp["tint"]
            iris.shadow_details = 0.35
            iris.limbal_ring_size = 0.6
            eye.iris = iris
            pupil = eye.pupil
            pupil.dilation = 0.85
            eye.pupil = pupil
            setattr(es, side, eye)
        mh.commit_eyes_settings(ch, es)
        eal.save_loaded_asset(ch)
        print("C00_EYES", path)
