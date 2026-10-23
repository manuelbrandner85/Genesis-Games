# GAMEFORGE GODMODE – VERBESSERUNG 03
# ULTIMATE LIVING WORLD SIMULATION GODMODE
## Vollständiger Masterprompt für Claude Code – 50 Funktionen, Unreal Engine 5, AION 2026 und GENESIS

**Entscheidung:** JA – vom Nutzer bestätigt am 23.10.2026.  
**Status:** Vollständige technische Entwicklungs- und Übergabespezifikation, **keine bereits installierte oder getestete Implementierung**.  
**Abhängigkeiten:** Verbesserung 01 – Autonomous Studio Brain GODMODE; Verbesserung 02 – Ultimate Character Creation 4.0 GODMODE.  
**Ziel:** Eine große, glaubwürdig lebendige, dauerhaft konsistente, performant simulierte Open World mit intelligenten NPCs, Beziehungen, Arbeit, Gesellschaft, Tierwelt, Ökosystemen, Wetter und spürbaren Folgen von Spielerhandlungen.

> **WICHTIG:** Dieser Auftrag erweitert die BESTEHENDEN Spiele und Systeme. Er ist ausdrücklich **kein neues Spiel**, keine neue Spielbibel, keine zweite Agentenplattform und keine Garantie für automatisch erreichbare AAA+-Qualität. Beginne mit echten Systemprüfungen, einem Vertical Slice und nachweisbaren Tests.

---

## 1. Auftrag und unveränderliche Regeln

Du bist **Claude Code** und handelst als technische Produktionsleitung von GAMEFORGE. Erstelle die **Ultimate Living World Simulation GODMODE Engine** als wiederverwendbares Modul, das vollständig durch das vorhandene Autonomous Studio Brain koordiniert wird.

1. **Bestehende Spielbibeln und Freigaben schützen.** AION 2026 und GENESIS behalten ihre jeweiligen Storys, Regeln, Figuren, Zeiten und bereits genehmigten Designs. Vor jedem Eingriff aktuelle freigegebene Dateien und Versionen feststellen; niemals aus einer Promptbeschreibung allein eine vollständige Spielbibel erfinden.
2. **AION:** Götter, Bosskämpfe, Kreaturen und Reaktionen der Gegenwartswelt nach der genehmigten AION-Bibel realisieren; keine neuen Götter, Regeln oder Story-Ereignisse eigenmächtig festlegen.
3. **GENESIS:** Zuletzt bestätigten Projektstand verwenden: erstes Leben startet 2026, die Welt entwickelt sich während des Spielens fortlaufend; Tod, Jenseits und freiwillige Wiedergeburt nur nach dem genehmigten GENESIS-Regelwerk. Keine automatische Epochenwahl oder neue Zeitreise-Mechanik einführen.
4. **StudioBrain-Wahrheitsquelle:** Nutze die vorhandenen Job-, Freigabe-, Event-, QA-, Artefakt- und Agentenregister aus Verbesserung 01. Keine konkurrierende zweite Produktionsdatenbank und keine zweiten permanenten Agentenprofile erstellen.
5. **Character Creation 4.0:** Verwende die DNA/Referenzen/Assets aus Verbesserung 02 für glaubwürdige Figuren und Kreaturen. Die World Engine darf freigegebene Charakter-DNA nicht überschreiben.
6. **Vor Installation oder Änderung:** Read-only Prüfung von Repository, Unreal-Version, CPU/GPU/RAM/VRAM, Datenspeicher, Plugins und Projektstatus. Downloads, Plugins, Systemänderungen, kritische Datenmigrationen, Überschreiben, Push/Release nur nach meiner Freigabe.
7. **Kosten:** Lokale, kostenlose und lizenzkompatible Werkzeuge bevorzugen. Keine pro-NPC-Abo-KI, keine bezahlte Cloud-Inferenz, keine zusätzlichen API-Kosten ohne ausdrückliche Freigabe. Claude-Nutzung bleibt tarif-/limitabhängig.
8. **Keine Scheinfunktionen:** Markiere `NOT_IMPLEMENTED`, `BLOCKED`, `TEST_FAILED`, `WAITING_APPROVAL` und `DONE` nach wirklichen technischen Bedingungen. Ein Design oder Blueprint-Screenshot allein ist keine funktionsfähige Simulation.
9. **Spielende deterministisch reproduzierbar, soweit sinnvoll:** Lebenssimulation primär durch überprüfbare C++-/Blueprint-/DataAsset-Logik. KI-Agenten erzeugen und testen Inhalte während der Entwicklung, nicht ungeprüft textbasierte Spielereignisse im laufenden Spiel.
10. **Performance:** Lebenssimulation darf nicht sämtliche NPCs und Tiere auf jedem Frame berechnen. Last nach Entfernung, Relevanz und Zustand staffeln; Budget und Zielhardware messbar konfigurieren.
11. **Einfachheit:** Deutsche, verständliche Studio-Oberfläche mit Fortschritt, Zustand der Welt, Testnachweisen und Freigaben. Keine unnötige Bedienkomplexität.

---

## 2. Architektur – StudioBrain und Laufzeitsimulation getrennt

