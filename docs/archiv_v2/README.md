# GENESIS – ULTIMATE CLAUDE CODE ÜBERGABE V2

**Aktualisierung 23.10.2026.** Alle zehn vorgeschlagenen Verbesserungen wurden ausdrücklich mit JA bestätigt. Dies ist das **neue** Übergabepaket, welches das alte Claude-Code-Paket ergänzt, es nicht durch Grok ersetzt.

## Neu: nicht nur eine Rollensammlung
- 10 umfangreiche, getrennte Verbesserungs-Spezifikationen mit Funktionen, Implementierungsarchitektur, Artefakten, Tests und Abnahmekriterien.
- 24 echte Claude-Code-Unteragenten-Dateien `.claude/agents/*.md` plus bisherige 24 ausführliche Rollenprofile in `agents/`.
- 11 Skills unter `.claude/skills/*/SKILL.md`, die als `/genesis-...` ausgeführt werden können, wenn Claude sie tatsächlich lädt.
- Windows PowerShell PreToolUse/PostToolUse Hooks in `.claude/settings.json` und `.claude/hooks/`; vor Nutzung in echter Claude-Code-Installation testen. Hooks ersetzen keinen Repo-/Systemschutz.
- lokaler Dry-run Installer `tools/install_into_repo.py`, 50er GAMEFORGE-Matrix, Missionen 12, `tools/qa/verify_package.py`, `tools/qa/render_status.py`.
- Blender-Geometrie-Audit, realer Sechs-Ansichten-Rendereffekt bei bestehendem Mesh, Unreal-Assetimport für statische FBX in Editor-Umgebung, versions-/toolabhängiges Preflight.
- Ursprüngliche 50-Funktionen-MD bleibt mit identischem SHA-256 bytegetreu erhalten.

## Warnung über echte Fähigkeiten
Dieses Paket **hat nicht** selbst Blender oder Unreal auf deinem Windows-Rechner gestartet, **hat keine** fotorealistischen Charaktere erzeugt, **hat keinen** Unreal-Build oder Gameplay/Visual-QA durchgeführt und **hat keine** Original-Storybibel C00–C21 als vollständige Bytes beigefügt. Die Bots sind konfiguriert, aber nicht automatisch aktiv oder unbegrenzt parallel lauffähig. Fotorealismus benötigt eine reale Modell-/Referenz-/Artist-Pipeline und menschliche Abnahme.

## Start
`START_HIER.md` → `docs/produktion/CLI_BEISPIELE_WINDOWS.md` → `GENESIS_CLAUDE_CODE_MASTERPROMPT_V2.md`. Im Zielrepo unbedingt vorhandenes `CLAUDE.md` und `.claude/settings.json` manuell prüfen/zusammenführen. **Keine automatische Übernahme nach GitHub erfolgt.**
