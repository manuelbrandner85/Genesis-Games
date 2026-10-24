# F1 – Kostenlose KI-Werkzeuge installiert und probegelaufen · Status: READY (Werkzeuge), keine Spielassets

Datum: 2026-10-24 · Freigabe: Chat-Zustimmung des Nutzers nach dem F0-Bericht („Ja zu deiner Empfehlung und FLUX.2 klein 4B die Bild-KI. Auch die restlichen darfst du installieren die wir brauchen“). Pläne mit Quelle, Version, Größe, Lizenz, Befehlen und Rückbau: `docs/v4_1/install_plans/`.

Alles liegt in **`C:\Users\manue\AI-Tools\GENESIS\`**, je Werkzeug in einem eigenen Ordner mit eigener Python-Umgebung. Es gibt keine globale Python-Änderung, keinen Systemdienst und keinen offenen Netzwerkport. Rückbau: den Ordner löschen.

## Ergebnis

| Werkzeug | Version | Größe | Lizenz | Probelauf | Status |
|---|---|---|---|---|---|
| FLUX.2 klein 4B (Bild) | bereits vorhanden, ComfyUI 0.41.0 | 16 GB | Apache-2.0 (Modellkarte) | in G1–G6 bereits benutzt | READY |
| **Piper** (Stimme) | piper-tts 1.8.0 (GPL-3.0, nur Werkzeug), onnxruntime 1.31.0 | 0,4 GB | Stimmen siehe unten | 4 Stimmen erzeugt | READY |
| **faster-whisper** (Spracherkennung) | 1.2.1, ctranslate2 4.8.3, Modell „small“ (Revision 536b066) auf CPU | 0,7 GB | MIT | 4 Stimmproben geprüft | READY |
| **ACE-Step 1.5** (Musik) | Tag v0.1.8 (dce6214), Gewichte HF 19671f4 (2B-Turbo-Modell, VAE, Textencoder, Sprachmodell 1,7B), torch 2.7.1+cu128 mit RTX-5070-Unterstützung | Code + Umgebung 6,3 GB, Gewichte 9,4 GB | Code und Gewichte MIT; laut Modellkarte kommerziell nutzbar | 30 s Instrumentalstück erzeugt | READY |

Insgesamt kamen rund **17 GB** neu hinzu.

### Stimmen (geladen nur mit geklärter Lizenz)

| Stimme | Lizenz | Whisper-Abgleich mit dem Testsatz | Einschätzung |
|---|---|---|---|
| de_DE-thorsten-high (männlich) | CC0 | **fehlerfrei** | gut verständlich, beste Qualität |
| de_DE-thorsten_emotional-medium (männlich, mit Stimmungen) | CC0 | **fehlerfrei** | gut |
| de_DE-kerstin-low (weiblich) | CC0 | 2 Wörter falsch („Stimmtes“, „Fuhrsorf“) | niedrige Qualitätsstufe, nur Platzhalter |
| de_DE-mls-medium (mehrere Sprecher) | CC-BY-4.0 (Namensnennung) | **unbrauchbar** (Gestammel) | Mit der Standard-Sprecherauswahl nicht brauchbar; andere Sprecher-IDs sind noch nicht getestet. |

Nicht geladen: **pavoque** (Lizenz CC BY-NC-SA, nicht kommerziell); **eva_k, karlsson, ramona** (M-AILABS, Lizenz auf der Modellkarte nicht angegeben).

**Wichtig für die Stimmproduktion:**
- Es gibt **nur eine gute weibliche deutsche Stimme mit niedriger Qualität**. Für die drei Rollen N01–N03 reicht das als Platzhalter, als Endqualität nicht.
- Piper klingt hörbar synthetisch. Für echte Sprachaufnahmen bleibt später eine Sprecherin oder ein Sprecher der realistische Weg.
- Piper braucht `PYTHONUTF8=1`, sonst werden Umlaute falsch gelesen. Diesen Fehler hat der Whisper-Abgleich aufgedeckt, behoben ist er in den Belegen.
- Die Piper-Ausgaben gehen bis knapp an die Übersteuerung (Spitze 1,0, 2 übersteuerte Samples). Die Produktionskette muss auf −1 dB normalisieren.

### Musik

- `docs/evidence/F1/acestep_smoke_flussdorf_morning_seed2026.ogg`: 30 s, 48 kHz, ruhiger Akustik-Folk (Gitarre, Akkordeon, Streicher, kein Schlagzeug), feste Saat 2026, Lautheit −14,1 LUFS.
- Der Lauf brauchte 26 s zum Laden und 275 s zum Erzeugen. Grafikspeicher in der Spitze 7,3 GB. Der Unreal Editor lief parallel, deshalb fiel der Decoder auf die langsame Kachel-Variante zurück. Ohne Unreal ist er deutlich schneller.
- Künstlerisch geprüft ist das Stück **noch nicht**; ich kann es nicht anhören. Es ist ein Werkzeugtest und kein GENESIS-Musikstück.

## V4.1 im Projekt

- Die V4.1-Dateien sind in `Genesis-Games` (`v4/neustart`) übernommen: 53 neue Dateien, dazu `CLAUDE.md`, `README.md` und drei Prüfskripte in der V4.1-Fassung. `.gitignore` habe ich ergänzt statt ersetzt.
- `.claude/settings.json` enthält jetzt den V4.1-Prüf-Hook gegen Installationsbefehle.
- Selbsttests: `tools/v4_1/test_free_ai.py` **14/14**, `validate_package.py` **STATIC_PASS**. Ein Test schlug zuerst fehl: Er hielt eine von Unreal erzeugte `.pth`-Pfaddatei in `Intermediate/` für ein Modell. Unreal-Build-Ordner sind jetzt ausgenommen.
- **Offen gesagt:** Der neue Hook wird erst in einer neuen Claude-Sitzung aktiv. Der Download der ACE-Step-Gewichte lief deshalb ohne Konsolen-Freigabebeleg, gedeckt durch deine Chat-Zustimmung; den Plan dazu habe ich vorher geschrieben (`FA-ACESTEP-002`). Ab der nächsten Sitzung braucht jeder weitere Download den Beleg. Den legst du selbst an:
  `python tools/v4_1/approval_gate.py --plan .genesis_approvals/<PLAN>.json --interactive-receipt`
  Dabei tippst du `FREIGABE <PLAN>`. Ich erstelle solche Belege nicht selbst.

## Was fehlt

- Musik und Stimmen sind nur Werkzeugtests. Echte GENESIS-Stimmen brauchen deine freigegebenen Dialogsätze aus G6. Echte Musik braucht eine Musikliste (Cue-Liste) für Flussdorf.
- 3D bleibt bei Blender (MPFB und Modellieren nach Referenzbild). TRELLIS wird nicht verwendet.
- Audacity habe ich nicht installiert; FFmpeg reicht für Schnitt, Pegel und Umwandlung.
