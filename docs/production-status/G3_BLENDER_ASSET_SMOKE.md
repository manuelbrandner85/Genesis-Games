# G3 – Blender-Asset-Smoketest · Status: ENGINE_TESTED (Blender), Reality Check bestanden · Unreal-Import offen (G4)

Datum: 2026-10-23 · Zweig `v4/neustart` · Blender 5.2.1 LTS · Cycles auf RTX 5070 (OptiX)

## Testobjekt

`SM_TechSmoke_PalletEUR` – **gebrauchte** Europalette nach EN 13698-1 (außen 1200 × 800 × 144 mm). Neutral (kein GENESIS-Kanon), mit genormten, nachmessbaren Maßen, aus echtem Werkstoff. Ein Skript erzeugt das Objekt vollständig und wiederholbar (fester Zufallsstartwert): `tools/v4/g3/build_pallet.py`.
- Im Hintergrund: `blender -b --factory-startup --python tools/v4/g3/build_pallet.py -- --out ArtSource/TechSmoke/SM_TechSmoke_PalletEUR --bake 4096`
- Sichtbar: Die Funktionen werden Schritt für Schritt über Blender-MCP im offenen Fenster aufgerufen. So ist der Endstand entstanden.

| Bauteil | Maß (mm) |
|---|---|
| Deckbretter | 5 Stück, 1200 lang, 145/100/145/100/145 breit, 22 dick, Fichte |
| Querbretter | 3 Stück, 800 × 145 × 22, Fichte |
| Klötze | 9 Stück, 78 hoch; Außenreihen 145 × 100, Mittelreihe 145 × 145, **Pressspan** |
| Bodenbretter | 3 Stück, 1200 lang, 100/145/100 breit, 22 dick, Fichte |
| Nagelköpfe | 30 Stück auf dem Deck. **Jeder anders:** Ø 6,4–7,6, 0,05–1,8 über der Oberfläche, bis ~10° geneigt, eigener Rostgrad |

### Gebrauchsspuren

**Geometrie** (echte Boolean-Schnitte, 1 129 Bruchflächen als frisches Holz markiert):
- **Kantenmacken:** kantige Ausbrüche, entlang der Faser gestreckt; an Brettenden, Bodenbrettern (Gabelstapler) und Klotzecken
- **Endrisse:** an Deck- und Bodenbrettern
- **Splitter:** abstehend an Brettkanten, mit der Rille, aus der sie gerissen sind
- **Maßabweichungen:** leicht unregelmäßig gesetzte Teile (≤ 0,6 mm Breite, ≤ 0,8 mm Lage, ≤ 0,08° Drehung)

**Material**, gebacken in die Unreal-Texturen:
- Fichte mit Fladerung und Ästen; Bretter unterschiedlich vergraut
- Pressspan als Mosaik aus Spänen mit Rindenstücken
- dunkleres, raueres Hirnholz
- Schmutz in Fugen und Ecken (Ambient Occlusion)
- Bodenschmutz unten, Laufspuren von Wasser an senkrechten Flächen
- Gabelstapler-Abrieb unten an Klötzen und Bodenbrettern
- Staub auf dem Deck, glattgegriffene Kanten
- frisches, helleres Holz in Brüchen

## Ergebnis

| Prüfung | Beleg | Ergebnis |
|---|---|---|
| Dateien | `ArtSource/TechSmoke/SM_TechSmoke_PalletEUR/` | `.blend` (Master, prozedurales Material), `Export/….fbx`, `Textures/T_…_BC.png` (sRGB), `_ORM.png` (R = AO 1,0 · G = Rauheit · B = Metall), `_N.png` (Normal Map **DirectX**), je 4096² |
| Bauwerte | `docs/evidence/G3/build_report.json` | 4 188 Punkte, 5 758 Flächen (8 168 Dreiecke), 1 Material, 1 UV-Kanal; Backen 92 s auf der GPU |
| **Maße nach FBX-Rückimport** | `tools/v4/g3/verify_fbx.py` → `docs/evidence/G3/fbx_verify.json`, `verify_log.txt` | **10/10 bestanden:** 1202,09 × 800,96 mm (Toleranz ±3 mm), Holzhöhe **144,05 mm**, höchster Punkt 145,84 mm (Nagelköpfe/Splitter), Ursprung Bodenmitte, Maßstab 1 / Drehung 0, 1 UV-Kanal, keine entarteten Dreiecke, keine Vielecke, genau 1 Material |
| Texturwerte (belegte Fläche 79,8 %) | `build_report.json` | Grundfarbe sRGB 86–138 (Mittel 116) – Nadelholz/Pressspan. Rauheit 0,60–0,86 (Mittel 0,72). Metall nur auf Nägeln |
| Gebackene Texturen geprüft | Prüfszene `Review/SM_TechSmoke_PalletEUR_Review.blend`, Skript `tools/v4/g3/review_scene.py` | Gerendert wird die Palette **mit den Unreal-Texturen** (DirectX-Normal zurückgerechnet), nicht mit dem Master-Material |
| Gesamtansicht | `docs/evidence/G3/review_render_final.png` | 1600 × 1000, Cycles, Rauschgrenze 0,01, bis 1 024 Samples, AgX. Sonne 38° über physikalischem Himmel, 50 mm aus 1,45 m, f/8. Luminanz Mittel 0,48, 99. Perzentil 0,59, **0 % ausgebrannt** |
| 100-%-Nahaufnahme | `docs/evidence/G3/review_detail_final.png` | 50 mm aus ~0,8 m, f/5,6, auf Klotz, Brettenden und Nägel. Luminanz Mittel 0,43, **0 % ausgebrannt** |
| Sichtbar in Blender | Blender-MCP (Blender Lab „MCP“ 1.0.3) | Geometrie, Material, Backen, Export, Prüfszene und alle Renders liefen im offenen Fenster |

