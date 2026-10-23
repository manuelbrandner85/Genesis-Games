# GENESIS – Verbesserung 09: Complete Story & Source Vault

**Bestätigt:** JA zu allen zehn Verbesserungen am 23.10.2026.
**Status:** geplanter, fachlich freigegebener Entwicklungsumfang; keine hier erfolgte UE-Implementierung.
**Leitziel:** Originalgeschichte, neue Beschlüsse und technische Arbeit getrennt versionieren – keine erfundenen Kapitel.
**Gültigkeit:** nur bestehendes `manuelbrandner85/Genesis-Games`, Claude Code als Entwicklungsleitung, keine Story-Umschreibung.

### Produktionsfunktionen
1. Originalquellenregister: Spielbibel, ScriptLock 1.1, C00–C21, J00–J24, V61/V62, spätere Entscheidungen, Visual Reference Vault, Audio-Cues.
2. Quellhierarchie: jüngster ausdrücklicher Nutzerbeschluss > getrennte gezielte Freigabe > Original Story > ältere Vorschläge; Konflikte sichtbar protokollieren, nie automatisch überschreiben.
3. In diesem Paket liegt Original GAMEFORGE-03 bytegetreu mit SHA-256; andere vollständige Storydateien sind **nicht** enthalten.
4. Vor Story-Arbeit lokale Originaldateien suchen, Hash erfassen, Vollständigkeit und explizite Finalfreigabe prüfen.
5. Keine Fehlstände durch Prompt-Nacherzählung „auffüllen“, fehlende Quellen ergeben `BLOCKED_SOURCE_MISSING`.
6. Geschützte 22 Szenen unverändert; C20 Identität von C00 sowie C19 Offenbarungsgrenzen.
7. GENESIS-Erststart 2026, spätere Todeswahl Jenseits/ freiwillige Wiedergeburt in fortlaufend alternder Hauptwelt; keine wählbaren Geschichtsepochen.
8. C21 Finale bleibt nach altem Original unüberarbeitet; Konflikt mit Ein-Welt-Regel dokumentieren, nicht automatisch lösen.
9. C15/C16 Raum-/Bibliothek-Konflikt `CON33-01` bleibt offene Regieentscheidung.
10. Verbesserungen 1–3 und 10 neue Produktionsverbesserungen sind Entwicklungsfreigaben, **keine** Textänderungsfreigabe für die Film-/Story-Dateien.
11. SourceMap: `claim → Datei → Revision → Abschnitt/Zeile → Freigabe → Implementierungs-WorkID`.
12. Diff-Guard: geschützte Pfade und Story-Strings sind in Hook-Policy als Warn-/Sperrklasse geführt; zusätzliche human-review erforderlich.
13. Externe Assets zusätzlich mit Lizenz, Urheber, SourceURL, Export/Reuse-Recht, Credits-Anforderung.
14. Keine Fremdrepo-Datei (AION) als alternative Spielbibel verwenden.

### Abnahme
`source_index.json` mit Original-SHA und Freigaben; `CANON_CONFLICTS.md`; Trace-Matrix C00–C21 und J00–J24; sichtbarer `BLOCKED`-Status bei Unklarheiten. Schutz bedeutet nicht, dass ein Hook niemals umgangen werden kann – Code Review bleibt Pflicht.

### Technischer Produktionsauftrag
Arbeite mit dem vorhandenen Repo, GAMEFORGE StudioBrain und Character Creation 4.0, sofern tatsächlich vorhanden. Ermittle Basiscommit, freigegebene Quellen und installierte Werkzeuge. Dokumentiere Architektur, konkrete Dateien, Tests und Evidenz. Führe nur genehmigte ungefährliche Schritte aus; für riskante Änderungen explizite Freigabe. Übergebe jeden Arbeitsschritt an unabhängige QA. `NOT_IMPLEMENTED` bleibt sichtbar, bis ein echter Editor-/Runtime-Nachweis vorliegt.

### Quellenverzeichnis als Schutzschicht
Jede Originalquelle erhält `source_id`, `path`, `sha256`, `timestamp`, `revision`, `publisher/owner`, `approval_state`, `locking_scope` und `supersedes`. Kanonbehauptungen referenzieren eine konkrete Datei samt Abschnitt/ID. Die Herkunft und die Unterschiede zwischen „vom Nutzer genehmigt“, „von einer KI vorgeschlagen“ und „in Unreal umgesetzt“ bleiben in Berichten getrennt. Widersprüche müssen sichtbar zum Game Director, niemals durch stille Prompt-Interpretation verschwinden.

**Unterschiedliche Versionen:** Der Vorschlag des ScriptLock 1.1 ist als Dokument vorhanden (außerhalb dieses ZIP), seine abschließende Freigabe war in früheren Dokumenten ausstehend. Die spätere Ein-Welt-Entscheidung ersetzt die auswählbaren Epochen, ohne zu erlauben, C00–C21 oder C21-Finale automatisch umzuschreiben. GAMEFORGE 03 ist vollständig beigelegt und integritätsgeprüft; StudioBrain 01/Character Creation 02 müssen aus zugänglichen Originalen gelesen werden, bevor ein Agent „vollständig integriert“ sagt.

**Schutz bei Produktion:** In `source_index` deklarierte gesperrte Abschnitte werden für Code-/Storydiffs referenziert. Ein Hook schützt bestimmte Dateinamen best-effort, aber nicht beliebige API-Aufrufe. Daher vor Merge Git-Diff, Originalhashes, Story/Asset-Mapping und manuelle StoryGuardian-Review vergleichen. Renderings können die Originaldialoge respektieren und trotzdem kreative Abnahme benötigen.

**QA-Fälle:** A1 Originalquellen vollständig; A2 korrekte Priorität jüngster Beschlüsse; A3 C00/20 unverändert; A4 C19 Spoiler-Gate; A5 C21-Konflikt offen und nicht überspielt; A6 Contentrechte vorhanden; A7 jede offene Kanon-Frage hat eine ausdrücklich protokollierte Freigabeinstanz.

### Abhängigkeiten / nächste Umsetzung
Vor Story-/Charakterarbeit müssen Originaldateien lokal gelesen und Freigabestatus explizit geklärt werden. WorkIDs dürfen erst nach Architektur-/Kanonabgleich in reale Dateiedits umgesetzt werden.
