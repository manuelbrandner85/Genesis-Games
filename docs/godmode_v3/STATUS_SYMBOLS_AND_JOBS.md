# Auftragsstatus – keine erfundenen Fertigstellungen

Einheitliche Bezeichnungen: `SPECIFIED` (Spezifikation), `NOT_RUN` (kein Test), `BLOCKED_SOURCE` (Quelle fehlt), `BLOCKED_TOOL` (Software/Connection fehlt), `WAITING_APPROVAL` (Freigabe offen), `BUILT_UNTESTED` (Datei vorhanden), `ENGINE_VERIFIED` (realer Engine-Test nachgewiesen), `HUMAN_REVIEWED` (Unabhängige Sicht-/Spielprüfung), `ACCEPTED` (Game Director hat den dokumentierten WorkID abgenommen), `FAILED` (Test fehlgeschlagen).

Kein Agent darf seine eigene Erstellung als „ACCEPTED“ deklarieren; QA und Game Director entscheiden. Ein Toolcheck kann `ENGINE_VERIFIED` nur für genau diese Aktion stützen (z. B. Asset-Laden), **nicht** den Schluss zulassen, ein ganzes Spiel sei fertig.

Kompakter Statusbericht: `Aktiver WorkID / Quelle+Hash / Agent / beabsichtigte Änderung / tatsächliche Dateien / Kommandos+Exit-Code / echter UE-/Blender-Test / nachgewiesene Probleme / QA Gate / nächste Freigabe`. Bei unterbrochenen Sessions aus Dateien/Laufprotokollen rekonstruieren, nicht aus Gedächtnisphantasien.
