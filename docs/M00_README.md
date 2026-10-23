# GENESIS – M00 Quellen und Sicherheitsplan

Stand der Prüfung: 2026-10-22. Änderung der IDs, Abnahmen und des Blockers CON33-01: 2026-10-23. Grundlage ist das Release `handover-v62`, Asset `GENESIS_V62.zip`, und der Masterprompt `01_CLAUDE_START/MASTERPROMPT_CLAUDE_CODE.md`. Das Paket wurde außerhalb des Projektordners entpackt. ScriptLock, Register und Quelltexte sind unverändert.

## Lesereihenfolge

| Dokument | Inhalt |
|---|---|
| [M00_IST_SOLL.md](M00_IST_SOLL.md) | Was als Datei vorliegt und was der Masterprompt als Ziel nennt |
| [M00_BLOCKER.md](M00_BLOCKER.md) | CON33-01 entschieden und in PR #3 dokumentiert, Merge offen; übrige Tore |
| [M00_PRODUKTIONSPLAN.md](M00_PRODUKTIONSPLAN.md) | M00–M09 mit WorkIDs, Abhängigkeiten und Abnahme |
| [M00_INVENTAR.md](M00_INVENTAR.md) | Zählung, Prüfsummen, Sonderbefunde |
| [M00_INVENTAR_DATEIEN.csv](M00_INVENTAR_DATEIEN.csv) | Jede geprüfte Datei mit SHA256 |
| [M00_INVENTAR_ZIPS.csv](M00_INVENTAR_ZIPS.csv) | Jede ZIP der Kette mit SHA256 |
| [M00_ROLLEN.md](M00_ROLLEN.md) | Verteilung auf die fünf Rollen |

Die 38 GLB-Grundmodelle und die 38 Turnarounds liegen unter `assets/source_glb/`. Herkunft und Hashbindung stehen in `assets/source_glb/HERKUNFT.md`.

## Statuswörter

Für WorkIDs gelten nur die Wörter des Masterprompts: `PLANNED`, `FILE_CREATED`, `FILE_VALIDATED`, `INTEGRATED`, `TESTED`, `APPROVED`. Fehlende Quelldateien heißen `SOURCE_MISSING`. Offene Entscheidungen und nicht erfüllte Tore heißen `BLOCKED`.

`FILE_VALIDATED` in M00 bedeutet: eine genannte SHA256- oder Zählprüfung ist gelaufen und das Ergebnis steht in der Evidence. Das ist keine Blender-Prüfung, kein Unreal-Import und keine fachliche Abnahme.

`TESTED` und `APPROVED` vergibt dieser Lauf nicht. Unreal und Blender wurden nicht gestartet. Archivberichte unter `docs/evidence/` bleiben liegen; ihre Felder werden zitiert und nicht als neuer Lauf gewertet.

Ältere Texte `docs/STAND.md` und `docs/BESTANDSAUFNAHME_UND_PRODUKTIONSPLAN.md` behalten ihren Wortlaut. Dieses Register übernimmt ihre Formulierung „GETESTET“ nicht.
