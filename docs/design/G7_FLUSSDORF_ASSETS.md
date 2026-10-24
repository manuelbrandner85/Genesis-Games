# G7 – Flussdorf: Assetplan, erste Lieferung Werkstatt R03

Quellen: `WELTBIBEL_FLUSSDORF` (R03: Arbeitstisch, Lichtleiste, Teilelager; Generator diagnostizieren, Werkzeug ausleihen), `V48_KANON_NPCS_UND_ORTSBINDUNG` (N01 = Generator-Arbeit; Flussdorf ist **zeitgenössisch**), `V24_MISSIONSBIBEL` (Kette A).
Was die Quellen offen lassen, ist als **Startwert** markiert.

## Warum zuerst R03

Die ganze spielbare Kette A spielt an diesen Objekten. Der Generator ist das interaktive Hauptobjekt der Region (Weltbibel §5). Er hat in G6 vier Prüfpunkte, die das Modell sichtbar tragen muss.

## Rahmen (Startwerte)

| Punkt | Startwert | Grund |
|---|---|---|
| Ort und Zeit | kleines mitteleuropäisches Flussdorf, Gegenwart 2026 | Die Quelle sagt „zeitgenössisch“, alle Texte sind deutsch; ein Land wird nicht genannt |
| Werkstatt | Kleingewerbe für Geräte- und Motorreparatur in einem älteren Nebengebäude (Ziegel/Putz, Betonboden), keine Schreinerei | V48: „nicht automatisch eine Schreinerei“ |
| Markennamen | keine; Typenschilder ohne echte Hersteller | Rechte |

## Lieferung 1 – Maßblätter

| ID | Objekt | Maße (B × T × H) | Material | Pflichtdetails |
|---|---|---|---|---|
| `SM_R03_Generator_N02` | tragbarer Benzin-Stromerzeuger mit offenem Rohrrahmen, 2,8 kW | 600 × 450 × 460 mm, ca. 45 kg | Stahlrohrrahmen pulverbeschichtet, Tank Stahlblech lackiert, Motor Aluguss, Kunststoff-Bedienfeld | Zündkerzenstecker und -kerze **zugänglich** (Prüfpunkt `Gen.InspectPlug`), **durchsichtiger Kraftstofffilter** in der Leitung unter dem Tank (`Gen.InspectFilter`), Seilzugstarter mit Griff (`Gen.TryStart`), Tankdeckel, Steckdosenfeld, Choke, Gebrauchsspuren (Benzin-Laufspuren unter dem Tankdeckel, Kratzer am Rahmen, Ölfilm am Motor) |
| `SM_R03_Workbench` | Werkbank | 2000 × 750 × 900 mm | Buche-Multiplex-Platte 40 mm, Stahlgestell, Schraubstock 125 mm | Ölflecken, Schnittspuren, Abrieb an der Vorderkante, Schraubstock vorn links |
| `SM_R03_PartsShelf` | Teilelager / Schwerlastregal | 1000 × 400 × 2000 mm, 5 Böden | verzinkter Stahl, Kunststoff-Sichtlagerkästen | beschriftete Kästen (ohne Marken), Kartons |
| `SM_R03_LightBar` | Lichtleiste über der Werkbank | 1500 × 60 × 40 mm, an Ketten | Aluprofil, opale Abdeckung | echte Lichtquelle für Unreal (4000 K, ca. 4000 lm) |

## Ablauf je Asset

1. Referenzbild lokal mit **FLUX.2 klein 4B** (ComfyUI, 127.0.0.1): Dreiviertel-Ansicht plus Seite und Rückseite auf neutralem Hintergrund. Herkunft mit Saat, Prompt und Modell-Hashes in `ArtSource/Reference/G7/` festhalten.
2. Blender-Modell in echten Maßen (Meter, Maßstab 1,0), Fasen, UVs, PBR-Material mit drei Detailebenen, Kollision (UCX), LOD über Nanite.
3. Prüfung: Maße gegen das Maßblatt, Turnaround-Render mit Cycles, Reality Check.
4. Erst danach Unreal-Import und Austausch in `L_Flussdorf_G6`.

## Nicht in Lieferung 1

Gebäude R01–R08, Figuren N01–N03 (Gesichter und Stimmen brauchen deine Freigabe), Brücke, Vegetation, Musik und Untertitel. Sie folgen in weiteren Lieferungen von G7.
