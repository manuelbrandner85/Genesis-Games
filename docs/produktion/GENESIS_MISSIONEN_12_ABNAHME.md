# GENESIS Verbesserung 3: 12 Mission-/Living-Events-Verträge

Das System ist **zusätzlich** zu GAMEFORGE Verbesserung 03 (50 Funktionen), kein Ersatz. Auf bestehende Mission/Quest-Anker zurückgreifen, fehlende Kanonquellen nicht erfinden.

1. Hauptmissionen nur aus kanonischen C00–C21 und Missionsankern.
2. Nebenmissionen aus belegten NPC-Berufen/Beziehungen.
3. Dynamische Ereignisse nur aus kontrollierten Templates.
4. Entscheidungen als nachweisbare Konsequenzen, keine Karma-Skala.
5. NPC-Gedächtnis mit Herkunft/Validierung.
6. Alternative Wege ohne Missions-Softlock.
7. Sequencer-/Gameplay-Handoff mit Commit/Skip.
8. Ereignisbedingungen: Zeit, Ort, Wetter, soziale Lage.
9. Beruf/Karriere nur auf ökonomischer Runtime-Wahrheit.
10. Familienereignisse nur über Social-/LifeCycle-Daten.
11. WorldState/Save/Travel konsistent über Zeit und Streaming.
12. Questgraph-, Gating-, Idempotenz- und Deadlock-Tests in realer Unreal-PIE-Umgebung.

**Missionszustandsmaschine:** `Eligible→BindingValidated→Ready→Playing→AwaitingInteraction?→CommitPending→Committed→HandedBack`; per-Event `idempotency_key`, `causal_event_ids`, `npc_memory_refs`, `return_location`, `save_schema_version`. Automatisches Zeitlimit nur wenn im echten Weltereignis begründet. 0/12 als implementiert behaupten, bis Runtime geprüft.
