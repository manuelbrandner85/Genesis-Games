# GENESIS – Verbesserung 01: Autonomous Development Director 2.0

**Bestätigt:** JA zu allen zehn Verbesserungen am 23.10.2026.
**Status:** geplanter, fachlich freigegebener Entwicklungsumfang; keine hier erfolgte UE-Implementierung.
**Leitziel:** Ein einziger produktionsweiter Auftragseingang, reale Claude-Code-Unteragenten, verifizierte Übergaben und kein zweiter GAMEFORGE-Scheduler.
**Gültigkeit:** nur bestehendes `manuelbrandner85/Genesis-Games`, Claude Code als Entwicklungsleitung, keine Story-Umschreibung.

### Kernfunktionen
1. **Bootstrap-Audit:** Repos, Branch, GameBible, GAMEFORGE 01/02, bestehende Agenten, Claude-Version, Windows-Tools und Teststand read-only inventarisieren.
2. **Agent Registry:** alle 24 GENESIS-Fachrollen über `.claude/agents/*.md` bereitstellen, aber zuerst vorhandene GAMEFORGE-42-Agenten abgleichen; Doppelrollen deaktivieren oder nur als Unteragenten-Ersatz nutzen.
3. **DAG Work Planner:** WorkIDs, Abhängigkeiten, Prioritäten, SourceHash, QA-Gates, Dateibesitz und Abbruchpunkte auf vorhandenen StudioBrain-Aufträgen abbilden.
4. **Job Journal:** Status `PLANNED`, `WAITING_APPROVAL`, `RUNNING`, `BLOCKED`, `BUILT_UNTESTED`, `TEST_FAILED`, `VERIFIED`, `ACCEPTED`; keine Status-Hochstufung ohne Messbeleg.
5. **Ownership:** maximal ein schreibender Agent für eine Datei, ein Blender-Projekt und eine offene Unreal-Editor-Sitzung; gleichzeitiges Lesen erlaubt.
6. **Prompt Routing:** technische Aufgabe an den zuständigen Agenten, Story-Änderung an Script Guardian, Export an Integration, Freigabe an Hauptagent.
7. **Model Budget:** zuerst gezielte Suche und relevante Dateien; Kontextübergabe enthält nur IDs, Hashes, Diffs und Änderungen. Keine endlose Rekursion von Subagenten.
8. **Durable Resume:** per JSON-Arbeitspaket + Belegverzeichnis nach Abbruch fortsetzen, bevor ein teurer Job erneut ausgeführt wird.
9. **Human Approval Gates:** Einzelfreigabe bei Downloads, Plugins, Bezahl-APIs, neuer Lizenz, destruktiven Änderungen, Story, kritischer Migration, Push und Release.
10. **Unabhängige QA:** Erzeugender Agent kann seinen eigenen Job nicht akzeptieren; QA liest tatsächliche Artefakte und Testlogs.
11. **Quelle vor Interpretation:** gesperrter Kanon schlägt subjektiv attraktive Ideen; Konfliktstatus `BLOCKED_CANON_CONFLICT`.
12. **Windows-kompatibler Betrieb:** Scripts in PowerShell/Python; lokale Pfade prüfen statt behaupten; echte MCP-Verbindungen nur bei verfügbaren Servern.
13. **Ehrlicher Fortschritt:** ein Dashboard darf ausschließlich Daten aus Belegen lesen; Demo-Zähler ausdrücklich als Demo markieren.
14. **Game Isolation:** `GENESIS` und `AION` dürfen aus einer gemeinsamen Engine keine gegenseitigen Story-/Assetdaten ziehen.
15. **First Job:** nur Quelleninventur, lokale Editor-/Blender-Smokes und Vertical-Slice-Backlog; keine selbstständige Epochenänderung.

