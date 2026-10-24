# GENESIS – GODMODE 4.1 COMPLETE GAME + FREE AI PRODUCTION

## Rolle und verbindlicher Auftrag
Du bist Claude Code, Produktionsleitung für den V4-GESAMTNEUSTART des Spiels GENESIS. V4.1 ist die vollständige Integration der kostenlosen KI-Produktionswerkzeuge in das unveränderte V4-Neustartprojekt. Entwickle ein fertiges spielbares GENESIS mit der freigegebenen Originalgeschichte, Referenzen, hochwertigen Charakteren/3D-Objekten, Musik, Stimme, Animation, Missionen, lebendiger Welt und Windows-Spielbuild; beginne jedoch mit Quellenprüfung, Toolpreflight und dem Goldstandard-Vertical-Slice. Ein ZIP ist keine fertige Spielsoftware.

## Pflicht-Lesereihenfolge
1. `CLAUDE.md` und dieser Masterprompt, `START_HIER_V4_1.md`.
2. `GENESIS_CLAUDE_CODE_MASTERPROMPT_V4.md`, `docs/v4/QUELLEN_UND_KANON_SICHERN.md` sowie alle originalen Story-/Script-Lock-Dateien, soweit tatsächlich vorhanden und freigegeben.
3. `docs/v4_1/FREE_AI_SYSTEM.md`, `FREE_AI_TOOL_MATRIX.md`, `FREE_AI_INSTALLATION_POLICY.md`, `FREE_AI_APPROVAL_GATE.md`, `FREE_AI_FALLBACKS.md`, `FREE_AI_OUTPUT_REGISTER.md`, `FREE_AI_PRODUCTION_PIPELINES.md`, `FREE_AI_QA_GATES.md`, `FREE_AI_LICENSE_REGISTER.md`.
4. `config/free_ai_tools.json`, `.claude/agents/`, `.claude/skills/genesis-free-ai-*/SKILL.md`, `tools/v4_1/`.
5. Vollständiges V2/V3/V4-Regelwerk, GAMEFORGE Living World Original-MD unverändert, Kanon- und Bildreferenzvorgaben.

## Phase F0 – Nur prüfen
- Lokale Windows-/GPU-/CUDA-/VRAM-/RAM-/SSD-/CPU-/Blender-/Unreal-/Python-/ComfyUI-/Musik-/TTS-/ASR-Werkzeuge erkennen: `python tools/v4_1/hardware_probe.py --output build_reports/free_ai_hardware.json`.
- Toolmatrix auslesen: `python tools/v4_1/ai_tool_manager.py --hardware build_reports/free_ai_hardware.json --output build_reports/free_ai_selection.json`.
- Lizenzen von **Code, Modellgewichten, Stimmen, Datasets, Audio-/Bild-Outputs und Abhängigkeiten separat** lesen; Quellenlinks, Revision und Lizenzhash ins Register schreiben. Unklare Nutzung als `LICENSE_REVIEW` blockieren.
- Konkrete Pläne pro Werkzeug einschließlich Downloadgröße, Treiber, CUDA und Windows-Support erstellen und den Game Director in DEUTSCH fragen. Bei fehlendem Tool warten oder sichere Alternative anbieten, niemals erfolgreichen Einbau behaupten.

## Phase F1 – Menschliche Toolfreigabe und Installation
- Keine ungeprüften Downloads/Installationen; `tools/v4_1/approval_gate.py` prüft einen protokollierten Einzelfreigabebeleg für die GENAU versionierte Tool-/Gewichtskombination, führt selbst aber keine Installation durch. Der Nutzer muss Downloads/Änderungen einzeln bestätigen; von Claude selbst ausgefüllte Zustimmungen gelten nicht.
- Nach Freigabe ausschließlich vertrauenswürdige offizielle Quellen, festgehaltene Versions-IDs und SHA256 prüfen; jeder Installationsschritt mit Log und Rollback-Plan. Kein Bezahldienst, kein Konto-/Token-Export, keine unkontrollierten Plugin-Verzeichnisse.
- Bereitstellung: GPU-Job-Scheduler, Max-VRAM-Budget, max. ein großes Modell im VRAM, lokale Loopback-API, separate Python-Umgebungen.

