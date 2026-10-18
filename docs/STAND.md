# GENESIS – Ehrlicher Projektstand

Stand: 2026-10-18 · Zweig `setup/ue58-projekt` (nur lokal, nicht gepusht)

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

## Was noch NICHT existiert
- Kein Level, keine Spielfigur, keine Spielmechanik, keine Assets (Content-Ordner leer).
- Wiedergeburt (Leben abschließen → Erinnerungen in die Seele → neues Leben) ist nur als Datenmodell vorbereitet, nicht programmiert.
- Kein Start des Editors mit Grafik (erster Start kompiliert Shader, dauert länger).
- Kein Push zu GitHub.
- Offene Kreativentscheidungen: ScriptLock-Endfreigabe, C15/C16 (CON33-01), Epochenumfang.
