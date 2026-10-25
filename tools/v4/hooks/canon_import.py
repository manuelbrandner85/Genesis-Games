"""GENESIS canon import - the ONLY way for Claude to add a file to the canon vault (Game Director, 2026-10-25:
"nur neue Dateien, nur mit Hash aus einer freigegebenen Regieentscheidung, nie ueberschreiben").

    python tools/v4/hooks/canon_import.py <source file> <GD-YYYY-MM-DD-NN>

Refuses (exit 2) unless ALL of these hold:
- target folder is canon_sources/scriptlock, file name is a script version (GENESIS_ScriptLock_<n>_Drehbuch_v<x.y>.md)
- the source does not lie inside canon_sources, the target does not exist yet (exclusive create: never overwrite)
- docs/v4_2/DIRECTOR_DECISIONS.md has a section "## <GD-ID> ..." whose Game-Director answer starts with "JA" and
  which names the full SHA-256 of the source file
Then it writes the file exclusively, sets it read-only, re-checks the hash and appends one line (decision, file,
SHA-256, time) to docs/v4_2/canon_import_log.jsonl. Existing canon files are never touched.
The PreToolUse guard (claude_pretool_guard.py) only lets this tool through in its plain form.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VAULT = ROOT / "canon_sources" / "scriptlock"
DECISIONS = ROOT / "docs/v4_2/DIRECTOR_DECISIONS.md"
LOG = ROOT / "docs/v4_2/canon_import_log.jsonl"
NAME_OK = re.compile(r"^GENESIS_ScriptLock_\d+_Drehbuch_v\d+(?:\.\d+)+\.md$")
GD_OK = re.compile(r"^GD-\d{4}-\d{2}-\d{2}-\d{2}$")


def fail(msg):
    sys.stderr.write("CANON_IMPORT_REFUSED: " + msg + "\n")
    return 2


def decision_section(gd):
    text = DECISIONS.read_text(encoding="utf8")
    m = re.search(rf"^## {re.escape(gd)}\b.*?(?=^## GD-|\Z)", text, re.M | re.S)
    return m.group(0) if m else None


def main(argv):
    if len(argv) != 2:
        return fail("Aufruf: canon_import.py <Quelldatei> <GD-YYYY-MM-DD-NN>")
    src, gd = Path(argv[0]).resolve(), argv[1]
    if not GD_OK.match(gd):
        return fail(f"keine gueltige Regieentscheidungs-ID: {gd}")
    if not src.is_file():
        return fail(f"Quelle fehlt: {src}")
    if (ROOT / "canon_sources").resolve() in src.parents:
        return fail("Quelle liegt bereits im Canon-Ordner")
    if not NAME_OK.match(src.name):
        return fail(f"nur Drehbuchfassungen (GENESIS_ScriptLock_<n>_Drehbuch_v<x.y>.md), nicht: {src.name}")
    dest = VAULT / src.name
    if dest.exists():
        return fail(f"Ziel existiert schon, wird nie ueberschrieben: {dest.name}")
    data = src.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    sec = decision_section(gd)
    if not sec:
        return fail(f"Regieentscheidung {gd} nicht in DIRECTOR_DECISIONS.md")
    answer = re.search(r"^\|\s*Antwort des Game Directors\s*\|\s*„?\"?(.*?)\|", sec, re.M)
    if not answer or not answer.group(1).strip().lstrip("„\"").startswith("JA"):
        return fail(f"{gd} enthaelt keine Freigabe mit „JA“")
    if sha not in sec:
        return fail(f"SHA-256 {sha} der Quelle steht nicht in {gd} (Datei weicht von der freigegebenen Fassung ab)")
    VAULT.mkdir(parents=True, exist_ok=True)
    with open(dest, "xb") as f:                          # exclusive create: fails if it appeared meanwhile
        f.write(data)
    os.chmod(dest, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
    if hashlib.sha256(dest.read_bytes()).hexdigest() != sha:
        return fail("Hash nach dem Schreiben abweichend - bitte manuell pruefen")
    entry = {"time": _dt.datetime.now().isoformat(timespec="seconds"), "decision": gd, "file": dest.name, "sha256": sha}
    with open(LOG, "a", encoding="utf8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("CANON_IMPORT_OK " + json.dumps(entry, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    for _s in (sys.stdout, sys.stderr):                  # German quotes in messages: UTF-8 instead of the console code page
        _s.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main(sys.argv[1:]))
