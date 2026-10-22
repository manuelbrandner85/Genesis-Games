# Inventar der Quellen und Assets

Stand: 2026-10-22. Entpackt unter einem Ordner außerhalb des Repos. Vollständige Hashes:

- [M00_INVENTAR_DATEIEN.csv](M00_INVENTAR_DATEIEN.csv) — 1845 Dateien, 366 945 914 Bytes
- [M00_INVENTAR_ZIPS.csv](M00_INVENTAR_ZIPS.csv) — 66 ZIP-Einträge

EvidenceID der Prüfung: `M00-EV-001` (Hülle), `M00-EV-002` (Kette), `M00-EV-003` (diese CSV-Dateien), `M00-EV-004` (GLB-Registerabgleich).

## Release und Hülle

| Datei | SHA256 | Prüfung |
|---|---|---|
| `GENESIS_V62.zip` | `be91f395b09a131adc8d16fa8cfa4b54e337010e1c2aa7c6defdf0762cf80e07` | Hash dieses Laufs. Die ZIP ist nicht Zeile ihrer eigenen Summendatei. |
| V61-Quell-ZIP | `f1884e9f0cc4ca4ad9f7015f1d2cd3f601703df86b55808508ef0824ce950114` | Gleich Manifest und gleich V62-Summenzeile |
| ScriptLock | `b23a047b13c1a7d77d00679c757f4fbcaa6cfc3e736305a7f77152c072ce732d` | V62-Kopie und V61-Original bytegleich |

Die Hülle enthält 92 Dateien. 91 Summenzeilen in `05_PRUEFBERICHT/SHA256SUMS.txt` stimmen. `SHA256SUMS.txt` und `MANIFEST.json` stehen nicht in der Liste; ihre Hashes stehen in der Datei-CSV. Abweichende Nutzlast in der Hülle: keine.

## Kette

Entpackt und mit `testzip` = OK: V61, V60, V59 und die 37 Pakete in `11_QUELLENPAKETE`. V61-Summe: 47 von 47 Zeilen gleich, darunter die V60-ZIP als eine Datei. Damit hängt der Inhalt der V60-ZIP am geprüften Blob.

Die 37 Namen:

`GENESIS_Vorschlag_20B_Claude_Paket.zip`, `GENESIS_V21_Claude_Gesamtpaket.zip`, `GENESIS_V22_Claude_Gesamtpaket.zip`, `GENESIS_V23_Claude_Entwicklungspaket_v1.zip`, `GENESIS_V24_Claude_Gesamtpaket.zip`, `GENESIS_V25_Claude_Produktionspaket.zip`, `GENESIS_V26_1_Sicherheitsrevision_Claude_Paket.zip`, `GENESIS_V27_Das_Unsichtbare_Band_Claude_Update.zip`, `GENESIS_V28_Das_Vermaechtnis_Claude_Paket.zip`, `GENESIS_V29_Seelengefaehrten_Claude_Paket.zip`, `GENESIS_V30_Stroemungen_der_Ewigkeit_Claude_Paket.zip`, `GENESIS_V31_Echo_Director_Claude_Paket.zip`, `GENESIS_V32_Der_Ewige_Kreislauf_Claude_Paket.zip`, `GENESIS_V33_Cinematic_Experience_Claude_Paket.zip`, `GENESIS_V34_Visual_DNA_AAA_LookDev_Claude_Paket.zip`, `GENESIS_V35_Drei_Pilotproduktionen_Claude_Planung.zip`, `GENESIS_V36_Produktionsleitstand_Claude_Paket.zip`, `GENESIS_V37_Sicherheits_Freigabeplanung_Claude_Paket.zip`, `GENESIS_V38_Sichere_Lokale_Bestandsaufnahme_Claude_Paket.zip`, `GENESIS_V39_Quellen_Rechte_Integritaet_Claude_Paket.zip`, `GENESIS_V41_Komplettes_Spiel_Claude_Produktionshandbuch.zip`, `GENESIS_V42_PRODUKTIONSREIFE_UND_ASSETABNAHME_CLAUDE.zip`, `GENESIS_V43_CLAUDE_GESAMTUMSETZUNG_GITHUB_UMSTELLUNG.zip`, `GENESIS_V44_CLAUDE_CODE_ALLES_VOM_SPERMIUM_BIS_FINALE.zip`, `GENESIS_V45_REFERENZATLAS_NUR_FEHLENDE_CLAUDE.zip`, `GENESIS_V46_Gegenwart_Referenzen_Wiederverwendet.zip`, `GENESIS_V47_Realismus_Berufe_Bruecke_Claude_Update.zip`, `GENESIS_V48_Moderne_NPC_Einzelreferenzen_Claude.zip`, `GENESIS_V49_N04_N05_Referenzen_Claude_Code.zip`, `GENESIS_V50_NPC_N02_N03_N06_N07_N08_CLAUDE_DELTA.zip`, `GENESIS_V51_N07_N08_Claude_Referenzdelta.zip`, `GENESIS_V52_N07_N08_Drei_Ansichten_Claude_Code.zip`, `GENESIS_V54_N07_N08_Referenzdelta_Claude_Code.zip`, `GENESIS_V55_3D_Referenzen_Audit_Blender_Unreal_Claude_Code.zip`, `GENESIS_V56_ERSTE_ECHTE_3D_ASSETS_BLENDER_UE.zip`, `GENESIS_V57_GLB_TURNAROUNDS.zip`, `GENESIS_V58_SECHS_ECHTE_NPC_GLBS_Claude_Code.zip`.

