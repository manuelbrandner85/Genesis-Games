# V4.2 – 50 unabhängige Abnahmefälle

**Vorbereitung ist keine Engine-Abnahme.** Wo Real-Life-Tests erforderlich sind, im neuen Windows-/Unreal-Projekt nachholen.

- [ ] **Q01** 22 eindeutige Szenen-IDs C00–C21 im Index
- [ ] **Q02** Originalquellen mit Versionshash liegen vor; fehlt -> BLOCKED_SOURCE
- [ ] **Q03** C00/C20 identische Referenz zum MasterAsset
- [ ] **Q04** C00/C20 gleiche Bytes im genehmigten Masterbeweis
- [ ] **Q05** keine Offenbarung zu C19/C20 vor Freischaltung
- [ ] **Q06** Story-Skip und Normalspiel liefern denselben Commit
- [ ] **Q07** Szene läuft im Unreal Editor tatsächlich ab
- [ ] **Q08** Film-Unterbrechung → Save/Load ohne Duplikat
- [ ] **Q09** Szenen-Unterbrechung bei Absturz → sichere Wiederaufnahme
- [ ] **Q10** nach Szene Input/Kamera/WorldClock korrekt
- [ ] **Q11** fehlende Sequenz führt zu nachvollziehbarem Fallback
- [ ] **Q12** C12-Archiv nur aus belegten Momentaufnahmen
- [ ] **Q13** C14 Tod/Save korrekt atomar
- [ ] **Q14** früher Tod: keine erfundene Erwachsenenbiografie
- [ ] **Q15** C15/C16-Konflikt nicht heimlich umgeschrieben
- [ ] **Q16** C17 ohne Epochen-Picker und ohne Originalscript-Edit
- [ ] **Q17** C21-Finale-Konflikt ausgewiesen
- [ ] **Q18** Boot-Menü in Windows-Build öffnet sich
- [ ] **Q19** Neues Spiel ohne Save klappt
- [ ] **Q20** Neues Spiel fragt vor Überschreiben nach
- [ ] **Q21** Fortsetzen nur bei intaktem Save aktiv
- [ ] **Q22** defektes Save wird fehlerfrei behandelt
- [ ] **Q23** Load Slot -> korrekte Weltzeit/Soul/Life
- [ ] **Q24** Menü-Graph vollständig erreichbar
- [ ] **Q25** Controller ohne Maus bis Gameplay navigierbar
- [ ] **Q26** Focus sichtbar und nicht verloren
- [ ] **Q27** Einstellungen persistieren Neustart
- [ ] **Q28** Untertitel/Voice synchron bei Pause/Seek
- [ ] **Q29** Musik/Sprache/SFX getrennt regelbar
- [ ] **Q30** Barrierefreiheits-Optionen wirken sichtbar
- [ ] **Q31** Fotosensitivität/Effekt-reduziert Modus vorhanden
- [ ] **Q32** Abspann/Back to Menu funktioniert
- [ ] **Q33** credits vermerken Quellen/Lizenzen korrekt
- [ ] **Q34** No-placeholder-action: jeder sichtbare Button wirkt
- [ ] **Q35** Spieldatenuhr läuft nicht im Menü-Hintergrund weiter
- [ ] **Q36** Menülauf erzeugt keine persistente Änderung
- [ ] **Q37** Movie Render Queue Output real existiert
- [ ] **Q38** Filmmaster-SHA im Register
- [ ] **Q39** Cue-/Audio-/Stimmenlizenz dokumentiert
- [ ] **Q40** Dialogtext folgt genehmigter Originalquelle
- [ ] **Q41** Closeups auf Mimik/Lipsync überprüft
- [ ] **Q42** Blender-Asset/UE-Import/Animation real geprüft
- [ ] **Q43** Shot Continuity Kostüm/Props/Beleuchtung
- [ ] **Q44** Cinematics 30/60 fps Sync-Test auf Zielhardware
- [ ] **Q45** Font-/Textüberlauf bei niedriger Auflösung
- [ ] **Q46** deutscher Controller-/Tasten-Hinweis korrekt
- [ ] **Q47** UI Screenshot Review durch Menschen
- [ ] **Q48** Perf-Traces/Cook/Build-Log als Beleg
- [ ] **Q49** QA-Agent nicht identisch Implementierer
- [ ] **Q50** Director erteilt echte Endabnahme

Status je Fall: `NOT_RUN`, `BLOCKED`, `PASSED_WITH_EVIDENCE`, `FAILED`; Belege: Build-Version, Commit, Artefaktpfad, Test-Log, Screenshot/Trace und Prüfer.
