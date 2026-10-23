# GENESIS – Verbesserung 02: Ultimate 3D Character Factory 5.0

**Bestätigt:** JA zu allen zehn Verbesserungen am 23.10.2026.
**Status:** geplanter, fachlich freigegebener Entwicklungsumfang; keine hier erfolgte UE-Implementierung.
**Leitziel:** Realistische, wiedererkennbare und über Lebensphasen hinweg konsistente Menschen – vom Referenzblatt bis zur getesteten UE-Figur.
**Gültigkeit:** nur bestehendes `manuelbrandner85/Genesis-Games`, Claude Code als Entwicklungsleitung, keine Story-Umschreibung.

### Produktionsfunktionen
1. Character-DNA: `CHAR-ID`, Lebensphasen, anatomische Proportionen, Gesichtsmerkmale, Familienähnlichkeit, Ausrüstung/Outfits und eindeutige Referenzrevision.
2. Identitätsschutz: feste Gesichtsanker (Augenabstand, Nase, Kiefer, Ohr, Hautbild) und Variation nur innerhalb genehmigter Grenzen.
3. Referenz-Turnarounds: Vorder-/Rück-/Links-/Rechts-/Dreiviertel- und Gesichtsnähenansichten mit konsistenter Brennweite, Scale-Ruler und neutraler Pose.
4. Anatomie-Vertrag: reale Maße, Schulter/Hüfte/Armspannweite, Fingerglieder, Fußkontakt, Augenhöhe; keine unmöglichen Körperproportionen.
5. Blender Master: quelloffene `.blend`-Datei mit organisierten Collections, richtiger Units-Konvention, sauberer Topologie und Version.
6. High/Low-Poly: Sculpt/Detail, Retopo, Normal-/Displacement-Baking, LODs für Gameplay statt immer cineastisch schwerer Meshes.
7. UV/PBR: getrennte Maps für Haut/Haare/Stoff, konsistente Farbräume; dokumentierte externe Quellen.
8. Haare: kontrolliertes Groom-/Cards-Konzept nach UE-Version/Performance; Augen, Tränenlinien, Zähne, Nägel und Kleidung als eigene kontrollierbare Komponenten.
9. Skelett: bestehende UE-kompatible Skeleton-/Retarget-Contracts berücksichtigen, keine unaufgeforderte Neudefinition des Charaktersystems.
10. Shape Keys/Face Rig: überprüfbare Morphtargets/Blinken/Emotionen mit neutralem Grundzustand; kein unkontrolliertes Gesichtsdriften.
11. Gewichtsprüfung: Deformation an Schultern, Ellenbogen, Knien, Fingern, Hals, Mundwinkeln, Kleidungsnähten.
12. Altersprofile: Säugling/Kind/Jugend/Erwachsener/älterer Mensch mit plausiblen Übergängen; kein reines Skalieren eines erwachsenen Skeletts.
13. Motion Profiles: natürliche Bewegungen je Alter und Mobilität, einschließlich Rollstuhl/Assistenz falls vom Kanon abgedeckt.
14. Unreal Import: fester `CharacterAssetId`-Bezug; SkeletalMesh, PhysicsAsset, AnimBP, Morphs, Materials, retarget und LODs müssen im tatsächlichen Editor geprüft sein.
15. Hero Quality: Cinematic-Nahaufnahme, Textur- und Mimikabnahme mit mehreren Lichtwinkeln.
16. Rechtslage: freie/geeignete Assetgrundlagen, eindeutige Lizenzliste; keine ungeprüften Gesichtsscans oder unautorisierte echten Personen nachbilden.
17. Optimierung: Skeletal Tick LOD, Materialkosten, Mesh-/Hair-Budgets auf tatsächlicher Zielhardware messen.
18. Editor Reality Check: Detailfotos, Abstand/Frontal- und Profilvergleich, Pose-Bilder sowie deformierte Problemstellen belegen.

