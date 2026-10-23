# V3-01 – Ultimate Digital Human GODMODE 6.0

**Status:** vom Game Director in diesem Gespräch mit JA bestätigt am 23.10.2026. Dies ist eine **Produktionsspezifikation**, kein Nachweis einer lokalen Implementierung.

**Kanon:** Weiterentwicklung des bestehenden `manuelbrandner85/Genesis-Games`, kein neues Spiel. C00–C21, J00–J24 und Ein-Welt-Regeln nicht ohne entsprechende Originalquellen/Freigaben verändern.

**Grundsatz:** Ergänzung zu V2, GENESIS-Missionen 3/12 und GAMEFORGE Living World 03/50; bereits bestehende Systemmodule/Agenten reuse statt kopieren.

## Ziel

Identitätsstabile, realistisch detaillierte Menschen vom Kleinkind bis zum älteren Menschen; nicht nur schöne Standbilder, sondern riggbare und gameplayfähige Figuren.

## Abhängigkeiten / Kanon-Gates

1. Story-/Character-Asset-ID
2. Freigegebene Figurenvorlage
3. Proportionsvertrag der vorhandenen Registry

## Konkrete Implementierungsarchitektur

1. Charakter-DNA versioniert: AssetID, LifeID, Körperprofil, Körpermaßstab, Kopf-/Augen-/Hand-Anker, Kleidung, Altersprofil und Referenzhashes. Kein kanonischer Figurenentwurf ohne verifizierte Storyquelle.
2. Referenzsatz: Vorderseite, Seite, Rückseite, 3/4, Gesichts-Closeups, Hände, Outfit, Farb-/Materialcharts. Einzelbild-KI darf Form nicht allein definieren.
3. Blender: Blockout → anatomische Kontrolle → Sculpt → Retopologie → UV → PBR → Haare/Kleidung → Skinning → Rig → LOD; Zwischenstände erhalten.
4. Unreal: Austausch über UGenesisCharacterAppearance/Registry statt Änderung des Gameplaycodes; PhysicsAsset, MorphTargets, AnimationBP, Materialien und LOD validieren.
5. Unterschiede nach Lebensalter nur über zulässige Erscheinungs-/Animationsprofile; keine automatische 1:1 Skalierung von Erwachsenen auf Säuglinge.

## Lieferobjekte (Dateipfade als Vertrag, nicht bereits existent)

- `characters/<AssetID>/reference_manifest.json`
- `characters/<AssetID>/master.blend`
- `characters/<AssetID>/export.fbx`
- `characters/<AssetID>/measurements.json`
- `characters/<AssetID>/turnaround/*.png`
- `UE-Asset-Registry- und PIE-Nachweise`

## Abnahme und reproduzierbare Tests

1. Maße/Pivot/Skeleton/Anker mit freigegebenem Charaktervertrag vergleichen; numerische Abweichungen protokollieren.
2. Vorder-/Seiten-/Rückansicht human-review gegen identische Referenz-ID und Objektversion.
3. Unreal-Proportionen, Kapsel, Fußhöhe, AnimBP-Skeleton, LOD, Gewichte und Knochenhierarchie testen.
4. Gesichtsausdrücke/Änderungen von Outfit oder Alter dürfen CharacterAssetId-Identität nicht unbemerkt ersetzen.

## Harte Negativregeln

- Ohne freigegebene Referenzen nur PROTOTYPE, niemals HERO_APPROVED.
- Keine rechtlich ungeklärten Gesichts-/Stimmenkopien realer Personen.
- Kein automatisch behaupteter 1:1-Bild-zu-3D-Transfer: künstlerische Revision nötig.

## Rollen und Übergabe

`genesis-character-artist`, `genesis-reference-director`, `genesis-rigging-specialist`, `genesis-pbr-specialist`, `genesis-qa-release`

### Protokollierungspflicht pro Arbeitspaket

`work_id, improvement_id, base_commit, canon_source_path, canon_sha256, agent_owner, files_changed, input_asset_hashes, outputs, license_proof, commands_run, engine_version, evidence_log, test_case_ids, outcome, reviewer, blockers`.

**Zustandsübergang:** `SPECIFIED → READY_FOR_IMPLEMENTATION → IMPLEMENTED_UNTESTED → VERIFIED_ENGINE → REVIEWED_HUMAN → ACCEPTED`. Bei fehlenden Quellen, Tools oder Freigaben ausdrücklich `BLOCKED`. Keine Abnahme durch Agenten-Selbsteinschätzung.

**Integrationsreihenfolge:** zuerst bestehende GENESIS-Komponenten und GAMEFORGE-Auftragsregister prüfen, dann kleinste funktionsfähige Implementierung auf getrenntem Git-Branch, Test, Review, erst danach nächster Auftrag. Kein eigenständiger Agentenserver.
