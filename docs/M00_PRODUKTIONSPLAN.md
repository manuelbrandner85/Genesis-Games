# Produktionsplan M00–M09

Stand der Änderung: 2026-10-23. Reihenfolge aus dem Masterprompt: M00 Quellen und Sicherheit, M01 Backup und Restore, M02 Fundamente und Save, M03 Vertikalschnitt VS01 von 30–45 Minuten ohne ein `GenesisSlice` zu überschreiben, M04 iterative 3D-Master, M05 Lebenszyklus, M06 Echo und Wiedergeburt, M07 C00–C21, Audio auf Deutsch und UI, M08 die 17 Phasen mit QA, Leistung und Zugänglichkeit, M09 unabhängiger Release und versionierte Migration.

Reviewer ist `OFFEN`, solange kein Personenname in der Evidence-Datei steht. Ein Ja zu diesem Dokument startet die nächste Zeile nicht. Niemand schreibt auf `main`.

`FILE_VALIDATED` heißt: die genannte SHA256- oder Zählprüfung ist gelaufen und die Evidence-Datei enthält das Ergebnis. Blender- und Unreal-Felder im GLB-Register bleiben `NOT_RUN`.

Eine Zeile mit Status `PLANNED` ist definiert. Ihre Ausführung startet erst, wenn jede Abhängigkeit `FILE_CREATED`, `FILE_VALIDATED`, `INTEGRATED`, `TESTED` oder `APPROVED` erreicht hat und keine Abhängigkeit mehr `BLOCKED` oder `SOURCE_MISSING` ist. `PLANNED` an einer `BLOCKED`-Abhängigkeit bleibt `PLANNED` und wird nicht ausgeführt.

## ID-Belegung

| ID | Belegung |
|---|---|
| WK-M02-001 | Commit `e9eb043`, Ordner `docs/evidence/WK-M02-001/`. Der Neulauf heißt WK-M02-007. |
| WK-M02-005 | In `docs/STAND.md` als Vorschlag für Tag und Nacht genannt. Diese ID bleibt frei. |
| WK-M03-001 | Rechteblatt der 38 GLBs. Die Rollenprüfung heißt WK-M03-006. |
| WK-M08-001 | Phasen N00–N16 und 390 Tests. Die Filmphasen heißen WK-M08-004. |

## Die ersten fünf WorkIDs

| WorkID | Abnahme, kurz | QAEvidenceID | Status |
|---|---|---|---|
| WK-M00-001 | Release-Hash gleich, 91 Summenzeilen, 0 Abweichungen | `M00-EV-001` | `FILE_VALIDATED` |
| WK-M00-002 | 40 Archive `testzip` OK, V61-Summe 47/47 | `M00-EV-002` | `FILE_VALIDATED` |
| WK-M00-003 | Zählungen und ScriptLock-SHA256 gleich | `M00-EV-005` | `FILE_VALIDATED` |
| WK-M00-004 | 38 GLB-Hashes gleich dem Register | `M00-EV-004` | `FILE_VALIDATED` für Bytes |
| WK-M00-005 | Sechs Plandateien mit SHA256 in der Evidence | `M00-EV-006` | `FILE_CREATED` |

### WK-M00-001 — Hülle — `FILE_VALIDATED`

Quelle: Release `handover-v62`. Abhängigkeit: keine. QAEvidenceID: `M00-EV-001`. Reviewer: `OFFEN`. Rolle: QA & Release.

Abnahme, bestanden wenn alle drei gelten: SHA256 von `GENESIS_V62.zip` = `be91f395b09a131adc8d16fa8cfa4b54e337010e1c2aa7c6defdf0762cf80e07`; Zahl der gleichen Summenzeilen = 91; Zahl der abweichenden Nutzlastzeilen = 0.

### WK-M00-002 — Kette — `FILE_VALIDATED`

Quelle: V61, V60, V59, 37 ZIPs. Abhängigkeit: WK-M00-001. QAEvidenceID: `M00-EV-002`, Dateiliste zusätzlich `M00-EV-003`. Reviewer: `OFFEN`. Rolle: QA & Release.

