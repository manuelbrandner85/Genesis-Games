# Aufgabenverteilung

Stand: 2026-10-22. Fünf Rollen. Jede WorkID hat eine führende Rolle. Die zweite Rolle prüft oder liefert zu. Reviewer bleibt `OFFEN`, bis eine Person namentlich benannt ist. Dieselbe Person schreibt und zeichnet eine Abnahme nicht allein, sobald das Tor `APPROVED` heißt. Heute ist kein Tor `APPROVED`.

## Story & Kanon

Führend, wo das Drehbuch, eine Rolle oder eine offene Entscheidung den nächsten Schritt bestimmt.

| WorkID | Auftrag | Status |
|---|---|---|
| WK-M00-003 | ScriptLock beider Kopien vergleichen, Zählung der 22 Szenen und 113 Shots gegenzeichnen | `FILE_VALIDATED` |
| WK-M03-001 | NPC-Rollen N01–N08 gegen die Rollen-CSV halten, keine Berufsänderung | `BLOCKED` an den Rechten |
| WK-M03-004 | Ablauftexte A–E nur aus V23, keine neuen EventIDs | `PLANNED` |
| WK-M03-005 | Gewerk der Steinbrücke aus V47, Holz nur an Holz | `PLANNED` |
| WK-M04-002 | Erscheinung N01–N08 erst nach `DEC-02` | `BLOCKED` |
| WK-M05-001 | C01–C04 im Wortlaut des ScriptLock, Segment-Hashes aus dem Szenenregister | `PLANNED` |
| WK-M05-002 | Altersgrenzen aus den Szenen, Testprofil der Karte bleibt außerhalb des Kanons | `PLANNED` |
| WK-M06-001 | Echo-Variante zu CON33-01, ScriptLock unverändert | `BLOCKED` |
| WK-M07-001 | C19 zu, C20 nur als dasselbe C00-Medium | `BLOCKED` |
| WK-M07-003 | UI-Texte gegen V33 und gegen die Spoiler-Grenze | `PLANNED` |

Zuarbeit: jede andere Rolle legt Kanonfragen hier ab, bevor eine Datei das Drehbuch ersetzt.

## Unreal Engineer

Führend für Modul `Genesis`, Save, Maps, Import und UI-Technik. In dieser Projektdatei steht `EngineAssociation` `5.8`. Ein Lauf fehlt bis WK-M01-002.

| WorkID | Auftrag | Status |
|---|---|---|
| WK-M01-002 | Editor-Log: Version, Plugins, Maps, LFS. `GenesisSlice` nur lesen | `PLANNED` |
| WK-M02-001 | Save in der isolierten Kopie erneut prüfen, Archiv vom 2026-10-18 nicht als diesen Lauf buchen | `BLOCKED` |
| WK-M02-002, WK-M02-003, WK-M02-004 | Vorhandene Figur-, Kamera- und Zeitdateien liegen vor und warten auf denselben Nachweisweg | `FILE_CREATED` |
| WK-M03-002 | Neue Sandbox, Default-Map bleibt, kein Slice-Pfad im Diff | `PLANNED` |
| WK-M03-003 | Unreal-Seite des Maßwürfels, 100 cm, Reimport-Log | `PLANNED` |
| WK-M03-004 | Questgraph A–E, Save/Load, Dauerprotokoll 30–45 Minuten | `PLANNED` |
| WK-M04-003 | Importseite der sieben Tore | `PLANNED` |
| WK-M05-002 | Lebensphasen an den bestätigten Grenzen, Save inklusive | `PLANNED` |
| WK-M06-002 | Wiedergeburt nur nach Save-Abnahme und Echo-Beschluss | `BLOCKED` |
| WK-M07-003 | HUD- und Interaktionsdaten aus V33 | `PLANNED` |
| WK-M08-003 | N16-Zeilen technisch | `PLANNED` |

Zuarbeit an 3D & Animation: Import bricht ab, wenn Maß, Slot oder Kollision vom Protokoll abweicht.

## 3D & Animation

