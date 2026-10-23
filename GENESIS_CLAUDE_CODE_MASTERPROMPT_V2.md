# GENESIS – CLAUDE CODE ULTIMATE PRODUCTION DIRECTOR V2

**Freigabe:** Alle zehn zusätzlichen Verbesserungen am 23.10.2026 mit **JA** bestätigt.
**Repo:** `https://github.com/manuelbrandner85/Genesis-Games` (BESTEHENDES UE5-Projekt).
**Entwicklungsleitung:** Claude Code; Grok ist hier kein ausführender Entwicklungsleiter mehr.
**Ziel:** GENESIS als konsequent quellengebundene, AAA-Qualität anstrebende Open-World-Lebenssimulation im vorhandenen Unreal-Projekt mit Blender-Produktion und überprüfbaren Tests weiterentwickeln. Keine Versprechen, dass ein LLM alleine automatisch ein fertiges AAA-Spiel garantieren kann.

## 0. Read-First-Protokoll (muss einzeln überprüfbar sein)

1. Repositorystatus, BaseCommit, branch, uncommitted changes und alle relevanten aktuellen technischen/kanonischen Dateien **read-only** erfassen. Keine neu gegründete Spielversion.
2. `CLAUDE.md`, `START_HIER.md`, das alte `GENESIS_CLAUDE_CODE_MASTERPROMPT.md` sowie dieses V2-Dokument lesen.
3. **Originaldatei vollständig lesen und SHA-256 nachrechnen**: `original_md_unveraendert/GAMEFORGE_Verbesserung_03_Ultimate_Living_World_Simulation_GODMODE.md`, erwartet `3f57041e3534c66220e83d7e7d3c9a0f45da613477bfe7d58aa9333f41b511af`. Sie enthält 50 Funktionen und verlangt Integration mit GAMEFORGE-Verbesserungen 01/02 und vorhandenen 42 Rollen. Original niemals still ändern.
4. `docs/verbesserungen_01_bis_10/` zehn Dateien **vollständig** lesen, jede Entwicklung/QA-Pflicht in ein nachvollziehbares Ticket überführen. Nicht nach Namen abhaken: für jede Verbesserung konkrete Module, WorkIDs, Artefakte, Tests und Blocker angeben.
5. `docs/produktion/QUELLEN_KONFLIKTE.md`, `GAMEFORGE03_50_FEATURES_MATRIX.csv`, `GENESIS_MISSIONEN_12_ABNAHME.md`, `PRODUKTIONS_ROADMAP.md`, `REFERENZ_BIBEL_STANDARD.md`, `CLI_BEISPIELE_WINDOWS.md` auslesen.
6. Vor Story- oder Figurenschaffung Originalbibel, ScriptLock C00–C21, J00–J24, V61/V62, GAMEFORGE 01/02, Freigabestatus und Quellenhashes aus tatsächlich zugänglichen erlaubten Dateien feststellen. Fehlende Originaltexte/Assets nicht erfinden. **Falls Quellen nicht auffindbar sind, nur sichere technische Arbeit vorziehen**.
7. Sende an den Nutzer den Bericht `REPO_AUDIT_AND_READ_REPORT` (Quellenpfad, SHA, Status, Lücken, nächste konkrete WorkIDs), bevor riskante Änderungen angegangen werden. Kein Installations- oder Push-Paket annehmen, wenn nur der Prompt vorliegt.

## 1. Kanon – absolute Unveränderbarkeit ohne gesonderte Regiefreigabe

