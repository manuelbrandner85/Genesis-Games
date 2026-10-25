# GENESIS – Beschlüsse des Game Directors

Nur Beschlüsse, die der Game Director selbst im Chat getroffen hat. Claude Code erstellt hier keine Freigaben, sondern protokolliert den Wortlaut und den Umfang.

## GD-2026-10-24-01 – Script-Lock „Vorschlag 11“ (ScriptLock 1.1)

| Feld | Wert |
|---|---|
| Datum | 2026-10-24 |
| Frage von Claude Code | „Gibst du ScriptLock 1.1 frei („JA zu Vorschlag 11“)? Dann beginne ich mit dem echten C00. Sonst mache ich mit Tastenbelegung, gepacktem Windows-Build und Controller-Test weiter.“ |
| Antwort des Game Directors | „Ja“ |
| Quelle | `canon_sources/scriptlock/GENESIS_ScriptLock_11_Drehbuch_v1.1.md` (lokal, nicht im Repo) |
| SHA-256 der Quelle | `b23a047b13c1a7d77d00679c757f4fbcaa6cfc3e736305a7f77152c072ce732d` |

**Was der Beschluss bewirkt (ScriptLock IV.D):**
- Der Kanon C00–C21 ist inhaltlich gesperrt: Szenen, Reihenfolge, Dialoge und die gesperrten Regeln IV.A.
- Änderungen sind nur noch über versionierte Änderungsanträge möglich. Ein Antrag nennt Szenen, Dialog-IDs, Trigger, Musik und Save-Migration.
- Das Szenenregister steht für alle 22 Szenen auf `DIRECTOR_APPROVED`, die Laufzeit erlaubt kanonische Szenenverträge.
- Die Referenzbildplanung für Figuren, Sets und Licht darf beginnen (ScriptLock III.G).

**Was der Beschluss NICHT bewirkt:**
- Er ist **keine** automatische Referenz-, Asset-, Code- oder Produktionsfreigabe (IV.D).
  - Die technische Produktionsfreigabe braucht separat Ressourcenplan, Vorfilm-Migration, Replay-/Cinematic-Systeme, Performance-Profil und Assetplan.
  - Sie wird pro Szene als CM4-Abnahme eingeholt.
- Offene Konflikte bleiben `WAITING_DIRECTOR_DECISION` und blockieren ihre Szenen weiter:
  - C15/C16 CON33-01
  - C17 (Epochenwortlaut)
  - C21 (Finalkonflikt)
- Downloads, Installationen und Plugins (z. B. MetaHuman, Sprach- und Musikmodelle) brauchen weiter je eine eigene Freigabe (V4.1).

**Bekannte Quellenlücken:** `Docs/33_Der_Vorfilm.md` (bisheriger 121,5-s-Vorfilm, 52-s-Fallback) und `Docs/31_Bildsprache.md` liegen lokal nicht vor. Das ScriptLock verweist auf beide. Bis sie vorliegen, gelten nur die Angaben im ScriptLock selbst.

## GD-2026-10-24-02 – Abnahme C00-Referenzentwürfe Rev. 2

| Feld | Wert |
|---|---|
| Datum | 2026-10-24 |
| Vorlauf | Regie: „Der Mann: älter, Das Schlafzimmer neubau“ → Rev. 2 (Commit e335ab9) |
| Antwort des Game Directors | „Rev. 2 abgenommen, MetaHuman freigegeben.“ |
| Umfang | Bevorzugte Entwürfe laut `ArtSource/Reference/C00/README.md`: Mann etwa 88 (`face34_v2`, `fullbody_front_v2`, `hands_v2`), Tochter Mitte 40 (`face34_v1`, `fullbody_front_v1`), Neubau-Schlafzimmer (`wide_neubau_s64`, `mood_00B_neubau`, `mood_00D_neubau_s66`) |
| Bedeutung | Look-Vorgabe für Modellierung und Set. Die verbindliche Figur ist erst das 3D-Modell, das wieder abgenommen wird. |

## GD-2026-10-24-03 – MetaHuman freigegeben

| Feld | Wert |
|---|---|
| Datum | 2026-10-24 |
| Antwort des Game Directors | „Rev. 2 abgenommen, MetaHuman freigegeben.“ |
| Umfang | Aktivieren der mit UE 5.8.3 **bereits installierten** MetaHuman-Plugins im Projekt (kein Download), Plan `docs/v4_1/install_plans/FA-METAHUMAN-001.json` |
| Nicht enthalten | **Epic-Cloud-Dienste** des MetaHuman Creators (Gesichts-Auto-Rigging, Hauttextur-Synthese): Sie senden Gesichtsdaten an Epic und brauchen eine Anmeldung mit dem Epic-Konto des Game Directors. Das ist eine eigene Freigabe (Typ EXTERNAL_API, standardmäßig gesperrt). Claude Code meldet sich nirgends an. |

## GD-2026-10-25-01 – Änderungsantrag CR-001 (Anfang: Lichtschlag, Pflicht-Schwimmphase)

