# G7 – Flussdorf, Lieferung 4 (Werkstatt moderner und voller) · Status: ENGINE_TESTED, Optik nicht abgenommen

Datum: 2026-10-24 · Deine Vorgaben: „moderner und voller“, dazu Hebebühne und Tresen.

## Freigabe und Herkunft
- **Plan `FA-POLYHAVEN-002`**:
  - Inhalt: `painted_brick` 4K für die Wände und `painted_concrete_02` 4K für den Boden. 8 Dateien, 225,8 MB, MD5 geprüft, CC0.
  - Manifest: `ArtSource/External/PolyHaven/MANIFEST_FA-POLYHAVEN-002.json`.
  - Seit dieser Lieferung bekommt jeder Plan ein eigenes Manifest. Beim zweiten Download hatte das Werkzeug das erste überschrieben; ich habe es wiederhergestellt und das Werkzeug korrigiert.
- **Wandfarbe:** Der Ziegel-Scan ist blau gestrichen. Relief, Fugen und Rauheit bleiben aus dem Scan, nur die Farbe wird im Material umgefärbt: `Tint · (0,55 + 0,9 · Helligkeit)`. Die Formel ist in Blender und in Unreal (`M_G7_Tiled`) gleich.

## Was neu ist
| Teil | Inhalt |
|---|---|
| Raum | Ziegel weiß gestrichen, grauer Sockel bis 1,20 m, grauer Beschichtungsboden, Decke und Balken weiß, Rahmen anthrazit; **3 LED-Leisten** (insgesamt etwa 12 000 lm) |
| `SM_R03_Cabinets` | 2 m Unterschränke anthrazit mit Schubladen, Buche-Platte, Lochwand, Hängeschränke; Diagnose-Laptop, Akkuschrauber auf Ladestation, Steckschlüsselkoffer, Kettensäge (Reparaturauftrag), Sprühdosen, Ölflasche |
| `SM_R03_Equipment` | 50-l-Kompressor, Druckluft-Schlauchtrommel, Feuerlöscher, Erste-Hilfe-Kasten, Rasenmäher (auf der Hebebühne), Freischneider, Abfalleimer, Gummimatte vor der Werkbank, Wanduhr |
| `SM_R03_ServiceCounter` | Tresen 1,26 × 0,60 m an der Tür, Bezahlterminal, Auftragsmappe, Zündkerzen-Auslage; Abholregal mit fertigen Aufträgen und leeren Anhängern |
| `SM_R03_LiftTable` | Scheren-Hebetisch 2,1 × 0,7 m für Motorräder und Gartengeräte, auf 60 cm hochgefahren, mit Rasenmäher, Pumpe und Handschalter. Eine Auto-Hebebühne bräuchte etwa 4,2 m Deckenhöhe, der Raum hat 3,48 m; außerdem ist es eine Kleinmotoren-Werkstatt. |

Alle Laufwege der Mission bleiben frei: Tür → Kundin, Tür → Werkbank, Prüfplatz am Generator. Tests: **16/16** (`docs/evidence/G7/regression_modern_final.txt`), Mission 82 GE, genau 1 Zahlung. Bilder (Lumen, höchste Qualität): `docs/evidence/G7/r03_modern_v1/`.

## Fehler gefunden und behoben
1. **Laptop-Deckel stand vorne:** Das Scharnier saß an der Vorderkante, der Laptop sah aus wie ein Bilderrahmen. Jetzt hinten.
2. **Rampe des Hebetischs stand senkrecht:** 45 cm Rampe reichen nicht für 60 cm Höhe, die Winkelformel lief in ihre Begrenzung. Die Rampe liegt jetzt abgenommen flach daneben, wie im echten Betrieb.
3. Ölwanne und Besen standen dort, wo jetzt Schränke und Tresen stehen. Beide versetzt.
4. **Backen dauerte über 20 Minuten pro Asset**, weil Unreal 8 von 12 GB Grafikspeicher belegte. Mit geschlossenem Unreal sind es etwa 70 Sekunden für eine 4K-Textur. Ein Backlauf ist mit offenem Unreal einmal ohne Fehlermeldung abgebrochen.
5. **Missionstest:** Er schlug nach einem Neustart des Editors einmal fehl (Fokus N02 statt N01). Danach 4 Durchläufe in Folge 16/16. **Die Ursache ist weiter offen**; der Test schreibt bei einem Fehlschlag inzwischen die Positionen aller Personen ins Protokoll.

## Offen
- Lumen ist etwa 1,5-mal heller und blauer als der Path Tracer: Abgleich steht aus.
- Kleinteile sind weiter vereinfacht: Rasenmäher-Fangkorb als Kasten, Kettensäge grob, Schlauchtrommel als geschlossene Scheibe.
- Fassade und Dach der Werkstatt sind von außen noch Graybox.
- Deine Sichtung (Pflicht für G7).
