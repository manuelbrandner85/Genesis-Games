# GENESIS – Start hier (GODMODE 3.0)

Alle zwölf Verbesserungen sind genehmigt; dieses ZIP enthält deren Planung plus praktische Konfiguration und Hilfsskripte. **Es ersetzt kein fertig gebautes Spiel** und ist nicht automatisch im vorhandenen GitHub-Repository installiert.

1. ZIP entpacken.
2. `python tools/v3/verify_v3_package.py` im Paketordner ausführen.
3. `python tools/v3/install_v3.py --repo "C:\Pfad\Genesis-Games"` (DRY RUN).
4. Falls gewünscht **nach Prüfung**: denselben Befehl mit `--apply`, um nur fehlende Dateien hinzuzufügen; Konflikte manuell mergen, niemals blind überschreiben.
5. Claude Code im bestehenden GENESIS-Repo öffnen, den Inhalt von `GENESIS_CLAUDE_CODE_MASTERPROMPT_V3.md` übergeben, alle V2/V3-Dokumente auslesen lassen.
6. Auftrag `WK-V3-G0` zuerst als read-only Bestandsaufnahme, dann nach Quellen-/Werkzeug-Freigabe G0–G9 Goldstandard-Slice; Blender/Unreal real testen. Vorhandene Savegames und Story sind geschützt.

Ausführlicher: `docs/godmode_v3/QUICK_START_WINDOWS.md`.
