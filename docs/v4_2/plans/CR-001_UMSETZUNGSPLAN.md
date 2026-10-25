# CR-001 – Umsetzungsplan „Neuer Anfang“ (Lichtschlag, Pflicht-Schwimmphase)

**Grundlage:** ScriptLock 1.2 (GD-2026-10-25-01), Antrag [`CR-001`](../change_requests/CR-001_ANFANG_LICHT_SAMENZELLE.md)
**Status:** Phase 1 + 2 **freigegeben** (GD-2026-10-25-02) und umgesetzt, siehe „Umsetzung Phase 1 + 2“. Phase 3–5 warten auf Freigabe. Jede Phase endet mit Belegen (Build, Tests, Bilder/Video).
**Stand 2026-10-25:** Das Dokumentationsregister `docs/v4_2/SCENE_REGISTRY.json` ist an 1.2 gebunden. Geändert sind nur C01/C02 (neuer Inhalt) und der C00-Hash (eine Übergabezeile); C03–C21 haben unveränderte Hashes. Das **Laufzeitregister** (`Content/Genesis/Data/scene_registry.json`) bleibt auf 1.1, bis Phase 1 den C++-Code umstellt – der Code verlangt heute fest `ScriptVersion == 1.1`.

## Ist-Stand im Code (gelesen, nicht verändert)

| Bereich | Heute | Fundstelle |
|---|---|---|
| Startablauf | `BOOT → STORY_START (C00/C01) → TITLE_CARD → MAIN_MENU`; STORY_START wird übersprungen, solange C00/C01 nicht produziert sind | `MENU_FLOW.json`, `GenesisMenuWidget.cpp` |
| Lichtwarnung | Epilepsie-Hinweis beim Start vorhanden | `GenesisMenuWidget.cpp` |
| „Lichtblitze verringern“ | vorhanden, **Standard aus** | `GenesisUserSettings.h` (`bReduceFlashes`) |
| Szenen-Zustandsmaschine | Eligible → … → Playing → (AwaitingInteraction) → CommitPending → Committed → HandedBack; Überspringen nie am Commit vorbei | `GenesisCinematicSubsystem` |
| Skriptversion | fest `1.1` (Prüfung im Vertrag) | `GenesisCinematicSubsystem.cpp`, `GenesisSceneTypes.h` |
| Spielstand | Schema 2 (`SoulID`/`LifeID`/`WorldID`), Migration 1→2 vorhanden | `GenesisSaveStore.cpp` |
| Tests | 23 Automationstests, u. a. `Genesis.Cinematic.*`, `Genesis.Menu.FlowGraph`, `Genesis.Menu.PIERoute`, `Genesis.Save.RoundtripAndRecovery` | `Source/Genesis/Private/Tests` |

## Phase 1 – Technik: neuer Startablauf (Code, keine Kunst)

1. **Skriptversion 1.2** im C++ (Vertragsprüfung, Standardwert) und Laufzeitregister neu binden.
2. **Ablauf** `BOOT → STORY_START = C00 → C01 → C02 (Pflicht-Schwimmphase) → TITLE_CARD → MAIN_MENU`; „Neues Leben“ → Kapitelkarte „KAPITEL I – DER ANFANG“ → **C03**. `MENU_FLOW.json` und Menü-Widget anpassen.
3. **Welt/Leben vor C02 anlegen** (`WorldID`, `WorldTime` strikt nach dem C00-Todeszeitpunkt, neue `LifeID`, gleiche `SoulID`); Überspringen von C00 legt weiter den `PreIncarnation_SoulSeed` an.
4. **C02 mit Spielabschnitt:** die Zustandsmaschine bekommt einen Gameplay-Abschnitt mitten in einer Szene (Film → Spielphase → Film). Schwimmphase **nicht überspringbar, aber pausierbar**.
5. **Licht:** `bReduceFlashes` **Standard an**; der Lichtschlag (C01-A) ist ein eigener Effekt, der die Einstellung beachtet (Puls ↔ weiches Aufblenden 1,5 s). Höchstens ein Puls, kein großflächiges Rot.
6. **Spielstand Schema 3:** Fortschritt „STORY_START bis einschließlich C02“; `LifeID` vor C02. Migration 2→3; es gibt keine Spieler-Spielstände, Testspeicher werden neu erzeugt.
7. **Tests:** bestehende anpassen (`Genesis.Cinematic.Registry`/`Transitions`, `Genesis.Menu.FlowGraph`/`PIERoute`, `Genesis.Save.RoundtripAndRecovery`) und neu: `Genesis.Cinematic.StoryStartFlow` (Reihenfolge, Titel nach C02, Rückkehr), `Genesis.Save.Schema3Migration`, `Genesis.Accessibility.FlashDefault`, `Genesis.Cinematic.SwimSegmentNoSkip`.

