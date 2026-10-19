# GENESIS – Ehrlicher Projektstand

Stand: 2026-10-18 · Zweig `setup/ue58-projekt` (auf GitHub gepusht, `main` unverändert)

## WK-M01-010 – Neues UE-5.8.3-C++-Projekt · Status: GETESTET (lokal)

| Was | Datei / Beleg | Ergebnis |
|---|---|---|
| Projektdatei | `Genesis.uproject` (EngineAssociation 5.8) | vorhanden |
| C++-Modul `Genesis` | `Source/Genesis/*`, `Source/*.Target.cs` | kompiliert: `Build.bat GenesisEditor Win64 Development` → `Result: Succeeded` (41 s) |
| Rendering-Grundeinstellung | `Config/DefaultEngine.ini` | DX12 SM6, Lumen GI + Reflexionen, Hardware-Raytracing, Virtual Shadow Maps, Nanite, TSR, keine Auto-Belichtung |
| Plugins | StateTree, GameplayStateTree, ModelingTools, ModelContextProtocol + AllToolsets (nur Editor) | geladen laut Log |
| Git LFS | `.gitattributes` | uasset, umap, blend, fbx, glb, gltf, usd, png, jpg, exr, tga, hdr, wav, ogg, mp4, mov, ttf, otf, zip |
| Editor-Starttest | `UnrealEditor-Cmd -nullrhi`, Log `Saved/Logs/SmokeTest.log` | „Engine is initialized“, Modul `Genesis` geladen, sauberes „Exiting“; 0 Warnungen. 17× `LogAutomationTest: Error: Condition failed` stammen aus dem Engine-eigenen Selbsttest `UE::UnifiedErrorTest`, nicht aus GENESIS |

## WK-M02-001 – Soul/World/Life + transaktionaler SaveBundle · Status: GETESTET (lokal)

| Was | Datei / Beleg | Ergebnis |
|---|---|---|
| Datenmodell | `Source/Genesis/Public/Save/GenesisSaveTypes.h` | Soul (SoulId, Echo-Erinnerungen, Enthüllungs-Guards), World (Jahr, Tag, Uhrzeit, Seed, Ereignisse), Life (LifeIndex, BodyAssetId, Lebensabschnitt, Alter, Ort, Transform, Beziehungen, Erinnerungen, Inventar, Geld in Cent) – immer gemeinsam in einem Bundle |
| SaveStore | `Source/Genesis/Private/Save/GenesisSaveStore.cpp` | Temp-Datei schreiben + auf Platte flushen → zurücklesen + SHA1 prüfen → atomarer Austausch (`ReplaceFileW`, alte Datei wird `.bak`); Laden: Hauptdatei, sonst Sicherung, `.tmp` nie |
| GameInstance + Subsystem | `UGenesisGameInstance`, `UGenesisSaveSubsystem` (in `DefaultEngine.ini` eingetragen) | kompiliert; im Spiel noch nicht benutzt (es gibt noch kein Level) |
| Automatische Tests | `Genesis.Save.*` (6 Tests), Bericht `docs/evidence/WK-M02-001/automation_report.json` | 6/6 bestanden (1 mit erwarteter Warnung „Sicherung geladen“): Hin-und-zurück, Abbruch nach Temp-Datei, halbe Temp-Datei, defekte Hauptdatei → Sicherung, Abbruch beim ersten Speichern, zukünftiges Schema abgelehnt |
| Echter Absturztest | `Tools/Tests/Run-SaveCrashTest.ps1`, `docs/evidence/WK-M02-001/crash_test.csv` | 15/15 harte Prozessabbrüche (TerminateProcess, 20–1500 ms nach Start des Dauerspeicherns, ~200 KB je Stand): jedes Mal vollständiger Stand geladen, Soul/World/Life aus derselben Transaktion, Sequenz nie rückwärts |

Einschränkung: In allen 15 Läufen lag der Abbruch nie genau im Austauschmoment (`backup=0`); der Rückfall auf `.bak` ist nur durch den automatischen Test mit beschädigter Hauptdatei belegt. Stromausfall-Test (echtes Ausschalten) wurde nicht gemacht.