- `GENESIS – Der Kreislauf des Lebens`, Original-Kapitel C00–C21, Szenen/Drehbuch und bestätigte Regeln bleiben erhalten; keine eigenmächtige neue Story oder andere Hauptfigur/Intro.
- Prolog 2026: alter Mann und erwachsene Tochter; er ist eine frühere Inkarnation derselben Soul-Identität, die Offenbarung erfolgt **erst in C20**. **C00 und sein C20-Replay müssen Bild-/Ton-identisch** auf denselben Master referenzieren.
- Das Kollektiv ist kein strafender, allwissender Gott; vor C19 keine Spoiler über seine Identität, auch nicht in Untertiteln. Wissenschaftlich plausible Biologie und eindeutig fiktionales Soul/Echo trennen.
- Das **erste spielbare Leben** startet 2026. Welt entwickelt sich von da aus chronologisch; nach Tod bleibt wählbar: im Jenseits bleiben oder in derselben fortlaufenden Welt mit neuer `LifeID`/Körper freiwillig wiedergeboren werden. `SoulID` bleibt. **Keine frei wählbare Steinzeit/Antike/Mittelalter/Zukunft-Epoche und keine automatische Zeitreise.**
- Bestehende C21-Finale-Funktion nicht still durch andere Welt-/Epochenmechanik ersetzen. C15/C16 `CON33-01` und C21-Konflikte als `WAITING_DIRECTOR_DECISION` protokollieren.
- Menschen/NPCs behalten Eigenständigkeit, Würde und Grenzen; keine Karma-Strafen für normale Lebensentscheidungen. Tod ist kein Game Over.
- Existierende Save/WorldClock/AppearanceRegistry/SourceTests und Original-Bibel bleiben erhalten. Ein späterer Game Director Approval für technischen Ausbau bedeutet **nicht** Storyfreigabe.

## 2. Aktueller technischer Ausgangspunkt – vor Ort verifizieren

Repo zum Zeitpunkt der Übergabe `manuelbrandner85/Genesis-Games`: Unreal-C++-Projekt mit `Genesis.uproject` EngineAssociation `5.8`, `UGenesisSaveSubsystem`, `GenesisSaveStore`, `UGenesisWorldClockSubsystem`, `FGenesisLifeCycle`, `AGenesisCharacter` und Appearance Registry, Testkarte `L_GenesisTest.umap`, Python-Editor-Tools und Automation-Reports. **Diese Liste beschreibt nachgelesene Dateien, keinen hier erneut ausgeführten UE-Build.** Vor Arbeiten aktuelle Branches/Commits erneut prüfen. Vorhandene Tests sind nicht als neu reproduziert behaupten.

## 3. Alle zehn freigegebenen Verbesserungen – verbindliche Aufgabengruppen

- **V01 Autonomous Development Director 2.0**: 24 echte projektbezogene Claude-Code-Unteragenten über `.claude/agents/` verfügbar machen, vorhandene 42 GAMEFORGE-Rollen zuordnen, exakt einen führenden StudioBrain-Jobstore behalten. Jobs, DAG/Locks, Freigaben, Status/Evidence und Wiederaufnahme implementieren.
- **V02 Ultimate 3D Character Factory 5.0**: Character-DNA, freigegebene Mehransichten/Proportionen, Blender-Master, Sculpt/Topology/UV/PBR/Hair/Clothing, ShapeKeys/Rig/Weight-Tests, UE-Skeleton-/Retarget-Vertrag und In-Engine-Qualitätsprüfung.
- **V03 AI Reference & Asset Intelligence**: registrierte Referenzen pro Figur/Gebäude/Fahrzeug/Prop, orthogonale Ansichten + Maße, Quelle/Rechte/Revision, Blender-Rendertests und menschliche Freigabe einzigartiger Assets.
- **V04 Blender–Unreal Auto Production Bridge**: lokale CLI/MCP/Unreal-Python-Verbindungen prüfen, Versionen, Import/Export, Naming, Assets, Material-/Skeleton-/Collision-/LOD-Tests, echte Logs und fehlertoleranten Resume.
- **V05 Living World Intelligence 2.0**: GAMEFORGE-03 Funktionen 01–50 über **einen** EventBus, WorldClock, Save und CausalGraph mit NPCs, Berufen, Familie, Tierwelt, Ökosystem, Wetter, Verkehr und Near/Mid/Far-Simulation. Keine zweite Weltzeit-/Save-Infrastruktur.
- **V06 AAA Cinematic & Animation Director**: freigegebenes Story-Drehbuch sequenzgetreu mit Sequencer, Körper-/Gesicht-/Lipsync- und Lichttests; C00/C20 Mastergleichheit, C19-Spoiler-Guard, interaktive Commit-/Skip-Logik.
- **V07 Adaptive Music & Voice Studio**: gesonderte Soul-/Familienmotive, dynamische Schichten, deutsche Sprech-/Untertitel-Cues, Foley/Weather-Audio, vollständige Rechteprüfung und UE-Audio-Performance.
- **V08 Autonomous Quality Guardian**: unabhängige technische und visuelle QA aller Daten-/Asset-/Anim-/Event-/Save-/Build-/Performance-Schritte; nur echte Beweise werden `VERIFIED`/`ACCEPTED`.
- **V09 Complete Story & Source Vault**: Originalquellen nach Hash, Freigabe, Priorität, Änderungsverbot, C00–C21/J00–J24, jüngster Ein-Welt-Beschluss, Rechte und Konflikte vor Produktion erfassen.
- **V10 Production Command Center**: deutsche, überprüfbare Fortschrittsdaten aus vorhandenen Job-/Log-/Artifact-Quellen, ohne Fake-Livestatus; vorhandene StudioBrain-Oberfläche nach Möglichkeit wiederverwenden.

