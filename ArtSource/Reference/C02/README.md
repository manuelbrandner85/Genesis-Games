# C02 – Referenzentwürfe Mikrowelt (CR-001 Phase 3, zur Regieabnahme)

Lokal erzeugt mit FLUX.2 klein 4B (ComfyUI, Apache-2.0) über die GAMEFORGE-GPU-Sperre; Prompt, Seed und Modell-Hashes stehen jeweils in der JSON neben dem Bild. Freigabe zur Erzeugung: GD-2026-10-25-03. Status: **GENERATED_PREVIEW – nicht abgenommen**. Übersicht: `C02_Referenzen_Abnahmeblatt.jpg`.

Bildsprache aller Entwürfe: wie durch ein Forschungsmikroskop gefilmt (Hoffman-/DIC-/Phasenkontrast), echte Maßstäbe, kein Leuchten, kein Comic.

| Motiv | Empfehlung | Bewertung (biologische Richtigkeit) | Verworfen |
|---|---|---|---|
| ENV_C02_EILEITER_AMPULLE | `lumen_v1` | Längsfalten der Schleimhaut, feuchte Oberfläche, Wimpernansatz, ferne Zellen als Punkte – stimmig. Echte Ampullenfalten sind noch stärker verzweigt (Labyrinth) – für das Modell verstärken | `lumen_v2` (Adern/Pilzlamellen) |
| CHR_C02_OOZYTE_CUMULUS (Komplex) | `complex_v3` | runde Cumulus-/Coronazellen mit Kern, klare Zona, Eizelle – stimmig; Cumuluszellen etwas zu groß gegenüber der 120-µm-Eizelle | `complex_v1/v2` (Nadeln/Kristalle), `complex_v4` (Zona versetzt) |
| CHR_C02_OOZYTE_CUMULUS (Zona + Samenzelle) | `zona_sperm_v4` nur als Look | Kontrast und Anlagerung von außen stimmen; **Maßstab falsch** (Samenzelle viel zu groß, Zona nur als Sichel) – Modell nach Maß, nicht nach Bild | `v1/v2` (Zelle im Inneren, Virenformen), `v3` (Sichel) |
| CHR_C02_SPERMIUM | `group_v1` nur als Look | Phasenkontrast-Look gut; **Formfehler** (Schwänze laufen zusammen, Köpfe zu spitz). FLUX hält die Anatomie nicht – Modell nach Maßblatt (Kopf 5 × 3 µm, Mittelstück 5 µm, Schwanz 45 µm) | `v2–v4` (zwei Schwänze bzw. Schwanz auf beiden Seiten) |
| CHR_C02_ZYGOTE (Vorkerne) | `pronuclei_v3` | ungefärbt, zwei sich berührende Vorkerne, dicke Zona, Polkörper – stimmig | `v1/v2` (gefärbtes Präparat), `v4` (Vorkerne getrennt) |
| CHR_C02_ZYGOTE (2-Zell) | `two_cell_v1` | zwei gleiche Blastomeren mit Kern, Polkörper, Zona – stimmig; Farbe leicht rosa, Spalt zur Zona etwas breit | `two_cell_v2` (wärmer, unruhiger) |

Grenze: Die verbindlichen Formen entstehen im 3D-Modell nach Maßblatt (Phase 3, Schritt 2), die Bilder legen nur Look, Licht und Materialwirkung fest.
