# Produktionsplan M00–M09

Stand: 2026-10-22. Reihenfolge aus dem Masterprompt: M00 Quellen und Sicherheit, M01 Backup und Restore, M02 Fundamente und Save, M03 Vertikalschnitt VS01 von 30–45 Minuten ohne ein `GenesisSlice` zu überschreiben, M04 iterative 3D-Master, M05 Lebenszyklus, M06 Echo und Wiedergeburt, M07 C00–C21, Audio auf Deutsch und UI, M08 die 17 Phasen mit QA, Leistung und Zugänglichkeit, M09 unabhängiger Release und versionierte Migration.

Jede Zeile hat eine Quelle, eine Abhängigkeit, ein Ausgangsartefakt und eine Abnahme. Reviewer ist überall `OFFEN`. Niemand schreibt auf `main` und niemand führt einen Force-Push aus. Ein Ja zu diesem Dokument startet die nächste Zeile nicht.

`FILE_VALIDATED` heißt hier: veröffentlichte SHA256 und Bytes stimmen. Blender- und Unreal-Felder im GLB-Register bleiben `NOT_RUN`.

## Die ersten fünf WorkIDs

| WorkID | Abnahme | Status |
|---|---|---|
| WK-M00-001 | Release-Hash und 91/91 Hüllenzeilen, Evidence `M00-EV-001` | `FILE_VALIDATED` |
| WK-M00-002 | 40 Archive `testzip` OK, V61-Summe 47/47, Selbstbezüge nur an den drei Summendateien dokumentiert, Evidence `M00-EV-002` | `FILE_VALIDATED` |
| WK-M00-003 | Zählungen gleich den Dateien, ScriptLock-SHA256 gleich in V62 und V61 | `FILE_VALIDATED` |
| WK-M00-004 | 38 GLB-Hashes gleich `38_GLB_QUELLEN.csv`, 38 Tafeln daneben, LFS-Pointer, Evidence `M00-EV-004` | `FILE_VALIDATED` für Bytes |
| WK-M00-005 | Diese Dokumente liegen im Repo, ScriptLock unverändert, kein `TESTED` und kein `APPROVED` | `FILE_CREATED` |

### WK-M00-001 — Hülle

Quelle: Release `handover-v62`, `05_PRUEFBERICHT/SHA256SUMS.txt`. Abhängigkeit: keine. Änderung: keine an Quelltexten. Artefakt: Hash der ZIP `be91f395b09a131adc8d16fa8cfa4b54e337010e1c2aa7c6defdf0762cf80e07`, 91 gleiche Zeilen. Rolle: QA & Release.

### WK-M00-002 — Kette

Quelle: `02_VOLLSTAENDIGES_QUELLPAKET`, dann V60, V59, 37 ZIPs. Abhängigkeit: WK-M00-001. Artefakt: [M00_INVENTAR_ZIPS.csv](M00_INVENTAR_ZIPS.csv). Abnahme: jede entpackte ZIP `testzip` OK; bestandene Summenzeilen in der Datei-CSV; die drei Selbstbezüge aus [M00_INVENTAR.md](M00_INVENTAR.md) bleiben als Befund stehen und werden nicht still überschrieben. Rolle: QA & Release.

### WK-M00-003 — Register und ScriptLock

Quelle: `04_PRODUKTIONSREGISTER`, V61-Manifest, ScriptLock beider Kopien. Abhängigkeit: WK-M00-002. Abnahme: 17, 226, 196, 38, 40, 43, 113, 22, 31, 36, 390 und 28 Rechtezeilen wie im Inventar gezählt. ScriptLock-SHA256 `b23a047b13c1a7d77d00679c757f4fbcaa6cfc3e736305a7f77152c072ce732d` in beiden Kopien. Kein Satz des Drehbuchs geändert. Rolle: Story & Kanon, Prüfung durch QA & Release.

### WK-M00-004 — GLB und Tafeln

Quelle: `03_DIREKT_NUTZBARE_3D_GEOMETRIE`, Register `38_GLB_QUELLEN.csv`. Abhängigkeit: WK-M00-001. Änderung: Kopie nach `assets/source_glb/`, Git LFS über `*.glb` und `*.png`. Abnahme: 38 Hashes gleich dem Register, 38 Tafeln mit dem Suffix `_FRONT_SEITE_RUECKEN.png`, Brücke 004 und 005 beide vorhanden und bytegleich. Kein Blender-Lauf, kein Unreal-Import. Rolle: 3D & Animation, Hashprüfung durch QA & Release.

