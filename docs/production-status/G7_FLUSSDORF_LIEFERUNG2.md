# G7 – Flussdorf, Lieferung 2 (Werkstatt R03 in Unreal) · Status: ENGINE_TESTED (Funktion), Optik nicht abgenommen

Datum: 2026-10-24 · Baut auf `G7_FLUSSDORF_LIEFERUNG1.md` auf.

## Was neu ist

| Teil | Ergebnis | Beleg |
|---|---|---|
| Teileregal `SM_R03_PartsShelf` | 1005 × 423 × 2000 mm, verzinkt, Lagerkästen mit leeren Etiketten, Kartons, Schlauch; FBX-Prüfung bestanden | `docs/evidence/G7/PartsShelf_v2/` |
| Lichtleiste `SM_R03_LightBar` | 1500-mm-LED-Leiste an Ketten, 600 mm Abhängung, Kabel, `SOCKET_Light`. Ursprung an der Decke, deshalb ist die Bodenprüfung absichtlich „nein“. | `docs/evidence/G7/LightBar_v1/` |
| Texturen gebacken | alle 4 Assets: BaseColor, ORM (AO/Rauheit/Metall), Normal (DirectX); Generator und Lichtleiste 2048, Werkbank und Regal 4096 | `tools/v4/g7/bake_g7.py`, `ArtSource/Textures/G7/` |
| Unreal-Import | Maße auf den Zentimeter wie in Blender, UCX-Kollision, Sockets, Nanite (außer Generator: durchsichtiges Filtergehäuse). Eigene Materialien für Filtergehäuse (durchsichtig) und LED-Abdeckung (leuchtend). | `docs/evidence/G7/unreal_import_report.json` |
| Level | Graybox-Blöcke in `L_Flussdorf_G6` ersetzt. Echte Lichtquelle 4000 lm / 4000 K unter der Leiste. Eigene Innenbelichtung (ISO 800, 1/60 s, f/2,8, ≈ EV 6). | `tools/v4/g7/g7_level.py` |
| **Werkstatt 7 × 6 m** (deine Entscheidung) | Westwand mit Tür bleibt. Wände, Regionsvolumen und N01-Arbeitsplatz versetzt, Navigation neu gebaut. Neu: neutrale Innendecke und Betonboden. | `tools/v4/g7/g7_room.py`; `g6_level.py` / `g6_npcs.py` angepasst |
| **Tests** | **16/16 bestanden**, Missionsdurchlauf: 82 GE, genau 1 Zahlung | `docs/evidence/G7/regression_after_g7.txt` |
| Bilder | 4 Kameras in der Werkstatt (Movie Render Queue) | `docs/evidence/G7/unreal_r03_7x6/` |

## Fehler gefunden und behoben

1. **Ausrichtung:** Der FBX-Import dreht die Y-Achse. Generator, Werkbank und Regal standen deshalb verkehrt herum. Korrigiert: Bedienfeld, Kerze und Filter zeigen zur Tür, der Schraubstock nach vorn.
2. **Grundfarbe:** Die Basisfarbe kam beim Backen über den Diffus-Durchgang und war auf Metall schwarz. Jetzt wird sie direkt über einen Emissions-Umweg gebacken.
3. **Metallwert:** Der Schmutz senkte auch den Metallwert, dadurch wechselten Metall und Nicht-Metall fleckig. Metallic ist jetzt binär.
4. Das Material für das durchsichtige Filtergehäuse hatte eine Beleuchtungsart, die es in UE 5.8 nicht gibt. Ersetzt durch `TLM_SURFACE_PER_PIXEL_LIGHTING`.
5. **Rote Färbung:** Das rotbraune Graybox-Dach wurde von der Leiste angestrahlt und färbte die Schatten rot. Abhilfe: neutrale Innendecke.
6. **Grüner Boden:** Der Raum stand auf dem Rasen des Dorfes. Abhilfe: Betonplatte, 1 cm erhöht, damit nichts flackert.
7. **Missionstest zweimal fehlgeschlagen:** Der Spieler-Fokus landete auf N02 statt auf N01, jeweils direkt nach einer Geometrieänderung. Danach lief er dreimal in Folge sauber. Die Ursache ist nicht bewiesen; vermutlich war die Navigation noch im Aufbau. Bei einem Fehlschlag schreibt der Test jetzt die Positionen aller Personen ins Protokoll.

## Offen (ehrlich)

- **Optik nicht abgenommen.** Der Raum ist noch Graybox: weiße Wände ohne Material, kein Fenster, keine Ausstattung außer den 4 Objekten. Dazu die Rendereinstellungen, siehe unten.
- **Bunte Lichtflecken** in sehr dunklen Ecken: unter der Werkbank wechselnd rot, orange, grün. Das ist Bildrauschen im indirekten Licht von Lumen, nicht eine farbige Fläche. Es braucht höhere Lumen-Qualität oder Hardware-Raytracing mit Hit-Lighting in der Render-Queue.
- **Fleckiges Gussaluminium** am Motor. Das tritt nur in der gebackenen Textur auf, nicht im Blender-Render. Die Ursache liegt im Back-Schritt der Schmutzmaske und ist noch nicht gefunden.
- UV-Aufteilung der Werkbank: etwa ein Viertel der Textur ist ungenutzt.
- Menschliche Sichtung von G7.
