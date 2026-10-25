# C00 – Referenzentwürfe v1 (CM4, zur Regieabnahme)

Lokal erzeugt mit FLUX.2 klein 4B (ComfyUI, Apache-2.0); Prompt, Seed und Modell-Hashes stehen jeweils in der JSON neben dem Bild. Status: **GENERATED_PREVIEW – nicht abgenommen**. Kanon: GD-2026-10-24-01.

| Asset | Datei | Bewertung |
|---|---|---|
| CHR_C00_MANN | `face34_v2_v1`, `fullbody_front_v2_v1`, `hands_v2_v1` | **aktuell** (Rev. 2, Regie: „älter“): etwa 88, sehr hager, dünnes weißes Haar, gebeugt |
| CHR_C00_MANN | `face34_v1`, `fullbody_front_v1`, `hands_v1` | ersetzt (Ende 70 war zu jung) |
| CHR_C00_TOCHTER | `face34_v1`, `fullbody_front_v1` | Vorschlag Mitte 40, Strickjacke |
| SET_C00_SCHLAFZIMMER_2026 | `wide_neubau_s64_v1` | **bevorzugt** (Rev. 2, Regie: Neubau): weiße Wände, Eichenboden, Kunststofffenster, dunkle Stimmung, kein erkennbares Foto |
| SET_C00_SCHLAFZIMMER_2026 | `mood_00B_neubau_v1` | **bevorzugt** für 00-B im Neubau: sehr alte und jüngere Hand klar verschieden, Foto unscharf |
| SET_C00_SCHLAFZIMMER_2026 | `mood_00D_neubau_s66_v1` | **bevorzugt** für 00-D: Fenster von innen, Rollladen, Regentropfen |
| SET_C00_SCHLAFZIMMER_2026 | `wide_neubau_v1`, `wide_neubau_s65_v1`, `mood_00D_neubau_v1`, `mood_00D_neubau_s67_v1` | verworfen: Foto erkennbar bzw. Fenster von außen / weißer Rahmen |
| SET_C00_SCHLAFZIMMER_2026 | `wide_v1` | ersetzt (Altbau) |
| SET_C00_SCHLAFZIMMER_2026 | `mood_00B_s42_v1` | ersetzt (Altbau, Mann jünger) |
| SET_C00_SCHLAFZIMMER_2026 | `mood_00B_v1`, `mood_00B_s41_v1` | **verworfen**: zwei alte Hände bzw. Foto erkennbar |
| SET_C00_SCHLAFZIMMER_2026 | `mood_00D_v1` | ersetzt (Altbau) |

Grenze: FLUX hält ein Gesicht nicht über mehrere Ansichten identisch. Die verbindliche, für C20 exakt reproduzierbare Figur entsteht erst im 3D-Modell (geplant MetaHuman, Freigabe ausstehend).

## PROPS_C00_FOTOS (2026-10-25, Regie: Bilder in die leeren Rahmen)

Lokal mit FLUX.2 klein 4B (ComfyUI, Apache-2.0) erzeugt, Prompt/Seed/Hashes in der JSON neben jedem Bild. Als gerahmte Fotos im Schlafzimmer eingesetzt (Status `ENGINE_TESTED` als Set-Dressing, Texturen `T_C00_Foto_<Key>`): Ehefrau des Mannes (Garten, späte 1990er), junge Familie mit der Tochter mit etwa 3 Jahren (Film 1984), Nordseestrand bei Sonnenuntergang. Die Gesichter sind bewusst als alte Fotos gehalten und nicht identisch mit den MetaHumans.
