# GENESIS V4.2 – CM0 bis CM3 (Cinematic-/Menü-Grundlage)

Datum: 2026-10-24 · Zweig `v4/neustart` · Unreal Engine 5.8.3 · RTX 5070

## Kurzfassung

| Gate | Inhalt | Status | Beleg |
|---|---|---|---|
| CM0 | V4.2-Paket übernommen, Quellen-/Toolaudit, alle 22 Szenen C00–C21 per Zeilenbereich + SHA-256 an ScriptLock 1.1 gebunden | **erledigt** | `docs/v4_2/SCENE_REGISTRY.json`, `tools/v4_2/bind_scriptlock.py` |
| CM1 | Szenenverträge, Cinematic-Zustandsmaschine, Kanonschutz, C20-Replay-Regel, Menü-Flussgraph, Spielstand-Schema 2 | **ENGINE_TESTED** | 8 Automationstests grün |
| CM2 | Hauptmenü mit Boot-Hinweisen, Titelkarte, Fortsetzen/Neues Spiel/Laden (3 Plätze), Einstellungen, Barrierefreiheit, Credits, Beenden, Pausenmenü | **ENGINE_TESTED (Editor-PIE + eigenständiges Windows-Fenster)**, Paket-Build und echter Controller ausstehend | `Genesis.Menu.PIERoute`, Bilder `docs/evidence/V42/cm2_*.jpg` |
| CM3 | Nicht-kanonischer technischer C00-Kameratest über den Vertrag (Abspielen, Überspringen, Commit, Rückgabe) | **ENGINE_TESTED (nur Technik, kein Kanon)** | `Genesis.Cinematic.TechC00PIE` |

Gesamte Testreihe: **26/26 Automationstests bestanden** (`docs/evidence/V42/regression_cm3.txt`).

## Kanonschutz – was bewusst NICHT passiert ist

- ScriptLock 1.1 ist weiterhin **Kandidat**. Ohne „JA zu Vorschlag 11“ (ScriptLock IV.D) läuft keine Szene als Kanon. Der Code erzwingt das: Ein Vertrag ohne Regiefreigabe bindet nur als `bTechnicalTest`, und technische Tests schreiben **nie** ins Weltbuch.
- Der Boot-Ablauf überspringt deshalb `STORY_START` (Prolog C00/C01) und geht direkt zur Titelkarte.
- C15/C16 (CON33-01), C17 und C21 bleiben `WAITING_DIRECTOR_DECISION`. Der Vertrag meldet den offenen Konflikt.
- C20 bindet nur als **Originalaufnahme von C00** (gleiche Masterdatei mit SHA-256), nie als Neu-Rendering.
- Kein Drehbuchtext im Repo, nur IDs, Zeilenbereiche und Hashes.

## CM1 – Verträge (C++)

- `FGenesisSceneContract` mit allen V4.2-Feldern (SceneID, ScriptVersion 1.1, Soul-/Life-/WorldID, WorldTime, WorldSeed, Teilnehmer, Ereignisbelege, Variante, Sprache, Zustand, Skip-Regel, Replay-Rezept, Audio-/Untertitel-Cues, Rückgabezustand und -ort).
- Zustandsmaschine mit genau 10 erlaubten Übergängen. Überspringen führt `Playing → CommitPending`, also nie am Commit vorbei. Bei interaktiven Szenen (C05, C06, C08, C10, C11, C16, C20) wartet das Spiel auf die Entscheidung des Spielers und trifft keine automatisch.
- Der Commit ist idempotent: einmal pro Szene, Leben und Variante, über den bestehenden Ledger.
- Menügraph aus `MENU_FLOW.json` mit Prüfung auf unerreichbare Knoten und tote Enden.
  - Laufzeitkopie `Content/Genesis/Data/menu_flow.json` mit zwei ergänzten Rückwegen: Einstellungen → Pause und Laden → Pause.
  - Grund: Aus dem Pausenmenü geöffnete Bildschirme sollen in die Pause zurückführen, nicht ins Hauptmenü.
- Spielstand-Schema 2 mit SoulID, LifeID, WorldID, WorldSeed und LifeNumber.
  - Alte Schema-1-Stände werden beim Laden deterministisch migriert: dieselbe Datei ergibt immer dieselbe Identität.