Eine Datei mit der Bezeichnung V40 oder V53 liegt in diesem Ordner nicht. Der Begleittext der Übergabe sagt „nach verfügbarem Stand“.

26 weitere ZIP-Dateien in schon entpackten Paketen haben dieselbe SHA256 wie eines der 40 Archive. Sie blieben gepackt. Ihre Hashes stehen in der ZIP-CSV, Spalte `duplikat_von`.

## Prüfstatus der 1845 Dateien

| pruefstatus | Anzahl | Bedeutung |
|---|---|---|
| `PFAD_UND_HASH_GLEICH` | 1505 | Pfadende und SHA256 treffen eine bestandene Summenzeile |
| `NUR_HASH_GLEICH` | 141 | Dieselben Bytes wie eine bestandene Zeile, anderer Pfad (Zweitkopie) |
| `KEINE_VEROEFFENTLICHTE_SUMME` | 196 | Keine eigene Summenzeile. Darunter die Release-ZIP, Summendateien, die sich selbst nicht aufführen, und Pakete ohne eigene `SHA256SUMS.txt` |
| `SELBSTBEZUG_ABWEICHEND` | 3 | Die Summendatei enthält eine Zeile über sich selbst, die nicht zur Datei passt |

Pakete ohne eigene Summendatei, Inhalt über die umschließende geprüfte ZIP gebunden: V20B, V21, V22, V23, V24, V27, V29, V31, V43, V46, V57. V60 hat keine eigene Summendatei neben den Dateien, die V61 bereits als ZIP-Blob geprüft hat.

### Drei Selbstbezüge

Nutzlastzeilen dieser drei Listen stimmen. Abweichend ist nur die Zeile `SHA256SUMS.txt` über die Liste selbst.

| Paket | Erwartet in der Liste | SHA256 der Datei |
|---|---|---|
| V33 | `4ddc45d45125c6f41ca2744650e609302cc949b0d92efaa0f243f62231aa8ae9` | `c1cfca238073dcf458076a4d9323726dea94b73f229e2a5d9a17ebe26253b80c` |
| V41, verschachtelte Liste `GENESIS_MASTER_CLAUDE_UMSETZUNG_2026-10-16` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (Hash der leeren Datei) | `2c0c601dea889b6cc84650988a283c963737c50eb33323fae34821606241c313` |
| V25 | `6eff5a91b99d718b24d9be0fd9a3f13f0f140f14f2adc249dc67a28de87a1daa` | `0111ee4614acbe29d435b2d94aac2e3e5f28edfeab878aa12b5f6da4977da418` |

## Register, gezählt an den Dateien