## Reality Check – Verlauf

| Stand | Bild | Urteil | Was nicht stimmte → was geändert wurde |
|---|---|---|---|
| v1 | `review_render_v1.png` | nicht bestanden | Maserung wie Cord, Bretter CAD-exakt, Holz einheitlich, Boden glatt → Fladerung um Markkern, Äste, Altersunterschiede, unregelmäßige Teile, Betonfugen |
| v2 | `review_render_v2.png` | teilweise | Kanten zu sauber, keine Gebrauchsspuren, Nägel gleich, Klötze Vollholz, leere Umgebung → Version 2 des Skripts mit Schäden, Pressspan, Nägeln, Gebrauchsspuren, Kies und Splittern |
| v3 | `review_render_v3.png`, `review_detail_v3.png` | nicht bestanden in der 100-%-Ansicht | Pressspan wie Tarnflecken, Kies facettiert (Low-Poly), Nägel orange, Beton ohne Poren → feine, gepresste Späne; Poren und Sandkorn im Beton; Rost gedämpft |
| v4 | `review_detail_v4.png` | nicht bestanden | Kies wie Perlen, Splitter wie Zahnstocher, Pressspan zu kontrastarm → unregelmäßiger Splitt (3D-Rauschen + Bruchflächen), spitz zulaufende Splitter |
| v5 | `review_detail_v5.png` | teilweise | Pressspan liest sich weiter wie Vollholz → führende Spanlage mit klaren Grenzen und Fugen |
| **final** | `review_render_final.png`, `review_detail_final.png` | **bestanden** | – |

### Prüfliste (Endstand)

| # | Bereich | Befund |
|---|---|---|
| 1–3 | Maßstab, Geometrie, Proportionen | OK – Normmaße, Bretter/Klötze im richtigen Verhältnis, Kies und Splitter in realer Größe |
| 4 | Kanten | OK – Fasen, Ausbrüche, Splitter, Endrisse |
| 5–6 | Materialien, Rauheit | OK – Albedo im Holzbereich, Metall nur auf Nägeln, Rauheit 0,60–0,86 mit Variation |
| 9–10 | Mikrodetail, Gebrauchsspuren | OK in der 100-%-Ansicht – Fasern, Ringe im Hirnholz, Späne, Abrieb, Staub, Kies an Fugen und Palettenrand |
| 11–13 | Licht, Schatten, Kontakt | OK – eine Sonne mit Himmel, harter Schlagschatten mit Halbschatten, Kontaktschatten unter allen Klötzen |
| 15 | Wiederholungen | OK – jedes Brett, jeder Nagel, jeder Klotz anders |
| 16–18 | Kamera, Perspektive, Schärfentiefe | OK – 50 mm Vollformat aus Augenhöhe, Schärfentiefe passend zu f/8 bzw. f/5,6 |
| 19–20 | Farben, Belichtung | OK – gemessen, nichts ausgebrannt, keine Übersättigung |
| 24 | Umgebung | OK für eine Prüfaufnahme – Betonhof mit Fugen, Flecken, Poren, Kies, Holzsplittern |
| 25–26 | Game-Look, Technik | OK – kein Bloom/Flare/Vignette, kein Rauschen, keine Artefakte |

**Quality Gate:** 1. Glaubwürdig real? **Ja.** 2. Höchste sinnvolle Qualität für ein Test-Asset? **Ja.**

**Bekannte Restpunkte, kein Blocker:**
- Das Deck ist eher leicht gebraucht als stark verschmutzt. Das ist plausibel, aber eine Ausprägung.
- Nagelköpfe lesen sich aus der Nähe dunkel. Das passt zu angelaufenem Stahl.
- Der Betonboden gehört nur zur Prüfszene und wird nicht exportiert.

## Nicht geprüft / offen

- **Unreal-Import (G4):** FBX und Texturen sind noch nicht in Unreal. Maßstab (cm), Achsen, Nanite, Kollision und DirectX-Normal sind dort noch nicht nachgewiesen.
- Kein `UCX_`-Kollisionsmesh mitgeliefert – für G4 genügt eine Box-Kollision aus Unreal.
- Ambient Occlusion für den Schmutz ist ins Grundfarbbild gebacken (gewollter Gebrauchsschmutz, kein Licht). In Unreal kommt die echte Verschattung von Lumen.
