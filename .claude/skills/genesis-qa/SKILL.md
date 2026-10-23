---
name: genesis-qa
description: Unabhängige Regression und Qualitätsgates für das bestehende GENESIS-Spiel. Nutze diesen Skill bei einem entsprechenden Produktionsauftrag.
---

# /genesis-qa

Prüfe nur existierende Tests/Logs; statische Paketsyntax via `tools/qa/verify_package.py` ist kein UE-Gameplaynachweis. Erzeuge Fehler-WorkIDs für blockierte/laufende Tests, messe mit UE Insights falls verfügbar und genehmige ACCEPTED nur mit Belegen.

### Vor dem Abschluss
Quelle und freigegebene Entscheidungen prüfen; echte geänderte Dateien/Tests auflisten. Falls andere Rollen berührt sind, nächsten vorgesehenen Agenten benennen. Jede nicht verfügbare Quelle/Toolleistung als `BLOCKED`, jede reine Vorbereitung als `PLANNED`/`BUILT_UNTESTED` markieren.
