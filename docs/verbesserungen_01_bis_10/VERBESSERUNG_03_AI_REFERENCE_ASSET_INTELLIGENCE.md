# GENESIS – Verbesserung 03: AI Reference & Asset Intelligence

**Bestätigt:** JA zu allen zehn Verbesserungen am 23.10.2026.
**Status:** geplanter, fachlich freigegebener Entwicklungsumfang; keine hier erfolgte UE-Implementierung.
**Leitziel:** Eine quellenbasierte Referenzbibel, damit Modelle, Gebäude, Fahrzeuge, Menschen und Requisiten konsistent bleiben.
**Gültigkeit:** nur bestehendes `manuelbrandner85/Genesis-Games`, Claude Code als Entwicklungsleitung, keine Story-Umschreibung.

### Produktionsfunktionen
1. Jedes Asset bekommt stabile `ASSET-ID`, Benennung, Funktion im Spiel, Kanonquelle, Zuständigkeit, Freigabezustand.
2. Für Charaktere 6 Standardansichten + Gesicht/Mimik; für Gebäude Grundriss/Höhen/Ansichten; für Fahrzeuge Front/Seite/Heck/Interieur; für Props 4 Ansichten/Explosionsdetail nach Bedarf.
3. 1:1 Maßreferenz mit metrischem Ruler; Unreal 1 unit=1 cm, Blender Szene in Meter, Exportscale dokumentieren.
4. Konsistenzblatt für Form, Material, Farbwerte, Gebrauchsspuren, Baujahr, kulturelle Details und Storybedeutung.
5. Perspektivkorrektheit: Ansichten müssen dasselbe Objekt zeigen; unklare KI-Mehransichten werden nicht ungeprüft zur 3D-Modellierung benutzt.
6. Referenzquellen unterscheiden: Original-GENESIS, lizenzierte Fotografie, selbst gezeichnet, generativ; genaue Herkunft und Nutzungsrecht.
7. Nur belegte Designregeln übernehmen; Szenenvarianten aus C00–C21 nicht durch frei erfundene Gestaltung ersetzen.
8. Style Bible: 2026 glaubwürdig und fotorealistisch, kein unmotiviertes Sci-Fi/Fantasy-Design in alltäglichen GENESIS-Szenen.
9. Werkbank: Blender-Kamera-Skript für reale Ansichten bestehender Geometrie, Framing identisch und reproduzierbar.
10. Referenz-Lock: nach Freigabe Revision erstellen statt unerkannt ändern.
11. Similarity QA: Silhouette, Maße, Landmarken, Materialien, Anschlüsse; kritische Abweichungen als Delta mit Screenshot.
12. Assets mit nicht vorhandenem Bildmaterial: `WAITING_REFERENCE` statt vorgespielter Bilderzeugung; Claude Code hat nicht automatisch einen Bildgenerator.
13. Leistungs-/LOD- und Lizenz-Felder sind Pflichtbestandteil der Assetbibel.
14. Referenz-zu-Import-Rückverfolgbarkeit: Foto/Sheet → `.blend` → Export → `.uasset` → Spielszene → QA-Beleg.

### Output
`templates/asset_manifest.example.json`, `docs/produktion/REFERENZ_BIBEL_STANDARD.md`, `tools/blender/render_turnaround.py` und Versions-/Hash-Index. Automatische Qualitätsbewertung darf `CHECK_REQUIRED` melden und braucht bei einzigartigen Assets menschliche Sichtabnahme.

### Technischer Produktionsauftrag
Arbeite mit dem vorhandenen Repo, GAMEFORGE StudioBrain und Character Creation 4.0, sofern tatsächlich vorhanden. Ermittle Basiscommit, freigegebene Quellen und installierte Werkzeuge. Dokumentiere Architektur, konkrete Dateien, Tests und Evidenz. Führe nur genehmigte ungefährliche Schritte aus; für riskante Änderungen explizite Freigabe. Übergebe jeden Arbeitsschritt an unabhängige QA. `NOT_IMPLEMENTED` bleibt sichtbar, bis ein echter Editor-/Runtime-Nachweis vorliegt.

### Referenzdaten und unveränderliche Rückverfolgung
Das Register `asset_index.json` referenziert `source_document_sha256`, `artist_brief_revision`, `generated_image_source`, `approved_reference_sha256`, Blender- und UE-Asset-IDs. Jede Referenzdatei hat Bildformat, Auflösung, Sichtachse, Brennweitenannahme, Maßreferenz, Lizenz und eine Anmerkung zu optischen Unsicherheiten. Die Verknüpfung ist bi-direktional: Von der UE-Requisite führt ein Pfad zurück zu einer genehmigten Ansichtsrevision.

**Prinzip korrekter Perspektiven:** Ein allein aus Text erzeugtes KI-Bild kann Perspektiven miteinander vermischen, asymmetrische Merkmale löschen oder Texturdetails verfälschen. Daher nicht sechs unabhängige Bilder als geometrisch identisch behandeln. Bevor Blender Details modelliert, muss der Reference-Director das Objekt mit drei anatomisch/architektonisch konsistenten Basisansichten plus Maßblatt plausibilisieren. Echte Blender-Turnarounds entstehen erst **nach** einer Grundgeometrie und dienen der Validierung, nicht als Ersatz für Originalkonzeptbilder.

**Auftragsvertrag:** `ASSET-ID`, `scene_id`, `reference_revision`, `angles`, `dimensions`, `fixed_landmarks`, `editable_features`, `materials`, `context`, `license`, `reviewer`, `status`. Wenn Fotos/Gegenstände geschützt sind, Rechte und Marken korrekt klären. Unterschiedliche Bildgenerationen niemals ohne ausdrückliche dokumentierte Rückführung zu einer neuen Designrevision zusammenführen.

**QA-Fälle:** A1 alle Pflichtansichten vorhanden; A2 Skala stimmt; A3 fixierte Landmarken gleich; A4 keinerlei Bildquelle fälschlich als Eigenproduktion markiert; A5 Blender-3D-Rendervergleich enthält Screenshots; A6 Referenzänderung löst abhängige Qualitätsprüfung aus; A7 keine Freigabe ohne echte visuelle Owner-Abnahme.

### Abhängigkeiten / nächste Umsetzung
Die Datenkontrakte und leeren Templates dürfen vor Bildfreigabe entstehen, echte Bildproduktion nicht vorgaukeln. WorkIDs dürfen erst nach Architektur-/Kanonabgleich in reale Dateiedits umgesetzt werden.