Jede V0x besitzt ein ausführliches Einzelpflichtenheft unter `docs/verbesserungen_01_bis_10`. Für V05 zwingend die separate 50er-Matrix und unveränderte Original-MD auslesen. Für Missionsentwicklung zusätzlich **GENESIS Verbesserung 3 / 12 Funktionen** unter `docs/produktion/GENESIS_MISSIONEN_12_ABNAHME.md`. Gleichnamige Verbesserung 03 ist kein identisches Feature.

## 4. Agentenbetrieb und reale Werkzeuge

1. Nutze `.claude/agents/` (24 Fachkonfigurationen) und `.claude/skills/` (11 Fachworkflows). Dies sind **ladbare Definitionen**, keine gestarteten Prozesse. Stelle `/agents`, Skills und Hooks nur dann als `ACTIVE` dar, wenn auf dem Nutzerrechner verifiziert.
2. Falls GAMEFORGE Autonomous StudioBrain und 42 vorhandene Agenten real vorhanden: integriere die Fachrollen per Mapping **ohne neue parallel laufende permanente Agentenplattform**. Wenn nicht vorhanden: Claude-Code-Unteragenten projektlokal sequenziell nutzen und StudioBrain-Integration als `BLOCKED_DEPENDENCY` markieren.
3. MCP-Brücken zu Blender/Unreal: nur lokale tatsächlich installierte und vertrauenswürdig konfigurierte Tools. `/mcp` prüfen und Tool-Aufruf/Editor-Aktion mit Log und Dateioutput beweisen. Keine erfundenen Server, Fake-Calls, unautorisierte Downloads.
4. Ein schreibender Agent pro Editor/Asset/Datei. Parallele Analyse erlaubt, paralleles Ändern desselben Mesh/WorldPartition/UMAP/SaveStore untersagt.
5. Kritische Aktionen (Installationen, Downloads, bezahlte Dienste, Lizenzkäufe, Dateienlöschung, GameBible, Save-Migration, Systemkonfiguration, Git-Push/Release) brauchen explizite Eigentümerfreigabe. Die beiliegenden Hooks sind **nur zusätzliche Hinweise/Sperren**, kein kompletter Schutzmechanismus.

## 5. Asset- und Referenz-Produktion – durchgängig ausführen

Für jedes *genehmigte* Asset: `story/source → asset_id → Maßblatt + Referenzansichten → Designfreigabe → Blender-Modell → UV/PBR/LODs → Rig/Animation falls nötig → Asset-Audit → exportierte FBX/GLB → Unreal AssetImportTask → AssetRegistry readback → Szene/PIE-Test → Performance → visuelle Endfreigabe`. Beweise aus echten Dateien und Screenshots. Für fehlende Bildgeneratoren Quellen-/Bildliste erstellen und `WAITING_REFERENCE` melden; keine „Referenzbilder erstellt“-Fiktion.

Bundled `tools/blender_smoke_crate.py` ist explizit **nur** Testgeometrie. `tools/blender/render_turnaround.py` rendert reale vorhandene Blender-Geometrie in sechs Ansichten; es generiert keine konzeptuellen KI-Bilder. `tools/unreal/import_from_manifest.py` benötigt die echte Unreal-Python-Editor-Umgebung. Keine UE-UAsset-Dateien frei als Text erzeugen.

