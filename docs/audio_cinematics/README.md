# GENESIS Audio & Cinematics – Arbeitsunterlagen

> **Intern. Enthält Story-Details zu C19/C20. Nicht in öffentliche Texte, Trailer, Store-Seiten oder UI übernehmen.**

Quelle für alles: `GENESIS_ScriptLock_11_Drehbuch_v1.1.md` (Release `handover-v62`, V61-Quellpaket). Status des Drehbuchs: Script-Lock-*Kandidat*, Endfreigabe ausstehend. Es gibt noch keine Aufnahmen, keine Musik und keine Renderings.

| Datei | Inhalt |
|---|---|
| `genesis_sprachzeilen_C00-C21.csv` / `.xlsx` | 200 Sprachzeilen mit IDs, Shot-Zuordnung und **vorläufigen, geschätzten** Zeitcodes |
| `C00_C01_ANIMATIC_SCHNITTPLAN.md` | Animatic- und Schnittplan C00/C01, Freeze-Liste für C20, Nachweisverfahren |
| `ENTSCHEIDUNG_C20_LAENGE_SHOT_20-B.md` | Entscheidung zu Shot 20-B (**entschieden 23.10.2026**: volle 60 s Reprise + 15 s stiller Übergang) |
| `genesis_bildschirmtexte.csv` + `UNTERTITEL_REGELN.md` | 38 gelesene Texte (Titel, Erklärtexte, Menüs, Auswahlpunkte, Nachrichten) und Untertitel-Regeln |
| `MUSIKPLAN_M01-M12.md` | Musikplan, Soul-Intervall-Spezifikation, Regel für M03 |
| `genesis_geraeusche_ui_klaenge.csv` + `GERAEUSCHE_UI_KLAENGE.md` | 77 Geräusche, V33-Cues und Audio-/UI-Anforderungen mit Länge, Lautheit, Bus, Quelle/Lizenz |
| `RECHTE_CHECKLISTE.md` | 20 Rechte-Punkte, alle offen |
| `werkzeuge/paket2.py` | erzeugt Bildschirmtext- und Geräuschliste |
| `werkzeuge/build.py`, `werkzeuge/timing.py` | Skripte, mit denen die Liste erzeugt wurde (erwarten das Drehbuch als `drehbuch.md`) |

## Wie die Zeitcodes geschätzt wurden
- Format `HH:MM:SS:FF` bei 24 fps, gerechnet ab Szenenbeginn (00:00:00:00 = erstes Bild der Szene).
- Start und Ende jedes Shots stammen aus dem Drehbuch (Spalten `Shot-Start`/`Shot-Ende`).
- Erste Zeile beginnt 1,0 s nach Shot-Beginn.
- Sprechdauer = Wörter ÷ 2,3 Wörter/s + 0,4 s (ruhiges, filmisches Sprechtempo).
- 0,6 s Lücke zwischen zwei Zeilen.
- Regie-Pausen aus dem Drehbuch werden addiert: „Acht Sekunden Stille“ = 8 s, „Drei Sekunden“ / „Längere Pause“ = 3 s, sonstige Pausen- oder Handlungsbeats = 1,5 s.
- Alternativen (Option A/B/C …) aus derselben Drehbuchzeile teilen sich denselben Zeitplatz; das Ende richtet sich nach der Option selbst.
- Jede Zeile trägt `vorläufig/geschätzt`. Die echten Zeiten entstehen erst durch Aufnahme und Schnitt („Performance und Sprache entscheiden über den finalen Rhythmus“, Drehbuch).
- **C15 und C16** (15 Zeilen): laut Kanon-Entscheidung CON33-01 freigegeben, mit Räumen und Bibliothek wie im ScriptLock. Sie haben jetzt vorläufige Zeitcodes nach derselben Methode.
- **C20, Shot 20-B:** Nach der Entscheidung vom 23.10.2026 enthält 20-B alle 8 C00-Zeilen im Originalton (VO_C20_004 … 011, keine Neuaufnahme). Ihre Zeiten sind die C00-Zeiten + 55,5 s (7,5 s Übergang hinein angenommen). Dadurch sind die C20-IDs ab VO_C20_004 neu nummeriert (C20 hat jetzt 38 statt 33 Zeilen). Es gibt noch keine Aufnahmen, deshalb ist die Umnummerierung unkritisch.
- Keine Zeile überschreitet nach dieser Schätzung ihr Shot-Ende.

## Annahmen im Paket 2 (Manuel: „mach alles automatisch“)
- Untertitel: 42 Zeichen/Zeile, 2 Zeilen, 17 Zeichen/s (13 bei langsamem Lesetempo), 0,83–7 s Standzeit.
- Lautheit: Gesamtmix -24 LUFS integriert, ≤ -1 dBTP; UI -26 LUFS, ≤ -3 dBTP.
- Soul-Intervall: **offene Kanon-Entscheidung A-M1** (Widerspruch „zwei Töne“/„zwei Intervalle“ im Drehbuch). Arbeitsvorschlag „zwei Töne“, Beschluss durch Story & Kanon offen.
- Instrumentierung im Musikplan ist Vorschlag, kein Kanon.
- Zeitcodes der Bildschirmtexte: vorläufig/geschätzt; C02-„Zygote“ ohne Zeit (Shot-Zuordnung offen).

## Anbindung an den M00-Plan
| Datei | WorkID | QAEvidenceID | Status |
|---|---|---|---|
| `genesis_bildschirmtexte.csv`, `UNTERTITEL_REGELN.md` (Untertitel) | WK-M07-002 | `EV-WK-M07-002` | `PLANNED`, Aufnahmen `SOURCE_MISSING` |
| `genesis_bildschirmtexte.csv` (Menü-/UI-Texte) | WK-M07-003 | `EV-WK-M07-003` | `PLANNED` |
| `genesis_geraeusche_ui_klaenge.csv`, `GERAEUSCHE_UI_KLAENGE.md` | WK-M07-002 (Cues), WK-M07-003 (UI) | `EV-WK-M07-002` / `EV-WK-M07-003` | `SOURCE_MISSING` |
| `MUSIKPLAN_M01-M12.md` | WK-M07-004 (neu vorgeschlagen) | `EV-WK-M07-004` | `PLANNED`; A-M1 `BLOCKED` (Kanon) |
| `RECHTE_CHECKLISTE.md` | WK-M07-002 (Rechteteil) | `EV-WK-M07-002` | `BLOCKED` |

SHA256 aller Dateien dieses Pakets: `docs/evidence/WK-M07-002/pr5_dateien.json`. Reviewer: `OFFEN`.