Abnahme, bestanden wenn alle drei gelten: `testzip` = OK für 40 Archive und für 0 Archive ein Fehler; V61-Summe ok = 47 und bad = 0; Selbstbezug abweichend bei genau drei Dateien namens `SHA256SUMS.txt` (V33, V25, verschachtelte V41-Liste) und bei 0 anderen Dateien.

### WK-M00-003 — Register und ScriptLock — `FILE_VALIDATED`

Quelle: `04_PRODUKTIONSREGISTER`, V61-Manifest, beide ScriptLock-Kopien. Abhängigkeit: WK-M00-002. QAEvidenceID: `M00-EV-005` in `docs/evidence/M00/WK-M00-003/register_counts.json`. Reviewer: `OFFEN`. Rolle: Story & Kanon, Zählung QA & Release.

Abnahme, bestanden wenn `register_counts.json` diese Zahlen trägt und `scriptlock_equal` = true: Phasen 17, Anforderungen 226, VS01-Assets 196, GLB 38, Animationen 40, Missionen 43, Shots 113, Szenen 22, Szenenpakete 31, V60-Lücken 36, V61-Tests 390, Rechtezeilen 28. ScriptLock-SHA256 beider Kopien = `b23a047b13c1a7d77d00679c757f4fbcaa6cfc3e736305a7f77152c072ce732d`.

### WK-M00-004 — GLB und Tafeln — `FILE_VALIDATED` für Bytes

Quelle: `38_GLB_QUELLEN.csv`. Abhängigkeit: WK-M00-001. QAEvidenceID: `M00-EV-004`. Reviewer: `OFFEN`. Rolle: 3D & Animation, Hashprüfung QA & Release.

Abnahme, bestanden wenn alle vier gelten: 38 Dateien unter `assets/source_glb/GLB/`; jede SHA256 gleich der Registerzeile; 38 Dateien `*_FRONT_SEITE_RUECKEN.png`; SHA256 von `VS01_R04_BRUECKE_004.glb` = SHA256 von `VS01_R04_BRUECKE_005.glb` = `aa103052582d842c302cd50d7bd54d6fb79567bd5fdf1914aee93699df344b7e`. Die Dateien bleiben im Repo. BlenderValidation und UnrealIntegration bleiben `NOT_RUN`.

### WK-M00-005 — Plan — `FILE_CREATED`

Quelle: Masterprompt, P0-Liste, V61 `05_DIE_ERSTEN_AUFTRAEGE_NACH_FREIGABE.md`. Abhängigkeit: WK-M00-001 bis WK-M00-004. QAEvidenceID: `M00-EV-006` in `docs/evidence/M00/WK-M00-005/dateien.json`. Reviewer: `OFFEN`. Rolle: QA & Release.

Abnahme, bestanden wenn `dateien.json` für jede dieser Dateien einen SHA256 enthält und die Datei im Baum liegt: `docs/M00_README.md`, `docs/M00_IST_SOLL.md`, `docs/M00_BLOCKER.md`, `docs/M00_PRODUKTIONSPLAN.md`, `docs/M00_INVENTAR.md`, `docs/M00_ROLLEN.md`. Zusätzlich: die Menge der WorkIDs in diesem Plan und in `M00_ROLLEN.md` hat keine ID mit zwei verschiedenen Aufträgen. Status bleibt `FILE_CREATED`, weil kein Reviewer `APPROVED` eingetragen hat.

## M01 Backup und Restore

### WK-M01-001 — Isolierte Kopie — `BLOCKED`

Quelle: `BL59-01`. Abhängigkeit: WK-M00-005 und ein freigegebener Pfad. QAEvidenceID: `EV-WK-M01-001`, Datei `docs/evidence/WK-M01-001/restore.json` (fehlt). Reviewer: `OFFEN`. Rolle: QA & Release.

Abnahme, bestanden wenn `restore.json` die Felder `files`, `mismatch_count` und `editor_started` trägt, `mismatch_count` = 0 und `editor_started` = false. `files` ist die Liste Pfad plus SHA256 vor dem Löschen und nach dem Restore. Jede SHA256 der zweiten Spalte gleicht der ersten.

### WK-M01-002 — Laufender Editor, nur lesen — `PLANNED`

Quelle: `BL59-08`. Abhängigkeit: WK-M01-001. QAEvidenceID: `EV-WK-M01-002`, Datei `docs/evidence/WK-M01-002/editor_log_auszug.txt` (fehlt). Reviewer: `OFFEN`. Rolle: Unreal Engineer.