- Die JSON-Daten werden im Paket als lose Dateien mitgeliefert (`DirectoriesToAlwaysStageAsNonUFS`).

## CM2 – Hauptmenü

**Karte und Start**
- Karte `L_MainMenu` ist jetzt Startkarte des Spiels.
- Hintergrund ist die G7-Werkstatt mit langsam driftender Kamera. Es gibt dort keine Weltsimulation, keine Figuren und keine Speicherzugriffe.

**Ablauf**
- Studio-Karte → „Erstellt mit Unreal Engine“ → Gesundheitshinweis (Lichtblitze) → Lautstärke-Hinweis.
- Danach die Titelkarte „GENESIS – Beliebige Taste drücken“, dann das Hauptmenü.
- Nach der Rückkehr aus dem Spiel geht es direkt ins Hauptmenü.

**Speicherplätze**
- Drei Plätze (Slot1–3) zeigen Tag, Uhrzeit, Geld und Speicherzeit, oder „leer“ bzw. „beschädigt“.
- „Fortsetzen“ erscheint nur, wenn ein gültiger Spielstand existiert.
- „Neues Spiel“ fragt vor dem Überschreiben nach und speichert dann sofort einen Startstand.
- Tests und Editor-Starts nutzen eigene Plätze und berühren nie Spielerstände.

**Einstellungen** – sofort wirksam:
- Grafikprofil, Anzeigemodus, VSync, Bildratengrenze
- Gesamtlautstärke
- Kamera-Empfindlichkeit und Y-Umkehr
- Bewegungsunschärfe

**Barrierefreiheit**
- Textgröße 100/125/150 % wirkt sofort in Menü und HUD; das Menü-Panel wächst mit.

**Nur gespeichert, noch ohne Wirkung** – im Menü offen als solche gekennzeichnet:
- Sprache-, Musik- und Effekt-Lautstärke
- Untertitel und Sprechername
- Lesetempo
- Blitz- und Wackelreduktion

**Steuerung**
- Tastatur, Maus und Gamepad: Pfeile/Steuerkreuz bewegen den sichtbaren Fokus, Enter/A wählt, Esc/B geht zurück, ←/→ ändert Werte.
- Mausüberfahrt setzt den Fokus mit.

**Pausenmenü im Spiel** (Esc, P oder Gamepad-Menütaste)
- Fortsetzen, Speichern, Laden, Einstellungen und Hauptmenü (mit Rückfrage).
- Die Spielzeit steht still, solange das Pausenmenü offen ist.

## CM3 – technischer C00-Test

- `LS_C00_TechTest`: 6 s Kamerafahrt durch die Werkstatt, ohne Figuren, Text oder Story.
- Start in der Konsole mit `GenesisTechCinematic`.
- Während des Tests ist die Spielersteuerung gesperrt. Esc, B oder Backspace überspringt.
- Der PIE-Test spielt die Sequenz zweimal:
  - einmal übersprungen
  - einmal bis zum Ende
- Geprüft wird jedes Mal:
  - Zustand `HandedBack`
  - Kamera wieder beim Spieler
  - Steuerung wieder frei
  - Weltbuch unverändert
  - kein Pausenmenü über der laufenden Sequenz

## Gefundene und behobene Fehler

1. **Absturz im eigenständigen Spiel** beim Wechsel von der Titelkarte zum Menü.
   - Ursache: Menüeinträge bekamen bei jedem Neuaufbau feste Objektnamen, und ein noch lebendes Widget wurde überschrieben.
   - Folge im Log: „Assertion failed: Index >= 0“.
   - Behoben durch eindeutige Namen. Danach traten bei mehreren Läufen 0 Assertions auf.
2. **←/→ änderte keine Werte.** Slate verbrauchte die Pfeiltasten für die Navigation, bevor das Menü sie sah.
   - Jetzt werden sie in der Vorschau-Phase abgefangen. Der PIE-Test prüft das mit echten Tastenereignissen.
3. **Schwarze Balken im Menühintergrund** durch das erzwungene Kamera-Seitenverhältnis – behoben.
4. **Controller-Symbole Ⓐ/Ⓑ** gibt es in der Schrift nicht – ersetzt durch „A/B“.
5. **Commit „G7 Lieferung 4“ (1bf5be0) war unvollständig.** Er enthielt nur das Entfernen einer Manifestdatei. Die Dateien wurden mit Commit 762f7b7 nachgeholt.

