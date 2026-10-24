# GENESIS GODMODE 4.2 – ULTIMATE CINEMATIC & MENU EXPERIENCE

**Status:** Freigegebene *Entwicklungsanforderung*, noch **keine implementierten Cinematics, Musikstücke oder Spielmenüs**. Version: 4.2 · 24.10.2026.

## 0. Mission & Grenzen
Claude Code entwickelt das **gesamte GENESIS-Spiel neu** auf Basis V4.1 und ergänzt jetzt eine durchgängige Film-, Menü-, Audio- und Übergabepipeline. Diese 4.2 ersetzt weder das 4.1-KI-System noch die übrigen 24 Agenten; es kommen **keine neuen laufenden Agentenplattformen** hinzu. Prolog, Hauptmenü, Storysequenzen, Ladephasen, Pausenmenü, Save/Load, Einstellungen, Abspann und die Reise von Cinematic in echtes Gameplay werden vollständig programmiert und kreativ produziert, sobald die konkreten Quellen freigegeben sind.

**Kanon unveränderlich:** 22 Kapitel C00–C21; altes Prolog-Leben als frühere Inkarnation erst in C20 offenbaren; C00 und C20-Rückblende verwenden den *exakt gleichen* Audio-/Bild-Master; Kollektiv erst C19; keine freie Epochenwahl; ein chronologisch fortlaufender Weltzustand ab erster spielbarer Inkarnation 2026; nach Tod Jenseits oder freiwillige Wiedergeburt. Bestehendes Drehbuch und J00–J24 ohne eigenmächtige Änderungen bewahren. Konflikte C15/C16 (CON33-01), C17-Wortlaut und C21-Finale sind als `WAITING_DIRECTOR_DECISION` zu dokumentieren und **nicht** umzuschreiben.

**Quellenlage:** Im bisherigen ZIP sind die vollständigen Originaldrehbücher/Originalaufnahmen *nicht enthalten*. Die Szenen-IDs/Titel im beigefügten Arbeitsindex sind Planungshinweise, kein Ersatz für das gesperrte Original. Ohne genehmigte Original-Szene: nur Technikprototypen, keine endgültigen Darstellungen/Dialoge/Filme.

**Sicherheit:** Keine Installationen/Downloads, Stimme-/Musikrechte, Kosten, Repo-Push, Überschreiben, Veröffentlichung ohne gesonderte Freigabe. Claude darf geprüfte freie Tools nach Einzelfreigabe einsetzen; keine Behauptung einer automatisch garantierten AAA+-Qualität.

## 1. Technische Umsetzung
- Unreal Engine 5: **UMG**, ggf. CommonUI erst nach Prüfung; Enhanced Input, Level Sequencer, CineCameraActor, Movie Render Queue (ggf. Plugin aktivieren nach Freigabe), Audio/MetaSounds. Keine vorausgesetzte Verfügbarkeit experimenteller Funktionen.
- Runtime-Szenendienst (C++ Subsystem / datengetriebene Assets): `SceneContract`, `CinematicStateMachine`, `SequenceRegistry`, `CinematicTransitionService`, `ReplayAssetRegistry`, `SubtitleAudioRouter`, `UIFlowCoordinator`. Andere existierende Spielsysteme lediglich referenzieren, nicht duplizieren.
- Bei vorgerenderten Clips bevorzugt Master-Datei und überprüfte Wiedergabe; bei interaktiven LevelSequences dieselbe Storyvertragslogik. Grafikqualität der Offline-Renderings nicht unbemerkt als Echtzeit-Qualität behaupten.
- `SceneContract`: `SceneID`, `ScriptVersion`, `SoulID`, `LifeID`, `WorldID`, `WorldTime`, `WorldSeed`, `ParticipantIDs`, `EventEvidenceIDs`, `VariantID`, `Language`, `CinematicState`, `SkipPolicy`, `ReplayRecipeID`, `AudioCueIDs`, `SubtitleCueIDs`, `ReturnControlState`, `ReturnLocation`, `CommitState`.
- Szenenzustände: `Eligible → BindingValidated → Ready → Playing → AwaitingInteraction? → CommitPending → Committed → HandedBack`. Beim Skip **niemals** `Playing → HandedBack` ohne Weltzustand-Commit. Der Save-/Soul-/World-/Life-Bundle bleibt atomar; Szene muss bei Spielabsturz konsistent wiederaufnehmbar sein.
- Audio: M01–M12 werden nur an geprüfte Original-Cues gebunden. Lebens-/Familienmotiv und Soul-Motiv sind getrennte Quellen. Untertitel werden an die echte Audio-Uhr gekoppelt.

## 2. 50 verbindliche Produktionsfunktionen (mit echten Abnahmekriterien)

### Kanon & Szenensteuerung

