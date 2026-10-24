# G7 – Flussdorf, Lieferung 1 (Werkstatt R03) · Status: BLENDER_VALIDATED (Geometrie), nicht in Unreal

Datum: 2026-10-24 · Plan und Maßblätter: `docs/design/G7_FLUSSDORF_ASSETS.md` · Bild-KI: FLUX.2 klein 4B lokal (ComfyUI auf 127.0.0.1, danach beendet)

## Referenzbilder (GENERATED_PREVIEW, nicht freigegeben)

`ArtSource/Reference/G7/`: jedes Bild hat eine JSON-Datei mit Prompt, Saat und den Modell-Prüfsummen.

| Asset | Bild | Bewertung |
|---|---|---|
| Generator | `front34_v2` (Saat 11) als Leitbild, `back34_v1` für die Rückseite | Proportionen und durchsichtiger Filter passen. FLUX zeichnet US-Steckdosen, im Modell sind es deutsche Schuko-Dosen. |
| | `front34_v1`, `front34_v3` | verworfen: zu hoch und würfelig bzw. Starter und Filter nicht erkennbar |
| Werkbank | `front34_v1` | passt (Platte, Stahlgestell, Schraubstock) |
| Teileregal | `front34_v1` | passt; im Bild breiter als das Maßblatt (1,0 m) |
| Werkstatt-Stimmung | `interior_v1` | Ziegelraum, Fensterlicht, Lichtleiste an Ketten: Vorgabe für den Raum und das Licht |

## Blender-Modelle

Gebaut mit Skripten (nachvollziehbar und wiederholbar): `tools/v4/g7/build_generator.py`, `build_workbench.py`, gemeinsame Bausteine in `g7_common.py`. Dateien: `ArtSource/Blender/G7/`, Export `ArtSource/Export/G7/`.

| Asset | Maße gemessen (FBX neu importiert) | Dreiecke | Kollision | Sockets | Prüfung |
|---|---|---|---|---|---|
| `SM_R03_Generator_N02` | 605 × 462 × 457,5 mm (Soll 600 × 450 × 460, Toleranz 15) | 36 264 | 1 UCX | `SOCKET_InspectPlug`, `SOCKET_InspectFilter`, `SOCKET_TryStart` | **7/7 bestanden** |
| `SM_R03_Workbench` | 2000 × 956 × 1050 mm (Werkbank 2000 × 750 × 900, Schraubstock steht vorn 206 mm über und 150 mm hoch) | 12 024 | 7 UCX | – | **7/7 bestanden** |

Geprüft wurde: Maße, Ursprung auf dem Boden, Kollision, Sockets, UV-Karte, keine Flächen mit mehr als vier Ecken, Maßstab 1,0. Prüfskript: `tools/v4/g7/verify_fbx_g7.py`. Belege: `docs/evidence/G7/`.

**Generator, sichtbar und prüfbar wie in der Mission:**
- Zündkerze mit Stecker vorn am Zylinderkopf, frei zugänglich.
- Durchsichtiger Benzinfilter mit Papiereinsatz in der Leitung.
- Seilzugstarter mit Griff.
- Zwei Schuko-Steckdosen mit Klappdeckeln, Schalter, Choke.
- Lochblech-Hitzeschutz, Lüftungsschlitze, Schrauben.

**Materialien:**
- Physikalisch aufgebaut auf drei Ebenen:
  - Große Farbverläufe
  - Abgeplatzte Kanten, Kratzer, Staub oben, Benzinflecken am Tankdeckel, Ölflecken und Schnittspuren auf der Werkbank, Furnierlagen an der Plattenkante
  - Rauheitsrauschen und Oberflächenstruktur
- Aluminium ist Metall, lackierter Stahl ist kein Metall.
- Gerendert in Cycles mit OptiX und AgX-Farbumwandlung.

## Fehler gefunden und behoben (Turnaround v1 → v4)

1. Aluminium wirkte wie weißer Gips. Ursache war ein Rechenfehler in der Material-Formel: Der Metallwert war auf offenen Flächen 0. Behoben.
2. Die Farben waren ausgewaschen (Tank pfirsich, Rahmen mint). Ursache: zu helles Licht. Die Lichtstärke ist jetzt um den Faktor 2,8 gesenkt.
3. Lackabplatzer sahen aus wie Schneeflocken. Kanten-Maske und Kratzer sind jetzt seltener und sitzen an den Kanten.
4. **Die Zündkerze saß unter dem Tank und war nicht erreichbar.** Zylinder gekürzt, Kerze nach vorn gedreht, Luftfilter versetzt.
5. Die Gesamthöhe lag 17 mm über dem Soll. Tank und Rahmen sind abgesenkt.
6. Faces mit mehr als vier Ecken verhinderten Tangenten in Unreal. Diese Flächen werden jetzt in Dreiecke geteilt.
7. Der Hitzeschutz war ohne Löcher, die Lüftungsschlitze bildeten ein Achteck. Behoben.
8. Werkbank: Der Staub auf der Ablage sah aus wie Tarnmuster. Reduziert.

## Reality Check – ehrlich

1. **Wirkt es glaubwürdig real?** Aus normaler Spielentfernung: ja, beide Objekte sind stimmig und plausibel gealtert. **Aus der Nähe noch nicht fotoecht.** Kunststoffteile sind zu glatt. Der Tank hat keine Sicken, Schweißnähte oder Aufkleber (ohne Text). Die Starter-Lamellen stehen vor, statt vertieft zu sein. Kabel und Bowdenzug zum Choke fehlen. Die Lackierung der Werkbank-Ablage ist noch etwas fleckig.
2. **Höchste sinnvolle Qualität?** Noch nicht.
   - Die Materialien sind prozedural (nur in Blender gültig). Für Unreal müssen sie in Texturen gebacken werden, wie bei der Palette in G3.
   - Beurteilt wurde unter Studiolicht, noch nicht unter dem Werkstattlicht aus dem Stimmungsbild.

**Damit ist G7 nicht abgenommen.** Diese Lieferung ist ein geprüfter Zwischenstand.

## Was fehlt (nächste Schritte von G7)

- Nahdetails nachziehen (Liste oben), dann die Texturen backen (BaseColor, ORM, Normal), Unreal-Import und Austausch der Graybox-Objekte in `L_Flussdorf_G6`.
- Teileregal `SM_R03_PartsShelf` und Lichtleiste `SM_R03_LightBar` (Referenzen sind fertig).
- Werkstattraum selbst (Ziegel, Fenster, Betonboden), danach R02 Markt, R01 Dorfplatz, R07 Häuser.
- Figuren N01–N03, Stimmen, Musik, Untertitel: Dafür brauche ich deine Freigabe der Dialogsätze aus G6.
- Menschliche Sichtung (Pflicht für G7).
