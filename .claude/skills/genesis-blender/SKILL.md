---
name: genesis-blender
description: Blender-Assetprüfung und Turnaround-Render durchführen für das bestehende GENESIS-Spiel. Nutze diesen Skill bei einem entsprechenden Produktionsauftrag.
---

# /genesis-blender

Prüfe zuerst Blender-CLI und `.blend`-Master. Führe `tools/blender/asset_audit.py` oder `tools/blender/render_turnaround.py` durch, nur wenn Blender lokal verfügbar. Speichere Logs/Bilder im Evidence-Ordner. Kein erdachtes Blender-Tool/Resultat.

### Vor dem Abschluss
Quelle und freigegebene Entscheidungen prüfen; echte geänderte Dateien/Tests auflisten. Falls andere Rollen berührt sind, nächsten vorgesehenen Agenten benennen. Jede nicht verfügbare Quelle/Toolleistung als `BLOCKED`, jede reine Vorbereitung als `PLANNED`/`BUILT_UNTESTED` markieren.
