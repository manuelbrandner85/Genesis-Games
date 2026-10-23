# GENESIS – Alle zwölf bestätigten GODMODE-3.0-Verbesserungen

Dies ist ein konsolidiertes technisches Dokument. Die Einzeldokumente in `docs/godmode_v3/verbesserungen/` sind die pflegbaren Masterdateien. Dieses Dokument ist **keine Implementation**.


---

# V3-01 – Ultimate Digital Human GODMODE 6.0

**Status:** vom Game Director in diesem Gespräch mit JA bestätigt am 23.10.2026. Dies ist eine **Produktionsspezifikation**, kein Nachweis einer lokalen Implementierung.

**Kanon:** Weiterentwicklung des bestehenden `manuelbrandner85/Genesis-Games`, kein neues Spiel. C00–C21, J00–J24 und Ein-Welt-Regeln nicht ohne entsprechende Originalquellen/Freigaben verändern.

**Grundsatz:** Ergänzung zu V2, GENESIS-Missionen 3/12 und GAMEFORGE Living World 03/50; bereits bestehende Systemmodule/Agenten reuse statt kopieren.

## Ziel

Identitätsstabile, realistisch detaillierte Menschen vom Kleinkind bis zum älteren Menschen; nicht nur schöne Standbilder, sondern riggbare und gameplayfähige Figuren.

## Abhängigkeiten / Kanon-Gates

1. Story-/Character-Asset-ID
2. Freigegebene Figurenvorlage
3. Proportionsvertrag der vorhandenen Registry

## Konkrete Implementierungsarchitektur

1. Charakter-DNA versioniert: AssetID, LifeID, Körperprofil, Körpermaßstab, Kopf-/Augen-/Hand-Anker, Kleidung, Altersprofil und Referenzhashes. Kein kanonischer Figurenentwurf ohne verifizierte Storyquelle.
2. Referenzsatz: Vorderseite, Seite, Rückseite, 3/4, Gesichts-Closeups, Hände, Outfit, Farb-/Materialcharts. Einzelbild-KI darf Form nicht allein definieren.
3. Blender: Blockout → anatomische Kontrolle → Sculpt → Retopologie → UV → PBR → Haare/Kleidung → Skinning → Rig → LOD; Zwischenstände erhalten.
4. Unreal: Austausch über UGenesisCharacterAppearance/Registry statt Änderung des Gameplaycodes; PhysicsAsset, MorphTargets, AnimationBP, Materialien und LOD validieren.
5. Unterschiede nach Lebensalter nur über zulässige Erscheinungs-/Animationsprofile; keine automatische 1:1 Skalierung von Erwachsenen auf Säuglinge.

## Lieferobjekte (Dateipfade als Vertrag, nicht bereits existent)

- `characters/<AssetID>/reference_manifest.json`
- `characters/<AssetID>/master.blend`
- `characters/<AssetID>/export.fbx`
- `characters/<AssetID>/measurements.json`
- `characters/<AssetID>/turnaround/*.png`
- `UE-Asset-Registry- und PIE-Nachweise`

## Abnahme und reproduzierbare Tests

1. Maße/Pivot/Skeleton/Anker mit freigegebenem Charaktervertrag vergleichen; numerische Abweichungen protokollieren.
2. Vorder-/Seiten-/Rückansicht human-review gegen identische Referenz-ID und Objektversion.
3. Unreal-Proportionen, Kapsel, Fußhöhe, AnimBP-Skeleton, LOD, Gewichte und Knochenhierarchie testen.
4. Gesichtsausdrücke/Änderungen von Outfit oder Alter dürfen CharacterAssetId-Identität nicht unbemerkt ersetzen.

## Harte Negativregeln

- Ohne freigegebene Referenzen nur PROTOTYPE, niemals HERO_APPROVED.
- Keine rechtlich ungeklärten Gesichts-/Stimmenkopien realer Personen.
- Kein automatisch behaupteter 1:1-Bild-zu-3D-Transfer: künstlerische Revision nötig.

## Rollen und Übergabe

`genesis-character-artist`, `genesis-reference-director`, `genesis-rigging-specialist`, `genesis-pbr-specialist`, `genesis-qa-release`

### Protokollierungspflicht pro Arbeitspaket

`work_id, improvement_id, base_commit, canon_source_path, canon_sha256, agent_owner, files_changed, input_asset_hashes, outputs, license_proof, commands_run, engine_version, evidence_log, test_case_ids, outcome, reviewer, blockers`.

