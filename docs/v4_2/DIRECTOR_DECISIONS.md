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
