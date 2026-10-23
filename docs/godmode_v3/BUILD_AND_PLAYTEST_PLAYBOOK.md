# GODMODE V3 – Build, Test, echte Fehlerprüfung

**Voraussetzung:** lokales Windows UE-C++-Projekt, EngineAssociation und UE-Version zuerst validieren; Build-Toolchain/SDK und Projekt sauber; freigegebener Git-Featurebranch. Ziel `Windows` und Toolversionen sind in Evidence zu schreiben.

## Stufen

- B01 `Build.bat GenesisEditor Win64 Development -Project=<Genesis.uproject>` – nur als geprüftes lokales Beispiel; tatsächliche installierte UE-Tool-CLI nachprüfen.
- B02 Unreal Automation Tests `Genesis.*` und Game/PIE Smoke; Enginescripts verwenden, wenn vorhandene Befehle von installierter Version akzeptiert werden. Neue Tests in `Source/Genesis/Private/Tests` statt separatem Testframework.
- B03 Unreal Editor-Python: echte Assetpfade laden, Details und UAsset-Readback dokumentieren. `tools/v3/run_local_audit.py unreal ... --execute` nur mit lokal getestetem UnrealEditor-Cmd und Editor-Python.
- B04 Cook/Build/Package Windows via Unreal AutomationTool `RunUAT BuildCookRun` in passenden Projekt-/UE-Versionen. Keine „FERTIG“-Markierung ohne ausführbare EXE, Cook-Ausgabe, Log und Installations-Test.
- B05 Launch Standalone, Input/Controller, Save/Load, NPC-/Quest-/Life-Gameplay, Streaming, Audio, Sprache und Cinematic-Gates.
- B06 Profiling: Unreal Insights/CSV Frame Time, GPU, CPU, VRAM, RAM, map load, save load, camera/bounds. Testbedingungen erfassen.
- B07 Fehlerfall: Ticket, Seed, BaseCommit, Log, wiederholbare Schritte, zuständiger Agent, Fix, erneuter Test und Regression.
- B08 Menschlicher Playtest und Story-/Creative-Review durch mindestens eine reale Person, Entscheidungen respektieren.

## Pflicht-Testfälle

1. Boot und C00→C01→Menü ohne doppelte Prologinszenierung (falls Film kanonisch freigegeben).
2. Skip während World-/Cinematic-Transition persistiert korrekte Events.
3. C19-/C20-Spoiler nicht in UI/Subtiteln vorzeitig.
4. Geburts-/Tod-/Jenseits-/Rebirth-Abbrüche sowie SaveStore-Migration und Crash.
5. NPC-Begegnung nach Speichern → Reload → Regionswechsel → Rückkehr; Identität und Erinnerung.
6. Mission mit Entscheidung, Neu-Laden, mehrfacher Trigger und Sackgassenprüfung.
7. Animations-/Interaction-Profil und Camera-Begrenzung bei mehreren Frameraten.
8. Fahrzeug-/Physics-Tests nur wenn für Slice tatsächlich freigegeben.
9. Reproduzierbarer Benchmark auf benannter GPU bei festem Wetter/Seed/Details.
10. Keine ausgelassenen Rechtsnachweise für Assets, Musik und Sprecher.

## Evidenzbeispiel (NICHT echter Test)

`{"work_id":"WK-V3-G7","status":"NOT_RUN","base_commit":null,"engine_version":null,"commands":[],"test_case_ids":[],"evidence_paths":[],"reviewer":null,"approval_id":null}`. Status niemals auf `ACCEPTED` setzen, solange echte Prüfung und Director-Freigabe fehlen.
