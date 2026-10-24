# Kurzkommandos (im entpackten Übergabeverzeichnis)

1. `python tools/v4_1/hardware_probe.py --output build_reports/free_ai_hardware.json`
2. `python tools/v4_1/ai_tool_manager.py --hardware build_reports/free_ai_hardware.json --output build_reports/free_ai_selection.json`
3. `python tools/v4_1/validate_package.py`
4. `python -m unittest discover -s tools/v4_1 -p test_free_ai.py -v`
5. Nur nach menschlich bestätigter Pfad-/Lizenzfreigabe: `python tools/v4/init_new_game.py --target "C:\Games\GENESIS-NEW" --engine-association <INSTALLED_UE_VERSION>` als Dry-Run, danach eventuell `--apply`.
6. ComfyUI: `python tools/v4_1/comfyui_local.py --workflow <API_WORKFLOW.json>` nur lokal prüfen; nach Modellfreigabe zusätzlich `--submit`. `python tools/v4_1/comfyui_results.py --prompt-id <id> --output-dir <folder>` nach nachweislicher Jobfertigstellung.
7. Piper: `python tools/v4_1/piper_preview.py --binary ... --model ... --model-card ... --text-file ... --output ...` (Dry-Run). `--execute` nur nach Voice-Gewichtsfreigabe und überprüfter lokaler CLI-Kompatibilität.
8. Artefakt registrieren: `python tools/v4_1/asset_register.py --file <file> --asset-id <id> --tool-id <tool> --model-id <model> --source-ref <source> --license-ref <license> --registry <evidence.jsonl>`.

**Vollständige Game-Produktion:** Originalquellen prüfen → neue C++-Projektstruktur → lokale Tools installieren (genehmigt) → Goldstandard-Spielregion → restliche GENESIS-Kapitel/Missionen/Assets/Spielsysteme → Windows-Release-Gate. Kein automatischer Abschluss durch diesen Pakettest.
