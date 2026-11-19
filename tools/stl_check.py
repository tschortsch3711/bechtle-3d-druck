"""Druckpruefung fuer die Merch-STLs (export/merch/<name>__<objekt>__<farbe>.stl).

Je Druckobjekt (alle Farben zusammen): Box, Volumen je Farbe, Auflageflaeche auf dem Bett und Ueberhaenge.
- "Decke": waagerechte, nach unten zeigende Flaeche ueber dem Bett (Bruecke oder echter Ueberhang). Flaechen, an
  denen nur zwei Farben aufeinanderliegen (Einlagen), heben sich auf und zaehlen nicht.
- "Schraege": nach unten zeigende Flaeche, flacher als 45 Grad zur Waagerechten gemessen (ohne Stuetzen kritisch).

Aufruf: python tools/stl_check.py <namensteil> [...]
"""
import glob
import math
import os
import sys
from collections import defaultdict

from stl_info import read_stl

MERCH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'export', 'merch'))


def check(name):
    objekte = defaultdict(dict)
    for path in sorted(glob.glob(os.path.join(MERCH, name + '__*__*.stl'))):
        _, objekt, farbe = os.path.basename(path)[:-4].split('__')
        objekte[objekt][farbe] = read_stl(path)
    print('== %s' % name)
    for objekt, farben in objekte.items():
        allp = [p for tris in farben.values() for t in tris for p in t]
        mn = [min(p[i] for p in allp) for i in range(3)]
        mx = [max(p[i] for p in allp) for i in range(3)]
        print('  Objekt %s: %.2f x %.2f x %.2f mm, x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f'
              % (objekt, mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2], mn[0], mx[0], mn[1], mx[1], mn[2], mx[2]))
        eben = defaultdict(float)       # z -> Flaeche nach unten minus Flaeche nach oben (waagerechte Flaechen)
        schraeg = defaultdict(float)    # z (auf 1 mm) -> Flaeche
        bett = 0.0
        for farbe, tris in farben.items():
            vol = 0.0
            for a, b, c in tris:
                ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
                vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
                nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
                ln = math.sqrt(nx * nx + ny * ny + nz * nz)
                vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                        + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
                if ln == 0:
                    continue
                area, nzn = ln / 2.0, nz / ln
                zmin = min(a[2], b[2], c[2])
                if abs(nzn) > 0.9995:
                    z = round((a[2] + b[2] + c[2]) / 3.0, 2)
                    if z - mn[2] < 0.02:
                        if nzn < 0:
                            bett += area
                    else:
                        eben[z] += area if nzn < 0 else -area
                elif nzn < -0.7072 and zmin - mn[2] > 0.3:
                    schraeg[round(zmin)] += area
            print('    %-9s %7d Dreiecke  %10.1f mm3' % (farbe, len(tris), vol))
        print('    Auflage auf dem Bett: %.0f mm2' % bett)
        decken = [(z, a) for z, a in sorted(eben.items()) if a > 0.5]
        if decken:
            print('    Decken (waagerecht nach unten, ueber dem Bett): '
                  + ', '.join('z %.2f: %.1f mm2' % (z, a) for z, a in decken))
        if schraeg:
            tot = sum(schraeg.values())
            zs = sorted(schraeg)
            print('    Schraegen flacher als 45 Grad: %.1f mm2 zwischen z %d und %d' % (tot, zs[0], zs[-1]))
        if not decken and not schraeg:
            print('    keine Ueberhaenge')


if __name__ == '__main__':
    names = set()
    for arg in sys.argv[1:]:
        for path in glob.glob(os.path.join(MERCH, '*%s*__*__*.stl' % arg)):
            names.add(os.path.basename(path).split('__')[0])
    for n in sorted(names):
        check(n)
