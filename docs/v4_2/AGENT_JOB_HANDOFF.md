# V4.2 – Verantwortlichkeiten & WorkIDs

| Rolle | Verantwortlich | Übergabe |
|---|---|---|
| genesis-master-director | Abhängigkeiten, Prioritäten, Freigaben, Scope-Guard | CM0→CM9 WorkID-DAG |
| genesis-script-guardian | Source Lock, C00/C20, Spoiler, Storykonflikte | Original-Hashes, freigegebene Shotliste |
| genesis-cinematic-director | Sequencer/CineCamera/Render/Skip-Callbacks | LevelSequence und Audio/Shot-Bericht |
| genesis-ui-accessibility | UMG/Controller/Hauptmenü, Load/Settings | UI-Graphs, Engine-Fokus-Test |
| genesis-audio-director | Musik/Voice/Submix/Untertitel | Cue-Register/WAV/Lizenzen |
| genesis-face-voice-sync | Lippen/Mimik/Voice Alignment | Face-rig Testclips + QA |
| genesis-unreal-core | C++ Subsystems Save, Cinematic State, UI | Compile/PIE/Standalone Beleg |
| genesis-reference-director | Canon-konsistente Set- und Figur-Referenzen | Asset DNA + Genehmigung |
| genesis-qa-release | Unabhängige Abnahme + Windows-Cook/Build | checkbare Reports, keine Selbstfreigabe |

Übergabevertrag je Task: `work_id`, `scene_id` optional, `source_hash`, `input_artifact_ids`, `expected_output_ids`, `branch`, `files_owned`, `approval_token_reference`, `acceptance_test_ids`, `evidence_paths`, `status`, `next_role`. StudioBrain wiederverwenden, sofern real vorhanden. Keine neue Agentenverwaltung.
