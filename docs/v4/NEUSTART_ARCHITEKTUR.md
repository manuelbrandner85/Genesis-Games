# Architektur: neues Unreal-Projekt, geschützte Quelle, Claude als Produktionsleitung

## Strict separate-root rule
`OLD_REPO` = nur lesen. `V4_HANDOFF_PACKAGE` = wiederverwendbare Dokumentation/Tools. `NEW_GAME_ROOT` = einziges aktives Game-Projekt, auf Freigabe frisch erzeugt. `SOURCE_VAULT` = Originalkanon, nicht destruktiv bearbeiten. `ARTIFACTS` = tatsächliche Blender-/UE-/Build-Dateien im neuen Projekt.

## Module in Abhängigkeitsreihenfolge
- Core: Engine-Projekt, Input, Kamera, Logging, BuildSystem, Featureflags, Save-/schema-Version.
- Soul/World/Life: persistente eindeutige IDs, Zeit, Weltfortschritt, Beziehungen und Erinnerungen, Tod/Jenseits/Rebirth, deterministische Replay-Abnahmen.
- Gameplay: Interaktion/Physics/Vehicle (nur nach Storybeleg), NPC StateTree/Smart Objects, Navmesh, GameplayTags, Missions- und Dialoggraph.
- World: World Partition, Data Layers, PCG, Wetter, Jahreszeiten, Near/Mid/Far-LOD, stabile EntityRegistry und GameplayEventBus.
- Presentation: Character/Material/Animation Rig, Lumen/Nanite per Hardwareprofil, UMG Accessibility, Sequencer C00–C21, deutsches Audio, MetaSounds.
- QA: Compile/PIE/Gauntlet/Package, Python AssetAudits, Unreal Insights, Windows-Bewegungstests und manuelle Abnahme.

## Erstes vollständig verifiziertes Asset
`SM_SmokeCrate_001` ist ein **technisches Testobjekt**, keine Storyrequisite. Blender erstellt `.blend` + `.fbx`, Export wird auf Disk geprüft, Unreal importiert (keine automatische Überschreibung), liest Asset zurück, instanziert in Testmap, erzeugt Screenshot/Log, testet Maße, Kollision und C++ Build. Erst danach wird hochwertige Referenz→3D-Pipeline mit freigegebenen echten Assets begonnen.

## Status / Nachweis
`SPEC_ONLY -> IMPLEMENTED_UNTESTED -> DCC_VERIFIED -> UE_IMPORTED -> PIE_VERIFIED -> PERFORMANCE_MEASURED -> HUMAN_APPROVED -> ACCEPTED`; abweichende Blocker `SOURCE_BLOCKED`, `TOOL_UNAVAILABLE`, `QA_FAILED`, `WAITING_APPROVAL`. Tests müssen sich mit Pfad/RunID/Toolversion wiederholen lassen. Kein Scheinfortschritt.

## Sicherheit und Realität
Python in Unreal nur Editor/Commandlet, C++/Blueprint in Runtime. Nicht jedes Objekt durch Claude live berechnen. Keine AI Cloud bei NPC-Laufzeitpflicht; kostenloser Offlinebetrieb vorsehen. Keine automatischen Rechteübertragungen aus Downloadportalen. Keine Verwaltung zweier konkurrierender StudioBrain-Systeme. Datenmodelle nicht duplizieren.

## Laufzeit und Budget
CPU/GPU/VRAM und Plattform des Ziel-PC bestimmen maßgeblich LOD, Anzahl NPCs, World Partition und Framebudgets. Keine fest versprochenen 60 FPS/1000 NPCs. UE-5.8-Vorlage ist nur ein lokal anzupassender Vorschlag; Versionsprüfung vor Build.