**01 – Source-Lock-Verifier.** Original-Drehbuch/Freigabe und Hashes vor jeder Szene prüfen. **Output/QA:** quellgebundenes Manifest; Änderung wird blockiert.

**02 – 22-Scene Production Registry.** C00–C21 einzeln mit State/WorkID/Assets/Test dokumentieren. **Output/QA:** 22 eindeutige IDs, kein Phantom-DONE.

**03 – Cinematic Contract Validator.** SceneID, ScriptVersion, SoulID/LifeID/WorldID, Zeit, Variante, Ort und Teilnehmer binden. **Output/QA:** vollständige Pflichtfelder vor Play validieren.

**04 – Canon Reveal Guard.** C19/C20-Enthüllungen nicht durch Menü, Untertitel oder Dateinamen in UI verraten. **Output/QA:** Spoiler-Tests vor und nach Freischaltung.

**05 – Narrative Conflict Escalation.** C15/C16 CON33-01, C17 Epochenwortlaut, C21-Finalkonflikt offen halten. **Output/QA:** BLOCKED_APPROVAL statt eigenmächtiger Storykorrektur.


### Prolog & Replay

**06 – C00 Master Capture.** freigegebenen Prolog als versionierte Originalaufnahme produzieren. **Output/QA:** Master-Asset-ID, Bild-/Audio-Hash, Review.

**07 – C00–C01 Startup Logic.** Kanongetreue Reihenfolge, Film, Titelkarte und Startmenü. **Output/QA:** Erststart, Wiederstart, Skip, Neustart getestet.

**08 – C20 Exact Replay.** C00 nur als identische Master-Ressource referenzieren, nicht neu rendern. **Output/QA:** identischer SHA256 der Originaldatei.

**09 – Prolog Skip Persistence.** Skip führt über CommitPending zu identischem Story-Weltzustand. **Output/QA:** Vorher-/Nachher-Savevergleich.

**10 – Alternative Playback Handling.** fehlende oder beschädigte Filmdateien mit definiertem Fehlerpfad behandeln. **Output/QA:** kein Schwarzbild-Softlock, kein falsches Ereignis.


### Szenen & Kameraführung

**11 – Level Sequencer Scene Factory.** LevelSequence-Assets mit Bindings pro genehmigter Szene anlegen. **Output/QA:** Editorlog und Assetpfade.

**12 – Shot/Camera Contract.** Shots, Brennweiten, Schärfe, Blocking und Übergänge aus Originalquellen. **Output/QA:** Director-/Kanonvergleich.

**13 – Runtime vs Render Master Strategy.** Realtime-Sequenz oder vorgerenderter Clip pro Shot bewusst festlegen. **Output/QA:** Cook-/Speicher-/FPS-Test.

**14 – Cinematic State Machine.** Eligible→Validated→Ready→Playing→AwaitChoice?→CommitPending→Committed→HandedBack. **Output/QA:** Transitions-Tests inkl. Unterbrechung.

**15 – Replay Modes.** OriginalRecording/StateReconstruction/AbstractEcho sauber unterscheiden. **Output/QA:** keine Rekonstruktion als Original behaupten.


### Digital Actors & Lip Sync

**16 – Character-Identity Binding.** Cinematic-Figuren aus genehmigter Character-DNA/Soul-/LifeID beziehen. **Output/QA:** identische IDs und Kostüme pro Shot.

**17 – Facial Performance QC.** Augenbewegung, Blendshapes, Lippenschluss, Ausdruck und Voice synchronisieren. **Output/QA:** Close-up-Differenzreview + Lippenprüflauf.

**18 – Body Performance Blocking.** Hände, Blickachsen, Standpunkte, Requisiten und Kontakt realistisch ausrichten. **Output/QA:** sichtbarer Animations-/Kollisionstest.

**19 – Life-Phase Actor Profiles.** Kind/Erwachsene/Ältere mit gültigem Rig/Bewegung verwenden. **Output/QA:** keine erwachsene Stimme bei Säuglingen.

**20 – Shot Continuity Guard.** Anschlussfehler an Position, Kleidung, Tageszeit, Schäden, Beleuchtung prüfen. **Output/QA:** Vorher-/Nachher-Snapshots.


### Musik, Dialog & Sound

**21 – Cinematic Cue Bible.** Musik/SFX/Ambience pro Szene anhand Original-IDs planen. **Output/QA:** Cue-Liste vollständig, Freigabe dokumentiert.

**22 – Soul vs Family Motifs.** Soul-Motiv strikt vom gelebten Familienmotiv trennen. **Output/QA:** separate Datenquellen und Mix-Rezepte.

**23 – German Dialogue Pipeline.** kanonische deutsche Dialoge, VariantIDs, Timecodes, Sprecher IDs. **Output/QA:** kein erfundener Text; Aufnahme- und Subtitlecheck.