```text
Deutscher GAMEFORGE-Auftrag
          |
          v
VERBESSERUNG 01: StudioBrain (bestehend)
  Intent -> DAG-Jobs -> Scheduler -> Freigaben -> QA -> Artefaktregister
          |
          v
LivingWorld-Workflow-Plugin (Build- und Editor-Zeit)
  Lore Resolver / World Blueprint / Population Designer / Simulation Author
  -> Unreal C++ / DataAssets / StateTree / Blueprints / World Partition
  -> Map- und Content-Integration -> automatisierte Tests
          |
          v
Unreal Engine 5 – Spiel-LAUFZEIT (kein ständig nötiges Claude)
  WorldClock + Weather + Ecology + Settlement + Economy + Social Graph
  NPC State/Needs/Schedules + AI Navigation + World Events + Audio Triggers
          |
          v
Near: hochwertige Actors/Animation/Interaktion
Mid: vereinfachte AI-/Mass-/State-Updates
Far: ereignisgesteuerte aggregierte Hintergrundsimulation
          |
          v
Persistenter WorldState + SaveGame + Migrations + Replay QA
          |
          v
Messwerte, Spieltests, freigegebene Versionen -> StudioBrain QA
```

**Technische Abgrenzung:** SQLite aus Verbesserung 01 speichert die **Entwicklungsaufträge** und deren Status. Der dauerhafte Weltzustand der **ausgelieferten Spiele** wird über eine versionierte, auf Zielplattform unterstützte Runtime-Speicherlösung verwaltet (etwa Unreal SaveGame und gezielt implementierte Serialisierung). Spiele dürfen keinen laufenden StudioBrain-Server oder Claude-Prozess benötigen.

**Unreal-Bausteine auf Eignung prüfen:** World Partition, Data Layers, One File Per Actor, HLOD, PCG, StateTree, Behavior Trees, EQS, AI Perception, Smart Objects, Navigation/ZoneGraph und MassEntity/MassGameplay. Prüfe die tatsächlich installierte UE-Version und den experimentellen Status einzelner Plugins; keine ungesicherten Funktionen für Release voraussetzen. Game-Logik zur Laufzeit in C++/Blueprint, Editor-Automation nach Möglichkeit über Python/Commandlets. Benutze Unreal Insights und Stat-Profile für echte Leistungsnachweise.

---

## 3. 50 VERBINDLICHE FUNKTIONEN – mit Output und Qualitätsprüfung

### A. Kanon, Produktionsplan, Weltmodell (01–05)

**01 – World Bible Resolver**  
**Funktion:** Liest genehmigte Spielbibel, Zeitregeln, Arten, Orte und Questregeln des aktiven Projekts; Konflikte sperren die Implementierung.  
**Output/QA:** `world_canon_manifest.json` mit Quellversionen und Konfliktliste; Test gegen gesperrte Storyelemente.

**02 – World Design Blueprint**  
**Funktion:** Erstellt ein editierbares Weltkonzept mit Regionen, Siedlungen, NPC-Archtypen, Tieren, Zeitabläufen, Simulationsdichte und Spielerinteraktionen – nur soweit freigegeben.  
**Output/QA:** `world_blueprint.yaml` und Umsetzungs-DAG; Vollständigkeit/Abhängigkeiten validieren.

**03 – Persistent Entity Identity**  
**Funktion:** Vergibt global stabile IDs für NPCs, Tiere, Familien, Häuser, Geschäfte und relevante Objekte; unabhängig vom Loaded/Unloaded-Zustand.  
**Output/QA:** versioniertes Identitätsregister; keine ID-Duplikate oder verlorene Referenzen beim Streaming.

**04 – Simulation Rulebook & Deterministic Core**  
**Funktion:** Definiert Regeln für Weltzeit, Bedürfnisse, Beziehungen, Wirtschaft, Zufallsquellen, Prioritäten und Ereignisreihenfolgen.  
**Output/QA:** testbare Regeldefinitionen mit Seeds, Tickstrategien und Konfliktauflösung; gleiche Ausgangslage liefert erwartbar nachvollziehbare Ergebnisse.

**05 – Scenario & World Presets**  
**Funktion:** Unterschiedliche Konfigurationen für AION, GENESIS und neue Spiele, ohne die Simulation zu kopieren oder die Geschichten zu vermischen.  
**Output/QA:** getrennte `WorldProfile`-Assets und Schema-Validator; projektfremde Inhalte werden zurückgewiesen.

### B. Zeit, Wetter, Jahreszeiten, Umwelt (06–10)

**06 – Game Time & Calendar Engine**  
**Funktion:** Steuert Spielzeit, Tageswechsel, Pause, Zeitraffer und Kalendereinträge nach Spielregeln; einheitliche Zeitbasis für NPCs, Quests und Wetter.  
**Output/QA:** `WorldClockSubsystem` und Zeitereignisse; Pause, Ladefortsetzung und Grenztage testen.

**07 – Day/Night Behavior Sync**  
**Funktion:** Verknüpft Tageszeiten mit Licht, Siedlungsbetrieb, Arbeit, Schlaf, Tieraktivität und Audio; Übergänge bleiben synchron.  
**Output/QA:** Datenprofile und Beispielszenen; Tag-Nacht-Wechsel ohne steckenbleibende NPCs.

