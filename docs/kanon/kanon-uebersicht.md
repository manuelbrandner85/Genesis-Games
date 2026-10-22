# GENESIS – Kanon-Übersicht (aus Release `handover-v62`)

Quelle: GitHub-Release `handover-v62` von `manuelbrandner85/Genesis-Games`, Asset `GENESIS_V62.zip`, entpackt nach `/workspace/genesis/handover-v62/`.
Das verschachtelte Quellpaket (V61 → V60 → V59 → ältere ZIPs) wurde nur zum Lesen nach `/workspace/genesis/quellen-lesen/` entpackt.
Im Repo wurde nichts geändert. Am ScriptLock-Text wurde nichts geändert.
Abkürzungen: `HO` = `handover-v62/GENESIS_V62_KOMPLETTUEBERGABE_CLAUDE_CODE/`, `QL` = `quellen-lesen/GENESIS_V61_VOLLSPIEL_ASSET_UND_SZENE_STUECKLISTE/00_QUELLEN_UNVERAENDERT/`.

---

## 1. Kapitelliste ScriptLock C00–C21

Quelle: `HO/04_PRODUKTIONSREGISTER/SCRIPTLOCK_ORIGINAL_UNVERAENDERT.md` (ScriptLock-Kandidat 1.1, Stand 15.10.2026).
**Gesamtstatus:** „Script-Lock-Kandidat 1.1, die endgültige Entscheidung des Game Directors steht noch aus“. Alle 113 Shots in `CINEMATIC_SHOTS.csv` haben den Status `SCRIPT_ONLY_NOT_ENGINE_TESTED`.

| ID | Titel | Phase | Shots | Status |
|---|---|---|---|---|
| C00 | DER LETZTE AUGENBLICK | N00 | 5 | Nur als Skript, nicht in der Engine getestet |
| C01 | EIN WINZIGER ANFANG | N00 | 4 | Nur als Skript |
| C02 | ZWEI WERDEN EINS | N01 | 5 | Nur als Skript |
| C03 | ICH HÖRE DICH | N03 | 5 | Nur als Skript |
| C04 | DER ERSTE ATEMZUG | N04 | 5 | Nur als Skript |
| C05 | DER ERSTE SCHRITT | N05 | 5 | Nur als Skript |
| C06 | DER FREIE PLATZ | N05 | 5 | Nur als Skript |
| C07 | DER LETZTE SOMMER | N06 | 5 | Nur als Skript |
| C08 | DAS VERSPRECHEN | N06 | 5 | Nur als Skript |
| C09 | DIE TÜR | N07 | 5 | Nur als Skript |
| C10 | ZWISCHEN UNS | N07 | 5 | Nur als Skript |
| C11 | DIE NACHRICHT | N07 | 5 | Nur als Skript |
| C12 | DER TISCH DER JAHRE | N07 | 5 | Nur als Skript |
| C13 | DER ORT VON DAMALS | N08 | 5 | Nur als Skript |
| C14 | WAS BLEIBT? | N08 | 5 | Nur als Skript |
| C15 | KEIN KÖRPER MEHR | N09 | 5 | Nur als Skript, CON33-01 entschieden (23.10.2026) |
| C16 | DIE ANDERE SEITE | N09 | 5 | Nur als Skript, CON33-01 entschieden (23.10.2026) |
| C17 | EIN NEUER HERZSCHLAG | N12 | 5 | Nur als Skript |
| C18 | DIE VERTRAUTE FREMDE | N12 | 5 | Nur als Skript |
| C19 | WER SPRICHT MIT MIR? | N13 | 6 | Nur als Skript; Spoiler-Schutz, Inhalt wird hier nicht zusammengefasst |
| C20 | DIE SCHÖPFER | N14 | 7 | Nur als Skript; Spoiler-Schutz, Inhalt wird hier nicht zusammengefasst |
| C21 | DER ERSTE MORGEN | N15 | 6 | Nur als Skript |

