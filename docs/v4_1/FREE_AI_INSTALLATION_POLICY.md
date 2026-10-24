# FREE AI INSTALLATION POLICY

1. Vor Installation: GPU+RAM+Disk+Treiber+Windows/WSL+Python-Version+Tool-Lizenz+Gewichtsmodell+Folgelizenzen prüfen. Technische Mindestanforderungen nicht aus Marketing-VRAM ableiten.
2. Erstelle für JEDES Tool einen **einzelnen** Installationsplan mit Repository-URL, Commit/Tag, Downloads/GB, Hash-Verfahren, Python-/CUDA-Umgebung, Sicherheitsrisiko und Rollback.
3. **Einzelfreigabe des Users** je Plan, Version und Downloadgröße. Der Nutzer genehmigt nicht mit bloßer Zustimmung zum V4.1-Feature automatisch Installationen.
4. Kein `curl | sh`, keine unpinned Drittplugins, kein unkontrolliertes `pip install -U`, keine globalen Python-Änderungen, keine Secrets in Kommandozeilen, keinen Zugriff auf fremde lokale Ordner.
5. Separate virtuelle Umgebungen und Toolordner außerhalb des Quellcodes; Treiber nur nach zusätzlicher ausdrücklicher Freigabe. Öffentliche Dienste nie ungefragt starten. Lokale HTTP-Bindung nur 127.0.0.1, keine Firewall-Regeln öffnen.
6. Keine kostenpflichtigen Dienste, keine versteckten Cloud-Calls, keine Model Uploads und keine Sprecher-Imitationen ohne Zustimmung.
7. Nach Installation reproduzierbaren Smoke-Test durchführen; Dateipfade, Versionen, SHA, stdout/stderr, Laufzeit, GPU-Nutzung protokollieren. Bei Fehler: `NOT_READY`, nicht 'fertig'.
8. Jede neue Toolversion/Modellversion erneut lizenz- und funktionsprüfen.
9. `approval_gate.py` ist ein organisatorischer Prüfpunkt – kein kryptografischer Schutz vor einem böswilligen Prozess. Claude darf niemals selbst eine menschliche Genehmigung vortäuschen.
10. Der Auftrag kann nur dann 'unbegrenzt kostenlos' heißen, wenn keine Nutzungsgebühr anfällt; lokale Ressourcen, Strom und Hardware sind nicht kostenlos. Claude-Nutzungsgrenzen gelten weiterhin.