### WK-M00-005 — Plan

Quelle: Masterprompt, P0-Liste, V61-Auftragsreihenfolge `05_DIE_ERSTEN_AUFTRAEGE_NACH_FREIGABE.md`. Abhängigkeit: WK-M00-001 bis WK-M00-004. Artefakt: die Dateien in `docs/M00_*.md`. Abnahme: WorkIDs, Abhängigkeiten und Abnahmen sind aus den Registern belegbar; Statuswörter nur aus dem Masterprompt; Kanon unverändert. Rolle: QA & Release, Inhalte der Fachrollen wie in [M00_ROLLEN.md](M00_ROLLEN.md).

## M01 Backup und Restore

### WK-M01-001 — Isolierte Kopie — `BLOCKED`

Quelle: `BL59-01`, V61-Schritt „SEC-G0B-001“, P0-Zeile zur lokalen Quelle. Abhängigkeit: WK-M00-005 und eine ausdrückliche Freigabe mit Pfad. Artefakt: Backup-Hash, Protokoll von Löschen und Restore, zweiter Hash gleich dem ersten. Abnahme: die zurückgespielte Kopie trifft den Backup-Hash dateiweise für die gesicherten Pfade. Editor und Blender bleiben aus. Dieser Lauf hat das nicht ausgeführt. Rolle: QA & Release, Unreal Engineer liest danach nur mit.

### WK-M01-002 — Laufender Editor, nur lesen — `PLANNED`

Quelle: `BL59-08`. Abhängigkeit: WK-M01-001. Artefakt: Log mit Engine-Version, Pluginliste, LFS-Status, Map-Liste. Abnahme: die Version steht im Log des gestarteten Editors. Die Textdatei `Genesis.uproject` mit `EngineAssociation` `5.8` ist dafür kein Ersatz. `GenesisSlice` wird, falls die Kopie es enthält, nur gelesen. Rolle: Unreal Engineer.

## M02 Fundamente und Save

Im Arbeitsbaum liegen bereits die Pakete `WK-M02-001` (Save), `WK-M02-002` und `WK-M02-003` (Figur, Eingabe, Kamera, Austausch) und `WK-M02-004` (Weltzeit). Ihre Dateien sind `FILE_CREATED`. Die Archivberichte stehen im Ist/Soll. Sie sind kein `TESTED` dieses Registers. Die Alterszahlen im Zeitcode sind keine ScriptLock-Entscheidung.

### WK-M02-001 — Save erneut in der isolierten Kopie — `BLOCKED`

Quelle: `BL59-03`, `DEC-07`, vorhandene Dateien `Source/Genesis/Private/Save/`. Abhängigkeit: WK-M01-001. Änderung an `main`: keine. Artefakt: neues Protokoll aus der isolierten Kopie, Crash-Matrix, zwei Inkarnationen, Laden eines älteren Schemas, Migration. Abnahme: die Matrix trifft die Schließzeile von `BL59-03`, Reviewer ist nicht die Person, die den Save geschrieben hat. Bis dahin bleibt Wiedergeburt zu. Rolle: Unreal Engineer, Abnahme QA & Release.

### WK-M02-006 — Save-Abnahmebericht — `BLOCKED`

Quelle: `02_ENGINE_CONTRACTS/TRANSAKTIONSSAVE_ABNAHME.md` in V60. Abhängigkeit: der neue Lauf von WK-M02-001. Artefakt: ein Bericht mit EvidenceID, ohne die Archivzähler vom 2026-10-18 als eigenen Lauf zu führen. Abnahme: QA zeichnet `APPROVED` erst nach dem Lauf. Heute: `BLOCKED`. Rolle: QA & Release.

`WK-M02-002`, `WK-M02-003` und `WK-M02-004` bleiben auf `FILE_CREATED`, bis derselbe Weg — isolierte Kopie, wiederholter Lauf, fremder Reviewer — auch für sie vorliegt. Sie sind nicht der nächste Schritt vor M01.

## M03 Vertikalschnitt VS01

Ziel laut Masterprompt: 30–45 Minuten, neben einem etwaigen `GenesisSlice`. Die sechs Abläufe A–F stehen in `11_V23_VS01_HAUPTABLAEUFE_6.csv`. Jede Zeile trägt dort `ADULT_VERTICAL_SLICE_TEST_SEPARATE_FROM_MAIN_INCARNATION`. Die Titelzeile von F nennt zusätzlich einen getrennten QA-Durchlauf. Zeiten und Missionskürzel bleiben die der Quelle. Neue EventIDs werden nicht erfunden.