**08 – Climate & Weather State Machine**  
**Funktion:** Konfigurierbares Wetter mit Zonen, Regen, Wind, Temperatur, Wolken, Gewitter und plausiblen Übergängen statt zufälliger Sprünge.  
**Output/QA:** Wetterzustände, reproduzierbare Wetter-Sequenzen und Effektauslöser; Profil-/Kanonprüfung.

**09 – Seasonal Environment Logic**  
**Funktion:** Optionale Jahreszeiten steuern Vegetation, Aktivitätsmuster, Tiere, Ernte und Umgebungsgeräusche; nur wenn vom Spiel vorgesehen.  
**Output/QA:** DataAssets, Sicht-/Gameplaytests je Saison; GENESIS-Zeitregeln unverändert.

**10 – Environmental Consequence Engine**  
**Funktion:** Regen/Nässe, Trockenheit, Sturm und Temperatur beeinflussen Wege, Geräusche, Verhalten und gegebenenfalls Gameplay-Eigenschaften.  
**Output/QA:** Ereignisgraphen und Zustandsdaten; keine Widersprüche zwischen visueller und physikalischer Umwelt.

### C. NPC-Identität, Bedürfnisse, Tagesabläufe (11–15)

**11 – NPC DNA & Identity Binding**  
**Funktion:** Verknüpft NPC-ID, Character-DNA, Optik, Stimme, Rolle, Fähigkeiten und Weltgeschichte ohne Identitätswechsel beim Laden.  
**Output/QA:** `NpcProfile` und Bindings; Charakter bleibt nach Neustart und Streaming identisch.

**12 – Needs & Motivation Model**  
**Funktion:** Modelliert passende Bedürfnisse wie Ruhe, Nahrung, Sicherheit, soziale Kontakte, Arbeit und individuelle Ziele ohne teure generative Laufzeit-KI.  
**Output/QA:** Datengetriebene Prioritätsregeln; Belastungs- und Grenzwerttests.

**13 – Daily Schedule Planner**  
**Funktion:** NPCs haben nachvollziehbare, veränderbare Pläne für Schlaf, Arbeit, Wege, Pausen, Freizeit und besondere Ereignisse.  
**Output/QA:** Schedule DataAssets mit Zeitfenstern; Zeitkonflikte und unerreichbare Ziele erkennen.

**14 – Contextual NPC Decision System**  
**Funktion:** StateTree/BehaviorTree/Utility-Regeln wählen Aktionen nach Bedürfnissen, Tagesplan, Gefahr, Beziehung und Questzustand.  
**Output/QA:** wiederholbare AI-Testfälle; NPCs verlassen blockierte Zustände und reagieren korrekt.

**15 – Smart Interactions & Occupancy**  
**Funktion:** Betten, Arbeitsplätze, Stühle, Türen, Werkzeuge und Marktstände als reservierbare interaktive Orte modellieren.  
**Output/QA:** Smart-Object-/Interaktionsdaten und Reservierungsprüfungen; zwei NPCs belegen nicht denselben exklusiven Platz.

### D. Sozialleben, Familie, Erinnerungen (16–20)

**16 – Relationship Graph**  
**Funktion:** Persistente, nachvollziehbare Beziehungen wie Bekanntschaft, Freundschaft, Rivalität, Familie und Vertrauen – gemäß Spielbibel.  
**Output/QA:** gerichteter Sozialgraph mit Regelprüfungen; keine unbeabsichtigten widersprüchlichen Familienbeziehungen.

**17 – Family & Household Life**  
**Funktion:** Familien, Haushalte, Zusammenleben, Partnerschaften, Lebensphasen und Vermächtnis nur im vorgesehenen GENESIS-/anderen Spielumfang.  
**Output/QA:** Familien- und Haushaltsdaten, Genealogie-Tests; keine ungewollten GENESIS-Storyänderungen.

**18 – NPC Memory & Reputation**  
**Funktion:** NPCs merken sich wichtige Spieleraktionen als kompakte Ereignisse, gewichten diese und reagieren auf Ruf/Vertrauen.  
**Output/QA:** begrenztes Event-/Memory-Modell mit Herkunft, Ablauf und Folgen; Speicherung und Vergessen testen.

**19 – Dialogue Context & Voice Handoff**  
**Funktion:** Verbindet Sozialstatus, Questzustand und Erinnerung mit vorhandener Dialog-/Voice-Produktion; vorproduzierte natürliche Gespräche statt Pflicht zur bezahlten Laufzeit-LLM.  
**Output/QA:** Dialogue Context API, Untertitel/Audio-IDs und Fallbacks; keine widersprüchlichen Antworten.

**20 – Social Event Director**  
**Funktion:** Begegnungen, Feiern, Konflikte, Hilfeleistungen und spontane Alltagssituationen unter Berücksichtigung sozialer Beziehungen erzeugen.  
**Output/QA:** kontrollierte Event-Templates, Conditions und Testfälle; erzählerische Verbote beachten.

### E. Gesellschaft, Arbeit, Siedlungen, Wirtschaft (21–25)

**21 – Profession & Workplace Engine**  
**Funktion:** Berufe, Zuständigkeiten, Arbeitszeiten, Produktionsmöglichkeiten und passende Werkzeuge für NPCs definieren.  
**Output/QA:** Berufsprofile und Job-Scheduler; kein NPC gleichzeitig an zwei exklusiven Arbeitsorten.