Die Phasen N02, N10, N11 und N16 haben keine eigene C-Szene (siehe `17_SPIELPHASEN_STATUS.csv`). Laut Register ist keine der 17 Phasen „ReadyForAAAProduction“.

---

## 2. Regeln für die Welt 2026
Quellen: `HO/01_CLAUDE_START/MASTERPROMPT_CLAUDE_CODE.md`, `QL/01_Weltbibel_Flussdorf.md`, ScriptLock I.1/I.7.
- Die Startepoche ist die **Gegenwart 2026**. Der Prolog C00 spielt 2026, und erst danach beginnt die Spermienreise. Die erste spielbare Befruchtung findet zeitlich **nach** dem Tod in C00 statt.
- Weitere historische oder zukünftige Epochen gibt es erst, wenn die Welt und ihre Zugänglichkeit freigegeben sind. Bis dahin werden keine Architekturen, Waffen oder Fahrzeuge für unbekannte Epochen erzeugt.
- Verboten sind: Elemente aus AION, Götter, erfundene Fantasy-Kreaturen, Portale und mittelalterliche Werkstätten in der Gegenwartswelt.
- Körper, Schwangerschaft, Geburt, Altern und Tod werden wissenschaftlich plausibel gezeigt. SoulSeed, Echo, Bibliothek und Weltschöpfung sind klar als Fiktion gekennzeichnet.
- Es gibt keine feste Biografie. Es gibt kein Karma und keine Strafe (Krankheit oder Armut sind keine Folge von Karma). Der Tod ist kein Game Over.
- Testwelt **Flussdorf (VS01)**: ein moderner Ort mit 8 Regionen (R01 Dorfplatz, R02 Markt, R03 Werkstatt, R04 Flussbrücke, R05 Uferweg, R06 Wetterstation, R07 Wohnhäuser, R08 Bushaltestelle). Die Spielfigur ist dort ein erwachsener Testcharakter und **nicht** die kanonische erste Inkarnation. In der Körperwelt gibt es keine Seelenmechanik.
- Folgen über Generationen (+1/+5/+30 Jahre) gibt es nur, wenn es eine belegte Ursache gibt. Es gibt keine erfundenen Nachfahren und keine Regel „wer Gutes tut, wird reich“.

## 3. Echo-Regeln
Quellen: Masterprompt, `P0_BLOCKER_LESEN.md`, `OFFENE_ENTSCHEIDUNGEN.md`, V20A/V30/V33/V35-QA-Register in QL.
- Das Echo besteht nur aus **Energie und Erinnerungen**. Es gibt keine begehbaren Tempel, Bibliotheksräume, Säulen, Böden, Treppen, Portale oder Türen (V20A). „Räume“ entstehen nur aus Lichtfäden. **Ausnahme (CON33-01, 23.10.2026):** In C15, C16, C17 und C19 sind Räume und eine Bibliothek erlaubt; Tempel und Säulen bleiben verboten. Siehe `docs/kanon/BESCHLUESSE.md`.
- Der Spieler hat im Echo keinen sichtbaren Körper. Die Seelenform ist ein Energiephänomen.
- Rückblicke brauchen eine echte `CausalEventID`. Wenn sie fehlt, wird eine subjektive Erinnerung gezeigt, die als solche erkennbar ist. Es gibt keine erfundenen Original-Tonspuren (C16).
- Es gibt keine Gut/Böse-Farben, keine „goldenen Räume“ für gute Spieler und keine Strafe.
- C15/C16 sind ein resumierbarer Checkpoint. Der atomare Life/World/Soul-Commit passiert erst beim Abschluss. Eine Wiedergeburt ist erst nach transaktionalem SaveBundle und Crashtests freigegeben.
- Nach dem Tod sind Wiedergeburt, Rückkehr zur Bibliothek oder Loslassen frei wählbar.

