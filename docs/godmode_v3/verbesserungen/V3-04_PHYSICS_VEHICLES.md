# V3-04 – Ultimate Physics & Vehicle Simulation

**Status:** vom Game Director in diesem Gespräch mit JA bestätigt am 23.10.2026. Dies ist eine **Produktionsspezifikation**, kein Nachweis einer lokalen Implementierung.

**Kanon:** Weiterentwicklung des bestehenden `manuelbrandner85/Genesis-Games`, kein neues Spiel. C00–C21, J00–J24 und Ein-Welt-Regeln nicht ohne entsprechende Originalquellen/Freigaben verändern.

**Grundsatz:** Ergänzung zu V2, GENESIS-Missionen 3/12 und GAMEFORGE Living World 03/50; bereits bestehende Systemmodule/Agenten reuse statt kopieren.

## Ziel

Plausible, kontrollierbare Fahrzeuge und Interaktionsphysik, die spielerisch verständlich bleibt und stabil gespeichert wird.

## Abhängigkeiten / Kanon-Gates

1. Freigegebener Fahrzeug-/Objektscope
2. Chaos-Version und Zielhardware
3. Kontroll- und Inputschemata

## Konkrete Implementierungsarchitektur

1. Chaos-Presets mit Massen, Trägheit, Reibung, Federung, Fahrbahn-Wetterkontakt und deterministischen Replay-Tests wo möglich.
2. Separates Gameplay-Modell für Ein-/Aussteigen, Türen, Gepäck, Sitze, Kamera, Kollision und Verkehrs-KI.
3. Pro Fahrzeug verifizierte Proportionen aus Referenz/Bauartdaten; kein Universalpreset für PKW/LKW/Fahrrad.
4. Physik-Substepping/Time-Step-Abgleich; Unfälle oder Straßensperren nur in genehmigter Quest-/Weltlogik.
5. Saving/Rollback: Location, Besitzer, Schäden (falls freigegeben), Tank/Ladung soweit vorgesehen.

## Lieferobjekte (Dateipfade als Vertrag, nicht bereits existent)

- `vehicles/vehicle_profile.schema.json`
- `physics_scenarios.csv`
- `drive_capture_log.json`
- `collision_reports/*.json`

## Abnahme und reproduzierbare Tests

1. Anfahren/Bremsen/Kurven bei trockener und nasser Straße auf Referenzstrecke.
2. Physik bei unterschiedlichen FPS und Pause/Resume; kein Teleport-/Kollisions-Exploit.
3. Ein-/Aussteigen, Türen, NPC-Wegfindung und Parken nach Save/Load.
4. Hardwaretest mit Fahrzeug plus NPC-Verkehr und dokumentierter CPU-/GPU-Last.

## Harte Negativregeln

- Keine Behauptung industriegenauer Fahrzeugphysik ohne Messdaten.
- Kein eigenmächtiges Kampfsystem aus Fahrzeugmechanik ableiten.
- Kein Quell-Asset ohne kommerziell kompatible Lizenz.

## Rollen und Übergabe

`genesis-vehicles-travel`, `genesis-unreal-core`, `genesis-qa-release`

### Protokollierungspflicht pro Arbeitspaket

`work_id, improvement_id, base_commit, canon_source_path, canon_sha256, agent_owner, files_changed, input_asset_hashes, outputs, license_proof, commands_run, engine_version, evidence_log, test_case_ids, outcome, reviewer, blockers`.

**Zustandsübergang:** `SPECIFIED → READY_FOR_IMPLEMENTATION → IMPLEMENTED_UNTESTED → VERIFIED_ENGINE → REVIEWED_HUMAN → ACCEPTED`. Bei fehlenden Quellen, Tools oder Freigaben ausdrücklich `BLOCKED`. Keine Abnahme durch Agenten-Selbsteinschätzung.

**Integrationsreihenfolge:** zuerst bestehende GENESIS-Komponenten und GAMEFORGE-Auftragsregister prüfen, dann kleinste funktionsfähige Implementierung auf getrenntem Git-Branch, Test, Review, erst danach nächster Auftrag. Kein eigenständiger Agentenserver.
