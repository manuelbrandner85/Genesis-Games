# C00 – Produktionsplan (öffentliche Fassung, ohne Drehbuchtext)

Kanon gesperrt durch [GD-2026-10-24-01](DIRECTOR_DECISIONS.md). Das vollständige Paket mit Shotinhalt, Dialog-Cues und Figurenbeschreibung liegt nur lokal unter `canon_sources/production/C00/` (gitignored). Hier stehen nur IDs und technische Daten.

**Status:** CM4 – Shotliste freigegeben (2026-10-25); Figuren-DNA, Stimmen und Vorfilm-Quelle offen.

## Technische Eckdaten

| Feld | Wert |
|---|---|
| Typ | A – Fixed (vorgerenderter Master, in C20 bild-/tonidentisch wiederverwendet) |
| Länge | ca. 100 s · 24 fps · 2400 Frames |
| Shots | 00-A 12 s/50 mm · 00-B 18 s/85 mm · 00-C 42 s/65 mm · 00-D 20 s/65–85 mm · 00-E 8 s |
| Audio-Cues | VO_C00_001–008 (2 Sprecherrollen), MUS_SOUL_INTERVAL_01, SFX-Bett |
| Untertitel | SUB_C00_001–008 |
| Assets | CHR_C00_MANN, CHR_C00_TOCHTER, SET_C00_SCHLAFZIMMER_2026 |
| Überspringen | Zweifachbestätigung → `CommitPending` (nie am Commit vorbei) |
| C20-Bindung | Master-Datei + SHA-256 + Framebereiche 00-B/00-C (CM5) |

## Offene Entscheidungen beim Game Director

1. ~~Abnahme der Shotliste~~ – **Shotliste 00-A bis 00-E freigegeben** (2026-10-25, Game Director: „Ja, die Shotliste 00-A bis 00-E ist freigegeben. Baue als Nächstes 00-B als echte Sequencer-Sequenz mit Bewegung (Daumen, Atem) und MRQ-Render, sobald der Editor frei ist.“; Eintrag in `DIRECTOR_DECISIONS.md` folgt). Figuren-DNA weiter offen (Entwürfe im lokalen Paket, Referenzbilder in `ArtSource/Reference/C00/`)
2. Stimmen: echte deutsche Sprecher:innen (Voraussetzung für die Abnahme) – Besetzung
3. ~~Freigabe MetaHuman~~ – erledigt: GD-2026-10-24-03 (Plugins), FA-METAHUMAN-CLOUD-001 (4K-Texturen, Auto-Rig)
4. Quelle `Docs/33_Der_Vorfilm.md` (Vorfilm-Migration) bereitstellen

## Stand 2026-10-25 (belegt, keine Abnahme)

Was es jetzt gibt, jeweils mit Werkzeug und Beleg. Fab-, Epic- und MetaHuman-Inhalte bleiben lokal (gitignored); im Repo liegen nur Skripte und Belegbilder.

| Baustein | Stand | Werkzeug | Beleg |
|---|---|---|---|
| SET_C00_SCHLAFZIMMER_2026 | in Unreal aufgebaut: Neubau-Zimmer, Regen, Bett mit Daunendecke (Drapierung mit Falten), Kissen, Stoffmaterial, Nachttisch, Fotos, Stuhl an der Fensterseite | Blender → `tools/v4_2/build_c00_bedroom*.py`, `place_c00_chair.py`, `export_c00_bedroom.py`; Unreal → `c00_scene_bedroom.py` | `docs/evidence/V42/C00_Schlafzimmer_UE_{weit,wand,raum,tuer}.png` |
| CHR_C00_MANN | gebauter, animierbarer MetaHuman: Liegepose (`c00_pose_lying.py`), Sterbe-Mimik über das Gesichts-Rig (`c00_face_dying_rig.py`), eigenes Schlafshirt, Haare für Nahaufnahmen | Unreal, MetaHuman | `…_UE_bett.png`, `…_UE_arme.png` |
| CHR_C00_TOCHTER | gebauter MetaHuman, 166 cm (`c00_tochter_height.py`), Sitzpose am Bett (`c00_pose_tochter.py`) | Unreal, MetaHuman | `…_UE_tochter.png` |
| 00-B (Hand in der Hand) | **technischer Test**: 85 mm, ihre Hand auf seiner (Hand an der Fensterseite = anatomisch seine linke) | `c00_scene_bedroom.py` Shot `00b` | `…_UE_00b.png` |

**Nicht behauptet:**
- Keine Sequenz (Sequencer).
- Kein Movie-Render-Queue-Master und keine Bewegung (alle Bilder sind Standbilder einer Einzelpose).
- Kein Ton, keine Stimmen, keine Untertitel, keine Musik.
- Keine Abnahme der Shotliste.

Die Szene steht deshalb weiter auf `NOT_IMPLEMENTED`; Set und Figuren sind technisch geprüft, aber nicht abgenommen.
