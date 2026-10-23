# V3-06 – Ultimate Life & Generations Simulation

**Status:** vom Game Director in diesem Gespräch mit JA bestätigt am 23.10.2026. Dies ist eine **Produktionsspezifikation**, kein Nachweis einer lokalen Implementierung.

**Kanon:** Weiterentwicklung des bestehenden `manuelbrandner85/Genesis-Games`, kein neues Spiel. C00–C21, J00–J24 und Ein-Welt-Regeln nicht ohne entsprechende Originalquellen/Freigaben verändern.

**Grundsatz:** Ergänzung zu V2, GENESIS-Missionen 3/12 und GAMEFORGE Living World 03/50; bereits bestehende Systemmodule/Agenten reuse statt kopieren.

## Ziel

Mehrgenerationen-Lebenssimulation mit weltzeitlich konsistenten Konsequenzen und freiwilligem Rebirth, ohne Epochenwahl.

## Abhängigkeiten / Kanon-Gates

1. Genehmigter GENESIS-Kanon 2026
2. Vorhandener SaveBundle Schema2
3. ScriptLock Storyquelle

## Konkrete Implementierungsarchitektur

1. Weltzeit läuft ab 2026 fort; biologischer Beginn nicht mit C00-Vorinkarnation verwechseln.
2. LifeID und körperliche Alterung trennen von persistenter SoulID; neuer Körper/Genom, begrenzte Erinnerungsresonanz, keine automatische Eigentumsübertragung.
3. Familie/Beziehungen/Erbe/Beruf/Wirtschaft/Ereignisse nur entlang bestätigter Systeme und personenspezifischer Zustände.
4. Tod: BodyDeathEvent → wiederaufnehmbarer Jenseitskontext → idempotenter atomarer Life/Soul/World-Commit → freiwillige Wahl Jenseits bleiben oder Wiedergeburt.
5. Langzeitfortschritt nutzt aggregierte Regeln mit nachvollziehbaren Veränderungen, nicht unmögliche Simulation jedes vergangene Frames.

## Lieferobjekte (Dateipfade als Vertrag, nicht bereits existent)

- `life/lifecycle_transition_table.csv`
- `life/rebirth_contract.md`
- `life/schema_migration_plan.md`
- `life/continuity_tests.json`

## Abnahme und reproduzierbare Tests

1. Erstes Spiel C00/Prolog-Bedingungen bleiben korrekt; erste spielbare Inkarnation beginnt in Gegenwart 2026.
2. Tod bei Geburt, frühem Erwachsenenalter, Alter: korrektes Jenseits und keine erfundene Biografie.
3. SoulID stabil und neue LifeID nach Rebirth; Weltzeit nie zum Ausgangs-2026 zurückgesetzt.
4. Crash, Save/Load und Mid-Commit-Retry ändern weder Ereignisanzahl noch Soul-/Life-Verknüpfung.

## Harte Negativregeln

- C15/C16, C17-Wortlaut und C21-Finale bleiben bei Konflikten blockiert statt umgeschrieben.
- Kein frei anwählbares Mittelalter/Zukunft, keine parallelen Epochenwelten.
- Kein automatisches Game-Over oder Karma-Strafsystem.

## Rollen und Übergabe

`genesis-life-soul-rebirth`, `genesis-unreal-core`, `genesis-script-guardian`, `genesis-qa-release`

### Protokollierungspflicht pro Arbeitspaket

`work_id, improvement_id, base_commit, canon_source_path, canon_sha256, agent_owner, files_changed, input_asset_hashes, outputs, license_proof, commands_run, engine_version, evidence_log, test_case_ids, outcome, reviewer, blockers`.

**Zustandsübergang:** `SPECIFIED → READY_FOR_IMPLEMENTATION → IMPLEMENTED_UNTESTED → VERIFIED_ENGINE → REVIEWED_HUMAN → ACCEPTED`. Bei fehlenden Quellen, Tools oder Freigaben ausdrücklich `BLOCKED`. Keine Abnahme durch Agenten-Selbsteinschätzung.

**Integrationsreihenfolge:** zuerst bestehende GENESIS-Komponenten und GAMEFORGE-Auftragsregister prüfen, dann kleinste funktionsfähige Implementierung auf getrenntem Git-Branch, Test, Review, erst danach nächster Auftrag. Kein eigenständiger Agentenserver.