## 4. Berufe und NPCs N01–N08
Quellen: Masterprompt, `QL/03_NPC_und_Ereignissimulation.md`.
- **Berufsregeln:** R03 ist eine **Reparatur- und Generatorwerkstatt** und wird nicht zur Schreinerei umgebaut. Die Steinbrücke R04 wird von Infrastruktur- und Baufachleuten geprüft und repariert. Schreiner arbeiten nur an passenden Holzarbeiten. Unqualifizierte Hochrisiko-Reparaturen sind nie Pflicht.
- **N01 Werkstattbesitzer/in:** Arbeitet von 9 bis 17 Uhr in R03 und lehnt unsichere Reparaturen oder Arbeiten ohne Teile ab.
- **N02 Reparaturkunde/-kundin:** Will ein Gerät im Rahmen des Budgets reparieren lassen und kann den Kostenvoranschlag ablehnen.
- **N03 Marktbetreiber/in:** Versorgt den Markt (R02) und verkauft keine reservierten oder fehlenden Waren.
- **N04 Lieferperson:** Liefert von 10 bis 15 Uhr über R08 und fährt nie über eine gesperrte Brücke.
- **N05 Gemeindekoordinator/in:** Entscheidet am Dorfplatz über Sicherheit und gibt die Brücke nie ohne gültige Prüfung frei.
- **N06 Wetterbeobachter/in:** Misst an der Wetterstation R06 und gibt nur belegte Warnungen aus.
- **N07 Bewohner/in A:** Geht am Uferweg spazieren, schützt den eigenen Haushalt und kann eine Freundschaft selbst beenden.
- **N08 Bewohner/in B:** Arbeitet in R03, sagt bei Erschöpfung ab und ist keine Pflichtromanze.
- Alle NPCs wissen nur, was sie selbst wahrgenommen haben (Beobachtung, Hörensagen und Bericht werden getrennt). Sie dürfen Nein sagen. Gesichter und endgültige Masters sind noch nicht freigegeben, und die GLBs sind nur Graybox/Proxy.

## 5. Missionen (Kurzform)
Quellen: `HO/04_PRODUKTIONSREGISTER/43_MISSIONSANKER.csv`, `QL/GENESIS_V21_Missionen_und_Generationen_v1.json`, `QL/GENESIS_V24_Paket__02_Missionsbibel_und_Entscheidungen.md`.

**Lebensmissionen (V21):**
- L00 Die Welt erwartet dich (C02–C04, biologischer Beginn)
- L01 Der erste eigene Weg (C05)
- L02 Ein Platz für zwei (C06)
- L03 Der letzte freie Sommer (C07)
- L04 Das zerbrechliche Versprechen (C08)
- L05 Die eigene Tür (C09)
- L06 Etwas können (Lernen/Können)
- L07 Wo die Karte endet (Erkunden)
- L08 Die Nacht der Naturgewalt (helfen im Rahmen der eigenen Fähigkeiten)
- L09 Zwischen uns (C10, keine Romanzepflicht)
- L10 Die Nachricht (C11)
- L11 Was wir bauen (lokales Projekt)
- L12 Die verschwundene Wahrheit (recherchieren/melden)
- L13 Der Tisch der Jahre (C12)
- L14 Der Ort von damals (C13)
- L15 Was bleibt (C14, Lebensende)
- G01 Ein Ort, zwei Generationen (C17/C18)
- G02 Die Welt gehört niemandem (Weltentwicklung, indirekt)

**Echo-Missionen J00–J24** (N09–N11, Quellen V20B/V27–V30): **Die Titel fehlen.** Im Register steht nur „Originaltitel übernehmen; nicht erfinden“.

