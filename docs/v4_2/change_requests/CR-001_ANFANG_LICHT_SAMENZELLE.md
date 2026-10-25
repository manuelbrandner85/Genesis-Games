# CR-001 – Anfang: greller Lichtschlag, danach direkt die Samenzelle (Pflicht-Schwimmphase)

| Feld | Wert |
|---|---|
| Antrag | CR-001 · Drehbuch ScriptLock 1.1 → **1.2** (nach Freigabe) |
| Gestellt von | Game Director, 2026-10-25: „Variante A: Der Prolog mit dem alten Mann bleibt. C01 beginnt mit einem kurzen grellen Licht, danach direkt die Samenzelle, und die Schwimmphase ist Pflicht statt optional.“ |
| Grundlage | ScriptLock 1.1, Abschnitt IV.D (Änderungen nur über versionierte Anträge mit Szenen, Dialog-IDs, Triggern, Musik, Save-Migration) · Sperre GD-2026-10-24-01 |
| Status | **FREIGEGEBEN** – GD-2026-10-25-01 („JA zu CR-001 mit den Vorschlägen E1 bis E4“). Fassung 1.2 vorbereitet, Ablage durch den Game Director ausstehend |
| Öffentliche Fassung | nur IDs und Auswirkungen. Der genaue neue Szenentext liegt lokal in `canon_proposals/CR-001/` (nicht im Repo). |

## 1. Was sich ändert

| Szene | heute (1.1) | neu (1.2) |
|---|---|---|
| **C00** Der letzte Augenblick | Prolog, endet in Schwarz mit einzelnem Lichtpunkt | **unverändert** (auch Länge, Dialog VO_C00_001–008, Soul-Intervall) |
| **C01** Ein winziger Anfang | 01-A ruhiger Lichtpunkt → Erde · 01-B Alltagsmontage + Erzählstimme · 01-C Gewebe → Eileiter · 01-D Titel | **01-A neu: kurzer greller Lichtschlag** aus dem Lichtpunkt (ein einziger Puls, ca. 1 s, kein Flackern, keine Explosion/Partikel) · **01-B und die Erzählstimme entfallen** · **01-C entfällt**: aus dem Weiß blendet das Bild direkt in den Eileiter · **01-D Titel wandert ans Ende von C02** |
| **C02** Zwei werden eins | 02-A Mikrowelt · 02-B **optionale** Schwimmphase · 02-C … 02-E | 02-A verkürzt (Einstieg aus dem Weiß) · **02-B Pflicht-Schwimmphase** · 02-C bis 02-E unverändert · danach **Titelkarte** (bisher 01-D) |
| C03 bis C21 | – | unverändert |
| C17 (Wiedergeburt) | optional spielbares Schwangerschaftskapitel | **unverändert optional** (siehe Entscheidung E3) |
| C20 (Enthüllung) | Replay von C00 | **unverändert** – C00 bleibt bild-/tonidentisch |

Bleibt ausdrücklich bestehen: Die Samenzelle hat **kein Bewusstsein**, keine Gedanken- oder Erzählstimme; der Spieler steuert eine biologisch begrenzte Schwimmbewegung (bisherige Regel 02-B). Die Schwimmphase wird **kein Wettrennen** („wer zuerst da ist, gewinnt“ bleibt ausgeschlossen). Der Lichtschlag liegt im Übergang C00 → C01, nicht bei der Verschmelzung (keine „Seeleninjektion“). Wissenschaftliche Plausibilität (Grundsatz 2) gilt weiter.

## 2. Dialog-IDs

- Entfällt: Erzählstimme C01 (zwei Sätze in 01-B). Sie hatten noch keine IDs; reserviert und gestrichen als **VO_C01_001, VO_C01_002** sowie **SUB_C01_001, SUB_C01_002**.
- Neu: keine Dialoge. C02-Erklärtexte („Befruchtung“, „Zygote“, „Erste Teilung“) unverändert, nur im Dokumentationsmodus.

## 3. Trigger / Ablauf (MENU_FLOW)

