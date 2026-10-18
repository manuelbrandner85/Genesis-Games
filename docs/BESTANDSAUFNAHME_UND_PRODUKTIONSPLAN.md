# GENESIS – Bestandsaufnahme, Lückenanalyse und Produktionsplan

Stand: 2026-10-18 · Repo `manuelbrandner85/Genesis-Games`, Zweig `setup/ue58-projekt`
Antwort auf den „Ultimate Production Masterprompt“ (Punkte 1–10). Nur Belegtes gilt als vorhanden.

## 0. Projektentscheidung

Der Masterprompt nennt `manuelbrandner85/GENESIS-GAME` als bestehendes Projekt. Mit dem angemeldeten GitHub-Konto ist dieses Repo **nicht auffindbar** (HTTP 404). Sichtbar sind nur `Genesis-Games` und `Genesis-Der-Kreislauf-des-Lebens-APP` (1,9 MB, nicht untersucht).
**Beschluss des Projektinhabers (2026-10-18):** `Genesis-Games` wird weitergebaut. Die Verbesserungen 1–17, 19–26 gelten hier als verbindliche Qualitätsliste. 18 und 27 sind abgelehnt, 28 ist offen.

## 1. Ergebnis der Repository- und Spielbibelanalyse

| Quelle | Inhalt | Status |
|---|---|---|
| `Genesis-Games` (dieses Repo) | UE-5.8.3-C++-Projekt, Speichersystem (siehe `STAND.md`) | 2 Arbeitspakete getestet |
| V62-Übergabe-ZIP (`Downloads\GENESIS_V62_…zip`, SHA256 geprüft) | ScriptLock C00–C21, 17 Phasen N00–N16, 226 Anforderungen, 196 VS01-Assets, 40 Animationen, 43 Missionsanker, 113 Shots, 38 GLB-Proxies | Dokumentation, nichts davon in einer Engine gebaut |
| ScriptLock „Vorschlag 11“ | Drehbuch C00–C21 mit Dialogen, Shots, Szenenschnittstellen und Abnahmetests | **Script-Lock-Kandidat 1.1, Endfreigabe ausstehend** |
| `GAMEFORGE Spiele\GENESIS` | GAMEFORGE-Gerüst, 5 Referenzdateien, veraltete SPIEL.md („neun Phasen“) | kein Blender/Unreal-Inhalt |
| `GAMEFORGE Spiele\GENESIS_V48_NPC_…` | 13 Dateien: NPC-Bildaufträge N01/N04/N05, 1 Konzeptbild | Referenzentwurf, nicht freigegeben |

Kanon-Kern (aus ScriptLock, unverändert übernommen): Prolog 2026 mit altem Mann und erwachsener Tochter. Er ist eine frühere Inkarnation derselben Seele, aufgelöst erst in C20. Biologie wird wissenschaftlich plausibel gezeigt, Soul/Echo ist klar gekennzeichnete Fiktion. Es gibt keine feste Biografie, keine Strafe/Karma-Strafe und kein Game Over. Das Kollektiv ist nicht Gott und wird vor C19 nicht verraten. C00 und das C20-Replay müssen bild- und tongleich sein.

## 2. Kapitel C00–C21 und tatsächlicher Produktionsstand

Typ nach ScriptLock IV-B: A = fest, B = zustandsgebunden, C = Archiv-Replay, D = weltabgeleitet.