**22 – Resource & Production Chains**  
**Funktion:** Für vorgesehene Spielsysteme einfache Versorgungsketten von Rohstoffen bis Produkten umsetzen; Produktion/Einkauf nur aus verfügbaren Ressourcen.  
**Output/QA:** Mengenbilanzen und Tests auf Erhaltung, Grenzen und Überlauf.

**23 – Market & Price Simulation**  
**Funktion:** Eine konfigurierbare, begrenzte Spielwirtschaft für Angebot/Nachfrage, Preise und Handel; keine frei halluzinierten Zahlen.  
**Output/QA:** überprüfbare mathematische Regeln, Inflations-/Exploit-/Stabilitätstests.

**24 – Settlement Services & Infrastructure**  
**Funktion:** Öffnungszeiten, Wohnhäuser, öffentliche Orte, Versorgung, Erreichbarkeit und Zustandsänderungen von Siedlungen verknüpfen.  
**Output/QA:** Siedlungsregister, Infrastrukturdiagramm und Tests für gesperrte/zerstörte Wege.

**25 – Society & Faction Response**  
**Funktion:** Fraktionen, Sicherheit, Reaktionen auf Spielerentscheidungen und regionale Ereignisse modellieren, soweit von der Story gedeckt.  
**Output/QA:** Event-to-Reputation-Regeln; Kanon- und Balancing-Tests.

### F. Tiere, Pflanzen, Ökosysteme (26–30)

**26 – Animal Behavior Profiles**  
**Funktion:** Arten mit Revieren, Ernährung, Schlaf, Flucht, Gruppenverhalten und Tagesaktivität als datengetriebene Profile.  
**Output/QA:** `SpeciesProfile` und Beobachtungstests; keine unangemessene Einheits-KI für alle Tiere.

**27 – Wildlife Populations & Migration**  
**Funktion:** Tiergruppen populationsbasiert nach Biomen und Jahreszeiten simulieren; nahe Tiere als echte Actors, entfernte als Aggregate.  
**Output/QA:** Biom-/Populationsdaten und LOD-Tests; keine unendlichen Spawns.

**28 – Ecosystem Dependencies**  
**Funktion:** Vereinfachte Nahrungsketten, Lebensräume und Bestandsgrenzen implementieren, ohne vollständige wissenschaftliche Ökologie vorzutäuschen.  
**Output/QA:** stabile Modellgleichungen, Szenariotests über viele In-Game-Tage.

**29 – Vegetation Growth & Biome Change**  
**Funktion:** Wachstumszustände, saisonale Vegetation, Ressourcenerholung und optional langfristige Landschaftsfolgen.  
**Output/QA:** PCG-/DataAsset-Verknüpfung; Streaming/SaveGame-Tests.

**30 – Environmental Audio & Wildlife Sound Triggers**  
**Funktion:** Tierlaute, Wind, Wetter, Wasser, Stadtbetrieb und regionale Ambiences an tatsächlich vorhandene Audio-Assets und Zustände koppeln.  
**Output/QA:** MetaSound-/SoundCue-/Audio-Ereignisse, Hör- und Performanceprüfung.

### G. Spielereinfluss, Story, Quests, Ereignisse (31–35)

**31 – Player Action Consequence Graph**  
**Funktion:** Interaktionen, Kämpfe, Rettungen, Handel und Entscheidungen als überprüfbare Zustandsänderungen verarbeiten.  
**Output/QA:** Event-Ketten, Before/After-State und Wiederholungstests; keine doppelte Ereignisverarbeitung.

**32 – Quest & World-State Synchronization**  
**Funktion:** Quests lesen und schreiben definierte Weltzustände; NPCs und Umwelt reagieren auf Missionsfortschritt.  
**Output/QA:** versionierte Quest-World-Contracts; Hauptquests bleiben frei von Softlocks.

**33 – Dynamic Local Events**  
**Funktion:** Wetterereignisse, Konflikte, Händlerankunft, Tierbewegungen und anderes als kuratierte lokale Vorfälle planen.  
**Output/QA:** Event-Templates mit Cooldowns, Bedingungen und Ausschlussregeln; Spam- und Wiederholungstests.

**34 – Regional Persistent Change**  
**Funktion:** Zerstörung, Reparaturen, kontrollierte Wiederaufbauten, geöffnete Wege und Folgen bleiben bei Rückkehr sichtbar.  
**Output/QA:** Region-Patches im WorldState; Save/Load/Streaming-Konsistenz.

**35 – Story-Safe Emergence Director**  
**Funktion:** Kleine emergente Geschehnisse erzeugen, ohne festgeschriebene Story, Figurenidentität oder genehmigte GENESIS-/AION-Regeln zu verletzen.  
**Output/QA:** Canon-Policy-Validator und Konfliktquarantäne; Freigabe bei neuen kanonischen Ereignissen.

### H. Navigation, Verkehr, Kampfreaktion, Weltinszenierung (36–40)

**36 – Navigation & Path Recovery**  
**Funktion:** Navigation Mesh/Smart Links/ZoneGraph je Eignung nutzen; blockierte Wege, Staus und unerreichbare Ziele erkennen.  
**Output/QA:** Wegfindungstests samt Recovery-Regeln; kein dauerhaft feststeckender NPC.