| Feld | Wert |
|---|---|
| Datum | 2026-10-25 |
| Antrag | [`change_requests/CR-001_ANFANG_LICHT_SAMENZELLE.md`](change_requests/CR-001_ANFANG_LICHT_SAMENZELLE.md) (Commit fc3f174) |
| Antwort des Game Directors | „JA zu CR-001 mit den Vorschlägen E1 bis E4.“ |
| Inhalt | C00 bleibt (Bild/Ton/Dialog, C20-Replay); C01 wird ein kurzer greller Lichtschlag mit direktem Übergang in den Eileiter (Erde, Alltagsmontage und Erzählstimme VO_C01_001/002 entfallen); C02-B Schwimmphase wird Pflicht |
| Entscheidungen | **E1** Titel und Hauptmenü nach der Befruchtung (Ende C02) · **E2** kein Game Over (eine andere Samenzelle verschmilzt), Hilfe „automatisch schwimmen“ · **E3** C17-Schwangerschaftskapitel bleibt optional · **E4** Schwimmphase 60–120 s |
| Neue Fassung | ScriptLock **1.2**, vorbereitet lokal in `canon_proposals/CR-001/GENESIS_ScriptLock_12_Drehbuch_v1.2.md` (SHA-256 `79c1b1b64dbbc0a7b71be7f2c4ae54eff7014da954d6e1c2e0a50ea5d5fc1928`), gebaut aus 1.1 (`b23a047b…732d`) mit `build_scriptlock_12.py`; Unterschied nur C01, C02, Verweiszeilen (Status, Prolog-Länge, C00-Übergabezeile, Übergangstabelle, Einstieg, `ScriptVersion`) und Änderungsprotokoll |
| Ablage | **erledigt 2026-10-25 21:12** über den geprüften Canon-Import (`tools/v4/hooks/canon_import.py`, Protokoll `canon_import_log.jsonl`): Hash stimmt, Datei schreibgeschützt, 1.1 bleibt als Historie liegen |
| Canon-Import (Weg) | Auf Anweisung des Game Directors („nur neue Dateien, nur mit Hash aus einer freigegebenen Regieentscheidung, nie überschreiben“) ist `canon_import.py` der einzige Weg für Claude in den Canon-Ordner; der Schutzhook lässt nur dessen schlichte Form durch. Testmatrix 20/20 + Nicht-Überschreiben geprüft |

**Was die Freigabe NICHT bewirkt:** keine Asset-, Code- oder Produktionsfreigabe. Die technischen Folgen (MENU_FLOW, Szenenverträge C01/C02, Zustandsmaschine, Spielstand-Schema, Automationstests, neue Registerbindung an 1.2) brauchen eine eigene Freigabe. Bis dahin bindet das Register weiter an 1.1.

## GD-2026-10-25-02 – Freigabe Umsetzung CR-001 Phase 1 und 2

| Feld | Wert |
|---|---|
| Datum | 2026-10-25 |
| Vorlage | [`plans/CR-001_UMSETZUNGSPLAN.md`](plans/CR-001_UMSETZUNGSPLAN.md) (Commit 56849ea) |
| Antwort des Game Directors | „Freigabe für Phase 1 (Startablauf, Lichtschalter-Standard, Spielstand Schema 3, Tests) und Phase 2 (Graubox-Schwimmphase) aus dem CR-001-Umsetzungsplan.“ |
| Umfang | Code und Daten: Skriptversion 1.2 in Laufzeit und Verträgen, Startablauf C00 → C01 → C02 (Schwimmphase) → Titel, „Lichtblitze verringern“ standardmäßig an, Spielstand Schema 3 mit Migration, Tests; spielbarer Graubox-Prototyp der Schwimmphase |
| Nicht enthalten | Phase 3–5 (Look der Mikrowelt, Filmteile C01/C02, Integration/Abnahme) – je eigene Freigabe. Keine Kunst- oder Kanonentscheidung. |

## GD-2026-10-25-03 – Freigabe CR-001 Phase 3 (Look der Mikrowelt), zuerst Referenzbilder

| Feld | Wert |
|---|---|
| Datum | 2026-10-25 |
| Antwort des Game Directors | „Freigabe für Phase 3 (Look der Mikrowelt) aus dem CR-001-Umsetzungsplan: zuerst Referenzbilder zur Abnahme.“ |
| Umfang jetzt | Referenzbilder lokal (ComfyUI + FLUX.2 klein 4B, Apache-2.0, bereits installiert): Eileiter-Schleimhaut, Cumulus-Oozyten-Komplex, Zona pellucida mit Samenzelle, Samenzellen, Zygote mit Vorkernen, 2-Zell-Stadium → Abnahme der Bildsprache durch den Game Director |
| Danach (Phase 3, Schritt 2–4) | Blender-Assets, Unreal-Materialien/Niagara, Reality Check – erst nach Abnahme der Referenzen |

## GD-2026-10-25-04 – Abnahme C02-Referenzen (Bildsprache Mikrowelt)

| Feld | Wert |
|---|---|
| Datum | 2026-10-25 |
| Vorlage | `ArtSource/Reference/C02/C02_Referenzen_Abnahmeblatt.jpg` (Commit f7d7e8a) |
| Antwort des Game Directors | „Ja alle gut aber die Samen sehen noch nicht richtig aus also realistisch“ |
| Abgenommen | Eileiter `lumen_v1`, Eizelle + Cumulus `complex_v3`, Zona + Samenzelle `zona_sperm_v4` (Look), Zygote `pronuclei_v3`, 2-Zell `two_cell_v1` |
| Offen | Samenzelle: noch nicht realistisch → neue Entwürfe zur Abnahme |
