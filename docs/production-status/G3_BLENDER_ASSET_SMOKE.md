# G3 – Blender-Asset-Smoketest · Status: ENGINE_TESTED (Blender) · Unreal-Import offen (G4)

Datum: 2026-10-23 · Zweig `v4/neustart` · Blender 5.2.1 LTS · Cycles auf RTX 5070 (OptiX)

## Testobjekt

`SM_TechSmoke_PalletEUR` – Europalette nach EN 13698-1 (außen 1200 × 800 × 144 mm). Neutral (kein GENESIS-Kanon), mit genormten, nachmessbaren Maßen, aus echtem Werkstoff. Ein Bau-Skript erzeugt das Objekt vollständig und wiederholbar:
`blender -b --factory-startup --python tools/v4/g3/build_pallet.py -- --out ArtSource/TechSmoke/SM_TechSmoke_PalletEUR --bake 4096`

| Bauteil | Maß (mm) |
|---|---|
| Deckbretter | 5 Stück, 1200 lang, 145/100/145/100/145 breit, 22 dick |
| Querbretter | 3 Stück, 800 × 145 × 22 |
| Klötze | 9 Stück, 78 hoch; Außenreihen 145 × 100, Mittelreihe 145 × 145 |
| Bodenbretter | 3 Stück, 1200 lang, 100/145/100 breit, 22 dick |
| Nagelköpfe | 30 Stück auf dem Deck, Ø 7, 0,3 über der Oberfläche |

Bewusst nicht CAD-genau: Jedes Teil hat eine kleine Breiten-, Lage- und Drehabweichung (höchstens 0,6 mm / 0,8 mm / 0,08°). Fasen von 1,5 mm (Bretter) bzw. 2,5 mm (Klötze), gehärtete Normalen.

## Ergebnis

| Prüfung | Beleg | Ergebnis |
|---|---|---|
| Bau, Backen, Export | `docs/evidence/G3/build_log.txt`, `build_report.json` | ohne Fehler, 31 s. 2 940 Punkte, 3 400 Flächen, nur Drei- und Vierecke |
| Dateien | `ArtSource/TechSmoke/SM_TechSmoke_PalletEUR/` | `.blend` (Master mit prozeduralem Material), `Export/….fbx`, `Textures/T_…_BC.png` (sRGB), `_ORM.png` (R = AO 1,0 · G = Rauheit · B = Metall), `_N.png` (Normal Map **DirectX**, Grünkanal für Unreal umgekehrt), je 4096² |
| **Maße nach FBX-Rückimport** | `tools/v4/g3/verify_fbx.py` → `docs/evidence/G3/fbx_verify.json` | **9/9 Prüfungen bestanden:** 1201,35 × 801,80 mm (Toleranz ±3 mm), Holzhöhe **144,00 mm** (mit Nagelköpfen 144,30), Ursprung Bodenmitte, Maßstab 1 / Drehung 0, 1 UV-Kanal, eigene Normalen erhalten, keine entarteten Dreiecke, keine Vielecke |
| Texturwerte (nur belegte Fläche, 80,3 %) | `build_report.json` | Grundfarbe sRGB 100–139 (Mittel 122) – im Bereich von Nadelholz. Rauheit 0,61–0,82 (Mittel 0,71) – unbehandeltes Holz. Metall nur auf den Nägeln (0,04 % der Fläche) |
| Gebackene Texturen geprüft | Prüfszene `Review/SM_TechSmoke_PalletEUR_Review.blend` | Die Palette wurde mit **den Unreal-Texturen** gerendert (DirectX-Normal wieder umgerechnet), nicht mit dem Master-Material |
| Testrender | `docs/evidence/G3/review_render_v1.png` (erster Stand), `review_render_v2.png` (Endstand) | 1600 × 1000, Cycles, Rauschgrenze 0,01, bis 1 024 Samples, OIDN, AgX. Sonne 38° über einem physikalischen Himmel, 50 mm Vollformat aus 1,45 m Augenhöhe, f/8. Belichtung gemessen: mittlere Luminanz 0,52, 99. Perzentil 0,59, **0 % ausgebrannt** |
| Sichtbar in Blender | Blender-MCP (Blender Lab, Erweiterung „MCP“ 1.0.3) | Verbindung steht. FBX-Rückimport, Prüfszene, alle Renders liefen im sichtbaren Fenster |

## Reality Check (Prüfliste `reality-check.md`)

Version 1 (`review_render_v1.png`) **nicht bestanden**: Maserung als gleichmäßige Streifen (wie Cord), alle Bretter millimetergenau gleich, Holz einheitlich beige, Boden eine glatte Fläche ohne Fugen. Behoben durch:

- Jahresringe um einen Markkern 4–20 cm neben dem Brett, mit Faserneigung → bogenförmige Fladerung wie bei Schnittholz
- Äste
- unterschiedlich gealterte Bretter
- Teile leicht unregelmäßig gesetzt
- Beton mit Sägefugen alle 4 m, Gesteinskorn, Flecken und Rauheitsvariation

Version 2 (`review_render_v2.png`): **teilweise bestanden.**

| OK | Noch künstlich |
|---|---|
| Maßstab, Proportionen, Fasen, Kontaktschatten, Sonnenschatten, Belichtung, Farben ohne Übersättigung, Maserung und Äste, Bodenfugen, kein Game-Look | Kanten zu gleichmäßig (keine Gabelstapler-Macken, Splitter, abgeplatzten Ecken); Holz für eine gebrauchte Palette zu sauber; alle Nagelköpfe gleich; Klötze sehen wie Vollholz aus (bei echten Paletten oft Pressspan); Umgebung ist nur eine leere Fläche |

**Quality Gate:** Für den Zweck dieses Gates (DCC-Pipeline nachweisen: Maße, Export, Texturen, Achsen) reicht der Stand. **Als Spielobjekt ist die Palette nicht freigegeben.** Wird sie im Goldstandard-Slice gebraucht, müssen die Punkte rechts vorher erledigt werden.

## Nicht geprüft / offen

- **Unreal-Import (G4):** FBX und Texturen sind noch nicht in Unreal geladen. Maßstab (cm), Achsen, Nanite, Kollision und die DirectX-Normal Map sind dort noch nicht nachgewiesen.
- Keine Kollisionshülle (`UCX_`) mitgeliefert – für G4 genügt eine einfache Box-Kollision aus Unreal.
- Vor dem Commit wurde die FBX-Prüfung nicht in einer frischen Blender-Sitzung auf einem zweiten Rechner wiederholt.