**Testwelt VS01 (V24), Missionsketten:**
- **A Werkstatt:** Generator diagnostizieren. Man kann selbst reparieren, eine Fachkraft holen oder ablehnen. Es gibt einmalig 60 GE, und ein Teil kostet 18 GE.
- **B Brücke:** Riss melden und Inspektion veranlassen. Die Gemeinde entscheidet. Bei Sperrung gibt es einen Umweg über R05.
- **C Unwetter:** Messung, Warnung, Sturm. Es gibt keine garantierte Rettung aller.

**Optionale Geschichten S24-01…08:**
- S24-01 Ersatzteile
- S24-02 Preis der Hilfe
- S24-03 Stimme am Markt
- S24-04 Riss am Geländer
- S24-05 Umweg
- S24-06 Warnung erreicht nicht alle
- S24-07 Strömung
- S24-08 Normaler Morgen?

Es gibt vier mögliche Endzustände (Brücke offen, Brücke gesperrt, niemand gewarnt, Werkstatt geschlossen).

## 6. Dialoge (Kurzform)
- Der ScriptLock-Text ist der kanonische Dialog. Vertont werden nur Varianten, die zum Kontext passen und auf wahren Fakten beruhen. `{{PLATZHALTER}}` müssen vor der Aufnahme grammatisch korrekt befüllt sein. `[REGIE]` wird nie gesprochen.
- Die gemeinsame Stimme ist anfangs eine einzige, ruhige Stimme. Ihre Natur wird vor C19 nicht verraten. Sie stellt eher Fragen, als Antworten zu geben.
- Embryo, Fötus und Neugeborenes haben keinen inneren Monolog. Kinder sprechen altersgerecht. Es gibt keine pathetische Dauererzählung.
- Die Anrede muss männlich, weiblich, neutral und formell korrekt gebeugt werden. TTS ohne Lippensynchronprüfung gilt nicht als Abnahme.
- VS01-Dialoge: Es gibt keinen Pflichtdialog. NPCs können ablehnen. Gerüchte (HeardClaims) bleiben getrennt von Fakten.

---

## 7. Offene Kreativfragen (mit Fundstelle)
1. **ENTSCHIEDEN am 23.10.2026, 01:51 Berlin (siehe `docs/kanon/BESCHLUESSE.md`): Räume und Bibliothek bleiben wie im ScriptLock, gilt auch für C17/C19.** Ursprüngliche Frage – **C15/C16 Architektur vs. reines Echo (CON33-01):** Der ScriptLock beschreibt Architektur bzw. eine Bibliothek, V20A verbietet das. Hier braucht es einen Beschluss des Creative Directors, ohne den ScriptLock still zu ändern. Fundstellen: `HO/04…/OFFENE_ENTSCHEIDUNGEN.md`, `HO/01…/P0_BLOCKER_LESEN.md`, Masterprompt („Echo“), `17_SPIELPHASEN_STATUS.csv` (N09). Betroffene Shots: 15-C, 15-E („ruhiger architektonischer Raum“), 16-A („Große Räume … räumliche Architekturen“).
2. **Endfreigabe ScriptLock 1.1:** Das ausdrückliche „JA zu Vorschlag 11“ fehlt noch. Fundstelle: ScriptLock Kopf und IV.D.
3. **Weitere Epochen:** Welche Epochen, welcher Umfang und welche Auslöser? Fundstellen: `OFFENE_ENTSCHEIDUNGEN.md`, `P0_BLOCKER_LESEN.md` („UNDECIDED“), ScriptLock I.7 (Zukunftszeit/Parallelwelt).
4. **Gesichter und endgültige Appearance der NPCs N01–N08 und der Figuren im Prolog:** Fundstelle: `OFFENE_ENTSCHEIDUNGEN.md`.
5. **Titel der Echo-Missionen J00–J24:** Sie fehlen und müssen aus der Originalquelle kommen. Fundstelle: `43_MISSIONSANKER.csv`.
6. **Freigabe der V21-Missionen:** Die JSON hat den Status `awaits_director_approval`. Fundstelle: `QL/GENESIS_V21_Missionen_und_Generationen_v1.json`.
7. **Sprache/Sprecher, Musik:** Fundstelle: `P0_BLOCKER_LESEN.md` („OPEN“).
8. **Nachweis C00/C20-Replay und C19-Spoiler-Guards:** Fundstelle: `OFFENE_ENTSCHEIDUNGEN.md`.
9. **Rechte** an KI-Bildern, Musik, Stimmen und Assets: Fundstelle: `OFFENE_ENTSCHEIDUNGEN.md`.

