# GENESIS – QA / Beweis- und Abnahmeregeln

## Unbedingt automatisieren
- **Storylock:** 22 einzigartige C00–C21 SceneIDs, Originaldialog-/Shot-Hashes unverändert, C19/C20 keine frühzeitigen Spoiler, C00/20 Replay bitidentisch bei fixen Masters; C21-Finalfunktion nicht heimlich geändert.
- **GameStart:** korrekter Prolog-/Menü-Flow ohne doppelten Film; erster spielbarer Start im freigegebenen Weltzeitkontext; keine Epoch-Picker.
- **Save:** Atomarität für Soul/World/Life; Crash/Power-Loss sofern sicher reproduzierbar; Rückfall auf .bak; 1→2→spätere Schemamigration; gleichbleibende IDs und WorldTime; keine doppelte Rebirth-Ausführung.
- **Human:** Turnaround-Assetmaße/face rig, bones/skeleton/IK/animation blueprint/LOD, extreme Deformationen, Fuß-/Handkontakte in UE.
- **NPCs:** 24h-Plan, Bedürfnisse/Interaktionsabbruch, Memories nach Laden; kein Claim, den Charakter nicht erlebt hat.
- **Quests:** alle Zweige, Fallbacks, Entscheidungen, Story-Gates, automatische Deadlock-Suche, Persistenz von Konsequenzen, Deadlines nur bei wirklichen Ereignisfristen.
- **Vehicles/World:** Physikstabilität, Verkehrsbeziehungen, Reise-/Save-/Load, WorldPartition-Streaming, keine systemischen Duplikate, GPU-/CPU-Profile.
- **Accessibility:** deutsche Untertitel und Sprecherlabel, Controller-only Weg, einstellbare Textgröße/Headbob/Flashes, Pause/Skip ohne Datenverlust.
- **Legal:** kostenloses Asset nur nach Lesen der gültigen Lizenz; Voice-/Music-/Image-Rechte, gefiltertes Material ohne Beleg entfernen.

## Pflichtbelege pro WorkID
1. Git-Commit + Diff/Datei-Hash und genaue Programmversion.
2. Reproduzierbarer lokaler Build-/Editor-/CLI-Aufruf mit Exitcode und Zeitstempel.
3. Unreal-/Blender-Rohprojekt und Export, keine bloße Beschreibung.
4. Vorher-/Nachher-Assets, echte Screenshots/Logs, nachvollziehbares Savegame.
5. Automatisierte Tests mit Testnamen, Pass/Fail und Failure-Artefakt.
6. QA-Review von Agent 24, getrennt vom Implementierer.

## Zusätzliche manuelle Reviews
- Menschen bewerten Glaubwürdigkeit, Mimik, Bewegungsfluss, deutsche Sprecherleistung, emotionale Wirkung sowie ethische Plausibilität. Automatisierte Tests allein können „fotorealistisch“ nicht beweisen.
- Reale Performancezahlen auf konfiguriertem Rechner dokumentieren; keine pauschalen 60/120 FPS-Behauptungen.
- `BUILT_UNTESTED` ist nicht `TESTED`, `TESTED` nicht `ACCEPTED`.

## Veröffentlichungssperren
`STORY_CONFLICT | COPYRIGHT_UNCLEAR | BROKEN_BUILD | SAVE_CORRUPTION | DEADLOCK | CRITICAL_PERFORMANCE | INACCESSIBLE_CONTROLS` müssen behoben/ausdrücklich freigegeben sein.

## GAMEFORGE 03 / Claude-Code-Übergabegate (zusätzlich)
- Original-MD vollständig gelesen, bytegenauer SHA-256 und 50/50 Function-Tracking nachgewiesen.
- Abhängigkeiten StudioBrain 01 und Character Creation 4.0 02 auditiert; keine zusätzlichen Agenten-Scheduler/Save-Systeme angelegt.
- NPCs, Wetter, Tiere, Siedlungen, Beziehungen, Missionsevents, WorldStreaming und Near/Mid/Far mit der Original-03-Testmatrix (30 explizite Tests) abgeglichen.
- Laufzeitspiel funktioniert ohne Claude Code/StudioBrain-Server; getrennte Entwicklungs- und Welt-Speicherdaten.
- Belege aus tatsächlichen UE PIE/Build/Insights und Blender-/UE-Importchecks, keine erfundenen Ergebnisse.
