# C02 – Maßblatt Mikrowelt (CR-001 Phase 3)

Grundlage für die Blender-Modelle; Look nach den abgenommenen Referenzen (GD-2026-10-25-04, GD-2026-10-26-01). Werte aus der Humanbiologie (WHO-Laborhandbuch 2021 für Spermien, Embryologie-Standardwerte); wo Spannweiten angegeben sind, nimmt das Modell den Mittelwert.

**Maßstab in den Werkzeugen:** 1 µm = 1 Unreal-Unit (1 uu) = 1 cm in Blender. Export aus Blender ohne Skalierung (FBX, Einheit cm) → in Unreal 1:1.

## Samenzelle (CHR_C02_SPERMIUM)
| Teil | Maß | Hinweis |
|---|---|---|
| Kopf Länge × Breite × Dicke | 4,1 × 2,8 × 1,2 µm | glatt oval, abgeflacht (Paddelform), vorn etwas dünner |
| Akrosom | 40–70 % der Kopffläche, vorn | hellere Kappe, leicht gewölbt |
| Mittelstück | 4,5 µm lang, ⌀ 0,7 µm | Mitochondrienspirale als feine Wendel |
| Hauptstück | 45 µm, ⌀ 0,5 → 0,15 µm | gleichmäßig verjüngt |
| Endstück | 4 µm, ⌀ 0,1 µm | haarfein |
| Gesamt | ≈ 58 µm | Schwanz ≈ 11 × Kopflänge |
| Geißelschlag | 10–20 Hz, Wellenlänge ≈ 25 µm, Amplitude an der Spitze ≈ 4–6 µm | im Spiel per Material (World Position Offset), im Blender-Modell als Pose |
| Brechzahl | Kopf ≈ 1,42, Schwanz ≈ 1,38 | dichtes Chromatin im Kopf |

## Eizelle mit Hüllen (CHR_C02_OOZYTE_CUMULUS)
| Teil | Maß | Hinweis |
|---|---|---|
| Eizelle (Oolemma) | ⌀ 115 µm | fein granuliertes Zytoplasma, leicht durchscheinend |
| Perivitelliner Spalt | 3–5 µm | klar |
| Zona pellucida | 16 µm dick (außen ⌀ ≈ 155 µm) | glasig, leicht faserig, Brechzahl ≈ 1,34 |
| Polkörper | ⌀ 12 µm | im perivitellinen Spalt |
| Corona radiata | 1–3 Zelllagen direkt auf der Zona | Zellen ⌀ 10–14 µm, rund bis oval, Kern ⌀ 5 µm |
| Cumulus oophorus | lockere Wolke bis ≈ 400 µm vom Zentrum | Zellen in klarer Gel-Matrix (Hyaluronsäure) |

## Zygote und 2-Zell-Stadium (CHR_C02_ZYGOTE)
| Teil | Maß | Hinweis |
|---|---|---|
| Vorkerne | 2 × ⌀ 22 µm, berühren sich in der Mitte | je 3–7 Nukleolen (⌀ 1–2 µm) an der Kontaktlinie |
| Blastomeren (2-Zell) | 2 × ⌀ 88 µm | gleiches Gesamtvolumen wie die Zygote, je ein Kern ⌀ 15 µm |
| Zona | wie Eizelle | bleibt unverändert |

## Eileiter-Ampulle (ENV_C02_EILEITER_AMPULLE)
| Teil | Maß | Hinweis |
|---|---|---|
| Lumen (Spielstrecke) | Radius 420–690 µm | wie `FGenesisOviduct::Radius` |
| Schleimhautfalten | Höhe 80–250 µm, Dicke 20–40 µm, längs, verzweigt | Labyrinth zur Ampulle hin dichter |
| Epithelzellen | ⌀ ≈ 10 µm | Flimmer- und sekretorische Zellen |
| Zilien | 8–10 µm lang, ⌀ 0,25 µm | nur als Oberflächen-Detail (Normal/Shader), keine Einzelgeometrie |
| Strömung | ≈ 12 µm/s zum Uterus | wie im Spiel |
