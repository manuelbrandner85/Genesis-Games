# CR-002 – C00/00-B: Bücher statt Fotografie auf dem Nachttisch

| Feld | Wert |
|---|---|
| Antrag | CR-002 · Drehbuch ScriptLock 1.2 → **1.3** (nach Freigabe) |
| Gestellt von | Game Director, 2026-10-25: „Entferne das Foto vom Nachttisch und leg die Bücher dorthin. Ich will das als Kanonänderung für 00-B, schreib dafür einen Änderungsantrag.“ |
| Grundlage | ScriptLock 1.2, Abschnitt IV.D (Änderungen nur über versionierte Anträge mit Szenen, Dialog-IDs, Triggern, Musik, Save-Migration) · Sperre GD-2026-10-24-01 · Shotliste C00 freigegeben 2026-10-25 |
| Status | **ENTWURF – zur Regieabnahme.** Der Canon (ScriptLock) bleibt bis zur Freigabe unverändert. Das Set ist als technische Vorschau bereits umgebaut (rückbaubar, siehe 7). |
| Öffentliche Fassung | nur IDs und Auswirkungen. Der genaue neue Shottext liegt lokal in `canon_proposals/CR-002/` (nicht im Repo). |

## 1. Was sich ändert

| Szene / Shot | heute (1.2) | neu (1.3) |
|---|---|---|
| **00-B** Detail / Hände | Fokus wandert zu einer alten **Fotografie** auf dem Nachttisch, Inhalt noch nicht erkennbar | Fokus wandert zu einem kleinen **Bücherstapel** auf dem Nachttisch (dort, wo bisher das Foto stand). Hände, Daumen, Ton, 85 mm, Länge unverändert |
| **20-B** Das Schlafzimmer | Match-Cut auf 00-B/00-C mit „gleicher Fotografie“ | gleicher Match-Cut, „gleiche Bücher“ statt „gleiche Fotografie“. C20 spielt die C00-Aufnahme weiter bild- und tonidentisch ab, die Änderung folgt also automatisch |
| C00 übrige Shots, C01–C19, C21 | – | unverändert |

**Fundstellen im ScriptLock 1.2:** Die Fotografie kommt nur in 00-B und 20-B vor. Andere Szenen nennen sie nicht. (09-A „Foto“ meint allgemein Gegenstände späterer Leben, nicht dieses Bild.)

**Offener Punkt (Risiko):** 00-B sagt, der Inhalt des Fotos dürfe *„noch nicht“* erkennbar sein. Das deutet auf eine geplante spätere Auflösung hin. Im ScriptLock 1.2 gibt es aber keine Szene, die das Motiv zeigt oder auflöst. Falls eine solche Auflösung außerhalb des ScriptLocks geplant war (Bibel, Notizen), entfällt sie mit diesem Antrag.

## 2. Entscheidungen für die Regie

| | Frage | Vorschlag |
|---|---|---|
| **E1** | Sind die Rückentitel im Fokus von 00-B lesbar? | **Ja, gerade so lesbar** (Easter Egg, siehe E2). Das Spiel verrät damit nichts über die Geschichte |
| **E2** | Welche Titel? | „GENESIS – Roman“, „Der letzte Augenblick“ (Arbeitstitel von C00), „Atlas 2026“ (das Jahr, in dem das erste Leben beginnt). Keine Titel, die Seele, Jenseits oder Wiedergeburt andeuten (keine vorzeitige C19/C20-Enthüllung) |
| **E3** | Bleibt sonst ein persönlicher Gegenstand auf dem Nachttisch? | Glas Wasser und Medikamentenschachtel bleiben. Kein neues Kanonobjekt |

## 3. Dialog-IDs

Keine Änderung (VO_C00_001–008 und SUB_C00_001–008 bleiben).

## 4. Trigger / Ablauf

Keine Änderung (MENU_FLOW, Szenenverträge, Überspringen mit Zweifachbestätigung bleiben).

## 5. Musik und Ton

Keine Änderung.

## 6. Spielstand-Migration

Keine. C00 ist ein vorgerenderter Film ohne Spielzustand.

## 7. Technische Folgen

- **Set (bereits umgesetzt, technische Vorschau):** `tools/v4_2/build_c00_bedroom.py` baut den Bilderrahmen nicht mehr (`NIGHTSTAND_PHOTO = False`), `tools/v4_2/build_c00_nightstand.py` stellt die Bücher an seine Stelle. **Rückbau:** `NIGHTSTAND_PHOTO = True` und die Buchposition zurücksetzen.
- **00-B-Sequenz:** `tools/v4_2/c00_seq_00b.py` zieht den Fokus auf die Bücher statt auf das Foto.
- **Nach Freigabe:** ScriptLock 1.3 über den geprüften Canon-Import ablegen und das Szenenregister an 1.3 binden (`tools/v4_2/bind_scriptlock.py`).
