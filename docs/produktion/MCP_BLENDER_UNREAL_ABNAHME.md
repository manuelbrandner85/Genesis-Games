# MCP-/CLI-Verbindung: überprüfbarer Integrationsvertrag für Claude Code

**Kein erfundener Server:** Dieses Paket bringt keine fertige „Blender MCP“-Serverinstallation und keinen „Unreal MCP“-Dämon mit. Es enthält die Workflows, Skripte und Tests für tatsächlich installierte Programme. Sieh `Config` und Engine-MCP-Plugins zunächst read-only durch. Verwende nur genehmigte Adapter/Server und überprüfe ihre Herkunft, Funktion, Lizenz, Netzwerkrechte und Kompatibilität.

## Verbindliche Preflight-Checks
1. Windows-Benutzer/Projektpfad und `git status` erfassen; Editor und Blender nicht gleichzeitig unkontrolliert ändern lassen.
2. `blender --version`, lokaler Blender-Pfad, `Genesis.uproject/EngineAssociation` und zugehöriger `UnrealEditor.exe`-Pfad **nachprüfen**. Nie Versionen aus einem Prompt als installiert behaupten.
3. In Claude Code `/mcp` mit tatsächlichem Servernamen durchführen. Wenn keine Server verfügbar: `BLOCKED_MCP_NOT_CONFIGURED`. CLI/Editor-Skripte sind erlaubte Alternative, keine Notwendigkeit, dubiose MCP-Software zu installieren.
4. Vor einer Verbindung prüfe Berechtigungen (Dateipfade auf GENESIS begrenzen), Autostart und Editorport. Keine Portfreigabe ins Internet und keine tokenlosen Remote-Endpoints.
5. Eine harmlose READ-Aktion je Tool (`get_active_scene`/Blender-Objektliste und Unreal-Projekt-/Map-Info) mit Antwort und Zeitstempel protokollieren.
6. Erst nach Freigabe eine Testgeometrie (TEST_SMOKE_CRATE_001) über die Schreibschnittstelle anlegen/übertragen; in UE-AssetRegistry re-laden und Screenshot im Editor beweisen.
7. Fehlersituationen prüfen: Blender geschlossen, UE geschlossen, nicht geladene Map, importiertes Duplikat, verlorene Verbindung, falsche Units und abgelaufene Berechtigungen.
8. Bei jedem Schreibvorgang `WorkID`, SourceHash, AssetID, Lock und erwarteten Output angeben. Im Fehlerfall keine Asset-Abnahme.

## Werkzeugvertrags-Tabelle
| Funktion | Erfolgsbeleg | Fehlerstatus |
|---|---|---|
| Blender CLI vorhanden | tatsächlicher `blender --version` Output | `BLOCKED_TOOL_MISSING` |
| Blender Szenensteuerung | benanntes existierendes Objekt in geöffneter `.blend` gelesen | `BLOCKED_CONNECTION` |
| Modell erzeugen | `.blend` existiert, wird erfolgreich wieder geöffnet, Mesh-Audit | `BUILT_UNTESTED` bis UE |
| Blender Referenzrender | 6 reale PNGs aus vorhandenem Modell und Render-Log | `WAITING_REFERENCE` für nicht vorhandene Konzeptbilder |
| Export | FBX/GLB existiert und Importattribute geprüft | `TEST_FAILED` |
| Unreal Python/MCP | echter Editor-Log und AssetRegistry-Readback | `BLOCKED_TOOL_MISSING` |
| Unreal Gameplay | echter PIE- und ggf. Standalone-Lauf | `TEST_FAILED` oder `NOT_RUN` |
| Performance | Unreal Insights Trace auf bekannter Hardware | `NOT_RUN` bis gemessen |

## MCP-Konfiguration nur wenn Server verifiziert
Project-scope `.mcp.json` ist grundsätzlich von Claude Code unterstützt. **Nicht** ungetestete Beispielserver anlegen, denn das könnte im Projekt auf eine nicht existierende Binärdatei verweisen. Claude soll nach Tool-Audit eine reale `.mcp.json` mit dem **exakten lokalen Command, Args und sicheren ENV-Variablen** vorbereiten, dem Besitzer zeigen und erst nach Freigabe speichern. Jeder Server muss minimal benötigte Rechte besitzen, keinen pauschalen System-/Netzwerkzugriff.

## Skript-Alternative, wenn MCP nicht verfügbar
- `tools/pipeline/preflight.py`: Version/Quelle/Platzhalter-Lücken, read-only.
- `tools/pipeline/run_asset_pipeline.py`: einfache Smokegeometrie über Blender CLI; nur mit `--execute`.
- `tools/blender/asset_audit.py`, `render_turnaround.py`: echte `.blend`-Datei und Geometrie notwendig.
- `tools/unreal/import_from_manifest.py`: in echter Unreal-Python-Umgebung mit `GENESIS_ASSET_MANIFEST` ausführen.
- Fehlende Editor-/Blender-Umgebung → `BLOCKED_TOOL_MISSING`, kein synthetischer Erfolg.
