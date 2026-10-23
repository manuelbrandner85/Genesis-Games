# GENESIS – START HIER (Claude Code, V2, 23.10.2026)

**Alle 10 neuen Verbesserungen sind genehmigt.** Die enthaltene unveränderte GAMEFORGE-03-MD (50 Funktionen) ist Pflichtquelle. GENESIS wird im **bestehenden Repo** mit Claude Code und **realen** Blender-/Unreal-Aktionen weiterentwickelt. Dies ist ein Projekt-Setup und Produktionsauftrag, **kein fertig entwickeltes Spiel**.

## Wie du auf deinem PC vorgehst
1. Das ZIP entpacken. Dein GENESIS GitHub Repo bleibt erhalten.
2. In diesem Paket die Anweisung `docs/produktion/CLI_BEISPIELE_WINDOWS.md` lesen.
3. `python tools/qa/verify_package.py` ist nur der **statische** Paketselbsttest.
4. `python tools/install_into_repo.py --repo "PFAD_ZU_GENESIS_GAMES"` zeigt **nur** an, was es kopieren würde.
5. Erst nach Kontrolle mit `--apply` ausschließlich fehlende Dateien hinzufügen. Dateien im Repo werden **niemals automatisch überschrieben**. Besonders `CLAUDE.md` muss manuell mit der Repo-Version abgeglichen werden.
6. Im Repository Claude Code starten. V2-Masterprompt lesen lassen, `/agents`, `/mcp`, `/hooks` verifizieren. Nicht annehmen, dass installierte Dienste durch Dateien allein laufen.
7. Erster Auftrag an Claude Code:

> Lies `CLAUDE.md` und `GENESIS_CLAUDE_CODE_MASTERPROMPT_V2.md` vollständig. Lies dann die 10 Verbesserungsdateien und die **komplette Original-GAMEFORGE-Living-World-MD**. Vergleiche SHA-256 und Funktionen 01–50. Prüfe read-only das bestehende GENESIS-Repository und die tatsächlichen GAMEFORGE-Agenten sowie lokale Blender-/Unreal-Verbindungen. Nutze vorhandene Systeme, ändere noch keine geschützte Story und starte keine kostenpflichtigen Dienste. Erstelle `WK-V2-000` mit echten Quellen, Konflikten, Agenten-Mapping, Tool-Status, Build-Vorbedingungen und nächstem abnehmbaren Schritt. Wenn Quellen fehlen, melde sie konkret.

## Paketinhalt
- 10 ausführliche Einzelkonzepte `docs/verbesserungen_01_bis_10`.
- 24 Claude-Code-Unteragenten `.claude/agents`, 11 aufrufbare Skills `.claude/skills`.
- Sicherheits-/Telemetrie-Hooks `.claude/hooks` plus `.claude/settings.json` für Windows; vor Nutzung real testen.
- Blender-Modellprüfung und vorhandene Modelle rendern, vorhandener Smoke-Crate-Bau, Unreal-Importer (Editor-/Plugin-abhängig).
- Matrices GENESIS-Verbesserung 3 /12 und GAMEFORGE-03 /50, Roadmap, Referenzstandard, Original-GAMEFORGE-MD bytegetreu.
- Python-Installer mit Dry-Run und **no-overwrite**, statische QA, SourceManifest, Status-HTML-Generator.

**Fehlend:** vollständiges ursprüngliches GENESIS-Story-/V61/V62-Quellenarchiv und die GAMEFORGE-01/02-Originaldokumente. Claude Code muss sie aus den autorisierten Projektquellen beziehen, bevor es davon abhängige Produktionen durchführt.
