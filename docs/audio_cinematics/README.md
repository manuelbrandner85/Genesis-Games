# GENESIS Audio & Cinematics – Arbeitsunterlagen

> **Intern. Enthält Story-Details zu C19/C20. Nicht in öffentliche Texte, Trailer, Store-Seiten oder UI übernehmen.**

Quelle für alles: `GENESIS_ScriptLock_11_Drehbuch_v1.1.md` (Release `handover-v62`, V61-Quellpaket). Status des Drehbuchs: Script-Lock-*Kandidat*, Endfreigabe ausstehend. Es gibt noch keine Aufnahmen, keine Musik und keine Renderings.

| Datei | Inhalt |
|---|---|
| `genesis_sprachzeilen_C00-C21.csv` / `.xlsx` | 195 Sprachzeilen mit IDs, Shot-Zuordnung und **vorläufigen, geschätzten** Zeitcodes |
| `C00_C01_ANIMATIC_SCHNITTPLAN.md` | Animatic- und Schnittplan C00/C01, Freeze-Liste für C20, Nachweisverfahren |
| `ENTSCHEIDUNG_C20_LAENGE_SHOT_20-B.md` | Entscheidungsvorlage für Manuel zum 75-s/60-s-Problem |
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
- **C15 und C16** (15 Zeilen): keine Zeitcodes, Status `zurückgestellt, Kanon-Entscheidung CON33-01 offen`.
- Keine Zeile überschreitet nach dieser Schätzung ihr Shot-Ende.
