# 24 GENESIS-Rollenprofile für Claude Code / bestehendes StudioBrain

## Erstellungsregel
Für jede der untenstehenden Rollen eine **eigene Agenten-Konfiguration** anlegen, benennen `GENESIS-01` bis `GENESIS-24`, mit dem jeweiligen Prompt aus `agents/`. Diese Dateien definieren die Rolle unabhängig von einem bestimmten Claude Code-UI-Produkt. Prüfe vorab, ob du Claude-Code-Unteragenten wirklich erstellen darfst. Bei fehlenden API-/UI-Rechten erstellt der Orchestrator stattdessen Rollen-Dateien und verwendet sie sequenziell; er darf die Bots nicht fälschlich als aktiv melden.

## Rollenregister
| Bot | Titel | Exklusive Verantwortung |
|---|---|---|
| 01 | Master Director | Kanon, Abhängigkeiten, Freigabe, Auftragsvergabe, Ergebnisübersicht |
| 02 | Story & Script Guardian | C00–C21 und J00–J24, Continuity, Offenlegung von Konflikten |
| 03 | Production & Token Planner | Reihenfolge, Kosten, Kontextkompression, Aufgaben-/Assetregister |
| 04 | Tool / MCP Integration | tatsächliche Claude-Code→Windows→Blender→Unreal Verbindung, verfügbare CLI/MCP-Adapter, Logs |
| 05 | Reference / Concept Director | Mehransichten, Maße, Konsistenz, Referenzbild- und Shot-Register |
| 06 | Character 3D Artist | Menschen aller Altersstufen, Kleidung, individuelle Charaktere |
| 07 | Environment 3D Artist | Architektur, Props, Vegetation, Landschaften, modulare Bausätze |
| 08 | Rigging & Skinning | Skelett-/Face-Rigs, Retarget, Deformations-/Gewichtstests |
| 09 | PBR / Material Artist | UV, Texturen, Shader, Lookdev, Materialvereinheitlichung |
| 10 | Motion & Animation | Gehen, Gesten, Motorik, Übergänge, IK/Motion Matching |
| 11 | Facial & Lip-Sync | Mimik, Lippen, Blick, altersgerechte Ausdrucksregeln |
| 12 | Unreal Core Programmer | C++, Blueprints, Save, Gameplay, Input, Basiskomponenten |
| 13 | Unreal Open World Architect | World Partition, Level, PCG, Streaming, HLOD |
| 14 | NPC Intelligence | StateTree, Smart Objects, Tagesabläufe, Gedächtnis |
| 15 | Mission / Living Events | Zustandsgrafen, Begegnungen, Folgen, Deadlock-Suche |
| 16 | Society & Economy | Arbeit, Beziehungen, Bildung, Besitz, Banken, Behörden |
| 17 | Vehicles & Travel | LKW/PKW/Bahn/Bus/Fähren/Flugpassagier, Interaktionen |
| 18 | Life, Soul & Rebirth | Alter, Medizin/Tod, Jenseits/Seele/Rebirth, Weltkontinuität |
| 19 | Cinematic Director | Sequencer, ScriptLock-Szenen, Replays, Übergänge |
| 20 | Audio & German Voices | deutsche Dialoge, Foley, Ambient, Musik, Subtitle IDs |
| 21 | UI / UX & Accessibility | Hauptmenü, HUD, Smartphone, Controller, Optionen |
| 22 | Performance Architect | LOD/HLOD, VRAM, Streaming, Profiling und Grafik-Presets |
| 23 | Free Asset & Rights Curator | Asset-Quellen, Lizenzprüfung, Rechteregister |
| 24 | QA & Release Director | Build, Automation, Regressions-/Playtests, Packaging |

## Abgleich mit GAMEFORGE Living World 03
- Originaldatei `original_md_unveraendert/GAMEFORGE_Verbesserung_03_Ultimate_Living_World_Simulation_GODMODE.md` vor Aufgabenvergabe komplett lesen.
- Benannte StudioBrain-Zuständigkeiten aus Abschnitt 5/50 Funktionen übernehmen; Nummern 01–42 der GAMEFORGE-Rollen **nicht** mechanisch mit GENESIS-01–24 gleichsetzen.
- GAMEFORGE-Living-World-Bausteine primär GENESIS-Rollen 12/13/14/15/16/18/20/22/24 fachlich zuordnen, jedoch tatsächliches Mapping erst nach Inventur.
- GAMEFORGE StudioBrain-Jobs und Unreal Runtime-Weltzustand streng getrennt verwalten; bestehende Save-Subsysteme erweitern statt duplizieren.

## Schreibkonflikte vermeiden
- 01 vergibt WorkIDs und Assets in einem Zustandstracker. Ein Asset/Editor-Projekt darf immer nur **einen schreibenden Agenten** haben.
- 05 liefert Referenzen → 06/07 Modellierung → 08–11 Rig/Lookdev/Animation → 23 Rechte → 04 Import → 12/13 Integration → 22 Performance → 24 QA.
- Story-Szenen müssen 02 freigeben, bevor 19 filmt. Generierte KI-Stimmen/Bilder nur mit Rechteprüfung/Qualitätsgates.
- Andere Agents dürfen per Leserechte parallel analysieren; Build-/Editorjobs koordiniert 04.
- Zwischen Bot-Aufrufen nur WorkID, relevante File-Hashes, Diff und fehlende Informationen übertragen, nicht ständig das gesamte Script. Originaltexte referenzieren statt neu schreiben (Token sparen **ohne Informationsverlust**).

## Status und Revisions-Policy
Jeder Job hat `Owner, WorkID, Quellen-SHA, Basiscommit, geänderte Dateien, Prüfbelege, KnownIssues, BlockedBy, Status`. `ACCEPTED` ausschließlich nach QA. Agents dürfen nicht ihre eigenen Tests als alleinige Abnahme nehmen. Jede Konsistenz-/Lizenz-/Storyverletzung sperrt Merge bis zur Korrektur. Keine externe Agent-API erfunden.
