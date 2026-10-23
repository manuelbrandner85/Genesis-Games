# G5 – Spielbare Figur · Status: ENGINE_TESTED (automatisch) · Menschentest offen

Datum: 2026-10-23 · Zweig `v4/neustart` · UE 5.8.3 · Testlevel `/Game/Genesis/TechSmoke/Maps/L_TechSmoke`

## Was gebaut ist

| Teil | Umsetzung |
|---|---|
| Figur | `AGenesisPrototypeCharacter` (C++). Kapsel 42 / 96 cm (1,8-m-Erwachsener) |
| Aussehen | **Platzhalter:** Epics Mannequin `SKM_Manny_Simple` + `ABP_Unarmed` (Idle/Walk/Run/Jump), eingetragen in `Config/DefaultGame.ini` (`ProxyMesh`, `ProxyAnimClass`) – austauschbar ohne Code. Lokal kopiert mit `tools/setup/Copy-EngineMannequin.ps1`, **nicht im öffentlichen Repo** (Epic-Vorlageninhalt) |
| Bewegung | Gehen **1,75 m/s** (6,3 km/h), Laufen **4,5 m/s** (16,2 km/h), Sprung **45 cm** (Absprung v = √(2gh) ≈ 297 cm/s), Stufe bis 40 cm, begehbar bis 44°, Drehung zur Laufrichtung 540°/s, Luftsteuerung 0,25 |
| Steuerung (Enhanced Input, im Code) | WASD / linker Stick bewegen · Maus / rechter Stick schauen (150°/s) · Leertaste / A springen · **Shift halten / linken Stick drücken (umschalten) laufen** |
| Kamera | Arm 2,8 m über der rechten Schulter (+45 cm seitlich, +60 cm hoch), Kollisionstest, leichte Nachführung, Sichtfeld 70°, Blick −70° … +55° |
| Stick-Totzone | rechter Stick **0,3** statt 0,2: Der Controller am Entwicklungs-PC steht in Ruhe bei ~27 % und hätte die Kamera im Spiel selbständig gedreht. Linker Stick 0,2 |
| Startpunkt | `PlayerStart_TechSmoke` 4 m vor und 2 m neben der Palette, Blick +X |

## Tests – alle bestanden

**Schnelle Tests** (Testwelt mit Boden, echte Figur, 60-Hz-Schritte) – `docs/evidence/G5/unit_tests_report.json`: **6/6, 0 Warnungen**

| Test | Gemessen |
|---|---|
| `Genesis.Gameplay.LandsOnFloor` | landet und läuft; Füße 2,15 cm über dem Boden (Unreals normaler Schwebeabstand der Kapsel) |
| `Genesis.Gameplay.WalkAndRunSpeed` | Gehen 175,00 cm/s, 5,19 m in 3 s; Laufen 450,00 cm/s; kommt ohne Eingabe zum Stehen; schaut in Laufrichtung |
| `Genesis.Gameplay.JumpHeight` | Sprung **45,00 cm**, landet wieder |
| `Genesis.Gameplay.CameraRig` | Arm 2,8 m, Kollision an, Blickgrenzen, Kapsel 96 cm |
| `Genesis.Input.PrototypeMapping` | 11 Belegungen, 14 Wertefälle, darunter **der gemessene Drift des rechten Sticks (−0,047 / 0,273) → keine Drehung** |
| `Genesis.Input.PrototypeBindings` | 7 Bindungen inklusive Laufen (halten + umschalten) |

**Spieltest im sichtbaren Editor (Play-in-Editor)** – `Genesis.Gameplay.PIEPlaythrough`, `docs/evidence/G5/pie_playthrough_log.txt`: **bestanden**

Echtes Level, echter GameMode, echter Spieler: Mannequin geladen, Animation läuft. 3 s gehen, 2 s laufen, ausrollen, springen. Gemessen: **Gehen 175,0 cm/s · Laufen 450,0 cm/s · Strecke 14,15 m · Sprung 45,0 cm · gelandet.** Bildschirmfoto im Lauf: `docs/evidence/G5/pie_running.png`.

## Unterwegs gefunden und behoben

- Die Testwelt startete das Spiel nicht (kein GameMode → kein BeginPlay) → Spielstart in der Testwelt ausdrücklich angestoßen.
- Die Bewegung lief nur ein einziges Mal, weil Unreal jede Tick-Funktion nur einmal pro Engine-Frame ausführt → Frame-Zähler pro Testschritt weitergezählt.
- Der Testboden bekam kein Mesh (statische Mobilität) → beweglich gesetzt.
- Die Phasen des Spieltests liefen nach Echtzeit; beim Ruckeln des Editors stimmte die Strecke nicht (10,5 m) → Spielzeit statt Echtzeit.
- C++-Warnung als Fehler (lokale Variable verdeckt Klassenmitglied) → umbenannt.

## Nicht geprüft / offen

- **Menschentest (Pflicht für G5):** Steuerung mit echter Tastatur, Maus und Controller, Mausempfindlichkeit, Kameragefühl. Das kann nur ein Mensch beurteilen.
- **Controller:** Der rechte Stick deines Xbox-360-Controllers driftet (~27 %). Die Totzone 0,3 fängt das ab, aber der Stick hat dadurch etwas weniger feinen Bereich. Die echte Lösung ist kalibrieren oder ersetzen.
- **Testlevel endet nach 30 m:** Am Horizont sieht man den Rand der Bodenplatte. Für Technik-Tests unkritisch, für den Goldstandard-Slice nicht.
- **Platzhalter-Figur:** Mannequin, keine GENESIS-Figur, kein Reality Check der Figur. Die Animationen sind Epic-Vorlagen (Fußgleiten bei 1,75 m/s nicht geprüft).
- Bildraten 30/60/120 und Kamera in engen Räumen (aus V3-10) noch nicht getestet.