Abnahme, bestanden wenn der Auszug eine Zeile enthält, die mit `Engine Version:` beginnt, und eine Zeile `Plugins:` mit der gefundenen Pluginliste. `Genesis.uproject` wird nur gelesen. Ein Pfad, der `GenesisSlice` enthält, wird im Auszug als vorhanden oder fehlend gezählt und nicht geändert.

## M02 Fundamente und Save

`WK-M02-001`, `WK-M02-002`, `WK-M02-003` und `WK-M02-004` bleiben die vorhandenen Pakete. Status `FILE_CREATED`. Sie sind kein `TESTED` dieses Registers.

### WK-M02-001 — Vorhandener Save — `FILE_CREATED`

Quelle: Commit `e9eb043`, `Source/Genesis/Private/Save/`. Abhängigkeit: keine neue. QAEvidenceID: der vorhandene Ordner `docs/evidence/WK-M02-001/`. Reviewer: `OFFEN`. Rolle: Unreal Engineer.

Abnahme dieses Registers, bestanden als Dateibestand wenn `automation_report.json` und `crash_test.csv` in diesem Ordner liegen. Die Archivfelder (`succeeded` 5, `succeededWithWarnings` 1, `failed` 0, 15 Crash-Zeilen) werden zitiert und nicht erneut gewertet. Ein neuer Lauf ist WK-M02-007.

### WK-M02-007 — Save erneut in der isolierten Kopie — `BLOCKED`

Quelle: `BL59-03`, `DEC-07`. Abhängigkeit: WK-M01-001. QAEvidenceID: `EV-WK-M02-007`, Datei `docs/evidence/WK-M02-007/crash_matrix.csv` (fehlt). Reviewer: `OFFEN`, und ungleich dem Autor von `e9eb043`. Rolle: Unreal Engineer.

Abnahme, bestanden wenn die CSV genau diese `case`-Werte je mindestens einmal trägt: `crash_during_write`, `two_incarnations`, `load_old_schema`, `migration`. Jede dieser Zeilen hat `result` = `EGenesisSaveResult::Ok` und `consistent` = 1. Zeilenzahl dieser vier Fälle = 4. Die Datei nennt `run_date` später als 2026-10-18.

### WK-M02-006 — Save-Abnahmebericht — `BLOCKED`

Quelle: V60 `TRANSAKTIONSSAVE_ABNAHME.md`. Abhängigkeit: WK-M02-007. QAEvidenceID: `EV-WK-M02-006`, Datei `docs/evidence/WK-M02-006/abnahme.json` (fehlt). Reviewer: `OFFEN`. Rolle: QA & Release.

Abnahme, bestanden wenn `abnahme.json` die SHA256 von `crash_matrix.csv` enthält, `reviewer` ungleich `author` ist und `decision` = `APPROVED`. Heute fehlt die Datei.

`WK-M02-002`, `WK-M02-003` und `WK-M02-004` bleiben `FILE_CREATED`. Ein Wiederholungslauf bekommt eine neue ID und überschreibt diese drei nicht.

## M03 Vertikalschnitt VS01

Die sechs Abläufe A–F stehen in `11_V23_VS01_HAUPTABLAEUFE_6.csv`. Jede Zeile trägt `ADULT_VERTICAL_SLICE_TEST_SEPARATE_FROM_MAIN_INCARNATION`. Die Titelzeile von F nennt einen getrennten QA-Durchlauf.

### WK-M03-001 — Rechteblatt der 38 GLBs — `BLOCKED`

Quelle: `BL59-02`, 28 V39-Zeilen. Abhängigkeit: WK-M00-004. QAEvidenceID: `EV-WK-M03-001`, Datei `docs/evidence/WK-M03-001/rechte_38.csv` (fehlt). Reviewer: `OFFEN`. Rolle: QA & Release.

Abnahme, bestanden wenn die CSV 38 Datenzeilen hat, die Dateinamen gleich den 38 GLBs sind, und jede Zeile entweder `Authorization` ungleich `NONE` plus einen existierenden Belegpfad trägt oder `gesperrt` = `ja`. Eine Zeile mit `Authorization` = `NONE` und `gesperrt` ungleich `ja` ist ein Fail. Import in Unreal zählt die gesperrten Dateinamen und endet mit Importzahl 0 für diese Namen. Die Dateien in `assets/source_glb/` werden dabei nicht gelöscht.

