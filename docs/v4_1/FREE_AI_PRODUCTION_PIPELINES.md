# FREE AI: KONKRETE PRODUKTIONSPIPES

## Referenzen (ein Character Asset)
1. `AssetID`, C00–C21-Story-/Figurenfreigabe, Lebensalter, Geschlecht/Genetik nach genehmigter Originalquelle, Maßstab, Materialien, Perspektiven.
2. Genehmigten Bildworkflow in ComfyUI/API-Format erstellen; nur auf lokalem 127.0.0.1-Endpunkt ausführen. `python tools/v4_1/comfyui_local.py --workflow <exportierte_api_workflow.json> --dry-run` validiert; `--submit` sendet an laufendes lokales ComfyUI (führt noch keinen Bilder-Download durch).
3. Front, Back, Side, 3/4 und Detail getrennt rendern/prüfen; prompt/seed/Modellversion dokumentieren. Unterschiedliche Ansichten aus reinem Text garantieren KEINE gemeinsame 3D-Konsistenz: visuell/messbar nacharbeiten.
4. Gesegnetes Reference Board plus Maßdaten → Modeler.

## 3D
Referenzboard → Blender-Mesh/retopo/UV/PBR/rig → `.blend` + prüfbarer GLB/FBX-Export → `python tools/v4_1/blender_turnaround.py --help` [im Blender-Prozess] → Unreal-Import durch tatsächlich gestarteten UnrealEditor, FBX-/GLB-Kompatibilität prüfen → realer PIE/Standalone-Test. TRELLIS liefert nur Kandidaten; Anatomie, Topologie, LODs und UV sind NICHT automatisch vollwertig.

## Musik
Bibel-gebundene Cues mit Ziel: Szene, Emotion, Länge, BPM, Tonart, separate Lebens-/Soul-Motive, darf nicht fremde Melodie kopieren. ACE-Step lokal nach Freigabe/Installation ausführen, tatsächliche WAV-Datei prüfen: `python tools/v4_1/audio_quality.py --input <datei.wav>`. Erst nach Ähnlichkeits-/Rechte-/Qualitätsprüfung nach Unreal. Keine generische AAA+-Abnahme aus Messwerten.

## Stimme/ASR
Abgenommene deutsche Dialogvariante → Sprecher-ID + lizenzierte Stimmkarte → Piper oder echte Schauspielaufnahme; tatsächliches WAV, Untertitel und Timecodes. ASR z.B. faster-whisper dient Transkriptionscheck, kein Face-Lip-Sync; dieser braucht separate Face-Rig-/Audiopipeline und menschengeprüfte Aussprache.

## Unreal
Niemals ein Asset allein durch das Erstellen einer FBX als 'Engine-Import fertig' markieren. Verlange Importlogs, Dateipfad im Unreal Content Browser, Skeleton/Materials/Collision/LOD-Checks und Render-/PIE-Aufnahme. Baue erst eine abgenommene Spielregion und danach – per WorkID, Abnahme und Regression – das komplette Spiel.

## Laufende lokale Ausgaben

- ComfyUI sendet nach `--submit` nur eine Job-ID. Mit `python tools/v4_1/comfyui_results.py --prompt-id <ID> --output-dir assets/free_ai_previews` liest Claude später den tatsächlich abgeschlossenen lokalen Job aus und speichert die Bilder mit `DOWNLOADED_UNREVIEWED`.
- Piper PREVIEW nur nach Installation und persönlicher Stimme-Modellkarte: `python tools/v4_1/piper_preview.py --binary <piper> --model <voice.onnx> --model-card <MODEL_CARD> --text-file <approved_dialog.txt> --output <preview.wav>` (dry run). `--execute` produziert ein WAV bei passender CLI-Version, markiert es niemals als finale Schauspielaufnahme.