| ID | Titel | Phase | Ort / Alter | Typ | Stand |
|---|---|---|---|---|---|
| C00 | Der letzte Augenblick | N00 | Schlafzimmer 2026, alter Mann + Tochter | A | nur Drehbuch |
| C01 | Ein winziger Anfang | N00/N01 | Übergang Erde → Mikrowelt | A | nur Drehbuch |
| C02 | Zwei werden eins | N01 | Eileiter, Zygote | A/B | nur Drehbuch |
| C03 | Ich höre dich | N03 | Zuhause der Schwangeren + Uterus | B | nur Drehbuch |
| C04 | Der erste Atemzug | N04 | Geburtsumgebung | B | nur Drehbuch |
| C05 | Der erste Schritt | N05 | Wohnraum, Kleinkind | B | nur Drehbuch |
| C06 | Der freie Platz | N05/N06 | Schule, 7–9 J. | B | nur Drehbuch |
| C07 | Der letzte Sommer | N06 | Sommerort, 11–13 J. | B | nur Drehbuch |
| C08 | Das Versprechen | N06 | Schule/Training, 14–17 J. | B | nur Drehbuch |
| C09 | Die Tür | N07 | persönlicher Raum, 17–22 J. | B | nur Drehbuch |
| C10 | Zwischen uns | N07 | Ort einer Beziehung | B | nur Drehbuch |
| C11 | Die Nachricht | N07 | Alltag, Erwachsener | B | nur Drehbuch |
| C12 | Der Tisch der Jahre | N08 | Ankerort über Jahre | B | nur Drehbuch; braucht Replay-Snapshots |
| C13 | Der Ort von damals | N08 | Kindheitsort Jahre später | B | nur Drehbuch |
| C14 | Was bleibt? | N08 | Sterbeort | B | nur Drehbuch |
| C15 | Kein Körper mehr | N09 | Dunkelraum → Erinnerungsraum | C | nur Drehbuch; **Konflikt CON33-01** |
| C16 | Die andere Seite | N09/N10 | „Bibliothek“ → Erinnerungsort | C | nur Drehbuch; **Konflikt CON33-01** |
| C17 | Ein neuer Herzschlag | N12 | Echo → neuer Anfang | D | nur Drehbuch |
| C18 | Die vertraute Fremde | N12 | Alltagsort neues Leben | B | nur Drehbuch |
| C19 | Wer spricht mit mir? | N13 | tiefere Echo-Ebene | A (geschützt) | nur Drehbuch |
| C20 | Die Schöpfer | N14 | Netzwerk → C00-Schlafzimmer → Weltenkern | A/C (geschützt) | nur Drehbuch |
| C21 | Der erste Morgen | N15 | neue Schöpfungswelt | D | nur Drehbuch |

0 von 22 Szenen existieren in Unreal. 0 von 113 Shots sind in der Engine getestet.

## 3. Vorhandene Assets und Funktionen (belegt)

| Bereich | Vorhanden | Beleg |
|---|---|---|
| Unreal-Projekt | ja, UE 5.8.3, kompiliert, Editor startet headless | `STAND.md` WK-M01-010 |
| Speichern Soul/World/Life | ja, transaktional, 6/6 Tests + 15/15 Absturztests | `docs/evidence/WK-M02-001` |
| Spielfigur, Steuerung, Kamera | **nein** | – |
| Level / Welt | **nein** | – |
| NPC-KI, Missionen, Dialoge, UI, Audio, Cinematics | **nein** | – |
| 3D-Geometrie | 38 GLB-Proxies (4–124 KB, Graybox), 1 Duplikat (`BRUECKE_004 = _005`) | V62-Register |
| Referenzbilder | 38 Graybox-Drehansichten, 1 NPC-Konzeptbild, 5 Dateien im GAMEFORGE-Ordner | nicht freigegeben |
| Blender-Master, Rigs, Animationen | **keine** | 40/40 Animationen `NOT_CREATED` |
| Lokale Werkzeuge | UE 5.8.3, Blender 5.2 (MCP verbunden), VS 2026 C++, Git LFS, RTX 5070 | Inventur M00 |
| Unreal-MCP | Plugin aktiv im Projekt, Verbindung nur bei offenem Editor | Log SmokeTest |

## 4. Lückenanalyse zu den bestätigten Verbesserungen