### WK-M03-001 — Rechteblatt der 38 GLBs — `BLOCKED`

Quelle: `BL59-02`, V39-Plan mit 28 ungeprüften Zeilen. Abhängigkeit: WK-M00-004. Artefakt: je GLB eine Zeile Herkunft, Fassung, erlaubter Gebrauch, Beleg oder Sperre. Abnahme: keine Zeile mit `Authorization` `NONE` geht in einen Unreal-Import. Heute sind alle 28 V39-Zeilen `NONE`. Rolle: QA & Release, Story & Kanon für die NPC-Rollen.

### WK-M03-002 — Sandbox-Map — `PLANNED`

Quelle: V61-Regel, `GenesisSlice` und Default-Map unangetastet zu lassen. Abhängigkeit: WK-M01-002 und WK-M03-001. Artefakt: eine neue Map. Abnahme: das Diff enthält keine Änderung an einem Pfad `GenesisSlice` und biegt die bestehende Default-Map nicht um. In dieser Projektdatei ist `GenesisSlice` nicht deklariert; das Diff weist das weiterhin so aus. Rolle: Unreal Engineer.

### WK-M03-003 — Ein GLB, Maßwürfel — `PLANNED`

Quelle: V61-Schritt 4 und `IMPORT_PLAN.txt`. Abhängigkeit: WK-M03-001 und WK-M01-001. Die Notiz nennt Marktgestell R02 und Wettermast R06 als formale Vorschläge und verbietet, die Graybox-Maße als normative Realmaße zu nehmen. Artefakt: Blender-Version, Mesh-Zahl, Bounding-Box, Würfel 1 m, in Unreal 100 cm, Reimport-Log, alles in der Kopie. Abnahme: Protokoll vorhanden. Ein Qualitäts-PASS wird dabei nicht vergeben. Rolle: 3D & Animation und Unreal Engineer.

### WK-M03-004 — Abläufe A–E spielbar — `PLANNED`

Quelle: V23-Abläufe A–E, Missionsanker nur mit den vorhandenen IDs. Abhängigkeit: WK-M03-002 und die Save-Abnahme WK-M02-006. Artefakt: Questgraph, NPC-Ausweichweg, Save/Load mitten in der Aufgabe. Abnahme: ein Durchlauf der Abläufe A–E, dessen gespielte Dauer im Protokoll zwischen 30 und 45 Minuten liegt. F bleibt der in der Titelzeile genannte getrennte QA-Durchlauf. Fehlende Quellzeilen bleiben `SOURCE_MISSING` und werden nicht ergänzt. Rolle: Unreal Engineer, Story & Kanon liest die Texte gegen.

### WK-M03-005 — Pilot Brücke R04 — `PLANNED`

Quelle: V23-Ablauf C, V47-Gewerketext, 13 GLBs `VS01_R04_BRUECKE_*`. Abhängigkeit: WK-M03-003. Die Steinbrücke prüfen und instand setzen Menschen des passenden Gewerks. Holzarbeiten bleiben beim Holzgewerk. `VS01_R04_BRUECKE_004.glb` und `_005.glb` werden nicht gelöscht und nicht still zu zwei verschiedenen Meshes erklärt. Artefakt: Entscheidung der Dublette als eigener Beschluss, danach Master nur für freigegebene IDs. Abnahme: sieben Tore je freigegebenem Mesh, siehe WK-M04-003. Rolle: 3D & Animation, Story & Kanon für das Gewerk.

## M04 3D-Master

### WK-M04-001 — Werkstatt R03 — `PLANNED`

Quelle: V61-Schritt 6, 15 GLBs `VS01_R03_WERKSTATT_*`, N01 und N02. Abhängigkeit: WK-M03-005. Die Quelle nennt Generator, Kontakt, Autonomie und Beträge aus V23. Die Beträge werden vor dem Bau mit der V23-Datei verglichen und hier nicht wiederholt, solange dieser Vergleich nicht als eigene EvidenceID liegt. R03 bleibt Reparatur- und Generatorwerkstatt. Abnahme: Master ersetzt die Graybox erst nach den sieben Toren und nach Rechtezeile. Rolle: 3D & Animation.