## 8. Gefundene Widersprüche
- **W1 (Kern, ENTSCHIEDEN mit CON33-01 am 23.10.2026 – Ausnahme gilt auch für C17/C19):** In C15/C16 stehen Architektur und Bibliothek (siehe oben), V20A und der Masterprompt verlangen dagegen reines Energie-Echo ohne Räume. **Auch C17** („kosmische Bibliothek“, Shot 17-A „Verlassen der Bibliothek“) **und C19** (Ortsangabe mit Bibliothek und Regalen) benutzen Bibliotheks- und Regal-Begriffe. CON33-01 nennt aber nur C15/C16. Aus Spoilergründen nicht weiter ausgeführt.
- **W2:** Laut ScriptLock I.7 „gehört ein SoulSeed zur **Fantasy**-/Science-Fiction-Kosmologie“, die Weltregeln sagen dagegen „keine Fantasy“. Wahrscheinlich ist das nur eine Wortwahl, sollte aber geklärt werden.
- **W3:** Der Masterprompt nennt den ScriptLock „verbindlich, wörtlich erhalten“. Das Dokument selbst nennt sich aber „Kandidat, Endfreigabe ausstehend“.
- **W4:** `43_MISSIONSANKER.csv` markiert L00–G02 als `APPROVED_V21`, die Quell-JSON sagt aber `awaits_director_approval`. J00–J24 sind „APPROVED_ECHO_MISSIONS“, haben aber keine Titel.
- **W5:** Die Geschichte S24-08 nennt das Ereignis `EV24_09`, der Ereigniskatalog reicht aber nur bis `EV24_08`.
- **W6:** Die Statusbegriffe sind uneinheitlich. V62 nutzt `FILE_CREATED/FILE_VALIDATED`, V61 nutzt `CREATED_FILE/VALIDATED_FILE`.
- **W7:** Repo-Name: Die Übergabe nennt `manuelbrandner85/GENESIS-GAME` (nur Lesezugriff), das Release liegt aber in `manuelbrandner85/Genesis-Games`.
- **W8 (klein):** Laut ScriptLock I.4 gibt es im Repo einen alten Vorfilm (121,5 s plus 52 s Fallback), den C00+C01 ersetzen sollen. Ob er schon ersetzt wurde, ist nicht belegt.

## 9. AION-/Fantasy-Reste
- In den gelesenen Kanon- und Registerdateien gibt es **keine direkten AION-Inhalte** (keine Daeva, Balaur, Götter, Magie, Schwerter usw.). „AION“ und „Götter“ kommen nur in Verbotsregeln und QA-Prüfungen vor.
- Wörter wie „Gott“ in C19/C20 werden nur verneint („nicht Gott“, kein „Gott-Akkord“).
- Die Asset-Liste VS01 (196 Positionen) ist durchweg modern: Generator, Multimeter, Bushaltestelle, Liefertransporter. Es gibt **keine Schreinerei und keine Schmiede**.
- Mögliche Reste bzw. Prüfpunkte:
  - Die Architektur- und Bibliotheksbilder in C15/C16/C17/C19 (siehe W1)
  - Das Wort „Fantasy“ in ScriptLock I.7 (W2)
  - Die „Kirchenglocke“ in R01 und die „Standlaterne“ in R02 sind modern vertretbar, sollten aber auf altertümliche Wirkung geprüft werden
  - Die Währung „GE“ ist nicht als echte Währung erklärt
