"""Baut aus den Merch-STLs (export/merch/<name>__<objekt>__<farbe>.stl) je Modell eine 3MF fuer Bambu Studio /
PrusaSlicer: ein Objekt je Druckobjekt, darin ein Teil je Farbe mit fest zugeordnetem Filament.

Aufruf:   python tools/make_3mf_merch.py [namensteil ...]
Ergebnis: export/merch/<name>.3mf und export/merch/FILAMENTE.txt (welche Filament-Nummer welche Farbe ist)
"""
import glob
import os
import struct
import sys

import make_3mf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MERCH = os.path.join(ROOT, 'export', 'merch')

# Reihenfolge wie in models/Merch/me_common.py (FARBEN)
FARBEN = ['weiss', 'dunkel', 'mittel', 'neon', 'anthrazit', 'schwarz', 'grau', 'rot', 'gelb']
KLARNAME = {'weiss': 'Weiss', 'dunkel': 'Experience Green #075033', 'mittel': 'Progressive Green #23A96A',
            'neon': 'Future Green #2FFB95', 'anthrazit': 'Anthrazit', 'schwarz': 'Schwarz', 'grau': 'Grau',
            'rot': 'Rot', 'gelb': 'Gelb'}


# Chip-Satz: derselbe Chip viermal auf einer Platte, je Grundfarbe sind die Farben der Einlagen umgehaengt.
# Grundfarbe -> {Farbe im Ausgangsmodell (weisser Chip): Farbe im Satz}
CHIPSATZ_BASIS = 'chip_logo_seit2004'
CHIPSATZ = [
    ('weiss', {'weiss': 'weiss', 'dunkel': 'dunkel', 'mittel': 'mittel'}, (-15.0, 15.0)),
    ('dunkel', {'weiss': 'dunkel', 'dunkel': 'weiss', 'mittel': 'neon'}, (15.0, 15.0)),
    ('mittel', {'weiss': 'mittel', 'dunkel': 'weiss', 'mittel': 'dunkel'}, (-15.0, -15.0)),
    ('neon', {'weiss': 'neon', 'dunkel': 'dunkel', 'mittel': 'weiss'}, (15.0, -15.0)),
]


def stl_schreiben(path, tris):
    with open(path, 'wb') as f:
        f.write(b'Merch STL (mm)'.ljust(80, b' '))
        f.write(struct.pack('<I', len(tris)))
        for a, b, c in tris:
            f.write(struct.pack('<12fH', 0.0, 0.0, 0.0, *a, *b, *c, 0))


def chipsatz():
    """Schreibt die STLs fuer chipsatz_logo_seit2004 (vier Chips in vier Farbwelten) aus dem weissen Chip."""
    name = CHIPSATZ_BASIS.replace('chip_', 'chipsatz_')
    for old in glob.glob(os.path.join(MERCH, name + '__*.stl')):
        os.remove(old)
    quelle = {}
    for f in ('weiss', 'dunkel', 'mittel'):
        p = os.path.join(MERCH, '%s__chip__%s.stl' % (CHIPSATZ_BASIS, f))
        if not os.path.exists(p):
            return
        quelle[f] = make_3mf.read_stl(p)
    for grund, karte, (dx, dy) in CHIPSATZ:
        ziel = {}
        for f, tris in quelle.items():
            ziel.setdefault(karte[f], []).extend(
                tuple((p[0] + dx, p[1] + dy, p[2]) for p in t) for t in tris)
        for f, tris in ziel.items():
            stl_schreiben(os.path.join(MERCH, '%s__chip_%s__%s.stl' % (name, grund, f)), tris)


def sammeln():
    modelle = {}
    for path in sorted(glob.glob(os.path.join(MERCH, '*__*__*.stl'))):
        name, objekt, farbe = os.path.basename(path)[:-4].split('__')
        modelle.setdefault(name, {}).setdefault(objekt, []).append(farbe)
    return modelle


def main(filter_):
    make_3mf.EXPORT = MERCH
    chipsatz()
    zeilen = ['Filament-Nummern je 3MF (im Slicer den Nummern diese Farben zuweisen)', '']
    for name, objekte in sammeln().items():
        if filter_ and not any(f in name for f in filter_):
            continue
        benutzt = [f for f in FARBEN if any(f in fs for fs in objekte.values())]
        nr = {f: i + 1 for i, f in enumerate(benutzt)}
        jobs = []
        for objekt, fs in objekte.items():
            teile = [('%s__%s__%s.stl' % (name, objekt, f), '%s %s' % (objekt, f), nr[f])
                     for f in FARBEN if f in fs]
            jobs.append((objekt, teile))
        print(name)
        make_3mf.build(name, jobs)
        zeilen.append('%s.3mf: %s' % (name, ', '.join('%d = %s' % (nr[f], KLARNAME[f]) for f in benutzt)))
    if not filter_:
        with open(os.path.join(MERCH, 'FILAMENTE.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(zeilen) + '\n')


if __name__ == '__main__':
    main(sys.argv[1:])