**24 – Adaptive Music Transition.** Stems/Busse für Menü/Gameplay/Cinematic mit sauberen Übergängen. **Output/QA:** kein Audio-Doppelstart; Hörtest.

**25 – Audio Rights & Deliverables.** Musik/Voice/SFX pro Asset lizenzieren und WAV/Loudness prüfen. **Output/QA:** Provenienz + technische QA + menschliche Abnahme.


### Hauptmenü & UI

**26 – Cinematic Main Menu.** dynamischer aber spielstandsisolierter Menü-Hintergrund, GENESIS-Branding. **Output/QA:** keine Weltzeit-/Save-Mutation.

**27 – Save-Integrated Continue/Load.** Fortsetzen, Laden, Neues Spiel mit echtem Save-Bundle verknüpfen. **Output/QA:** defekte/fehlende Slots mit korrektem Fehlerpfad.

**28 – Settings Persistence.** Grafik, Audio, Controller, Sprache, Untertitel dauerhaft speichern. **Output/QA:** Neustart-Roundtrip.

**29 – Controller & Focus Navigation.** volle Maus/Tastatur/Controller-Bedienung samt sichtbarem Fokus. **Output/QA:** No-mouse-Spieldurchlauf.

**30 – Localized Text & UI Layout.** alle Texte auf Deutsch, längere Übersetzungen ohne Überlauf. **Output/QA:** Layout-Screenshots und Textüberlauf-Test.


### Screen-Flows & Übergänge

**31 – Seamless Gameplay Return.** nach Szene Kontrolle, Kamera, Input, Ort, Uhr korrekt zurückgeben. **Output/QA:** PIE- und Standalone-Test.

**32 – Save/Load in Cinematics.** Suspend/Resume oder definierter Checkpoint mit atomarem Commit. **Output/QA:** Crash-/Restart-Tests.

**33 – Chapter Transition System.** Kapitelankündigungen, Ortswechsel, Zeitraffer nur nach genehmigter Story. **Output/QA:** keine erfundene Zeitreise.

**34 – Loading & Streaming Presentation.** legale/spielbare Übergänge bei World Partition mit echtem Load-State. **Output/QA:** kein unendlicher Spinner / Softlock.

**35 – Credits & Ending Routes.** C21-Endoptionen gemäß Original, Abspann, Lizenzcredits, Rückkehr. **Output/QA:** C21-Konflikt nicht automatisch repariert.


### Zugänglichkeit

**36 – Subtitle Timing.** Untertitel, Sprecher-ID, Farben, Textgröße synchron zum hörbaren Cue. **Output/QA:** Pause/Seek/Skip-Langzeittest.

**37 – Photosensitivity Safety.** Warnungen, reduzierte Flashes, begrenzte Kameraeffekte. **Output/QA:** konfigurierbarer Testmodus.

**38 – Emotionally Sensitive Skip.** optionaler Skip für Belastungsszenen ohne Verlust von WorldState. **Output/QA:** vergleichbare Save-Zustände.

**39 – Audio & Visual Accessibility.** separater Musik-/Sprache-/Effektmix, Kontrast, Schrift. **Output/QA:** lesbare UI auf kleiner Auflösung.

**40 – Input Remapping & Captions.** freie Belegung / Controller-Pfade / verständliche Textalternativen. **Output/QA:** Maus- und Controller-Tests.


### Automation & Asset Pipeline

**41 – Blender→Unreal Scene Props.** Props, Sets und Figuren via freigegebenen Asset-DNA-Vertrag übergeben. **Output/QA:** Maßstabs-/Material-/Rig-Verifikation.

**42 – Sequence Automation Tools.** Sequencer-Basisassets per Unreal-Python erst nach Toolcheck erstellen. **Output/QA:** logbare Editor-Ausführung.

**43 – Render Asset Matrix.** Reels, Stills, WAV, Subtitle, Sequence und Source-Hashes versionieren. **Output/QA:** Manifest-Validator.

**44 – Production DAG Integration.** 24 bestehende Agenten, StudioBrain-Arbeitspakete, Ownership und Freigaben. **Output/QA:** keine zweite Agenten-/Schedulerinstanz.

**45 – Safe Batch Render.** Movie Render Queue nur mit versionierter preset/freigegebenem Job. **Output/QA:** Dateiausgabe+Asset-Facts+Qualitätsprüfung.


### QA & Release

**46 – Scene QA Matrix.** für alle 22 Szenen Quelle, Variante, Replays, Save, Performance testen. **Output/QA:** 22× prüfbarer Status.

**47 – Menu Interaction QA.** vollständiger Menü-Graph, Fokussierung, Screenreader/Text, Rückwege. **Output/QA:** keine Sackgassen.

