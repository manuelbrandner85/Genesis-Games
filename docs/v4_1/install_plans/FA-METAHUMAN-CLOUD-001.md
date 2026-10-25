# FA-METAHUMAN-CLOUD-001 – Epic-Cloud für die C00-MetaHumans (Auto-Rig + hochauflösende Texturen)

Status: **WAITING_APPROVAL**. Diese Datei ist kein Freigabenachweis. Freigegeben wird nur im Chat, durch den Game Director.
Freigabetyp: `NETWORK_SERVICE` (Epic-Cloud über die Editor-Funktionen).
Ausdrücklich **nicht** enthalten: `EXTERNAL_API`, `PUBLISH`, `PAYMENT`.

## 1. Wozu

| Ziel | Heute lokal | Mit der Cloud |
|---|---|---|
| Alte Hände: Adern, Falten, dünne Haut; Gesicht in voller Schärfe | Vorschau-Texturen in 2K (`desired_texture_sources_resolutions`: alles Res2k), Körper ohne Feinstruktur | Textur-Synthese mit Quellen in 4K/8K für Gesicht und Körper (Albedo, Normal, Cavity, Masken) |
| Animierbare Figuren (Sterbeszene, Mimik, Lippen) | nur Gelenk-Posen im Editor; `build_meta_human` verweigert ohne Gesichtsrig | Auto-Rig erzeugt das Gesichts-Rig (DNA) → Figur lässt sich bauen und animieren |

## 2. Was zu Epic hochgeladen wird

Nach Epics Roadmap nutzen „Auto-Rigging und Textur-Synthese weiterhin die Cloud-Infrastruktur“ von Epic.

| Dienst | Funktion im Editor | Daten, die das Projekt verlassen (nach Doku und Funktionsaufruf, *nicht im Detail von Epic offengelegt*) |
|---|---|---|
| Auto-Rig | `request_auto_rigging(character, params=[MetaHumanRigType.JOINTS_ONLY, …])` | die Gesichtsgeometrie bzw. die Gesichtsparameter der Figuren MHC_C00_Mann und MHC_C00_Tochter (aus Epic-Presets, Blend-Werten und Regler-Einstellungen) |
| Textur-Synthese | Auflösung in `skin_settings.desired_texture_sources_resolutions` auf 4K/8K, dann Assemble | die Haut-Parameter: Texturindex, Farbton u/v, Sommersprossen, Akzente, Make-up |

**Nicht hochgeladen** werden:
- Fotos oder Scans echter Menschen (es gibt keine; alles stammt aus Epic-Presets),
- Story- oder Script-Texte,
- Projektdateien,
- das Repo.

**Verarbeitung:** Laut EULA dürfen Epic und seine Dienstleister die Daten „auf Servern in den USA oder anderen Ländern“ verarbeiten. Wie lange Epic sie speichert, ist öffentlich nicht beschrieben.

**Konto:** Nötig ist ein Epic-Konto. **Du meldest dich selbst im Editor an**; Claude gibt keine Zugangsdaten ein. Im Fab-Fenster bist du bereits angemeldet. Ob der MetaHuman-Dienst diese Anmeldung mitnutzt, sehe ich erst beim ersten Aufruf.

**Netzwerkziele:** Epic-Server über den Editor (MetaHuman-Plugin). Es gibt keine eigenen Skripte, keine Drittanbieter-API und keine Installation.

## 3. Kosten

Nach Epics MetaHuman-Lizenzseite ist MetaHuman Teil der normalen Unreal-Engine-Lizenz:
- **Kostenlos** bis 1 Mio. USD Umsatz,
- darüber gelten die Standardbedingungen von Unreal Engine.

Ein Preis pro Cloud-Aufruf ist nicht bekannt.

**Nicht verifiziert:** Die Lizenzseite selbst verlangt eine Anmeldung und konnte deshalb nicht direkt gelesen werden; die Angaben stammen aus dem Suchauszug der offiziellen Seite. Vor einer Veröffentlichung von GENESIS muss die Seite angemeldet gegengelesen werden (Tantiemen/Sitzplatzkosten über der Schwelle).

## 4. Lizenz und Repo

- **Lizenzrahmen:** Ab UE 5.6 gilt für den MetaHuman Creator im Editor die **Unreal Engine EULA**. Die ältere MetaHuman-Creator-EULA gilt nur noch für Versionen bis 5.5.
- **Ergebnisse:** Die erzeugten Rigs und Texturen sind Epic-Inhalte. Sie bleiben **lokal und gitignored** wie alle MHC-Assets. Ins öffentliche Repo kommen nur Skripte, IDs und Belegbilder.
- **Kanon:** Story-Kanon ist nicht berührt.

## 5. Ablauf nach Freigabe

1. Du meldest dich im Editor an, falls der Dienst danach fragt.
2. Claude sichert MHC_C00_Mann und MHC_C00_Tochter als lokale Kopie (Rollback).
3. Claude stellt die Texturauflösung auf 4K: Gesicht und Körper bei Albedo und Normal, Cavity und Masken ebenfalls 4K. 8K nur nach deiner Rückmeldung, denn 8K vervielfacht Speicherbedarf und Ladezeit.
4. Claude ruft `request_auto_rigging` für beide Figuren auf, Rig-Typ zunächst `JOINTS_ONLY`.
5. Claude baut die Figuren (`build_meta_human`) und prüft Hände und Gesicht per Nahaufnahme. Danach wird die Sterbe-Mimik als echte Animation gesetzt statt als Gelenk-Pose.
6. Bericht mit Bildern; Status `ENGINE_TESTED` erst nach echten Renders.

## 6. Rollback

- Die Sicherungskopien der beiden MHC-Assets zurückspielen.
- Die heruntergeladenen Textur- und Rig-Daten unter `/Game/Genesis/Characters/C00` löschen.
- Es gibt keine Einstellungen im System und keine Installation.

## 7. Quellen

- [Unreal Engine EULA / MetaHuman Creator EULA](https://www.unrealengine.com/en-US/eula/mhc)
- [MetaHuman License](https://www.metahuman.com/en-US/license)
- [MetaHuman Plugins Overview](https://dev.epicgames.com/documentation/metahuman/metahuman-plugins-overview-in-unreal-engine?lang=en-US)
- [Unreal Engine Public Roadmap: MetaHuman Creator in Unreal Engine](https://portal.productboard.com/epicgames/1-unreal-engine-public-roadmap/c/2024-metahuman-creator-in-unreal-engine-beta-)