| Nr. | Verbesserung | Vorhanden | Lücke (Kern) |
|---|---|---|---|
| 1, 17 | Weltkonsequenzen / Destiny & Consequence | Datenfelder EventFlags, Relationships, Memories im Save | Kausalgraph (`CausalEventID`), NPC-Gedächtnis, verdecktes mehrdimensionales Profil, Konsequenzmatrix, Widerspruchsprüfung |
| 2, 15 | Charakterbewegung / Motion | – | Skelett-Vertrag, Motion Matching, IK/Fußplatzierung, Mimik, Altersprofile (Säugling bis Greis) |
| 3 | Missions-/Ereignissystem | 43 Missionsanker (Text) | Questgraph, Trigger-/Deadlock-Prüfung, Szenen-Statemachine `Eligible → … → HandedBack` |
| 4, 24 | Character Studio / Asset DNA Vault | feste ID-Felder im Save (`BodyAssetId`) | Asset-Register mit IDs, Proportionsverträgen, Freigabestatus, Rechten |
| 5, 16, 23 | Welt / Streaming / Prozedural | – | World Partition, PCG, Flussdorf-Region, Wetter/Tageszeit |
| 6 | Cinematics | 22 Drehbuchszenen | Sequencer-Pipeline, Szenenvertrag, Skip/Commit-Regeln, Replay-Rezepte |
| 7, 22 | Gameplay / Kamera | – | Enhanced-Input-Steuerung (Maus/Tastatur/Controller), Kameraprofile je Lebensphase, Mikrowelt-Steuerung |
| 8 | Living Intelligence (NPC) | StateTree-Plugin aktiv | Bedürfnisse, Tagesabläufe, Persönlichkeit, persistente NPC-Zustände, lokal ohne externe KI-API |
| 9 | Sound/Voice/Music | Cue-Sheet im Drehbuch | MetaSounds, zwei Motive (Lebens-/Soul-Motiv), deutsche Aufnahmen, Lip-Sync, Rechte |
| 10, 26 | Production Brain / Token | GAMEFORGE-Plugin, `STAND.md`, Evidenzordner | Asset-Register, automatischer Projektscanner, Build-/Test-Skripte |
| 11 | Player Experience / UI | – | Hauptmenü, HUD ohne Karma-Zahlen, Speichern/Checkpoints, Fotomodus, Optionen |
| 12, 25 | QA / Playtest | 6 Automation-Tests + Absturztest | Gameplay-/UI-/KI-Tests, Playtest-Protokoll, menschliche Tester |
| 13 | Physik | Chaos (Engine-Standard) | Interaktionsobjekte, Wasser, Wind, Vegetation |
| 14 | Visual Fidelity | Lumen/HW-RT/VSM/Nanite konfiguriert | alle Assets, Materialien, Licht-Setups |
| 19 | Release | – | Packaging, Installer, Fehlerprotokoll (erst am Ende) |
| 20 | Vertical Slice | Register VS01 (196 Positionen) | alles Gebaute |
| 21 | Epochen | – | Epochenumfang **nicht entschieden** (2026 ist Primärwelt) |

Nicht anwendbar oder nicht vorgesehen: Kampf-/Gegner-KI und „Kreaturen“ im Fantasy-Sinn. Das Drehbuch sieht kein Kampfsystem vor. „Intelligente Gegnerreaktionen“ (8) und „Kreaturen“ (4) werden nur umgesetzt, wenn die Spielbibel sie belegt (z. B. Tiere, Lebewesen in C21).

## 5. Technisches Zielbild

Modul `Genesis` (C++), datengetrieben, Aussehen streng von Logik getrennt:

- **Kern:** `UGenesisGameInstance` mit Subsystemen: Save (vorhanden), LifeCycle (Lebensphasen, Alterung), WorldClock (Zeit, Jahreszeiten), Causality (Ereignisse, Konsequenzen), Scene (Cinematic-Vertrag nach ScriptLock IV-B), Echo/Rebirth.
- **Figuren:** `AGenesisCharacter` kennt nur eine `CharacterAssetId`. Ein `UGenesisCharacterAppearanceRegistry` (DataAsset) löst ID → Mesh, Skelett, AnimBP, Materialien, Physics Asset, Sockets, Kameraanker auf. Ein Modellwechsel ändert nur diesen Eintrag. Pro Hauptfigur gibt es einen **Proportions-/Kameravertrag** (Größe, Augenhöhe, Socket-Positionen, Toleranzen), den ein automatischer Test vor dem Austausch prüft.
- **Skelette:** ein Erwachsenen-Referenzskelett (UE-Mannequin-kompatibel für Retargeting), dazu eigene Profile für Säugling/Kind/Greis mit IK-Retargeter.
- **NPC:** StateTree + Smart Objects, Tagespläne als Daten, Gedächtnis als Einträge im Kausalgraph.
- **Welt:** World Partition, PCG für Vegetation/Streuobjekte, gespeicherter Level ohne Wegstreamen für MCP-Bauarbeit.
- **Cinematics:** Level Sequencer, Szenenaufruf nur über validierten Vertrag. Skip bedeutet `CommitPending`, nie „Zustand unverändert“.
- **Pipeline:** Blender (Master .blend) → FBX/glTF-Export per Skript → UE-Import per Skript → automatischer Asset-Test (Maße, Pivot, Materialslots, LOD, Kollision, Skelett-Kompatibilität).

