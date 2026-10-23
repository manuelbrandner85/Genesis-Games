# Referenz → Blender → Unreal: verbindliche Produktionspipeline

## A. Automatische Referenzerstellung (Claude Code Agent 05)
Für jede AssetID ein Set an **echten, zueinander passenden** Referenzen:
- Menschen/Tiere: front, rear, left, right, top, 3/4, Mimik-/Gesicht- und Handdetails, T-Pose/A-Pose, Größenlinie, Haut-/Haar-/Kleidungsvarianten, rigging markers.
- Fahrzeuge/Gebäude/Objekte: front, rear, left, right, top, 3/4, Explosions-/Baugruppensicht wenn nötig, Tür-/Fenster-/Radmaße, reale Materialdefinition.
- Biologische/Storyobjekte: gesonderte Script-/wissenschaftliche Prüfung statt beliebiger Fantasiedetails.
- Metadaten: `AssetID, SourcePrompt, Creator, GenerationTool, ReferenceVersion, Units_m, Height_m, Width_m, Depth_m, StyleGuideID, ColorPalette, MaterialIDs, StoryRefs, ApprovalStatus, LicenseProof, SHA256`.
**Nicht verfügbare Bildgeneratoren:** Fallback zu Blender-Blockouts und Render-Turnarounds, schriftliche Maße; keine erfundenen Bilder. Wenn echte hochqualitative Render-Referenzen fehlen, bleibt das Asset unfreigegeben.

## B. Blender 3D Herstellung
1. Freigabe von Form/Orthobildern. Szene in Meter, `+Z` oben (korrekter UE-Achsen-/Unit-Export explizit testbar).
2. Original `.blend` anlegen, verständliche Collections, versionierte Material-/Meshnamen.
3. Präzise harte/sanfte Formen, menschliche Anatomie, Topologie; Rig/Voronoi/UV je Bedarf, Weighted Normals, PBR.
4. Automatische Analysen: Null-Geometrie, freie Vertices, normals, offene Ränder (außer absichtlich), UVs, Polygon-/Bonebudget, Face-Features, Rig-Bewegungsraum.
5. Echte Blender-Turnaround-Renders zur Abnahme, inkl. Silhouetten-Overlay/vermessenem Maßbild. Gegen Originalreferenz prüfen und iterieren.
6. Export `.fbx`/`.glb`/ggf. `.usd` plus .blend Master; vorher Exportklassen, Skelett-/Animationsdaten klar trennen. Exportroutinen mit exakten Versionen erfassen.
7. Lizenz-/Herkunftszertifikat durch Agent 23; kein kostenpflichtiges oder ungeklärtes Asset.

## C. Unreal Import und Test
1. UE Editor startet mit gültigem Projektpfad, Pluginkompatibilität bestätigt, Python/Import-API/MCP-Adapter `healthcheck=ok`.
2. FBX/GLTF je Pluginfähigkeit importieren, **AssetID-Stammdaten und Import Task Log** speichern; automatischer Readback im Unreal-Editor.
3. Mesh-Skalierung Unreal cm, Skelette, Materialslots, Pivot, Transform, Kollisionen, Animation Blueprint/Rigs, LODs prüfen.
4. Vergleichsmap öffnen und objektive Render- und Messdaten speichern. Auf Distanz und bei Echtzeitbewegung beobachten.
5. UE5-Integration in World Partition, PCG, Gameplay oder Sequencer. Regression und Performance mit echten Builds.
6. `build_artifact.json`: BlenderMasterSHA, FBXSHA, UEContentPath, EngineVersion, ToolVersions, ImportedSizeCm, TestPass, ScreenshotPaths, RightsStatus, WorkID.

## D. Qualitätsstufen
- `DRAFT_REFERENCE` → `REFERENCE_APPROVED` → `BLENDER_BUILT_UNTESTED` → `BLENDER_VALIDATED` → `EXPORTED` → `UE_IMPORTED_UNTESTED` → `IN_ENGINE_TESTED` → `PERFORMANCE_APPROVED` → `PRODUCTION_ACCEPTED`.
- Korrekte 3D-Objekte müssen echte editierbare Geometrie sein, keine bloße Projektion von Fototexturen auf einen Würfel. Vorlagenbilder sind NICHT automatisch Meshes.
- Referenz-/Mesh-Vergleich: reproduzierbare Front-/Seiten-/Topansichten, maßhaltiges Overlay; Gesichtsmerkmale/proportionen bei Figuren gesondert prüfen. KI darf Detail und Wiedererkennbarkeit nicht einfach behaupten.
- Veröffentlichung erst mit Lizenz- und QA-Freigabe. Für große offene Welten erzeugt Level-/PCG-System Variationen, aber spezifische Hero-Assets bleiben individuell modelliert.

## E. Lokalwerkzeuge und Agenten
- Werkzeugstart: Blender `--background --python tools/blender_smoke_crate.py`, Unreal Editor/Unreal Python `tools/unreal_import_smoke.py` (Pfade gemäß Installation).
- Die Skripte sind **Smoketest-Beispiele**, bewusst einfache geometrische Test-Props. Sie beweisen nur die Pipeline nach tatsächlichem Lauf, keine fertige GENESIS-Welt.
- Wenn eine Engine-Version andere Import-APIs verwendet: den echten Editor introspektieren, Compat-Fix dokumentieren, dann erst ausführen.