### WK-M03-006 — Rollen N01–N08 — `PLANNED`

Quelle: `18_V24_NPCS_8_CANON_ROLLEN.csv`. Abhängigkeit: WK-M00-003. QAEvidenceID: `EV-WK-M03-006`, Datei `docs/evidence/WK-M03-006/rollenvergleich.json` (fehlt). Reviewer: `OFFEN`. Rolle: Story & Kanon.

Abnahme, bestanden wenn die JSON acht Einträge N01–N08 enthält und jeder `RoleAsSource` zeichengleich der folgenden CSV-Zelle ist. Zahl der abweichenden Rollenstrings = 0.

```
N01 Werkstattbesitzer/in (`WorkshopOwner`)
N02 Reparaturkundin/-kunde (`RepairCustomer`)
N03 Marktbetreiber/in (`MarketOwner`)
N04 Lieferperson (`DeliveryDriver`)
N05 Gemeindekoordinator/in (`CommunityCoordinator`)
N06 Wetterbeobachter/in (`WeatherObserver`)
N07 Bewohner/in A (`ResidentA`)
N08 Bewohner/in B (`ResidentB`)
```

### WK-M03-002 — Sandbox-Map — `PLANNED`

Quelle: V61-Regel zu `GenesisSlice` und Default-Map. Abhängigkeit: WK-M01-002 und WK-M03-001. QAEvidenceID: `EV-WK-M03-002`. Reviewer: `OFFEN`. Rolle: Unreal Engineer.

Abnahme, bestanden wenn `git diff --name-only` der Sandbox-Änderung 0 Pfade mit dem Teilstring `GenesisSlice` enthält und `Config/DefaultEngine.ini` die Zeilen `EditorStartupMap=/Game/Maps/L_GenesisTest.L_GenesisTest` und `GameDefaultMap=/Game/Maps/L_GenesisTest.L_GenesisTest` unverändert lässt. Die neue Map hat einen anderen Asset-Namen.

### WK-M03-003 — Ein GLB, Maßwürfel — `PLANNED`

Quelle: V61-Schritt 4, `IMPORT_PLAN.txt`. Abhängigkeit: WK-M03-001 und WK-M01-001. QAEvidenceID: `EV-WK-M03-003`, Datei `docs/evidence/WK-M03-003/mass.csv` (fehlt). Reviewer: `OFFEN`. Rolle: 3D & Animation und Unreal Engineer.

Abnahme, bestanden wenn die CSV eine Zeile `cube` trägt mit `blender_meters` im Intervall 0,999 bis 1,001 und `unreal_cm` im Intervall 99,9 bis 100,1, plus `blender_version` als nicht leere Zeichenkette und `mesh_count` als ganze Zahl. Graybox-Maße stehen in eigenen Spalten und tragen `normativ` = `nein`. Das Feld `quality_pass` bleibt `false`.

### WK-M03-004 — Abläufe A–E — `PLANNED`

Quelle: V23-Abläufe A–E. Abhängigkeit: WK-M03-002 und WK-M02-006. QAEvidenceID: `EV-WK-M03-004`, Datei `docs/evidence/WK-M03-004/durchlauf.json` (fehlt). Reviewer: `OFFEN`. Rolle: Unreal Engineer. Story & Kanon prüft die IDs.

Abnahme, bestanden wenn `duration_minutes` >= 30 und <= 45, `save_load_mid_quest` >= 1, und jede verwendete Quest-ID in der Menge {VS01-A, VS01-B, VS01-C, VS01-D, VS01-E} oder in der Menge der 43 Missions-IDs aus `43_MISSIONSANKER.csv` liegt. Ablauf F hat ein eigenes Feld `f_separate` = true und zählt nicht in die 30–45 Minuten.

### WK-M03-005 — Pilot Brücke R04 — `PLANNED`

Quelle: V23-Ablauf C, 13 Dateien `VS01_R04_BRUECKE_001` bis `_013`. Abhängigkeit: WK-M03-003. QAEvidenceID: `EV-WK-M03-005`. Reviewer: `OFFEN`. Rolle: 3D & Animation. Gewerk: Story & Kanon.

