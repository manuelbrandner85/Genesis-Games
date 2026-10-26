# C02 – Blender-Modelle der Mikrowelt (CR-001 Phase 3, Schritt 2)

Eigene Modelle (keine Fremdassets), gebaut per Skript nach `docs/v4_2/C02_MASSBLATT.md`, Maßstab **1 Blender-Einheit = 1 µm = 1 Unreal-Einheit** (Szene `scale_length` 0,01; FBX in cm). Datei `C02_Mikrowelt.blend`, Exporte in `Export/`.

| Asset | Skript | Inhalt | Prüfbild (`docs/evidence/C02_Blender/`) |
|---|---|---|---|
| SM_C02_Spermium | `tools/v4_2/c02_build_sperm.py` | Kopf 4,1 × 2,8 × 1,1 µm mit Akrosom-Kappe (weiche, gebogene Grenze) und körnigem Kern, Hals, Mittelstück mit Mitochondrienwendel, Haupt- und Endstück, gesamt 58 µm; UV2 „TailWave“ für den Geißelschlag in Unreal | `spermium_hell`, `spermium_kopf_hell` |
| SM_C02_Oozyte (+ Zona, Polkörper) | `c02_build_oocyte.py` | Eizelle 115 µm, perivitelliner Spalt, Zona 16 µm (außen 155 µm), Polkörper 12 µm | `oozyte_nackt_hell` |
| SM_C02_CumulusZelle + `C02_Cumulus_Instanzen.json` | `c02_build_oocyte.py` | Zelle 12 µm mit Kern; 2 500 Instanzen (Corona dicht auf der Zona, Cumulus-Wolke bis 400 µm) | `oozyte_spielersicht_dunkel` |
| SM_C02_Eileiter | `c02_build_ampulla.py` | kachelbares Stück 1,4 mm, Lumen 520 µm, 22 verzweigte Längsfalten + Nebenfalten | `eileiter_innen_dunkel` |
| SM_C02_Zygote | `c02_build_zygote.py` | Zygote mit zwei aneinanderliegenden Vorkernen (22 µm, je 5 Nukleolen), zwei Polkörper | `zygote_hell` |
| SM_C02_Zweizell | `c02_build_zygote.py` | zwei von der Zona abgeflachte Blastomeren (60 × 104 × 112 µm) mit Kern | `zweizell_hell` |

**Prüfung:** FBX-Rückimport misst Samenzelle 57,98 uu, Zona 155 uu, Eileiterstück 1400 uu. Brechzahlen relativ zur Flüssigkeit (siehe Maßblatt) – mit absoluten Werten in Luft wirkten die Zellen wie Glaslinsen (behoben).

**Nachbesserung (Regie 2026-10-26: „Cumuluszellen und Faltenkämme nachbessern“):**
- Cumuluszellen: glatte, unregelmäßige Ovale statt Kugeln (großflächige Verformung), stärker streuendes Zellinneres und dichterer Kern, dazu die klare Gelmatrix (Hyaluronsäure) als feiner Dunst um die Eizelle (`SM_C02_CumulusMatrix`). Der frühere Glasperlen-Eindruck kam von Brechzahlen wie in Luft.
- Eileiter: Die „Zahnspitzen“ waren die abgeschnittenen Enden des Teststücks – geprüft in einer Kette aus drei Stücken wie im Spiel sind sie weg. Die Falten sind jetzt an den Kämmen flacher und runder und neigen sich wie weiches Gewebe; die Neigung wird nach dem Anteil jeder Falte gemischt (vorher rissen Netzstellen, wo eine Seitenfalte in ihre Falte überging).

**Ehrliche Grenzen:** Die Volumen-Materialien sind Blender-Prüfmaterialien; im Spiel entsteht der Look über durchscheinende Unreal-Materialien (nächster Schritt). Kerne der Cumuluszellen sind in der Spielersicht noch kaum zu sehen. Status: Modelle **GENERATED_PREVIEW**, noch nicht in Unreal importiert, nicht abgenommen.