**Zustandsübergang:** `SPECIFIED → READY_FOR_IMPLEMENTATION → IMPLEMENTED_UNTESTED → VERIFIED_ENGINE → REVIEWED_HUMAN → ACCEPTED`. Bei fehlenden Quellen, Tools oder Freigaben ausdrücklich `BLOCKED`. Keine Abnahme durch Agenten-Selbsteinschätzung.

**Integrationsreihenfolge:** zuerst bestehende GENESIS-Komponenten und GAMEFORGE-Auftragsregister prüfen, dann kleinste funktionsfähige Implementierung auf getrenntem Git-Branch, Test, Review, erst danach nächster Auftrag. Kein eigenständiger Agentenserver.


---

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


---

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


---

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


---

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


---

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


---

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


---

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


---

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


---

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


---

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


---

# V3-12 – Autonomous Build & Playtest Factory

**Status:** vom Game Director in diesem Gespräch mit JA bestätigt am 23.10.2026. Dies ist eine **Produktionsspezifikation**, kein Nachweis einer lokalen Implementierung.

**Kanon:** Weiterentwicklung des bestehenden `manuelbrandner85/Genesis-Games`, kein neues Spiel. C00–C21, J00–J24 und Ein-Welt-Regeln nicht ohne entsprechende Originalquellen/Freigaben verändern.

**Grundsatz:** Ergänzung zu V2, GENESIS-Missionen 3/12 und GAMEFORGE Living World 03/50; bereits bestehende Systemmodule/Agenten reuse statt kopieren.

## Ziel

Kontinuierlich nachvollziehbare, spielbare Builds und Szenariotests mit klarer Fehlertriage und reproduzierbarer Beweisführung.

## Abhängigkeiten / Kanon-Gates

1. UE-Installation und SDK
2. Projekt buildbar
3. Repro-Szenario und Lizenzbestand

## Konkrete Implementierungsarchitektur

1. Build-Pipeline mit gesonderten Stufen C++ Compile → Asset/Cook Validation → Windows Package → Smoke → PIE/Standalone → Functional Tests → Profiling.
2. Testdaten aus Story/World-/Quest-/Life-Save-Fällen generieren (ohne Kanon umzuschreiben), Seeds stabil halten.
3. Test-Launcher akzeptiert nur explizite lokale Pfade und --execute; niemals Tool-Erfolg ohne Returncode, Filesize und Logs.
4. Bug-Triage: Repro-Schritte, BaseCommit, Priorität, verantwortlicher Agent, Screenshots, Stacktrace, Maßnahmen, erneuter Test.
5. Release Gate benötigt Rechtsbelege, Storyfreigaben, echte menschliche Spieltests und explizite Owner-Freigabe.

## Lieferobjekte (Dateipfade als Vertrag, nicht bereits existent)

- `builds/build_manifest.json`
- `builds/logs/*`
- `qa/test_evidence.json`
- `qa/defect_registry.csv`
- `qa/acceptance_report.md`

## Abnahme und reproduzierbare Tests

1. Build/Package erzeugt überprüfbares Artefakt statt bloßes Konsolenversprechen.
2. Crash/Save/Load/Teleport/Story-Regression auf eigenem Testsave und dokumentiertem Seed.
3. Negative Testfälle führen zu FAILED/BLOCKED, kein Fortschritt durch Statusmanipulation.
4. Goldstandard-Slice wird von mindestens einem menschlichen Test überprüft.

## Harte Negativregeln

- Kein Packaging auf nicht vorhandener Maschine behaupten.
- Ohne Story-/Assetfreigabe maximal Prototyp, nie Release.
- Kein automatische Push/Release/Installerveröffentlichung.

## Rollen und Übergabe

`genesis-qa-release`, `genesis-master-director`, `genesis-production-planner`, `genesis-tool-integration`

### Protokollierungspflicht pro Arbeitspaket

`work_id, improvement_id, base_commit, canon_source_path, canon_sha256, agent_owner, files_changed, input_asset_hashes, outputs, license_proof, commands_run, engine_version, evidence_log, test_case_ids, outcome, reviewer, blockers`.

**Zustandsübergang:** `SPECIFIED → READY_FOR_IMPLEMENTATION → IMPLEMENTED_UNTESTED → VERIFIED_ENGINE → REVIEWED_HUMAN → ACCEPTED`. Bei fehlenden Quellen, Tools oder Freigaben ausdrücklich `BLOCKED`. Keine Abnahme durch Agenten-Selbsteinschätzung.

**Integrationsreihenfolge:** zuerst bestehende GENESIS-Komponenten und GAMEFORGE-Auftragsregister prüfen, dann kleinste funktionsfähige Implementierung auf getrenntem Git-Branch, Test, Review, erst danach nächster Auftrag. Kein eigenständiger Agentenserver.
