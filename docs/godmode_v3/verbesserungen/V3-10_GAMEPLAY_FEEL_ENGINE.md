# V3-10 – Perfect Gameplay Feel Engine

**Status:** vom Game Director in diesem Gespräch mit JA bestätigt am 23.10.2026. Dies ist eine **Produktionsspezifikation**, kein Nachweis einer lokalen Implementierung.

**Kanon:** Weiterentwicklung des bestehenden `manuelbrandner85/Genesis-Games`, kein neues Spiel. C00–C21, J00–J24 und Ein-Welt-Regeln nicht ohne entsprechende Originalquellen/Freigaben verändern.

**Grundsatz:** Ergänzung zu V2, GENESIS-Missionen 3/12 und GAMEFORGE Living World 03/50; bereits bestehende Systemmodule/Agenten reuse statt kopieren.

## Ziel

Reaktionsfreudige, lesbare und barrierearme Bedienung, die den Spieler nie mit unnötigen Steuerungsfehlern frustriert.

## Abhängigkeiten / Kanon-Gates

1. Vorhandenes Enhanced Input
2. Spielersteuerung und Kamera
3. Zielhardware/Controller

## Konkrete Implementierungsarchitektur

1. Input-Pipeline: Gerät → Mapping → Command → CharacterMotor → Camera → Gameplay Feedback, Latenz/Deadzone getrennt messen.
2. Kamera-Kollisionen, Schulterwechsel, Innenraum, über Kopf, enge Wege, Szenenübergänge, Fotomodus.
3. Action-Abbruchfenster, Puffer, Interaktionsfokus und visuelles/auditives Feedback als konfigurierte Daten, nicht hartkodierte Sonderfälle.
4. Spieleinstellungen für Untertitelgröße, Kontrast, Kameraempfindlichkeit, Headbob, Motion Blur und frei zuweisbare Tasten.
5. Automatisiertes Traversal und echte menschliche Spieltests in realen Szenen; Testgeräte Windows Tastatur/Maus/Controller.

## Lieferobjekte (Dateipfade als Vertrag, nicht bereits existent)

- `gameplay/feel_profile.json`
- `gameplay/camera_test_matrix.csv`
- `gameplay/playtest_sessions.csv`
- `gameplay/accessibility_audit.md`

## Abnahme und reproduzierbare Tests

1. Input-Konsistenz bei variablen FPS; Drehung und Geschwindigkeit nicht framerateabhängig.
2. Laufen/Rampe/Treppen/Türen/Indoor/Cinematic-Return aus echten Build-Tests.
3. Keine Pflicht-QTE in Verlust-/Sterbeszenen; Untertitel und vereinfachte Interaktion funktionieren.
4. Playtester können Hauptaktionen ohne Entwicklerhilfe erledigen.

## Harte Negativregeln

- Keine UX-Abnahme nur über Bot-Kommentar.
- Kein globaler Input-Refactor ohne Regressionstests.
- Kein ungefragtes Umschreiben von Menütönen/Story.

## Rollen und Übergabe

`genesis-unreal-core`, `genesis-motion-specialist`, `genesis-ui-accessibility`, `genesis-qa-release`

### Protokollierungspflicht pro Arbeitspaket

`work_id, improvement_id, base_commit, canon_source_path, canon_sha256, agent_owner, files_changed, input_asset_hashes, outputs, license_proof, commands_run, engine_version, evidence_log, test_case_ids, outcome, reviewer, blockers`.

**Zustandsübergang:** `SPECIFIED → READY_FOR_IMPLEMENTATION → IMPLEMENTED_UNTESTED → VERIFIED_ENGINE → REVIEWED_HUMAN → ACCEPTED`. Bei fehlenden Quellen, Tools oder Freigaben ausdrücklich `BLOCKED`. Keine Abnahme durch Agenten-Selbsteinschätzung.

**Integrationsreihenfolge:** zuerst bestehende GENESIS-Komponenten und GAMEFORGE-Auftragsregister prüfen, dann kleinste funktionsfähige Implementierung auf getrenntem Git-Branch, Test, Review, erst danach nächster Auftrag. Kein eigenständiger Agentenserver.
