# Tatsächlich registrierbare Claude-Code-Rollen

- 24 Dateien in `.claude/agents/` mit gültigem YAML-Frontmatter, Werkzeug-Allowlists und eindeutiger Rolle.
- 11 Skills in `.claude/skills/<name>/SKILL.md`.
- Subagenten werden **nicht** automatisch gestartet; Claude Code stellt sie bei Projektstart bereit, sofern Version und Einstellungen dies zulassen.
- Wenn ein bestehender GAMEFORGE-42-Rollen-Agent diesen Auftrag erfüllt, statt Doppelbelegung vorhandene StudioBrain-Rolle verwenden.
- Ein schreibender Agent pro `.blend`/`.umap`/Codepfad; der Hauptagent behält Orchestrierung.
- Nutze `/agents` bzw. `/mcp` auf dem echten Windows-Entwicklungsrechner zur Prüfung.
