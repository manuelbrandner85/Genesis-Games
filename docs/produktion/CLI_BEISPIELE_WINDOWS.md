# Click für Click: Windows-Integration mit Claude Code

1. ZIP entpacken. Bestehendes Repo bereits lokal geklont haben, darin muss `Genesis.uproject` liegen.
2. Im PowerShell-Terminal zuerst Python testen: `python --version`, Claude: `claude --version`, Blender: `blender --version` und UE-Editorpfad herausfinden (nichts installieren ohne Freigabe).
3. Im **Paket** starten: `python tools/qa/verify_package.py` (nur **statischer Test**, keine UE-Behauptung).
4. Im Paket vorab: `python tools/install_into_repo.py --repo "C:\\Pfad\\zu\\Genesis-Games"` (nur Ansicht, kein Copy).
5. Prüfe Dateikonflikte, besonders `.claude/settings.json` und bereits bestehende GAMEFORGE-Agenten. Danach explizit `python tools/install_into_repo.py --repo "C:\\Pfad\\zu\\Genesis-Games" --apply`. Das kopiert nur **nicht vorhandene** Dateien; es überschreibt nichts.
6. Vorhandenes `CLAUDE.md` **manuell** mit dem beiliegenden `CLAUDE.md` abgleichen – aus Sicherheitsgründen nicht automatisch ersetzen.
7. In lokalem Repo `claude` starten und mit `/agents`, `/skills`, `/mcp`, `/hooks` die echte Konfiguration prüfen; Befehle nach installierter Version.
8. Ersten Auftrag aus `START_HIER.md` geben: nur Read-only Quelleninventur und Windows-Toolcheck. Wenn Quellen fehlen, `BLOCKED_SOURCE_MISSING` dokumentieren.
9. Nur mit erlaubter Blender-Version testen: `python tools/pipeline/run_asset_pipeline.py --output "C:\\Temp\\genesis-smoke"` zeigt zuerst den Plan. Mit `--execute` wird Blender wirklich aufgerufen (vorher Erlaubnis/Temp-Pfad prüfen).
10. UE-Smoke: Originalprojekt im Unreal Editor öffnen und `tools/unreal/import_from_manifest.py` anhand des verifizierten Export-Manifests in seiner Python-Umgebung ausführen. Das Beispiel erwartet echte existierende FBX-Dateien. Import/PIE/Test-Screenshots nachweisen, nicht aus dry-run ableiten.
11. Für eine Story-Szene erst den echten freigegebenen ScriptLock vor Ort verifizieren. Fehlende Originale nicht simulieren.

**Beispiel ist keine Erfolgsgarantie:** Jede Maschine kann abweichende Pfade, Versionen oder Rechte haben. Das Paket ist noch nicht auf deinem Windows-System gestartet worden. Hooks sind keine vollständige Sicherheitsgrenze.
