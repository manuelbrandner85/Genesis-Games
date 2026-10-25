"""C00 (runs INSIDE the Unreal Editor): the daughter's approved height of 166 cm (CHR_C00_TOCHTER, Figuren-DNA).

c00_mh_tochter.py set the Height body constraint to 166 on struct copies, so the asset kept it INACTIVE at 179.6 cm (the built figure
stood ~180 cm, head joint at 181 cm). Here the constraint is activated and the body re-solved and committed; afterwards
c00_mh_build.py (GENESIS_BUILD_CHAR=Tochter) rebuilds the animatable figure.
"""
import unreal

eal = unreal.EditorAssetLibrary
mh = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
TARGET = 166.0
ch = eal.load_asset("/Game/Genesis/Characters/C00/MHC_C00_Tochter")
if not mh.is_object_added_for_editing(ch):
    mh.try_add_object_to_edit(ch)
bcs = mh.get_body_constraints(ch, False)
i = [str(x.name) for x in bcs].index("Height")
c = bcs[i]                                  # iterating yields struct copies: edit one and write it back by index
c.set_editor_property("is_active", True)
c.set_editor_property("target_measurement", TARGET)
bcs[i] = c
mh.set_body_constraints(ch, bcs)
mh.commit_body_state(ch)
eal.save_loaded_asset(ch, False)
h = next(c for c in mh.get_body_constraints(ch, False) if str(c.name) == "Height")
print("C00_TOCHTER_HEIGHT active", h.is_active, "target", round(h.target_measurement, 1))
