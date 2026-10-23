# V3-05 – True Living NPC Intelligence 5.0

**Status:** vom Game Director in diesem Gespräch mit JA bestätigt am 23.10.2026. Dies ist eine **Produktionsspezifikation**, kein Nachweis einer lokalen Implementierung.

**Kanon:** Weiterentwicklung des bestehenden `manuelbrandner85/Genesis-Games`, kein neues Spiel. C00–C21, J00–J24 und Ein-Welt-Regeln nicht ohne entsprechende Originalquellen/Freigaben verändern.

**Grundsatz:** Ergänzung zu V2, GENESIS-Missionen 3/12 und GAMEFORGE Living World 03/50; bereits bestehende Systemmodule/Agenten reuse statt kopieren.

## Ziel

Individuelle, soziale und zeitlich plausible NPCs ohne kostenintensive permanente Cloud-KI.

## Abhängigkeiten / Kanon-Gates

1. GAMEFORGE Living World 01–50
2. Existierende WorldClock/SaveSubsystem
3. Causal-Graph/Story-Kontrakte

## Konkrete Implementierungsarchitektur

1. Stabile EntityIDs, Tagesplan, Bedürfnisse und persönliche Ziele in StateTree/SmartObjects; Emotion/Erinnerung ausschließlich aus gespeicherten Ereignissen.
2. Near/Mid/Far-LODs: nahe NPCs animiert, mittlere vereinfacht, entfernte aggregiert; Übergänge bewahren Identität/Beziehungen.
3. Verweigerungen, Zustimmung, Arbeitszeiten, Familienbeziehungen und Alterung nach überprüfbaren Regeln.
4. Event-Bus verbindet NPC, Quests, Wirtschaft, Wetter und Save, aber verhindert doppelte Belohnungen/Events.
5. Gespräche aus lokalisierten, kanonverträglichen Varianten; generative TTS/LLM nicht zur Laufzeit voraussetzen.

## Lieferobjekte (Dateipfade als Vertrag, nicht bereits existent)

- `npc/npc_profile.schema.json`
- `npc/daily_schedule_matrix.csv`
- `npc/memory_event_contract.json`
- `npc/long_run_test_report.json`

## Abnahme und reproduzierbare Tests

1. Mehrere NPCs mit konkurrierender Smart-Object-Belegung und Fallback.
2. Spieler hilft/ignoriert jemanden, NPC erinnert sich nach Reload und nach Tagen.
3. Zeitvorlauf 1/10/100 In-Game-Tage ohne exponentielles Wachstum.
4. Laden und Streamen dupliziert keinen NPC und macht niemanden gleichzeitig an zwei Orten.

## Harte Negativregeln

- NPCs dürfen keine Erinnerungen an nie stattgefundene Ereignisse erfinden.
- Keine permanente Online-Inferenz pro NPC.
- Keine Änderung der Story-C00–C21.

## Rollen und Übergabe

`genesis-npc-intelligence`, `genesis-life-soul-rebirth`, `genesis-society-economy`, `genesis-performance-specialist`

### Protokollierungspflicht pro Arbeitspaket

`work_id, improvement_id, base_commit, canon_source_path, canon_sha256, agent_owner, files_changed, input_asset_hashes, outputs, license_proof, commands_run, engine_version, evidence_log, test_case_ids, outcome, reviewer, blockers`.

**Zustandsübergang:** `SPECIFIED → READY_FOR_IMPLEMENTATION → IMPLEMENTED_UNTESTED → VERIFIED_ENGINE → REVIEWED_HUMAN → ACCEPTED`. Bei fehlenden Quellen, Tools oder Freigaben ausdrücklich `BLOCKED`. Keine Abnahme durch Agenten-Selbsteinschätzung.

**Integrationsreihenfolge:** zuerst bestehende GENESIS-Komponenten und GAMEFORGE-Auftragsregister prüfen, dann kleinste funktionsfähige Implementierung auf getrenntem Git-Branch, Test, Review, erst danach nächster Auftrag. Kein eigenständiger Agentenserver.