Abnahme, bestanden wenn 13 GLB-Dateien dieses Präfixes im Baum liegen, die SHA256 von 004 und 005 gleich `aa103052582d842c302cd50d7bd54d6fb79567bd5fdf1914aee93699df344b7e` sind, und eine Beschlussdatei `docs/evidence/WK-M03-005/dublette.md` existiert, bevor eine der beiden Dateien ersetzt wird. Für jedes danach freigegebene Mesh gelten die sieben Tore aus WK-M04-003. Ein Leveltext, der die Steinbrücke einem Holzgewerk zuweist, ist ein Fail.

## M04 3D-Master

### WK-M04-001 — Werkstatt R03 — `PLANNED`

Quelle: 15 Dateien `VS01_R03_WERKSTATT_001` bis `_015`, N01 und N02. Abhängigkeit: WK-M03-005. QAEvidenceID: `EV-WK-M04-001`, Datei `docs/evidence/WK-M04-001/werkstatt.json` (fehlt). Reviewer: `OFFEN`. Rolle: 3D & Animation.

Abnahme, bestanden wenn alle drei gelten: die 15 GLBs liegen noch im Baum; `usage` = `Reparatur- und Generatorwerkstatt` und die Zeichenkette `Schreinerei` kommt in `werkstatt.json` 0 Mal vor; die Felder `start_ge`, `repair_reward_ge` und `part_cost_ge` sind ganze Zahlen und gleich den drei ganzen Zahlen, die das Evidence-Skript aus `GENESIS_V23_Paket__02_Vertical_Slice_Ablauf_und_Backlog.md` in die Felder `source_start_ge`, `source_repair_reward_ge` und `source_part_cost_ge` schreibt. Zusätzlich je ersetztem Mesh die sieben Tore aus WK-M04-003 und eine Rechtezeile aus WK-M03-001 mit `gesperrt` ungleich `ja`.

### WK-M04-002 — Erscheinung N01–N08 — `BLOCKED`

Quelle: `DEC-02`, `BL59-11`. Abhängigkeit: acht Einzelbeschlüsse. QAEvidenceID: `EV-WK-M04-002`, acht Dateien `docs/evidence/WK-M04-002/N01.json` bis `N08.json` (fehlen). Reviewer: `OFFEN`. Rolle: Story & Kanon.

Abnahme, bestanden wenn jede der acht Dateien `decision` = `entschieden`, ein Datum und einen `reviewer` trägt, und erst danach eine Masterdatei mit diesem NPC-Präfix hinzukommt. Solange `AppearanceStatus` in der Rollen-CSV `NOT_APPROVED` ist und die acht Dateien fehlen, bleibt der Status `BLOCKED`.

### WK-M04-003 — Sieben Tore je Master — `PLANNED`

Quelle: `03_VERBINDLICHE_3D_MASTER_UND_UE_ABNAHME.md`. Abhängigkeit: das Pilotpaket und WK-M03-001. QAEvidenceID: `EV-WK-M04-003`, je Mesh ein Ordner `docs/evidence/WK-M04-003/<MeshID>/` (fehlt). Reviewer: `OFFEN`. Rolle: 3D & Animation, Import Unreal Engineer, Abnahme QA & Release.

Abnahme, bestanden für ein Mesh wenn der Ordner genau diese sieben Dateien enthält und jede nicht leer ist: `front.png`, `seite.png`, `ruecken.png` (dieselbe `blend_sha256` in `meta.json`), `material.json`, `mass.csv` mit dem Würfelmaß aus WK-M03-003, `rig.json` mit `rig` = `vorhanden` oder `rig` = `N/A` plus `begruendung` länger als 20 Zeichen, `ue_import.log` mit dem Asset-Pfad. `meta.json` nennt zusätzlich UV-Kanalzahl, LOD-Zahl und `collision` = `ja` oder `nein`. Ein einzelnes Sammelbild ohne die drei Dateien ist ein Fail. Zahl der fehlenden der sieben Dateien = 0.

### WK-M04-004 — 40 Animationen — `SOURCE_MISSING`

