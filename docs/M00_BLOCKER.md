# Blocker

Stand: 2026-10-22. Die fünf Tore unten stammen aus `P0_BLOCKER_LESEN.md` und den Verträgen `BL59-01` bis `BL59-15`. M00 hat keines davon geschlossen. Quellenworte wie `UNVERIFIED` oder `NOT_RUN` bleiben Zitate. Der Status dieses Registers ist `BLOCKED`, bis der jeweilige Schließnachweis vorliegt.

## 1. C15/C16, CON33-01 — `BLOCKED`

ID: `BL59-04`, Entscheidung `DEC-01`. Der ScriptLock-Text von C15 und C16 spricht von körperlicher, bibliotheksartiger Architektur. V20A lässt im Echo nur Energie zu. Beides liegt unverändert vor. Eine technische Textänderung wäre eine Kanonänderung und unterbleibt. Schließung: eine vom Rechteinhaber benannte Variante, ScriptLock bytegleich, danach erst die Filmregie.

## 2. Rechte — `BLOCKED`

ID: `BL59-02`, Entscheidung `DEC-05`. Der V39-Prüfplan hat 28 Zeilen. Jede Zeile ist `UNVERIFIED`, `NOT_REVIEWED`, `PENDING`, `Authorization` `NONE`. Betroffen sind Eigen-Code, Assets, Musik, Stimmen, Plugins und KI-Referenzen. Ein öffentliches Repository ist kein Nutzungsbeleg. Schließung: je Datei Herkunft, Fassung, Nutzungsraum und ein Beleg des Rechteinhabers. Bis dahin bleibt die Verwendung der 38 GLBs über die reine Archivierung in `assets/source_glb/` hinaus gesperrt.

## 3. Soul/World/Life-Speicherung — `BLOCKED`

ID: `BL59-03`, Entscheidung `DEC-07`. Der Vertrag verlangt ein Commit-Bundle mit Generations- und Transaktions-ID, Hashes von Soul, World und Life, atomaren Wechsel und Recovery. Der Schließnachweis ist eine Crash-Matrix, zwei Inkarnationen, Laden eines alten Schemas und Migration, gelesen von einer Person, die den Code nicht geschrieben hat. Im Arbeitsbaum liegen Quelldateien und die Archivberichte aus dem Ist/Soll. Dieser Lauf hat sie nicht ausgeführt. Die Archivzähler schließen das Tor nicht. Wiedergeburt bleibt zu.

## 4. Lokale Engine, LFS-Lauf und Restore — `BLOCKED`

IDs: `BL59-01`, `BL59-08`. Der Vertrag verlangt eine freigegebene, isolierte Bestandsaufnahme: Engine-Version aus dem laufenden Editor, Plugins, Maps, Compiler, Backup und einen Restore, der die Bytes zurückbringt. Dieser Lauf hat die Übergabe außerhalb des Projektordners gelesen und `Genesis.uproject` als Text gelesen. Unreal wurde nicht gestartet. Ein Restore-Test hat nicht stattgefunden. `GenesisSlice` ist in dieser Projektdatei nicht deklariert (`SOURCE_MISSING`). Ältere Quellen verbieten, ein solches Slice zu überschreiben, sobald es in einer anderen Kopie auftaucht. Der historische Verweis auf den Commit `5b7e3a66` vom 2026-09-27 wurde hier nicht nachgeschlagen.

## 5. C19, C20 und das identische C00 — `BLOCKED`

ID: `BL59-05`, Entscheidung `DEC-06`. C19 und C20 sind geschützt. C20 verwendet dasselbe C00-Medium, nachgewiesen durch Bild- und Tonvergleich am gebauten Spiel. Es gibt keine versiegelte Mediendatei und keinen Fingerprint-Lauf. Schließung: ein unveränderliches C00-Master, Digest, Rollen, die den Text vor C19 nicht ausspielen, und der Vergleich am Build.

## Weitere offene Tore

Sie blockieren jeweils ihren eigenen Abschnitt und sind in den WorkIDs zugeordnet.

| ID | Thema | Quellenstand | Status hier |
|---|---|---|---|
| BL59-06 | 38 GLBs sind Grundgeometrie | Register: Blender und Unreal `NOT_RUN` | Master `SOURCE_MISSING` |
| BL59-07 | Referenzbilder mit falschen Motiven | Quarantäne V45–V54 | `BLOCKED` |
| BL59-09 | 196 Positionen sind der Testslice, nicht das ganze Spiel | `NOT_CREATED` | `PLANNED` |
| BL59-10, DEC-03 | Weitere Epochen | 2026 primär, Umfang offen | `BLOCKED` |
| BL59-11, DEC-02 | Aussehen N01–N08 | Rolle freigegeben, Erscheinung `NOT_APPROVED` | `BLOCKED` |
| BL59-12 | Deutsche Sprache, Musik | 0 WAV in der Übergabe | Aufnahmen `SOURCE_MISSING` |
| BL59-13 | Leistung | Keine Messung in diesem Lauf | `PLANNED` |
| BL59-14 | Missionen im Spiel | 43 Anker, `NOT_VERIFIED` | `PLANNED` |
| BL59-15 | 40 Animationsclips | `NOT_CREATED`, 0 FBX | `SOURCE_MISSING` |

## Nächster begrenzter Antrag

`WK-M01-001`: eine benannte isolierte Kopie dieser Arbeitskopie, Backup mit SHA256, Löschen der Kopie, Restore, erneuter Hashvergleich. Ohne Editor, ohne Blender, ohne Schreibzugriff auf `main`. Diesen Antrag hat M00 vorbereitet und nicht ausgeführt.
