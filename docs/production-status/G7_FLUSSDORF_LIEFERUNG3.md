# G7 – Flussdorf, Lieferung 3 (Werkstattraum mit echten Materialien) · Status: ENGINE_TESTED, Optik nicht abgenommen

Datum: 2026-10-24 · Baut auf `G7_FLUSSDORF_LIEFERUNG2.md` auf.

## Freigabe und Herkunft

- **Plan `FA-POLYHAVEN-001`** (`docs/v4_1/install_plans/`): Freigabe im Chat („Ja, erstelle einen Download-Plan für CC0-Texturen und HDRIs von Poly Haven. Danach baue …“).
- **Lizenz:** CC0. Laut polyhaven.com/license kommerziell und in Spielen frei, keine Namensnennung nötig. Die Poly-Haven-API ist laut Repository für jeden Zweck frei nutzbar.
- **Download:** 18 Dateien, 299,6 MB, nur über `dl.polyhaven.org`. Jede MD5-Prüfsumme stimmt, SHA-256 steht im Manifest (`FA-POLYHAVEN-001_MANIFEST.json`). Die Dateien selbst sind nicht im Git, weil sie jederzeit neu ladbar sind.
- **Werkzeug:** `tools/v4_1/polyhaven_fetch.py`. Es lädt nur, was im Plan steht, und bricht bei falschem Host oder falscher Prüfsumme ab.

| Asset | Einsatz | Kachelgröße |
|---|---|---|
| damaged_plaster 4K | Wände: Ziegel mit Putzresten | 1,85 m |
| garage_floor 4K | Betonboden mit Ölflecken | 1,89 m |
| brown_planks_03 4K | Bretterdecke und Balken | 1,00 m |
| distressed_painted_planks 2K | Tür- und Fensterrahmen | 1,60 m |
| empty_workshop / hausdorf_meadow | HDRIs für Blender (Himmel durchs Fenster) | – |

## Was gebaut ist

| Teil | Inhalt | Skript |
|---|---|---|
| `SM_R03_Room` | Raum 7 × 6 m, 24-cm-Wände; Tür 1,20 × 2,20 m mit Rahmen, Blatt nach außen geöffnet; Fenster 1,20 × 1,10 m in der Ostwand (Zweifachverglasung, Innenbrett, Zinkblech außen); Bretterdecke auf 3 Balken; Betonboden; 12 Kollisionsboxen; UVs im Weltmaßstab | `build_room.py` |
| `SM_R03_ToolWall` | Lochblech mit 4 Ringschlüsseln, 4 Schraubendrehern, 2 Zangen, Hammer; Wandbord mit Kisten, Schraubengläsern, Öldose, Karton; Elektrodose mit Schuko-Steckdose und Schalter, Rohr bis zur Decke, Ladekabel | `build_dressing.py` |
| `SM_R03_BenchItems` | Ladegerät mit Klemmen, Radio (laut Quelle optionales Motiv), Schraubenglas, 3 Schraubendreher, Putzlappen, Zündkerzenschachtel | `build_dressing.py` |
| `SM_R03_FloorItems` | Werkzeugwagen mit 3 Schubladen, 2 × 20-l-Kanister, Kabeltrommel mit Kabel über den Boden, Eimer, Ölauffangwanne, Karton unter dem Generator, Besen; 5 Kollisionsboxen | `build_dressing.py` |
| `M_G7_Tiled` (Unreal) | Kachelndes PBR-Master-Material mit derselben Anti-Kachel-Methode wie in Blender: zweite, versetzte Texturlage, über eine großflächige Maske gemischt. Ziegel und Bretter bleiben dabei waagerecht. 238 Instruktionen, 5 Sampler. | `g7_room_import.py` |
| Licht | Morgensonne fällt durchs Ostfenster (mit Sprossenschatten); LED-Leiste 4000 lm / 4000 K; Belichtung EV ≈ 6 | `render_room.py`, `g7_level.py` |
| Renderqualität Unreal | Neu in `mrq_render.py` als `"quality": "max"`: Hardware-Raytracing mit Hit-Lighting für Lumen, 4 × 32 Samples, dichtere Lichtproben, 16 Schattenstrahlen. Neu als `"pathtracer"`: 512 Samples pro Pixel, entrauscht. | `tools/v4/common/mrq_render.py` |

