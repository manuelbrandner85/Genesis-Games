# Orchestration: Scheduler und Fehlerbehandlung

- Ein GPU Worker, idempotente Jobs: `DISCOVER -> REVIEW -> APPROVE -> INSTALL -> SMOKE -> GENERATE -> VERIFY -> INTEGRATE -> QA -> ACCEPT`.
- Wenn Claude-Code-Limit, Rechnerabsturz oder GPU-OOM: Job `PAUSED/BLOCKED`, Artefakt-SHA behalten, nach Neustart Hardware und Lizenz erneut vergleichen; kein automatischer Retry-Loop mit Kosten.
- Jede Agentenantwort enthält konkrete Dateien und Messwerte, keine '100% perfekt'-Behauptung.
- Trenne Entwicklungsdaten von ausgeliefertem GENESIS-Savegame; keine permanenten Cloud-KI-Abhängigkeiten im Spiel.
- Prioritäten: Lesbarkeit/Kanon -> guter Vertical Slice -> hochwertiger Hero-Charakter -> echte Animationen -> richtige Dialoge/Musik -> stabile Welt -> skalierte Produktion.
- Workflow-Timeouts, GPU-VRAM und Disk-Nutzung messbar konfigurieren, keine erfundenen Maximalzahlen.
