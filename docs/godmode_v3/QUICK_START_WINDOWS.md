# START HIER – Windows / Claude Code / GENESIS GODMODE V3

## Übergabe ohne Überschreiben
1. V3 ZIP entpacken. **Nichts** in deinem lokalen GENESIS-Projekt automatisch ersetzen lassen. Das Repo ist `manuelbrandner85/Genesis-Games`; lokaler Projektordner muss eine echte `Genesis.uproject` und `.git` enthalten.
2. Im entpackten V3-Ordner `python tools/v3/verify_v3_package.py` ausführen; das prüft **nur das Paket**.
3. `python tools/v3/install_v3.py --repo "C:\Pfad\zu\Genesis-Games"` für DRY RUN; zeigt fehlende und abweichende Dateien.
4. **Nach Kontrolle** mit `--apply` ausschließlich fehlende Dateien kopieren. Abweichende Original-/V2-Dateien bleiben **unverändert**. **Besonders wichtig:** Bestehende `.claude/settings.json`, `CLAUDE.md` und Agenten enthalten dann möglicherweise noch V2-Anweisungen; Änderungen manuell diffen/zusammenführen (im entpackten Paket bleiben V3-Vorlagen). Nicht ohne Review blind ersetzen.
5. Claude Code in GENESIS starten, auf sichere Einstellungen achten (kein `bypassPermissions`), Masterprompt V3 in den Chat geben. `/agents`, `/mcp`, Skills und Hooks überprüfen. Agentenrollen in der Datei sind keine laufenden Botprozesse.
6. Claude muss den lokalen Codebestand, ScriptLock/Quellenstände, Hardware, Blender- und UE-Version vor Eingriff echt prüfen. Fehlt das originale Skript, Feature nur konzeptuell bis zur Freigabe bearbeiten.
7. Erster Auftrag `WK-V3-G0`: Source-Vault und bestehende GENESIS-Systeme lesen, Goldstandard-Slice als freigabefähigen Plan mit echten G0-Testartefakten abgeben. **Noch keine Story ändern, kein Git pushen.**

## Nach freigegebenem G0
Für Blender-Assetprüfungen beispielsweise: `blender -b "pfad\master.blend" --python tools/v3/blender_scene_audit.py -- --out "pfad\audit.json"`. Das Skript lädt nur ein vorhandenes Modell und protokolliert Fakten. Unreal-Python muss im installierten Unreal-Editor laufen, nicht als normales Python-Modul.

Teststatus aus diesem ZIP ≠ lokaler Spieltest. Das ZIP kann den Benutzerrechner nicht fernsteuern; erst mit lokal eingerichteter Claude Code-/MCP-/Engine-Anbindung sind echte Aktionen möglich.