**37 – Crowd & Density Simulation**  
**Funktion:** Nahe Figuren hochwertig animieren; mittlere/weite Gruppen ressourcensparend darstellen; MassEntity nur bei passender UE-Version/Pluginstabilität.  
**Output/QA:** Szenen mit konfigurierbarer Dichte und Messdaten, keine durchgängig volle Actor-KI.

**38 – Traffic & Vehicle Life**  
**Funktion:** Verkehr, Routen, Park-/Haltevorgänge und Fahrzeuginteraktionen nur für Spiele/Zonen mit entsprechender Freigabe.  
**Output/QA:** Fahrzeugzustände und Routingtests; AION-/GENESIS-spezifische Aktivierung.

**39 – Combat & Threat Awareness**  
**Funktion:** NPCs/Tiere reagieren auf Gefahren, Kämpfe, Geräusche, Fluchtwege und sichere Orte; verbindet vorhandene Combat- und AI-Agenten.  
**Output/QA:** Perception-/Reaktionsszenarien; keine unpassenden Zivilisten-Boss-AI-Profile.

**40 – World Presentation & Cinematic Events**  
**Funktion:** Sichtbare Mimik, Gestik, Sitz-/Arbeitsanimationen, Licht und Audio synchronisieren; wichtige Szenen an Cinematic-/Character-Pipelines geben.  
**Output/QA:** echte In-Engine-Demos und Timingtests.

### I. Speichern, Streaming, Simulationstiefe, Leistung (41–45)

**41 – Persistent World State & Versioned Saves**  
**Funktion:** NPC-ID, Beziehungen, Weltzeit, Regionen, Fraktionen, relevante Ressourcen und Queständerungen versioniert sichern; Schema-Migration planen.  
**Output/QA:** SaveGame-/Serializer-Tests mit Save/Load und Upgrade-Pfaden.

**42 – Multi-Tier Simulation LOD**  
**Funktion:** Near = vollständige Actor-/Animations-/Interaktionssimulation; Mid = reduzierte Entscheidungsintervalle; Far = aggregierte Ereignisfortschreibung.  
**Output/QA:** Distanz-/Relevanzprofile und Seamless-Handoff-Tests, kein Identitätsverlust.

**43 – World Partition & Streaming Bridge**  
**Funktion:** Weltzellen mit persistenter Entity Registry, Data Layers und HLOD verknüpfen; Darstellung streamen, Simulationszustand separat verwalten.  
**Output/QA:** Ein-/Austritts- und Teleport-Tests, keine verlorenen oder duplizierten NPCs.

**44 – Simulation Budget Governor**  
**Funktion:** CPU/GPU/RAM, Tickkosten, NPC-Zahl, Eventrate und KI-Aufwand anhand konfigurierbarer Performanceziele begrenzen; dynamisch degradieren.  
**Output/QA:** `sim_perf_report.json`, Unreal-Insights-Traces und FPS-/Frame-Time-Messwerte auf realer Zielhardware.

**45 – Offline/Time-Skip Event Reconciliation**  
**Funktion:** Während Schnellreise, Schlaf, Todes-/Wiedergeburtsabläufen oder Ladeunterbrechungen relevante Weltzeit kontrolliert nachführen; nur nach genehmigten Spielregeln.  
**Output/QA:** Replay- und Zeitsprungtests; keine unbeschränkte Vollsimulation jedes vergangenen Einzelereignisses.

### J. Produktionssteuerung, Debugging, Prüfungen, Release (46–50)

**46 – StudioBrain Workflow Integration**  
**Funktion:** Alle Weltaufgaben als versionierte DAG-Jobs mit Projekt-ID, Bibelrevision, Agentenzuweisung, Kosten-/Ressourcenlimits, Artefakten und Wiederaufnahme in Verbesserung 01 registrieren.  
**Output/QA:** echte Jobläufe in bestehender Datenbank; keine zweite Scheduler-Instanz.

**47 – Agent Responsibility & Handoff Contracts**  
**Funktion:** Die 42 vorhandenen Agenten nach Zuständigkeit orchestrieren (Story 05, System 09, World 15, NPC 22, Open World 24, Integration 21/25, Performance 26, Audio 27–42, QA 29/30).  
**Output/QA:** versionierte Ein-/Ausgabeverträge und Datei-Eigentümer; parallele Schreibkonflikte werden verhindert.

**48 – Living World Debug & Observatory**  
**Funktion:** Deutsche Debuganzeige für Weltzeit, Wetter, Regionen, NPC-Status, Wege, soziale Verbindungen, Tierpopulation, Weltänderungen, Streaming und Ressourcen.  
**Output/QA:** Livewerte nur aus tatsächlicher Spiel-/Build-Telemetrie, nicht aus erfundenen UI-Daten.

**49 – Automated World Simulation QA**  
**Funktion:** Unit-, Integrations-, Save/Load-, Streaming-, Chaos-/Long-Run- und Performanceprüfungen automatisieren, inklusive Worst-Case-Dichte und Quest-Rückwirkungen.  
**Output/QA:** echte Testlogs, reproduzierbare Seeds, Fehlerfälle, Screenshots/Traces und Ampelstatus; keine erfundenen Passes.

