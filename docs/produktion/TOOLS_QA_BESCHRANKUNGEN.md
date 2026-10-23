# Tool- und Sicherheitsgrenzen der Lieferung

### Getestet im Erstellungscontainer (ohne Unity/Unreal/Blender)
- Statische Prüfung von JSON/CSV/Python/Dateibestand/Original-MD-Hash.
- Python-Validator für die Asset-Manifeste.
- Python-Statusreport aus leerem/vorhandenem Quellen-JSON.
- Installer-Dry-run und Copy-no-overwrite in einem künstlichen lokalen Testrepo (nur falls Testskript wirklich ausgeführt wurde).

### Nicht hier durchführbar
- Windows PowerShell Hook-Ausführung in installiertem Claude Code (sofern PowerShell/Claude nicht vorhanden).
- `/agents`, `/skills`, `/mcp` in einer echten Claude-Sitzung und Zugriff auf den Windows-PC.
- Blender `.blend` Master-/Face-/Skeleton-/High-Poly-Qualität und Renderings.
- Unreal Editor/Python/AssetRegistry, PIE, Build, reale UE-Maps, World Partition, FPS/VRAM/Insights.
- Produktionsfreigabe der vollständigen Originalbibel und des Skripts C00–C21/J00–J24, die als Originaldateien im Paket fehlen.

**Direkte Folge:** Der Status für reale Entwicklungsarbeiten bleibt `PLANNED`/`NOT_RUN`. Die Tests sind nicht „schon erledigt“, weil die Scripts im ZIP existieren. Die Rolle QA hat unabhängig zu verifizieren.
