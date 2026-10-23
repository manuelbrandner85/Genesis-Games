# GENESIS GODMODE V3 – Inhalt und Reihenfolge

Vom Game Director am 23.10.2026 ausdrücklich genehmigt: 12 Verbesserungen zusätzlich zu den 10 V2-Konzepten und GAMEFORGE 03 (50 Living World Funktionen). V2 erhalten, 24 Agenten mit V3-Gates erweitert, 7 neue Skills ergänzt = 18 Skills. Keine zweite Agenten-/Spielengine.

## Zuerst lesen

1. `START_HIER_V3.md`
2. `GENESIS_CLAUDE_CODE_MASTERPROMPT_V3.md`
3. `CLAUDE.md`
4. `docs/godmode_v3/GOLDSTANDARD_SLICE_2026.md`
5. `docs/godmode_v3/verbesserungen/V3-01*` bis `V3-12*`
6. `docs/godmode_v3/CANON_AND_SPOILER_PROTECTION.md`
7. Original Living World 03 und V2-Dokumentation.

## Programmatisch vorbereitet

- 24 `.claude/agents/genesis-*.md`.
- 18 Skills insgesamt (V2: 11, V3: +7).
- Existierende Windows-Hooks, Verbot riskanter Befehle und Protokollierung.
- V3 Installer `tools/v3/install_v3.py` (nur fehlende Dateien, niemals blindes Überschreiben).
- Paketcheck, Status-/QA-Gatechecker, Canon-SHA Baseline und Blender-/Unreal-Audit-Skripte; diese führen keine unautorisierten externen Aktionen aus.
- 12 ausführliche V3-Designs, 48 testbare Nachweisfälle, 9 übergreifende Goldstandard-Gates.

## Nicht im ZIP / nicht bewiesen

- Kein fertig produziertes Spiel, keine wirklichen High-End-Modelle, keine finalen Referenzbilder oder synchronisierte Dialoge.
- Original-Storyquellen C00–C21, J00–J24 und GAMEFORGE 01/02 können fehlen; Story SourceVault und Freigabe sind `BLOCKED_SOURCE` bis Originalfund.
- Keine lokal getestete Unreal-/Blender-Verbindung. Die enthaltenen Skripte sind statisch in Python getestet, aber Engine-Python muss auf dem Entwicklungs-PC getestet werden.
- Keine gültigen Benchmarks, Spieltests oder Build-Artefakte; Gates alle `NOT_RUN`.

Unreal-Python ist ausschließlich Editor-/Automatisierungstechnik, Spiel-Runtime muss in C++/Blueprint erfolgen. Offizielle Dokumentation: https://dev.epicgames.com/documentation/unreal-engine/scripting-the-unreal-editor-using-python ; Blender: https://docs.blender.org/api/main/info_tips_and_tricks.html ; Claude Code: https://code.claude.com/docs/en/sub-agents und https://code.claude.com/docs/en/skills
