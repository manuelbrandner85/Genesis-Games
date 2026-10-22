# Animatic- und Schnittplan C00 + C01

> **Intern – enthält das C20-Geheimnis. Nicht nach außen geben.**
> Alle Zeiten: 24 fps, Timecode `HH:MM:SS:FF` ab Szenenbeginn. Shot-Grenzen stammen aus dem Drehbuch. Dialogzeiten sind **vorläufig/geschätzt** (siehe Sprachzeilen-Liste). Drehbuch: „Die Schnittzeiten sind Orientierung für die Regie; Performance und Sprache entscheiden über den finalen Rhythmus.“
> Es werden keine Aufnahmen, keine fremden Stimmen und keine fremde Musik verwendet. Für das Animatic gilt: Platzhalter-Ton nur aus eigenen, rechtlich geklärten Quellen oder Stille mit Texttafel.

Länge C00: 00:01:40:00 (2.400 Frames). Länge C01: 00:01:20:00 (1.920 Frames). Zusammen 3:00 Prolog, wie im Drehbuch vorgesehen.

## C00 – DER LETZTE AUGENBLICK (INT. Schlafzimmer, Abend, 2026)

| Shot | Zeit (TC von–bis, Frames) | Bild | Kamera | Dialog-IDs | Ton | Musik-Cue |
|---|---|---|---|---|---|---|
| 00-A | 00:00:00:00–00:00:12:00 (0–288) | Schwarz. Nach ca. 1 s schmaler Lichtstreifen an der Gardine. Kein Logo. | Höhe Bettkante, 50 mm, langsames Vorrollen | – | Tropfen auf Glas, entfernte Reifen auf nasser Straße, langsamer schwerer Atem | `M01_LAST_BREATH` (nur Geräusche, **keine Musik**) |
| 00-B | 00:00:12:00–00:00:30:00 (288–720) | Hand des Mannes in der Hand der Tochter, Daumen bewegt sich. Fokus wandert zur alten Fotografie (Inhalt noch nicht erkennbar). | 85 mm Nah, Schärfeverlagerung | – | Regen, Bettlaken, Atem. Kein Schluchzen. | `M01` (keine Musik) |
| 00-C | 00:00:30:00–00:01:12:00 (720–1728) | Zwei schlichte Einzelaufnahmen der Gesichter | 2 × 65 mm, konsistente Blickachsen | VO_C00_001 … VO_C00_008 (geschätzt 00:00:31:00–00:01:03:05) | Dialog trocken, Tochter ohne Hall, Regen links, Atem zentriert | keine Musik bis zur entscheidenden Pause |
| 00-D | 00:01:12:00–00:01:32:00 (1728–2208) | Blick zum Fenster, ein Regentropfen läuft. Letzter Atemzug endet. Hand der Tochter hält weiter. | Kamera bleibt stehen, kein Wegdrehen | – (Tochter sagt nichts) | Atem endet → Stille. **Kein Herzmonitor.** | Nach der Stille: zwei sehr leise aufeinanderfolgende Töne = Soul-Intervall (`M01`/`M02`-Kern) |
| 00-E | 00:01:32:00–00:01:40:00 (2208–2400) | Bild fällt ins Schwarz. Ein schwacher Punkt erscheint und erlischt. | – | – | Stille / Ausklang des Intervalls | Übergang in `M02_BEGINNING` |

Geschätzte Dialogzeiten in 00-C (vorläufig): 001 00:00:31:00–00:00:34:10 · 002 00:00:35:00–00:00:38:22 · 003 00:00:39:12–00:00:43:10 · 004 00:00:44:00–00:00:45:07 · 005 00:00:45:22–00:00:48:22 · 006 00:00:49:12–00:00:55:14 · 007 00:00:56:05–00:00:58:07 · 008 00:00:58:22–00:01:03:05. Danach rund 9 s Raum für Blicke und Atem bis 00:01:12:00.
Reprise-Zeilen für C20: **VO_C00_001, VO_C00_002, VO_C00_006**.

