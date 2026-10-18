# GENESIS – Asset DNA Vault: Fremd-Assets und Rechte

Jedes Asset, das nicht im Projekt selbst entstanden ist, steht hier mit Quelle, Lizenz, Nachweis, Veränderungen und Freigabestatus.

| Asset-ID | Quelle / Originalname | Urheber / Rechte | Lizenz-Nachweis | Format / Prüfsumme | Veränderungen | Projekt-Datei / Unreal | Im Repo? | Status |
|---|---|---|---|---|---|---|---|---|
| EXT-0001 Mannequin (Manny/Quinn, Skelett, Fuß-IK-Rig, Physik, Unarmed-Animationen) | Unreal Engine 5.8 Template-Inhalt `Templates/TemplateResources/High/Characters/Content/Mannequins` | Epic Games | Unreal Engine EULA (Nutzung in UE-Projekten erlaubt; Verbreitung von Engine-Inhalten nur eingeschränkt) | .uasset | keine | `/Game/Characters/Mannequins` | **nein** – wird per `Tools/Setup/Copy-EngineMannequin.ps1` aus der lokalen Engine kopiert, weil das Repo öffentlich ist | PROXY, technisch geprüft (WK-M02-002) |
| EXT-0002 Sternkarte „Deep Star Maps 2020“, `starmap_2020_8k.exr` (8192 × 4096, Äquirektangulär, Äquatorkoordinaten, RA 0 h mittig, RA nach links steigend) | NASA SVS, Item 4851: https://svs.gsfc.nasa.gov/4851 | NASA/Goddard Space Flight Center Scientific Visualization Studio; Daten: Gaia DR2 (ESA/Gaia/DPAC), Hipparcos/Tycho | SVS: „All of our content is in the public domain (unless otherwise noted)“ (https://svs.gsfc.nasa.gov/help/, abgerufen 2026-10-18); Item 4851 nennt keine Einschränkung. Gaia-Archiv: Daten frei nutzbar mit Nennung „ESA/Gaia/DPAC“ (https://cosmos.esa.int/web/gaia-users/license) | OpenEXR half-float, SHA256 `dc6c4f413e85707a29a25a9451148154554ecca2c996f84fa8f47b65ef9ff7c4` | keine an der Datei; im Material: Drehung nach Sternzeit, atmosphärische Extinktion, Eichung auf 6,8·10⁻⁵ cd/m² mittleres Sternlicht | `SourceArt/Sky/starmap_2020_8k.exr` → `/Game/Genesis/Sky/T_StarMap_2020_8k` (BC6H) | **nein** – `Tools/Setup/Get-StarMap.ps1` lädt und prüft (Git-LFS-Kontingent) | technisch geprüft (WK-M02-006); Credits müssen in den Abspann |

## Pflicht-Nennungen für den Abspann (Credits)

- Star map: NASA/Goddard Space Flight Center Scientific Visualization Studio. Gaia DR2: ESA/Gaia/DPAC.
- Unreal Engine und Mannequin-Proxy: © Epic Games (nur solange Proxy-Figuren im Spiel sind).
