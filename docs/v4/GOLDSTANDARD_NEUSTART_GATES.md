# GENESIS V4 · Goldstandard 2026 – Elf Prüftore

| Gate | Inhalt | Nachweis | Pflicht |
|---|---|---|---|
| G0 | Read-only Quellen-/Hardware-/Engine-/Git-Audit | inventory.json, Toolversions, Risiken | Ohne G0 keine Projektänderung |
| G1 | Neuen Pfad genehmigen, frisches UE-C++-Template | neuer separater Ordner, `Genesis.uproject`, kein Alt-Repo-Diff | separates Projekt |
| G2 | UE C++ kompiliert / Editor startet | Build-Log, Screenshot/Editor-Log | ERROR=0 im Projektcode |
| G3 | Blender-Asset-Smoke | `.blend`+ `.fbx`, Modell-/Maßtest | kein Fake |
| G4 | Unreal-Asset-Handoff | Assetpfad, Registry Readback, Testmap | UE-Import real |
| G5 | Spielbare Figur | WASD/Controller/Kamera/Sprung, Menschentest | reale PIE-Tests |
| G6 | NPC/World/Mission | 3 Rollen, Tagesplan, Dialogkonsequenz, Save/Load | gültige Quelle, keine Softlocks |
| G7 | Grafische/akustische Abnahme | PBR, Licht/Animation/Untertitel/Audio, Rechte | menschliche Sichtung |
| G8 | Simulations-Langtest | Zeitsprung, Rebirth, NPC Save, Migration, Weather, Chaos | echte Logs |
| G9 | Windows Standalone | gepackter Build, startet ohne Editor/Claude | sauberer Smoke-Log |
| G10 | Director-Freigabe | Liste freigegebener Assets/WorkIDs, bekannte Mängel | ausdrückliche menschliche Zustimmung |

**Scope-Sperre:** Kein massenhafter Content-Ausbau, bevor G10 bestanden ist. G0–G4 dürfen rein neutrale Testinhalte verwenden. Alle Kapitel/Story-Assets und finale Region nur aus freigegebenem Source-Lock.
