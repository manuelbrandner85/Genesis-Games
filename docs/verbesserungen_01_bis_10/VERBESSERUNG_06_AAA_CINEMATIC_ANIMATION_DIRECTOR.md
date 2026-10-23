# GENESIS – Verbesserung 06: AAA Cinematic & Animation Director

**Bestätigt:** JA zu allen zehn Verbesserungen am 23.10.2026.
**Status:** geplanter, fachlich freigegebener Entwicklungsumfang; keine hier erfolgte UE-Implementierung.
**Leitziel:** C00–C21 filmisch, durchgängig storytreu und interaktiv – Sequencer plus Blender-Rigging, Performance und Replay.
**Gültigkeit:** nur bestehendes `manuelbrandner85/Genesis-Games`, Claude Code als Entwicklungsleitung, keine Story-Umschreibung.

### Produktionsfunktionen
1. Original ScriptLock v1.1 C00–C21 vollständig lesen; Status **Finalfreigabe offen**, daher keine storyabhängigen Renderersetzungen ohne spezifische Freigabe.
2. Szenen-IDs, Shot-IDs, Varianten, Beteiligte, ReturnControlState und Gating/Skip aus Quellskript übernehmen.
3. C00-Prolog und C20-Replay identische Video-/Audio-Quelle; automatische Hash-/Timingprüfung.
4. C19-Kollektiv enthüllen, niemals in früheren Untertiteln oder Debug-UIs verraten.
5. Flexible Kameraformen: fixed, state-bound, replay und world-derived; jede Sequenz hat Sequencer-/Kamerarig-Vertrag.
6. Realistische Körperanimation pro Alter und Situation, keine immer gleiche Motion-Animation.
7. Foot IK, Hand-Prop Constraints, Eye Lines, Mouth Shapes, Gesichtsanimation und Outfit-Sim auf Ausgangsmesh prüfen.
8. Dialog-Lipsync nur mit tatsächlich bereitgestellten deutschen Wave-Files/Fonem-/Morphdaten; nicht „fertig“ markieren mit TTS-Text.
9. Licht: begründete Beleuchtungsquellen, konsistenter Look, Kontakt/Reflexionen, Proben für mehrere Belichtungen.
10. Interaktive Entscheidungspause erhält WorldState korrekt und commitet auch beim Skip.
11. Save/Load in C14–C17 transaktional inkl. Soul-Kontinuität.
12. Replay kann `OriginalRecording`, `StateReconstruction` und `AbstractEcho` auseinanderhalten; nichts Erfundenes als Aufzeichnung ausgeben.
13. Film-/Gameplay-Übergänge vermeiden Kamera-Sprünge und doppelte Trigger.
14. Accessibility: Untertitel, Flash-Reduktion, Trigger Skip, QTE nicht zwingend, Lesbarkeit.
15. QA: Shots gegen Originalzeitcodes, Assetlisten, Sprachausgabe und Story-Quellen prüfen.

### Freigabe
Szenen-Contract (`SceneID`, `ScriptVersion`, `SoulID`, `LifeID`, `WorldID`, `WorldTime`, `ParticipantIDs`, `EventEvidenceIDs`, `VariantID`, `AudioCueIDs`, `SubtitleCueIDs`, `SkipPolicy`, `ReturnControlState`, `CommitState`) wird vor Spielstart jeder Cine validiert. Creative-Review erst nach in-UE-Wiedergabe und echten Logs.

### Technischer Produktionsauftrag
Arbeite mit dem vorhandenen Repo, GAMEFORGE StudioBrain und Character Creation 4.0, sofern tatsächlich vorhanden. Ermittle Basiscommit, freigegebene Quellen und installierte Werkzeuge. Dokumentiere Architektur, konkrete Dateien, Tests und Evidenz. Führe nur genehmigte ungefährliche Schritte aus; für riskante Änderungen explizite Freigabe. Übergebe jeden Arbeitsschritt an unabhängige QA. `NOT_IMPLEMENTED` bleibt sichtbar, bis ein echter Editor-/Runtime-Nachweis vorliegt.

### Cinematic Scene Contract
Die Produktionsinstanz verwendet `SceneID`, `ScriptVersion`, `SoulID`, `LifeID`, `WorldID`, `WorldTime`, `WorldSeed`, `ParticipantIDs`, `EventEvidenceIDs`, `VariantID`, `Language`, `CinematicState`, `SkipPolicy`, `ReplayRecipeID`, `AudioCueIDs`, `SubtitleCueIDs`, `ReturnControlState`, `ReturnLocation`, `CommitState`. `Eligible → BindingValidated → Ready → Playing → AwaitingInteraction? → CommitPending → Committed → HandedBack` ist Pflicht. Skip führt ebenfalls zum gültigen Commit, nicht zu verschwundenen Lebensentscheidungen.

**Kameravertrag:** Für jeden Shot Objektliste, Kanontext, Dauer/Variante, Sensor/Brennweite, Fokus/Blende, Bewegungskurve, Licht-Setup, LipSync-Cue, Animations-Timeline, gewünschter emotionaler Schwerpunkt und Verknüpfung zur zurückgegebenen Spielkontrolle. Für archivische Sequenzen sind `OriginalRecording`, `StateReconstruction` und `AbstractEcho` nicht austauschbar. Eine aus GameState rekonstruierte Erinnerung darf niemals als garantiert echte Vergangenheit behauptet werden.

**Kanon-Gates:** C00/C20 nutzen denselben Masterclip sowie identische Audio- und Untertitel-Timecodes; C19-Enthüllung nie in frühem HUD/Untertiteln; Geburt/Tod/Kindszenen folgen den realen aktiven Biologie- und Lebensphasen. Bei nicht vorhandener Vorbedingung darf eine Szene auslassen oder alternative belegte Variante verwenden; der Agent erfindet keinen Ehepartner oder Elternteil.

**QA-Fälle:** A1 Contract-Validierung vor Sequencer; A2 zwei Skip-Wege speichern gleich; A3 Save/Load innerhalb Interaktion; A4 Audio-/Subtitel-Timecodes passen; A5 C00/C20 Mastergleichheit; A6 Character-Facial-Performance im UE-Editor; A7 keine C19-Spoiler; A8 Alter/Modelle/Ausstattung und Wetter glaubwürdig; A9 Creative Signoff vorhanden.

### Abhängigkeiten / nächste Umsetzung
Vor endgültiger Storyfreigabe ausschließlich Dummy-Sequenzen auf technischem Testlevel bauen. WorkIDs dürfen erst nach Architektur-/Kanonabgleich in reale Dateiedits umgesetzt werden.
