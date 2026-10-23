# GENESIS-24-Rollen → GAMEFORGE-42-Agenten (erst nach Inventur verbindlich)

Die Nutzerdatei GAMEFORGE Verbesserung 03 verweist auf ein bereits gedachtes 42-Rollen-System. Das Original der Agenten-Konfiguration ist **hier nicht in Bytes enthalten**, deshalb ist folgende Liste nur ein **Mapping-Vorschlag**, keine Aussage über tatsächlich installierte Agents.

| GENESIS-Role | Fachbereich | Bevorzugtes GAMEFORGE-Profil nach Original-03 (soweit vorhanden) | Entscheidung |
|---|---|---|---|
| 01 Master Director | Koordination | 01, 02, 03, 25 | Audit Pflicht |
| 02 Script Guardian | Story/Kanon | 04, 05, 06 | Audit Pflicht |
| 03 Planner | Produktion, Token | 01, 02, 03 | Audit Pflicht |
| 04 Tool Integration | Blender/Unreal | 21, 25 | Audit Pflicht |
| 05 References | Art Bible | 11–15 | Audit Pflicht |
| 06 Character | Human modeling | 11–15, 17–20 | Audit Pflicht |
| 07 Environment | Siedlung/Biome | 11–15 | Audit Pflicht |
| 08 Rigging | Rigging/Motion | 17–20 | Audit Pflicht |
| 09 PBR | Textur/Render | 17–20 | Audit Pflicht |
| 10 Motion | Charakteranimation | 17–20 | Audit Pflicht |
| 11 Facial | Gesicht/Lipsync | 17–20, 27–42 | Audit Pflicht |
| 12 Unreal Core | C++ / Blueprint | 21, 22, 23, 24 | Audit Pflicht |
| 13 Open World | Streaming/PCG | 24, 25 | Audit Pflicht |
| 14 NPC | StateTree/Social | 22, 24 | Audit Pflicht |
| 15 Missions | Quest Contracts | 06, 09 | Audit Pflicht |
| 16 Economy | Societal Systems | 09, 22 | Audit Pflicht |
| 17 Vehicles | Chaos/Navigation | 22, 24 | Audit Pflicht |
| 18 Soul/Rebirth | Story + Save | 09, 21 | Audit Pflicht |
| 19 Cinematic | Sequencer | 11–15, 17–20 | Audit Pflicht |
| 20 Audio | Voice/Music | 27, 28, 33–42 | Audit Pflicht |
| 21 UI | Menus/HUD | 21, 25 | Audit Pflicht |
| 22 Performance | Profiling | 26 | Audit Pflicht |
| 23 Rights | Lizenz/Quellen | 32 | Audit Pflicht |
| 24 QA/Release | Tests/Build | 29, 30, 31 | Audit Pflicht |

**Konfliktverhinderung:** Mapping zuerst an echter StudioBrain-Agentenregistrierung und Rollenprompt ausrichten; Nummern sind nur aus GAMEFORGE-03-Bericht übernommen. Bestehende 42 nicht pauschal löschen oder duplizieren. In Claude Code definierte 24 Unteragenten sind Alternative für Fachaufgaben, keine zweiten permanenten StudioBrain-Services. Echte `/agents`-Verfügbarkeit separat prüfen.
