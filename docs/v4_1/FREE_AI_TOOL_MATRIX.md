# FREE AI TOOL MATRIX – aktuelle Kandidaten, keine Vorinstallation

| Kategorie | Werkzeug | Code-/Gewichtsrecht (getrennt prüfen!) | Hardware / Windows | Integration | Stand im ZIP |
|---|---|---|---|---|---|
| Bild-GUI | ComfyUI | GPL-3.0 Code; jedes Modell separat | Win/Linux, GPU abhängig | lokale HTTP/Workflow-API | Adapter, nicht installiert |
| Bildmodell | FLUX.1 schnell | Gewichte Apache-2.0, kommerzielle Nutzung prinzipiell zulässig | sehr speicherintensiv, Quantisierung optional mit Zusatzlizenzen | ComfyUI / Diffusers | nur Plan |
| Bildmodell | FLUX.1 dev | Nicht-kommerzielle Modelllizenz; standardmäßig **BLOCKIERT** | GPU abhängig | nur nach gesonderter Rechteprüfung | nicht enthalten |
| 3D-Startmesh | Microsoft TRELLIS | Mehrheit Code/Gewichte MIT; einzelne Submodule anders | offizieller Mindestbedarf 16GB NVIDIA GPU; Linux getestet, Windows nicht stabil garantiert | separater 3D-Generator → Blender | optional / nur nach Prüfung |
| Music | ACE-Step 1.5 | Repo MIT; exaktes Gewichtsmodell, Abhängigkeiten und Musikähnlichkeit prüfen | verschiedene VRAM-Profile, große Varianten >12GB | lokale CLI/ComfyUI nach Validierung | Szenen-/Cue-Spec, nicht installiert |
| Voice Preview | Piper | Codebasis/Version prüfen; JEDE Stimme hat eigene Modellkarte/Lizenz | lokal, meist CPU-fähig | WAV → Lippen-/Subtitle-Pipeline | nicht installiert |
| Voice alternative | Menschlich aufgenommene Voice / selbst produzierte Demo | Sprecher-Einwilligung/Performance und Soundrechte | Aufnahmehardware | WAV importiert → Unreal | als Fallback |
| Speech-to-Text | faster-whisper | MIT Code; ASR-Gewichte separat bewerten | CPU/GPU verschiedene Profile | Transkription/Untertitel | nicht installiert |
| Modeling | Blender | GPL-Code (Wiedergaberechte erzeugter Werke separat) | lokal vorhanden prüfen | .blend → FBX/GLB | Test-/QA-Skripte |
| Runtime | Unreal Engine 5 | Epic EULA je Nutzungsart prüfen; kein 'kostenlos frei lizenziert' | installierte Version prüfen | C++/Editor-Import | V4-Projektgerüst |
| Audioschnitt | Audacity | GPL; Soundquellen selbst klären | Windows/Linux | WAV Editing | optional |
| Krita | Krita | GPL; Bilderrechte getrennt | Windows/Linux | Referenzretusche | optional |

**Standardmäßig gesperrt:** unbekannte Hugging-Face-Repos, FLUX-dev für kommerzielle Produktion ohne ausdrückliche Nutzungsrechtsprüfung, ungeprüfte TRELLIS-Abhängigkeiten, fremde Sprecherstimmen ohne Rechte, nicht genehmigte bezahlte APIs. Modelldateien/Gewichte müssen versioniert und mit Quellen und SHA erfasst werden.

**Offizielle Quellen (Stand der Recherche 24.10.2026):**
- https://github.com/Comfy-Org/ComfyUI
- https://huggingface.co/black-forest-labs/FLUX.1-schnell
- https://github.com/black-forest-labs/flux
- https://github.com/microsoft/TRELLIS
- https://github.com/ace-step/ACE-Step-1.5
- https://github.com/rhasspy/piper (ältere MIT-Variante; Forks können andere Lizenzen haben)
- https://github.com/OHF-Voice/piper1-gpl (aktuelle GPL-Variante)
- https://huggingface.co/rhasspy/piper-voices
- https://github.com/SYSTRAN/faster-whisper
- https://github.com/blender/blender
- https://www.unrealengine.com/en-US/eula/unreal