**50 – Vertical Slice & Production Readiness Gate**  
**Funktion:** Nach Freigabe zuerst eine kleine Region mit Tageswechsel, mindestens mehreren funktional unterschiedlichen NPC-Rollen, Arbeitsort, Dialog, Tierwelt, Wetter, Persistenz und Performanceprofil liefern.  
**Output/QA:** lauffähige Unreal-Demokarte, nachweisbare Testprotokolle, Blockerliste und ausdrückliche Abnahme vor World-Scale-Ausbau.

---

## 4. Konkrete Service-Schnittstellen und Laufzeitmodelle

### Kernmodule (keine parallel konkurrierenden Systeme)

- `WorldCanonAdapter`: Weltbibel lesen, Lock-/Approval-Regeln prüfen.
- `WorldDesignWorkflow`: StudioBrain-Jobs in Produktionsreihenfolge anlegen.
- `WorldClockSubsystem`: Spielzeit, Tages-/Zeitereignisse und Zeitfortschritt.
- `WorldStateSubsystem`: stabile Entitäten, Weltzustand, SaveGame, Migrations.
- `NpcSimulationSubsystem`: Profile, Bedürfnisse, Aktionen und Simulationsstufen.
- `SocialGraphSubsystem`: Beziehungen, Familien, Erinnerungen und Ruf.
- `EconomySubsystem`: Berufe, Handel, Ressourcen und Siedlungsdienste.
- `EcologySubsystem`: Tiere, Biome, Pflanzen und Populationen.
- `WeatherSubsystem`: Wetter und davon abhängige Spielereignisse.
- `WorldEventBus`: typsichere Events, idempotente Verarbeitung, Persistenz.
- `SimulationLODScheduler`: Near/Mid/Far, Budget-Grenzen, Pausierung.
- `WorldStreamingAdapter`: World-Partition-Zellen ↔ Entity Registry ↔ Actor-Lebenszyklen.
- `WorldAudioAdapter`: Audio-Auslöser statt neue TTS-/Musikengine.
- `WorldQAGates`: reproduzierbare Prüfungen, reale Telemetrie.

**Schnittstellenvertrag je Modul:** `initialize(config)`, `validate()`, `tick(sim_time, budget)`, `emit(event)`, `snapshot()`, `restore(state, schema_version)`, `collect_metrics()` – nur implementieren, soweit zur tatsächlichen Unreal-Architektur passend. Stabile Entity-IDs, versionierte Datenformate, dokumentierte Ownership und Laufzeitbudgets sind verbindlich.

### Minimales versioniertes Datenmodell (Beispiel, an echtes Projekt anpassen)

```json
{
  "schema_version": 1,
  "project_id": "AION-2026",
  "world_save_id": "example-save",
  "game_time": {"day": 12, "hour": 14, "minute": 30},
  "rng_streams": {"weather_seed": 42, "npc_seed": 7},
  "regions": {"region_alpha": {"weather": "cloudy", "world_flags": []}},
  "entities": {
    "npc_001": {
      "profile_ref": "npc_profile_001",
      "region_id": "region_alpha",
      "lod_state": "far",
      "schedule_state": "working",
      "health_state": "healthy",
      "relationship_refs": [],
      "memory_refs": []
    }
  },
  "events_processed": ["event_0001"]
}
```

*Das JSON ist ein Schemabeispiel, kein tatsächliches existierendes Savegame oder ein festgelegtes AION-Design. Datenformate, Lizenzen und Beispiel-NPCs sind je Spiel zu prüfen.*

### Technische Persistenzregeln

- Trenne Entwicklungs-Jobs in StudioBrain von Runtime-Spielständen.
- Speichere nicht jeden Actor oder jeden Frame. Lege nur relevante persistente Änderungen und rekonstruierbare Basiszustände ab.
- Nutze stabile IDs statt flüchtiger Actor-Pointer.
- Speichere Canon-Version, Save-Schema-Version, Build-Version und nötige Migrationsinformationen.
- Events brauchen Idempotenzschlüssel, damit ein Ladevorgang keine doppelten Verkäufe, Geburten, Tode oder Questabschlüsse auslöst.
- Für große Weltstände inkrementelle Snapshots und sichere Wiederherstellung konzipieren; nicht pauschal garantieren, ohne Plattformtests.

---

## 5. Steuerung der 42 bestätigten Agenten

Keine neuen 42 parallelen Claude-Prozesse erstellen. Wiederverwende die existierenden Rollendefinitionen:

| Verantwortungsbereich | Rollen | Prüf-/Übergabeanforderung |
|---|---|---|
| Steuerung & Architektur | 01, 02, 03, 25 | Jobs, Architekturfreigabe, Artefakt-DAG |
| Kanon, Missionen & Regeln | 04, 05, 06, 09 | Story-Lock, Quest-State-Contracts |
| Siedlungen, Biome, Figuren | 11–15, 17–20 | Artist-Brief, DNA, lizenzierte Assets |
| Runtime-Technik | 21, 22, 23, 24 | Getestete UE-C++/Blueprint-Systeme |
| Performance | 26 | Unreal Insights, Lasttests |
| Musik, Stimme, Weltgeräusche | 27, 28, 33–42 | Tonzustand, Events, gemessene Audiolast |
| QA & Rechte | 29, 30, 32 | Tests, Lizenzen, Freigaben |
| Builds | 31 | überprüfbarer Spielbuild |