## WK-M02-002 + WK-M02-003 – Spielfigur, Steuerung, Kamera, Testlevel, Austausch-Schnittstelle · Status: GETESTET (lokal)

| Was | Datei / Beleg | Ergebnis |
|---|---|---|
| Spielfigur | `AGenesisCharacter` | Gehen 150 cm/s (5,4 km/h), Laufen 360 cm/s (13 km/h), Sprung ~45 cm, Treppenstufe bis 40 cm, begehbar bis 44° |
| Steuerung | `UGenesisInputSet` (Enhanced Input, im Code definiert) | WASD/Pfeile + linker Stick (Totzone 15 %), Maus + rechter Stick (bildratenunabhängig, 160 °/s), Leertaste/A springen, Shift halten bzw. L3 umschalten = laufen |
| Third-Person-Kamera | Spring Arm 2,8 m, Schulterversatz, Kollisionsprüfung, leichte Nachführung, Blick −70°…+55° | Kamera hängt an der **Vertrags**-Ankerhöhe (162,6 cm), nicht am Mesh |
| Austausch-Schnittstelle | `UGenesisCharacterAppearance` (DataAsset: Mesh, AnimBP, Materialien, Physik, Kapsel), `UGenesisCharacterRegistry` (Projekteinstellungen: feste ID → Aussehen + **Proportions-/Kameravertrag**) | Spiellogik kennt nur `CharacterAssetId`; ein Modell wird nur eingesetzt, wenn es den Vertrag erfüllt (Höhe, Ankerhöhe, Pflichtknochen, Skelett, AnimBP-Skelett, aufrecht, Fußsohle auf Kapselboden), sonst bleibt das alte |
| Basismodell (Proxy) | UE5-Mannequin Manny/Quinn aus der Engine-Installation, `Content/Genesis/Characters/Appearances/DA_Proxy_Adult_M/F` | gemessen: 180,5 / 180,2 cm, Kopfknochen 162,6 / 162,5 cm (`docs/evidence/WK-M02-002/measurements.json`). **Proxy, kein GENESIS-Charakter** |
| Testlevel | `Content/Maps/L_GenesisTest.umap`, erzeugt durch `Tools/Editor/build_wk_m02_002.py` | 120×120 m Boden, Treppe (17/29 cm), Rampe 10°, Wand, Durchgang 1×2,1 m; Sonne 90 000 lx, Himmel, Wolken, Nebel, Belichtung physikalisch ISO 100, 1/100 s, f/16 |
| Automatische Tests | `Genesis.*` – 12 Tests, Bericht `docs/evidence/WK-M02-002/automation_report.json` | **12/12 bestanden** (1 mit erwarteter Warnung): Tastenbelegung, alle Registry-Einträge erfüllen Vertrag, Modelltausch behält Spiellogik und Kamerahöhe (162,60 → 162,60 cm), Vertragsverstoß wird abgelehnt, Wechsel per ID, Gehen/Laufen/Springen im echten Testlevel per Play-in-Editor |
| Spielstart mit Grafik | `-game -GenesisAutoTest`, Log `docs/evidence/WK-M02-002/game_autotest.log`, Bild `autotest_shot.png` | Figur aufrecht, geht 4,0 m, am Boden, Kamera auf 164,8 cm, Schatten sichtbar |

Unterwegs gefundene und behobene Fehler: Mesh lag um 90° gekippt (Python-Rotator falsch zugeordnet; neue Vertragsregel „aufrecht“ erkennt das jetzt), erstes Bild komplett weiß (Belichtung jetzt physikalisch statt als Aufhellung), Kamera-Test prüfte relative statt absolute Höhe.

Nicht getestet: echte Bedienung mit physischem Controller und Maus durch einen Menschen (nur Tastenbelegung und Bewegungslogik sind automatisch geprüft). Kein Reality Check bestanden – Level und Figur sind bewusst Graubox/Proxy, nicht fotorealistisch.

