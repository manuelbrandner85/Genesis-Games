# GENESIS – Ehrlicher Projektstand

Stand: 2026-10-18 · Zweig `setup/ue58-projekt` (auf GitHub gepusht, `main` unverändert)

## WK-M01-010 – Neues UE-5.8.3-C++-Projekt · Status: GETESTET (lokal)

| Was | Datei / Beleg | Ergebnis |
|---|---|---|
| Projektdatei | `Genesis.uproject` (EngineAssociation 5.8) | vorhanden |
| C++-Modul `Genesis` | `Source/Genesis/*`, `Source/*.Target.cs` | kompiliert: `Build.bat GenesisEditor Win64 Development` → `Result: Succeeded` (41 s) |
| Rendering-Grundeinstellung | `Config/DefaultEngine.ini` | DX12 SM6, Lumen GI + Reflexionen, Hardware-Raytracing, Virtual Shadow Maps, Nanite, TSR, keine Auto-Belichtung |
| Plugins | StateTree, GameplayStateTree, ModelingTools, ModelContextProtocol + AllToolsets (nur Editor) | geladen laut Log |
| Git LFS | `.gitattributes` | uasset, umap, blend, fbx, glb, gltf, usd, png, jpg, exr, tga, hdr, wav, ogg, mp4, mov, ttf, otf, zip |
| Editor-Starttest | `UnrealEditor-Cmd -nullrhi`, Log `Saved/Logs/SmokeTest.log` | „Engine is initialized“, Modul `Genesis` geladen, sauberes „Exiting“; 0 Warnungen. 17× `LogAutomationTest: Error: Condition failed` stammen aus dem Engine-eigenen Selbsttest `UE::UnifiedErrorTest`, nicht aus GENESIS |

## WK-M02-001 – Soul/World/Life + transaktionaler SaveBundle · Status: GETESTET (lokal)

| Was | Datei / Beleg | Ergebnis |
|---|---|---|
| Datenmodell | `Source/Genesis/Public/Save/GenesisSaveTypes.h` | Soul (SoulId, Echo-Erinnerungen, Enthüllungs-Guards), World (Jahr, Tag, Uhrzeit, Seed, Ereignisse), Life (LifeIndex, BodyAssetId, Lebensabschnitt, Alter, Ort, Transform, Beziehungen, Erinnerungen, Inventar, Geld in Cent) – immer gemeinsam in einem Bundle |
| SaveStore | `Source/Genesis/Private/Save/GenesisSaveStore.cpp` | Temp-Datei schreiben + auf Platte flushen → zurücklesen + SHA1 prüfen → atomarer Austausch (`ReplaceFileW`, alte Datei wird `.bak`); Laden: Hauptdatei, sonst Sicherung, `.tmp` nie |
| GameInstance + Subsystem | `UGenesisGameInstance`, `UGenesisSaveSubsystem` (in `DefaultEngine.ini` eingetragen) | kompiliert; im Spiel noch nicht benutzt (es gibt noch kein Level) |
| Automatische Tests | `Genesis.Save.*` (6 Tests), Bericht `docs/evidence/WK-M02-001/automation_report.json` | 6/6 bestanden (1 mit erwarteter Warnung „Sicherung geladen“): Hin-und-zurück, Abbruch nach Temp-Datei, halbe Temp-Datei, defekte Hauptdatei → Sicherung, Abbruch beim ersten Speichern, zukünftiges Schema abgelehnt |
| Echter Absturztest | `Tools/Tests/Run-SaveCrashTest.ps1`, `docs/evidence/WK-M02-001/crash_test.csv` | 15/15 harte Prozessabbrüche (TerminateProcess, 20–1500 ms nach Start des Dauerspeicherns, ~200 KB je Stand): jedes Mal vollständiger Stand geladen, Soul/World/Life aus derselben Transaktion, Sequenz nie rückwärts |

Einschränkung: In allen 15 Läufen lag der Abbruch nie genau im Austauschmoment (`backup=0`); der Rückfall auf `.bak` ist nur durch den automatischen Test mit beschädigter Hauptdatei belegt. Stromausfall-Test (echtes Ausschalten) wurde nicht gemacht.

## WK-M02-002 + WK-M02-003 – Spielfigur, Steuerung, Kamera, Testlevel, Austausch-Schnittstelle · Status: GETESTET (lokal)

