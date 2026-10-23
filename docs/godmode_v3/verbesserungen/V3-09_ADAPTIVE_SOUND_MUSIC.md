# V3-09 – Ultimate Adaptive Sound & Music

**Status:** vom Game Director in diesem Gespräch mit JA bestätigt am 23.10.2026. Dies ist eine **Produktionsspezifikation**, kein Nachweis einer lokalen Implementierung.

**Kanon:** Weiterentwicklung des bestehenden `manuelbrandner85/Genesis-Games`, kein neues Spiel. C00–C21, J00–J24 und Ein-Welt-Regeln nicht ohne entsprechende Originalquellen/Freigaben verändern.

**Grundsatz:** Ergänzung zu V2, GENESIS-Missionen 3/12 und GAMEFORGE Living World 03/50; bereits bestehende Systemmodule/Agenten reuse statt kopieren.

## Ziel

Räumlicher, dynamischer Sound und unterscheidbare Musikthemen mit lückenlos dokumentierten Nutzungsrechten.

## Abhängigkeiten / Kanon-Gates

1. Story-Cue-Sheet
2. Freigegebene Rechte/Sprecher
3. MetaSound/Audio-API im Projekt

## Konkrete Implementierungsarchitektur

1. Sound-Event-System koppelt WorldTime, Wetter, Material-Footsteps, Verkehr, NPC-Dialog und Missionen.
2. Musikzustände modulieren Lebensphasen, Spannung, Jenseits und Schlüsselszenen; Soul-Motiv strikt getrennt vom persönlichen Familienmotiv.
3. Foley/Umgebung in professionell normalisierten Ebenen; Innen/Außen, Occlusion, Entfernung, Wettereinfluss.
4. Deutsche Dialoge mit kontrollierter Sprecheridentität, Untertiteln, tatsächlichen Wav/Viseme-/Face-Rig-Tracks, Audio-Lokalisation.
5. Rechteregister je Sound/Musik/Stimme und kommerzieller Verwendbarkeit; kostenlose Werkzeuge bevorzugen, keine ungefragten Abo-KI-Calls.

## Lieferobjekte (Dateipfade als Vertrag, nicht bereits existent)

- `audio/audio_event_registry.csv`
- `audio/music_state_machine.md`
- `audio/voice_production_sheet.csv`
- `audio/right_evidence_register.csv`
- `audio/perceptual_review.md`

## Abnahme und reproduzierbare Tests

1. Dialogpausen/Choice/Resume halten Audio, Untertitel, Gesicht synchron.
2. Musik-Ducking unter Dialog, ohne knallende Lautstärkesprünge.
3. Hören mit Kopfhörer/Stereo, Lautstärkeoptionen, Sound aus/an, Sprachwechsel.
4. Lizenzbelege pro finalem Audioasset; fehlender Nachweis blockiert Release.

## Harte Negativregeln

- Kein als final deklariertes synthetisches Audio ohne Lizenz-/Qualitätsprüfung.
- Kein unzulässiges Imitieren echter Sprecher ohne Einwilligung.
- C00-Replay-Audio darf nicht geändert werden.

## Rollen und Übergabe

`genesis-audio-director`, `genesis-face-voice-sync`, `genesis-asset-licensing`, `genesis-qa-release`

### Protokollierungspflicht pro Arbeitspaket

`work_id, improvement_id, base_commit, canon_source_path, canon_sha256, agent_owner, files_changed, input_asset_hashes, outputs, license_proof, commands_run, engine_version, evidence_log, test_case_ids, outcome, reviewer, blockers`.

**Zustandsübergang:** `SPECIFIED → READY_FOR_IMPLEMENTATION → IMPLEMENTED_UNTESTED → VERIFIED_ENGINE → REVIEWED_HUMAN → ACCEPTED`. Bei fehlenden Quellen, Tools oder Freigaben ausdrücklich `BLOCKED`. Keine Abnahme durch Agenten-Selbsteinschätzung.

**Integrationsreihenfolge:** zuerst bestehende GENESIS-Komponenten und GAMEFORGE-Auftragsregister prüfen, dann kleinste funktionsfähige Implementierung auf getrenntem Git-Branch, Test, Review, erst danach nächster Auftrag. Kein eigenständiger Agentenserver.