## Übergang C00 → C01 (Ton-Match-Cut)

- Drehbuch: „direkter Klang-Match-Cut nach C01“; „Schwarz des letzten Atems → C01, erster Lichtpunkt wird zum Stern-/Erdbild“; Klangregie C01: „Aus Regen wird leiser Wind“.
- Umsetzung im Schnitt:
  1. Der Lichtpunkt aus 00-E (um 00:01:38:00 in C00) ist dasselbe Bildelement wie der Lichtpunkt am Anfang von 01-A. Bildposition und Größe im Frame gleich halten (Match über Form und Licht).
  2. Tonbrücke: Das Soul-Intervall aus 00-D klingt über den Schnitt hinaus. Die Regen-Ebene wird ab ca. 00:01:36:00 (C00) gefiltert und geht bis ca. 00:00:04:00 (C01) in leisen Wind über. Kein harter Pegelsprung am Schnittpunkt.
  3. Kein Logo, kein Titel, keine Bibliothek beim Übergang. Prolog-Identität wird nicht verraten.
- Regel aus dem Drehbuch: Der neue Prolog ersetzt den alten Repository-Vorfilm (121,5 s) und den Fallback (52 s); niemals beide nacheinander.

## C01 – EIN WINZIGER ANFANG

| Shot | Zeit (TC von–bis, Frames) | Bild | Kamera | Dialog-IDs | Ton | Musik-Cue |
|---|---|---|---|---|---|---|
| 01-A | 00:00:00:00–00:00:17:00 (0–408) | Lichtpunkt aus C00 wird zur entfernten Erde | Bewegung verlangsamt sich in Orbitperspektive; bewusster Filmschnitt über Form/Licht, kein Echtzeit-Zoom | – | Regen → leiser Wind | `M02_BEGINNING` (zwei abstrakte Soul-Intervalle, kein Reinkarnations-Spoiler) |
| 01-B | 00:00:17:00–00:00:40:00 (408–960) | Drei kurze wortlose Ausschnitte: Hilfe beim Aufheben von Einkäufen; Kind läuft zu vertrauter Person; Arbeit im Morgengrauen; Pause über fremder Stadt | ruhig, alltäglich | VO_C01_001 (geschätzt 00:00:18:00–00:00:21:22), VO_C01_002 (geschätzt 00:00:24:00–00:00:27:10) | Umweltgeräusche wechseln als Sound-Bridges | `M02` sehr zurückhaltend |
| 01-C | 00:00:40:00–00:01:05:00 (960–1560) | Gewebeoberfläche → Innenraum des Eileiters; Größe/Zeitmaßstab filmisch markiert | Schnitt, keine Partikel-Effekte | – (Stimme schweigt) | Objektiver biologischer Filmton (Strömung, Flüssigkeit) | – |
| 01-D | 00:01:05:00–00:01:20:00 (1560–1920) | Schwarzes Titelbild „GENESIS – DER KREISLAUF DES LEBENS“, darunter „Jede Entscheidung hinterlässt ein Echo.“ Kurze Stille, dann „Beliebige Taste drücken“ | statisch | – (nur Bildschirmtext) | „langsamer Atemzug der Musik“, dann Stille | atmosphärischer Chor **erst beim Titel** |

Übergabe danach: Hauptmenü (Neues Leben / Fortsetzen / Lebensarchiv / Einstellungen / Barrierefreiheit / Mitwirkende / Beenden). Bei „Neues Leben“ Kapitelkarte „KAPITEL I – DER ANFANG“. Skip mit Zweifachbestätigung, ohne Storyverlust.

## Für C20 einzufrierende C00-Masterdateien

Grundlage: „C20 darf C00 bild-/tonidentisch replayen“; „Keine Szene mischt 2026-Prolog-Audio mit einem abweichend neu aufgenommenen C20-O-Ton“; „Sein Gesicht wird für die C20-Wiederaufnahme digital exakt reproduzierbar archiviert“.