Übergabe: `task_id`, `project_id`, `canon_revision`, `input_artifacts`, `expected_outputs`, `changed_files`, `acceptance_tests`, `dependencies`, `assigned_role`, `status`, `logs`, `artifacts_sha256`, `next_action`. Jobs werden nur durch die StudioBrain-QA-Gates abgeschlossen, nicht durch eine Selbsteinschätzung des Agenten.

### Abhängigkeiten am Beispiel „ein Dorf wird lebendig“

```text
Kanon und World Blueprint
    -> Dorf-/Biomdaten -> NPC-Profile & Berufe
    -> Wege & Smart Objects -> Tagespläne / StateTree
    -> Social/Memory -> Dialogzustände / Audioverknüpfung
    -> Tierpopulation / Wetter -> Sicht-/Klangreaktionen
    -> Save/Load / Streaming / Simulation LOD
    -> QA-Testregion / Profiling / Creative Review
    -> Freigabe und kontrollierte Integration
```

---

## 6. Tests und nachweisbare Abnahmekriterien

**Implementiere mindestens die folgenden Testfälle als ausführbare Tests oder reproduzierbare Testpläne mit Belegen:**

1. Spielbibelkonflikt wird blockiert, keine stillschweigende Neuschreibung.
2. AION-/GENESIS-Weltdaten lassen sich nicht vermischen.
3. 24-Stunden-NPC-Tagesplan läuft ohne dauerhafte Zustandsblockade.
4. Zwei NPCs reservieren nicht dasselbe exklusive Smart Object.
5. Navigation findet bei gesperrtem Weg eine Alternative oder definiert einen klaren Fallback.
6. NPC reagiert auf Gefahr und kehrt anschließend kontrolliert in einen Alltag zurück.
7. Beziehung und Spielerreputation bleiben nach Save/Load erhalten.
8. Dialogauswahl widerspricht dem gespeicherten Quest-/Sozialzustand nicht.
9. Siedlungsöffnung/-schließung folgt Spielzeit und Kontext.
10. Handel produziert keine negativen, doppelten oder unbegründeten Ressourcen.
11. Biome unterstützen unterschiedliche Tier-/Vegetationsprofile.
12. Tierpopulation explodiert bei langem Simulationslauf nicht unkontrolliert.
13. Regen führt zu passenden Audio-/Visual-/Gameplay-Änderungen.
14. Tag-/Nacht-Wechsel synchronisiert Beleuchtung, NPC-Verhalten und Sound.
15. Region verlassen, entladen, zurückkehren: dieselben relevanten NPC-Identitäten.
16. Teleport/Schnellreise lädt Ziele ohne NPC-Duplikation.
17. Nach Spielneustart bleibt zerstörter/reparierter Weg im richtigen Zustand.
18. Zeitraffer erzeugt nachvollziehbare, nicht doppelt ausgeführte Ereignisse.
19. Vorhandener Questabschluss kann nicht mehrfach belohnt werden.
20. NPC- oder Familienereignis entsteht nicht gegen gesperrte GENESIS-Regeln.
21. Fernsimulation verbraucht weniger Ressourcen als Vollsimulation vergleichbarer Gruppen.
22. Übergang Near/Mid/Far führt zu keinen Sprüngen im gespeicherten Zustandsmodell.
23. 1, 10, 100 und skalierte NPC-/Tierlasten anhand echter Hardwareprofile vergleichen (Zahlen sind **Testszenarien**, keine Performanceversprechen).
24. Unreal Insights liefert CPU-/Frame-Time-/Memory-Messungen der Testregion.
25. Bild und Sound bleiben unter Wetter-/NPC-Wechseln synchron.
26. Langer Stresstest über mehrere simulierte Spieltage und Spielstand-Wiederaufnahme.
27. Kein Produktionsjob wird nach Claude-Limit fälschlich als abgeschlossen markiert.
28. Ein unterbrochener StudioBrain-Job setzt mit versionierten Artefakten kontrolliert fort.
29. Nicht genehmigte Storyänderung erzeugt Freigabesperre.
30. Ein realer Unreal-Build oder PIE-Test mit protokollierten Ergebnissen ist erforderlich, bevor `DONE` gesetzt wird.

**Qualitätsmetrik:** Ziele für FPS, Frametimes, Simulation-Budget, Tier-/NPC-Zahl, maximale Eventlatenz, SaveGame-Größe und Ladezeit anhand der tatsächlichen Zielhardware bzw. Zielplattform mit dem Nutzer festlegen. Keine pauschalen „60 FPS mit Tausenden NPCs“ behaupten.

**Abnahme eines Vertical Slice:** Mindestens eine begehbare Region mit NPC-Tagesablauf, Arbeit, Smart Object, Dialogreaktion, Tierwelt, Wetter, Audio, gespeichertem Weltzustand und Near/Mid/Far-Simulation. Dazu saubere Tests, relevante Traces und ein verständlicher Bericht. Erst danach Projektgröße und Simulationsdichte erhöhen.

---

## 7. Konkrete Umsetzungsphasen für Claude Code