| | heute | neu |
|---|---|---|
| Start | `STORY_START` = C00 + C01 → `TITLE_CARD` → Hauptmenü → „Neues Leben“ → Kapitelkarte → C02 | `STORY_START` = C00 → C01 (Lichtschlag) → **C02 mit Pflicht-Schwimmphase** → `TITLE_CARD` → Hauptmenü → „Neues Leben“ → Kapitelkarte → **C03** |
| Welt-/Leben-Initialisierung | bei „Neues Leben“ | **vor C02** (die Befruchtung braucht `WorldID`, `LifeID`, `WorldTime` strikt nach dem Tod in C00 – Regel bleibt) |
| Überspringen | C00/C01 mit Zweifachbestätigung → `CommitPending` | C00 weiterhin überspringbar (Zweifachbestätigung, `PreIncarnation_SoulSeed` wird angelegt) · **Schwimmphase nicht überspringbar** (Pflicht), aber mit Hilfe-Option (siehe E2) |
| Scheitern | Befruchtungssimulation kann scheitern → biologisches Alternativende | Schwimmphase hat **kein Game Over** (E2). Die Regel für gescheiterte Einnistung (C02 VARIANTEN/C03) bleibt unverändert |

## 4. Musik und Ton

- C00-Ende (zwei leise Töne, Soul-Intervall) **unverändert**.
- Lichtschlag: kein Knall, kein Effektton; Stille bzw. ein einzelner tiefer Luftzug (Licht macht keinen Ton). Der Übergang Regen → Wind aus der C01-Klangregie entfällt mit 01-B.
- Atmosphärischer Chor: wandert mit der Titelkarte ans Ende von C02.
- Cue `M02_BEGINNING` (C01/C02) bleibt, wird neu getimt; „keine vorzeitige Spoiler-Stimme“ gilt weiter.

## 5. Barrierefreiheit (neu nötig wegen des Lichtschlags)

- Boot-Hinweis um eine **Lichtwarnung** ergänzen (vor C00, da der Lichtschlag vor dem Hauptmenü kommt).
- Einstellung „Lichtblitz abschwächen“ (weiches Aufblenden statt Puls), Standard **an**, bis der Spieler es ändert – der Blitz kommt vor jeder Einstellmöglichkeit.
- Ein einzelner Puls, nie mehr als 3 Lichtwechsel pro Sekunde, kein großflächiges Rot (übliche Grenzwerte für lichtempfindliche Epilepsie).

## 6. Spielstand-Migration

Spielstand-Schema 2 bekommt den Zustand „STORY_START abgeschlossen bis einschließlich C02“ und die `LifeID` entsteht vor C02 statt bei „Neues Leben“. **Es gibt noch keine echten Spielstände** (nur Testspeicher der CM-Automationstests). Migration: Testspeicher werden verworfen, die Tests auf den neuen Ablauf angepasst. Keine Spieler-Migration nötig.

## 7. Technische Folgen (nach Freigabe, getrennt freizugeben)

- `docs/v4_2/MENU_FLOW.json` (`STORY_START`, `TITLE_CARD`), Szenenverträge C01/C02, Cinematic-Zustandsmaschine, Automationstests `Genesis.Cinematic.*` und Menü-Tests.
- `SCENE_REGISTRY.json` / `SCENE_MATRIX_C00_C21.json` neu an ScriptLock 1.2 binden (`tools/v4_2/bind_scriptlock.py`, neue Zeilenbereiche + SHA-256).
- C02 wechselt von Kategorie B (beobachtend, optional interaktiv) zu einer Szene mit **Pflicht-Gameplay**.
- Kinotrailer: nicht betroffen (zeigt C00, keine C01-Montage).

## 8. Entscheidungen, die mit dem JA festgelegt werden (Vorschlag in Klammern)

| Nr. | Frage | Vorschlag |
|---|---|---|
| E1 | Wo kommen Titel und Hauptmenü hin? | **Nach der Befruchtung** (Ende C02), damit nach dem Lichtschlag wirklich direkt die Samenzelle kommt |
| E2 | Was passiert, wenn der Spieler die Eizelle nicht erreicht? | **Kein Game Over**: eine andere Samenzelle erreicht sie, die Kamera wechselt in die objektive Sicht, die Szene läuft weiter. Dazu eine Hilfe-Option „automatisch schwimmen“ |
| E3 | Gilt die Pflicht auch für das Schwangerschaftskapitel nach einer Wiedergeburt (C17)? | **Nein**, dort bleibt es optional |
| E4 | Länge der Schwimmphase | **60–120 s** Spielzeit, danach führt die Strömung sanft zur Eizelle |

## 9. Was dieser Antrag NICHT ist

Keine Freigabe von Assets, Code oder Produktion; keine Änderung an C00, C03–C21, C15/C16-Konflikt CON33-01, C17-Epochenwortlaut oder C21-Finale. Das Canon-Archiv `canon_sources/` wird von Claude nicht beschrieben: Nach dem JA bereitet Claude die Fassung 1.2 vor, der Game Director legt sie selbst ab.

**Freigabe:** „JA zu CR-001“ (mit den Vorschlägen E1–E4) oder „JA zu CR-001 mit …“ (abweichende Entscheidungen).
