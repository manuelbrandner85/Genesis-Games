# GENESIS – Verbesserung 07: Adaptive Music & Voice Studio

**Bestätigt:** JA zu allen zehn Verbesserungen am 23.10.2026.
**Status:** geplanter, fachlich freigegebener Entwicklungsumfang; keine hier erfolgte UE-Implementierung.
**Leitziel:** Kontextabhängige Musik, deutsche Dialoge und physikalisch glaubwürdiger Sound mit belegten Rechte-/Audio-Cues.
**Gültigkeit:** nur bestehendes `manuelbrandner85/Genesis-Games`, Claude Code als Entwicklungsleitung, keine Story-Umschreibung.

### Produktionsfunktionen
1. Ursprüngliches Soul-Motiv und die persönliche Familienmelodie als getrennte Quellen führen; nicht ohne Quellfreigabe vereinheitlichen.
2. Lebensphasen, Tageszeit, Wetter, Gespräch, Tod/Jenseits und Entdeckung als Musik-/Soundzustände abbilden.
3. MetaSounds/SoundCues/AudioMixer-Schichten, die im Spiel *ereignisgetrieben* ohne Online-API laufen.
4. Musik stems/intensities: Übergänge quantisiert, Ducking bei Sprache, keine abrupten Loops ohne Fades.
5. Deutsche Sprach-Cue-Verträge `SpeakerID`, `Locale`, `VariantID`, `SubtitleID`, `AudioCueID`, `Timecodes`.
6. Kein KI-Stimmenklon realer Menschen ohne Rechte; kommerzielle Lizenzen für Synthese-/Samples/Klangarchive nachweisen.
7. Hochwertiger Lipsync und Emotion mit tatsächlichem Audio testen; synthetisches Roh-TTS ohne menschliche Prüfung nicht als AAA abnehmen.
8. Foley: Schrittmaterial, Stoff, Tür, Fahrzeug, Innen-/Außenraum, Wetter, Personen- und Tiergeräusche.
9. Akustik: Distanz, Occlusion, Reverb, unterschiedliche Innenräume und Umgebungen.
10. Barrierefreiheit: unabhängige Lautstärken, Untertitelsprecher, Dynamic-Range-Preset, Audio-Hinweise.
11. Keine bezahlte API ohne Zustimmung; kostenlose Werkzeuge nur bei klaren Nutzungsrechten.
12. Sequencer-Audio und C00/C20-Master gegen identische Assets/Hashes koppeln.
13. Silent Fallback bei fehlenden lizenzierten Clips, keinesfalls erfundene Sprachdatei als vorhandenes Asset melden.
14. Performance: Voice-Count, Streaming, Speicherverbrauch, Decompression anhand UE-Audioprofiler testen.

### Ausgabe/Abnahme
Cue-Sheet CSV, WAVE-Dateien/Source-Projekte, Lizenzbuch, MetaSound/UE-Referenzen, Untertiteldateien, Lip-Sync-Asset, Hörtestprotokoll und CI-Test auf ID-Konsistenz. Musikaufträge zuerst als Brief/Mockup bis Audio-Quelle tatsächlich vorliegt.

### Technischer Produktionsauftrag
Arbeite mit dem vorhandenen Repo, GAMEFORGE StudioBrain und Character Creation 4.0, sofern tatsächlich vorhanden. Ermittle Basiscommit, freigegebene Quellen und installierte Werkzeuge. Dokumentiere Architektur, konkrete Dateien, Tests und Evidenz. Führe nur genehmigte ungefährliche Schritte aus; für riskante Änderungen explizite Freigabe. Übergebe jeden Arbeitsschritt an unabhängige QA. `NOT_IMPLEMENTED` bleibt sichtbar, bis ein echter Editor-/Runtime-Nachweis vorliegt.

### Sound Runtime Contract
`AudioCueID` beschreibt Trigger, Zone, Spielphase, Stimmenidentität, Bedingung, Priorität, Lautheit/Laufzeit, Loop-/Fade-Regel, Streamingklasse und Lizenz. `SubtitleCueID` enthält Sprachen, Start/Ende, Sprecherrolle, Variantenbindung und Barrierefreiheitsmarker. Eine hörbare Stimme erfordert ein vorhandenes Audiofile; „KI kann Text erzeugen“ reicht nicht für Produktionsqualität. Ambient-Wetter, Straßenverkehr, Tiere, Innenraumhall und NPC-Arbeit werden an reale Zustandsereignisse gebunden.

**Komposition:** Musikerzeugung und konkrete Musikaufnahme sind getrennte Aufgaben. Claude kann CueSheets, harmonische Motive und Stem-Baupläne entwickeln, aber fertig aufgenommene Musik nur melden, wenn echte WAV/DAW-Projektdateien vorliegen. Rechte und Nutzbarkeit sind zu jedem Sample/Synth/Sprachmodell dokumentiert. Die emotionalen Rückgriffe auf Familienmelodie dürfen nur aus tatsächlich in der jeweiligen Lebensgeschichte begründeten Geräuschen entstehen.

**Cue-Integration:** MetaSounds/Mixer steuern Übergänge über `WorldClock`, Zone, `NpcContext`, `QuestEvent`, `SoulTransition`. Spiel muss ohne generative Audio-API funktionieren; Cloudanbieter nur optionale durch Benutzer freigegebene Produktionshilfe, nie zwingende Laufzeitabhängigkeit. Deutsche Lippensynchronisation mit Wave-/Morph-Laufzeiten validieren.

**QA-Fälle:** A1 alle CueIDs auf existierende, lizenzierte Dateien referenziert; A2 Untertitel folgen Wave-Position beim Pausieren/Skip; A3 Soul-/Familienmotiv getrennt; A4 dynamischer Musikübergang ohne Klack; A5 Dialog verständlich neben Verkehr/Wetter; A6 keine Stimmen ohne Einwilligung geklont; A7 UI-Audioregler wirken in Runtime; A8 Audio-GPU/CPU/Memory auf echter Zielhardware geprüft.

### Abhängigkeiten / nächste Umsetzung
Zunächst Original-CueSheet und lizenzierten Tonbestand inventarisieren; fehlende Aufnahme nicht simulieren. WorkIDs dürfen erst nach Architektur-/Kanonabgleich in reale Dateiedits umgesetzt werden.
