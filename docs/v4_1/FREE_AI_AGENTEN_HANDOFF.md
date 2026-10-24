# Aufgabenverteilung für die bestehenden 24 GENESIS-Agenten

- `genesis-master-director`: WorkID, Kanonprüfung, Einzelfreigaben, Pipeline-Reihenfolge, keine Parallel-GPU-Jobs.
- `genesis-tool-integration`: Hardwareinventur, lokale Modelle/Versionen, freigegebene Installations-/ComfyUI-/Blender-/UE-Anbindung.
- `genesis-asset-licensing`: Modelle, Stimmen, Datasets, Code, Fremdassets und spätere Veröffentlichung getrennt prüfen.
- `genesis-reference-director`: kanonische Motiv- und Turnaround-Briefs/IDs, Referenzvergleich und Director-Freigabe.
- `genesis-character-artist`, `genesis-rigging-specialist`, `genesis-pbr-specialist`, `genesis-motion-specialist`: aus freigegebenen Referenzen echte Blender-/UE-Figuren und Animationen mit Logs produzieren.
- `genesis-audio-director` & `genesis-face-voice-sync`: Motive/Cues/Musik/Mix, deutsche Sprecher-/Dialogvarianten und Face-Rig-Lipsync.
- `genesis-environment-artist` & `genesis-open-world`: PBR/3D-Umwelt und World Partition, nie unkontrolliert tausende AI-Assets erzeugen.
- `genesis-cinematic-director` und `genesis-script-guardian`: C00–C21 geschützt; ohne vollständigen Kanon keine finale Filmszene.
- `genesis-unreal-core` und `genesis-qa-release`: echter Import, Rendering/PIE, Windows-Testbuild und evidenzbasierte QA.
- Alle übrigen Agenten behalten ihre V4-Zuständigkeit. Keine 24 Hintergrundprozesse als bereits installiert behaupten; es handelt sich um auswählbare Claude-Code-Unteragenten-Konfigurationen.

**Jobvertrag**: `WorkID + AssetID + CanonHash + ModelID + ModelLicense + ApprovalPlanHash + InputHashes + OutputHashes + LocalToolLog + QAStatus`. Konflikt zwischen Story und generativer Ausgabe: Generatorausgabe verwerfen, nie Story überschreiben.
