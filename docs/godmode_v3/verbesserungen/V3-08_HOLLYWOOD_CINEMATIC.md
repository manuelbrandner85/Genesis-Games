# V3-08 – Hollywood Cinematic Production

**Status:** vom Game Director in diesem Gespräch mit JA bestätigt am 23.10.2026. Dies ist eine **Produktionsspezifikation**, kein Nachweis einer lokalen Implementierung.

**Kanon:** Weiterentwicklung des bestehenden `manuelbrandner85/Genesis-Games`, kein neues Spiel. C00–C21, J00–J24 und Ein-Welt-Regeln nicht ohne entsprechende Originalquellen/Freigaben verändern.

**Grundsatz:** Ergänzung zu V2, GENESIS-Missionen 3/12 und GAMEFORGE Living World 03/50; bereits bestehende Systemmodule/Agenten reuse statt kopieren.

## Ziel

Filmreife Szenen mit synchroner Darstellung, echten Varianten und garantierter Story-Kontinuität.

## Abhängigkeiten / Kanon-Gates

1. Freigegebenes Originaldrehbuch
2. Szenen- und Cue-IDs
3. Finale Charakter-/Voice-Assets

## Konkrete Implementierungsarchitektur

1. Sequencer/ControlRig/CameraRig mit Versionierung je SceneID, ShotID, Timecode; differenzierbare Fixed/State-bound/Archive/World-derived-Modi.
2. AudioCueID, SpeakerID, SubtitleCueID, Locale, VoiceProfile, VariantID und FaceRig-Version bleiben gekoppelt.
3. C00-Master-Bild/Audio für C20-Replay unverändert referenzieren, nicht neu rendern oder nachsprechen.
4. Shot-Transitions, Kamera-Motion, Blickkontakt, Lippensynchronisation und Player-Choice-Resume getrennt testen.
5. Jede 3D-Erinnerungsrekonstruktion als solche kennzeichnen; ohne gespeicherte Bewegungsdaten nie Originalaufnahme vortäuschen.

## Lieferobjekte (Dateipfade als Vertrag, nicht bereits existent)

- `cinematics/scene_contracts.json`
- `cinematics/shotlist.csv`
- `cinematics/audio_cue_map.json`
- `cinematics/replay_hash_report.json`

## Abnahme und reproduzierbare Tests

1. C00 und C20 referenzieren exakt denselben geprüften Master-Asset-Hash.
2. Skip/Save/Load/Sprachwahl in jeder Phase keine kaputten Weltzustände.
3. Gesichts-/Mundbewegung wird gegen tatsächlich vorhandenes Sprach-Audio von Menschen geprüft.
4. C19/C20 Offenbarungszeitpunkte und C21 Originaloptionen bleiben unverändert.

## Harte Negativregeln

- Solange ScriptLock final ungeklärt: nur technische Mock-Sequenzen, keine Kanon-Renderproduktion.
- Keine erfundene deutsche Studioaufnahme oder Emotionsechtheit.
- Kein verstecktes Kürzen/Löschen von C00–C21.

## Rollen und Übergabe

`genesis-cinematic-director`, `genesis-face-voice-sync`, `genesis-audio-director`, `genesis-script-guardian`

### Protokollierungspflicht pro Arbeitspaket

`work_id, improvement_id, base_commit, canon_source_path, canon_sha256, agent_owner, files_changed, input_asset_hashes, outputs, license_proof, commands_run, engine_version, evidence_log, test_case_ids, outcome, reviewer, blockers`.

**Zustandsübergang:** `SPECIFIED → READY_FOR_IMPLEMENTATION → IMPLEMENTED_UNTESTED → VERIFIED_ENGINE → REVIEWED_HUMAN → ACCEPTED`. Bei fehlenden Quellen, Tools oder Freigaben ausdrücklich `BLOCKED`. Keine Abnahme durch Agenten-Selbsteinschätzung.

**Integrationsreihenfolge:** zuerst bestehende GENESIS-Komponenten und GAMEFORGE-Auftragsregister prüfen, dann kleinste funktionsfähige Implementierung auf getrenntem Git-Branch, Test, Review, erst danach nächster Auftrag. Kein eigenständiger Agentenserver.
