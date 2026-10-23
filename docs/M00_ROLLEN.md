# Aufgabenverteilung

Stand der Änderung: 2026-10-23. Jede WorkID hat eine führende Rolle und genau einen Auftrag. Reviewer bleibt `OFFEN`, bis die Evidence-Datei einen Namen trägt. Dieselbe Person schreibt und zeichnet `APPROVED` nicht allein.

Die ID-Belegung steht in [M00_PRODUKTIONSPLAN.md](M00_PRODUKTIONSPLAN.md). Kurz: WK-M02-001 ist der vorhandene Save. Der Neulauf ist WK-M02-007. WK-M03-001 ist das Rechteblatt. Die Rollenprüfung ist WK-M03-006. WK-M08-001 sind die 17 Phasen. Die Filmphasen sind WK-M08-004. Steht dieselbe WorkID in zwei Rollentabellen, ist das dieselbe Arbeit mit einer führenden Rolle, kein zweiter Auftrag.

## Story & Kanon

| WorkID | Auftrag | Status |
|---|---|---|
| WK-M00-003 | ScriptLock-SHA256 beider Kopien und die Zählung 22 Szenen, 113 Shots. Evidence `M00-EV-005`. | `FILE_VALIDATED` |
| WK-M03-006 | Acht `RoleAsSource`-Strings zeichengleich zur Rollen-CSV | `PLANNED` |
| WK-M03-004 | Quest-IDs nur aus VS01-A–E und den 43 Missionsankern | `PLANNED` |
| WK-M03-005 | Steinbrücke ohne Zuweisung an ein Holzgewerk | `PLANNED` |
| WK-M04-002 | Acht Beschlussdateien N01–N08 vor jedem Mastergesicht | `BLOCKED` |
| WK-M05-001 | C01–C04: gelieferter Segment-Hash gleich `SourceSegmentSHA256` | `PLANNED` |
| WK-M05-002 | `bounds.json` aus C05–C14, Testprofil mit `test_profile_is_canon` = false | `PLANNED` |
| WK-M06-001 | Räume und Bibliothek in C15, C16, C17, C19 nach PR #3. Tempel- und Säulen-Meshzahl 0. | `PLANNED` |
| WK-M07-001 | `c00_sha256` gleich `c20_playback_sha256` | `BLOCKED` |
| WK-M07-003 | `c19_string_hits_before_reveal` = 0 | `PLANNED` |

## Unreal Engineer

| WorkID | Auftrag | Status |
|---|---|---|
| WK-M01-002 | Logzeile `Engine Version:` und Pluginliste | `PLANNED` |
| WK-M02-001 | Vorhandener Save, Commit `e9eb043`, Evidence-Ordner `docs/evidence/WK-M02-001/` | `FILE_CREATED` |
| WK-M02-007 | Vier Fälle in `crash_matrix.csv`, jeder `consistent` = 1 | `BLOCKED` |
| WK-M02-002, WK-M02-003, WK-M02-004 | Vorhandene Figur-, Kamera- und Zeitdateien | `FILE_CREATED` |
| WK-M03-002 | Diff ohne `GenesisSlice`, Default-Map bleibt `L_GenesisTest` | `PLANNED` |
| WK-M03-003 | Würfel 99,9–100,1 cm | `PLANNED` |
| WK-M03-004 | Dauer 30–45 Minuten, `save_load_mid_quest` >= 1 | `PLANNED` |
| WK-M04-003 | `ue_import.log` je Mesh | `PLANNED` |
| WK-M05-002 | `age_ms`-Differenz nach Laden = 0 | `PLANNED` |
| WK-M06-002 | `soul_tx` = `world_tx` = `life_tx` | `BLOCKED` |
| WK-M07-003 | `hud_assets` = 12, `interaction_assets` = 19 | `PLANNED` |
| WK-M08-003 | 15 IDs `V61-N16-001` bis `V61-N16-015` | `PLANNED` |

## 3D & Animation

Die 38 GLBs und 38 Tafeln bleiben unter `assets/source_glb/`. Manuel hat entschieden, dass das Repo öffentlich bleibt, einschließlich dieser Dateien. Die Rechteklärung bleibt für das Release offen.

| WorkID | Auftrag | Status |
|---|---|---|
| WK-M00-004 | 38 Hashes gleich dem Register, 004 und 005 beide vorhanden | `FILE_VALIDATED` für Bytes |
| WK-M03-003 | Maßwürfel, `quality_pass` = false | `PLANNED` |
| WK-M03-005 | 13 Brücken-GLBs, Dublette erst nach `dublette.md` | `PLANNED` |
| WK-M04-001 | 15 Werkstatt-GLBs, `usage` Reparatur und Generator, Beträge gleich dem V23-Auszug | `PLANNED` |
| WK-M04-002 | Mastergesichter erst nach den acht Beschlussdateien | `BLOCKED` |
| WK-M04-003 | Sieben Dateien je Mesh, fehlende Dateien = 0 | `PLANNED` |
| WK-M04-004 | 40 Aktionsdateien, heute 0 FBX | `SOURCE_MISSING` |
| WK-M05-001 | Körper der Szenen C01–C04 nach bestandenen Segment-Hashes | `PLANNED` |
| WK-M06-001 | Räume und Bibliothek nur in C15, C16, C17, C19. Tempel und Säulen 0. | `PLANNED` |

## Audio & Cinematics

| WorkID | Auftrag | Status |
|---|---|---|
| WK-M00-003 | Shot-Zahl 113 in `M00-EV-005` | `FILE_VALIDATED` |
| WK-M07-001 | Fingerprint C00 gleich C20, Sample-Differenz 0 | `BLOCKED` |
| WK-M07-002 | 113 Sequencer-Pfade, 24 WAV. WAV-Zahl heute 0. | Aufnahmen `SOURCE_MISSING`, Ablauf `PLANNED` |
| WK-M08-004 | Shot-Zahlen C00 = 5, C01 = 4, C19 = 6, C20 = 7, Reveal-Zähler 0 | `PLANNED` |

## QA & Release

| WorkID | Auftrag | Status |
|---|---|---|
| WK-M00-001 | Hülle 91/91, Evidence `M00-EV-001` | `FILE_VALIDATED` |
| WK-M00-002 | 40 Archive, V61 47/47, Evidence `M00-EV-002` | `FILE_VALIDATED` |
| WK-M00-003 | Zählung, Evidence `M00-EV-005` | `FILE_VALIDATED` |
| WK-M00-005 | Sechs Plandateien, Evidence `M00-EV-006` | `FILE_CREATED` |
| WK-M01-001 | `mismatch_count` = 0 | `BLOCKED` |
| WK-M02-006 | `decision` = `APPROVED` nur mit fremdem Reviewer | `BLOCKED` |
| WK-M03-001 | 38 Rechtezeilen, Import gesperrter Namen = 0 | `BLOCKED` |
| WK-M04-003 | Sieben Dateien je Mesh | `PLANNED` |
| WK-M08-001 | 390 QA-IDs, `not_run_count` = 0 | `PLANNED` |
| WK-M08-002 | p50, p99, 1%-Low, GPU-Speicher bei 1080p und 1440p. Ziel 16,7 ms erst mit benannter Maschine. | `PLANNED` |
| WK-M08-003 | 15 N16-IDs | `PLANNED` |
| WK-M09-001 | Zwei Builds, gleiche SHA256 | `BLOCKED` |
| WK-M09-002 | Pull Request auf `main` mit der Build-SHA256 | `PLANNED` |
