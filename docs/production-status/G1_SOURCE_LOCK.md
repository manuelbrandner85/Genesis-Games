# G1 – Source Lock · Status: ACCEPTED (Arbeitskanon, Kandidat)

Datum: 2026-10-23 · Entscheid Game Director: „V62-Quellen als Arbeitskanon mit Status ‚Kandidat, nicht endfreigegeben‘ sichern.“

## Was gesichert ist

Quelle: `GENESIS_V62_GESAMTES_SPIEL_CLAUDE_CODE_UEBERGABE.zip` (SHA-256 `be91f395…cf80e07`), nur gelesen. Werkzeug: `tools/v4/g1/canon_lock.py`.

| Gruppe | Dateien | Inhalt |
|---|---|---|
| `scriptlock` | 3 | Drehbuch ScriptLock 1.1 (C00–C21), Szenenmatrix, Konfliktentscheidungen |
| `jenseits` | 30 | J00–J24 einzeln, Missionsliste J00–J24 (CSV), Originale V27–V30 |
| `welt_flussdorf` | 3 | Weltbibel Flussdorf, V24 NPC- und Ereignissimulation, V48 Kanon-NPCs und Ortsbindung |
| `missionen` | 3 | V21 Missionsbibel + Missionsdaten (JSON), V24 Missionsbibel und Entscheidungen |

- **Vollständig:** 39 von 39 Dateien gefunden. Wo die ZIP mehrere Kopien enthält, sind alle bytegleich (kein Konflikt).
- **Ergänzt über deine Aufzählung hinaus:** die beiden NPC-Dokumente zum Flussdorf (V24 NPC-Simulation, V48 Kanon-NPCs). Sie gehören zum Flussdorf-Paket und G6 braucht sie für die NPC-Rollen.
- **Nicht gesichert:** Storybibel Vorschlag 09, weitere Paketdokumente V25–V61 – nicht angefordert.

## Schutz

- Ablage `canon_sources/` – **nur lokal**, per `.gitignore` aus dem öffentlichen Repo ausgeschlossen. Dateien schreibgeschützt.
- `canon_sources/canon_manifest.json` (lokal): Pfad, SHA-256, Größe, Herkunft in der ZIP, Status `KANDIDAT_NICHT_ENDFREIGEGEBEN`.
- `docs/v4/CANON_SOURCE_REGISTER.json` (öffentlich): nur IDs, Gruppen und Prüfsummen, **keine Titel oder Inhalte** (Spoilerschutz).
- Hash-Inventur `tools/v4/source_audit.py` → `Saved/G1/source_audit.json` (lokal, 40 Dateien inkl. README).
- Der Projekt-Hook `.claude/settings.json` blockiert Schreibzugriffe auf `canon_sources/` in Sitzungen, die im Projektordner gestartet werden.

## Bewusst offen gelassen (keine stille Kanonkorrektur)

- `CON33-01` C15/C16 (Bibliotheksraum vs. formloser Erinnerungsraum)
- C17-Wortlaut „andere Epoche“ vs. später entfernte Epochenwahl
- C21 Schöpfungsfinale vs. Ein-Welt-Wiedergeburt
- C00/C20-Replay nur mit echtem Bild-/Tonmaster

## Regel für die Produktion

Inhalte aus diesen Quellen werden **wörtlich übernommen oder als Quelle zitiert**. Alles, was die Quellen offen lassen, wird als `Gestaltungs-Startwert` bzw. `DRAFT_NEEDS_APPROVAL` markiert und nicht als Kanon ausgegeben. Bei Endfreigabe einer Quelle: neue Datei sichern, Hash vergleichen, Status im Manifest ändern.
