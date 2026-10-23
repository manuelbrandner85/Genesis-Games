# GENESIS – Verbesserung 10: Production Command Center

**Bestätigt:** JA zu allen zehn Verbesserungen am 23.10.2026.
**Status:** geplanter, fachlich freigegebener Entwicklungsumfang; keine hier erfolgte UE-Implementierung.
**Leitziel:** Ein deutsches, quellengenaues Fortschritts- und Diagnosezentrum ohne Fantasiedaten.
**Gültigkeit:** nur bestehendes `manuelbrandner85/Genesis-Games`, Claude Code als Entwicklungsleitung, keine Story-Umschreibung.

### Produktionsfunktionen
1. Konsolidierter Read-only View auf GAMEFORGE-StudioBrain-Jobdaten, Agentenstatus und GENESIS-Artefakte, wenn echte Quelle verfügbar.
2. Offline-Fallback: JSON/CSV-Workorders und Testberichte, beschriftet als lokaler Snapshot.
3. Status je WorkID: `PLANNED`, `RUNNING`, `BLOCKED`, `WAITING_APPROVAL`, `VERIFIED`, `ACCEPTED`, mit Grund und Zeitstempel.
4. Agentenliveanzeige nur aus echten Hook-Logs/SubagentStart/SubagentStop; keine erfundenen online-Anzeigen.
5. Asset-Funnel: Referenz → Modell → Export → Import → Validierung → QA → Freigabe, inkl. Pfad/Hash.
6. UE-Logs und tatsächliche Build-/PIE-/Insights-Artefakte als Link, kein fiktiver FPS-Wert.
7. Gesonderter Kanon-/Lizenz-/Kosten-Blocker-Tab mit offenen Freigaben.
8. Assetdiff/Storydiff zum letzten freigegebenen Branch anzeigen, inklusive betroffener WorkIDs.
9. Einfache Nutzerführung auf Deutsch: „Was ist fertig?“, „Was wird gebaut?“, „Was fehlt?“, „Was soll ich entscheiden?“.
10. Grenzen: Lokale HTML-Vorschau darf keine Behauptung über aktive Claude-Engine/Blender-Verbindung machen.
11. Dashboard dient Auswertung, nicht zweite Produktionsteuerung oder konkurrierende Job-DB.
12. Exportierbarer JSON/HTML-Bericht mit Snapshotzeit und Evidenzpfaden.

### Lieferbestand
`tools/qa/render_status.py` erzeugt aus tatsächlichen belegten `docs/production-status/*.json` eine lokale HTML-Statusseite. Ohne Statusdaten erscheint ein leeres/„Keine Ergebnisse“-Dashboard. Sicherheitsgate: Nur lesender Generator, nie ungefragt senden/veröffentlichen.

### Technischer Produktionsauftrag
Arbeite mit dem vorhandenen Repo, GAMEFORGE StudioBrain und Character Creation 4.0, sofern tatsächlich vorhanden. Ermittle Basiscommit, freigegebene Quellen und installierte Werkzeuge. Dokumentiere Architektur, konkrete Dateien, Tests und Evidenz. Führe nur genehmigte ungefährliche Schritte aus; für riskante Änderungen explizite Freigabe. Übergebe jeden Arbeitsschritt an unabhängige QA. `NOT_IMPLEMENTED` bleibt sichtbar, bis ein echter Editor-/Runtime-Nachweis vorliegt.

### Datenmodell und Integrationsarchitektur
`JobSnapshot`: WorkID, Typ, Owner, Dependencies, Started/Updated, Status, Exit-Code, Evidence-Links, SourceHashes und Approval-Hinweis. `AssetSnapshot`: ASSET-ID, Referenzstand, Blender-Master, UE-Asset-Pfad, QA-Gate, VisualReview. `ToolSnapshot`: gemessene zuletzt erfolgreiche Blender-/UE-/MCP-Prüfung mit Zeitstempel statt bloß `connected=true` aus Konfiguration. `PerformanceSnapshot`: HardwareID, UE-Version, Map/Scenario, Frame/GPU/Memory/Sim-Zahlen und Trace-Path. Ohne echte Quelle zeigt UI „Keine Daten“.

**Oberfläche:** links Projekt/Region/Produktion; zentral chronologische WorkIDs und Assets; rechts offene Abnahmen/Blocker. Suchbare Filter nach Story, 3D, Unreal, QA, Rechte. Nutzer sieht in Deutsch nur verständliche Statusbegriffe; Klick auf Asset führt zu Bild/Log/Hash, nicht zu einer Dummy-Aktion. Die HTML-Snapshotvorlage in `tools/qa/render_status.py` ist bewusst minimal und offline; Echtzeitstatus benötigt einen tatsächlich vorhandenen StudioBrain-Eventfeed. Keine zweite Jobsteuerungsdatenbank.

**Ereignisverarbeitung:** `SubagentStart/Stop`, BuildStarted/Finished, ArtifactReady und QACompleted nur aus bestätigten Logs zu Snapshots komprimieren. Der mitgelieferte PostToolUse-Hook loggt minimal; er dokumentiert **nicht** automatisch Blender-/Unreal-Build-Erfolg. Der Dashboard-Refresh darf keine API-Downloads/Kosten verursachen und keine Logs an Dritte senden.

**QA-Fälle:** A1 leere Quelle zeigt „Keine Daten“; A2 fehlender Build bleibt NOT_RUN; A3 Evidence-Klick öffnet existierende Datei; A4 Status nur aus belegtem Job; A5 Agentenabbrüche werden nicht als DONE gezeigt; A6 Source-/Kanon-/Lizenzwarnungen sichtbar; A7 keine Performancezahl ohne Hardware/Trace; A8 Exportdaten reproduzierbar und privat gespeichert.

### Abhängigkeiten / nächste Umsetzung
Die minimale lokale Statusseite ist gebaut und statisch getestet; live Web-App/StudioBrain-Integration ist noch nicht durchgeführt. WorkIDs dürfen erst nach Architektur-/Kanonabgleich in reale Dateiedits umgesetzt werden.
