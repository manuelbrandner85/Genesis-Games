# G2 – UE-C++ kompiliert / Editor startet · Status: ENGINE_TESTED

Datum: 2026-10-23 · Zweig `v4/neustart` · Rechner: Ryzen 7 5700X, 32 GB, RTX 5070 · Unreal Engine 5.8.3 (CL 58210709)

## Ergebnis

| Prüfung | Befehl | Ergebnis | Beleg |
|---|---|---|---|
| Build `GenesisEditor Win64 Development` | `Build.bat GenesisEditor Win64 Development -Project=…\Genesis.uproject -WaitMutex` | **Succeeded**, 68 s, 10/10 Schritte (Genesis.cpp, GenesisGameMode.cpp, GenesisPrototypeCharacter.cpp). **0 Warnungen, 0 Fehler im Projektcode** | `docs/evidence/G2/build_log.txt` (SHA256 `fdb0ff67…`) |
| Modul-Binary | `Binaries/Win64/UnrealEditor-Genesis.dll` | erzeugt (SHA256 `c5f8db11…`, nicht im Repo) | – |
| Editor-Starttest ohne Grafik | `UnrealEditor-Cmd Genesis.uproject -nullrhi -unattended -nosplash -nopause -NoSound -ExecCmds="QUIT_EDITOR"` | Exit-Code 0, 52 s. Modul `Genesis` geladen, „Engine is initialized“, sauber beendet („Exiting.“) | `docs/evidence/G2/editor_start_log.txt` (SHA256 `0d6e7018…`) |
| Fehler im Editor-Log | Suche nach `Error`/`Fatal`/`Critical` | 22 Treffer, **alle** aus dem Engine-eigenen Selbsttest `UE::UnifiedErrorTest` (17× `LogAutomationTest: Error: Condition failed`, 5× `LogTemp`). **0 Fehler aus GENESIS** – gleiches Bild wie beim früheren Build auf `setup/ue58-projekt` | ebenda |
| Warnungen im Editor-Log | Suche nach `Warning:` | 1: `LogLayoutService` – Editor-Layout aus einer anderen UE-Version in der lokalen `Saved/Config`; harmlos | ebenda |

## Änderung gegenüber dem V4-Grundgerüst

`Source/Genesis.Target.cs` und `Source/GenesisEditor.Target.cs`: `BuildSettingsVersion.V5` → `BuildSettingsVersion.Latest`.
Grund: UE 5.8 bricht mit V5 ab („GenesisEditor modifies the values of properties … not allowed, as GenesisEditor has build products in common with UnrealEditor“, Exit 6). Dieselbe Einstellung lief schon beim früheren Projekt.

## Nicht geprüft / Grenzen

- **Kein Screenshot:** Start lief bewusst ohne Grafik (`-nullrhi`). Der sichtbare Editor-Start mit DX12 ist nicht belegt.
- **Kein Spieltest:** Die Startkarte ist `/Engine/Maps/Entry`; es gibt noch keine Testkarte, keine PIE-Session, keine Figur im Level (→ G5).
- **Steuerung ist Altsystem:** `GenesisPrototypeCharacter` nutzt noch `BindAxis`/`BindAction` mit Mappings aus `DefaultInput.ini`. Das Grundgerüst verlangt selbst die Umstellung auf Enhanced Input direkt nach dem ersten Build – offen.
- Der Game-Target (`Genesis Win64`) und ein gepackter Build sind nicht gebaut (→ G9).
- Reality Check: nicht anwendbar – es gibt noch keine sichtbaren Inhalte.
