"""CM0 (V4.2): bind the 22 scenes C00-C21 to the local ScriptLock 1.1 candidate by line range and SHA-256.

    python -I tools/v4_2/bind_scriptlock.py --scriptlock canon_sources/scriptlock/GENESIS_ScriptLock_11_Drehbuch_v1.1.md \
        --matrix docs/v4_2/SCENE_MATRIX_C00_C21.json --out docs/v4_2/SCENE_REGISTRY.json [--runtime Content/Genesis/Data/scene_registry.json]

Writes ONLY ids, titles from the public matrix, categories (ScriptLock IV.B), line ranges and hashes - never
script text (story sources stay out of the public repository). Approval stays SOURCE_CANDIDATE until the
game director says "JA zu Vorschlag 11" (ScriptLock IV.D); production of real scenes (CM4+) needs that.
"""
import argparse, hashlib, json, re
from pathlib import Path

# ScriptLock 1.1, part IV.B "Cinematic-Typen"
CATEGORY = {"C00": "A", "C01": "A", "C19": "A", "C20": "A/C", "C15": "C", "C16": "C", "C17": "D", "C21": "D"}
CATEGORY.update({c: "B" for c in ("C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C18")})
INTERACTIVE = {"C05", "C06", "C08", "C10", "C11", "C16", "C20"}      # ScriptLock I.7: no auto-decision at shot end
OPEN_CONFLICTS = {"C15": "CON33-01 (C15/C16)", "C16": "CON33-01 (C15/C16)", "C17": "C17 Epochenwortlaut", "C21": "C21 Finalkonflikt"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scriptlock", type=Path, required=True)
    ap.add_argument("--matrix", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--runtime", type=Path)
    a = ap.parse_args()
    raw = a.scriptlock.read_bytes()
    lines = raw.decode("utf8").splitlines(keepends=True)
    heads = [(i, m.group(1)) for i, l in enumerate(lines) if (m := re.match(r"^## (C\d\d) ", l))]
    end_part = next(i for i, l in enumerate(lines) if l.startswith("# III."))
    matrix = {s["scene_id"]: s for s in json.loads(a.matrix.read_text(encoding="utf8"))["scenes"]}
    scenes = []
    for k, (start, sid) in enumerate(heads):
        stop = heads[k + 1][0] if k + 1 < len(heads) else end_part
        section = "".join(lines[start:stop]).encode("utf8")
        scenes.append({
            "scene_id": sid, "working_title": matrix[sid]["working_title"], "category": CATEGORY[sid],
            "interactive_no_auto_decision": sid in INTERACTIVE, "open_conflict": OPEN_CONFLICTS.get(sid),
            "script_lines": [start + 1, stop], "section_sha256": hashlib.sha256(section).hexdigest(),
            "approval_status": "SOURCE_CANDIDATE_AWAITING_DIRECTOR", "implementation_status": "NOT_IMPLEMENTED",
            "replay_of": "C00" if sid == "C20" else None,
        })
    ids = [s["scene_id"] for s in scenes]
    if ids != [f"C{i:02d}" for i in range(22)]:
        raise SystemExit(f"expected C00..C21, found {ids}")
    reg = {"schema_version": 1, "script_version": "1.1",
           "scriptlock_file": a.scriptlock.name, "scriptlock_sha256": hashlib.sha256(raw).hexdigest(),
           "canon_status": "SCRIPT-LOCK-KANDIDAT - Game-Director-Beschluss ausstehend (IV.D: 'JA zu Vorschlag 11')",
           "replay_master_rule": "C20 replays the C00 master asset byte-identical (OriginalRecording), never re-rendered",
           "scenes": scenes}
    text = json.dumps(reg, indent=2, ensure_ascii=False) + "\n"
    a.out.write_text(text, encoding="utf8")
    if a.runtime:
        a.runtime.parent.mkdir(parents=True, exist_ok=True)
        a.runtime.write_text(text, encoding="utf8")
    print("BOUND", len(scenes), "scenes", reg["scriptlock_sha256"][:16])


if __name__ == "__main__":
    main()