| Was | Datei / Beleg | Ergebnis |
|---|---|---|
| Spielfigur | `AGenesisCharacter` | Gehen 150 cm/s (5,4 km/h), Laufen 360 cm/s (13 km/h), Sprung ~45 cm, Treppenstufe bis 40 cm, begehbar bis 44° |
| Steuerung | `UGenesisInputSet` (Enhanced Input, im Code definiert) | WASD/Pfeile + linker Stick (Totzone 15 %), Maus + rechter Stick (bildratenunabhängig, 160 °/s), Leertaste/A springen, Shift halten bzw. L3 umschalten = laufen |
| Third-Person-Kamera | Spring Arm 2,8 m, Schulterversatz, Kollisionsprüfung, leichte Nachführung, Blick −70°…+55° | Kamera hängt an der **Vertrags**-Ankerhöhe (162,6 cm), nicht am Mesh |
| Austausch-Schnittstelle | `UGenesisCharacterAppearance` (DataAsset: Mesh, AnimBP, Materialien, Physik, Kapsel), `UGenesisCharacterRegistry` (Projekteinstellungen: feste ID → Aussehen + **Proportions-/Kameravertrag**) | Spiellogik kennt nur `CharacterAssetId`; ein Modell wird nur eingesetzt, wenn es den Vertrag erfüllt (Höhe, Ankerhöhe, Pflichtknochen, Skelett, AnimBP-Skelett, aufrecht, Fußsohle auf Kapselboden), sonst bleibt das alte |
| Basismodell (Proxy) | UE5-Mannequin Manny/Quinn aus der Engine-Installation, `Content/Genesis/Characters/Appearances/DA_Proxy_Adult_M/F` | gemessen: 180,5 / 180,2 cm, Kopfknochen 162,6 / 162,5 cm (`docs/evidence/WK-M02-002/measurements.json`). **Proxy, kein GENESIS-Charakter** |
| Testlevel | `Content/Maps/L_GenesisTest.umap`, erzeugt durch `Tools/Editor/build_wk_m02_002.py` | 120×120 m Boden, Treppe (17/29 cm), Rampe 10°, Wand, Durchgang 1×2,1 m; Sonne 90 000 lx, Himmel, Wolken, Nebel, Belichtung physikalisch ISO 100, 1/100 s, f/16 |
| Automatische Tests | `Genesis.*` – 12 Tests, Bericht `docs/evidence/WK-M02-002/automation_report.json` | **12/12 bestanden** (1 mit erwarteter Warnung): Tastenbelegung, alle Registry-Einträge erfüllen Vertrag, Modelltausch behält Spiellogik und Kamerahöhe (162,60 → 162,60 cm), Vertragsverstoß wird abgelehnt, Wechsel per ID, Gehen/Laufen/Springen im echten Testlevel per Play-in-Editor |
| Spielstart mit Grafik | `-game -GenesisAutoTest`, Log `docs/evidence/WK-M02-002/game_autotest.log`, Bild `autotest_shot.png` | Figur aufrecht, geht 4,0 m, am Boden, Kamera auf 164,8 cm, Schatten sichtbar |

Unterwegs gefundene und behobene Fehler: Mesh lag um 90° gekippt (Python-Rotator falsch zugeordnet; neue Vertragsregel „aufrecht“ erkennt das jetzt), erstes Bild komplett weiß (Belichtung jetzt physikalisch statt als Aufhellung), Kamera-Test prüfte relative statt absolute Höhe.

Nicht getestet: echte Bedienung mit physischem Controller und Maus durch einen Menschen (nur Tastenbelegung und Bewegungslogik sind automatisch geprüft). Kein Reality Check bestanden – Level und Figur sind bewusst Graubox/Proxy, nicht fotorealistisch.

**Lizenz-Hinweis:** Das Mannequin ist Epic-Template-Inhalt. Weil das Repo öffentlich ist, liegt es **nicht** im Repo (`.gitignore`), sondern wird nach dem Klonen mit `Tools/Setup/Copy-EngineMannequin.ps1` aus der lokalen Engine kopiert.

## Was noch NICHT existiert
- Keine GENESIS-Figuren (nur Proxy-Mannequin), keine Spielwelt außer dem Graubox-Testlevel, keine NPCs, Missionen, Dialoge, UI.
- Wiedergeburt (Leben abschließen → Erinnerungen in die Seele → neues Leben) ist nur als Datenmodell vorbereitet, nicht programmiert.
- Speichern ist noch nicht an Figur/Welt angebunden (Position, Zeit).
- Offene Kreativentscheidungen: ScriptLock-Endfreigabe, C15/C16 (CON33-01), Epochenumfang.

## Nächster Schritt (wartet auf Freigabe)
WK-M02-004: WorldClock + LifeCycle (Weltzeit, Jahreszeiten, Alterung, Lebensabschnitte) an das Speichersystem anbinden, inkl. Position der Figur; Test: Speichern/Laden stellt Zeit, Alter und Ort exakt wieder her.
