# V3-07 – Next Generation Mission Director

**Status:** vom Game Director in diesem Gespräch mit JA bestätigt am 23.10.2026. Dies ist eine **Produktionsspezifikation**, kein Nachweis einer lokalen Implementierung.

**Kanon:** Weiterentwicklung des bestehenden `manuelbrandner85/Genesis-Games`, kein neues Spiel. C00–C21, J00–J24 und Ein-Welt-Regeln nicht ohne entsprechende Originalquellen/Freigaben verändern.

**Grundsatz:** Ergänzung zu V2, GENESIS-Missionen 3/12 und GAMEFORGE Living World 03/50; bereits bestehende Systemmodule/Agenten reuse statt kopieren.

## Ziel

Dynamische, kausal nachvollziehbare Missionen ohne generierte Plotwidersprüche oder Softlocks.

## Abhängigkeiten / Kanon-Gates

1. GENESIS-Verbesserung 3 (12 Anforderungen)
2. V61/V62 Missionsanker
3. Kausal-/Eventbus

## Konkrete Implementierungsarchitektur

1. Mission DataAssets mit QuestID, Weltbedingungen, Teilnehmer-IDs, verfügbarer Dialogvariante, Fristen, Eindeutigkeit und Exit-Regeln.
2. Questgraph muss klar getrennt sein von ScriptLock C00–C21; optionale Events dürfen keinen Kanon überschreiben.
3. Konsequenzen ausschließlich als gültige World-Events mit Idempotenzschlüssel und Snapshots; NPCs reagieren in ihrem Beziehungs- und Weltzustand.
4. Szenenstatus Eligible → BindingValidated → Ready → Playing → AwaitingInteraction? → CommitPending → Committed → HandedBack.
5. Ereignis Director nutzt Pool, Cooldowns, regionale Einschränkungen und realistische Alternative bei fehlenden Fakten.

## Lieferobjekte (Dateipfade als Vertrag, nicht bereits existent)

- `quests/quest_contract.schema.json`
- `quests/quest_dependency_graph.json`
- `quests/branch_coverage.csv`
- `quests/softlock_report.json`

## Abnahme und reproduzierbare Tests

1. Sämtliche Missionszweige in automatischen Graph-Tests begehbar; keine doppelte Auszahlung.
2. Dialog über Beziehung nur wenn Beziehung im Save nachweisbar.
3. Mission abbrechen, Spiel speichern, neu laden, Ort verlassen, Teilnehmer weg: definierter Zustand.
4. ScriptLock-Szenen nie stillschweigend ändern, Skip committen, Spoiler vor C19 sperren.

## Harte Negativregeln

- Quests ohne Originalmissionstexte sind DESIGN_ONLY.
- Keine automatische Kanonerweiterung durch generatives NPC-System.
- Keine Autoentscheidung in geschützten interaktiven Szenen.

## Rollen und Übergabe

`genesis-mission-events`, `genesis-script-guardian`, `genesis-npc-intelligence`, `genesis-qa-release`

### Protokollierungspflicht pro Arbeitspaket

`work_id, improvement_id, base_commit, canon_source_path, canon_sha256, agent_owner, files_changed, input_asset_hashes, outputs, license_proof, commands_run, engine_version, evidence_log, test_case_ids, outcome, reviewer, blockers`.

**Zustandsübergang:** `SPECIFIED → READY_FOR_IMPLEMENTATION → IMPLEMENTED_UNTESTED → VERIFIED_ENGINE → REVIEWED_HUMAN → ACCEPTED`. Bei fehlenden Quellen, Tools oder Freigaben ausdrücklich `BLOCKED`. Keine Abnahme durch Agenten-Selbsteinschätzung.

**Integrationsreihenfolge:** zuerst bestehende GENESIS-Komponenten und GAMEFORGE-Auftragsregister prüfen, dann kleinste funktionsfähige Implementierung auf getrenntem Git-Branch, Test, Review, erst danach nächster Auftrag. Kein eigenständiger Agentenserver.
