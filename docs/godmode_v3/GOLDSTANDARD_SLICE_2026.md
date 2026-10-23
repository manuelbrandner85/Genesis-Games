# GENESIS – GOLDSTANDARD-SPIELREGION 2026 – verbindliche Produktionsregel

## Zweck und Umfang

Eine **vollständige, überprüfbare** Beispielregion in der bestehenden chronologisch fortlaufenden Welt 2026 vor Skalierung. Kein neues GENESIS-Spiel und keine willkürliche Wahl historischer/futuristischer Epochen. Eine Region „Flussdorf / Markt / Werkstatt / Brücke / Wetterstation“ wurde in einem älteren Bestandsplan als **Kandidat** vorgeschlagen, ist **nicht automatisch genehmigte Weltgeografie**. Claude sucht die Original-Regionenmatrix in V61/V62 und wartet bei Kanonlücken auf die Entscheidung.

**Scope-Freeze:** Bei G0 wird die Slice-Region samt genehmigtem Storyanker als `SLICE_DESIGN_FREEZE` dokumentiert. Scopeänderungen brauchen einen Änderungsauftrag. Vorher laufen nur Tech-/Graybox-Szenarien ohne fiktionalen Kanonanspruch.

## Umsetzungsreihenfolge und echte Outputs

1. **G0 Audit & Source Vault:** Basiskommit, alle lokalen Original-Spielbibeln, ScriptLock, J00–J24, bekannte Konflikte, Ist-Code, Maschinen/UE/Blender-Versionen, Lizenzen, bestätigte Features. Quellen-Hashes und Statusbericht. Ohne Originalmaterial nur tech-experimentelle Arbeiten.
2. **G1 Team und lokaler Toolcheck:** 24 Agenten tatsächlich unter `.claude/agents`, Skills und Hooks im Claude-CLI sichtbar; keine verdoppelte StudioBrain-Datenbank. Kein Toolstatus ohne manuellen/CLI-Test.
3. **G2 Asset Pipeline Smoke:** einfaches Testmesh; `.blend` → Export → UE Asset → rücklesbarer Import → PIE-Screenshot + Logs. Testmesh ist weder Held noch finales GENESIS-Asset.
4. **G3 Hero-Character Quality Proof:** freigegebene Figur mit mehransichtiger Referenz, metrischem Vertrag, sauberem Rig, Material/LOD, Animations-/Face-/Outfit-Test. Human Artist Review. Ohne finale Referenzen prototypisch.
5. **G4 NPC/World Core:** WorldClock, SaveBundle, CausalGraph/EventBus, StateTree, Smart Objects, Near/Mid/Far, Save/Load/Streaming Regression. Keine zweiten Uhr-/SaveSubsysteme.
6. **G5 Begehbare Region:** Wohn- und Arbeitsorte aus freigegebenem Register, mehrere unterschiedliche NPC-Rollen, Tageszeiten, realistisches Wettersystem, Navigation, ein genehmigter Missionsanker, lokalisierte Dialog-/UI-Kette, relevante Verkehrsszenen falls bestätigt.
7. **G6 Cinematic/Audio Proof:** genehmigte Szene nach ScriptLock und echte Ton-/Subtitle-IDs; C00/C20 Master-Replay-Vertrag prüfen, aber ohne finale Storyfreigabe keine kanonische Filmproduktion. Deutscher Audio- und Voice-Rechtestand.
8. **G7 Standalone Build & Tests:** echte Windows-Spielversion, verständliche Eingabe, persistenter Save, Life-Szenario, Spieltest, Crash/Regression und kontrollierter Performancebericht auf echter Zielhardware.
9. **G8 Human QA/Creative Gate:** mindestens eine fremde Testperson; technische und ästhetische Freigabe getrennt. Visuelle Qualität, Spielfluss, Story, UX, Zugänglichkeit. Bugs nach severity protokollieren.
10. **G9 Scale Decision:** größere Weltbereiche erst nach erfüllten Gates G0–G8 und ausdrücklicher Freigabe erweitern.

## Konkrete spielbare Slice-Akzeptanz

- Windows-Spiel startbar, Steuerung Maus/Tastatur und Controller nachweislich getestet.
- Mindestens eine interaktive Innen- und Außenumgebung (sofern Original-Worlddaten es erlauben) mit Wegfindung, Kollision, Beleuchtung und Wetter.
- Mehrere NPCs mit verschiedenen Rollen, Tagesabläufen, lokalen Bedürfnissen, passendem Verhalten, gespeichertem Ereignisgedächtnis.
- Ein Originalmissionsanker mit echten Alternativen, Folgen, Mission-Skip/Save/Load; keine Storyumdeutung.
- Eine hochwertige **freigegebene** Spielerfigur statt ausschließlich Proxy, inklusive Rig, AnimBP und Gesichtsinteraktion.
- Audiosystem mit Wetter/Foley/Dialog/Untertiteln, geprüften Audioquellen und Loudness-Review.
- WorldPartition/LOD-Handoff und relevante persistente Zustände (nicht nur permanent geladene Map).
- Getrenntes Testprotokoll: Unit, Gameplay/PIE, Standalone, Save/Load, Streaming, GPU/CPU, menschlicher Test.
- Artefakte: `Genesis.uproject`, `.uasset`, `.umap`, master `.blend`, Referenzmanifest, gebaute EXE, Logs/Screenshots/Videos/Traces und Lizenzregister.

## Nicht vorab behaupten

AAA+ ist Ziel, keine garantiert erreichbare Bewertung. Zahl der NPCs, Bildrate und Zielgeräte werden nach Hardwareinventur und sichtbaren realen Benchmarks festgelegt. Fotografische Schönheit = menschliche Sichtprüfung, keine Pixel-Metrik allein. Großer Contentumfang ist **nicht** gleich spielbare Qualität.

## Auflösung der schwierigen Quellenfragen

- C00–C21 ScriptLock-Fassung 1.1 enthält Vorschlags-/Freigabestatus; neuere ausdrückliche Freigabe als echte Datei prüfen.
- C15/C16 `CON33-01`, C17 Epochenwortlaut und C21 Finale-Ein-Welt-Konflikt bleiben im Conflict-Register.
- Erste spielbare Inkarnation 2026; Prolog mit altem Mann 2026 ist separate Vorgeschichte.
- Jenseits oder freiwilliges Rebirth, gleiches fortlaufendes Weltjahr; keine Epochenwahl.
- Ohne gesicherten Storyanker darf nur ein neutraler Testfall gebaut werden; nie generierte Mission als „Original“ ausgeben.

## Zielhardware, Bildrate, Detailbudget

`hardware_profile.json` hält CPU, GPU, VRAM, RAM, SSD, Auflösung, Skalierung, Preset, Render-Backend, UE-Commit und Benchmarkbedingungen. Messwerte werden in Millisekunden für CPU/GPU/Frametime, Speicher in MiB/GiB und IO/Ladezeit gespeichert. **Keine unbestätigten festen FPS-/GPU-Zahlen**. Der Game Director bestätigt Zielbudget nach Messung einer belastbaren Baseline.
