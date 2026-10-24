# FREE AI SYSTEM – Architektur

## Ziel
Ein zentraler Produktionsrouter für Bild, 3D, Musik, Sprache, ASR und Standard-3D/UE. Vorhandene lokale Fähigkeiten einsetzen, sonst blockieren oder Alternativen anbieten. GENESIS-Zukunftswelt ab 2026, Leben/Jenseits/Rebirth und C00–C21 bleiben unverändert.

## Design
`Director Auftrag -> Kanon-/Asset-ID -> Tool Registry -> Hardware/Cost/License Validator -> Human Approval -> Local Runtime Adapter -> Output Verification -> Asset Provenance -> Blender -> Unreal -> QA.`

**Die 24 GENESIS-Rollen bleiben:** keine neuen Prozesse per Rollebeschreibung, keine zweite Jobdatenbank; bei vorhandenem StudioBrain dessen Jobs und Gate-Status verwenden. Das JSON-Toolregister ist eine deklarative Startvorlage, kein Installationsnachweis.

## Softwarekomponenten
- `config/free_ai_tools.json`: Katalog mit Quellen, Grenzen, Lizenzen und Features.
- `tools/v4_1/hardware_probe.py`: read-only Hardware-/Software-Inventar.
- `tools/v4_1/ai_tool_manager.py`: Auswahlmatrix und Hardwarefilter.
- `tools/v4_1/approval_gate.py`: erforderliche Menschfreigabe gegen präzisen Plan (Sicherheits-Hinweis: keine kryptografische Authentifizierung).
- `tools/v4_1/comfyui_local.py`: kontrollierter ComfyUI-Request an lokale Loopback-API; keine Cloud.
- `tools/v4_1/asset_register.py`: echte Datei-Hashes und Provenienz.
- `tools/v4_1/audio_quality.py`: WAV-Mindestprüfung; kein künstlerischer Qualitätsersatz.
- `tools/v4_1/blender_turnaround.py`: Blender-bpy Multiangle eines tatsächlich vorhandenen .blend-Projekts.
- `tools/v4_1/validate_package.py`: Projektpaket-/Quellenchecks.

## Ressourcen
Immer ein großer GPU-Generator zur selben Zeit, VRAM-/RAM-/Disk-Wachstum prüfen. WSL/Linux nur bei vollständig geprüften GPU-Treiber-/CUDA- und Lizenzbedingungen. Download- und Installationsschritte NICHT implizit bei der Hardwareprüfung ausführen.

## Steuerung
Keine 'Autonomer Dauerdienst'-Behauptung ohne aktive lokale Prozess-/Jobinfrastruktur. Claude Code arbeitet während der tatsächlichen Ausführung; das Spiel zur Laufzeit benötigt **keine Cloud-KI oder laufenden Claude-Prozesse**.
