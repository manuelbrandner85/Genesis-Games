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

## Was noch NICHT existiert
- Kein Level, keine Spielfigur, keine Spielsysteme, keine Assets (Content-Ordner leer).
- Kein Start des Editors mit Grafik (erster Start kompiliert Shader, dauert länger).
- Kein Push zu GitHub.
- Offene Kreativentscheidungen: ScriptLock-Endfreigabe, C15/C16 (CON33-01), Epochenumfang.

## Nächster Schritt (wartet auf Freigabe)
WK-M02-001: Grundgerüst – GameInstance, Soul/World/Life-Datenmodell, transaktionaler SaveBundle mit automatisiertem Abbruch-Test.
