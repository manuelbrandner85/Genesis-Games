# Geräusche und Menüklänge – Erläuterung zur Liste

Liste: `genesis_geraeusche_ui_klaenge.csv` – **77 Einträge**:
- 14 Sounds des Testausschnitts VS01 (`196_TESTSLICE_ASSETS.csv`, alle `NOT_CREATED`)
- 24 V33-Cues (`15_V33_AUDIO_CUES_24.csv`, alle `DESIGN_ONLY`)
- 18 Audio- und 21 UI-Anforderungen aus `226_VOLLSPIEL_ANFORDERUNGEN.csv` (alle `SPECIFIED_NOT_BUILT`)

Spalten „Quelle“ und „Lizenz“ sind **leer = offen**. Es gibt noch keine einzige Audiodatei.

## Lautheitsziele (Annahmen, bis Mastering-Vorgabe beschlossen ist)
| Bereich | Ziel | Spitze |
|---|---|---|
| Gesamtmix Spiel / Cinematics | **-24 LUFS integriert** (±2), Dialog als Bezug | ≤ **-1 dBTP** |
| Dialog | Bezugspegel des Mixes | ≤ -1 dBTP |
| Atmosphären (Loops) | -30 LUFS (kurzfristig gemessen) | ≤ -1 dBTP |
| Foley | -24 LUFS (Referenz-Satz) | ≤ -1 dBTP |
| UI-Klänge | -26 LUFS (One-Shot) | ≤ -3 dBTP |
| Echo-Schichten V33 | -28 LUFS | ≤ -1 dBTP |

Grund: -24 LUFS ist für Heimgeräte ein verbreiteter Zielwert für Spiele; Dialog bleibt verständlich, UI überdeckt ihn nicht. Getrennte Regler für Sprache, Musik und Effekte sind Pflicht (Drehbuch, Abschnitt D).

## Mix-Busse
`DIALOG`, `MUSIC`, `AMBIENCE`, `FOLEY`, `UI` (UI_FOCUS, UI_STATUS), `ECHO_MOTIF`, `ECHO_AMBIENCE`, `ECHO_FOLEY`, `LIVE_AMBIENCE`, `BLEND`, `CANON_ORIGINAL`. Bus-Namen der V33-Cues sind aus dem Paket übernommen; `SCENE_MIX (offen)` bei V61-Audio heißt: Bus wird pro Szene festgelegt.

## Regeln für Menüklänge (aus dem Paket)
- Kein Erfolgs-/Siegeston, keine Fanfare, kein Schuld- oder Versagenston.
- Kein Ton als Beweis für ein Speichern; Ton erst nach gültigem Commit, keine Wiederholung bei Doppelklick.
- Fehler: kurzes neutrales Geräusch + Text.
- Jeder UI-Klang hat eine Text-Entsprechung (Barrierefreiheit).