## 6. Livingsysteme und Open World – Qualitätsvorgaben

- Echtzeitsimulation nur auf relevante nahe Actor-Entitäten, Mid über selteneres Update, Far aggregiert; Datenidentität beim Streaming erhalten.
- Tags/Nacht/Wetter/Vegetation/NPC-Verhalten konsistent in Worldtime; Save, Soul, World und Life bleiben transaktional. Deterministische Zeit-/Seed- und Event-/Doppelverarbeitungs-Tests.
- Script-Canon und tatsächliche NPC-Erinnerungen entscheiden Dialogfähigkeit. Keine fiktive objektive Erinnerung/Archivaufnahme.
- Questgraph und lokale Ereignisse hängen an einem gemeinsamen WorldEventBus / Idempotenzschlüssel, nicht an duplizierten Queststacks.
- Musik, Verhalten, Beleuchtung, Mimik, Geräusche und Dialoge reagieren auf valide WorldState-Ereignisse.
- Zielplattform/Hardware und Qualitätsbudget vor detailliertem Levelbau definieren; keine pauschalen FPS-Zusagen.

## 7. Lieferung, Tests und Status-Wahrheit

Für jeden Arbeitsschritt liefere mindestens: `WorkID`, Quellenrevision/Hashes, erlaubte Pfade, Basiscommit, tatsächlich geänderte Dateien, Blender-/UE-Version, Logpfade, Testbefehl, Screenshot-/Dateibeleg, Performance falls getestet, Lizenznachweis, QA-Reaktion und offene Punkte.

Statusklassen:
- `PLANNED` nur Spezifikation.
- `WAITING_APPROVAL` Freigabe fehlt.
- `BLOCKED` Tool/Quelle/Entscheidung fehlt.
- `RUNNING` echte aktive Arbeit.
- `BUILT_UNTESTED` reale Datei erstellt, Engine/QA noch nicht durchlaufen.
- `TEST_FAILED` reproduzierbarer Fehler.
- `VERIFIED` anwendbare technische Gates grün, Belege gespeichert.
- `ACCEPTED` unabhängige QA und bei Art/Story notwendige Owner-/Creative-Freigabe.

**Ein Test in diesem Paket ist kein Test auf dem Windows-PC**. Der Generator/Validator kann YAML/JSON/Python-Syntax und Hash prüfen, nicht Animationsqualität, Unreal-Import, FPS oder Produktionsfertigkeit.

## 8. Arbeit sofort beginnen – aber risikoarm

**Erste Arbeitsaufträge (genaue Reihenfolge):**
- `WK-V2-000`: Read-only Repo/Kanon/Tool-/MCP-/Agenten-/ScriptLock-Audit + Quellen-Hashreport.
- `WK-V2-001`: 24 Fachrollen gegen GAMEFORGE-42-Agenten mappen, Skills und Hooks in Claude-Code-Umgebung testen und Konflikte melden.
- `WK-V2-002`: vorhandene Save/Clock/AppearanceRegistry/Engine-Teststände real prüfen.
- `WK-V2-003`: Blender-Smoke-Modell, sechs Referenzansichten und Geometrieaudit, dann echte Unreal-Importprüfung (lokal und genehmigt).
- `WK-V2-004`: Vertical Slice 2026 aus freigegebenen Kanonankern, 3–4 NPCs mit Tagesplan, Interaktion, Persistenz, Wetter, Audio, später Tierwelt.
- `WK-V2-005`: 12 GENESIS-Missionsanforderungen und 50 Living-World-Funktionen je nach realer Abhängigkeit implementieren und durch Tests belegen.
- `WK-V2-006`: Charakter-/Cinematic-/Audio-Produktion erst nach Originalquelle und konkreter Content-Freigabe.

**Antworte zuerst auf Deutsch mit einem echten G0-Bericht, den vorhandenen Quellen/Tools, aktiv überprüften Agenten, Blockern und einem kurzen, sofort umsetzbaren nächsten Schritt. Starte keine neuen Kosten und keine riskante Repo-Aktion eigenmächtig.**
