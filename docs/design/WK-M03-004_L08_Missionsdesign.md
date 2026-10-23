# WK-M03-004 – L08 „Die Nacht der Naturgewalt“ im Flussdorf (Graybox)

Status der Quellen: „wartet auf Freigabe durch die Spielleitung“. Dieses Dokument setzt sie um und erfindet keinen Kanon.
Alles, was die Quellen offenlassen, steht unter **Ungeklärt** oder **Gestaltungs-Startwert** und ist im Code/Config genauso markiert.

## 1. Quellen (lokal, nicht im Repo)
| Kürzel | Datei | Verwendet für |
|---|---|---|
| V21-L08 | `GENESIS_V21_Menschliches_Leben_Missionsbibel_v1.md`, Abschnitt L08 | Auslöser, 5 Schritte, echte Wahl, Folge, Alternative |
| V24-MB | `GENESIS_V24_Paket/02_Missionsbibel_und_Entscheidungen.md` | Kette B (Brücke), Kette C (Unwetter), S24-04/05/06/07/08, Endlagen A–D |
| V24-WB | `GENESIS_V24_Paket/01_Weltbibel_Flussdorf.md` | Regionen R01–R08, Nachbarwege, Dauerzustände |
| V24-NPC | `GENESIS_V24_Paket/03_NPC_und_Ereignissimulation.md` | N01/N04/N05 Ziele, Grenzen, Wetterreaktion; EV24_03..09; Datenvertrag |
| V48-Kanon | `01_KANON_NPCS_UND_ORTSBINDUNG.md` | Basisorte und Grenzen N01/N04/N05; Brückenprüfer = nur künftige Rolle |

## 2. Was L08 laut Quelle ist
- **Auslöser:** dynamische, glaubwürdige lokale Gefahr (hier: Sturm mit Hochwasser – passt zu Kette C und R04/R05/R06).
- **Schritte:** 1. Frühwarnzeichen erkennen oder Alarmierung erleben · 2. Gefährdung und erlaubte Handlungen einschätzen · 3. warnen, helfen oder eigene Sicherheit · 4. Naturereignis mit Wetter- und NPC-Systemen durchspielen · 5. Folgen erleben.
- **Echte Wahl:** helfen innerhalb tatsächlicher Fähigkeiten; Hilfe anfordern; keine Heldentat erzwingen.
- **Folge:** Gebäude-/Straßenzustand, lokale Ressourcen, Langzeitfolgen.
- **Kein Zwang:** Die Mission ist ein Angebot; Welt, NPCs und Wetter laufen ohne Spieler weiter (V24-MB Kernprinzip, EV24_04 „auch ohne aktiven Spieler tritt Wetter ein“).

## 3. Umsetzung als Systeme (nicht als Skript)
| Baustein | Umsetzung | Quelle |
|---|---|---|
| Wetter | deterministisch aus `WorldSeed + Weltzeit` (Szenario + Seed-Streuung); Phasen Ruhe → Vorzeichen → Warnschwelle → Sturm → Abklingen → vorbei | EV24_04, EV24_07, „Ereignissimulation 1.“ |
| Wetterstation R06 | ablesbare Messwerte (Druck, Wind, Regen, Pegel); Station löst Alarm bei Schwelle aus | V24-WB R06, Kette C 1. |
| Öffentliche Warnung | nur N05 als berechtigte Stelle gibt sie aus, sobald sie die Messung kennt; Aushang R01 | EV24_05, V24-WB R01 |
| Warnung erreicht nicht alle | Wissen nur bei echter Zustellung: am Aushang gelesen oder persönlich gewarnt | S24-06, „MessageDelivered“ |
| Brücke VS01_BRIDGE_01 | Objektzustand mit Version und Ereignis-ID: Riss sichtbar, gemeldet, gesperrt, beschädigt, passierbar | Kette B, V24-WB R04, §6 |
| Sperrung | N05 sperrt bei Risikomeldung + Gefahrenlage; Sperre blockiert die Navigation, Umweg über R05 | EV24_06, Kette B 4. |
| Prüfung | Prüfauftrag wird gespeichert, aber es gibt noch keinen Prüfer (künftige Rolle) → Brücke bleibt nach Sperrung zu | V48-Kanon, EV24_09 „bis dahin Umweg“ |
| Werkstatt R03 | N01 sichert sie, wenn sie gewarnt ist; ungesichert führt Sturm zu Lagerschaden → keine Aufträge | N01 Wetterreaktion, Endlage D |
| Uferweg R05 | wird bei Hochwasser über Schwelle gesperrt und bleibt es (Uferzustand verändert) | S24-07, V24-WB R05 |
| Lieferperson N04 | fährt nie über gesperrte/unpassierbare Brücke; Umweg oder vertagen; vertagt, wenn sie vom Riss weiß | N04 Grenze, S24-05 |
| Schaden | nur aus Exposition, Pegel und Wind – nicht aus einer „richtigen“ Antwort | Kette C 4., Endlagen „gleicher Save/Seed → gleicher Zustand“ |

