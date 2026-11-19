# Bechtle-Merch aus dem 3D-Drucker

Neun Merch-Entwürfe mit Bechtle-Bezug, komplett per Python-Skript über die Fusion-API modelliert und mehrfarbig für den 3D-Druck vorbereitet.

**Übersicht:** https://tschortsch3711.github.io/bechtle-3d-druck/

Die Modelle: Token mit Schlüsselring, Einkaufswagenchips, Uptime-Untersetzer, Handyständer „On Call“, Deploy-Würfel, HE-Lineal, Rack-Stiftehalter, Drehzähler „Stabiler Betrieb“ und Zahnrad-Trio „Plan Build Run“. Jedes Modell gibt es mit Logo und als neutrale Fassung.

## Aufbau

| Ordner | Inhalt |
| --- | --- |
| `models/Merch/` | Fusion-Skripte, eins pro Modell (`me_*.py`), Start über `Merch.py` |
| `models/Mitbringsel/` | gemeinsame Fusion-Helfer (`mb_common.py`), Logo-Aufbau (`mb_logo.py`) und Logo-Quelle |
| `tools/` | 3MF-Erzeugung für Bambu Studio (`make_3mf_merch.py`, `make_3mf_platten.py`), STL-Prüfung |
| `preview/merch/` | Vorschaubilder aus Fusion und Slicer-Vergleiche |
| `galerie/` | lokale Galerie mit Details zu allen Varianten (`merch.html`) |
| `docs/` | Übersichtsseite (GitHub Pages) |

## Ablauf

1. In Fusion das Skript `models/Merch/Merch.py` ausführen. Es baut alle Modelle und exportiert STL und F3D nach `export/merch/`.
2. `python tools/make_3mf_merch.py` erzeugt je Modell ein Bambu-Studio-Projekt mit fest zugeordneten Filamenten.
3. `python tools/make_3mf_platten.py` legt alle Varianten in ein Projekt, eine Platte je Kategorie.

Farben: Weiß, Experience Green, Progressive Green, Future Green, dazu Anthrazit und Schwarz für den Stiftehalter. Gedruckt wird FDM mit 0,4- oder 0,2-mm-Düse, mehrfarbig per AMS, ohne Stützen.

## Lizenz

Der Code (Fusion-Skripte, Tools, Webseiten) steht unter der MIT-Lizenz, siehe `LICENSE`. Die Lizenz gilt nicht für Name und Logo der Bechtle AG: Dafür werden hier keine Rechte eingeräumt.

## Rechtlicher Hinweis

Dies ist ein privates, nicht kommerzielles Fan- und Lernprojekt. Es steht in keiner Verbindung zur Bechtle AG und ist von ihr weder beauftragt noch geprüft oder unterstützt.

„Bechtle“ und das Bechtle-Logo sind Marken der Bechtle AG. Die Logo-Datei stammt von Wikimedia Commons (Quelle in `models/Mitbringsel/logo/QUELLE.md`); der dort genannte Status „Public domain“ betrifft nur das Urheberrecht, die Markenrechte bleiben bestehen.

Die Modelle mit Logo sind nur für den privaten Gebrauch gedacht. Wer sie verkaufen, verteilen oder werblich nutzen will, braucht die Zustimmung der Bechtle AG. Für eigene Zwecke gibt es zu jedem Modell eine neutrale Fassung ohne Logo.

Fragen oder ein Löschwunsch: bitte ein Issue in diesem Repo anlegen.
