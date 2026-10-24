# F0 – Inventur kostenloser KI-Werkzeuge (GODMODE 4.1) · Status: NUR GEPRÜFT, NICHTS INSTALLIERT

Datum: 2026-10-24 · Nur gelesen: kein Download, keine Installation, keine Einstellungsänderung.
Ausgeführt wurden nur die V4.1-Prüfskripte `hardware_probe.py` und `ai_tool_manager.py` (Python isoliert, `-I`). Dazu kamen Datei- und Ordnerlisten sowie SHA-256-Prüfsummen. Für die Lizenz von FLUX.2 klein habe ich die Modellkarte auf Hugging Face gelesen.

## Hardware (gemessen)

| Teil | Wert |
|---|---|
| Grafikkarte | NVIDIA GeForce RTX 5070, **12 227 MiB**, Treiber 630.20 |
| Prozessor / RAM | AMD Ryzen 7 5700X · 32 GB |
| System | Windows 11 Pro 10.0.26340 (Insider) · Python 3.13.15 |
| Freier Platz C: | ≈ 345 GiB |
| Engines | Unreal Engine 5.8.3 (`C:\Program Files\Epic Games\UE_5.8`), Blender 5.2.1 LTS |

## Originalquellen

- Alle **39 Arbeitskanon-Dateien** in `canon_sources/` haben dieselbe SHA-256-Prüfsumme wie im G1-Manifest: 39 von 39 stimmen, keine fehlt und keine ist verändert.
- Die unveränderte Original-MD im V4.1-Paket ist byte-gleich mit dem V4-Stand im Repo.
- Das V4.1-Paket ändert weder die Geschichte noch C00–C21 oder J00–J24.
- Neu sind nur Werkzeuge und Regeln für kostenlose KI: 53 neue Dateien und 7 geänderte Steuerdateien. Geändert sind `CLAUDE.md`, `README.md`, `.gitignore`, `.claude/settings.json` (neuer Prüf-Hook für Installationsbefehle) und drei Prüfskripte.

## 1 · INSTALLIERT (auf deinem PC vorhanden)

| Werkzeug | Version / Ort | Lizenz | Einsatz bei GENESIS |
|---|---|---|---|
| ComfyUI portable | 0.41.0 · `Desktop\GAMEFORGE_GODMODE_v2_0\engines\ComfyUI_windows_portable` · keine Zusatz-Nodes | GPL-3.0 (Werkzeug) | Referenzbilder |
| **FLUX.2 klein 4B** | `flux-2-klein-4b.safetensors` (7,75 GB) SHA-256 `ec3d4e73…bda7a343` | **Apache-2.0**, laut Modellkarte kommerziell nutzbar (geprüft 2026-10-24) | Referenzbilder, Konzept, Maßblätter |
| Qwen3-4B Textencoder | `qwen_3_4b.safetensors` (8,04 GB) SHA-256 `6c671498…36edfc5a` | Apache-2.0 (Comfy-Org-Paket) | gehört zu FLUX.2 klein |
| FLUX.2 VAE | `flux2-vae.safetensors` (336 MB) SHA-256 `868fe7b3…66ce8f3`* | Apache-2.0 (Comfy-Org-Paket) | gehört zu FLUX.2 klein |
| Blender | 5.2.1 LTS + MPFB (Menschenkörper) + MCP + Baker-Add-ons | GPL; MPFB-Assets CC0 | Modelle, Rig, Turnarounds |
| Unreal Engine | 5.8.3 | Epic-EULA (Tantieme ab 1 Mio. $ Umsatz) | Spiel |
| Krita | 5.3.4 | GPL-3.0 | Texturen, Nacharbeit |
| FFmpeg | 9.0.2 | LGPL/GPL | Video, Audio, Prüfung |
| Ollama | gemma2 2B, llama3.2 3B, qwen2.5 0.5B/3B | je Modell eigene Lizenz | **wird nicht gebraucht**, bleibt unberührt |

\* VAE vollständig: `868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3`.

**Abweichung vom V4.1-Paket:** Die V4.1-Matrix nennt FLUX.1 schnell. Auf deinem PC ist bereits **FLUX.2 klein 4B** installiert, das du als Standard festgelegt hast. Es hat ebenfalls Apache-2.0, ist neuer und passt in 12 GB. Empfehlung: FLUX.2 klein 4B bleibt, FLUX.1 schnell wird nicht zusätzlich geladen. Die **9B-Variante** von FLUX.2 klein steht unter einer Nicht-kommerziell-Lizenz und bleibt gesperrt.