## 4. Questgraph L08 (Ziele für das HUD)
- **Start:** automatisch beim Wetterereignis „Vorzeichen“ (Auslöser `WX_PRECURSOR`), nicht beim Spielstart.
- **ANZEICHEN** – Wetter schlägt um; Messwerte prüfen oder Warnung abwarten.
  → Messwerte gelesen (`SIGNS_RECOGNIZED`) oder öffentliche Warnung (`WX_PUBLIC_WARNING`) → ENTSCHEIDEN; Sturm beginnt (`WX_STORM`) → UNWETTER.
- **ENTSCHEIDEN** – warnen (N01, N04), melden/Hilfe anfordern (N05), beim Sichern helfen (N01), Riss ansehen (Brücke), Schutz suchen – oder nichts. Keine Antwort beendet den Schritt; das Wetter tut es (`WX_STORM` → UNWETTER).
- **UNWETTER** – in Sicherheit bleiben; `WX_RECEDED` → MORGEN_DANACH.
- **MORGEN_DANACH** – Folgen ansehen (N05, N01). Gespräch mit N05 → Ausgang `FOLGEN_GESEHEN`; oder Zeit vergeht (`WX_AFTERMATH_OVER`) → Ausgang `WEITERGEZOGEN`.

Kein Ausgang ist „gut“ oder „schlecht“. Die Weltlage danach ergibt sich nur aus gespeicherten Zuständen.

## 5. Ungeklärt (bewusst nicht erfunden)
1. **N06 Wetterbeobachter/in** ist in diesem Arbeitspaket nicht dabei. Ersatz: Stationsalarm erreicht N05 nach einer festen Meldezeit (Gestaltungs-Startwert), schneller, wenn der Spieler die Werte überbringt.
2. **Brückenprüfer/in** ist laut Kanon nur eine künftige Rolle. Prüfaufträge werden gespeichert, aber nicht erledigt.
3. **Geografie:** die Topologie ist „kein geografischer Plan“. Graybox-Annahmen: Fluss trennt Dorf (R01/R02/R03/R07/R08) von R06; Umweg R05 führt am Ufer entlang zu einem Steg; N04 holt Ware am anderen Ufer.
4. **N05 Sprechstunden** („variieren“): Graybox-Testplan 08–18 Uhr am Dorfplatz.
5. **Geschlecht/Aussehen** von N01/N04/N05 („Werkstattbesitzer/in“ usw.) sind offen. Es werden die Proxy-Mannequins genutzt.
6. **Dialog-Wortlaut:** Die Quellen enthalten keine Dialogzeilen. Alle Zeilen sind **Arbeitstext**, nur aus Rollen/Grenzen abgeleitet, und im Asset als solcher markiert.
7. **Zeitpunkt und Stärke** des Sturms, alle Schwellen und Dauern sind **Gestaltungs-Startwerte** (Config `Genesis Weather` / `Genesis Flussdorf`).
8. **Wetter-Optik** (Regen, Wolken, Wind an Vegetation) ist nicht Teil dieses Pakets. Sichtbar sind Pegelstand, Sperren und Schäden.

## 6. Nicht enthalten
Kein Kampf, keine Rettung „aller“, keine Pflichtheldentat, keine C-Szene, keine C19/C20-Bezüge, keine Seelenmechanik.