Quelle: `40_ANIMATIONEN_STATUS.csv`, IDs `VS01_AN_001` bis `VS01_AN_040`. Abhängigkeit: ein Rig, das WK-M04-003 besteht. QAEvidenceID: `EV-WK-M04-004`. Reviewer: `OFFEN`. Rolle: 3D & Animation.

Abnahme, bestanden wenn 40 Aktionsdateien existieren, ihre Namen die 40 AnimIDs tragen, und jede eine UE-Logzeile `played` hat. Heute ist die Zahl der FBX in der Übergabe 0. Status bleibt `SOURCE_MISSING`, bis die Zahl 40 erreicht.

## M05 Lebenszyklus

### WK-M05-001 — C01 bis C04 — `PLANNED`

Quelle: ScriptLock, `01_KANON_FILMSZENEN_22.csv` Spalte `SourceSegmentSHA256`. Abhängigkeit: WK-M00-003. QAEvidenceID: `EV-WK-M05-001`, Datei `docs/evidence/WK-M05-001/segmente.json` (fehlt). Reviewer: `OFFEN`. Rolle: Story & Kanon.

Abnahme, bestanden wenn `segmente.json` für C01, C02, C03 und C04 je `delivered_sha256` gleich `SourceSegmentSHA256` der CSV zeigt. Zahl der ungleichen Szenen = 0. Die vier Soll-Hashes stehen in der CSV und werden von dort gelesen, nicht neu festgelegt.

### WK-M05-002 — C05 bis C14 — `PLANNED`

Quelle: ScriptLock, Phasen N05–N08. Abhängigkeit: WK-M05-001 und WK-M02-006. QAEvidenceID: `EV-WK-M05-002`, Datei `docs/evidence/WK-M05-002/save_load.json` (fehlt). Reviewer: `OFFEN`. Rolle: Unreal Engineer. Grenzen: Story & Kanon.

Abnahme, bestanden wenn nach Laden `age_ms` und `stage` gleich den Werten vor dem Speichern sind, Differenz von `age_ms` = 0. Das Feld `test_profile_is_canon` = false. Altersgrenzen in der JSON sind die Zeichenketten, die Story & Kanon aus den Szenen C05–C14 in `bounds.json` schreibt. Eine Grenze ohne diese Datei wird nicht als Kanon gewertet.

## M06 Echo und Wiedergeburt

### WK-M06-001 — Echo nach CON33-01 — `PLANNED`

Quelle: Beschluss PR #3, 23.10.2026, 01:51 Berlin. Abhängigkeit: WK-M00-003. QAEvidenceID: `EV-WK-M06-001`, Datei `docs/evidence/WK-M06-001/echo.json` (fehlt). Reviewer: `OFFEN`. Rolle: Story & Kanon, Raum 3D & Animation.

Abnahme, bestanden wenn alle fünf gelten: ScriptLock-SHA256 = `b23a047b13c1a7d77d00679c757f4fbcaa6cfc3e736305a7f77152c072ce732d`; `rooms_library` enthält C15, C16, C17 und C19; `temple_mesh_count` = 0; `column_mesh_count` = 0; `library_outside_exception` = 0 (Bibliothek nur in diesen vier Kapiteln). Die Registerzeile N09 bleibt im Originalregister stehen. Der Beschluss ersetzt sie für den Bau.

### WK-M06-002 — Wiedergeburt — `BLOCKED`

Quelle: `DEC-07`, Phasen N12–N14. Abhängigkeit: WK-M02-006 und WK-M06-001. QAEvidenceID: `EV-WK-M06-002`, Datei `docs/evidence/WK-M06-002/rebirth.json` (fehlt). Reviewer: `OFFEN`. Rolle: Unreal Engineer.

Abnahme, bestanden wenn `soul_tx` = `world_tx` = `life_tx`, `crash_case` = `ok`, und `c19_asset_count_before_reveal` = 0.

## M07 Filme, Ton, UI

### WK-M07-001 — C00-Master und C20 — `BLOCKED`

Quelle: `BL59-05`, `DEC-06`. Abhängigkeit: WK-M03-001 für die genutzten Medien. QAEvidenceID: `EV-WK-M07-001`, Datei `docs/evidence/WK-M07-001/fingerprint.json` (fehlt). Reviewer: `OFFEN`. Rolle: Audio & Cinematics.

