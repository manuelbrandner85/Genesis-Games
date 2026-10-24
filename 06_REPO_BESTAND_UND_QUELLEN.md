# GENESIS – bei der Übergabe überprüfter Ist-Zustand
**Direkt via GitHub-Repolesezugriff auf `main` am 23.10.2026:**
- Repository: `https://github.com/manuelbrandner85/Genesis-Games` (öffentlich, Stand ohne Schreibzugriff).
- `Genesis.uproject` `EngineAssociation: 5.8`, Module `Genesis`, Plugins StateTree, GameplayStateTree, ModelContextProtocol, AllToolsets, PythonScriptPlugin, EditorScriptingUtilities. **Plugin in Dateikonfiguration ≠ geprüfter laufender MCP-Adapter.**
- C++ Verzeichnisse `Source/Genesis/Private/{Character,Commandlets,Core,Input,Save,Tests,Time}`; passende Public-Header.
- `Config/DefaultEngine.ini`: DX12 SM6, Lumen, Raytracing, Nanite und Virtual Shadow Maps konfiguriert (Qualität/FPS nicht dadurch garantiert).
- `Content/Maps/L_GenesisTest.umap` nur ca. 130 Bytes; `DA_Proxy_Adult_M/F.uasset` je ca. 129 Bytes im GitHub-Dateibaum. Wahrscheinlich Platzhalter; lokal um echte Engine-Assets abgleichen. Kein Beleg für fertige echte Maps aus diesen Bytes.
- Dokumentationsdateien `docs/STAND.md`, `docs/BESTANDSAUFNAHME_UND_PRODUKTIONSPLAN.md`. Bericht `STAND.md` datiert 18.10.2026 und berichtet ältere lokale Tests: 6 Save Tests + Crash Tests, später Spielfigur/Steuerung/Appearance Registry, Weltuhr/LifeCycle. **Aktuellen Zustand in lokalem Build unabhängig neu prüfen.**
- README.md ist nur sehr kurz. Keine fertigen AAA-/Story-/NPC-/Mission-/Audio-/Jenseitswelten auf main belegt.

## Mitgelieferte neu bestätigte Originalquelle
- `original_md_unveraendert/GAMEFORGE_Verbesserung_03_Ultimate_Living_World_Simulation_GODMODE.md` ist **unverändert im ZIP** enthalten und muss vollständig gelesen werden. Sie ist nicht der vollständige Story-ScriptLock.

## Weitere persönliche Quelldateien (nicht im ZIP enthalten)
- `GENESIS_ScriptLock_11_Drehbuch_v1.1.md` bzw. `.docx` (22 Story-Szenen + Verträge; als *Freigabekandidat* dokumentiert).
- `GENESIS_ScriptLock_11_Pruefbericht.md` und `GENESIS_ScriptLock_11_Szenenmatrix.json`.
- `GENESIS_Kanon_Update_Eine_Welt_ab_2026.md` (neuere konkrete Epochen-Entfernungsregel und offener C21-Konflikt).
- Frühere V61/V62 Quellarchive, vollständige J00–J24-/Mission-/Assetregister nach Repo-Dokumentation möglicherweise nur lokal gespeichert.
**Wichtig:** Diese Dateien waren für Analyse teilweise lesbar, aber die Originalbytes konnten nicht als Kopie in dieses ZIP geholt werden. Der Auftraggeber muss sie Claude Code separat geben bzw. Claude Code muss mit eigenen autorisierten Quellzugriffen lesen. Ansonsten ist originale Dialog-/Shot-Reproduktion nicht vollständig möglich.

## Notwendiger erster Claude Code-Lauf
`git clone https://github.com/manuelbrandner85/Genesis-Games.git`; `git log -1 --format=fuller`; `git status`; Datei-/LFS-Inventar; Unreal-Build; Blender-MCP/CLI-Abfrage; Beispiel-Asset-Probe. Erst *danach* Ist-Soll-Lücken und Umsetzungszeitplan ableiten. Keine verworfenen Experimente auf main überschreiben.