Führend für Geometrie, Rig und Clips. Die 38 GLBs sind Grundkörper. Blender wurde in diesem Lauf nicht gestartet. Das Skript unter V59 `12_BLENDER_SKRIPE_NICHT_AUSGEFUEHRT` bleibt unausgeführt.

| WorkID | Auftrag | Status |
|---|---|---|
| WK-M00-004 | GLBs und Tafeln nach `assets/source_glb/`, Hashes gleich dem Register, 004 und 005 beide behalten | `FILE_VALIDATED` für Bytes |
| WK-M03-003 | Ein GLB in der Kopie, Würfel 1 m, Graybox-Maße sind keine Realmaße | `PLANNED` |
| WK-M03-005 | Brücke R04, Dublette sichtbar lassen, Gewerk einhalten | `PLANNED` |
| WK-M04-001 | Werkstatt R03, Beträge erst nach V23-Abgleich | `PLANNED` |
| WK-M04-002 | Mastergesichter erst nach Beschluss | `BLOCKED` |
| WK-M04-003 | Sieben Tore je Master, N/A nur mit Begründung bei starrer Geometrie | `PLANNED` |
| WK-M04-004 | 40 Clips, heute keine FBX | `SOURCE_MISSING` |
| WK-M05-001 | Körper der frühen Szenen nach ScriptLock | `PLANNED` |
| WK-M06-001 | Echo ohne feste Architektur | `BLOCKED` |

Zuarbeit: QA prüft die Hashes, Unreal Engineer den Import.

## Audio & Cinematics

Führend für Shots, Stimme, Musik und das versiegelte C00. In der Übergabe liegen 0 WAV-Dateien.

| WorkID | Auftrag | Status |
|---|---|---|
| WK-M07-001 | Ein C00-Master, Digest, C20 spielt diese Datei | `BLOCKED` |
| WK-M07-002 | 113 Shots und 24 V33-Cues, deutsche Aufnahmen, Untertitel | Aufnahmen `SOURCE_MISSING`, Ablauf `PLANNED` |
| WK-M00-003 | Shot-Zählung 113 mitzeichnen | `FILE_VALIDATED` für die Zählung |
| WK-M08-001 | Filmphasen N00, N13, N14 nur mit Spoiler-Grenze | `PLANNED` |

Zuarbeit von Story & Kanon: kein Satz von C19 in Aufgaben, die vor der Enthüllung liegen. Zuarbeit von QA: Rechtezeile je Aufnahme, sonst bleibt die Datei draußen.

## QA & Release

Führend für Summen, EvidenceIDs, Restore, Leistung und den Release. QA vergibt `TESTED` nur nach einem Lauf, der im Protokoll steht, und `APPROVED` nur mit einer zweiten Person.

| WorkID | Auftrag | Status |
|---|---|---|
| WK-M00-001 | Hülle 91/91 | `FILE_VALIDATED` |
| WK-M00-002 | Kette, 40 Archive, drei Selbstbezüge dokumentiert | `FILE_VALIDATED` |
| WK-M00-005 | Plan und Statusdisziplin | `FILE_CREATED` |
| WK-M01-001 | Backup und Restore | `BLOCKED` |
| WK-M02-006 | Save-Abnahme gegen `BL59-03` | `BLOCKED` |
| WK-M03-001 | Rechteblatt, V39 bleibt bis zum Beleg `NONE` | `BLOCKED` |
| WK-M04-003 | Sieben Tore abnehmen | `PLANNED` |
| WK-M08-001 | 390 Tests, heute alle `NOT_RUN` | `PLANNED` |
| WK-M08-002 | Leistung nur mit Messdatei | `PLANNED` |
| WK-M08-003 | Zugang N16 | `PLANNED` |
| WK-M09-001 | Release-Build | `BLOCKED` |
| WK-M09-002 | Migration als Pull Request, `main` bleibt unberührt | `PLANNED` |

Zuarbeit: jede Rolle liefert EvidenceID, SHA256 und den Namen der prüfenden Person. Ein Archivbericht vom 2026-10-18 bleibt ein Archivbericht.
