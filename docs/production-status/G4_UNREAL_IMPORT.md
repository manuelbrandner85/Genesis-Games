# G4 – Unreal-Asset-Handoff · Status: ENGINE_TESTED

Datum: 2026-10-23 · Zweig `v4/neustart` · Unreal Engine 5.8.3 (DX12, SM6, Lumen mit Hardware-Raytracing, Nanite, VSM) · RTX 5070

Asset aus G3: `ArtSource/TechSmoke/SM_TechSmoke_PalletEUR` → `/Game/Genesis/TechSmoke/PalletEUR/SM_TechSmoke_PalletEUR`

## Wie gearbeitet wurde

Der Unreal-Editor lief **sichtbar**. Gesteuert wurde er über Epics Python-Fernsteuerung (`tools/v4/g4/ue_remote.py`, nur lokal). Alle Schritte sind Skripte und wiederholbar:

| Skript | Aufgabe |
|---|---|
| `g4_import.py` | Texturen (BC sRGB · ORM Masks · N Normalmap, alles 4096²) und FBX importieren, PBR-Master `M_PBR_Master` + Instanz `MI_TechSmoke_PalletWood`, importierte Normalen/Tangenten behalten, Nanite an (Ersatz-Mesh 100 %), UCX-Kollision übernehmen |
| `g4_level.py` | leeres Level ohne World Partition `L_TechSmoke`: Sonne 90 000 lx bei 38°, Sky Atmosphere, Sky Light (Echtzeit), Höhennebel, manuelle physikalische Belichtung, zwei Kino-Kameras 50 mm Vollformat |
| `g4_floor.py` | Betonboden aus der in Blender gebackenen 4 × 4 m-Kachel (`tools/v4/g4/bake_concrete.py`), weltweit ausgerichtet, großflächige Tonvariation gegen sichtbare Wiederholung |
| `g4_render.py` | Endbilder mit der **Movie Render Queue** (16 zeitliche Samples, 90 Aufwärmbilder für Lumen), unabhängig vom Editor-Viewport |
| `g4_verify.py` | Rücklesen und Prüfen, inklusive Linientests durch die Gabeltaschen |

## Ergebnis – `docs/evidence/G4/verify_report.json`: **10/10 bestanden**

| Prüfung | Ergebnis |
|---|---|
| Maße wie Blender (±0,1 mm) | 120,209 × 80,096 × 14,584 cm = 1202,09 × 800,96 × 145,84 mm ✔ |
| Achsen und Ursprung | Länge auf X, Breite auf Y, Z oben, Ursprung Bodenmitte ✔ |
| Nanite | an. Ersatz-Mesh mit voller Geometrie (Zielmodus „PercentTriangles“, 8 223 Punkte), damit Raytracing-Schatten und -Spiegelungen das echte Mesh nutzen ✔ |
| Material | genau 1 Platz = `MI_TechSmoke_PalletWood`; das vom Importer angelegte Platzhalter-Material ist entfernt ✔ |
| Kollision | 20 Quader aus dem FBX (`UCX_`, je Brett/Querbrett/Klotz). **Gabeltaschen frei:** 4 Linientests durch die Taschen ohne Treffer, Deck und Klotz werden getroffen ✔ |
| Auflage | Palette steht bei z = 0 auf dem Boden ✔ |
| Endbilder | `ue_review_cam.png`, `ue_review_detail.png` (1920 × 1280). Luminanz Mittel 0,47 / 0,38, 99. Perzentil 0,66 / 0,68, **0 % ausgebrannt** |

## Unterwegs gefunden und behoben

1. **Kamera bewegte sich von selbst:** Der angeschlossene Xbox-360-Controller hat Stick-Drift (rechter Stick in Ruhe ~27 %, über Unreals Totzone 0,25). Behoben mit `bLevelEditorJoystickControls=False` (`Config/DefaultEditorPerProjectUserSettings.ini`, wirkt nach Editor-Neustart). Nachgemessen: Die Kamera bleibt mit Fokus 7,5 s exakt stehen. **Im Spiel (PIE) driftet der rechte Stick weiterhin**, solange die Totzone unter 0,28 liegt. Die echte Lösung ist, den Controller zu kalibrieren oder zu ersetzen.
2. **Gabeltaschen zu:** Die automatische Konvex-Zerlegung (15 Hüllen) hat die Taschen verschlossen → eigene `UCX_`-Quader aus Blender (`add_collision` in `tools/v4/g3/build_pallet.py`), FBX-Prüfung jetzt 11/11.
3. **Ersatz-Mesh vereinfacht:** „100 %“ wurde ignoriert, solange der Zielmodus „Auto“ war (974 Punkte) → Zielmodus „PercentTriangles“.
4. **Bild 2–3 Blendenstufen zu hell:** Bei physikalischer Belichtung gilt in der Movie Render Queue die Blende der **Kino-Kamera**, nicht die des Post-Process-Volumes → Kameras auf f/16 (Sunny 16: ISO 100, 1/100 s, f/16).
5. **Boden mit künstlichem Zellmuster** (Noise-Material) → in Blender gebackene Betonkachel, Kachelnaht liegt in den Sägefugen.

## Reality Check (Unreal-Endbilder)

| Bereich | Befund |
|---|---|
| Maßstab, Geometrie, Kanten | OK – wie in Blender, Ausbrüche, Splitter und Endrisse sichtbar |
| Material | OK – Maserung, Pressspan, Nägel, Gebrauchsspuren kommen über die gebackenen Texturen 1:1 an |
| Licht und Schatten | OK – Sonne mit weichem Schattenrand, Kontaktschatten, Lumen-Licht unter dem Deck, keine Aufhelllichter |
| Belichtung, Farben | OK – gemessen, nichts ausgebrannt, kein Bloom/Flare/Aberration |
| Umgebung | OK für eine Prüfaufnahme – Beton mit Fugen, Fahrspuren, Sandkorn. Kies und Splitter liegen in Unreal (noch) nicht |

**Quality Gate:** 1. Glaubwürdig real? **Ja.** 2. Höchste sinnvolle Qualität für ein Test-Asset? **Ja.**

## Nicht geprüft / offen

- Kein Path-Tracer-Vergleichsbild (Lumen gegen Referenz).
- Kein Spieltest mit der Palette (Physik, Gabelstapler) – gehört in spätere Gates.
- Gamepad-Drift im Spiel siehe Punkt 1 – Entscheidung des Nutzers.
