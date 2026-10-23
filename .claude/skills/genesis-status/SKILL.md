---
name: genesis-status
description: Produktionsübersicht aus tatsächlichen Jobbelegen erzeugen für das bestehende GENESIS-Spiel. Nutze diesen Skill bei einem entsprechenden Produktionsauftrag.
---

# /genesis-status

Lies `docs/production-status` oder den bestehenden StudioBrain-Jobstore read-only. Führe `tools/qa/render_status.py` für HTML mit echten Statuswerten aus. Keine erdachten Agenten-Livezahlen, FPS oder Prozentfortschritte.

### Vor dem Abschluss
Quelle und freigegebene Entscheidungen prüfen; echte geänderte Dateien/Tests auflisten. Falls andere Rollen berührt sind, nächsten vorgesehenen Agenten benennen. Jede nicht verfügbare Quelle/Toolleistung als `BLOCKED`, jede reine Vorbereitung als `PLANNED`/`BUILT_UNTESTED` markieren.