**Belege:** C++-Build, alle Automationstests grün, PIE-Durchlauf des Ablaufs mit Platzhalter-Szenen (als `bTechnicalTest` markiert).

## Phase 2 – Schwimmphase als spielbarer Graubox-Prototyp

- Pawn „Samenzelle“ mit biologisch begrenzter Vortriebsmechanik (Geißelschlag, Trägheit, Strömungsfeld des Eileiters); Steuerung Gamepad + Tastatur.
- **Kein Game Over** (E2): Zeitfenster 60–120 s (E4), danach sanftes Führen zur Eizelle; wer nicht ankommt, sieht über die objektive Kamera eine andere Samenzelle verschmelzen. Hilfe-Option „automatisch schwimmen“.
- **Kein Wettrennen-Design:** keine Platzierung, kein Timer-UI, keine Siegesmeldung.
- **Belege:** PIE-Video, Controller- und Tastatur-Test, Test „120 s ohne Eingabe → Szene läuft weiter“, Framerate auf der RTX 5070.

## Umsetzung Phase 1 + 2 (2026-10-25)

| Bereich | Umsetzung | Fundstelle |
|---|---|---|
| Skriptversion | `UGenesisCinematicSubsystem::ScriptVersion = 1.2`; Register mit anderer Version wird abgelehnt, Verträge mit 1.1 ebenso; Laufzeitregister an 1.2 gebunden (identisch mit `SCENE_REGISTRY.json`) | `GenesisCinematicSubsystem.cpp`, `Content/Genesis/Data/scene_registry.json` |
| Zustandsmaschine | neuer Zustand `InGameplaySegment` (Playing ↔ Segment, Segment → Failed); Überspringen des Films landet im Segment, das Segment selbst ist nie überspringbar; nur C02 darf ein Segment haben | `GenesisSceneTypes.h` |
| Startablauf | `FGenesisStoryStart` im GameInstance: C00 (Überspringen nur nach zweitem Tastendruck, Seelen-Keim auch beim Überspringen) → C01 (Lichtschlag) → neue `LifeID` strikt nach dem Seelen-Keim → C02-A → Schwimmkarte → C02-C…F → Titel (E1). Alle Teile laufen als Szenenverträge (technische Tests, solange die Master fehlen) | `GenesisStoryStart.*`, `GenesisMenuWidget.cpp` |
| Menüfluss | 16 Knoten: neu `STORY_SWIM` (Spielphase, Pause möglich) und `CHAPTER_CARD`; „Neues Leben“ → Kapitelkarte „KAPITEL I – DER ANFANG“ → Spiel mit Seele und Leben aus dem Startablauf | `MENU_FLOW.json`, `menu_flow.json` |
| Lichtschlag | `FGenesisLightStrike`: Lichtpunkt → ein Schlag → Weiß → Aufblenden; mit „Lichtblitze verringern“ (jetzt Standard **an**, ältere ini einmalig umgestellt) nur weiches Aufblenden über 1,5 s; warmes Weiß, kein Rot | `GenesisLightStrike.h`, `GenesisUserSettings.*` |
| Spielstand | Schema 3: `StoryStartStage`, `SoulSeedMinute`, `LifeStartMinute`, `ConceptionMode` (Own/Other), `StoryStartCommits`; Migration 2→3 markiert alte Leben als „Done/Migrated“ | `GenesisWorldTypes.h`, `GenesisSaveStore.cpp` |
| Schwimmphase (Graubox) | Karte `L_C02_Swim`, `AGenesisSwimGameMode`: Maßstab 1 uu = 1 µm; Eileiter als analytischer Schlauch mit Strömung zum Uterus; Samenzelle mit Geißelschlag, ohne Nachgleiten (niedrige Reynolds-Zahl), Rheotaxis; Eizelle 120 µm mit Cumuluszellen; 40 andere Samenzellen ohne Rangliste; ab 120 s sanfte Führung, ab 165 s objektive Kamera mit fremder Verschmelzung (kein Game Over); Hilfe „Automatisch schwimmen“; Pause mit Einstellungen/Barrierefreiheit, kein Speichern | `Swim/*`, `tools/v4_2/cr001_swim_map.py` |
| Zeiten (Nachrechnung) | ohne Eingabe ≈ 95 s, automatisch ≈ 71 s, schnellstmöglich ≈ 61 s – alle im Fenster 60–120 s (E4) | Test `Genesis.Swim.Course` |