**Lizenz-Hinweis:** Das Mannequin ist Epic-Template-Inhalt. Weil das Repo öffentlich ist, liegt es **nicht** im Repo (`.gitignore`), sondern wird nach dem Klonen mit `Tools/Setup/Copy-EngineMannequin.ps1` aus der lokalen Engine kopiert.

## WK-M02-004 – Weltzeit, Jahreszeiten, Alterung, Lebensabschnitte, Speichern von Position/Zeit · Status: GETESTET (lokal)

| Was | Datei / Beleg | Ergebnis |
|---|---|---|
| Spielstand Schema 2 | `GenesisSaveTypes.h` | Weltdatum (`WorldDateTime`) statt Jahr/Tag/Stunde; Leben mit Zeugungs- und Geburtszeitpunkt statt gespeicherter Alterszahl (Alter wird immer berechnet) |
| Migration 1 → 2 | `GenesisSaveStore.cpp` | alte Spielstände werden beim Laden umgerechnet; Test mit echtem Schema-1-Spielstand bestanden |
| Lebenszyklus | `FGenesisLifeCycle`, Einstellungen `UGenesisTimeSettings` (Projekteinstellungen > Genesis Time) | vor der Geburt nach Tagen ab Befruchtung: Befruchtung < 14 → Embryo < 56 → Fetus < 266 → Geburtszeitraum; **die Geburt selbst ist ein Spielereignis** (`CompleteBirth`), kein Automatismus. Danach: Säugling < 1 J → Kind < 12 → Jugend < 18 → Erwachsen < 65 → Alter; Echo bleibt Echo |
| Jahreszeiten | `GetSeason` | meteorologisch, Nordhalbkugel (Annahme: Primärwelt Mitteleuropa) |
| Weltuhr | `UGenesisWorldClockSubsystem` | läuft im Spiel mit 60× (1 echte Minute = 1 Spielstunde, einstellbar), pausierbar (z. B. für Filme), Zeitraffer `SkipTime`; meldet neuen Tag, neue Jahreszeit und jeden durchlaufenen Lebensabschnitt (auch mehrere bei einem Zeitraffer) |
| Position/Ort speichern | `UGenesisSaveSubsystem::SaveToSlot/LoadFromSlot` | übernimmt Position, Blickrichtung und Karte der Figur; setzt sie beim Laden zurück (Laden in eine andere Karte ist noch nicht möglich und wird abgelehnt statt falsch teleportiert) |
| Tests | `docs/evidence/WK-M02-004/automation_report.json` | **20/20 bestanden** (1 mit erwarteter Warnung). Neu: Lebensabschnitte vor/nach Geburt, Jahreszeiten, Tag-/Jahreszeitwechsel, 20-Jahre-Zeitraffer (Kind → Jugend → Erwachsen, Alter 20,0821 J), Befruchtung bis Geburt, Migration, **Rundlauf im echten Spiel (PIE):** Position 300/−200 exakt, Weltzeit-Abweichung 0, Alter und Abschnitt gleich, Uhr lief mit ~57 Spielsekunden pro Sekunde |
| Absturztest erneut | `docs/evidence/WK-M02-004/crash_test_schema2.csv` | 15/15 harte Abbrüche konsistent |

Unterwegs gefundener Fehler (betraf auch WK-M02-001): Unreals JSON-Standardexport kürzt Datumswerte auf ganze Sekunden. Jetzt wird ISO 8601 mit Millisekunden geschrieben, und die Weltuhr rechnet in ganzen Millisekunden mit Übertrag. Laden ist dadurch verlustfrei (Abweichung 0).

Annahmen, die du prüfen solltest: Altersgrenzen nach der Geburt (1/12/18/65) sind Vorschläge, das Drehbuch nennt nur Szenenalter. Das Testlevel startet mit einem **Testprofil** (Erwachsener, 30 Jahre, 15.06.2026 10:00), das kein Kanon ist.

## WK-M02-005 – Sonnenstand und Belichtung folgen der Weltuhr · Status: GETESTET (Nacht siehe WK-M02-006)

