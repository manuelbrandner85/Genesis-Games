# G6 – Flussdorf: Werkstatt-Kette (Arbeitsplan)

Status der Quellen: **Arbeitskanon, Kandidat, nicht endfreigegeben** (G1, `docs/v4/CANON_SOURCE_REGISTER.json`).
Alles, was die Quellen offen lassen, ist hier als **Startwert** markiert und kein Kanon.

## 1. Quellen

| ID (Register) | Verwendet für |
|---|---|
| `WELTBIBEL_FLUSSDORF` | Regionen R01, R02, R03, R07, Wegefolge, Dauerzustände, Spielerfigur = erwachsener Testcharakter |
| `V24_NPC_UND_EREIGNISSIMULATION` | N01, N02, N03: Basis, Privatort, Routine, Ziele, Grenzen, Gedächtnis; Wissen getrennt in beobachtet / gehört / geprüft; Datenvertrag; Save-Gates |
| `V48_KANON_NPCS_UND_ORTSBINDUNG` | N01 = Generator-Arbeit mit gültiger Teile-/Material-/Bezahllogik |
| `V24_MISSIONSBIBEL` | Kette A (Werkstatt), S24-02 „Der Preis der Hilfe“, Beispielvergütung 60 GE, Teil 18 GE, Fehlerfälle |

## 2. Umfang G6 (Gate: 3 Rollen, Tagesplan, Dialogkonsequenz, Save/Load, keine Softlocks)

**Regionen (Graybox):** R01 Dorfplatz, R02 Markt, R03 Werkstatt, R07 Wohnhäuser. Wegefolge laut Quelle: Werkstatt ↔ Markt ↔ Dorfplatz, Häuser an Dorfplatz angebunden. R04 Brücke und weitere Regionen bleiben außerhalb von G6.

**NPCs (laut Quelle):**

| NPC | Basis | Privat | Routine | Grenze |
|---|---|---|---|---|
| N01 Werkstattbesitzer/in | R03 | R07 | 09:00–17:00 Arbeit, danach privat | keine unsichere Reparatur, keine Zusage ohne Teile |
| N02 Reparaturkund/in | R02 | R07 | vormittags Erledigungen, Termin nur nach Vereinbarung | kann Kostenvoranschlag ablehnen oder zurückziehen |
| N03 Marktbetreiber/in | R02 | R07 | 08:00–18:00, nur wenn der Laden geöffnet ist | verkauft keine reservierten oder fehlenden Waren |

**Auftrag (Kette A / S24-02):**
1. N02 legt einen Generator-Auftrag vor (nur während N02 am Markt ist).
2. Spieler: **annehmen** · **an N01 verweisen** · **ablehnen**. N02 darf den Preis ablehnen oder zurückziehen.
3. Diagnose am Generator in R03: mindestens **zwei plausible, prüfbare Ursachen**; Beobachtung statt Minispiel.
4. Teil am Markt bei N03: **18 GE**, nur wenn vorrätig und Geld reicht; Reservierung bei Zusage.
5. Reparatur → Abnahme durch N02 → **60 GE genau einmal** (Beispielvergütung laut Quelle).
6. Fehlerfälle: Kundin geht, Teil fehlt, Spielstand neu geladen → Auftrag behält nachvollziehbaren Status, **keine Doppelvergütung**.
7. Ablehnung/Verweis ist ein vollwertiges Ende: N02 handelt selbst (geht zu N01 oder lässt es). **Keine Sackgasse.**

## 3. Startwerte (nicht aus der Quelle, als solche markiert)

| Punkt | Startwert | Grund |
|---|---|---|
| Geräte-Fehler, zwei Ursachen | (a) verbrauchte Zündkerze, (b) verstopfter Kraftstofffilter – sichtbar/prüfbar | Quelle verlangt „zwei plausible, prüfbare Ursachen“, nennt keine |
| Teil am Markt | Zündkerze 18 GE, Bestand 1 | Quelle nennt 18 GE, nicht welches Teil |
| Startgeld Spieler | 40 GE | reicht für das Teil, nicht für Verschwendung |
| Spielstart | Tag 1, 08:30 Uhr | N03 hat geöffnet, N02 vormittags am Markt, N01 ab 09:00 |
| Zeitraffer | 1 Echtminute = 10 Spielminuten | 30–45-Minuten-Slice deckt einen Vormittag bis Nachmittag ab |
| NPC-Aussehen | Mannequin-Platzhalter Manny/Quinn | keine freigegebenen Gesichter |
| Namen der NPCs | keine – nur Rollen | Quelle nennt keine Namen |

## 4. Arbeitspakete

| WP | Inhalt | Abnahme |
|---|---|---|
| 6.1 | Weltuhr (Tag, Uhrzeit, Zeitraffer, Pause), Spielstand mit Transaktion (Temp-Datei → prüfen → austauschen) | Automationstests: Zeit, Speichern/Laden verlustfrei, Abbruch beim Schreiben |
| 6.2 | Graybox R01/R02/R03/R07 mit Wegen, NavMesh, Wegweiser | begehbar, NavMesh deckt alle Wege, Maße plausibel |
| 6.3 | N01–N03: Tagesplan, Wege per NavMesh, Wissen nur aus Wahrnehmung | Test: Zeitraffer 08:00→18:00, jede Figur an ihrem Ort |
| 6.4 | Gespräch, Auswahl, Auftrag, Diagnose, Kauf, Reparatur, Abnahme | Tests aller Wege inkl. Ablehnung/Verweis |
| 6.5 | Speichern/Laden in jedem Auftragsschritt, Idempotenz | keine Doppelvergütung, keine Sackgasse (alle Zustände erreichen ein Ende) |
| 6.6 | Spieltest im Editor, Menschentest | PIE-Durchlauf + deine Abnahme |

## 5. Nicht in G6

Brücke, Wetter, Warnung (Ketten B/C), Generationenlabor, Seelenmechanik, C-Szenen, freie KI-Dialoge, Fotorealismus der Graybox (kommt mit G7).
