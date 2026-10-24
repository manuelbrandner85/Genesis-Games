# V4.2-Ordner – Cinematic & Menu Experience

- `SCENE_MATRIX_C00_C21.json`: IDs/Arbeitstitel, keine Original-Drehbuchquelle
- `MENU_FLOW.json`: Menügraph als Umsetzungsvorgabe
- `QA_ACCEPTANCE.md`: 50 reale Abnahmepunkte
- `AUDIO_MUSIC_CUE_SPEC.md`: Cue-/Voice-/Soul-Regeln
- `IMPLEMENTATION_GUIDE.md`: Unreal-/C++-/Blueprint-Vorschlag
- `WORK_ORDERS.csv`: 26+ konkrete WorkIDs
- `AGENT_JOB_HANDOFF.md`: vorhandene Agenten-Rollen
- `TECHNICAL_NOTES.md`: offizielle Unreal-Referenzen

**CLI vor lokalem Engine-Test:** `python tools/v4_2/validate_cinematic_bundle.py` und `python -m unittest discover -s tools/v4_2 -p 'test_*.py'`. Beides ersetzt niemals Build- oder Kreativabnahme.