## Was noch fehlt (offen, nicht beschönigt)

- **Freie Tasten- und Controller-Belegung** (ScriptLock III-D) – nicht gebaut.
- **Filmkorn-Schalter** fehlt.
- **Lebensarchiv im Pausenmenü** fehlt; es erscheint laut Spezifikation erst nach Freischaltung, die es noch nicht gibt.
- **Untertitel, Lesetempo, Blitz-/Wackelreduktion und Einzel-Lautstärken** sind gespeichert, wirken aber erst mit Vertonung, Musik und Cinematics (CM4+).
- **Prüfstand der Menütests**
  - Getestet in Editor-PIE und als eigenständiges Windows-Fenster (`-game`).
  - **Kein gepackter Windows-Build** und **kein Test mit echtem Gamepad**: Gamepad-Tasten wurden als Slate-Ereignisse simuliert. Hinweis: Der rechte Stick des vorhandenen Controllers driftet.
  - Nach V4.2-Regel ist das Menü damit noch nicht voll abgenommen.
- **Echtes C00/C01, alle 22 Cinematics, Dialoge, Stimmen, Musik** – alles erst nach „JA zu Vorschlag 11“.
- Menü-Musik und Menü-Klänge fehlen.
- **Menschliche Sichtprüfung** von Menü, Werkstatt und Techniktest steht aus.

## Nächster Schritt (Entscheidung beim Game Director)

Für CM4 (echtes C00) braucht es die Regiefreigabe von ScriptLock 1.1: **„JA zu Vorschlag 11“**. Bis dahin sind möglich:
- Tastenbelegung
- gepackter Windows-Build mit Controller-Test
- Lumen-Kalibrierung der Werkstatt

---

# Nachtrag CM4 – Regiefreigabe und C00-Produktionspaket (2026-10-24)

**Regiefreigabe:** Der Game Director hat ScriptLock 1.1 freigegeben: „Ja“ auf die Frage nach „JA zu Vorschlag 11“, protokolliert als [GD-2026-10-24-01](../v4_2/DIRECTOR_DECISIONS.md).
- Folgen im System:
  - Kanon gesperrt, alle 22 Szenen im Register auf `DIRECTOR_APPROVED`.
  - Kanonische Szenenverträge sind jetzt möglich.
  - C15/C16, C17 und C21 bleiben durch ihre offenen Konflikte blockiert; ein Test prüft das.
- Keine Produktions-, Asset- oder Downloadfreigabe (ScriptLock IV.D).

**Menü am Kanon ausgerichtet (C01 SHOT 01-D):**
- Titelkarte „GENESIS – DER KREISLAUF DES LEBENS / Jede Entscheidung hinterlässt ein Echo.“
- „Beliebige Taste drücken“ erst nach kurzer Stille.
- Menüpunkte „Neues Leben“ und „Mitwirkende“.
- Die erste Bootkarte ist keine zweite Titelkarte mehr.

**C00-Produktionspaket v1 (Entwurf zur Abnahme):**
- Vollständig nur lokal (`canon_sources/production/C00/`, gitignored, enthält Drehbuchinhalt): Shotliste 00-A…00-E mit Optik und Ton, 8 Dialog-Cues mit Untertitel-IDs, Figuren-DNA, Set, Musik und Ton, Produktionsweg, Abnahmekriterien.
- Öffentliche Fassung ohne Text: [C00_PRODUCTION_PLAN.md](../v4_2/C00_PRODUCTION_PLAN.md).

**Referenzentwürfe:**
- 9 Bilder lokal mit FLUX.2 klein erzeugt; davon 2 verworfen und 1 Ersatz (s42) bevorzugt.
- Ablage: `ArtSource/Reference/C00/`. Status `GENERATED_PREVIEW`, nicht abgenommen.

**Tests:** 26/26 bestanden (`docs/evidence/V42/regression_cm4.txt`).

**Offen für C00 (CM4-Abnahme fehlt noch):**
- Regieabnahme von Shotliste, Figuren-DNA und Referenzen
- Besetzung echter deutscher Stimmen
- Freigabe von MetaHuman (Plugin/Inhalte)
- Quelle `Docs/33_Der_Vorfilm.md`
