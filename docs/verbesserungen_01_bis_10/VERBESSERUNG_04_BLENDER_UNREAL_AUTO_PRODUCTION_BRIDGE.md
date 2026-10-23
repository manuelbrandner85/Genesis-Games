# GENESIS – Verbesserung 04: Blender-Unreal Auto Production Bridge

**Bestätigt:** JA zu allen zehn Verbesserungen am 23.10.2026.
**Status:** geplanter, fachlich freigegebener Entwicklungsumfang; keine hier erfolgte UE-Implementierung.
**Leitziel:** Ein reproduzierbarer, überprüfbarer Asset-Transfer mit Versions-, Maße-, Material-, Skeleton- und Importtests.
**Gültigkeit:** nur bestehendes `manuelbrandner85/Genesis-Games`, Claude Code als Entwicklungsleitung, keine Story-Umschreibung.

### Produktionsfunktionen
1. Lokal installierte Blender-Version und `blender --version` verifizieren; UE-Version aus Projektdatei und Editor-Binärpfad vergleichen.
2. `/mcp` tatsächlich prüfen; keine erfundenen Blender-/Unreal-MCP-Server, keine beispielhaften Zugangsdaten aktivieren.
3. Unterbrechbare Pipeline `REFERENCED → MODELED → AUDITED → EXPORTED → IMPORTED → VALIDATED → ACCEPTED`.
4. Quelle bleibt `.blend`, exportierte `.fbx` oder `.glb` und Manifest sind abgeleitete Dateien; kein Export ohne nachvollziehbaren Master.
5. Statische Assets mit Metern/Zentimetern, Pivot, Axis, Applied transforms, UV, Materialslots, Kollision, Mesh-Zuweisung prüfen.
6. Charaktere separat behandeln: Skeleton/Armature, bind pose, Skinning, Animationsclips, Bone-Names, Face Morphs und AnimBP.
7. Unreal-Python-Import via Editor/Commandlet, tatsächliches Asset-Registry-Vorkommen validieren.
8. Assetziele in `/Game/Genesis/...`, ohne Pseudopfade oder private Systempfade festzucodieren.
9. Sichere Wiederholbarkeit: ein Importauftrag pro Asset/Revision, deterministische Dateinamen, keine stillen Überschreibungen.
10. Logs mit absolutem Eingangs-/Ausgangspfad und Toolversion; vorhandene Fehlermeldungen weitergeben, statt Erfolg zu simulieren.
11. Editor-Lock: höchstens ein schreibender UE-Editor/MCP-Prozess; vorgegebene Hardwarekapazität respektieren.
12. LOD/Nanite/Texture Streaming und GPU-Speicher im UE-Projektprofil testen, nicht blind überall einschalten.
13. Failure Recovery: bei fehlendem Tool `BLOCKED_TOOL_MISSING`, fehlender Datei `BLOCKED_SOURCE`, fehlerhaftem Import `TEST_FAILED`.
14. Keine Installation/Download/Plugin-Änderung ohne Freigabe; freie Plugins nach Lizenzprüfung.
15. Referenzvergleich via reproduzierbare Blender-Renderings und In-Engine-Screenshots, kein Proxy als AAA-Asset bezeichnen.

### Implementationsdateien
`tools/pipeline/asset_manifest.py`, `tools/blender/asset_audit.py`, `tools/blender/render_turnaround.py`, `tools/unreal/import_from_manifest.py`, `tools/pipeline/preflight.py`, `tools/pipeline/run_asset_pipeline.py`. Auf lokalem Windows-PC zuerst mit einem ungefährlichen Testobjekt vollständig ausführen, danach Charakter-/Levelproduktion.

### Technischer Produktionsauftrag
Arbeite mit dem vorhandenen Repo, GAMEFORGE StudioBrain und Character Creation 4.0, sofern tatsächlich vorhanden. Ermittle Basiscommit, freigegebene Quellen und installierte Werkzeuge. Dokumentiere Architektur, konkrete Dateien, Tests und Evidenz. Führe nur genehmigte ungefährliche Schritte aus; für riskante Änderungen explizite Freigabe. Übergebe jeden Arbeitsschritt an unabhängige QA. `NOT_IMPLEMENTED` bleibt sichtbar, bis ein echter Editor-/Runtime-Nachweis vorliegt.

### Reale Pipeline-Architektur
**Editor orchestriert nicht sich selbst:** Hauptprozess erzeugt verifizierte Aufträge. Blender arbeitet nur mit lokalen `.blend`-Masterfiles und schreibt Export plus Report; Unreal führt Import/Aktualisierung nur in einer exklusiven Editor-Sitzung durch. Zwischen Editorprogrammen stehen ein Manifest, Datei-Hashes und definierte Kollisionsregeln. Engine-Plugins und MCP-Server werden nie „auf Verdacht“ angenommen.

**Manifest-Felder:** `asset_id`, `input_ref_hash`, `blender_master`, `geometry_report`, `output_fbx`, `output_glb`, `unit_scale`, `pivot`, `material_slot_names`, `lod_data`, `collision_mode`, `target_ue_path`, `imported_object_paths`, `editor_log`, `qa_status`. Die enthaltenen Python-Beispielskripte sind bewusst Standardbausteine. Charakter-Skinning, Animationsexport, Groom und Nanite brauchen eigene, gegen installierte UE-Version verifizierte Export-/Importerweiterungen; diese sind als zusätzliche Aufträge ausgewiesen und nicht fertig gelöst.

**Idempotenz:** Wenn Quelle und Asset-ID/Revision unverändert sind, muss der zweite Import entweder einen nachvollziehbar identischen Zustand bestätigen oder geschützt stoppen. Bei anderem Hash darf keine stille Überschreibung passieren. Asset-Paths und `.uasset`-Dateien nicht manuell als Text generieren oder verschieben; Unreal Editor-Asset-API nutzen.

**QA-Fälle:** A1 Blender CLI Version; A2 echte `.blend` erfolgreich gespeichert/geladen; A3 Mesh Audit; A4 FBX/GLB-Hash; A5 UE-Importlog; A6 AssetRegistry-Readback; A7 Sichtprüfung in Spielkarte; A8 Material/Kollision/Skeleton korrekt; A9 Wiederholung ohne Duplikat; A10 Unterbrechung ohne Assetverlust.

### Abhängigkeiten / nächste Umsetzung
Mindestens einen realen Testgegenstand durch Blender→UE importieren bevor ein Hero-Asset gebaut wird. WorkIDs dürfen erst nach Architektur-/Kanonabgleich in reale Dateiedits umgesetzt werden.
