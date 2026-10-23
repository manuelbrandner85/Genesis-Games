# GENESIS GODMODE V4 – NEUSTART, ganz einfach

**Dein Auftrag:** Claude Code entwickelt ein NEUES GENESIS-Spielprojekt von Grund auf – die alte Installation/Repository wird nicht geändert. **Die originale Geschichte und bestätigten Entscheidungen werden übernommen, nicht neu erfunden.**

## So startest du am PC

1. Paket entpacken, z. B. nach `C:\GENESIS-GODMODE-V4-PAKET`. Das ist die **Übergabe**, nicht schon das neue Spiel.
2. **Originale Quellen** (vollständige freigegebene Storybibel, C00–C21, J00–J24, Referenzen, Spielentscheidungen) lokal bereitlegen. Die vollständigen Originale sind **nicht alle im ZIP**; siehe `docs/v4/QUELLEN_UND_KANON_SICHERN.md`.
3. Öffne Claude Code in **diesem entpackten Paketordner** und gib ihm den folgenden Auftrag: `Lies CLAUDE.md und GENESIS_CLAUDE_CODE_MASTERPROMPT_V4.md vollständig. Richte anschließend mit tools/v4/init_new_game.py ein separates neues GENESIS-Unreal-Projekt ein. Beginne mit Phase G0, ohne Dateien der alten GENESIS-Installation zu verändern.`
4. Nach read-only Inventur, Freigabe und lokalem Engine-Check darf Claude das neue Projekt z. B. unter `C:\Games\Genesis-Reborn` erzeugen; **nie im alten Repo**. Python-Beispiel (erst Probelauf):
   `python tools/v4/init_new_game.py --target "C:\Games\Genesis-Reborn" --engine-association 5.8`
5. Wenn Ziel und Pfade stimmen, darf Claude mit deiner Zustimmung denselben Befehl um `--apply` ergänzen. Ohne `--apply` schreibt er nichts. Die Angabe `5.8` ist nur ein Startwert aus dem alten Repo; Claude muss deine wirklich installierte Unreal-Version feststellen.
6. In den neu angelegten Projektordner wechseln und **dort** Claude Code starten. Projekt-CLAUDE.md lädt den V4-Masterprompt.
7. Claude übernimmt deine Originalquellen unter einem freizugebenden lokalen `canon_sources/`-Pfad, erstellt Prüfsummen und sperrt Story-/Dialogänderungen.
8. Zuerst eine **technische Smoketest-Map** und einen **Goldstandard-Vertical-Slice in der Gegenwart 2026** entwickeln. Nur genehmigte Story-Elemente in die finale Spielwelt integrieren.

## Wichtig zu verstehen

- Ein `.zip` mit Prompts und Werkzeugen ist noch **kein spielbares Game**. In diesem Paket steckt ein kleines **UE-C++-Projektgrundgerüst**, das nur am Entwicklungs-PC gebaut werden kann.
- Keine automatische Installation von Blender, Unreal, Plugins oder bezahlten KI-Diensten; erst prüfen, dann fragen.
- Die 24 Agenten und alle V2-/V3-Verbesserungen bleiben im Paket; V4 ist die **höchste Startanweisung**.
- Ohne vollständige Originalbibel keine neuen endgültigen GENESIS-Szenen, Dialoge oder finale Referenzen ausdenken. Neutrale technische Tests sind erlaubt.
- Alle Änderungen finden ausschließlich im neuen Projektordner statt. Das alte Repository `manuelbrandner85/Genesis-Games` bleibt als historische Quelle erhalten und wird nur lesend untersucht.

## Die vier wichtigsten Dokumente
- `CLAUDE.md`: oberste Projektregel
- `GENESIS_CLAUDE_CODE_MASTERPROMPT_V4.md`: vollständiger Auftrag
- `docs/v4/NEUSTART_ARCHITEKTUR.md`: technische Umsetzung
- `docs/v4/QUELLEN_UND_KANON_SICHERN.md`: was Claude vor Storyarbeit wirklich benötigt
