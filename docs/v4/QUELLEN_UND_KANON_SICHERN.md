# Source Lock: Original GENESIS ist wichtiger als generierter Content

## Das fehlt im Paket (und darf NICHT von Claude erfunden werden)
- Freigegebene **Original-Spielbibel** samt vollständiger Kapitel-/Missionsdetails und finalem Freigabevermerk.
- Vollständige **C00–C21 Script-Lock**-Quellen. Eine `GENESIS_ScriptLock_11_Drehbuch_v1.1.md` wurde als Bibliotheksdokument identifiziert, war für dieses Paket jedoch nicht als Originaldatei exportierbar und bleibt deshalb NICHT eingebettet. Dort wurde sie als Script-Lock-Kandidat ohne endgültige Freigabe geführt.
- Ggf. `J00–J24`, V61/V62-Pakete, eigenständige Assetregister, Voice-Lizenzen, freigegebene Bildreferenzen und Original-C00-Video/-Ton. Bestandsaufnahme und menschliche Freigabe nötig.
- GAMEFORGE Verbesserung 01 und 02 als *vollständige* Originaldateien, falls nicht im Projektverzeichnis verfügbar.

## Source-Order (nicht stillschweigend zusammenführen)
1. Letzte ausdrückliche Game-Director-Entscheidung **Neustart des Codes und der Assets** – Story unverändert.
2. Letzte ausdrückliche Weltregel (19.10.2026): keine wählbaren Epochen; kontinuierliche Hauptwelt ab 2026, Wiedergeburt in fortlaufender Welt; originale C21-Finale-Regel bleibt bis expliziter Konfliktlösung unverändert.
3. Freigegebene Original-Spielbibel und tatsächlich freigegebene Script-Lock-Version, Dialoge, Aufnahmen, IDs.
4. Bestätigte Features und V2/V3-Qualitätsregeln, sofern kein Konflikt mit Kanon.
5. Nicht freigegebene Entwürfe/technische Vorschläge; werden niemals stillschweigend Kanon.

## Offen statt erfunden
- `CON33-01` für C15/C16: ältere Bibliotheksdarstellung vs. abstrakter Erinnerungsraum.
- C17: ältere Scriptfassung erwähnt eine „andere Epoche“, aber aktive Epochewahl wurde später entfernt. Script selbst nicht umschreiben.
- C21: mögliches zusätzliches Schöpfungsfinale vs. gewöhnliche Ein-Welt-Wiedergeburt; originale Finalfunktion nicht heimlich löschen.
- C00/C20: nur identisches tatsächliches Aufnahme-/Bildmaster; kein rekonstruiertes „Original“ behaupten.

## Pflichten
1. Originale getrennt in einem **nur lesbaren** Verzeichnis sichern (lokal, außerhalb öffentlichen Git-Repos, bei Bedarf Datei-Hash und erlaubte Kopie unter `canon_sources/`).
2. `tools/v4/source_audit.py --sources <PATH> --out <PATH>` ausführen, Dateien + SHA256 protokollieren. Freigabestatus manuell prüfen; automatischer Audit bestätigt **nicht** finale Freigabe.
3. `docs/v4/CANON_SOURCE_REGISTER.example.json` ausfüllen und Quellkonflikte im Bericht lassen. Keine sensible oder nicht lizenzierte Quelle in ein öffentliches Repo pushen.
4. Änderungen an gesperrten Text-/Bild-/Ton-Originalen verweigern, neue Variationen als `DRAFT_NEEDS_APPROVAL` markieren.
5. Falls kein Original vorhanden: nur generische Projekttechnik (Build, Input, Testmap, Export-Smoketest), kein finales Kapitel, NPC-Lore, Quests, Marketingbilder.