Nach der Abnahme von C00 werden diese Dateien eingefroren (schreibgeschützt, Git LFS, Tag z. B. `c00-master-v1`). Danach darf nichts davon geändert werden; Änderungen nur per Änderungsantrag, der C00 **und** C20 betrifft.

| # | Master | Zweck |
|---|---|---|
| 1 | Dialog-Waves VO_C00_001 … 008, unbearbeitet und final geschnitten (WAV, 48 kHz / 24 bit) | Originalton; C20 nutzt 001, 002, 006 |
| 2 | Atmo- und Foley-Stems von 00-B und 00-C (Regen, Laken, Atem, Straße) | gleiche Tonumgebung in C20 |
| 3 | Final-Mix-Stems C00 (Dialog, Atmo, Foley, Musik getrennt) | Null-Test und Neu-Mischung ohne Neuaufnahme |
| 4 | Soul-Intervall-Master aus 00-D | gemeinsamer Kern für C17/C20 |
| 5 | Sequencer-Asset C00 inkl. Shots 00-B und 00-C (Kamera, Brennweite, Fokus, Licht) | gleiche Bilder in C20 |
| 6 | Charakter-Master Mann und Tochter (Mesh, Rig, Gesichtsanimation/Lipsync-Track, Materialien, Haare, Kleidung) | „gleiches Gesicht, keine Doppelgängerfigur“ |
| 7 | Set-Master Schlafzimmer, Regenfenster, Fotografie, Licht-Setup | „gleiches Licht, gleiches Regenfenster, gleiche Fotografie“ |
| 8 | Referenz-Render 00-B und 00-C als verlustfreie Frame-Folge (z. B. EXR oder PNG 16 bit) plus ProRes-Vorschau | Bildvergleich |
| 9 | Untertitel-Datei C00 (SUB_C00_001 … 008) | gleicher Text in C20 |
| 10 | Manifest mit SHA256 aller obigen Dateien, UE-Version, Plugin-Versionen, Render-Einstellungen | Nachweis |

## Nachweisverfahren C00 = C20 (Reprise)

1. **Prüfsummen:** SHA256 jeder eingefrorenen Datei ins Manifest. Das C20-Sequencer-Asset darf auf die Dialog-Waves 001/002/006 nur **verweisen** (gleiche Asset-Referenz, keine Kopie). Prüfschritt: Asset-Referenzen auslesen und SHA256 der verwendeten Dateien mit dem Manifest vergleichen. Muss 100 % gleich sein.
2. **Null-Test beim Ton:** Den Dialog-Stem aus dem C20-Render an den Stellen der Reprise ausschneiden, auf Sample genau an das C00-Original legen, eine Spur invertieren und summieren. Erwartung: Restsignal digital Null (bei identischer Kette). Wenn in C20 bewusst anders gemischt wird (z. B. Hall), wird der Null-Test am **Dialog-Stem vor dem Mix** gemacht und die Abweichung im Protokoll begründet. Zusätzlich Lautheit (LUFS) und Start-Sample jeder Zeile protokollieren.
3. **Bildvergleich Frame für Frame:** Gleiche Frames aus C00 (00-B/00-C) und C20 (20-B) mit gleichen Render-Einstellungen rendern. Pro Frame vergleichen: pixelgleicher Hash; falls Echtzeit-Rendering nicht deterministisch ist (Temporal AA, Partikel, Regen), stattdessen PSNR und SSIM mit vorher festgelegter Schwelle (z. B. SSIM ≥ 0,99, wird mit QA festgelegt) plus Differenzbild. Abweichende Frames mit Nummer melden.
4. **Timing:** Für jede Reprise-Zeile Start- und End-Frame in C00 und in C20 notieren. Dauer muss auf das Frame gleich sein.
5. **Protokoll:** Bericht mit Datum, Build-Version, Manifest-Hash, Ergebnissen 1–4 und Freigabe durch eine zweite Person. Erst dann gilt laut Paket das Thema „C00/C20 Replay“ als erledigt („nur tatsächliche identische Medien-Fingerprints … schließen das Thema“).