| Was | Datei / Beleg | Ergebnis |
|---|---|---|
| Sonnenstand | `FGenesisSolar` (Astronomical-Almanac-Näherung), Ort in Projekteinstellungen > Genesis Time (vorläufig 49° N, 10° O, MEZ/MESZ nach EU-Regel) | Tests gegen Geometrie: Sommer-Mittag 64,435° (Soll 64,44°), Winter-Mittag 17,566° (Soll 17,56°), Tagundnachtgleiche 40,95° (Soll ca. 41°), Sonnenhöchststand 11:22 UTC, Aufgang am 20.03. im Osten (90,4°), Sommerzeit-Wechsel 2026 korrekt |
| Belichtung | `GetClearSkyEV100`: Stützwerte der fotografischen Belichtungstabelle (Sunny-16 = EV 15 …; Nachtwerte in WK-M02-006 neu abgeglichen), lineare Interpolation; Umsetzung laut Engine-Quelltext `Bias = −EV100` | Test: monoton, keine Sprünge |
| Himmels-Steuerung | `AGenesisSkyController` (vom GameMode automatisch erzeugt) | dreht die Sonne (Licht bleibt 90 000 lx) und setzt die Belichtung je Frame passend zur Weltzeit |
| Tests | `docs/evidence/WK-M02-005/automation_report.json` | **24/24 bestanden** (2 Warnungen: erwartete „Sicherung geladen“, Internet-Prüfung der Engine) |
| Bildschirmfotos 15.06.2026 | `sky_0700/1320/2100/2330.png`, Werte `sky_shots.log`, Messung `luminance.txt` | 07:00 (14,2°, Ost-Nordost), 13:20 (64,3°, Süd), 21:00 (2,6°, Nordwest, goldene Stunde): glaubwürdig, gleichmäßig belichtet, nichts ausgebrannt. **23:30 (−13,6°): Bild komplett schwarz** |

Reality Check Nacht: **nicht bestanden** (Stand WK-M02-005). Ursache: Bei −13,6° erreicht kein direktes Sonnenlicht mehr die modellierte Atmosphäre; das reale Restlicht (Mehrfachstreuung der Dämmerung, Sterne, Airglow, Mond) fehlt im Level. Am 15.06.2026 ist zudem etwa Neumond. Kein Aufhelllicht eingebaut, weil es keine reale Quelle hätte. → behoben mit WK-M02-006.

## WK-M02-006 – Nachthimmel: Mond, Sterne, Airglow, Dämmerung · Status: GETESTET (lokal)

| Was | Datei / Beleg | Ergebnis |
|---|---|---|
| Mond | `FGenesisSolar::ComputeMoon` (Hauptglieder der Mondtheorie, Parallaxe; Helligkeit nach Allen/Krisciunas-Schaefer) | Test an den Finsternissen 2026: Mondfinsternis 03.03. und 28.08. → Vollmond (Phasenwinkel 0,47° / 0,35°, 0,27 / 0,26 lx); Sonnenfinsternis 17.02. und 12.08. → Neumond (179°) |
| Mondlicht | zweites Atmosphärenlicht im `AGenesisSkyController`, 4100 K, Beleuchtungsstärke aus Phase und Entfernung | wirft Schatten, Atmosphäre dämpft/färbt es |
| Sternenhimmel | NASA-SVS-Sternkarte 8K (gemeinfrei, Credits im Register `docs/asset-vault/ASSET_REGISTER.md`), Himmelsmaterial `M_GenesisSky` (Python-Skript `Tools/Editor/build_wk_m02_006.py`), Drehung nach Ortssternzeit | Test: Himmelsachsen orthonormal und echte Drehung; Polarstern auf 49° Höhe im Norden; Vega/Sirius identisch mit unabhängigem Rechenweg. Helligkeit über die gemessene Kartenhelligkeit auf 6,8·10⁻⁵ cd/m² mittleres Sternlicht geeicht (Leinert et al. 1998), Extinktion 0,2 mag pro Luftmasse |
| Airglow | im Himmelsmaterial: 1,2·10⁻⁴ cd/m² im Zenit, zum Horizont heller (Van-Rhijn-Effekt), leicht grünlich | sichtbar als Grundhelligkeit des Nachthimmels |
| Tiefe Dämmerung | `GetTwilightZenithLuminance` (Messwerte Patat et al. 2006, Rozenberg 1966), setzt ab −5° ein, wo Unreals Atmosphäre aufhört (gemessen: oberer Himmel ab −8,3° nur noch 2,5/255, Bilder in `twilight_measurement_unreal_only/`) | |
| Belichtung | Nachtteil der Tabelle neu abgeglichen (Milchstraße EV −7, nautische Dämmerung −3), Mond addiert (Vollmond hoch = EV −2,5) | Bildhelligkeit fällt jetzt gleichmäßig: 21:45 → 22:30 → 23:30 → Neumond = 52 → 35 → 20 → 10 (von 255), nichts ausgebrannt |
| Tests | `docs/evidence/WK-M02-006/automation_report.json` | **26/26 bestanden** |
| Bilder | `docs/evidence/WK-M02-006/sky_*.png`, Messung `luminance.txt`, Werte `sky_shots.log` | Tag unverändert; blaue Stunde, nautische Dämmerung mit ersten Sternen, Neumondnacht mit Milchstraße, Vollmondnacht mit Mondschatten: glaubwürdig |

