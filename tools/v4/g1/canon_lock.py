"""G1 Source Lock: copy the approved working-canon files out of the V62 hand-over ZIP.

    python -I tools/v4/g1/canon_lock.py --zip <V62.zip> --out canon_sources [--apply]

Walks all nested ZIPs read-only, finds every copy of each requested source, checks that all
copies are byte-identical (otherwise CONFLICT, nothing is chosen silently), then - only with
--apply - writes one copy per file to canon_sources/<group>/, marks it read-only and writes
canon_sources/canon_manifest.json (local, contains titles) plus a public, title-free register
docs/v4/CANON_SOURCE_REGISTER.json (IDs + SHA-256 only). Never modifies the ZIP.
"""
import argparse
import hashlib
import io
import json
import os
import re
import stat
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

STATUS = "KANDIDAT_NICHT_ENDFREIGEGEBEN"
APPROVAL = "Arbeitskanon per Game-Director-Entscheid 2026-10-23; Endfreigabe ausstehend"

# group, public id, filename regex (basename)
WANTED = [
    ("scriptlock", "SCRIPTLOCK_1_1", r"^GENESIS_ScriptLock_11_Drehbuch_v1\.1\.md$"),
    ("scriptlock", "SCRIPTLOCK_1_1_SZENENMATRIX", r"^GENESIS_ScriptLock_11_Szenenmatrix\.json$"),
    ("scriptlock", "SCRIPTLOCK_KONFLIKTENTSCHEIDUNGEN", r"^SCRIPTLOCK_KONFLIKTENTSCHEIDUNGEN\.md$"),
    ("jenseits", "J_MISSIONEN_J00_J24_CSV", r"^04_JENSEITS_MISSIONEN_J00_J24\.csv$"),
    *[("jenseits", f"J{n:02d}", rf"^J{n:02d}_.+\.md$") for n in range(25)],
    ("jenseits", "V27_J12_ORIGINAL", r"^V27_J12_ORIGINAL\.md$"),
    ("jenseits", "V28_J13_J16_ORIGINAL", r"^V28_J13_J16_ORIGINAL\.md$"),
    ("jenseits", "V29_J17_J20_ORIGINAL", r"^V29_J17_J20_ORIGINAL\.md$"),
    ("jenseits", "V30_J21_J24_ORIGINAL", r"^V30_J21_J24_ORIGINAL\.md$"),
    ("welt_flussdorf", "WELTBIBEL_FLUSSDORF", r"^01_Weltbibel_Flussdorf\.md$"),
    ("welt_flussdorf", "V24_NPC_UND_EREIGNISSIMULATION", r"^03_NPC_und_Ereignissimulation\.md$"),
    ("welt_flussdorf", "V48_KANON_NPCS_UND_ORTSBINDUNG", r"^01_KANON_NPCS_UND_ORTSBINDUNG\.md$"),
    ("missionen", "V21_MISSIONSBIBEL", r"^GENESIS_V21_Menschliches_Leben_Missionsbibel_v1\.md$"),
    ("missionen", "V21_MISSIONEN_GENERATIONEN_JSON", r"^GENESIS_V21_Missionen_und_Generationen_v1\.json$"),
    ("missionen", "V24_MISSIONSBIBEL", r"^(GENESIS_V24_Paket__)?02_Missionsbibel_und_Entscheidungen\.md$"),
]


def walk(zf, chain, depth, found):
    for name in zf.namelist():
        if name.endswith("/"):
            continue
        base = name.rsplit("/", 1)[-1]
        if base.lower().endswith(".zip") and depth < 8:
            try:
                walk(zipfile.ZipFile(io.BytesIO(zf.read(name))), chain + [name], depth + 1, found)
            except zipfile.BadZipFile:
                pass
            continue
        for group, sid, rx in WANTED:
            if re.match(rx, base):
                data = zf.read(name)
                found.setdefault(sid, []).append({"group": group, "name": base, "chain": " > ".join(chain + [name]),
                                                  "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "data": data})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--public-register", type=Path, default=Path("docs/v4/CANON_SOURCE_REGISTER.json"))
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    zip_sha = hashlib.sha256(a.zip.read_bytes()).hexdigest()
    found = {}
    walk(zipfile.ZipFile(a.zip), [a.zip.name], 0, found)

    entries, missing, conflicts = [], [], []
    for group, sid, _ in WANTED:
        copies = found.get(sid, [])
        if not copies:
            missing.append(sid)
            continue
        hashes = sorted({c["sha256"] for c in copies})
        if len(hashes) > 1:
            conflicts.append({"id": sid, "variants": [{"sha256": h, "chains": [c["chain"] for c in copies if c["sha256"] == h]} for h in hashes]})
            continue
        c = copies[0]
        entries.append({"id": sid, "group": group, "file": f"{group}/{c['name']}", "sha256": c["sha256"], "bytes": c["bytes"],
                        "copies_in_zip": len(copies), "first_source": c["chain"], "data": c["data"]})

    summary = {"v62_zip_sha256": zip_sha, "requested": len(WANTED), "locked": len(entries), "missing": missing,
               "conflicts": [{"id": x["id"], "variants": len(x["variants"])} for x in conflicts]}
    print(json.dumps(summary, indent=2))
    if conflicts:
        print(json.dumps(conflicts, indent=2)[:4000])
    if not a.apply:
        print("DRY RUN - nothing written")
        return 0
    if conflicts:
        print("BLOCKED: byte conflicts between copies - resolve before locking", file=sys.stderr)
        return 2

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for e in entries:
        dest = a.out / e["file"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            if hashlib.sha256(dest.read_bytes()).hexdigest() != e["sha256"]:
                print(f"BLOCKED: {dest} exists with different content", file=sys.stderr)
                return 3
        else:
            dest.write_bytes(e.pop("data"))
            os.chmod(dest, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
        e.pop("data", None)
    manifest = {"created_utc": now, "status": STATUS, "approval": APPROVAL, "source_zip": str(a.zip), **summary,
                "open_conflicts_not_touched": ["CON33-01 C15/C16", "C17 Wortlaut 'andere Epoche'", "C21 Finale vs. Ein-Welt-Regel",
                                                "C00/C20 nur mit echtem Bild-/Tonmaster"],
                "files": entries}
    (a.out / "canon_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    public = {"created_utc": now, "status": STATUS, "approval": APPROVAL, "v62_zip_sha256": zip_sha,
              "note": "Titel und Inhalte liegen nur lokal in canon_sources/ (nicht im oeffentlichen Repo).",
              "open_conflicts_not_touched": manifest["open_conflicts_not_touched"],
              "files": [{"id": e["id"], "group": e["group"], "sha256": e["sha256"], "bytes": e["bytes"], "copies_in_zip": e["copies_in_zip"]} for e in entries],
              "missing": missing}
    a.public_register.parent.mkdir(parents=True, exist_ok=True)
    a.public_register.write_text(json.dumps(public, indent=2), encoding="utf-8")
    print(f"LOCKED {len(entries)} files -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
