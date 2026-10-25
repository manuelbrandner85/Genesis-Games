# CR-002 – Der komplette Weg der Samenzelle (C01-B, C02-A/B)

| Feld | Wert |
|---|---|
| Antrag | Game Director, 2026-10-26: „… auch als Samen steuern den Weg zur Eizelle von Anfang bis Ende einfach alles“ |
| Grundlage | ScriptLock 1.2 (GD-2026-10-25-01, CR-001) |
| Betrifft | C01 (SHOT 01-B), C02 (Ort, Länge, SHOT 02-A, SPIELPHASE 02-B), Entscheidung **E4** aus CR-001 |
| Unverändert | C00, C01-A (Lichtschlag), C02-C bis 02-F, C03–C21, C15/C16 CON33-01, C17-Epochenwortlaut, C21-Finale, alle gesperrten Regeln IV.A |
| Status | **ENTWURF – wartet auf Freigabe** („JA zu CR-002“ bzw. „JA zu CR-002 mit …“) |

## Was sich ändert

| Stelle | ScriptLock 1.2 heute | Vorschlag 1.3 |
|---|---|---|
| C01-B | Aus dem Weiß schält sich das Relief des **Eileiters** | Aus dem Weiß schält sich die **Scheide** kurz nach der Samenablage (Startpunkt, siehe F1) |
| C02 Ort | Eileiter-Ampulle | gesamter Weg: Scheide → Gebärmutterhals → Gebärmutter → Übergang in den Eileiter → Isthmus → Ampulle → Cumulus → Zona |
| C02-A | 12 s Kamerafahrt durch Tubenfalten | 12 s Orientierung am Startpunkt mit Einblendung „Scheide – mikroskopische Darstellung \| Zeitmaßstab: beschleunigt“ |
| C02-B | 60–120 s Pflicht-Schwimmphase im Eileiter | **Pflicht-Weg in fünf Abschnitten**, zusammen ca. 8–12 min (F2); die letzte Annäherung an die Eizelle bleibt 60–120 s |
| E4 | 60–120 s | ersetzt durch F2 (Gesamtweg) + F3 (Abkürzen) |

Alles andere aus 02-B gilt weiter: Simulationsperspektive ohne Gedanken, Gefühle oder Stimme; **kein Wettrennen** (keine Platzierung, kein Timer); **kein Game Over** (erreicht die gesteuerte Zelle die Eizelle nicht, verschmilzt eine andere und die Szene läuft weiter); Hilfe „automatisch schwimmen“; pausierbar.

## Die fünf Abschnitte (biologisch begründet)

| # | Abschnitt | Was dort wirklich passiert | Spielmechanik (Vorschlag) | Spielzeit |
|---|---|---|---|---|
| W1 | Scheide | saures Milieu; das Ejakulat gerinnt kurz und schützt; die meisten Zellen gehen hier verloren | aus dem Gerinnsel heraus Richtung Muttermund schwimmen, Säure meiden | 1–2 min |
| W2 | Gebärmutterhals | Schleim mit Kanälen (Mikrostruktur je nach Zyklustag); Krypten speichern Zellen | den Kanälen folgen, Sackgassen (Krypten) erkennen | 2–3 min |
| W3 | Gebärmutter | weite Höhle; Muskelkontraktionen tragen Zellen in Minuten zum Eileiterabgang | Strömung/Kontraktionen nutzen, die richtige Seite (Eileiter mit Eizelle) finden | 1–2 min |
| W4 | Übergang + Isthmus | enge, gewundene Stelle; Zellen binden ans Epithel („Reservoir“) und reifen (Kapazitation, real Stunden → **Zeitsprung mit Einblendung**) | durch die Engstelle, an der Wand „rasten“, danach Hyperaktivierung = kräftigerer Schlag | 2–3 min |
| W5 | Ampulle → Cumulus → Zona | bestehende Phase (CR-001) | wie heute | 1–2 min |

Die Zahl der sichtbaren Mitschwimmer nimmt von Abschnitt zu Abschnitt ab (real: Millionen → einige Hundert im Eileiter); das wird nur gezeigt, nie gezählt oder bewertet.

## Entscheidungen für den Game Director

| # | Frage | Vorschlag |
|---|---|---|
| F1 | Wo beginnt der Weg? | **In der Scheide kurz nach der Samenablage.** Der Geschlechtsakt und der Körper des Mannes werden **nicht** gezeigt (Altersfreigabe, Würde, ScriptLock-Regel „kein grafisch ausbeuterischer Blick“). |
| F2 | Wie lang ist der Pflicht-Weg? | **ca. 8–12 min** Spielzeit gesamt (Abschnitte s. o.), sichtbare Zeitraffer-Marken |
| F3 | Muss man den ganzen Weg jedes Mal spielen? | **Beim ersten Mal ja (Pflicht).** Bei jedem weiteren Lebensbeginn bietet das Spiel „Weg abkürzen“ an (W1–W4 als kurzer Film, W5 bleibt spielbar). |
| F4 | Was passiert, wenn die Zelle in einem Abschnitt „verloren geht“ (z. B. in einer Krypta hängen bleibt)? | Kein Game Over: Die Kamera wechselt auf eine andere Zelle desselben Abschnitts, die Steuerung geht auf sie über; erst W5 kann mit fremder Verschmelzung enden (wie heute). |
| F5 | Lerntexte? | Optional im Dokumentationsmodus (sachliche Einblendungen je Abschnitt), sonst nur Ortsangabe. |

## Technische Folgen (eigene Freigabe nach dem JA)

- ScriptLock **1.3** (vorbereitet von Claude, abgelegt über den geprüften Canon-Import), Registerbindung an 1.3
- Spielstand: Fortschritt pro Abschnitt (Schema 4), Abkürz-Option nach dem ersten Mal
- Schwimmkarte → fünf Abschnitte (Streaming-Level), Strömungsfelder je Abschnitt, Graubox zuerst, danach Look wie Phase 3
- Neue Referenzbilder und Modelle: Scheidenepithel, Zervixschleim-Kanäle, Gebärmutterhöhle, Isthmus
- Tests: Abschnittsfolge, kein Game Over in jedem Abschnitt, Abkürzen erst nach dem ersten Mal, 120-s-Regel in W5

**Freigabe:** „JA zu CR-002“ (mit den Vorschlägen F1–F5) oder „JA zu CR-002 mit …“.