Bekannte Schwächen (nicht kaschiert):
- Mondscheibe wird immer voll gezeichnet; bei Halbmond ist nur die Helligkeit richtig, nicht die Form.
- Roter Horizontstreifen in der nautischen Dämmerung etwas zu gesättigt.
- Die Proxy-Figur hat ein leuchtendes Unreal-Logo auf der Brust (Epic-Mannequin), das nachts auffällt; entfällt mit der echten GENESIS-Figur.
- Belichtungsstufen sind wie in der Nachtfotografie gewählt (Nachtbilder heller als das Auge sie sieht). Ob GENESIS nachts eher „Foto“ oder „Augenwahrnehmung“ zeigen soll, ist eine Gestaltungsentscheidung.
- Sternkarte und Textur liegen nicht im Repo (Git-LFS-Kontingent): nach dem Klonen `Tools/Setup/Get-StarMap.ps1` ausführen.

## WK-M03-001 – Kausalgraph und NPC-Gedächtnis (Verbesserung 1/17) · Status: GETESTET (lokal, ohne sichtbare NPCs)

| Was | Datei / Beleg | Ergebnis |
|---|---|---|
| Spielstand Schema 3 | `GenesisSaveTypes.h` | Welt: Ereignisse (`FGenesisCausalEvent`: Typ, Zeit, Ort, Leben, Handelnder, Betroffene, Zeugen, Ursachen, Bewertung, Bedeutung, Missions-/Szenenbezug), NPC-Zustände mit Erinnerungen und Haltungen. Leben: verdecktes Verhaltensprofil. Schema-2-Spielstände laden mit leerem Graphen |
| Kausalgraph | `FGenesisCausality` (reine Funktionen), `UGenesisCausalitySubsystem` | Ereignis eintragen nur mit gültigem Typ, Handelndem und Ursachen, die existieren und nicht in der Zukunft liegen; Ursachenkette abfragbar (Grundlage für belegte Rückblenden C12/C16) |
| NPC-Gedächtnis | Betroffene: volle Erinnerung, Zeugen: halbe, Gehörtes: abhängig vom Vertrauen in den Erzähler | Erinnerungen verblassen (Halbwertszeit 60 Tage bei Beiläufigem bis ca. 3 Jahre bei Lebensveränderndem); Ereignisse ab Bedeutung 0,8 werden nie vergessen; das Ereignis selbst bleibt im Graphen, auch wenn es niemand mehr erinnert |
| Haltungen | Vertrauen und Zuneigung je Gegenüber; wer eine starke Meinung hat, ändert sie langsamer | grobe Stufe (feindselig … eng verbunden) für Verhalten/Dialog, **nie als Zahl im HUD** |
| Neues Leben | Spieler-ID je Leben (`PLAYER_L<n>`) | Nach der Wiedergeburt ist der Spieler für alle ein Fremder, aber die Welt erinnert sich an das frühere Leben (Kanon: neue körperliche Identität) |
| Verhaltensprofil | z. B. Empathy, Reliability, Courage | wird mitgeführt, aber nirgends angezeigt und nie als Strafe benutzt (Kanon: kein Karma-Gericht) |
| Widerspruchsprüfung | `ValidateGraph` | erkennt doppelte IDs, fehlende oder spätere Ursachen, Zyklen, unbelegte Erinnerungen, Werte außerhalb −1…1 |
| NPC-Komponente | `UGenesisNpcMemoryComponent` | Figuren im Level fragen Haltung zum Spieler und ihre präsentesten Erinnerungen ab (nur kompiliert, noch keine NPC im Level) |
| Ereignistypen | `Config/DefaultGame.ini` (Projekteinstellungen > Genesis Causality): HELPED, GIFT, PROMISE_KEPT, PROMISE_BROKEN, IGNORED_REQUEST, HARMED, ARGUMENT, SAVED_LIFE | **Gestaltungs-Startwerte, kein Kanon** – bitte prüfen |
| Absturztest | `docs/evidence/WK-M03-001/crash_test_schema3.csv` | 15/15 harte Abbrüche konsistent (Schema 3) |
| Tests | `docs/evidence/WK-M03-001/automation_report.json` | **34/34 bestanden.** Neu: Typen geladen, Erinnerungen und Haltungen beim Eintragen, Ursachenkette + Ablehnung unbekannter/zukünftiger Ursachen, Verblassen, Gerücht abhängig vom Vertrauen (−0,05 vs. −0,01), neues Leben = Fremder, Widerspruchsprüfung, Speichern/Laden inkl. Gerüchtequelle und Schema-2-Spielstand |