## Tests

**16/16 bestanden** im eingerichteten Raum. Missionsdurchlauf: 82 GE, genau 1 Zahlung (`docs/evidence/G7/regression_room_final.txt`).

## Bilder

`docs/evidence/G7/r03_room_v1/`:
- Blender Cycles: 4 Ansichten.
- Unreal Lumen in höchster Qualität: 4 Ansichten.
- Unreal Path Tracer als Referenz: 1 Ansicht.

## Fehler gefunden und behoben

1. **Sichtbare Kachelwiederholung** der Ziegelwand alle 1,85 m. Abhilfe: Anti-Kachel-Mischung.
2. Die erste Fassung der Anti-Kachel-Mischung drehte die zweite Lage um 37°, dadurch liefen **Ziegelreihen und Bretter schräg**. Jetzt wird nur bei Beton gedreht.
3. **Keine Sonne durchs Fenster in Blender:** Cycles findet die fast punktförmige Sonne nicht durch brechendes Glas. Abhilfe: Schattenstrahlen gehen durch die Verglasung, mit 92 % Durchlass wie bei echtem Doppelglas. Unreal verhält sich mit durchsichtigem Glas genauso.
4. Das **geöffnete Türblatt stand im Raum** und verdeckte das Bild. Es öffnet jetzt nach außen.
5. Die **Kabeltrommel sah aus wie ein schwarzer Kasten.** Sie hat jetzt einen offenen Rahmen mit Seitenscheiben und Tragbügel.
6. Ein **Aufhängehaken der Lichtleiste steckte im Deckenbalken.** Die Leiste ist um 15 cm versetzt, die Höhe richtet sich jetzt nach der Deckenunterseite (346 cm).
7. **Schachbrettmuster in Unreal:** Das neue Master-Material hatte Texturparameter ohne Standardtextur und kompilierte deshalb nicht. Behoben.
8. Unreal hatte für Wand- und Werkbankdeko automatisch eine Kollisionshülle erzeugt. Entfernt, weil sie den Weg versperren könnte.
9. Die **rotation-Node von Unreal (CustomRotator) fehlt in der Python-API.** Die Rotation ist jetzt als einfache Rechnung (cos/sin) gebaut, das Ergebnis ist gleich.
10. Selbst verursacht: Mit einem zu breiten `taskkill` habe ich das sichtbare Blender-Fenster geschlossen. Es ging nichts verloren, die Datei war gespeichert.

## Reality Check – ehrlich

1. **Wirkt es glaubwürdig real?**
   - Aus Raumentfernung: weitgehend ja. Ziegel und Putz, Beton, Bretterdecke, Sonnenfleck, Werkstattkram.
   - Aus der Nähe noch nicht fotoecht:
     - Die kleinen Teile sind vereinfacht: Werkzeuge ohne Prägung, Kanister als Quader mit Griffen, der Lappen ist ein geknittertes Blatt.
     - Die Löcher im Lochblech werden auf Abstand zu Pixelrauschen.
     - Im Path Tracer wirken Regal und Lochblech fast weiß, bei Lumen grau. Die Ursache ist noch nicht gemessen; vermutlich der Metallwert der gebackenen Texturen.
2. **Höchste sinnvolle Qualität?** Die Render-Einstellungen sind jetzt auf dem Maximum. Bei den Assets noch nicht, siehe oben, dazu das fleckige Gussalu am Generator aus Lieferung 2.

**G7 ist nicht abgenommen.** Pflicht ist deine Sichtung.

## Offen

- Nahdetails der Kleinteile; Lochblech als echtes Lochmuster in der Normal-Map; den Weißton im Path Tracer messen.
- Fleckiges Gussaluminium am Generator (Back-Schritt).
- Außenansicht der Werkstatt: Fassade und Dach sind noch Graybox.
- Figuren N01–N03, Stimmen, Musik, Untertitel. Dafür brauche ich deine Freigabe der Dialogsätze aus G6.
