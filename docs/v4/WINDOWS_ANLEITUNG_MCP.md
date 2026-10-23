# Claude Code → Blender → Unreal (Windows)

1. Lokale Programme ermitteln: `where.exe blender`, `where.exe UnrealEditor.exe`, `where.exe python`, `where.exe claude`, tatsächliche Versionen ausführen (ggf. direkte Pfade). Nichts herunterladen ohne Freigabe.
2. Claude Code `/agents` prüfen. Projektspezifische Rollen müssen vorhanden und tatsächlich ladbar sein. Skills unter `.claude/skills/` aufrufen. Python muss im Terminal vorhanden sein.
3. MCP-Server nicht anhand bloßer Dateinamen behaupten: aktive Verbindungen, Toolschemas, Berechtigungen und echte Probe-Aufrufe prüfen. Ohne MCP kann Blender auch über `blender.exe -b --python <script>` und Unreal über `UnrealEditor-Cmd.exe <uproject> -ExecutePythonScript=<file>` per CLI automatisiert werden, sofern lokale Versionen das unterstützen.
4. **Blender Smoke:** `blender -b --python tools/v4/blender_smoke_prop.py -- --output <NEUES_PROJEKT>/ArtSource/Smoke/`; tatsächliche `.blend`- und `.fbx`-Dateien kontrollieren. Nur Testwürfel, nicht GENESIS-Endmodell.
5. **Unreal-Import:** aus dem neuen Spielordner `tools/unreal/import_from_manifest.py` im **UE Editor Python Kontext** starten; vorher gültiges Manifest mit wirklichem Export anlegen. Bei Fehlern `QA_FAILED`; keine Demo-Dummy-Screenshots als Nachweis.
6. Realistisches Modell: Referenz aus originaler freigegebener Beschreibung oder erst nach Freigabe erzeugtem Design, Ansichten, Proportionsvertrag und Lizenzregister; Blender Export; UE Readback; PIE; Animation/Material/Performance- und menschlicher QC-Gate.
7. Kein Unreal-Python in einem ausgelieferten Game. Nicht mehrere Claude-Agenten gleichzeitig denselben Unreal-/Blender-Editor bedienen lassen.

**Nachprüfen:** Unreal-Python ist eine Editorfunktion (Epic Docs: https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python). Claude-Subagenten: https://support.claude.com/en/articles/14554000-claude-code-power-user-tips
