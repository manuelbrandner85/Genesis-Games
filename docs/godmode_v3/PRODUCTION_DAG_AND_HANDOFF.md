# V3 – Echte Produktionskette und Agentenbesitz

Auftragsfolge: Nutzerauftrag → Canon Resolver → StudioBrain WorkID → Planung/Gate → Agenten/Skills → Referenz/DNA → Blender `.blend` → Export → Unreal import/readback → Gameplay/Cinematic → Engine QA → unabhängiges Review → Benachrichtigung/Freigabe → Artefaktregister. Ein Fehler eröffnet einen neuen Reparaturauftrag, nicht `DONE`.

**Bestehende 24 Projektrollen bleiben erhalten**, ebenso GAMEFORGE 42, wenn auf dem Zielrechner tatsächlich eingerichtet. V3 erzeugt keine weiteren virtuellen Agentenprozesse und keinen Scheduler. Claude Code-Subagents sind kontextspezifische Rollen; lokale Toolprozesse führen die Arbeit aus. Gemeinsamer Editor/Blender/GPU werden **exklusiv gelockt**, kein paralleles Verändern desselben Maps-/Assets-/Editorprozesses. Scripts sind niemals Ersatz für echte Editoranbindung.

## Jobvertrag

Pflichtfelder: `work_id`, `project_id=GENESIS`, `owner_agent`, `base_commit`, `source_hashes`, `allowed_paths`, `dependencies`, `inputs`, `expected_artifacts`, `test_ids`, `reviewer`, `status`, `actual_artifacts`, `commands`, `evidence_paths`, `known_issues`, `approval_needed`. Ein Status wird erst nach realem Tool-Event gesetzt. Jedes Maschinenereignis besitzt Timestamp, Job-ID, Exitcode, Engine-Version und SHA256 des Ergebnisses.

## Schreibbesitz pro Stage

- Story & Locked Canon: `genesis-script-guardian` ausschließlich lesend, Game Director genehmigt Textänderungen.
- Concept/reference manifests: `genesis-reference-director`.
- Blender assets: `genesis-character-artist` / `genesis-environment-artist`; nur ein Editorprozess/GPU-Job.
- Rig/motion: `genesis-rigging-specialist`, `genesis-motion-specialist` in voneinander getrennten Arbeitspaketen.
- Unreal: `genesis-unreal-core` und `genesis-open-world` unter gemeinsamer Editor-Sperre.
- NPC/Missions/Life: jeweilige Fachrolle; Save-Vertrag/Schema nur zentral nach Migrationfreigabe.
- Cinematic/Audio: eigene Agenten, verknüpfte Cue-/Dialog-IDs.
- QA: `genesis-qa-release`, unabhängig von Autor, darf niemals eigene Ergebnisse voraussetzen.
- Master/Integrationsentscheidung: `genesis-master-director` im Hauptdialog, nicht parallel als schreibender Bot.

## Qualitätszustände

`SPECIFIED` = nur Plan. `BLOCKED_SOURCE` = Quelle fehlt; `BLOCKED_TOOL` = Tool nicht ausführbar; `WAITING_APPROVAL` = risikobehaftete Aktion benötigt Zustimmung; `BUILT_UNTESTED` = echte Datei ohne Enginebeleg; `ENGINE_VERIFIED` = importiert und mit echtem Runtime-/Editorbeleg; `HUMAN_REVIEWED` = Mensch hat Design/Gefühl beurteilt; `ACCEPTED` = QA und Game Director nehmen einen WorkID ab. Die Statusmaschine wird von `tools/v3/validate_evidence.py` geprüft, ohne automatisch echte QA zu ersetzen.

## Rückfall und Reparatur

Nach einem fehlgeschlagenen Test: Daten-/Logbeleg aufheben, eine konkrete Bug-ID registrieren, minimalen Code/Asset-Diff auf Featurebranch herstellen, denselben Test und Regression durchführen. Bei fehlendem Blender/UE nur `BLOCKED_TOOL`; kein simuliertes grünes Ergebnis. Upload/Push/Release, Systeminstallation, Cloudkosten oder destruktive Operationen erst nach Freigabe.
