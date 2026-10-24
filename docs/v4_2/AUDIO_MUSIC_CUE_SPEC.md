# GENESIS V4.2 – Audio, Musik, Stimme, Untertitel

Kanonschutz: individuelle Familien-/Lebensmelodie (`M03`) ist nicht das Soul-Motiv (`M09`). Audioreferenzen dienen nur als IDs und Produktions-Cues, **nicht als bereits erstellte Musik/Vertonung**.

| Cue | Szenen | Produktions-/QA-Zweck |
|---|---|---|
| M01_LAST_BREATH | C00, C20 | derselbe Originalmaster mit Regen/Atem/Dialog: C20 nutzt identischen Film-/Audiomaster |
| M02_BEGINNING | C01/C02 | keine vorzeitige Spoiler-Stimme |
| M03_LIFE_MOTIF | C03/C07/C12/C14 | individuelles Lebens-/Familienmotiv nur bei echter Quelldatenlage |
| M04_FIRST_AIR | C04 | Geburtstonlage und Transition abhängig vom tatsächlichen Zustand |
| M05_SMALL_CHOICE | C06/C08/C11 | Dialog hörbar, Musik unterliegt Ducking |
| M06_TIME_TABLE | C12/C13 | nur belegte Orts-/Erinnerungs-Snapshots |
| M07_BODILY_END | C14 | echtes Todesereignis, keine unpassende biologische Herzspur danach |
| M08_ECHO_SPACE | C15/C16 | Echo-Audio klar als Reconstruction/Abstraktion markieren |
| M09_SOUL_RECUR | C17/C18 | Soul-Motiv getrennt vom persönlichen Lebensmotiv |
| M10_MANY_VOICES | C19 | Enthüllung erst hier; keine vorzeitigen Sprecherlabels |
| M11_REVEAL | C20 | exakt C00-Prolog als Master, Timing identisch |
| M12_FIRST_MORNING | C21 | Weltzustand nach tatsächlichem Modell, nicht garantierte Menschheit |

Jeder Sprach-Cue: `AudioCueID`, `SubtitleCueID`, `SpeakerID`, `VariantID`, `Locale`, `TimecodeStart`, `TimecodeEnd`, `AudioSHA256`, `LicenseRecord`, `VoiceApproval`. Voice im finalen Release nur nach Qualitäts-/Rechtefreigabe. KI-Preview/TTS als `PREVIEW` markiert. Waveform, Untertitel und Face-Rig-Timing in echter Engine überprüfen. Lade-/Menü-Sounds separat von Gameplay-Lebensklang führen. Lautstärken-Einstellungen für Sprache/Musik/SFX unabhängig speichern.
