# V3-02 – Human Motion & Interaction 5.0

**Status:** vom Game Director in diesem Gespräch mit JA bestätigt am 23.10.2026. Dies ist eine **Produktionsspezifikation**, kein Nachweis einer lokalen Implementierung.

**Kanon:** Weiterentwicklung des bestehenden `manuelbrandner85/Genesis-Games`, kein neues Spiel. C00–C21, J00–J24 und Ein-Welt-Regeln nicht ohne entsprechende Originalquellen/Freigaben verändern.

**Grundsatz:** Ergänzung zu V2, GENESIS-Missionen 3/12 und GAMEFORGE Living World 03/50; bereits bestehende Systemmodule/Agenten reuse statt kopieren.

## Ziel

Kontinuierliche natürliche Bewegung und taktile Interaktion, ohne Fußgleiten, Handdurchdringung oder Kamera-Aussetzer.

## Abhängigkeiten / Kanon-Gates

1. Kompatibles Skelett
2. AnimBP-Integrationsvertrag
3. Freigegebener CharacterAssetId

## Konkrete Implementierungsarchitektur

1. Locomotion-Zustände mit synchronisierten Transitionen, Start/Stop/Pivot, Geschwindigkeits- und Beschleunigungsprofilen; Motion Matching/Chooser nur nach Plugin- und Datensatzprüfung.
2. IK für Fußstellung und Hände, Motion Warping für präzise Interaktionsanfänge, Smart-Object-Anker zum Sitzen und Arbeiten.
3. Separat getestete Altersprofile für Infant/Kleinkind/Kind/Jugend/Erwachsen/Greis und Barrierefreiheitsvarianten; Motorik an Lifecycle gekoppelt.
4. Interaktionsvertrag definiert Owner, Start/Ende, Abbruch, Transform, Animation ID, Kollision und Cancel-Recovery.
5. Inputlatenz und Kameraverhalten bei 30/60/120 FPS prüfen; Framerate darf Bewegungsablauf nicht verändern.

## Lieferobjekte (Dateipfade als Vertrag, nicht bereits existent)

- `anim/motion_profile.json`
- `AnimBP/IK-Retarget/Interaction-Daten`
- `test_sequences/motion_matrix.md`
- `Evidence Videos mit echter In-Engine-Aufnahme`

## Abnahme und reproduzierbare Tests

1. Stehen/Gehen/Laufen/Sprint/Stop/Pivot/Sprung/Treppe/Steigung/Unebenheit je Input-Gerät.
2. Stuhl-/Tür-/Gegenstandsszenen ohne offensichtliche Penetration; Testcamera inklusive.
3. Controller und Tastatur/Maus manuell durch Tester; automatische Eingabe ergänzt, ersetzt nicht.
4. Save/Load während Interaktion führt zu definiertem Recovery und nicht zu dauerhaft gesperrter Aufgabe.

## Harte Negativregeln

- Nur Renderanimation ohne Gameplayintegration ist nicht abgenommen.
- Keine ungeprüfte Motion-Matching-Einführung mit großem Daten-/GPU-Budget.
- Keine erwachsene Standardbewegung für Säuglinge.

## Rollen und Übergabe

`genesis-motion-specialist`, `genesis-rigging-specialist`, `genesis-unreal-core`, `genesis-qa-release`

### Protokollierungspflicht pro Arbeitspaket

`work_id, improvement_id, base_commit, canon_source_path, canon_sha256, agent_owner, files_changed, input_asset_hashes, outputs, license_proof, commands_run, engine_version, evidence_log, test_case_ids, outcome, reviewer, blockers`.

**Zustandsübergang:** `SPECIFIED → READY_FOR_IMPLEMENTATION → IMPLEMENTED_UNTESTED → VERIFIED_ENGINE → REVIEWED_HUMAN → ACCEPTED`. Bei fehlenden Quellen, Tools oder Freigaben ausdrücklich `BLOCKED`. Keine Abnahme durch Agenten-Selbsteinschätzung.

**Integrationsreihenfolge:** zuerst bestehende GENESIS-Komponenten und GAMEFORGE-Auftragsregister prüfen, dann kleinste funktionsfähige Implementierung auf getrenntem Git-Branch, Test, Review, erst danach nächster Auftrag. Kein eigenständiger Agentenserver.
