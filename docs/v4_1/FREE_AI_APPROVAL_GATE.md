# FREE AI APPROVAL GATE

**Vor jedem Download/Install:**
- eindeutige Plan-ID, geprüftes Tool (Name, URL, Tag/Commit) sowie Modell/gewählte Gewichte,
- Code-/Gewichts-/Stimmen-/Datensatz-Lizenzstatus, EU-/kommerzielle Rechte,
- lokales Hardwareprofil und Speicherbedarf,
- exakte Kommandos, Zielordner, Netzwerkziele, Rollback,
- bestätigte Nutzerentscheidung für DIESEN Plan.

`approval_gate.py` speichert eine manuell bestandsgeprüfte Freigabe-Bestätigung. Das Tool installiert **nichts**; es validiert nur. Keine automatisch erzeugten Approval-Einträge mit `approved_by=user` vortäuschen. Bestätigung über interaktive Konsoleneingabe/anderes explizites menschliches Verfahren. Bei Änderung des Plan-Hashes wird die Freigabe ungültig.

## Freigabetypen
`READ_ONLY`, `LOCAL_INFERENCE`, `DOWNLOAD_MODEL`, `INSTALL_SOFTWARE`, `NETWORK_SERVICE`, `UPGRADE_DRIVER`, `EXTERNAL_API`, `PUBLISH`, `PAYMENT`. Die drei letzten standardmäßig verweigert; niemals aus einer generellen Toolfreigabe ableiten.

## Claude Code PreToolUse-Guard
Für offensichtliche Installations-/Download-Kommandos prüft `.claude/settings.json` den Hook `tools/v4_1/hooks/free_ai_pretool_guard.py`. Ein freigegebenes `*.json`-Planfile plus gleichnamiges `*.approval.json`-Receipt liegt unter `.genesis_approvals/`, das Claude nicht eigenständig ausfüllen darf. Der geplante Befehl muss wörtlich dem tatsächlichen Shell-Kommando entsprechen; plan_hash muss stimmen. Der Guard ist **nur Zusatzschutz**, kann umgangen werden und ersetzt keine menschliche Aufsicht oder Betriebssystemrechte.
