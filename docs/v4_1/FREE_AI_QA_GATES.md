# FREE AI QA / RELEASE-GATES

- FAI-00 Source & Rights: Story-/Figuren-ID, Script-Lock, Lizenzversionen, Herkunft vorhanden.
- FAI-01 Hardware: `hardware_probe.py` erfasst verifizierbare Daten; GPU-Eignung nur wenn gemessen.
- FAI-02 Installation: Nutzer gibt exakten Installationsplan frei; Installlog, SHA und lokale Version vorhanden.
- FAI-03 Generator Smoke: vom Tool wirklich erzeugtes, gespeichertes Artefakt mit Hash; nicht nur Prompt.
- FAI-04 Reference: geometrische Identität der Mehransichten im Review nachvollziehbar.
- FAI-05 Blender: Quelle .blend, reale View-Render, Dimensions-/Rig-/Material-Check, Artefaktvergleich.
- FAI-06 Unreal: tatsächlicher Import, angemessene Skelett-/LOD-/Physik-/Material-/Collision-/Performance-Tests.
- FAI-07 Audio: WAV gültig, Dialog verständlich, korrekte deutsche Untertitel/Timecode, urheber- und sprecherrechtlich freigegeben.
- FAI-08 Story: C00/C20-Originalreferenz, C15/C16, C17 und C21 Konfliktentscheidungen geschützt; kein versteckter Epoch-Picker.
- FAI-09 Windows: echter lokal gebauter testbarer Build mit Logs und menschlicher Game-Director-Abnahme.

Die integrierten Python-Tests prüfen nur Tools/Dateien/Gates; sie beweisen weder fotorealistische Charaktere noch vollständiges Spiel. Ergebnisse strikt mit `SPEC_ONLY`, `TESTED_LOCAL_SCRIPT`, `ENGINE_TESTED`, `DIRECTOR_ACCEPTED` trennen.