Noch nicht: automatische Gerüchte zwischen NPCs, Dialoge, die Erinnerungen ansprechen, Haltungen, die sich ohne neue Ereignisse langsam erholen. (Wahrnehmung: siehe WK-M03-002.)

## WK-M03-002 – NPC-Tagesablauf (StateTree + Smart Objects) und Wahrnehmung · Status: GETESTET (lokal, Graubox)

| Was | Datei / Beleg | Ergebnis |
|---|---|---|
| NPC-Figur + KI | `AGenesisNpcCharacter` (Aussehen über Registry, Gedächtnis-Komponente), `AGenesisNpcAIController` mit StateTree-Komponente | 3 Proxy-NPCs `NPC_TEST_01..03` im Testlevel |
| Tagespläne | Projekteinstellungen > Genesis NPC (`Config/DefaultGame.ini`) | Schlafen, Arbeiten, Markt, Freizeit je Stunde, auch über Mitternacht. **Testdaten, kein Kanon** |
| StateTree „Tagesablauf“ | `/Game/Genesis/AI/ST_GenesisDailyLife`, erzeugt von `UGenesisNpcAssetBuilder` (C++) über `Tools/Editor/build_wk_m03_002.py` | 4 Zustände mit eigener Bedingung („Plan sieht Aktivität vor“) und Aufgabe („Aktivität ausführen“); Freizeit als Rückfall; nach jedem Wechsel wird neu gewählt |
| Smart Objects | `/Game/Genesis/AI/SOD_Sleep/Work/Market/Leisure`, Plätze `AGenesisActivitySpot` (Betten, Werkbank, Marktstand, Bank) | Platz suchen (nächster freier), reservieren, **von vorn** herangehen, belegen, bei Planwechsel freigeben. Wer 3 s feststeckt, tritt zur Seite und sucht neu |
| Navigation | Navigationsvolumen 60 × 60 m, Navigationsnetz zur Laufzeit dynamisch | alle Figuren (auch die Spielfigur) weichen einander aus (RVO) |
| Wahrnehmung | `FGenesisPerception`, `UGenesisCausalitySubsystem::RecordEventAt` | Zeugen automatisch: Sichtweite nach Licht (Tag 40 m, Nacht bis 8 m), Blickwinkel ±105°, Sichtlinie (Wände verdecken) |
| PIE-Test über einen Spieltag | `Genesis.Npc.PIE.DailyScheduleAndPerception`, Protokoll `docs/evidence/WK-M03-002/npc_day_log.txt` | 03:00, 09:00, 12:30, 15:00, 21:30, 23:30: alle drei Figuren am richtigen Platz (Ankunft nach 17–31 s Echtzeit). Wahrnehmung: am Tag nur die Figur in 5 m mit Blick hin; hinter der Wand, 60 m entfernt oder wegschauend: kein Zeuge; nachts 15 m nein, 6 m ja |
| Alle Tests | `docs/evidence/WK-M03-002/automation_report.json` | **35/35 bestanden.** Verbleibende Warnungen: erwartete „Sicherung geladen“; 6× Crowd-Startmeldung der Engine (Navigationsnetz entsteht erst zur Laufzeit, harmlos) |
| Spielstart mit Grafik | `sky_20260615-1000_40_-10.png` (Markt), `sky_20260615-1000_315_-10.png` (Werkstatt) | Figuren stehen um 10:00 an Marktstand und Werkbank |