Abnahme, bestanden wenn `c00_sha256` = `c20_playback_sha256`, `audio_sample_count_delta` = 0 und `frame_delta` = 0. Eine zweite Mediendatei mit anderem Hash, die C20 zugeordnet ist, ist ein Fail.

### WK-M07-002 — 113 Shots und deutsche Cues — `PLANNED`, Aufnahmen `SOURCE_MISSING`

Quelle: `CINEMATIC_SHOTS.csv`, V33-Register (24 Cues, 24 Gameplay-Shots, 12 HUD, 19 Interaktionen). Abhängigkeit: WK-M07-001 für C00. QAEvidenceID: `EV-WK-M07-002`. Reviewer: `OFFEN`. Rolle: Audio & Cinematics.

Abnahme, bestanden wenn die Zahl der Shot-Zeilen mit Sequencer-Pfad = 113, die Zahl der Cue-IDs mit vorhandener WAV = 24, und jede dieser WAV eine Rechtezeile mit `Authorization` ungleich `NONE` hat. Heute ist die WAV-Zahl in der Übergabe 0. Dieser Teil bleibt `SOURCE_MISSING`, bis die Zahl 24 erreicht.

### WK-M07-003 — UI — `PLANNED`

Quelle: V33, 12 HUD-Zustände, 19 Interaktionsverträge. Abhängigkeit: WK-M07-002 für Zeilen mit Sprache. QAEvidenceID: `EV-WK-M07-003`, Datei `docs/evidence/WK-M07-003/ui_counts.json` (fehlt). Reviewer: `OFFEN`. Rolle: Unreal Engineer. Texte: Story & Kanon.

Abnahme, bestanden wenn `hud_assets` = 12, `interaction_assets` = 19, und `c19_string_hits_before_reveal` = 0.

## M08 Phasen, QA, Leistung, Zugang

### WK-M08-001 — N00 bis N16 — `PLANNED`

Quelle: `17_SPIELPHASEN_STATUS.csv`, `12_V61_NEUE_ABNAHMETESTS.csv`. Abhängigkeit: die abgeschlossenen Pakete M03 bis M07 der jeweiligen Phase. QAEvidenceID: `EV-WK-M08-001`, Datei `docs/evidence/WK-M08-001/tests.csv` (fehlt). Reviewer: `OFFEN`. Rolle: QA & Release.

Abnahme, bestanden wenn `tests.csv` 390 Zeilen hat, die `QA_ID`-Menge gleich der V61-CSV ist, und `not_run_count` = 0. `ReadyForAAAProduction` einer Phase wird YES nur, wenn jede Anforderungszeile dieser `StageID` eine Evidence-Datei hat. Heute ist `not_run_count` der Quelle = 390.

### WK-M08-004 — Filmphasen N00, N13, N14 — `PLANNED`

Quelle: Szenenregister, Shots C00, C01, C19, C20. Abhängigkeit: WK-M07-001 und WK-M07-003. QAEvidenceID: `EV-WK-M08-004`, Datei `docs/evidence/WK-M08-004/film.json` (fehlt). Reviewer: `OFFEN`. Rolle: Audio & Cinematics.

Abnahme, bestanden wenn `film.json` die Shot-Zahlen C00 = 5, C01 = 4, C19 = 6, C20 = 7 trägt und jede Shot-ID einen Sequencer-Pfad hat, und `c19_asset_count_before_reveal` = 0 aus WK-M07-003 übernommen ist. Diese ID ist nicht WK-M08-001.

### WK-M08-002 — Leistung — `PLANNED`

Quelle: V34 `06_RENDERING_PERFORMANCE_UND_ACCESSIBILITY.md` und `BL59-13`. Abhängigkeit: ein startbarer Build und eine benannte Referenzmaschine. QAEvidenceID: `EV-WK-M08-002`, Datei `docs/evidence/WK-M08-002/frame.csv` (fehlt). Reviewer: `OFFEN`. Rolle: QA & Release.

Abnahme, bestanden wenn die CSV für 1920×1080 und für 2560×1440 je `p50_ms`, `p99_ms`, `one_percent_low_ms` und `gpu_memory_mb` als Zahlen trägt, `cpu` und `gpu` nicht leer sind, und `p50_ms` bei 1920×1080 <= 16,7. Liegt kein Maschinenname vor, bleibt das Zahlenziel unbewertet und der Status der Abnahme `BLOCKED`. Die 16,7 ms sind das in V34 genannte Rechenziel 60 FPS, keine Messung. Ein 30-FPS-Fallback ist `p50_ms` <= 33,3 und steht in einer eigenen Zeile `fallback`.