## 6. Asset-Such- und Wiederverwendungsstrategie

Reihenfolge je Bedarf: Projektbestand → Engine-Inhalte (UE-Mannequin, Templates) → **Poly Haven** (CC0: HDRIs, Texturen, Modelle) → **Fab** (nur Einträge, die kostenlos sind und deren Lizenz kommerzielle Spiele erlaubt; Quixel-Megascans-Inhalte) → **BlenderKit** (nur „Royalty Free“ markierte, kostenlose Assets) → **MetaHuman** als möglicher Ausgangspunkt für Menschen (Lizenz vor Nutzung prüfen) → Eigenmodellierung in Blender.

Je externes Asset wird ein Eintrag im Asset DNA Vault (`docs/asset-vault/`, CSV + Lizenznachweis) angelegt: Quelle, Originalname, Urheber, Lizenz mit Link/Screenshot, Format, Änderungen, Blender-Datei, UE-Pfad, Freigabestatus. Einzigartige Figuren (alter Mann, Tochter, Spielfigur-Varianten) werden nie 1:1 aus Bibliotheken übernommen. Keine Downloads ohne Einzelfreigabe. Keine kostenpflichtigen Assets.

## 7. Vorgeschlagener Vertical Slice (zur Entscheidung)

**VS-A „Flussdorf, Erwachsenenleben 2026“ (Gameplay):** eine Region aus dem VS01-Register (Ortsmitte, Markt, Werkstatt, Brücke, Wetterstation). Inhalt: eine Spielfigur (Erwachsener), 3–4 NPCs mit Tagesablauf, eine Mission aus den Ankern mit Entscheidung und sichtbarer Konsequenz (Kandidat L08 „Die Nacht der Naturgewalt“, Sturm passt zu Wetterstation und Brücke), Save/Load, Menü, Tag/Nacht/Wetter. Die Missionsdetails müssen aus den Originalquellen kommen und werden nicht erfunden.

**VS-B „C00 Der letzte Augenblick“ (Cinematic):** ein Innenraum, zwei Figuren, fester Film. Er testet Gesicht, Hände, Licht, Sequencer, deutsche Stimme und das spätere C20-Replay. Voraussetzung: ScriptLock-Endfreigabe für C00.

Empfehlung: zuerst VS-A mit austauschbaren Basismodellen (UE-Mannequin), parallel dazu als erstes Blender-Master eine Flussdorf-Umgebungseinheit (Werkstatt). VS-B folgt, sobald C00 freigegeben ist.

## 8. Priorisierter Produktionsplan