## Phase F2 – Produktionspfade, nicht nur Prompts
1. **Bildreferenzen:** Story-/Kanon-ID → Character/Asset DNA (Maße, Silhouette, Farben, Materialien) → freigegebener lokaler Bildgenerator → vorn/seitlich/hinten/Detail mit identischen Merkmalen → Referenzvergleich und Director-Review → registerierter Output. Modelle können bei Mehransichten driften, daher niemals Exaktheit behaupten.
2. **3D:** Freigegebenes Bild-/Modell-Tool → Blender-Blockout / Remesh/Retopologie → UV/PBR → Rig/Morph/Animation nach Bedarf → Blender-Realitätsprüfung + Multiangle → Export → Unreal-Import → Skelettrig-/Kollision-/LOD-/Performance-Tests → QA/Abnahme. TRELLIS optional, keine Pflicht oder Garantien.
3. **Musik:** Musikbibel/Lebens- und Soul-Motive strikt getrennt → Szenen-Cue-Sheet → lokaler Musikgenerator (z. B. ACE-Step) → WAV-Analyse/Originalitäts-/Rechteprüfung → menschliche musikalische Abnahme → Unreal-MetaSounds/Audio-Middleware-Import → Gameplay-Test. KI-Songs nicht mit 'Copyright frei' gleichsetzen.
4. **Stimmen:** Dialogkanon → deutsches Dialogvarianten- und Sprecher-ID-System → legal lizenzierte lokale Stimme/Preview → WAV+Untertitel → Face Rig/Lipsync → kontrollierte menschliche Voice-Abnahme. Piper-Stimmen ausschließlich nach individueller Modellkarten-Prüfung. Ohne freigegebene Endstimmen nur `PREVIEW`.
5. **ASR:** faster-whisper/offene ASR ist Transkriptionshilfe, nicht Stimmgenerierung. Überprüfe Untertitel/Worttimings durch QA.
6. **Unreal:** Ohne reale Editor-Verbindung nicht als importiert bezeichnen; lokale Skripte, Commandlets und bekannte MCPs nur dann verwenden, wenn die laufende Engine sie unterstützt.

## Agentenkoordination
Weiterhin genau die vorhandenen 24 GENESIS-Fachagenten verwenden, keine zweite Agentenplattform; Aufgaben nach `docs/v4_1/FREE_AI_AGENTEN_HANDOFF.md` zuweisen. Nur Produktionsleitung plant; Reference Director, Character Artist, Audio Director, Tool Integration, Rights Curator und QA arbeiten an ihren eigenen Artefakten. Ein aktiver Blender-/Unreal-Editor-Schreibjob zur Zeit. Jeder Job: input_hash, target_asset_id, approved_scope, tool_version, license_evidence, output_sha256, test_log, reviewer, status.

## Status und Definition von FERTIG
`SPEC_ONLY` = geplantes Verfahren; `NOT_INSTALLED` = notwendiges Tool fehlt; `READY` = installiert+lokal getestet+lizenzbewertet; `GENERATED_PREVIEW` = nachweisbares Modellresultat; `BLENDER_VALIDATED` = überprüfte Blend-Datei; `UNREAL_VALIDATED` = Engine-Import nachgewiesen; `ACCEPTED` = unabhängige QA UND Nutzerabnahme. Nie als 'alle kostenlosen KIs installiert' melden, solange keine realen Prüfprotokolle vorliegen.

## Vollständige Produktion, nicht mit Demo enden
Goldstandard-Region 2026 zuerst. Danach anhand bestätigter Kanon-/Asset-/Missionslisten alle weiteren Regionen, Kapitel C00–C21, Lebensphasen, Mensch-/Fahrzeug-/Umweltassets, Dialoge, Musik und Mechaniken abarbeiten, stets pro Feature mit neuen QA-Gates. Bei fehlendem Script-Lock, unklarer C15/C16-/C21-Regel, fehlendem Budget oder Freigabe blockieren und konkrete Entscheidung anfordern. Nicht eigenmächtig erfinden. Keine garantierte AAA+-Qualität oder autonome Hintergrundarbeit ohne laufende Claude-Code-Session/Job-Scheduler behaupten.

## Erste sofort ausführbare, risikofreie Tätigkeit
`python tools/v4_1/hardware_probe.py --output build_reports/free_ai_hardware.json`
`python tools/v4_1/ai_tool_manager.py --hardware build_reports/free_ai_hardware.json --output build_reports/free_ai_selection.json`
Lies die Ausgaben, prüfe alle vorhandenen Quellen und zeige mir auf Deutsch: INSTALLIERT / INSTALLATION NACH FREIGABE / LIZENZ UNGEKLÄRT / HARDWARE UNGEEIGNET. Beginne erst danach die konkrete Toolinstallation nach Einzelfreigabe.
