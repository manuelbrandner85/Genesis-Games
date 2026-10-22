# GLB-Grundmodelle und Turnarounds

Quelle: Release `handover-v62`, Ordner `03_DIREKT_NUTZBARE_3D_GEOMETRIE` im Paket `GENESIS_V62.zip`.

38 Dateien unter `GLB/` und 38 Tafeln unter `TURNAROUNDS_AUS_GLBS/`. Jede GLB-SHA256 ist gleich der Zeile in `04_PRODUKTIONSREGISTER/38_GLB_QUELLEN.csv` und gleich der Zeile in `05_PRUEFBERICHT/SHA256SUMS.txt`. Die Prüfung ist `FILE_VALIDATED` für die Bytes.

Das Register nennt jede Datei `GRAYBOX_OR_PROXY`. `BlenderValidation`, `UnrealIntegration`, `MaterialApproval`, `ScaleApproval` und `RigApproval` stehen dort auf `NOT_RUN`. `HeroReferenceReplacement` steht auf `NOT_AUTHORIZED`. Es gibt in der Kette keine `.blend`-Masterdatei. Die Tafeln sind Ansichten dieser Grundgeometrie, kein fertiges Modell.

`VS01_R04_BRUECKE_004.glb` und `VS01_R04_BRUECKE_005.glb` haben dieselbe SHA256 `aa103052582d842c302cd50d7bd54d6fb79567bd5fdf1914aee93699df344b7e`. Beide Dateien bleiben erhalten.

Die 196-Zeilen des Testslice-Registers führen die acht NPC-GLBs weiterhin als `NO_VERIFIED_GLB`. Eine Graybox-Datei ist dort keine verifizierte Skeletal-Mastergeometrie. `GameReady` ist für alle 196 Zeilen `NO_EVIDENCE`.

Git LFS ist über die vorhandenen Attribute `*.glb` und `*.png` gebunden.
