# GENESIS – verbindliche WorkID Roadmap
**Regel:** nur tatsächlich abgenommene Ergebnisse als fertig melden. Jede WorkID: Owner, Inputs, Changes, Proof, QA, KnownIssues.

## Phase 0 – Quellen, Sicherheit, Tools
| WorkID | Owner | Ergebnis | Abnahme |
|---|---|---|---|
| WK-000 | 01/02/03/04 | Read-only Repo- und Spielbibel-Inventar, Installations-/Berechtigungsliste, unklare Freigaben, gesicherter Branch | Repo-SHA, Versionen, Backupnachweis, Audit-Matrix |
| WK-001 | 04/05/07/12/24 | Blender→FBX→Unreal-Pipeline mit Testkiste inkl. 6 Referenz-/Turnaroundbildern | `.blend`, `.fbx`, reale UE Asset-Import-ID, Maße, Screenshot, Logs |
| WK-001B | 03/23/24 | Quellen-/Lizenz- und Assetmanifest initialisieren | mindestens 1 vollständiges Testmanifest, Rechtegate prüfbar |

## Phase 1 – echter Vertical Slice (eine glaubwürdige Region)
| WorkID | Owner | Ergebnis | Abnahme |
|---|---|---|---|
| WK-002 | 12/21/24 | steuerbare erwachsene Figur 2026, Kamera/Input/Controller, getesteter Game Loop, Save/Load | UE PIE und Standalone Build, Input-/Save-Tests |
| WK-003 | 05/07/09/13/22 | kleine Flussdorf-Region: Dorfkern, Markt, Brücke, Werkstatt, Wetterstation als **Arbeitshypothese aus Repo-Plan**, nicht verbindliche Originalstory | World Partition/Streaming, Interiors, Prop-Assets, LODs, Profiling |
| WK-004 | 14/16/24 | 3–4 NPCs mit Uhr/Tagesablauf, 1 Erinnerung & Beziehung | StateTree und persistente Save/Load-Tests |
| WK-005 | 15/02/24 | mindestens eine **originalquellenbelegte** Mission (z.B. Kandidat L08 nur nach Sichtung von V61/V62) mit mehreren Pfaden | Deadlock-Tests, Kausalevents + Wiedersehen nach Load |
| WK-006 | 05/06/08/09/10/11/04 | mindestens ein speziell für GENESIS angefertigter, rigbarer erwachsener Charakter (keine Manny-Proxy-Finalabnahme) | 360° Referenzsheet, .blend, Rig, FBX, Anim, UE-Tests |
| WK-007 | 20/21/22/24 | Hauptmenü, Untertitel, Accessibility, Sound, Debug HUD, Performancebudget | realer Standalone-Spieltest, Bildschirmbelege und Frametime |

## Phase 2 – Life & World System
- `WK-020` Lebensphasen, Gesicht/Körperalterung/Familienähnlichkeit, Kind-/Senior-Animation inkl. zeitlich konsistenter NPC-Generationen.
- `WK-021` Gesundheit, Krankenhaus, ärztliche Ereignisse, Rettung und echte Near-Death/Return-Logik.
- `WK-022` fortlaufende Weltjahr-Entwicklung 2026→spätere Jahre, Wachstum, Weltbestand, Spielstands-Migrationen, Weltzeit/Seasons/Wetter.
- `WK-023` Wohn-/Immobilienmarkt, Karriere/Unternehmen, Wirtschaft, Bank, Smartphone, Bildung, Behörden, Alltag und Interaktionen.
- `WK-024` Verkehr/Fahrzeuge (PKW, LKW, Bus, Zug, Fähre), internationale Reise-/Flugsysteme; zuerst eine echte, überprüfte Fahrzeug-/Reise-Ende-zu-Ende-Schleife.
- `WK-025` große Welt systematisch modular erweitern (nicht „volle Erde“ vortäuschen); Playtest- und LOD-Zonen.

## Phase 3 – Soul & Story
- `WK-030` endgültiger körperlicher Tod: transaktionaler Übergang Save→Echo, bei kurzen Leben und langen Leben korrekt.
- `WK-031` Jenseits-Energiewelt und Originalmodule J00–J24, nur aus vollständigen Originalquellen, mit echter Freigabe des aktuellen Jenseitskonzepts.
- `WK-032` Rebirth: gleiche `SoulID`, neue `LifeID`, neues Genom/Body, zeitlich fortlaufende Welt, keine Epochenwahl.
- `WK-033` 22 Szenen C00–C21 als Sequencer-/Interaktionsverträge aufstellen, ABER Original-Skriptfreigabe und C21-Konflikt vor storyrelevanter Umsetzung prüfen.
- `WK-034` C00 Originalaufnahme und C20 identisches Replay, C19-Spoilerbarrieren und Fallback-Cinematics testen.
- `WK-035` vollständiger Szenen-/Causal-/NPC-/Mission-Regressionstest über mehrere Leben.

