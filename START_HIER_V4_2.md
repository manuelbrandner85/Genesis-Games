# GENESIS GODMODE 4.2 – START HIER

**Dieses ZIP enthält den vollständigen V4.1-Übergabestand PLUS die Film-/Menüerweiterung V4.2.** Es enthält nicht automatisch alle Original-Drehbuchquellen, fertig produzierte Videoclips oder die erforderlichen KI-Modelle.

1. Entpacke das ZIP auf deinem Windows-Rechner in einen **eigenen Paketordner** und öffne **Claude Code** dort.
2. Schicke ihm den folgenden Auftrag:

> Lies `CLAUDE.md`, `GENESIS_CLAUDE_CODE_MASTERPROMPT_V4_2.md`, die V4.2-50-Funktionen-MD sowie V4.1 und sämtliche verfügbaren Originalquellen. Prüfe zuerst alle Dateien, Engines und Tools im Lesemodus. Starte dann die GENESIS-Neuentwicklung unter Schutz des bisherigen Repositories. Erstelle ein funktionsfähiges Hauptmenü, Save-/Load und Einstellungen; lege anschließend eine nichtkanonische Unreal-Sequencer-Testszene an. Produziere den echten Prolog C00 und alle Original-Zwischensequenzen nur nach gültigem Story-/Shot-/Audio-Abgleich und meiner Freigabe. Stelle sicher, dass das C20-Replay exakt dieselbe C00-Aufnahme verwendet. Erzeuge Figuren/Animation/Musik/Ton mit zugelassenen kostenlosen Tools, teste echte Editor-/Gameplay-/Windows-Builds und entwickle anschließend das vollständige GENESIS weiter. Berichte auf Deutsch mit Logs, Ausgabepfaden, offenen Aufgaben und ohne erfundene Fertigmeldungen. Frage gesondert vor Downloads, Installationen, destruktiven Schritten und Veröffentlichung.

3. Das frische Projekt wird erst nach Pfad-/Freigabecheck erzeugt: `python tools/v4/init_new_game.py --target "C:\Games\GENESIS-NEW" --engine-association <LOKAL_GEPRUEFTE_VERSION>` und danach mit deiner ausdrücklichen Zustimmung dieselbe Eingabe `--apply` anhängen. Kein bestehendes Repo überschreiben.
4. Gib Claude die autorisierten vollständigen Drehbuch-/Story-/Jenseitsdateien; die enthaltene Szenenmatrix ist **kein vollständiges Originaldrehbuch**.
5. Claude soll mit `python tools/v4_2/validate_cinematic_bundle.py --root .` die Dokumentationsvertragsprüfung durchführen. `python -m unittest discover -s tools/v4_2 -p 'test_*.py'` testet Paketregeln; das ist noch **kein Unreal-Test**.
6. Prüfe die erste echte Windows-Testversion mit Hauptmenü, Prolog-Abspielung und Save/Skip/Continue persönlich. Erst nach Abnahme alle Szenen und Regionen ausbauen.