**Belege (2026-10-25, `docs/evidence/CR001/`):** Editor-Build Win64 Development erfolgreich; Automationslauf **33/33 grün** (`regression_cr001.txt`), darunter neu `Genesis.Cinematic.StoryStartFlow`, `Genesis.Cinematic.SwimSegmentNoSkip`, `Genesis.Save.Schema3Migration`, `Genesis.Accessibility.FlashDefault`, `Genesis.Swim.Course`, `Genesis.Swim.ControlsPIE` (Tastatur + Gamepad-Stick über die Eingabe-Pipeline, Totzone gegen Drift, Pause, „Automatisch schwimmen“) und `Genesis.Swim.NoInputPIE` (ohne jede Eingabe: Ankunft nach 94,6 s, PIE-Bildrate Ø 118 fps im Editor) sowie die angepasste PIE-Route BOOT → C00 → C01 → C02 → Schwimmkarte → C02 → Titel → Menü → Neues Leben → Kapitelkarte → Spiel mit Seele/Leben aus dem Startablauf.
**Nicht belegt:** Führung ab 120 s und die objektive Kamera (fremde Verschmelzung) laufen nur, wenn man absichtlich falsch steuert – im Test ohne Eingabe kam die Zelle schon nach 94,6 s an; beide Wege sind im Code, aber ohne eigenen PIE-Nachweis. Kein Windows-Build, kein echter Controller-Handtest.

**Technische Entscheidung (änderbar durch dich):** Der Startablauf läuft beim ersten Start (noch kein gültiger Spielstand). Wer schon Spielstände hat, kommt direkt zum Titel; „Neues Leben“ spielt dann C00–C02 und endet mit der Kapitelkarte statt dem Titel.

**Grenzen:** C00/C02 sind Platzhalter-Tafeln (nur IDs), bis die Filme produziert sind (Phase 4). Die Graubox hat keinen Look (Phase 3). Bildrate nur im Editor-PIE gemessen, nicht im Windows-Build.

## Phase 3 – Look der Mikrowelt (Abnahme durch dich)

1. **Referenzbilder** (lokal, ComfyUI + FLUX.2 klein, freigegeben): Eileiter-Schleimhautfalten, Cumulus-Oozyten-Komplex, Zona pellucida, Spermien, Zygote/2-Zell-Stadium – an mikroskopischen Vorlagen orientiert, maßstäblich. → **Abnahme der Bildsprache.**
2. **Assets in Blender** (eigene Modelle, keine Fremdassets): Eileiter-Kulisse (Faltenrelief), Eizelle mit Zona pellucida und Zellkranz, Spermien mit animierter Geißel (LOD für viele Instanzen), Vorkerne, Zellteilung.
3. **Unreal:** durchscheinende/subsurface Materialien, Flüssigkeit und Schwebeteilchen (Niagara), Licht ohne „Fantasy-Glitzern“, Maßstabs-Einblendung.
4. **Belege:** Renders je Asset, Reality Check nach Skill „maximum-realism“, Abnahme durch dich.

## Phase 4 – Filmteile C01 und C02

- **C01** (≈ 6 s): Lichtpunkt → Lichtschlag → Weiß → Gewebe; Variante mit „Lichtblitze verringern“.
- **C02-A** (≈ 12 s), **02-C bis 02-E** (Verschmelzung, Vorkerne, erste Teilung mit korrektem Zeitsprung), **02-F Titel**.
- Sequencer + Movie Render Queue; Ton: Mikrowelt-Atmosphäre, Cue `M02_BEGINNING`, Chor erst beim Titel; keine Stimme. Musik-Entwurf mit ACE-Step (lokal) nur als TEMP bis zur Musikabnahme.
- **Belege:** Render-Master, Lautheits- und Bildprüfung, Abnahme durch dich.

## Phase 5 – Integration und Abnahme

- Kompletter Durchlauf BOOT → C00 → C01 → C02 → Titel → Menü → „Neues Leben“ → C03-Einstieg im Editor **und** im Windows-Build.
- Prüfung: Lichtwarnung, beide Lichtschlag-Varianten, Pause in der Schwimmphase, Speichern/Laden davor und danach, Canon-Hashes unverändert.
- **Status erst dann `ENGINE_TESTED`**; `ACCEPTED` nur durch dich.

## Abhängigkeiten und ehrliche Grenzen

- **C00 als fertiger Film fehlt noch** (Set und Figuren stehen, Szene/Ton/Stimmen nicht). Bis dahin läuft STORY_START mit C00 als technischem Platzhalter.
- Mikroskopisch glaubwürdige Biologie in Echtzeit ist anspruchsvoll; Qualität wird an Renders belegt, nicht versprochen.
- Keine Downloads und keine Cloud nötig; alle Werkzeuge sind installiert und getestet.

## Freigabe

Vorschlag: **Phase 1 + 2 jetzt** (reine Technik und Graubox, keine Kanon- oder Kunstentscheidung). Phase 3–5 einzeln nach Vorlage der Ergebnisse.
