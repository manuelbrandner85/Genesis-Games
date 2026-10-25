# Umsetzungsplan – CR-002 (Samenweg), CR-003 (Seelenaustritt) und Schwangerschaft

**Grundlage:** ScriptLock 1.3 (GD-2026-10-26-02, SHA-256 `2a6de42b…7046`, über den Canon-Import abgelegt), Spielkonzept `design/SCHWANGERSCHAFT_KONZEPT.md` (P1–P6).
**Status:** **ENTWURF – wartet auf Freigabe**, phasenweise wie bei CR-001. Jede Phase endet mit Belegen (Build, Tests, Bilder/Video).
**Stand 2026-10-26:** Dokumentationsregister an 1.3 gebunden (geändert nur C00, C01, C02). Das Laufzeitregister bleibt auf 1.2, bis Phase A den Code umstellt. Läuft parallel weiter: CR-001 Phase 3 (Look der Mikrowelt, Blender-Modelle; Samenzelle fertig, Eizelle im Rohbau).

## Phase A – Technik: Samenweg und Prolog-Anschluss (Code, Graubox)

1. **Skriptversion 1.3** im C++ und Laufzeitregister neu binden (Registry-, Vertrags-, Flow-Tests anpassen).
2. **Samenweg W1–W5** als fünf Streaming-Abschnitte statt einer Karte; je Abschnitt eigene Röhren-/Raumform, Strömung und Hindernisse:
   - W1 Scheide: saures Milieu als Zone, aus dem Gerinnsel zum Muttermund
   - W2 Gebärmutterhals: Kanalnetz mit Sackgassen (Krypten)
   - W3 Gebärmutter: weite Höhle, Kontraktionswellen als Strömung, zwei Eileiterabgänge
   - W4 Übergang/Isthmus: Engstelle, „Rasten“ am Epithel, Zeitsprung Kapazitation, danach Hyperaktivierung
   - W5 Ampulle → Eizelle: die bestehende Schwimmphase
3. **Kein Game Over je Abschnitt:** Steuerungswechsel auf eine andere Zelle desselben Abschnitts (F4); in W5 weiter fremde Verschmelzung.
4. **Abkürzen erst nach dem ersten Mal (F3):** seelenübergreifender Merker „Samenweg erlebt“ im Profil (nicht im Lebens-Spielstand), danach W1–W4 als kurzer Film.
5. **Spielstand Schema 4:** Fortschritt pro Abschnitt, Pause/Fortsetzen innerhalb des Wegs.
6. **Prolog-Anschluss (CR-003):** Lichtpunkt bleibt nach C00 bestehen und geht ohne Schnitt in den Lichtschlag über (Platzhalter bis zum C00-Master).
7. **Tests:** Abschnittsfolge W1→W5, Steuerungswechsel statt Game Over in jedem Abschnitt, Abkürzen gesperrt beim ersten Mal, 120-s-Führung in W5, Spieldauer ohne Eingabe im Fenster 8–12 min (Nachrechnung + PIE mit Zeitraffer).

**Belege:** C++-Build, alle Automationstests, PIE-Durchlauf Prolog-Platzhalter → W1…W5 → Titel.

## Phase B – Technik: spielbare Schwangerschaft (Graubox)

1. **Schwangerschafts-Zustandsmaschine:** zehn Stufen S1–S10 mit Wochenuhr (Tag 1 bis Geburt), Zeitraffer mit Wochenmarke, „Abschnitt abkürzen“ je Stufe (P2), Speichern zwischen den Stufen.
2. **Stadiengerechte Steuerung (P3):** S1–S3 nur Beobachten (Zeitraffer, Lupe, Doku-Modus); ab S4 Bewegungsimpulse, ab S5 strecken/greifen/Daumen/schlucken, ab S6 treten/drehen, ab S7 auf Stimmen/Klopfen reagieren, ab S8 zum Licht wenden – jede Aktion nur, wenn die Woche sie erlaubt (Test je Stufe).
3. **Folgen in der Außenwelt:** Ereignisse („Tritt gespürt“, „Hand auf dem Bauch“) über das bestehende Welt-Ledger, ohne Punktestand.
4. **Anschluss:** C03 bei später Schwangerschaft, C04 bei der Geburt als Szenenverträge (technische Platzhalter bis zur Produktion).
5. **Tests:** Stufenfolge, Aktionen nie vor ihrer Woche, Abkürzen schreibt Woche/Weltzeit konsistent fort, Speichern/Laden in jeder Stufe, keine zufällige Fehlgeburt im ersten Leben (P5).

**Belege:** Build, Tests, PIE-Durchlauf S1→S10 mit Abkürzen.

## Phase C – Figuren des ersten Lebens (deine Entscheidung, P4)

Schwangere Person und Umfeld im ersten Leben: Name, Alter, Lebenssituation, Wohnort 2026, Sprache, Familienmelodie. **Claude erfindet sie nicht** – Vorlage mit Fragen, du entscheidest; danach Referenzbilder und MetaHuman.

## Phase D – Look und Produktion (je eigene Abnahme)

1. Referenzbilder W1–W4 (Scheidenepithel, Zervixschleim-Kanäle, Gebärmutterhöhle, Isthmus) und Embryo/Fötus S1–S9 (anatomisch, keine verstörenden Bilder), lokal mit FLUX.2 klein → Abnahme.
2. Blender-Modelle nach Maßblatt (Scheitel-Steiß-Länge je Woche, Plazenta, Nabelschnur, Fruchtblase, Uterusraum).
3. C00-Seelenaustritt als Licht-/Volumeneffekt (Niagara, Master im Path Tracer), Seelenmotiv-Ton.
4. Reality Check nach Skill „maximum-realism“, Renders, Abnahme.

## Reihenfolge und Grenzen

- Vorschlag: **Phase A + B jetzt** (reine Technik, Graubox, keine Kunst- oder Kanonentscheidung), parallel CR-001 Phase 3 fertigstellen; Phase C sobald du Zeit hast; Phase D je nach Abnahme.
- Die Schwangerschaft mit 2–3 Stunden Spielzeit ist der größte Inhaltsblock bisher; ehrliche Erwartung: Graubox in Phase B, glaubwürdige Optik erst mit Phase D.
- Keine Downloads, keine Cloud; Werkzeuge vorhanden.