## 2 · INSTALLATION NACH FREIGABE (fehlt noch für die Goldstandard-Region)

Für jedes Werkzeug gibt es vor dem Download einen eigenen Plan mit URL, Version/Commit, Größe, Prüfsumme, eigenem Ordner und Rückbau. Es läuft nur lokal (127.0.0.1), in einer eigenen Python-Umgebung und ohne globale Änderungen.

| Werkzeug | Wozu | Grobe Größe | Hinweis |
|---|---|---|---|
| **Piper** (Sprachausgabe) + deutsche Stimmen | Stimmen der Bewohner (N01–N03) | Programm ≈ 30 MB, je Stimme ≈ 60 MB | Jede Stimme hat ihre eigene Lizenz. Klingt hörbar synthetisch, Vorschlag: nur als Platzhalter-Stimme. |
| **ACE-Step 1.5** (Musik) | Musik für Flussdorf, Tag und Abend | mehrere GB, genaue Zahl im Einzelplan | Code MIT. Gewichte und die passende Variante für 12 GB prüfe ich vorher. |
| **faster-whisper** (Spracherkennung) | Untertitel-Timing und Prüfung, ob Stimme und Text übereinstimmen | Programm klein, Modell „small“ ≈ 0,5 GB | Code MIT |
| Audacity | Audio schneiden, Pegel | ≈ 60 MB | optional; FFmpeg deckt das Meiste ab |

## 3 · LIZENZ UNGEKLÄRT

- **Deutsche Piper-Stimmen:** Jede Stimmkarte prüfe ich einzeln, erst dann wird sie geladen.
- **ACE-Step-1.5-Gewichte:** Die genaue Datei und ihre Lizenz sind noch nicht geprüft.
- **TRELLIS-Nebenteile:** Der Code ist MIT. Einzelne Abhängigkeiten, zum Beispiel die Rasterizer, haben eigene, teils nicht-kommerzielle Lizenzen. Damit ist eine kommerzielle Nutzung der Ergebnisse nicht freigabefähig, solange das nicht geklärt ist.
- **Ollama-Modelle:** Sie werden nicht benutzt. Qwen2.5-3B hat zum Beispiel eine eigene Forschungslizenz.

## 4 · HARDWARE UNGEEIGNET / GESPERRT

| Werkzeug | Grund |
|---|---|
| **TRELLIS** | Es ist bereits nativ unter Windows vorhanden (`C:\Users\manue\AI\TRELLIS`, Commit 442aa1e, 1,2 GB, Gewichte 2,9 GB) und lief dort schon einmal. Offiziell verlangt es Linux und 16 GB; gemessen wurden **12,28 GB Spitze**, also genau am Limit. V4.1 und deine Ansage („nur wenn notwendig“) sagen: Modelle in Blender selbst bauen. Ich benutze es nicht; die Installation bleibt unangetastet liegen. |
| FLUX.1 dev, FLUX.2 klein 9B | Lizenz nicht kommerziell |
| große ACE-Step-Varianten | brauchen mehr als 12 GB |

## Offene Entscheidungen

1. **Projektort:** V4.1 schlägt einen neuen Ordner vor. Du hast aber `Desktop\Genesis-Games`, Zweig `v4/neustart`, schon als neues GENESIS-Projekt bestimmt, und dort sind G1–G6 erledigt. Empfehlung: dort weitermachen.
2. **V4.1-Dateien ins Projekt übernehmen:** Das betrifft die 53 neuen Dateien und die 7 Steuerdateien. Bei `.gitignore` und `CLAUDE.md` wird zusammengeführt, nicht überschrieben. Dazu kommt der neue Prüf-Hook in `.claude/settings.json`.
3. FLUX.2 klein 4B als Bild-KI für GENESIS bestätigen.
4. Einzelpläne für Piper, ACE-Step und faster-whisper erstellen. Das ist nur der Plan, noch kein Download.
5. Aus G6 noch offen: dein eigener Spieltest sowie die Freigabe der Dialogsätze und Startwerte.
