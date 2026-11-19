# Bechtle-Merch aus dem 3D-Drucker

Neun Merch-Entwürfe mit Bechtle-Bezug, komplett per Python-Skript über die Fusion-API modelliert und mehrfarbig für den 3D-Druck vorbereitet.

**Übersicht:** https://tschortsch3711.github.io/bechtle-3d-merch/

Die Modelle: Token mit Schlüsselring, Einkaufswagenchips, Uptime-Untersetzer, Handyständer „On Call“, Deploy-Würfel, HE-Lineal, Rack-Stiftehalter, Drehzähler „Stabiler Betrieb“ und Zahnrad-Trio „Plan Build Run“. Jedes Modell gibt es mit Logo und als neutrale Fassung.

## Aufbau

| Ordner | Inhalt |
| --- | --- |
| `models/Merch/` | Fusion-Skripte, eins pro Modell (`me_*.py`), Start über `Merch.py` |
| `models/Mitbringsel/` | gemeinsame Fusion-Helfer (`mb_common.py`), Logo-Aufbau (`mb_logo.py`) und Logo-Quelle |
| `tools/` | 3MF-Erzeugung für Bambu Studio (`make_3mf_merch.py`, `make_3mf_platten.py`), STL-Prüfung |
| `preview/merch/` | Vorschaubilder aus Fusion und Slicer-Vergleiche |
| `galerie/` | lokale Galerie mit Details zu allen Varianten (`merch.html`) |
| `site/` | Quelle der Übersichtsseite (GitHub Pages) |

## Ablauf

1. In Fusion das Skript `models/Merch/Merch.py` ausführen. Es baut alle Modelle und exportiert STL und F3D nach `export/merch/`.
2. `python tools/make_3mf_merch.py` erzeugt je Modell ein Bambu-Studio-Projekt mit fest zugeordneten Filamenten.
3. `python tools/make_3mf_platten.py` legt alle Varianten in ein Projekt, eine Platte je Kategorie.

Farben: Weiß, Experience Green, Progressive Green, Future Green, dazu Anthrazit und Schwarz für den Stiftehalter. Gedruckt wird FDM mit 0,4- oder 0,2-mm-Düse, mehrfarbig per AMS, ohne Stützen.

## Hinweis

Private Entwürfe, kein offizielles Produkt der Bechtle AG. Name und Logo sind Marken der Bechtle AG. Die Logo-Quelle steht in `models/Mitbringsel/logo/QUELLE.md`.
