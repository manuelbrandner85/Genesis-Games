# Untertitel und Bildschirmtexte – Regeln

> **Intern – enthält Details zu C19/C20.**
> Liste aller gelesenen Texte: `genesis_bildschirmtexte.csv` (38 Einträge, IDs `TXT_<Szene>_<Nr>`). Untertitel zu gesprochenen Zeilen: `SUB_…` in `genesis_sprachzeilen_C00-C21.csv`.
> Zeitcodes in Filmen: 24 fps, ab Szenenbeginn, **vorläufig/geschätzt** (Shot-Start aus dem Drehbuch + 1 s, Dauer = Zeichen ÷ 15 + 0,5 s, mindestens 1,5 s). Menüs und Auswahlpunkte sind interaktiv und haben keinen Filmzeitcode.

## Feste Vorgaben aus dem Drehbuch
- Jeder Sprach-Cue hat `AudioCueID`, `SubtitleID`, `TimecodeStart`, `TimecodeEnd`, `SpeakerID`, `Locale`, `VariantID`.
- Untertitel und Wave müssen zeitlich übereinstimmen (Synchronisationstest C.1).
- Untertitel dürfen **vor C19 weder „Kollektiv“ noch „SoulSeed“** zeigen. Die Stimme heißt bis dahin nur „STIMME“.
- Untertitel und Lebensarchiv zu C19 erst nach Freischaltung (V61-N13-008).
- In C15 kein Untertitel, der schon „Jenseits“ erklärt.
- Einstellungen: Untertitel, Sprache, Textgröße, Kontrast, Untertitel-Sprecher, Lesetempo (Drehbuch, Abschnitt D).
- Variablen `{{…}}` müssen vor der Anzeige grammatisch vollständig aufgelöst sein.

## Regeln (Annahmen, wo das Drehbuch nichts sagt)
| Regel | Wert | Grund |
|---|---|---|
| Zeichen pro Zeile | höchstens **42** | übliche Norm für deutsche Untertitel |
| Zeilen pro Untertitel | höchstens **2** | Lesbarkeit |
| Lesegeschwindigkeit | höchstens **17 Zeichen/s** Standard; **13 Zeichen/s** bei Einstellung „langsames Lesetempo“ | übliche Norm; Drehbuch fordert Lesetempo-Option |
| Standzeit | mind. **20 Frames (0,83 s)**, höchstens **7 s** | Lesbarkeit |
| Abstand zwischen zwei Untertiteln | mind. **2 Frames** | Flackern vermeiden |
| Schnitt | Untertitel nicht über einen harten Bildschnitt ziehen, wenn vermeidbar | Lesbarkeit |
| Zeilenumbruch | nach Sinneinheiten, nicht zwischen Artikel und Nomen | Lesbarkeit |
| Sprecherkennung | Name in Großbuchstaben nur, wenn der Sprecher nicht im Bild ist oder mehrere sprechen, z. B. `TOCHTER:`; Off-Stimmen kursiv | Barrierefreiheit |
| Bezeichnungen vor C19 | „STIMME“, nie „Kollektiv“; C19 ab Shot 19-C: „STIMME A/B/C“, „STIMMEN“ | Spoilerschutz |
| Spieler-Echo | „ECHO“ (Annahme), nicht der Name aus dem letzten Leben | Drehbuch: neutrales Stimmprofil |
| Geräuschbeschreibungen (Hörgeschädigte, optional) | in eckigen Klammern, z. B. `[Regen]`, `[Atem endet]`, `[zwei leise Töne]` | Barrierefreiheit |
| Spoiler in Geräuschbeschreibungen | nie deuten, z. B. nicht „[Soul-Motiv]“, sondern „[zwei leise Töne]“ | Spoilerschutz |
| Musik in Beschreibungen | `[ruhige Musik]`, keine Titel fremder Lieder ohne geklärte Rechte | Rechte |
| Bildschirmtexte (Titel, Nachrichten) | werden **nicht** zusätzlich untertitelt; bei Screenreader-Option vorlesen | Barrierefreiheit |
| Größe und Kontrast | mind. 3 Größen; Hintergrundbox mit einstellbarer Deckkraft; Kontrast mind. 4,5 : 1 | Barrierefreiheit |
| Position | unten mittig; nach oben ausweichen, wenn UI unten liegt | Lesbarkeit |

## Prüfung der vorhandenen Sprachzeilen gegen diese Regeln
- **8 Zeilen länger als 84 Zeichen** (passen nicht in 2 × 42): VO_C06_001, VO_C10_004, VO_C10_005, VO_C10_006, VO_C11_006, VO_C19_015, VO_C20_026, VO_C20_032. Sie werden in **zwei aufeinanderfolgende Untertitel** geteilt (Text bleibt gleich).
- **4 Zeilen schneller als 17 Zeichen/s** nach den geschätzten Zeiten: VO_C07_008, VO_C13_003, VO_C13_006, VO_C20_023. Neu prüfen, sobald echte Aufnahmen vorliegen; die Schätzung kann sich ändern.
