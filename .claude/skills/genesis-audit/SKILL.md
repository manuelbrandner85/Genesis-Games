---
name: genesis-audit
description: Read-only Ausgangslage und Quelleninventur für das bestehende GENESIS-Spiel. Nutze diesen Skill bei einem entsprechenden Produktionsauftrag.
---

# /genesis-audit

Inventarisiere Git-Basiscommit, UE-Projektdatei, EngineAssociation, Skriptstände, G0-Blocker, GAMEFORGE 01/02 und Agenten. Nutze `tools/pipeline/preflight.py` wenn Python lokal vorhanden. Lege ausschließlich einen Bericht an; keine Produktionsdateien anfassen.

### Vor dem Abschluss
Quelle und freigegebene Entscheidungen prüfen; echte geänderte Dateien/Tests auflisten. Falls andere Rollen berührt sind, nächsten vorgesehenen Agenten benennen. Jede nicht verfügbare Quelle/Toolleistung als `BLOCKED`, jede reine Vorbereitung als `PLANNED`/`BUILT_UNTESTED` markieren.