### WK-M08-003 — Zugänglichkeit — `PLANNED`

Quelle: die 15 Zeilen `V61-N16-001` bis `V61-N16-015`. Abhängigkeit: WK-M08-001. QAEvidenceID: `EV-WK-M08-003`, Datei `docs/evidence/WK-M08-003/n16.csv` (fehlt). Reviewer: `OFFEN`. Rolle: QA & Release und Unreal Engineer.

Abnahme, bestanden wenn `n16.csv` genau diese 15 IDs je einmal mit `pass` = `ja` enthält:

`V61-N16-001` Hauptmenü, `V61-N16-002` Ladebild und Optionen, `V61-N16-003` Interaktionsanzeigen, `V61-N16-004` Sensitivitätsoptionen, `V61-N16-005` Tastatur, Maus, Controller und Accessibility-Profil, `V61-N16-006` Audio-Subsystem, `V61-N16-007` Speicher-Schema, `V61-N16-008` Migration und Recovery, `V61-N16-009` NPC-Autonomie, `V61-N16-010` Deadlock und Solo-Alternativen, `V61-N16-011` VRAM/FPS-Budget, `V61-N16-012` Releasebuild, `V61-N16-013` Durchlauf der 17 Phasen, `V61-N16-014` Save/Load je Phasenübergang, `V61-N16-015` deutscher Text, Lip-Sync, Untertitel.

Für `V61-N16-005` gilt zusätzlich: die Settings-Datei nennt mindestens je ein Binding für Tastatur, Maus und Controller und mindestens eine `accessibility_profile_id`. Zahl der IDs mit `pass` ungleich `ja` = 0.

## M09 Release

### WK-M09-001 — Release-Build — `BLOCKED`

Quelle: Masterprompt-Schluss, `BL59-02`. Abhängigkeit: WK-M08-001, WK-M08-002, WK-M08-003 und WK-M03-001. QAEvidenceID: `EV-WK-M09-001`, Datei `docs/evidence/WK-M09-001/builds.json` (fehlt). Reviewer: `OFFEN`. Rolle: QA & Release.

Abnahme, bestanden wenn zwei Build-Läufe dieselbe SHA256 der gepackten Datei tragen, die Rechte-CSV der enthaltenen Dateien 0 Zeilen mit `Authorization` = `NONE` hat, und `reviewer` ungleich `build_author` ist. Heute existiert der Build nicht.

### WK-M09-002 — Migration — `PLANNED`

Quelle: Masterprompt. Abhängigkeit: WK-M09-001. QAEvidenceID: `EV-WK-M09-002`. Reviewer: `OFFEN`. Rolle: QA & Release.

Abnahme, bestanden wenn der Pull Request als Basis `main` nennt, die SHA256 aus `builds.json` im Bericht steht, und der Branch kein Force-Push auf `main` ist. Direktes Schreiben auf `main` ist ein Fail.

## Abhängigkeiten

WK-M00-001 → WK-M00-002 → WK-M00-003 → WK-M00-005.

WK-M00-001 → WK-M00-004 → WK-M00-005.

WK-M00-005 → WK-M01-001 → WK-M01-002 → WK-M03-002.

WK-M01-001 → WK-M02-007 → WK-M02-006 → WK-M03-004 und WK-M06-002.

WK-M02-001 bleibt der vorhandene Save und ist keine Abhängigkeit des Neulaufs.

WK-M00-004 → WK-M03-001 → WK-M03-003 → WK-M03-005 → WK-M04-001 → WK-M04-003.

WK-M00-003 → WK-M03-006.

WK-M04-002 hängt an `DEC-02`.

WK-M00-003 → WK-M06-001 → WK-M06-002.

WK-M07-001 hängt an `BL59-05` und an WK-M03-001. WK-M08-004 hängt an WK-M07-001 und WK-M07-003.

WK-M08-001 hängt an den abgeschlossenen Paketen M03–M07. WK-M09-001 hängt an M08 und an WK-M03-001.