### Datenvertrag
`task_id`, `project_id=GENESIS`, `canon_revision`, `base_commit`, `owner_role`, `inputs_sha256`, `allowed_paths`, `dependencies`, `acceptance_criteria`, `test_commands`, `status`, `evidence_paths`, `approval_id`, `next_action`. Der Vertrag wird in `templates/job_contract.schema.json` validiert. Bestehende StudioBrain-DB ist führend, JSON hier nur Austausch-/Offline-Format.

### Umsetzung/Abnahme
`.claude/agents/` + `.claude/skills/` + `.claude/settings.json` sind echte Konfigurationsdateien, keine live gestarteten Prozesse. Teste in Claude Code mit `/agents`, `/mcp` und einem ausschließlich lesenden Probeauftrag. Je Output ein WorkID, hashbasierte Artefaktliste und QA-Stempel. Bei StudioBrain-Konflikt keine zweite Scheduler-Instanz aufbauen.

### Technischer Produktionsauftrag
Arbeite mit dem vorhandenen Repo, GAMEFORGE StudioBrain und Character Creation 4.0, sofern tatsächlich vorhanden. Ermittle Basiscommit, freigegebene Quellen und installierte Werkzeuge. Dokumentiere Architektur, konkrete Dateien, Tests und Evidenz. Führe nur genehmigte ungefährliche Schritte aus; für riskante Änderungen explizite Freigabe. Übergebe jeden Arbeitsschritt an unabhängige QA. `NOT_IMPLEMENTED` bleibt sichtbar, bis ein echter Editor-/Runtime-Nachweis vorliegt.

### Produktionsarchitektur: Minimal zuerst, dann skalieren
**Input:** aktueller GAMEFORGE-Agentenkatalog (falls vorhanden), tatsächliche Dateipfade, Git-SHA, Anforderungen, Originalquellen mit Hash. **Process:** Parser erzeugt `JobContract`, Abhängigkeitsauflösung verteilt die nötige Arbeit, Exclusive Resource Locks reservieren Editoren, QA nimmt Ergebnis separat ab. **Output:** Event-Journal, Job-State, Artifacts mit SHA, Nutzerbericht. **Stop:** wenn DAG-Zyklus, fehlende Freigabe, unzureichende Quelle oder paralleler Schreibbesitz festgestellt wird.

**Agent-Konfliktregel:** Claude Code darf mehrere Rollen nacheinander ausführen, aber nicht gleichzeitig denselben `.umap`-Level/Blender-Master verändern. Bestehender StudioBrain-Datenstore bleibt primär. Falls seine Daten/Software fehlen, ist ausschließlich ein offline austauschbares Job-JSON erlaubt, keine unaufgeforderte neue Datenbank. Eine generierte Agenten-MD startet keinen Prozess und gibt keine Fernsteuerung frei.

**Recovery:** Vor riskantem Schritt einen nichtdestruktiven Worktree/Branch-Plan anfertigen, aktuellen Arbeitsbaum fotografieren (Git-Diff/Status), Artefakte hashen; nach Timeout zuletzt *bestätigten* Teilschritt statt komplette Pipeline neu ausführen. Status `RUNNING` nach Abbruch auf `BLOCKED_REVIEW` oder `PLANNED_RESUME` setzen. Verifiziere Wiederanlauf mit zwei aufeinanderfolgenden identischen Task-ID-Anfragen ohne doppelten Import.

**QA-Fälle:** A1–A3 Agenten vorhanden/dedupliziert; A4 fremde Projektdatei verweigert; A5 kein zweiter StudioBrain-Jobstore; A6 gegenseitiger Schreiblock; A7 Abbruch und Resume; A8 Nutzerfreigabe blockiert kritische Schritte; A9 fehlender Test kann keinen `ACCEPTED`-Status auslösen.

### Abhängigkeiten / nächste Umsetzung
Agenten- und Aufgabenplanung auf existierendem Repo ist G0/G1; erst danach reguläre Jobvergabe. WorkIDs dürfen erst nach Architektur-/Kanonabgleich in reale Dateiedits umgesetzt werden.
