# G6 – NPC / Welt / Mission (Flussdorf, Werkstatt-Kette) · Status: ENGINE_TESTED · Menschentest offen

Datum: 2026-10-24 · Zweig `v4/neustart` · Level `/Game/Genesis/Flussdorf/Maps/L_Flussdorf_G6` · Plan: `docs/design/G6_FLUSSDORF_WERKSTATT.md`

Quellen: Arbeitskanon (Kandidat, nicht endfreigegeben, G1) – `WELTBIBEL_FLUSSDORF`, `V24_NPC_UND_EREIGNISSIMULATION`, `V48_KANON_NPCS_UND_ORTSBINDUNG`, `V24_MISSIONSBIBEL`. Was die Quellen offen lassen, ist als **Startwert** markiert. **Alle Dialogsätze sind Startwerte** (`DRAFT_NEEDS_APPROVAL`): Die Quellen enthalten keine Dialogtexte.

## Gate-Kriterien

| Kriterium (Gate G6) | Umsetzung | Beleg |
|---|---|---|
| 3 Rollen | N01 Werkstattbesitzer/in, N02 Reparaturkund/in, N03 Marktbetreiber/in – Ziele, Grenzen, Orte laut Quelle | `GenesisNpcSchedule.cpp`, `GenesisWorkshopContract.cpp` |
| Tagesplan | N01 09–17 R03, N02 vormittags R02 (Startwert 08:30–12:00), N03 08–18 R02; sonst zu Hause in R07 (privat, nicht betretbar). Wege zu Fuß über das Navigationsnetz, kein Teleport | `Genesis.Flussdorf.DailySchedule` **bestanden** (4 Prüfzeiten, 34–48 s Fußwege) |
| Dialog mit Konsequenz | Werkstatt-Kette (Kette A / S24-02): Annehmen / zu teuer / Verweis an N01 / Ablehnen / Zurückgeben; Folgen in Weltzustand und Protokoll; N02 kommt zur Abnahme selbst in die Werkstatt; N01 übernimmt beim Verweis; Rückzug am Ende von Tag 2 | `Genesis.Flussdorf.Contract.*` **4/4**, `Genesis.Flussdorf.MissionPlaythrough` **bestanden** |
| Save/Load | Transaktional (Temp → prüfen → Austausch, SHA-1, Sicherungskopie, beschädigte Datei nie über guter Sicherung), F5 / F9 im Spiel, nach dem Laden stehen die Bewohner dort, wo die geladene Zeit sie vorsieht | `Genesis.Save.RoundtripAndRecovery`, `Contract.SaveLoadEveryStep`, Speichern/Laden mitten im PIE-Durchlauf |
| Keine Softlocks | Vollständige Suche über alle Handlungen und Warten (3 Tage): **2 580 Zustände, keiner ohne Weg zu einem Ende**, nie doppelt bezahlt, nie über 82 GE | `Genesis.Flussdorf.Contract.NoSoftlockExhaustive` |
| Gültige Quelle | G1-Arbeitskanon, Hashes in `docs/v4/CANON_SOURCE_REGISTER.json` | G1-Bericht |

## Durchspielt im echten Spiel (sichtbarer Editor) – `docs/evidence/G6/wp66_mission_playthrough_log.txt`

08:30 N02 bietet an → angenommen (60 GE, Teil reserviert) → 09:05 Werkstatt öffnet, N01 geht hin (48 s) → Werkzeug geliehen → Startversuch / Filter ok / Zündkerze verrußt → Zündkerze bei N03 gekauft (18 GE) → **Speichern + Laden** (verfälschter Geldwert wird korrekt zurückgesetzt) → Reparatur, Werkzeug zurück → „läuft wieder“ → **N02 geht selbst in die Werkstatt (16 s), prüft und zahlt** → 82 GE, **genau 1 Zahlung**, 13 Protokolleinträge.

## Bausteine

| Baustein | Datei |
|---|---|
| Weltzustand, Uhr, Ereignisprotokoll (V24-Datenvertrag, Idempotenz), NPC-Wissen beobachtet/gehört/geprüft | `World/GenesisWorldStateSubsystem` |
| Spielstand | `Save/GenesisSaveStore` |
| Bewohner, Tagesplan, Wahrnehmung (Reichweite + Sichtlinie) | `Npc/GenesisNpc`, `GenesisNpcController`, `GenesisNpcSchedule` |
| Werkstatt-Kette | `Mission/GenesisWorkshopContract` |
| Dorf-Regie (wer steht wo, Termine, Fortschritt ohne Spieler) | `World/GenesisFlussdorfDirector` |
| Spielerseite: Ansprechen, Gespräch, Speichern/Laden | `Player/GenesisPlayerController`, `UI/GenesisHudWidget` |
| Level-Skripte | `tools/v4/g6/` (Graybox, Bewohner, Interaktion, Wegeprüfung) |

## Steuerung zum Selbsttesten

Im Editor `L_Flussdorf_G6` öffnen → **Play** (Alt+P). **E** (Controller X) ansprechen / untersuchen / Gespräch beenden · **1–6** oder **Pfeiltasten / Steuerkreuz + Enter / A** antworten · **F5** speichern · **F9** laden · Uhrzeit und Geld oben links, offene Aufgabe oben rechts. Uhr: 1 Echtminute = 10 Spielminuten; N01 öffnet die Werkstatt um 09:00 (≈ 3 Echtminuten nach dem Start).

## Nicht geprüft / offen

- **Menschentest (Pflicht für G6).**
- Graybox, Mannequin-Platzhalter, keine Gesichter, keine Stimmen, kein Ton – Optik und Akustik sind G7.
- Dialogsätze und alle Startwerte brauchen deine Freigabe (oder Ersatz aus einer freigegebenen Quelle).
- Ketten B/C (Brücke, Unwetter), R04–R06, R08 sind nicht Teil von G6.
- Die HUD-Anzeige ist auf den automatischen Bildschirmfotos nicht mit drauf (Aufnahme ohne Oberfläche).
