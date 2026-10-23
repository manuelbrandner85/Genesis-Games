# Standard – Referenzbibel je Asset

## Verbindliche Daten
`asset_id`, `kind`, `project_id`, `story_source`, `source_hash`, `approval_id`, `revision`, `scope`, `dimensions_m`, `origin`, `up_axis`, `materials`, `reference_files`, `look_variants`, `license`, `intended_lod`, `target_ue_path`, `blender_master`, `export_path`, `qa_evidence`.

## Mehransichten
- **Mensch:** Front, Rücken, links, rechts, 3/4 links, 3/4 rechts, Portrait 50/85 mm, Hände/Füße und neutral A/T-Pose, konsistente Landmarken.
- **Gebäude:** maßhaltiger Grundriss, Höhen/Schnitt, vier Fassaden, Türen/Treppen, Material/Alterung, Innenraumansichten.
- **Fahrzeug:** Front/Heck/links/rechts/Draufsicht/Innenraum, Radstand/Spurbreite, Fahrwerk, Sitze, Cockpit und Schäden.
- **Requisite:** mindestens Vorder-/Seiten-/Oberansicht und Material-/Verschleißblatt; passende technische Maße.

**Keine Referenz erfinden:** Referenzbilder in diesem Paket sind Vorlagen/Dateinamen. Eine Bilderstellung braucht ein tatsächlich installiertes Bildtool, selbst angefertigte Referenzen oder rechtskonforme externe Quellen. Blender `render_turnaround.py` kann Ansichten eines **vorhandenen 3D-Modells** erzeugen, nicht aus Text einen hochwertigen Menschen generieren. Fehlendes Bild bleibt `WAITING_REFERENCE`.

## Qualitätsvergleich
1. Maßstab/Pivot; 2. Umriss; 3. Anatomie/Hard-Surface-Geometrie; 4. Material/UV; 5. Gesicht/Markenzeichen; 6. Rig/Animation; 7. LOD/Kollision; 8. Lizenz. Jeder Vergleich mit Referenzrevision, Screenshots und Signoff.
