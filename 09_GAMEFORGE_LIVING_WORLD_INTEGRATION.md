# GENESIS – verbindliche Integration GAMEFORGE-Verbesserung 03

## Quelle und Entscheidung
Der Auftraggeber bestätigt GENESIS soll ab sofort durch **Claude Code** weiterentwickelt werden. Die vollständige, im ZIP enthaltene Datei `original_md_unveraendert/GAMEFORGE_Verbesserung_03_Ultimate_Living_World_Simulation_GODMODE.md` gehört zum Auftrag und muss von Claude Code **vollständig gelesen und verarbeitet** werden. Sie beschreibt 50 Funktionen der *Ultimate Living World Simulation GODMODE* mit Unreal Engine 5 und GAMEFORGE-StudioBrain. Dies ist ein genehmigtes Entwicklungsziel, **kein Beleg einer vorhandenen Installation**.

## Begriffe und Grenzen
1. `GENESIS-Verbesserung 3`: 12 Funktionen für Missionen, NPCs, Entscheidungen und Live-Ereignisse, siehe `01_KANON_UND_FEATURES.md`.
2. `GAMEFORGE-Verbesserung 03`: **50 Funktionen** der Living World Simulation, Originalfile siehe oben. Beide bleiben verbindlich, arbeiten aber über *ein* konsistentes Event- und Save-Modell.
3. GAMEFORGE Verbesserung **01** = Autonomous Studio Brain; **02** = Ultimate Character Creation 4.0. Ihre Originaldateien sind hier nicht belegt: suchen, Hash/Freigaben prüfen, Fehlstand ausdrücklich kennzeichnen.
4. AION wird in der Originaldatei als separates Wiederverwendungsziel genannt; dieser Auftrag erlaubt **keinen Zugriff mit Schreibwirkung auf AION**. Projekte bleiben strikt isoliert; generische Module nur nach freigegebener Architektur.

## Datei → Runtime-Reuse (Ist-Zustand zuerst testen)
| vorhandener GENESIS-Baustein | Living World-Verwendung | zwingende Prüfung |
|---|---|---|
| `UGenesisWorldClockSubsystem`, `FGenesisLifeCycle` | Funktionen 06,07,09,45 | nicht durch zweite Uhr ersetzen; Save/TimeSkip/Rebirth-Prüfung |
| `UGenesisSaveSubsystem`, `GenesisSaveStore`, `GenesisSaveTypes` | 03,04,16–18,31–35,41,43,45 | transaktionaler Soul/World/Life-Bundle, Migration, keine doppelt verarbeiteten Events |
| `AGenesisCharacter`, Appearance Registry | 11,40 | Charakter-DNA/ID, Proportionen, Alter und Animation kompatibel |
| `Genesis.*` Automation-/PIE-Tests | 49,50 | Bestehende Tests dürfen nicht ausfallen; echte neue Tests hinzunehmen |
| C00–C21 + J00–J24 (Originale separat) | 19,20,31–35,40 | keine erfundenen Dialoge/Quests oder Story-Reveals |
| Content/Maps-Testlevel (nur nach Editorprüfung) | 02,07–10,24,43,50 | reale `.umap`-Integrität, World Partition, keine bloße Datei-Hülle |

## 50-Funktionen-Matrix – Pflicht zum individuellen Mapping
Jede einzelne Funktion der Original-MD bekommt `ID, Bezeichnung, Originalquelle+Abschnitt, Owner/StudioBrain-Job, vorhandene UE-Komponente, Status, geplante Datei, Test, Evidence, Dependency, Approval`. Die Bereiche:

- **01–05:** Kanon, Weltentwurf, stabile Identitäten, deterministische Regeln, Spielprofile.
- **06–10:** Spielzeit, Tag/Nacht, Wetter, Jahreszeiten, Umweltfolgen.
- **11–15:** NPC-DNA, Bedürfnisse, Tagesabläufe, Entscheidungslogik, Smart Objects.
- **16–20:** Beziehungen, Haushalt/Familie, Erinnerungen, Dialoge, soziale Ereignisse.
- **21–25:** Berufe, Ressourcen, Marktpreise, Siedlungsinfrastruktur, Gesellschaft.
- **26–30:** Tierprofile, Population, Ökosystem, Pflanzen, Umwelt-Audio.
- **31–35:** Spielerfolgen, Quest-Welt-Synchronisierung, Ereignisse, regionale Änderungen, Story-Schutz.
- **36–40:** Navigation, Menschenmengen, Verkehr, Gefahrreaktion, cineastische Präsentation.
- **41–45:** persistente Welt, Simulations-LOD, Streaming, Leistungsbudget, Zeitsprünge.
- **46–50:** StudioBrain-Jobs, Agentenverträge, Debug, automatisierte QA, Vertical Slice.

`ALREADY_TESTED` nur bei replizierten Belegen, sonst `PLANNED`, `IN_PROGRESS`, `BLOCKED`, `BUILT_UNTESTED` oder `TESTED`. Bewusst deaktivierte Kanon-Funktionen nicht gegen Freigaben aktivieren (z.B. keine neu erfundene Kampfspielmechanik).

## Priorisierte Integrationskette
1. Original-MD im vollen Umfang lesen und Hash nachweisen.
2. Aktuellen Git-Commit/UE-Editor/Blender/StudioBrain lesen und Verbindungstests ausführen.
3. Bestehenden Runtime-Baustein für Zeit und Save *wiederverwenden*; Entity-IDs, versionierte Events und Teststrategie entwerfen.
4. Eine kleine begehbare Region mit unterschiedlichen NPCs, Arbeitsablauf, Witterung, mindestens einer echten Interaktion und Audio in Unreal bauen.
5. Originalquellenbelegte Mission mit GENESIS-Mission-System koppeln.
6. Pflanzen/Tiere, soziale Konsequenzen, Near/Mid/Far-Simulation ergänzen; Stress-/Langlauftests.
7. Für jedes neue relevante 3D-Asset das freigegebene Referenzblatt samt Mehransichten, `.blend`-Master, Export, Unreal-Import und Testartefakten erstellen; keine Scheingeometrie.
8. Quality Gate vor Ausweitung auf größere Welt. Laufzeitspiel darf **nicht** von einer laufenden Claude-/StudioBrain-Verbindung abhängig sein.

## Sonderschutz und Konflikte
- ScriptLock C00–C21: bleibt unverändert, sofern keine separate endgültige Regiefreigabe für konkrete storywirksame Arbeit nachweisbar.
- Chronologie 2026 und spätere Generationen, keine frei anwählbare Epoche; C21-Weltfunktion ist weiterhin kein automatischer Epoch-Picker.
- Rebirth/SoulID/WorldTime/Save: atomar und ohne idempotente Wiederholung.
- `NPC-KI` zur Laufzeit muss deterministisch/data-driven genug für Tests sein; Generierung durch Claude ist Entwicklungszeit-Tool, keine versteckte pro-NPC-API-Anbindung.
- Kostenlose lizenzkompatible Assets; Lizenzen je Asset nachweisen.
- Remotezugriff, Plugins, Downloads, Branchänderungen, Push, Löschen, migrationskritische Operationen: nur mit erforderlicher Freigabe.
