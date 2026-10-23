# GENESIS – Verbesserung 08: Autonomous Quality Guardian

**Bestätigt:** JA zu allen zehn Verbesserungen am 23.10.2026.
**Status:** geplanter, fachlich freigegebener Entwicklungsumfang; keine hier erfolgte UE-Implementierung.
**Leitziel:** Keine Behauptung von AAA+: ausführbare Tests, unabhängige Abnahme, nachvollziehbare Regressionssicherheit.
**Gültigkeit:** nur bestehendes `manuelbrandner85/Genesis-Games`, Claude Code als Entwicklungsleitung, keine Story-Umschreibung.

### Produktionsfunktionen
1. Mindest-Gates: Datei wirklich da? Syntax? Build? UE-Import? PIE? Standalone? Assetvergleich? Performance? Lizenz? ScriptLock?
2. Modelltests: Abmessungen, UV, Skeleton, Materials, Pivot, Normals, Mesh-Topologie, Texturauflösung und Exportvalidität.
3. Charaktertests: Retarget, FootIK, Hand/Face, Kleidungsdurchdringung, Kinder-/Greis-Skelette und Animationsloops.
4. Missionstests: Auslöser, Entscheidung, Konsequenz, Deadlock, Skip/Load, NPC-Zustände, Spam und Softlock.
5. Story-Schutz: unveränderte C00–C21-J00–J24-Originalbytes wenn keine ausdrückliche Freigabe, C00/C20 identisch, C19-Spoiler-Guard.
6. Save-Regression: Migration, Crash-Consistency, WorldClock, Alter, Rebirth, NPC-ID- und Familienkontinuität.
7. Grafik: UE-Standbilder aus mehreren Blickwinkeln plus visuelle Freigabe der einzigartigen Modelle.
8. Langzeitsimulation: deterministische Seeds, Event-Budget, Save/Snapshot-Wiederaufnahme, abgeschnittene TimeSkip-Logs.
9. Performance: Unreal Insights, `stat unit`, GPU/VRAM, LOD Handoff auf tatsächlicher Hardware erfassen.
10. Unabhängigkeit: Ersteller liefert Artefakte, QA verifiziert neu; Ergebnisse werden `PASS`, `FAIL`, `SKIPPED_NO_ENGINE` oder `BLOCKED` dokumentiert.
11. CI auf Python/JSON/MD/Manifeste darf grün sein, **niemals** aus sich heraus Unreal-Laufzeit grün melden.
12. Keine Erfolgsquoten ohne Denominator und echte Testergebnisse; visuelle Nahaufnahme bedarf kreativer Sichtabnahme.
13. Every FAIL → nachvollziehbarer Bug-WorkID mit minimal reproduzierbarem Repro und Owner.
14. Release nur mit Lizenz- und Performance-Bericht, Savegame-Restore, Game Director signoff.

### Gates
`STATIC_PASS → TOOL_AVAILABLE → MODEL_PASS → UE_IMPORT_PASS → PIE_PASS → PROFILE_PASS → ART_REVIEW_PASS → ACCEPTED`. Ein nicht durchgeführter Gate bleibt `NOT_RUN`, er wird nicht still übersprungen. Beispiele `tools/qa/verify_package.py` und `docs/produktion/QA_TEST_MATRIX.csv`.

### Technischer Produktionsauftrag
Arbeite mit dem vorhandenen Repo, GAMEFORGE StudioBrain und Character Creation 4.0, sofern tatsächlich vorhanden. Ermittle Basiscommit, freigegebene Quellen und installierte Werkzeuge. Dokumentiere Architektur, konkrete Dateien, Tests und Evidenz. Führe nur genehmigte ungefährliche Schritte aus; für riskante Änderungen explizite Freigabe. Übergebe jeden Arbeitsschritt an unabhängige QA. `NOT_IMPLEMENTED` bleibt sichtbar, bis ein echter Editor-/Runtime-Nachweis vorliegt.

### Unabhängige Gate-Implementierung
`ArtifactReady` reicht nicht: der Validator sammelt Datei-Existenz, Hash, statischen Schema-/Geometriecheck, echten Blender-Reload, tatsächlichen UE-Import, Build, PIE, Gameplay-Regression, Profiler, Rechte und Creative-Approval. Ein Agent darf *nie* `ACCEPTED` selbst vergeben, ohne unabhängigen QA-Eintrag. Ein fehlender Test wird `NOT_RUN`, auch wenn alle vorhandenen Testläufe bestanden haben.

**Regressionstrategie:** Ausgangszustand aus `docs/STAND.md` mit tatsächlicher aktuellem Git-Commit und erneuten Save/Clock/Character-Tests vergleichen. Jede Erweiterung stellt sicher, dass alte Spielstände kompatibel behandelt werden. End-to-End-Tests für C14–C17 und Zeit-/Rebirth-Größen verbinden dynamische Missionen mit persistenter Welt. Visualtests in neutraler und dynamischer Beleuchtung werden von einem Menschen unterschrieben.

**Fehlerbewertung:** P0 = ScriptLock- oder Save-Korruption / Datenverlust; P1 = reproduzierbarer Gameplay-Softlock / Asset nicht ladbar; P2 = Render-/Deformation-/Leistungsfehler; P3 = kosmetisch. Fehler erzeugt Ticket mit Repro, AssetIDs, Screenshots/Logs und vermuteter Ursache ohne falsches Versprechen, dass Auto-Fix garantiert.

**QA-Fälle:** A1 keine „grün“-Meldung ohne Engine; A2 Testfehler sperrt ACCEPTED; A3 Source-/Lizenzkonflikt sperrt Merge; A4 reale Build-Logs vorhanden; A5 Neustart/Crash Save identisch; A6 Messwerte aus Insights, nicht halluziniert; A7 Kreativtest getrennt vom Unit-Test; A8 Releasecheckliste dokumentiert.

### Abhängigkeiten / nächste Umsetzung
Die automatisierten Tests im Paket sind reine Paketselbsttests, keine durchgeführten Spieltests. WorkIDs dürfen erst nach Architektur-/Kanonabgleich in reale Dateiedits umgesetzt werden.