### WK-M04-002 — Erscheinung N01–N08 — `BLOCKED`

Quelle: `DEC-02`, `BL59-11`, Rollen-CSV. Abhängigkeit: Beschluss zu jeder Erscheinung. Die acht Rollen und ihre Orte bleiben. Gesichter sind `NOT_APPROVED`. Entwurfsbilder werden keine Master. Abnahme: je ID ein Beschluss, dann erst WK-M04-003. Rolle: Story & Kanon.

### WK-M04-003 — Sieben Tore je Master — `PLANNED`

Quelle: `03_VERBINDLICHE_3D_MASTER_UND_UE_ABNAHME.md`. Abhängigkeit: das jeweilige Pilotpaket und WK-M03-001. Tore, einzeln belegt: Front, Seite, Rücken aus derselben Geometrie; Material; Maßstab; Rig oder ein begründetes N/A bei starrer Geometrie; Unreal-Import mit Log; dazu UV, Topologie, Kollision und LOD. Abnahme: je Tor eine EvidenceID. Ein Sammelbild gilt nicht als Modell. Rolle: 3D & Animation, Import Unreal Engineer, Abnahme QA & Release.

### WK-M04-004 — 40 Animationen — `SOURCE_MISSING`

Quelle: `40_ANIMATIONEN_STATUS.csv`, `BL59-15`. Alle 40 Zeilen `NOT_CREATED`, keine FBX in der Kette. Abhängigkeit: ein abgenommenes Menschen-Rig aus WK-M04-003. Kinder- und Altersprofile entstehen als eigene Rigs, sobald die Szenenalter sie verlangen. Abnahme: Aktion in Blender, Clip in Unreal, Kontaktprüfung. Heute fehlt die Quelldatei jedes Clips. Rolle: 3D & Animation.

## M05 Lebenszyklus

### WK-M05-001 — C01 bis C04 — `PLANNED`

Quelle: ScriptLock C01–C04, Anforderungen N00–N04. Abhängigkeit: WK-M00-003. Biologie bleibt im Rahmen des Drehbuchs. Was das Drehbuch nicht sagt, wird nicht als medizinische Tatsache ergänzt. Abnahme: jede Szene gegen ihren Segment-Hash aus `01_KANON_FILMSZENEN_22.csv`, Review durch eine dafür benannte Prüfung. Rolle: Story & Kanon, Figuren 3D & Animation.

### WK-M05-002 — C05 bis C14 — `PLANNED`

Quelle: ScriptLock, Phasen N05–N08. Abhängigkeit: WK-M05-001 und WK-M02-006. Der vorhandene Zeitcode bleibt `FILE_CREATED` und wird an die Szenenalter gebunden, sobald Story & Kanon die Grenzen aus dem Drehbuch bestätigt. Das Testprofil der Karte ist kein Kanon. Abnahme: Alter und Abschnitt überleben Save und Load in der isolierten Kopie, mit Protokoll. Rolle: Unreal Engineer, Grenzen durch Story & Kanon.

## M06 Echo und Wiedergeburt

### WK-M06-001 — Echo — `BLOCKED`

Quelle: `CON33-01`, `BL59-04`, V61-Schritt 7. Abhängigkeit: der Beschluss aus [M00_BLOCKER.md](M00_BLOCKER.md). Das Echo bleibt Energie und Erinnerung. Feste Tempel, Bibliotheksräume und Säulen werden nicht gebaut. Besuche ändern die Menschenwelt nicht. Abnahme: die gewählte Variante, ScriptLock-Hash unverändert, eine Szene ohne begehbare Architektur. Rolle: Story & Kanon, Raum 3D & Animation.

### WK-M06-002 — Wiedergeburt — `BLOCKED`

Quelle: `DEC-07`, Missionen der Echo-Kette im 43er-Register, Phasen N12–N14. Abhängigkeit: WK-M02-006 und WK-M06-001. Abnahme: ein Lebenswechsel, bei dem Soul, World und Life aus einer Transaktion kommen, Crash inklusive, C19 weiterhin zu. Rolle: Unreal Engineer.

## M07 Filme, Ton, UI

### WK-M07-001 — C00-Master und C20 — `BLOCKED`

