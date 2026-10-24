# Cinematic-/Menu-Implementierungsplan für Claude Code

## Architektur
- `UGenesisCinematicSubsystem` (GameInstanceSubsystem) verwaltet Cine-Kontrakte; bindet `UGenesisSaveSubsystem` (ein einziges persistentes Save-Schema), WorldClock und CausalEvent-IDs. In neuem V4-Projekt erst implementieren, wenn realer Codebestand geprüft.
- `USceneDefinition` als versioniertes PrimaryDataAsset, referenziert eine LevelSequence oder einen genehmigten Medienmaster. Filmsequenzen mit interaktiven Entscheidungen benutzen pausierbare Sequencer-/Gameplay-Zustände; niemals Ablauf bei starren Shot-Zeiten erzwingen.
- `USceneTransitionController`: `Eligible`, `BindingValidated`, `Ready`, `Playing`, `AwaitingInteraction`, `CommitPending`, `Committed`, `HandedBack`; jedes Ereignis idempotent, Source-Hash-gebunden. Eingabe/Kamera/Postprocess/TimeDilation nach ReturnControlState zurücksetzen.
- `UReplayRecipe`: Quellenart `OriginalRecording`, `StateReconstruction`, `AbstractEcho`, mit belegbarer Datenherkunft. Für C20/C00 gilt `OriginalRecording` mit **gleicher Master-Datei** und gleichem Audiomaster.
- `UGenesisMenuFlowSubsystem` (oder UI-Controller): UI-Graph aus DataAssets, UMG/optional CommonUI mit Enhanced Input, keine zweite Save-Implementierung. MainMenu-Background läuft auf statischer Sequence oder separater Simulationsinstanz ohne Save-/Weltuhrzugriff.
- `UGenesisSubtitleRouter`: Sprecher/Cue-Lokalisierung, Wav-Timecode, Untertitel, Pause/Seek/Skip. Spracheinstellungen getrennt von Musik/Effekten.

## Source-to-Scene-Pipeline
Original-ScriptLock-Text + autorisierte Versionsnummer → Shot/Dialogue/Subtitle/Cue-IDs mit SHA → Figuren-DNA/Set/Props als Jobs an vorhandene Rollen → Blender asset `.blend`/UE assets → Sequencer Shot Assembly → optionale Movie Render Queue Master → Integration in Echtzeit/GameBuild → Tests/Abnahme. Nie einen Clip als fertig deklarieren, wenn nur Beschreibung/Storyboard besteht.

## Menu-Flow-Implementierung
Menü-Blueprints/C++ Widgets: BootWarnings → ggf. C00/C01 → Titelkarte → Start/Continue/Load/Settings/Accessibility/Credits/Quit. Wird Film übersprungen, tritt derselbe zulässige SceneCommit ein. Gameplay PauseMenu: Resume, Settings, Save, Load, Back to Main. Speicherdaten vor Fortsetzen validieren; unzugängliche Optionen sichtbar, aber korrekt deaktiviert. Focus/Controller immer testbar. Menü kein Spoiler für C19/C20.

## Engine-Prüfungen
Auf lokaler Engine festhalten: UE-Version, Plugins, GUI, Editor/Python verfügbar, MRQ-Version, Audio-Subsystem, MetaSounds; verfügbare APIs vor Skripteinsatz gegen die tatsächlich installierte Version prüfen. Freigegebene Änderungen per isoliertem Branch, je Agent disjunkte Schreibbereiche; nur ein Editor-Writer gleichzeitig. Film- und Audioquellen ausschließlich lizenziert. Für endgültige Testbeweise: Real Unreal Editor-/PIE-Lauf, Render, Controller, Save/Load, Windows-Build, menschliche Review.

## Risiken
C00-Master keine vorhandene fertige Datei im Paket. C21 nach Original (Konflikt sichtbar machen). C15/C16 und C17 nur nach Directorentscheidung bei Kollision. Keine garantierte 0-Sekunden-Ladezeit, keine garantierten perfekten KI-Stimmen, keine automatische AAA+-Qualität. Keine Story-Dialoge hinzuerfinden.
