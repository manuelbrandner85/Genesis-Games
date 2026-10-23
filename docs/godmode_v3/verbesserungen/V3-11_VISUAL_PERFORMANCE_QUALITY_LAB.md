# V3-11 – AAA Visual & Performance Quality Lab

**Status:** vom Game Director in diesem Gespräch mit JA bestätigt am 23.10.2026. Dies ist eine **Produktionsspezifikation**, kein Nachweis einer lokalen Implementierung.

**Kanon:** Weiterentwicklung des bestehenden `manuelbrandner85/Genesis-Games`, kein neues Spiel. C00–C21, J00–J24 und Ein-Welt-Regeln nicht ohne entsprechende Originalquellen/Freigaben verändern.

**Grundsatz:** Ergänzung zu V2, GENESIS-Missionen 3/12 und GAMEFORGE Living World 03/50; bereits bestehende Systemmodule/Agenten reuse statt kopieren.

## Ziel

Visuelle Konsistenz, Stabilität und flüssige Darstellung als nachweisbare Eigenschaften, nicht als Marketingversprechen.

## Abhängigkeiten / Kanon-Gates

1. Definierte Zielhardware
2. Baseline-Build
3. Reproduzierbare Testkarte/Seeds

## Konkrete Implementierungsarchitektur

1. Golden Frames je Szene mit festem Zeitpunkt, Kamera, Wetter, Profil und UI, dazu Perceptual Review.
2. Unreal Insights, Stat-Profile, GPU-Profiler: CPU/GPU-Frametime, Speicher, Streaming, Sim-Tick, LOD/Animation.
3. Asset-Budgets nach Plattform für Nanite, Licht, Texturen, Materialkomplexität, Animationen, NPC-LOD und Shaderkompilierung.
4. Automatisierte Vergleiche erkennen technische Bildabweichungen; semantische Ästhetik erfordert menschliche Sichtabnahme.
5. Regression-Dashboard trennt echte Telemetrie von noch nicht gemessenen Zielen und bekannten Ausreißern.

## Lieferobjekte (Dateipfade als Vertrag, nicht bereits existent)

- `perf/hardware_profile.json`
- `perf/baseline_metrics.json`
- `perf/measurements/*.json`
- `perf/golden_frame_manifest.csv`
- `perf/regression_report.md`

## Abnahme und reproduzierbare Tests

1. Framezeiten/GPU-Speicher/CPU-Last auf konkreter Hardware messen, kein globaler FPS-Fixwert ohne Spezifikation.
2. World Partition: Bewegung/Teleport/QuickSave/Last unter Worst-Case-Dichte reproduzierbar.
3. Visuelle Falschfarben-/Shader-/Normalkarten-/Tonemapping-Anomalien auf 4 Tageszeiten.
4. Ungetestete Konfigurationen bleiben NOT_MEASURED.

## Harte Negativregeln

- Benchmarks aus Entwicklungs-PC nicht als alle Geräte gültig darstellen.
- Keine maschinelle Bildähnlichkeit mit künstlerischer Gleichwertigkeit verwechseln.
- Niemals Messwerte schätzen/erfinden.

## Rollen und Übergabe

`genesis-performance-specialist`, `genesis-pbr-specialist`, `genesis-qa-release`, `genesis-open-world`

### Protokollierungspflicht pro Arbeitspaket

`work_id, improvement_id, base_commit, canon_source_path, canon_sha256, agent_owner, files_changed, input_asset_hashes, outputs, license_proof, commands_run, engine_version, evidence_log, test_case_ids, outcome, reviewer, blockers`.

**Zustandsübergang:** `SPECIFIED → READY_FOR_IMPLEMENTATION → IMPLEMENTED_UNTESTED → VERIFIED_ENGINE → REVIEWED_HUMAN → ACCEPTED`. Bei fehlenden Quellen, Tools oder Freigaben ausdrücklich `BLOCKED`. Keine Abnahme durch Agenten-Selbsteinschätzung.

**Integrationsreihenfolge:** zuerst bestehende GENESIS-Komponenten und GAMEFORGE-Auftragsregister prüfen, dann kleinste funktionsfähige Implementierung auf getrenntem Git-Branch, Test, Review, erst danach nächster Auftrag. Kein eigenständiger Agentenserver.