Quelle: `BL59-05`, `DEC-06`, Szenen C00 und C20. Abhängigkeit: Rechte für Bild und Stimme, WK-M03-001. Artefakt: ein versiegeltes C00-Medium und sein Digest. C20 spielt dieses Medium. Eine zweite, ähnliche Fassung entsteht nicht. Abnahme: Bild- und Tonvergleich am Build, EvidenceID, Spoiler-Grenze vor C19 im Aufgabenweg. Rolle: Audio & Cinematics.

### WK-M07-002 — 113 Shots und deutsche Cues — `PLANNED`, Aufnahmen `SOURCE_MISSING`

Quelle: `CINEMATIC_SHOTS.csv` (113 Zeilen `SCRIPT_ONLY_NOT_ENGINE_TESTED`), V33-Register mit 24 Audio-Cues, 24 Gameplay-Shots, 12 HUD-Zuständen, 19 Interaktionsverträgen. WAV in der Übergabe: 0. Abhängigkeit: WK-M07-001 für C00, sonst je Szene nach ScriptLock. Abnahme: je Cue eine lizenzierte Datei, Untertitel, Wiedergabe in Unreal. Lippensynchronisation erst mit dieser Datei. Rolle: Audio & Cinematics.

### WK-M07-003 — UI — `PLANNED`

Quelle: V33-HUD und Interaktion, Phase N16. Abhängigkeit: WK-M07-002 für alle Zeilen mit Sprache. Abnahme: die 12 HUD-Zustände und 19 Verträge als Daten, Spieltest, C19-Text bleibt aus den Oberflächen vor der Enthüllung. Rolle: Unreal Engineer, Texte Story & Kanon.

## M08 Phasen, QA, Leistung, Zugang

### WK-M08-001 — N00 bis N16 — `PLANNED`

Quelle: `17_SPIELPHASEN_STATUS.csv`, 390 Tests `NOT_RUN`. Abhängigkeit: M03 bis M07 je Phase. Abnahme: je Phase die eigene EvidenceID, `ReadyForAAAProduction` nur nach Beleg. Heute steht überall NO. Rolle: QA & Release, Fachrollen liefern die Phase.

### WK-M08-002 — Leistung — `PLANNED`

Quelle: `BL59-13`. Abhängigkeit: ein startbarer Build aus der isolierten Kopie. Abnahme: gemessene Framezeiten und Speicher auf benannter Hardware, mit Protokolldatei. Zahlen ohne Messung werden nicht eingetragen. Rolle: QA & Release.

### WK-M08-003 — Zugänglichkeit — `PLANNED`

Quelle: Phase N16, 15 Anforderungszeilen dieser Phase innerhalb der 226. Abhängigkeit: WK-M08-001. Abnahme: die N16-Zeilen einzeln abgehakt, Steuerung mit den im Drehbuch und in N16 genannten Wegen. Rolle: QA & Release und Unreal Engineer.

## M09 Release

### WK-M09-001 — Release-Build — `BLOCKED`

Quelle: Masterprompt-Schluss, `BL59-02`, P0-Zeile Release. Abhängigkeit: WK-M08-001 bis WK-M08-003 und geschlossene Rechte. Artefakt: ein wiederholt startbarer, rechtlich nutzbarer Unreal-Build über die freigegebenen Phasen, signierter Bericht. Abnahme: zweite Person, anderer Tag, gleicher Build-Hash. Heute existiert dieser Build nicht. Rolle: QA & Release.

### WK-M09-002 — Migration — `PLANNED`

Quelle: Masterprompt, Schreibrecht nur über Review. Abhängigkeit: WK-M09-001. Artefakt: Pull Request mit Build-Hash und EvidenceIDs. Abnahme: Review, kein Force-Push, kein direktes Schreiben auf `main`. Rolle: QA & Release.

## Abhängigkeiten in einer Kette

WK-M00-001 → WK-M00-002 → WK-M00-003 → WK-M00-005.

WK-M00-001 → WK-M00-004 → WK-M00-005.

WK-M00-005 → WK-M01-001 → WK-M01-002 → WK-M03-002.

WK-M01-001 → WK-M02-001 → WK-M02-006 → WK-M03-004 und → WK-M06-002.

WK-M00-004 → WK-M03-001 → WK-M03-003 → WK-M03-005 → WK-M04-001 → WK-M04-003.

WK-M04-002 blockiert die NPC-Master und hängt an `DEC-02`.

WK-M06-001 hängt an `CON33-01`. WK-M07-001 hängt an `BL59-05` und an den Rechten.

WK-M08-001 hängt an M03–M07. WK-M09-001 hängt an M08 und an `BL59-02`.