**Phase 0 – Read-only Bestandsaufnahme:** Repositories, Spielbibelrevisionen, GAMEFORGE StudioBrain/Character 4.0, vorhandene UE-Version/Plugins, Hardware und QA-Bestand erfassen. Projektrisiken und Lücken zeigen, nichts installieren/überschreiben.

**Phase 1 – Architektur und Freigabe:** Benötigte Module, existierende Komponenten, Dateikonflikte, Kostenfreiheit, Lizenz-/Versionsfragen und SaveGame-Migrationsstrategie definieren. Nutzerfreigaben einholen.

**Phase 2 – Kleiner funktionsfähiger Kern:** Zeit, WorldState, NPC-ID, erster Tagesablauf, Interaktionspunkt, Speichern/Laden, World-Event-Bus. Echte C++-/Blueprint-Dateien und Tests erstellen.

**Phase 3 – Weltleben:** Mehrere NPC-Typen, Arbeitsorte, soziale Beziehungen, einfache Ressourcen, Tiere, Wetter, Audioereignisse und Questkopplung hinzufügen.

**Phase 4 – Open-World-Skalierung:** World Partition, Data Layers, Entity Registry, Simulation-LOD, Mid-/Far-Aggregate, Belastungstests und Recovery implementieren.

**Phase 5 – Vertical Slice:** Mindestens ein Dorf/Ort bzw. eine geeignete AION-Region als begehbare Demo mit Spielzeit, sozialen Reaktionen, Siedlungsleben, Tierwelt, Wetter, Sound und echten Tests bereitstellen.

**Phase 6 – QA und kontrollierte Erweiterung:** Regression, Langzeitsimulation, In-Engine-Profiling, SaveGame-Migration, Creative Review, Freigabe. Erst danach weitere Regionen/Spielsysteme.

**Reihenfolge:** Bei vorhandenen bereits funktionsfähigen Modulen keine zweite Version entwickeln. Design und Testplan dürfen keine erfolgreich abgeschlossene Implementierung vortäuschen.

---

## 8. Sofort ausführbarer Übergabeauftrag

**CLAUDE CODE, BEGINNE JETZT MIT FOLGENDEM AUFTRAG:**

> Entwickle die **Ultimate Living World Simulation GODMODE Engine** mit den oben spezifizierten 50 Funktionen als Erweiterung des bestehenden GAMEFORGE-Systems. Nutze die bereits bestätigten Verbesserungen 01 (Autonomous Studio Brain) und 02 (Ultimate Character Creation 4.0) sowie die vorhandenen 42 Agentenrollen. Untersuche zuerst read-only das tatsächliche Repository, die genehmigten Spielbibeln und die installierte Unreal-/Blender-/Claude-Umgebung; dokumentiere fehlende Teile und Versionsunterschiede. Bewahre AION und GENESIS vollständig getrennt, führe keine neue GENESIS-Epochenregel ein und verändere keine Storyfreigabe. Erstelle einen versionierten DAG-Plan mit kleinen abnehmbaren Arbeitsschritten, verwende die bestehenden StudioBrain-Jobs und QA-Gates, setze die Runtime mit geeigneten Unreal-Engine-Subsystemen und testbaren C++-/Blueprint-Komponenten um. Installiere oder verändere nichts Kritisches ohne Freigabe. Baue und teste zuerst eine kleine lebendige Region mit NPCs, Berufs-/Tagesabläufen, Gesprächen, Tierwelt, Wetter, Audio, Save/Load, Streaming und Near/Mid/Far-Simulation. Sammle echte Testlogs und Profilingdaten. Melde nur belegbare Fertigstellungen. Zeige mir die tatsächlichen erstellten Dateien, Messwerte, bekannten Grenzen und nächsten Schritte auf Deutsch.

**ERFOLG IST NICHT:** 50 Stichpunkte oder hübsche Screenshots.  
**ERFOLG IST:** Ein nachweislich funktionierender, nachvollziehbarer und erweiterbarer Welt-Simulationskern in Unreal Engine, der im GAMEFORGE StudioBrain sauber verwaltet wird.

---

## 9. Offizielle technische Referenzen (bei Umsetzung gegen installierte UE-Version prüfen)

- Epic Games – World Partition: https://dev.epicgames.com/documentation/unreal-engine/world-partition-in-unreal-engine
- Epic Games – Data Layers: https://dev.epicgames.com/documentation/unreal-engine/world-partition---data-layers-in-unreal-engine
- Epic Games – Hierarchical LOD: https://dev.epicgames.com/documentation/unreal-engine/world-partition---hierarchical-level-of-detail-in-unreal-engine
- Epic Games – MassEntity: https://dev.epicgames.com/documentation/unreal-engine/mass-entity-in-unreal-engine
- Epic Games – StateTree: https://dev.epicgames.com/documentation/unreal-engine/overview-of-state-tree-in-unreal-engine
- Epic Games – Smart Objects: https://dev.epicgames.com/documentation/unreal-engine/smart-objects-in-unreal-engine
- Epic Games – PCG: https://dev.epicgames.com/documentation/unreal-engine/procedural-content-generation-framework-in-unreal-engine
- Epic Games – Unreal Performance Profiling: https://dev.epicgames.com/documentation/unreal-engine/introduction-to-performance-profiling-and-configuration-in-unreal-engine

**ENDE DES MASTERPROMPTS – VERBESSERUNG 03**
