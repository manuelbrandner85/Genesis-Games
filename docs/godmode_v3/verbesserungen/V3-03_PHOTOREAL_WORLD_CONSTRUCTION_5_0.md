# V3-03 – Photorealistic World Construction 5.0

**Status:** vom Game Director in diesem Gespräch mit JA bestätigt am 23.10.2026. Dies ist eine **Produktionsspezifikation**, kein Nachweis einer lokalen Implementierung.

**Kanon:** Weiterentwicklung des bestehenden `manuelbrandner85/Genesis-Games`, kein neues Spiel. C00–C21, J00–J24 und Ein-Welt-Regeln nicht ohne entsprechende Originalquellen/Freigaben verändern.

**Grundsatz:** Ergänzung zu V2, GENESIS-Missionen 3/12 und GAMEFORGE Living World 03/50; bereits bestehende Systemmodule/Agenten reuse statt kopieren.

## Ziel

Maßhaltige, interaktive, kohärente Open-World-Umgebungen mit glaubwürdigem Tageslicht, Wetter und Innenräumen.

## Abhängigkeiten / Kanon-Gates

1. Bestätigte Karten-/Regionsdaten
2. Legal Asset-Vault
3. Weltzeit- und Save-Schnittstelle

## Konkrete Implementierungsarchitektur

1. Level-Layout auf genehmigten Regionen/Wegen/Sichtachsen statt erfundener GENESIS-Geschichte.
2. Modulare Bausätze mit metrischen Einheiten, Texeldichte, Pivotkonvention, Kollision, LOD/HLOD und Nanite-Eignungsprüfung.
3. World Partition und Data Layers für Streaming; persistente Weltzustände von ausgeladenen Actors trennen.
4. PBR mit lizenzierten Texturen, sinnvollen Roughness-/Normalwerten, korrekt skalierten Materialien, Lumen/Virtual Shadow Maps nach Zielprofil.
5. Innen/Außen-Beleuchtung, Regen/Nässe, Jahreszeiten, Distanz/Nebel, Lesbarkeit und Zugänglichkeit koordinieren; PCG nur für regenerierbare dekorative Inhalte.

## Lieferobjekte (Dateipfade als Vertrag, nicht bereits existent)

- `world/region_blueprint.json`
- `world/modular_asset_register.csv`
- `lighting/profile_matrix.md`
- `map_gates/region_acceptance.json`
- `Standalone-/PIE-Screenshots + Insights-Messungen`

## Abnahme und reproduzierbare Tests

1. Begehbarkeit jedes vorgesehenen Eingangs, NavMesh, Interaktionshöhe, Innen/Außen-Licht und Kollision.
2. Revisit nach World-Partition-Unload: gleiche relevante Objekte und NPC-IDs.
3. Vier Tageszeiten, Wetterlagen, Detailstufen und auf genehmigter Zielhardware gemessene Framezeiten.
4. Keine unberechtigten Bibliotheks-/Gebäudeelemente für gesperrte Storybereiche.

## Harte Negativregeln

- Keine frei erfundenen neuen Kanonorte.
- Fotos reichen nicht als Performance- oder Navigationsbeleg.
- Keine rechteunklare Mesh-/Texturdownloads.

## Rollen und Übergabe

`genesis-environment-artist`, `genesis-open-world`, `genesis-pbr-specialist`, `genesis-performance-specialist`

### Protokollierungspflicht pro Arbeitspaket

`work_id, improvement_id, base_commit, canon_source_path, canon_sha256, agent_owner, files_changed, input_asset_hashes, outputs, license_proof, commands_run, engine_version, evidence_log, test_case_ids, outcome, reviewer, blockers`.

**Zustandsübergang:** `SPECIFIED → READY_FOR_IMPLEMENTATION → IMPLEMENTED_UNTESTED → VERIFIED_ENGINE → REVIEWED_HUMAN → ACCEPTED`. Bei fehlenden Quellen, Tools oder Freigaben ausdrücklich `BLOCKED`. Keine Abnahme durch Agenten-Selbsteinschätzung.

**Integrationsreihenfolge:** zuerst bestehende GENESIS-Komponenten und GAMEFORGE-Auftragsregister prüfen, dann kleinste funktionsfähige Implementierung auf getrenntem Git-Branch, Test, Review, erst danach nächster Auftrag. Kein eigenständiger Agentenserver.
