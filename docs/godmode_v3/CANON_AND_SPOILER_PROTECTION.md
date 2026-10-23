# GENESIS Storykanon: Schutzkonzept & Freigabe

**Oberste Regel:** aktueller ausdrücklicher Nutzerentscheid vor freigegebenem Originaldokument vor Konzept-/Masterprompts; bloße KI-Antworten sind keine originale Storyquelle. Nicht automatisch Konflikte lösen.

Geschützt: C00–C21 Szenen, Shot-/Dialogtexte, mysteriöser Prolog 2026 (alter Mann + Tochter), gleiche Film-/Audioversion bei C20, C19/C20 Offenbarungen, J00–J24 freigegebene Jenseits-Regeln, erste spielbare Inkarnation 2026, chronologische fortlaufende Welt, freiwilliges Rebirth oder Jenseits, keine Epochenauswahl, `SoulID` persistiert, neue `LifeID`.

P0-Konflikte: ScriptLock v1.1 kann noch Freigabekandidat sein; C15/C16 CON33-01; C17 Epochentext trotz Epochenentfernung; C21-Finale vs Ein-Welt-Definition. `CHANGE_BLOCKED_OUT_OF_SCOPE` und `WAITING_DIRECTOR_DECISION` wo nötig. Keine heimliche Script-Migration.

Vor Eingriff: Baseline-SHA256 manifestieren (`tools/v3/canon_guard.py baseline` nur in freigegebenem Git-Repo, Pfade explizit), nach Arbeit SHA prüfen (`verify`). Vergleich ist **keine** vollständige Sandbox und verhindert keine direkten Änderungen; native OS-Git-Rechte und Reviews zusätzlich nutzen. Ohne existierende Baseline keine PASS-Meldung. V2 PreToolUse ist nur Defense-in-Depth; Skript kann keine beliebigen Shell-Umgehungen verhindern.
