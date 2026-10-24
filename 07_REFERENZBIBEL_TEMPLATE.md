# GENESIS – Vorlage für jede einzelne Referenz / jedes 3D-Objekt

## Pflichtfelder
`AssetID | Anzeigename | Typ | StoryRefs | RegionID | Charakter-Alter | OriginSource | License | StyleGuide | DimensionsMeters | FocalFeatures | SkeletonID | Materials | RequiredAngles | SourceImages | Approval | .blend | FBX | UnrealPath | QA`.

## Beispiel (nur SMOKE-TEST, kein originales Spielasset)
`AssetID: TEST_SMOKE_CRATE_001`
- Zweck: Toolkette prüfen, nicht als High-End-GENESIS-Prop verkaufen.
- Maße: 1.0×1.0×1.0 m, Holz-Kiste, simple PBR-Basismaterialien.
- Orthobilder: front/back/left/right/top/iso durch Blender-Skript gerendert, je 512px.
- Quelle: eigener Blender-Bau; keine Fremdassets. Blender `.blend`, `FBX`, `.glb`, `views/`.
- Unreal-Import: `/Game/Genesis/Prototyping/SMOKE_TEST`, tatsächlicher Importreadback.
- Final-Accepted-Status: VERBOTEN; Asset ist Testgeometrie.

## Charakter-Template
1. Name/AssetID, Geburts-/Spielalter, biologische Merkmale nur nach Originalstory und kreativer Freigabe.
2. Grund-/Anatomieproportionen in Zentimetern: Körpergröße, Bein/Rumpf-Relation, Auge, Schulter/Becken, Hände/Füße, Gesicht Landmarken.
3. Head close-up neutral/lächeln/ernst/sprechen; front, profile links/rechts, hinten, 3/4, A-/T-Pose, Kleidungsschichten, Silhouettenraster.
4. Rigs: kompatibler Basisstandard, Ersatzskelett/Retarget je Altersstufe, Face-Rig, FACS wenn praktikabel.
5. Textur-/Materialkarte: Haut/Haar/Augen/Kleidung, PBR Maps; Lizenz-/Rechtepfad.
6. Referenzvergleich und echte in Unreal animierte Drehung/Interaktion. `Blueprint`/`AnimBP`/`Skeleton` IDs und Versionen.

## Environment/Vehicle Template
- Exakte Dimensionen, koordinierte Ansichten, Innen-/Außenbezüge, Tragwerk/Beweglichkeit, Materialalterung, modular tile-Schnittstellen, Achsen-/Radstand bzw. Gebäudemaße.
- Kollisions-Layer, LODs, Nanite-Eignung, Physik, PCG-Instancefähigkeit und realer Performancecheck.

## Fehlerbehandlung
Falls inkonsistente AI-Referenzansichten geliefert wurden, den Bildsatz korrigieren oder einen rig- und perspektivenkonsistenten Blender-Blockout rendern. Darauf basierend hochwertig modellieren. KI-Referenzbild ist keine Automatik-Konvertierung in ein korrektes 3D-Mesh. Es wird niemals ein nicht vorhandenes Bild in einem Bericht als angehängt behauptet.