| Prio | WorkID | Inhalt | Abnahme |
|---|---|---|---|
| 1 | WK-M02-002 | Spielfigur + Enhanced Input (Maus/Tastatur/Controller) + Third-Person-Kamera mit Kollision; Testlevel | Figur steuerbar, Controller getestet, PIE-Automation-Test |
| 2 | WK-M02-003 | Character-Austauschschnittstelle: AssetId → Appearance-Registry, Proportions-/Kameravertrag, Austauschtest | Zwei verschiedene Meshes per ID tauschbar ohne Codeänderung, Test grün |
| 3 | WK-M02-004 | WorldClock + LifeCycle (Alterung, Jahreszeiten) an Save angebunden | Zeit läuft, Save/Load stellt Zeit/Alter exakt her |
| 4 | WK-M03-001 | Kausalgraph + NPC-Gedächtnis (Verbesserung 1/17) | Ereignis → NPC-Reaktion nach Laden noch vorhanden |
| 5 | WK-M03-002 | NPC-Tagesablauf mit StateTree + Smart Objects | 3 NPCs folgen 24-h-Plan, Test |
| 6 | WK-M03-003 | Mission/Questgraph + Dialog mit Entscheidung + Deadlock-Prüfung | Mission durchspielbar, alle Zweige automatisch geprüft |
| 7 | WK-M03-004 | Menü, HUD (ohne Karma-Zahlen), Save-Slots, Optionen | UI-Test |
| 8 | WK-M04-001 | Asset DNA Vault + Blender→UE-Importskript + automatischer Asset-Test | 1 GLB-Proxy durchläuft die Pipeline nachweisbar |
| 9 | WK-M04-002 | Erstes Blender-Master (Werkstatt) nach Realismus-Standard | Reality Check + UE-Import + Austausch des Proxys |
| 10 | WK-M05-001 | Flussdorf-Region zusammenbauen (VS-A), Performance-Messung | Standalone-Testbuild, FPS-Bericht |

## 9. Erste Agentenaufträge (GAMEFORGE)

Nur benötigte Spezialisten, nie zwei gleichzeitig im selben Editor:

1. `gameforge:unreal-programming` → WK-M02-002 und WK-M02-003 (C++, kein Editor nötig bis zum Test).
2. `gameforge:mission-quest` → L08 und die Flussdorf-Anker aus den Originalquellen der V61-Kette extrahieren (nur lesen, nichts erfinden), Ergebnis als Missionsdatensatz.
3. `gameforge:world-building` → VS01-Regionsplan R01–R08 aus Register in Level-Layout (Maße, Wege, Sichtachsen) übersetzen.
4. `gameforge:blender-3d` → Werkstatt-Master (nach Freigabe von WK-M04-002).
5. `gameforge:quality-testing` → Testkatalog für VS-A aus ScriptLock IV-C und Register.

## 10. Risiken, Abhängigkeiten und benötigte Freigaben

| Thema | Risiko | Benötigt |
|---|---|---|
| ScriptLock 1.1 nicht endfreigegeben | Kanon kann sich noch ändern | dein „JA zu Vorschlag 11“ (oder Änderungen) |
| C15/C16 (CON33-01) | Drehbuch nennt „Bibliothek“ und „räumliche Architekturen“, die Vorgabe verbietet begehbare Bibliotheken/Architektur im Echo. Betrifft auch C17/C19 („Bibliothek“) | kreative Entscheidung von dir, Drehbuch bleibt bis dahin unverändert |
| Altes Repo nicht erreichbar | ScriptLock verweist auf `Docs/*.md` und einen 121,5-s-Vorfilm des alten Repos, die hier fehlen | ggf. Zugang oder Bestätigung, dass sie entfallen |
| Epochenumfang | ohne Entscheidung keine Epochen-Assets | Entscheidung, welche Epochen spielbar sind |
| Missionsdetails J00–J24 | Titel laut Register „aus Quellenpaket übernehmen“, V61-Kette nicht vollständig ausgewertet | Auswertung der eingebetteten Quell-ZIPs (lesen) |
| Rechte | KI-Bilder, Stimmen, Musik, Fremd-Assets ohne Nachweis | Rechteregister; Sprecher/Musik extern |
| Deutsche Sprachausgabe | echte Schauspielaufnahmen nötig (TTS reicht laut Abnahme nicht) | Budget-/Vorgehensentscheidung |
| Menschliche Playtests | nicht durch Claude ersetzbar | Testpersonen |
| Hardware | 1 Rechner; Editor und Blender teilen GPU | sequentielle Produktion |
| Umfang | AAA-Gesamtspiel ist sehr groß; kein realistischer Fertigtermin ableitbar | schrittweise Abnahme je WorkID |
