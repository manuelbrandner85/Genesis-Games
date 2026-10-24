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
