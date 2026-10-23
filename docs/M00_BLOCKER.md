# Blocker

Stand der Änderung: 2026-10-23. Quellenworte wie `UNVERIFIED` oder `NOT_RUN` bleiben Zitate. `BLOCKED` gilt, bis der Schließnachweis der jeweiligen Zeile vorliegt.

## Entschieden: CON33-01

ID: `BL59-04`, Entscheidung `DEC-01`. Manuel Brandner hat am 23.10.2026 um 01:51 Uhr (Berlin) entschieden. Quelle: Pull Request #3, `docs/kanon/BESCHLUESSE.md` auf dem Zweig `kanon/con33-01-entschieden`. Dieser Zweig ist hier nicht gemergt. Der Beschluss lautet:

- C15 und C16 behalten Räume und Bibliothek so, wie sie im ScriptLock stehen.
- Dasselbe gilt für die Bibliotheks- und Regalbilder in C17 und C19.
- V20A gilt weiter. Für diese vier Kapitel gibt es eine Ausnahme: Räume und Bibliothek sind erlaubt. Tempel und Säulen bleiben verboten, auch dort.
- Der ScriptLock-Text C00–C21 wird nicht geändert. SHA256 bleibt `b23a047b13c1a7d77d00679c757f4fbcaa6cfc3e736305a7f77152c072ce732d`.

Der Entscheidungstor ist damit zu. Die Umsetzung ist `WK-M06-001`, Status `PLANNED`. Ein gebauter Echo-Raum ist daraus nicht entstanden.

## Offen

### 1. Rechte — `BLOCKED`

ID: `BL59-02`, Entscheidung `DEC-05`. Der V39-Prüfplan hat 28 Zeilen. Jede Zeile ist `UNVERIFIED`, `NOT_REVIEWED`, `PENDING`, `Authorization` `NONE`. Schließung: je Datei Herkunft, Fassung, Nutzungsraum und ein Beleg. Ein Unreal-Import der 38 GLBs bleibt zu, solange die Zeile der Datei `Authorization` `NONE` trägt.

Die 38 GLBs und 38 Tafeln bleiben in `assets/source_glb/`. Ob sie aus dem öffentlichen Repo genommen werden, entscheidet Manuel separat. Dieser Lauf löscht sie nicht.

### 2. Soul/World/Life-Speicherung — `BLOCKED`

ID: `BL59-03`, Entscheidung `DEC-07`. `WK-M02-001` bleibt die vorhandene Implementierung aus Commit `e9eb043` und dem Ordner `docs/evidence/WK-M02-001/` (`FILE_CREATED`). Der neue Nachweis in der isolierten Kopie heißt `WK-M02-007`. Schließung: vier benannte Fälle in `docs/evidence/WK-M02-007/crash_matrix.csv` (Crash während des Schreibens, zwei Inkarnationen, Laden eines älteren Schemas, Migration), jede Zeile `result` = `EGenesisSaveResult::Ok` und `consistent` = 1, Reviewer-Name ungleich dem Autor des Save-Commits. Die Archivzähler vom 2026-10-18 schließen das Tor nicht.

### 3. Lokale Engine, LFS-Lauf und Restore — `BLOCKED`

IDs: `BL59-01`, `BL59-08`. WorkID: `WK-M01-001`. Schließung: für jede Zeile der Backup-Liste ist die SHA256 nach dem Restore gleich der SHA256 davor, Differenzzahl 0. Ein Editor-Log ist `WK-M01-002` und verlangt eine Zeile `Engine Version:`. `GenesisSlice` ist in dieser Projektdatei nicht deklariert (`SOURCE_MISSING`).

### 4. C19, C20 und das identische C00 — `BLOCKED`

ID: `BL59-05`, Entscheidung `DEC-06`. WorkID: `WK-M07-001`. Schließung: SHA256 der C00-Mediendatei gleich der SHA256 der in C20 abgespielten Datei, Audiodauer in Samples gleich, Differenz 0. C19-Assets fehlen in einem Paket, dessen Save `RevealGuard` = false trägt.

## Weitere offene Tore

| ID | Thema | Quellenstand | Status hier | WorkID |
|---|---|---|---|---|
| BL59-06 | 38 GLBs sind Grundgeometrie | Blender und Unreal `NOT_RUN` | Master `SOURCE_MISSING` | WK-M04-003 |
| BL59-07 | Referenzbilder mit falschen Motiven | Quarantäne V45–V54 | `BLOCKED` | kein Bauauftrag; Bilder bleiben in Quarantäne |
| BL59-09 | 196 Positionen sind der Testslice | `NOT_CREATED` | `PLANNED` | WK-M03-004 |
| BL59-10, DEC-03 | Weitere Epochen | 2026 primär | `BLOCKED` | offen, kein Bau |
| BL59-11, DEC-02 | Aussehen N01–N08 | `NOT_APPROVED` | `BLOCKED` | WK-M04-002 |
| BL59-12 | Deutsche Sprache, Musik | 0 WAV | Aufnahmen `SOURCE_MISSING` | WK-M07-002 |
| BL59-13 | Leistung | keine Messung | `PLANNED`, Maschinenname fehlt | WK-M08-002 |
| BL59-14 | Missionen im Spiel | 43 Anker `NOT_VERIFIED` | `PLANNED` | WK-M03-004 |
| BL59-15 | 40 Animationsclips | `NOT_CREATED`, 0 FBX | `SOURCE_MISSING` | WK-M04-004 |

## Nächster begrenzter Antrag

`WK-M01-001`: eine benannte isolierte Kopie, Backup-Liste mit SHA256, Löschen der Kopie, Restore, Differenzzahl 0. Editor und Blender bleiben aus. `main` wird nicht beschrieben. Der Antrag ist vorbereitet und nicht ausgeführt.