| Register | Gezählte Zeilen | Quellenstatus |
|---|---|---|
| `17_SPIELPHASEN_STATUS.csv` | 17 | gebaute Assets 0, AAA-bereit NO |
| `226_VOLLSPIEL_ANFORDERUNGEN.csv` | 226 | alle `SPECIFIED_NOT_BUILT` |
| `196_TESTSLICE_ASSETS.csv` | 196 | alle `NOT_CREATED` / `NO_EVIDENCE` |
| `38_GLB_QUELLEN.csv` | 38 | alle `GRAYBOX_OR_PROXY` |
| `40_ANIMATIONEN_STATUS.csv` | 40 | alle `NOT_CREATED` |
| `43_MISSIONSANKER.csv` | 43 | alle `NOT_VERIFIED` |
| `CINEMATIC_SHOTS.csv` | 113 in 22 Szenen | alle `SCRIPT_ONLY_NOT_ENGINE_TESTED` |
| V61-Manifest | 31 Szenenpakete, 36 Lücken, 390 neue Tests, 15 Blocker, 7 Entscheidungen | Tests `NOT_RUN` |
| V61 `12_V61_NEUE_ABNAHMETESTS.csv` | 390 | alle `NOT_RUN` |
| V39 `21_RECHTEPRUEFPLAN.csv` | 28 | alle `UNVERIFIED` |

Disziplinen der 226 Zeilen, gleich dem V61-Manifest: Environment 30, Gameplay 24, Character 23, Animation 23, UI 21, Camera 18, Audio 18, State 17, VFX 11, Prop 10, Mesh 9, System 7, Safety 6, QA 4, Continuity 2, Rig 2, Vehicle 1.

VS01-Abläufe aus `11_V23_VS01_HAUPTABLAEUFE_6.csv`, Status dort `SPEC_NOT_ENGINE_VERIFIED`: A „Die Welt empfängt dich“, B „Der beschädigte Generator“, C „Die Brücke“, D „Das Unwetter“, E „Die Folgen“, F „Generationen-Labor“ (der Text der Quelle trennt F von der Hauptinkarnation).

Acht Rollen aus `18_V24_NPCS_8_CANON_ROLLEN.csv`, `CanonStatus` `APPROVED_ROLE_AND_ROUTINE`, `AppearanceStatus` `NOT_APPROVED`: N01 Werkstatt, N02 Reparaturkundschaft, N03 Markt, N04 Lieferung, N05 Gemeinde, N06 Wetter, N07 und N08 Bewohner. Die Rollenkürzel der Quelle bleiben. Erscheinungsbilder bleiben offen.

## GLB-Abgleich

Alle 38 Dateien der Hülle treffen `38_GLB_QUELLEN.csv`. Dieselben Bytes liegen im Repo unter `assets/source_glb/GLB/`.

Von 37 unterschiedlichen Hashes (004 und 005 teilen sich einen) liegen 29 auch im entpackten V56 und 6 auch im entpackten V58, ohne Überschneidung dieser beiden Mengen. `VS01_R02_HANDEL_001.glb` und `VS01_R06_WETTER_001.glb` liegen mit demselben Hash in V59 `04_3D_GLBS/`, nicht in den ZIPs V56 und V58.

Die 38 Tafeln der Hülle sind die Dateien, die ins Repo kopiert wurden. V57 enthält 30 PNG mit dem Namensmuster `*_TURNAROUND.png`. Keine dieser SHA256 ist unter den 38 Tafeln.

## V59-Ordner neben den 37 ZIPs

`00_START`, `01_AUDIT`, `02_KANON`, `03_ARBEITSPAKETE`, `04_3D_GLBS`, `05_3D_ANSICHTEN`, `06_TECHNIK`, `07_QA`, `08_CLAUDE_CODE`, `09_VERSIONSICHERUNG`, `10_ORIGINALQUELLEN`, `11_QUELLENPAKETE`, `12_BLENDER_SKRIPE_NICHT_AUSGEFUEHRT`.

In `04_3D_GLBS` liegen 38 GLB-Dateien. Ob jede davon bytegleich zur Hülle ist, beantwortet die Datei-CSV über die Spalte `sha256`. Für Handel und Wetter ist die Gleichheit oben genannt. Die Brücken-Dublette ist im Register bereits mit zwei gleichen Hashes eingetragen.

## Arbeitskopie, nur Dateibestand

Gezählt ohne neuen Engine-Lauf. Archivberichte siehe [M00_IST_SOLL.md](M00_IST_SOLL.md). `Genesis.uproject`: Engine-Zuordnung `5.8`, Modul `Genesis`, Plugins Modeling Tools, StateTree, GameplayStateTree, ModelContextProtocol, AllToolsets, Python, Editor Scripting. Kein `GenesisSlice`. Content der Kopie: Testmap und zwei Appearance-Data-Assets. Mannequin-Dateien sind ignoriert und in diesem Stand nicht enthalten.