## Phase 4 – Vollproduktion & Veröffentlichung
- `WK-040` vollständiges freigegebenes 3D-Asset- und Referenzregister, zusätzliche Welt-/Charakter/Vehicle-Produktion.
- `WK-041` deutsche Sprach-/Dialog-/Face-Rig-/Untertitel-Abnahme, Sound und Musik mit Lizenznachweisen.
- `WK-042` Quality/Accessibility/Mass-Playtesting, unvorhersehbare Saves und Edge-Case-Regression.
- `WK-043` reale PC-Grafikprofile, Performance-/Ladezeit-/Crash-Benchmarks auf Zielhardware.
- `WK-044` Windows Packaging, Installer, Store-/Rechtetexte, lokaler Installations- und Upgrade-Test, Releasefreigabe.

## Blocker-Regeln
- Originalscript/Freigabe fehlt: Architektur-, Technik-, rigging-, Smoke-, QA- und Greyboxjobs möglich; keine behauptete finale Kanon-/Dialog-/Szenenproduktion.
- Tool-/MCP-Zugriff fehlt: Test als `BLOCKED_TOOL_MISSING`, Install-/Connection-Anleitung statt „erfolgreich“.
- Skriptlogik widerspricht jüngerer Epochenregel: stoppe nur betroffenen Featurezweig; formuliere Entscheidungsvorlage.
- Behauptete Qualität ohne Build/Test/Beleg: QA `REJECTED_UNVERIFIED`.


## Zusätzliche WorkIDs: GAMEFORGE-Verbesserung 03 / Living World
Diese Aufgaben **ergänzen** die bestehenden WorkIDs und dürfen keine funktional identischen Subsysteme duplizieren. Genaue 50 Funktionsverträge: `original_md_unveraendert/GAMEFORGE_Verbesserung_03_Ultimate_Living_World_Simulation_GODMODE.md`.

| WorkID | Zweck | Erfolgskriterium |
|---|---|---|
| WK-LW-000 | Originaldatei vollständig lesen, SHA prüfen, 50 Funktionen inventarisieren, StudioBrain + Character 4.0 + GENESIS-Bestand zuordnen | verifizierter Quell-/Abhängigkeitsbericht und 50/50 Funktionsmatrix |
| WK-LW-010 | Reuse-Architektur: GENESIS WorldClock, Save, Lifecycle, World Event Bus, Entity-IDs | dokumentierte Ownership, API und Migrationstests; kein zweiter Clock/Save-Store |
| WK-LW-020 | Tageszeit, Wetter, Jahreszeiten, Umwelteinflüsse | nachweisbar synchronisierte 24h- und Wetterszenarien |
| WK-LW-030 | NPC-Identität, Bedürfnisse, Tagesabläufe, Smart Objects, Navigation | drei unabhängige NPCs mit korrekter Reservierung, Recovery und gespeicherter Identität |
| WK-LW-040 | Erinnerungen, soziale Beziehungen, Familie, Beruf, Interaktionsdialoge | echte NPC-Folgen nach Laden; keine Script-Lock-Verletzung |
| WK-LW-050 | Tiere, Ökologie, Biome, Ressourcen und Handel nach Kanon und Budget | deterministische Langlauftests und in-engine Tiere/Vegetation |
| WK-LW-060 | Missionen und Ereignisse mit GENESIS Verbesserung 3 integrieren | Quest-Zustandsautomat, Deadlock-/Spam-Tests, Story-Schutz |
| WK-LW-070 | Weltpartition, Streaming, Near/Mid/Far und Ressourcenregler | stabile Entity-IDs, Lasttests, Unreal Insights |
| WK-LW-080 | vollständig spielbarer, lebendiger Dorf-Vertical-Slice | echter Unreal-Build/PIE, Logs, Profile, QA-Abnahme |
| WK-LW-090 | Regression über Weltzeit/Generation/Rebirth/Migration/Story | reproduzierbare Langlauftests, kein Save-Verlust, Freigabe |

Soweit Arbeitspakete `WK-003`–`WK-005` usw. denselben Funktionsbereich abdecken, eine WorkID als Parent/Child verlinken, nie doppelt implementieren. Keine Fake-Tests, keine unsicheren Eingriffe ohne Freigabe.
