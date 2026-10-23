# V3-12 – Autonomous Build & Playtest Factory

**Status:** vom Game Director in diesem Gespräch mit JA bestätigt am 23.10.2026. Dies ist eine **Produktionsspezifikation**, kein Nachweis einer lokalen Implementierung.

**Kanon:** Weiterentwicklung des bestehenden `manuelbrandner85/Genesis-Games`, kein neues Spiel. C00–C21, J00–J24 und Ein-Welt-Regeln nicht ohne entsprechende Originalquellen/Freigaben verändern.

**Grundsatz:** Ergänzung zu V2, GENESIS-Missionen 3/12 und GAMEFORGE Living World 03/50; bereits bestehende Systemmodule/Agenten reuse statt kopieren.

## Ziel

Kontinuierlich nachvollziehbare, spielbare Builds und Szenariotests mit klarer Fehlertriage und reproduzierbarer Beweisführung.

## Abhängigkeiten / Kanon-Gates

1. UE-Installation und SDK
2. Projekt buildbar
3. Repro-Szenario und Lizenzbestand

## Konkrete Implementierungsarchitektur

1. Build-Pipeline mit gesonderten Stufen C++ Compile → Asset/Cook Validation → Windows Package → Smoke → PIE/Standalone → Functional Tests → Profiling.
2. Testdaten aus Story/World-/Quest-/Life-Save-Fällen generieren (ohne Kanon umzuschreiben), Seeds stabil halten.
3. Test-Launcher akzeptiert nur explizite lokale Pfade und --execute; niemals Tool-Erfolg ohne Returncode, Filesize und Logs.
4. Bug-Triage: Repro-Schritte, BaseCommit, Priorität, verantwortlicher Agent, Screenshots, Stacktrace, Maßnahmen, erneuter Test.
5. Release Gate benötigt Rechtsbelege, Storyfreigaben, echte menschliche Spieltests und explizite Owner-Freigabe.

## Lieferobjekte (Dateipfade als Vertrag, nicht bereits existent)

- `builds/build_manifest.json`
- `builds/logs/*`
- `qa/test_evidence.json`
- `qa/defect_registry.csv`
- `qa/acceptance_report.md`

## Abnahme und reproduzierbare Tests

1. Build/Package erzeugt überprüfbares Artefakt statt bloßes Konsolenversprechen.
2. Crash/Save/Load/Teleport/Story-Regression auf eigenem Testsave und dokumentiertem Seed.
3. Negative Testfälle führen zu FAILED/BLOCKED, kein Fortschritt durch Statusmanipulation.
4. Goldstandard-Slice wird von mindestens einem menschlichen Test überprüft.

## Harte Negativregeln

- Kein Packaging auf nicht vorhandener Maschine behaupten.
- Ohne Story-/Assetfreigabe maximal Prototyp, nie Release.
- Kein automatische Push/Release/Installerveröffentlichung.

## Rollen und Übergabe

`genesis-qa-release`, `genesis-master-director`, `genesis-production-planner`, `genesis-tool-integration`

### Protokollierungspflicht pro Arbeitspaket

`work_id, improvement_id, base_commit, canon_source_path, canon_sha256, agent_owner, files_changed, input_asset_hashes, outputs, license_proof, commands_run, engine_version, evidence_log, test_case_ids, outcome, reviewer, blockers`.

**Zustandsübergang:** `SPECIFIED → READY_FOR_IMPLEMENTATION → IMPLEMENTED_UNTESTED → VERIFIED_ENGINE → REVIEWED_HUMAN → ACCEPTED`. Bei fehlenden Quellen, Tools oder Freigaben ausdrücklich `BLOCKED`. Keine Abnahme durch Agenten-Selbsteinschätzung.

**Integrationsreihenfolge:** zuerst bestehende GENESIS-Komponenten und GAMEFORGE-Auftragsregister prüfen, dann kleinste funktionsfähige Implementierung auf getrenntem Git-Branch, Test, Review, erst danach nächster Auftrag. Kein eigenständiger Agentenserver.