Unterwegs gefundene und behobene Fehler: Test setzte die Uhrzeit vor dem Spielstart (überschrieben); Bankplätze zu eng für eine Figur; Figuren liefen entlang der Sitzreihe in eine sitzende Figur; NPCs kannten die stehende Spielfigur nicht als Hindernis; Asset-Builder konnte vorhandene Assets nicht überschreiben.

Noch nicht: Animationen für Tätigkeiten (Figuren stehen am Platz, statt zu liegen/arbeiten/sitzen), Türen/Innenräume, Begrüßung oder Reaktion beim Vorbeigehen, automatische Gerüchte im Gespräch, Tagespläne aus der Spielbibel (Flussdorf-Figuren).

## WK-M03-003 – Missionen und Dialoge mit Entscheidungen · Status: GETESTET (lokal, Platzhalter-Inhalt)

| Was | Datei / Beleg | Ergebnis |
|---|---|---|
| Datenmodell | `GenesisStoryTypes.h`: Quest (Schritte, Kanten mit Auslöser und optionaler Weltbedingung, Ausgänge), Dialog (Knoten, Antworten, Folgen, Vertrauensbedingung); Spielstand Schema 4 mit Questfortschritt und Verlauf | Quests und Dialoge sind Daten-Assets, keine Programmierung pro Mission |
| Logik | `FGenesisStory` (reine Funktionen), `UGenesisStorySubsystem` | Antwort wirkt erst beim Wählen (atomar): Weltzustand, Ereignis im Kausalgraphen (Zeugen über Wahrnehmung), Questauslöser. Antworten können Vertrauen voraussetzen |
| Sackgassen-Prüfung | `FGenesisStory::ValidateQuest/ValidateDialog` | erkennt: Schritt ohne Ausweg, kein Questende erreichbar, unerreichbare Schritte/Knoten, fehlende Folgeschritte/-knoten, Auslöser die nie kommen oder ohne Wirkung bleiben, Auslöser nur unter Bedingung, Gesprächsschleifen ohne Ausgang, Knoten mit nur bedingten Antworten, unbekannte Figuren und Ereignistypen |
| Spiel | Taste E / Controller X: Figur ansprechen; 1–4 / Steuerkreuz: antworten; `AGenesisHUD` | **Platzhalter-HUD** (Text auf dem Bild, keine gestaltete Oberfläche); zeigt Gespräch und aktuelles Ziel, nie Vertrauens- oder Karmawerte |
| Testmission | `TEST_Q01` „Die Waage“ (`/Game/Genesis/Quests`, gebaut von `Tools/Editor/build_wk_m03_003.py`) | **Platzhalter-Inhalt, kein Kanon.** 3 Schritte über alle drei NPCs, 4 Ausgänge/Wege (ablehnen, helfen, behalten, Vertrauens-Antwort) |
| Tests | `docs/evidence/WK-M03-003/automation_report.json` | **40/40 bestanden.** Neu: alle Projekt-Quests ohne Fehler; kaputte Testquest – alle 12 Fehlerarten erkannt; alle Wege führen zum richtigen Ausgang mit passender Wirkung auf Vertrauen und verdecktes Profil; Laden mitten in der Mission und zu Ende spielen; **Durchspielen im laufenden Spiel (PIE)** über die echte Ansprech-Funktion |
| Bild | `docs/evidence/WK-M03-003/dialog_hud_0900.png` | Gespräch mit der Händlerin am Markt, drei Antworten |