**48 – Audio/Video Sync QA.** Timecode- und Untertitelsynchronität bei Frameratedrops/Skip. **Output/QA:** gemessene Drift, toleranzbasiert.

**49 – Packaged Windows Smoke Tests.** Prolog, Menü, Save, C00, Skip und End-Rückweg im Build. **Output/QA:** realer Build-Log/Testergebnis.

**50 – Human Creative Acceptance.** Game-Director-Review von Film, Grafik, Ton, Menü und Gefühl. **Output/QA:** ACCEPTED nur nach tatsächlicher Freigabe.

## 3. Produktionsphasen – immer nachweisbare Ausführung
| Phase | Arbeitspaket | Technische Abnahme |
|---|---|---|
| CM0 | Quellen- und Toolaudit | Original-ScriptLock, Quellenhashes, Engine-/Plugin-/Audio-Stand, offengelegte Konflikte |
| CM1 | Szenen-/Menüverträge | 22-Scene-Registry und Menügraf validieren; Freigaben verknüpfen |
| CM2 | Technisches Startmenü | boot → title → menu, echte Controller-Navigation, Save-Slots, Einstellungen |
| CM3 | C00-**Technik**-Prototype | in Unreal abgespielte Demo-Sequenz mit Platzhaltern, keine erfundenen C00-Dialogleistungen |
| CM4 | C00 Produktionsfreigabe | Shotlisten/Charakter-DNA/Audio aus Originalquellen + Director-Abnahme |
| CM5 | C00 filmreif + C20 Masterbindung | echten freigegebenen Master aufnehmen, SHA256/Playback-ID, C20 exakt wiederverwenden |
| CM6 | Filmintegration | Untertitel, Audio, Save/Skip/ReturnControl, Rückfallpfad real testen |
| CM7 | 22 Kapitel iterativ | je Szene: Originalquelle, Sequenz, Audio, Variablen, unabhängiges QA |
| CM8 | finales Menü/Abspann | visuelle Abnahme, Credits, alle Optionen und Accessibility |
| CM9 | Windows-Spielbuild | automatisierte Tests + echte menschliche Playtests auf Zielhardware |

**Abnahme-Gate:** Nach jeder Phase `SPECIFIED`, `BLOCKED_SOURCE`, `BUILT_UNTESTED`, `ENGINE_TESTED`, `HUMAN_REVIEWED`, `ACCEPTED` mit Pfad, Log, Commit, SHA256. Kein `DONE` für reine JSON-Dateien oder Storyboards. Autonome nächste Arbeitspakete nur nach echten Abnahmen, keine stille Freigabe.

## 4. Agentenbelegung (bestehende 24 Rollen)
- `genesis-script-guardian`: Source-Lock, Reveal, C00/C20, offene Konflikte.
- `genesis-cinematic-director`: Sequencer, Shot-Kontrakte, Übergänge, Render.
- `genesis-ui-accessibility`: Main/Pause/Save/Settings/Controller/Untertitel-Zugänglichkeit.
- `genesis-audio-director` und `genesis-face-voice-sync`: Cue-/Voice-/LipSync-Kette.
- `genesis-character-artist`, `genesis-motion-specialist`, `genesis-environment-artist`: Figuren, Mocap/Animation, Sets.
- `genesis-unreal-core`: C++-Szenen-/UI-Integration, Tests im Editor.
- `genesis-qa-release`: unabhängig prüfen; keine doppelte `ACCEPTED`-Selbstfreigabe.
- `genesis-master-director`: WorkIDs, Rechte, Quellfreigaben und Prioritäten bündeln.

**Referenzen:** `docs/v4_2/SCENE_MATRIX_C00_C21.json`, `MENU_FLOW.json`, `QA_ACCEPTANCE.md`, `IMPLEMENTATION_GUIDE.md`, `AUDIO_MUSIC_CUE_SPEC.md`, `WORK_ORDERS.csv`, `tools/v4_2/`.

## 5. Konkreter erster Auftrag
> Claude Code, lies zuerst `CLAUDE.md`, den V4.2-Masterprompt und die V4.1-Quellen. Prüfe nur lesend alle kanonischen C00–C21/J00–J24-Quellen, die Unreal-/Audio-/Bild-Tools und die 24 Agenten. Schreibe dann ein prüfbares Szenen- und Menü-Auftragsregister. Beginne mit dem technisch funktionierenden Hauptmenü (Controller, Save-Slots, Einstellungen) und einer nichtkanonischen Sequencer-Testszene, damit die Schnittstellen geprüft werden. Baue die tatsächlichen Original-Filme erst nach Freigabe der Story-/Shot-/Audioquellen. Priorisiere den exakten C00/C20-Master und die sicheren Save-/Skip-Übergänge. Anschließend bringe pro Phase tatsächlich lauffähige Unreal-Artefakte mit Logs, statt lediglich Pläne zu beschreiben.
