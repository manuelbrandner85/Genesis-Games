"""G6 WP6.2 (runs INSIDE the Unreal Editor): can people walk between all places the NPC
schedules need? Path queries on the editor nav mesh between region anchor points."""
import json
import os

import unreal

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
nav = unreal.NavigationSystemV1.get_navigation_system(world)
POINTS = {  # where NPCs stand / the player must reach (cm)
    "R01_Square": (0, 0, 20), "R01_NoticeBoard": (-640, -600, 20),
    "R02_Counter_Front": (3000, -100, 20), "R02_Behind_Counter": (3000, 200, 20),
    "R03_Inside_Workbench": (5400, 180, 20), "R03_Generator": (5100, -120, 20),
    "R07_House2_Door": (0, 2700, 70), "R07_House1_Letterbox": (-1300, 2400, 70),
}
results = {}
names = list(POINTS)
for i, a in enumerate(names):
    for b in names[i + 1:]:
        p = unreal.NavigationSystemV1.find_path_to_location_synchronously(world, unreal.Vector(*POINTS[a]), unreal.Vector(*POINTS[b]))
        ok = bool(p) and p.is_valid() and not p.is_partial()
        length = p.get_path_length() if ok else -1.0
        results[f"{a} -> {b}"] = {"ok": ok, "length_m": round(length / 100.0, 1)}
out = os.path.join(unreal.Paths.project_dir(), "Saved", "G6", "navcheck.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
bad = [k for k, v in results.items() if not v["ok"]]
print("G6_NAV", len(results), "paths,", len(bad), "failed", bad[:8])