Beobachtung: Bei der Übergabe am Markt war die Nachbarin **kein** Zeuge, weil sie zum Stand schaute und die Übergabe hinter ihrem Rücken stattfand – das ist das gewollte Verhalten der Wahrnehmung.

Noch nicht: echte Missionen aus der Spielbibel (L00–L15, G01–G02, J00–J24 müssen erst aus den Quellpaketen extrahiert werden), gestaltete Oberfläche, Sprachausgabe, Umlaute in den Platzhaltertexten (ae/oe statt ä/ö), Missionsschritte ohne Gespräch (Orte erreichen, Gegenstände), Abbrechen/Wiederholen von Gesprächen per Taste.

## Was noch NICHT existiert
- Keine GENESIS-Figuren (nur Proxy-Mannequin), keine Spielwelt außer dem Graubox-Testlevel, nur 3 Test-NPCs, nur eine Platzhalter-Mission, keine gestaltete UI.
- Wetter (Wolkenmenge, Regen) beeinflusst Licht und Belichtung noch nicht; die Belichtungstabelle gilt für klaren Himmel.
- Figur wechselt beim Altern noch nicht ihr Aussehen (Kinder-/Altersmodelle fehlen; die Schnittstelle dafür existiert).
- Wiedergeburt (Leben abschließen → Erinnerungen in die Seele → neues Leben) ist nur als Datenmodell vorbereitet, nicht programmiert.
- Offene Kreativentscheidungen: ScriptLock-Endfreigabe, C15/C16 (CON33-01), Epochenumfang.

## WK-M00-001 – Originalquellen erschlossen · Status: ERLEDIGT (nur gelesen)

| Was | Ergebnis |
|---|---|
| Quellkette | V62 → V61 → V60 → V59 → 37 Quellpakete, insgesamt 109 ZIP-Archive und 4043 Dateien, entpackt im temporären Leseordner (nicht im Projekt) |
| Prüfsummen | 64 Prüflisten, **3862 Einträge korrekt, 0 fehlende Dateien, 0 inhaltliche Abweichungen** (9 Meldungen betreffen nur die Prüflisten selbst, die sich nicht selbst prüfen können) |
| Gefunden | alle Missionsquellen: L00–L15 und G01–G02 (V21), J00–J11 (Vorschlag 20B), J12–J24 (V27–V30), Flussdorf-Weltbibel mit 8 Regionen, Bewohner N01–N08 und Missionsbibel (V24) |
| Extrakt | `Desktop\GENESIS_V62_PLANUNG\WK-M00-001_ORIGINALMISSIONEN_UND_FLUSSDORF.md` (wörtlich, mit Prüfsumme je Quelle). **Bewusst nicht im öffentlichen Repo**, weil es Story und geschützte Enthüllungen enthält |

Hinweis: Alle Missionsquellen tragen den Status „wartet auf Freigabe durch die Spielleitung“. Sie sind die Grundlage für echte Missionen, aber noch kein freigegebener Kanon.

## Nächster Schritt (Vorschlag, wartet auf Freigabe)
WK-M03-004: Erste echte Mission statt Platzhalter – L08 „Die Nacht der Naturgewalt“ im Flussdorf (Sturm, Brücke, Wetterstation passen zum Vertical Slice) mit den Original-Rollen N01 Werkstatt, N04 Lieferperson, N05 Gemeindekoordination; Inhalte nur aus den Quellen, offene Punkte als ungeklärt markiert.
