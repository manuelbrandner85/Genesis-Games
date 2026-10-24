# FAB-ASSET-PLAN-001 – Kleidung und Assets für C00 und künftige Bewohner

Status: **APPROVED_IN_CHAT 2026-10-25**. Der Nutzer schrieb im Chat: "FAB-ASSET-PLAN-001 freigegeben. Ich lege die Einträge in meine Fab-Bibliothek, dann importiere und baue ein." Die Lizenzprüfung je Eintrag (Schritt 4) bleibt trotzdem Pflicht.

Regie 2026-10-25: Alle Figuren in GENESIS bekommen passende, fotorealistische Kleidung von Fab, auch künftige Bewohner. Dazu kommen nach Möglichkeit passende Umgebungs-Assets.

## Ablauf

1. **Bibliothek (Nutzer):** Der Nutzer meldet sich bei Fab an und legt die Einträge in seine Bibliothek ("Zur Bibliothek hinzufügen"). Damit nimmt er die Lizenz in seinem Konto an. Claude meldet sich nicht an und nimmt keine Lizenzen an.
2. **Import (Claude):** Claude holt die Einträge im Unreal-Editor über das Fab-Fenster ("Zu Projekt hinzufügen") nach `Content/Fab/...`. Dort bleiben sie lokal; sie sind gitignored, weil das Repo öffentlich ist.
3. **Wardrobe-Register (Claude):** Claude legt eine Garderobe in `docs/v4_2/WARDROBE_REGISTER.json` an. Darin stehen nur IDs, Lizenz, Herkunft und die Zuordnung Rolle → Outfit, keine Assets.
4. **Lizenzprüfung vor jeder Nutzung im Spiel:** Die Lizenz wird je Eintrag auf der angemeldeten Fab-Seite abgelesen und eingetragen.
   - Ohne Anmeldung zeigt Fab "Lizenzbedingungen: -".
   - "Persönlich" heißt: nicht kommerziell, nur für Tests.
   - "Standard" heißt: für das Spiel nutzbar.

## A. Kleidung, MetaHuman-nativ (Epic Games, kostenlos)

Alle Einträge stammen von Epic, die Lizenz ist voraussichtlich Standard.

| Eintrag | Einsatz |
|---|---|
| MetaHuman Fashion Starter Kit | Grundgarderobe, Vorlagen |
| MetaHuman Clothing Construction Presets (Set of 4 / Set of 2) | eigene Kleidungsteile auf MetaHuman-Körper |
| MetaHuman T Shirt Variants | Mann C00 (navy) |
| MetaHuman Tucked T Shirt Variants | Alltagsbewohner |
| MetaHuman Sweater | Tochter C00 (über der Bluse) |
| MetaHuman Hoodie | jüngere Bewohner |
| MetaHuman Jeans | Bewohner allgemein |
| MetaHuman Slim Jeans Variants | Tochter C00 |
| MetaHuman Cargo Pants | Arbeiter, Handwerker |
| MetaHuman Shorts | Sommer |
| MetaHuman Crop Top Variants | jüngere Bewohnerinnen |
| MetaHuman Boots | Winter, Arbeit |
| MetaHuman Loafers | Büro, ältere Bewohner |
| MetaHuman Flats | Tochter C00 |
| MetaHuman Techwear Outfit | nur zum Testen, für 2026 eher unpassend |

## B. Kleidung von Drittanbietern (Lizenz offen, erst prüfen)

| Eintrag | Anbieter | Einsatz |
|---|---|---|
| Altena Blouse | QuingKhaos | Tochter C00, Bluse |
| The Clarkston Carpenter Pants | QuingKhaos | Handwerker |
| Shirt V-neck with rolled sleeves | Nyanpasinka | Alltag |

## C. Umgebung C00 / Wohnungen 2026

| Eintrag | Anbieter | Einsatz | Hinweis |
|---|---|---|---|
| ArchViz Interior | Epic Games | Möbel, Materialien für Wohnungen | Lizenz voraussichtlich Standard |
| Luxury Modern Bedroom Interior | 3dShowdown | nur Material-/Bettwäsche-Referenz | gltf/Blender; Lizenz "-" und KI-Nutzung "Nein"; Luxusstil passt nicht zum Neubau-Zimmer |
| Quixel-Megascans-Einträge (Holz, Stoffe, Putz) | Quixel | Oberflächen fotorealistisch | je Eintrag prüfen |

## Grenzen

- Die Figuren bleiben preview-only: Animieren geht erst nach Freigabe des Epic-Cloud-Auto-Rigs. Die Kleidung lässt sich trotzdem lokal anziehen und rendern.
- Fotorealismus ist das Ziel. Jede Figur und jedes Zimmer bekommt vor der Abnahme einen Reality Check mit Render.
