---
name: genesis-agent-map
description: GENESIS-Rollen an bestehende GAMEFORGE-Agenten anbinden für das bestehende GENESIS-Spiel. Nutze diesen Skill bei einem entsprechenden Produktionsauftrag.
---

# /genesis-agent-map

Prüfe den existierenden GAMEFORGE-StudioBrain-Agentenkatalog. Mappe 24 GENESIS-Rollen auf vorhandene 42 Rollen; `.claude/agents` sind Fallbacks und keine 24 zusätzlichen Dauerprozesse. Gib eine tabellarische Rollen-/WorkID-Zuordnung und Editor-Exklusivität an.

### Vor dem Abschluss
Quelle und freigegebene Entscheidungen prüfen; echte geänderte Dateien/Tests auflisten. Falls andere Rollen berührt sind, nächsten vorgesehenen Agenten benennen. Jede nicht verfügbare Quelle/Toolleistung als `BLOCKED`, jede reine Vorbereitung als `PLANNED`/`BUILT_UNTESTED` markieren.
