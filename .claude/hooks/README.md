# Windows-Hooks – Installations-/Vertrauenshinweise

`settings.json` ruft `genesis_guard.ps1` (PreToolUse) und `genesis_event_log.ps1` (PostToolUse) auf. **Nicht automatisch installiert oder ausgeführt**. Windows PowerShell 5.1 und passende Claude Code Hook-Schemas auf dem Zielrechner prüfen. Wenn Windows PowerShell nicht als `powershell.exe` verfügbar ist, Pfad anpassen **nach Freigabe**.

Der Guard verweigert typische riskante Shell-Aktionen (Push, destruktive Git-Kommandos, Shell-Downloads/Installationen) und direkte Editor-Tool-Änderungen an bestimmten Kanonpfaden. Dies ist **keine vollständige Sicherheitsgrenze**: Shell-Encoding, alternative Werkzeuge und MCP-Server können es umgehen. Zusätzliche Berechtigungsregeln, isolierte Arbeitsbranches, Backups und menschliche Reviews sind Pflicht.

Der Event Logger schreibt nur Zeit/Tool/Session-ID nach `.genesis-local/hook-events.jsonl` (lokal ignorieren; keine Prompts, Secrets oder Dateiinhalte). Er behauptet keinen Live-Status, sondern protokolliert Ereignisse, die tatsächlich über diesen Hook liefen.

**Test lokal in Claude Code:** Teste zunächst einen harmlosen `Read`, eine ungefährliche Dateiänderung in einem Testbranch, anschließend eine absichtlich gesperrte Beispielaktion. Aktive Hooks über `/hooks` verifizieren. Bei nicht unterstützter PowerShell-/Hook-Version nicht behaupten, Sicherheitsmechanismus sei aktiv.
