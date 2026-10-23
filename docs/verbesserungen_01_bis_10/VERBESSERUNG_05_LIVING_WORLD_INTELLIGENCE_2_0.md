# GENESIS – Verbesserung 05: Living World Intelligence 2.0

**Bestätigt:** JA zu allen zehn Verbesserungen am 23.10.2026.
**Status:** geplanter, fachlich freigegebener Entwicklungsumfang; keine hier erfolgte UE-Implementierung.
**Leitziel:** Die 50 bestätigten GAMEFORGE-03-Funktionen als nachweislich persistente Lebenssimulation ohne zweiten Weltzeit-/Save-Kern.
**Gültigkeit:** nur bestehendes `manuelbrandner85/Genesis-Games`, Claude Code als Entwicklungsleitung, keine Story-Umschreibung.

### Produktionsfunktionen
1. **Alle 50 Punkte** aus der unveränderten Originaldatei einzeln in `GAMEFORGE03_50_FEATURES_MATRIX.csv` inventarisieren; Quelle, Owner, UE-Modul, Test, Freigabe.
2. Vorhandene `UGenesisWorldClockSubsystem`, `FGenesisLifeCycle`, `UGenesisSaveSubsystem` und `GenesisSaveStore` zuerst lesen und Regression testen.
3. Stabile EntityIDs für NPC, Familie, Tier, Gebäude und Wirtschaft; Streaming darf keine IDs duplizieren.
4. Deterministische Event-IDs, Zufallsstreams und geordnete Konfliktauflösung; Save/Laden idempotent.
5. Near-/Mid-/Far-Simulation: relevante Figuren genau, entfernte Gruppen aggregiert, Langzeitkonsequenzen ohne massenhafte Actor-Ticks.
6. Tagespläne/Bedürfnisse/Berufe über StateTree, Smart Objects und Datenprofile nur nach geprüfter Pluginversion.
7. Sozialgraph, Haushalte, Erinnerung und Ruf ohne Karma-Balken/erzwungene Zustimmung.
8. Wirtschaft: Preise und Ressourcen bilanziert mit Grenzen; keine halluzinierten Zahlen in Runtime.
9. Tier- und Pflanzenarten aus lizenzierten, zum Gebiet passenden Artprofilen; Populations- und Saisontests.
10. Wetter/Zeit an Himmel, physikalische Umwelteffekte, Kleidung, Audio und NPC-Verhalten koppeln.
11. Verkehr/Wege mit Fallbacks bei Sperrungen, Jobs und Rettungsszenarien nur soweit Storybelege reichen.
12. Regionale Schäden, Reparaturen, Eigentum und Geschichten persistieren.
13. Lange Zeitsprünge und freiwillige Rebirth mit Kausalgraph und Weltchronologie abstimmen.
14. Simulation Engine läuft im fertigen Spiel **ohne** Claude Code, Grok, Server-Abo oder StudioBrain-Jobdatenbank.
15. Performancebudgets aus Unreal Insights und Systemhardware bestimmen, keine unbewiesenen Frame-Zusagen.
16. Kontextsensitive Dialoge nur zu real vorhandenen Beziehungen/Ereignissen; deutsche Audio-Cues und Fallbacks koppeln.
17. 50 Funktionen inkrementell im Vertical Slice nachweisen; Punkte, die vom Kanon verboten sind, dokumentiert deaktivieren.

### Architektur
Worldtime/Soul/Life aus Bestand → EventBus/Kausalgraph → NPC-/Social-/Economy-/Weather-/Ecology-Systeme → Persistenzlayer → Streaming-/SimulationLODScheduler → QA/Insights. StudioBrain führt nur Entwicklungsjobs, nie Runtime-Simulationszustände.

### Abnahme
24h-Schedules, Wetterwechsel, Beziehungsfolgen nach Save/Load, 10-Tage-Simulation, Zellstreaming, Rebirth+Zeitsprung ohne Epoch Picker, simulierte regionale Folgen, belegte Last-/Speichertests. Quelle der 50 Namen unverändert.

### Technischer Produktionsauftrag
Arbeite mit dem vorhandenen Repo, GAMEFORGE StudioBrain und Character Creation 4.0, sofern tatsächlich vorhanden. Ermittle Basiscommit, freigegebene Quellen und installierte Werkzeuge. Dokumentiere Architektur, konkrete Dateien, Tests und Evidenz. Führe nur genehmigte ungefährliche Schritte aus; für riskante Änderungen explizite Freigabe. Übergebe jeden Arbeitsschritt an unabhängige QA. `NOT_IMPLEMENTED` bleibt sichtbar, bis ein echter Editor-/Runtime-Nachweis vorliegt.

### Runtime-Systemgrenzen und konkrete Verarbeitung
**Update Loop:** `WorldClock` emittiert `TimeAdvanced`; deterministischer `WorldEventBus` führt fällige Ereignisse aus, validiert Idempotenz-Keys, aktualisiert betroffene EntityStates, benachrichtigt NPC-/Wetter-/Ökologie-/Quest-Präsentation und markiert persistente Deltas. Der `SaveSubsystem` schreibt Soul/World/Life atomar. Streaming lädt nur Actor-Darstellung; NPC-Identität und Weltchronik liegen außerhalb der flüchtigen Actor-Lebenszeit. GAMEFORGE StudioBrain verwaltet dagegen Build-/Design-/QA-Aufträge **nur während der Entwicklung**.

**LOD-Konzept:** Near nutzt Actor, Navigation und Motion; Mid reduziert Tick/Sichtbarkeit und aktualisiert Interaktionen ereignisgesteuert; Far führt Zeitfenster, Arbeits-/Sozial-/Populationsergebnisse aggregiert nach, ohne jedes Einzelwesen frameweise zu animieren. Der Spieler darf beim Rückkehren keine widersprüchlichen Spawns, Tode oder Eigentumszustände sehen. Simulation muss auch mit pausierter und beschleunigter Uhr sowie langen Reisen deterministisch bleiben, soweit Story das zulässt.

**Quest-Interoperabilität:** GAMEFORGE03 Punkt 31–35 schreibt Weltzustand; GENESIS Mission 3 liest Ereignisbelege und setzt nur erlaubte Storyfolgen. Gleiche Rettungshandlung darf nicht zwei Reputation-/Questbelohnungen verursachen. Behördliche/medizinische/soziale Folgen müssen zum tatsächlichen Weltjahr und bestehenden Figurenwissen passen.

**QA-Fälle:** A1 Save/Load gleiches Weltjahr; A2 Rebirth neues Leben alte Welt; A3 NPC Tagesablauf 24h; A4 SmartObject-Doppelbelegung verhindert; A5 Beziehung bleibt; A6 Weltzelle entladen und zurück; A7 Tierpopulationsgrenzen; A8 Ressourcenbilanz; A9 10-Tage-Langlauf; A10 Tests Near/Mid/Far gegen echte Frametimes; A11 Kanonfehler sperren dynamisches Event; A12 kein Claude zur Laufzeit nötig.

### Abhängigkeiten / nächste Umsetzung
Mindestens ein begehbarer 2026-Vertical-Slice mit 3–4 NPCs statt sofortiger planetenweiter Vollsimulation. WorkIDs dürfen erst nach Architektur-/Kanonabgleich in reale Dateiedits umgesetzt werden.