### Artefakte je Figur
`refs/CHAR-ID/{front,back,left,right,three-quarter,face-closeup}.png`, `character_dna.json`, `proportions.json`, `model/master.blend`, `exports/*.fbx|*.glb`, `ue_import_report.json`, `license_record.json`, `qa/turnaround_comparison.md`. Ein JSON-Report ohne tatsächliche Modelle ist *nicht* fertig.

### Abnahme
Mindestens dimensions-/Skeleton-/UV-/Material-/Deformations-Prüfung und echte In-Editor-Vorschau bei Gehen, Sitzen, Gesichtsausdruck. Referenzübereinstimmung wird visuell vom Game Director akzeptiert; algorithmischer Vergleich ist Unterstützung, keine Garantie. Freigabe einzigartiger Hauptfiguren separat.

### Technischer Produktionsauftrag
Arbeite mit dem vorhandenen Repo, GAMEFORGE StudioBrain und Character Creation 4.0, sofern tatsächlich vorhanden. Ermittle Basiscommit, freigegebene Quellen und installierte Werkzeuge. Dokumentiere Architektur, konkrete Dateien, Tests und Evidenz. Führe nur genehmigte ungefährliche Schritte aus; für riskante Änderungen explizite Freigabe. Übergebe jeden Arbeitsschritt an unabhängige QA. `NOT_IMPLEMENTED` bleibt sichtbar, bis ein echter Editor-/Runtime-Nachweis vorliegt.

### Technische Character-Schnittstellen
`CharacterDna`: ID, genetisch bedingte und lebensbedingte Merkmale getrennt, Variation je Lebensphase, Identitätshash, Elternbezug (falls belegt), gesperrte Gesichtsanker. `CharacterAssetContract`: bind_pose, skeleton_id, camera_anchor_cm, capsule, required_bones, cloth_slots, face_shapes, physics_asset, texture_budgets. Diese JSON/DataAsset-Konzepte sind **an vorhandene** `UGenesisCharacterAppearance` und Registry anzupassen, statt neue parallele Charakterklassen zu schaffen.

**Reale Modellqualität:** Hauptfiguren benötigen sichtbare menschliche Anatomie, Hautstruktur, Augenmaterial, Haaransatz, korrekte Fingernägel, eigene Kleidungsschichten, Platz für Morph-/Rig-Deformation und fotorealistische Lookdev-Tests. Die Testkiste im Paket belegt nur die Datenpipeline. Die Qualität einer 3D-Figur wird durch Artist-Sichtabnahme auf Referenzansichten, Topologieausschnitten, Neutral-/Smile-/Speak-Frames und Unreal-Closeups bewertet. Automatische Kontrolle kann Maße, fehlende UV oder Bone-Struktur erfassen, jedoch keine menschliche Ähnlichkeit zuverlässig garantieren.

**Verarbeitung:** `reference_locked` → Proportions-Modell → High/Low → UV/Material → Rig → Deformation/Testposes → export → UE Retarget/AnimBP → Laufzeit/LOD → creative_signoff. Fehlende Referenz: `WAITING_REFERENCE`, unverträgliche Skeletons: `TEST_FAILED_SKELETON`, nur FaceTexture ohne rig: `BUILT_UNTESTED`. Mehrere Persönlichkeits-/Altersvarianten müssen zu *einer* identifizierbaren Person passen, außer die Story schreibt neue Identität vor.

**QA-Fälle:** A1 Figur in neutraler Pose in Blender und UE gleich dimensioniert; A2 korrekte Bodenberührung; A3 Camera Anchor verändert sich nicht unkontrolliert beim Meshwechsel; A4 AnimBP akzeptiert Retarget; A5 Finger/Knie/Schulter/Faces korrekt deformiert; A6 Material unter 3 Lichtsettings plausibel; A7 Fern-LOD spart messbare Ressourcen; A8 Referenz-ID und Quellenrechte stimmen.

### Abhängigkeiten / nächste Umsetzung
Hauptfiguren, besonders Prologmann/Tochter, bis Story-/Designfreigabe nur planen. WorkIDs dürfen erst nach Architektur-/Kanonabgleich in reale Dateiedits umgesetzt werden.
