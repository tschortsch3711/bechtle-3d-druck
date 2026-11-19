"""Baut eine Bambu-Studio-3MF mit allen Merch-Varianten: je Objekt-Kategorie eine Platte (X1C, 256 x 256 mm).

Passt eine Kategorie nicht auf eine Platte oder braucht sie mehr als vier Filamente (ein AMS), kommen weitere
Platten derselben Kategorie dazu. Jede Variante behaelt die Drucklage aus Fusion (alle Teile zusammen).
Filament-Nummern gelten fuer die ganze Datei, siehe FILAMENTE am Ende der Ausgabe.

Aufruf:   python tools/make_3mf_platten.py
Ergebnis: export/merch/bechtle_merch_alle_platten.3mf
"""
import glob
import os
import uuid
import zipfile
from xml.sax.saxutils import escape

import make_3mf
from make_3mf_merch import FARBEN, KLARNAME, MERCH, chipsatz

BETT = 256.0
RAND = 8.0                  # Abstand zum Plattenrand
LUFT = 8.0                  # Abstand zwischen Varianten
MAX_FILAMENTE = 4           # ein AMS
STRIDE = BETT * 1.2         # Bambu Studio: Platten liegen im Raster mit 1/5 Plattenbreite Abstand
HEX = {'weiss': '#F3F3EF', 'dunkel': '#075033', 'mittel': '#23A96A', 'neon': '#2FFB95', 'anthrazit': '#2B3442',
       'schwarz': '#181818', 'grau': '#969CA3', 'rot': '#C83228', 'gelb': '#F0B41E'}

# (Plattenname, Auswahl ueber Modellname und Objekt)
KATEGORIEN = [
    ('Token', lambda n, o: n.startswith('token_')),
    ('Einkaufswagenchips', lambda n, o: n.startswith('chip_') or n.startswith('chipsatz_')),
    ('Uptime-Untersetzer', lambda n, o: n.startswith('untersetzer_')),
    ('Handystaender On Call', lambda n, o: n.startswith('handystaender_')),
    ('Deploy-Wuerfel', lambda n, o: n.startswith('wuerfel_')),
    ('HE-Lineal', lambda n, o: n.startswith('lineal_')),
    ('Stiftehalter', lambda n, o: n.startswith('stiftehalter_') and o == 'halter'),
    ('Stiftehalter-Blende', lambda n, o: n.startswith('stiftehalter_') and o == 'blende'),
    ('Drehzaehler', lambda n, o: n.startswith('drehzaehler_')),
    ('Zahnrad-Trio', lambda n, o: n.startswith('zahnrad_')),
]


VORLAGE = os.path.join(os.path.dirname(__file__), 'bambu', 'x1c_projekt_vorlage.json')
VORLAGE_N, VORLAGE_PLA = 4, 3                # Vorlage: 4 Filamente, Nr. 4 ist Bambu PLA Basic @BBL X1C
KEIN_FILAMENT = {'bed_exclude_area', 'printable_area', 'print_compatible_printers', 'flush_volumes_matrix'}


def _hell(h):
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def projekt_einstellungen(farben, einstellungen=None):
    """Projekt-Einstellungen aus einer Bambu-Studio-2.9-Vorlage (X1C 0.4, Prozess 0.20mm Strength MFG):
    alle Filament-Listen auf len(farben) x Bambu PLA Basic umgestellt, Farben gesetzt, Spuelmengen neu."""
    import json
    c = json.load(open(VORLAGE, encoding='utf-8'))
    n = len(farben)
    for k, v in list(c.items()):
        if not isinstance(v, list) or not v or len(v) % VORLAGE_N or k in KEIN_FILAMENT or k.startswith('machine_max_'):
            continue
        je = len(v) // VORLAGE_N                     # Werte je Filament (1, 2 Duesenvarianten, 4 oder 8)
        c[k] = v[VORLAGE_PLA * je:(VORLAGE_PLA + 1) * je] * n
    c['filament_self_index'] = [str(i + 1) for i in range(n) for _ in range(len(c['filament_self_index']) // n)]
    c['filament_colour'] = c['filament_multi_colour'] = c['default_filament_colour'] = [HEX[f] for f in farben]
    c['filament_map'] = ['1'] * n
    # Spuelmenge: von dunkel nach hell viel, sonst wenig (in Bambu Studio mit "Automatisch berechnen" verfeinerbar)
    c['flush_volumes_matrix'] = [str(0 if a == b else int(round(140 + 500 * max(0.0, _hell(HEX[b]) - _hell(HEX[a])))))
                                 for a in farben for b in farben]
    ig, ds = c['inherits_group'], c['different_settings_to_system']
    c['inherits_group'] = [ig[0]] + [''] * n + [ig[-1]]
    c['different_settings_to_system'] = [ds[0]] + [''] * n + [ds[-1]]
    if einstellungen:                            # Prozess-Werte ueberschreiben und als geaendert markieren
        c.update(einstellungen)
        geaendert = [k for k in ds[0].split(';') if k] + [k for k in einstellungen if k not in ds[0].split(';')]
        c['different_settings_to_system'][0] = ';'.join(sorted(geaendert))
    return json.dumps(c, indent=4, ensure_ascii=False)


def bbox(punkte):
    return [min(p[i] for p in punkte) for i in range(3)] + [max(p[i] for p in punkte) for i in range(3)]


def laden():
    """{modell: {objekt: [(farbe, tris)]}}"""
    modelle = {}
    for path in sorted(glob.glob(os.path.join(MERCH, '*__*__*.stl'))):
        name, objekt, farbe = os.path.basename(path)[:-4].split('__')
        modelle.setdefault(name, {}).setdefault(objekt, []).append((farbe, make_3mf.read_stl(path)))
    for objs in modelle.values():
        for teile in objs.values():
            teile.sort(key=lambda ft: FARBEN.index(ft[0]))
    return modelle


def gruppen(modelle, kategorien):
    """Je Kategorie die Varianten als Gruppen: (modell, [(objekt, teile, bbox)], bbox, farben)."""
    out = []
    for titel, wahl in kategorien:
        gs = []
        for name in sorted(modelle, key=lambda n: ('neutral' in n, n)):
            objs = [(o, t) for o, t in modelle[name].items() if wahl(name, o)]
            if not objs:
                continue
            objs = [(o, t, bbox([p for _, tris in t for tri in tris for p in tri])) for o, t in objs]
            bb = [min(b[i] for _, _, b in objs) for i in range(3)] + [max(b[i] for _, _, b in objs) for i in range(3, 6)]
            farben = {f for _, t, _ in objs for f, _ in t}
            gs.append((name, objs, bb, farben))
        out.append((titel, gs))
    return out


def packen(titel, gs):
    """Regalpackung je Kategorie. Rueckgabe: Platten als (Name, [(gruppe, x, y)]) mit Plattenkoordinaten der Gruppen-Ecke."""
    nutz = BETT - 2 * RAND
    platten, akt = [], None

    def neu():
        return {'teile': [], 'x': 0.0, 'y': 0.0, 'reihe': 0.0, 'farben': set()}

    for g in gs:
        w, h = g[2][3] - g[2][0], g[2][4] - g[2][1]
        if w > nutz or h > nutz:
            raise ValueError('%s ist zu gross fuer die Platte (%.0f x %.0f)' % (g[0], w, h))
        if akt is None or len(akt['farben'] | g[3]) > MAX_FILAMENTE:
            akt = neu()
            platten.append(akt)
        if akt['x'] > 0 and akt['x'] + w > nutz:            # neue Reihe
            akt['x'], akt['y'], akt['reihe'] = 0.0, akt['y'] + akt['reihe'] + LUFT, 0.0
        if akt['y'] + h > nutz:                              # neue Platte
            akt = neu()
            platten.append(akt)
        akt['teile'].append((g, akt['x'], akt['y']))
        akt['farben'] |= g[3]
        akt['x'] += w + LUFT
        akt['reihe'] = max(akt['reihe'], h)

    out = []
    for i, p in enumerate(platten):
        # Belegung auf der Platte mittig ausrichten, Reihen von hinten nach vorn (y nach unten gespiegelt)
        breite = max(x + g[2][3] - g[2][0] for g, x, y in p['teile'])
        tiefe = max(y + g[2][4] - g[2][1] for g, x, y in p['teile'])
        dx, dy = (BETT - breite) / 2.0, (BETT - tiefe) / 2.0
        lage = [(g, dx + x, BETT - dy - y - (g[2][4] - g[2][1])) for g, x, y in p['teile']]
        name = titel
        if len(platten) > 1:
            name += ' ' + ', '.join(g[0].split('_', 1)[1] for g, _, _ in p['teile'])
        out.append((name, lage))
    return out


def main(kategorien=None, out=None, titel='Bechtle Merch - alle Varianten', einstellungen=None):
    """kategorien: Liste wie KATEGORIEN; out: Pfad der 3MF."""
    chipsatz()
    alle = gruppen(laden(), kategorien or KATEGORIEN)
    platten = [pl for titel, gs in alle if gs for pl in packen(titel, gs)]
    farben = [f for f in FARBEN if any(f in g[3] for _, lage in platten for g, _, _ in lage)]
    nr = {f: i + 1 for i, f in enumerate(farben)}
    spalten = 1
    while spalten * spalten < len(platten):
        spalten += 1

    # Objekte: Netz um die eigene Mitte (z ab 0), Lage ueber die Transformation des Build-Eintrags
    objekte = []        # (oid, name, [(pid, teilname, filament)], transform, platte)
    netze = []          # (pid, tris, versatz)
    nid = 1
    for k, (pname, lage) in enumerate(platten):
        ox, oy = (k % spalten) * STRIDE, -(k // spalten) * STRIDE
        for (gname, objs, gbb, _), gx, gy in lage:
            for o, teile, b in objs:
                cx, cy = (b[0] + b[3]) / 2.0, (b[1] + b[4]) / 2.0
                plist = []
                for f, tris in teile:
                    netze.append((nid, tris, (-cx, -cy, -b[2])))
                    plist.append((nid, '%s %s' % (o, f), nr[f]))
                    nid += 1
                tx = ox + gx + (cx - gbb[0])
                ty = oy + gy + (cy - gbb[1])
                tz = b[2] - gbb[2]
                oname = gname if len(objs) == 1 else '%s - %s' % (gname, o)
                objekte.append((nid, oname, plist, '1 0 0 0 1 0 0 0 1 %g %g %g' % (tx, ty, tz), k))
                nid += 1

    obj_path = '/3D/Objects/object_1.model'
    out = out or os.path.join(MERCH, 'bechtle_merch_alle_platten.3mf')
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        with z.open('3D/Objects/object_1.model', 'w', force_zip64=True) as fh:
            fh.write(('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" %s>'
                      '<metadata name="BambuStudio:3mfVersion">1</metadata><resources>' % make_3mf.NS).encode())
            for pid, tris, versatz in netze:
                m, _, _ = make_3mf.mesh_xml(tris, versatz)
                fh.write(('<object id="%d" p:UUID="%s" type="model">%s</object>' % (pid, uuid.uuid4(), m)).encode())
            fh.write(b'</resources><build/></model>')

        res, items = [], []
        for oid, oname, plist, tr, k in objekte:
            comps = ''.join('<component p:path="%s" objectid="%d" p:UUID="%s" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>'
                            % (obj_path, pid, uuid.uuid4()) for pid, _, _ in plist)
            res.append('<object id="%d" p:UUID="%s" type="model"><components>%s</components></object>'
                       % (oid, uuid.uuid4(), comps))
            items.append('<item objectid="%d" p:UUID="%s" transform="%s" printable="1"/>' % (oid, uuid.uuid4(), tr))
        z.writestr('3D/3dmodel.model',
                   '<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" %s>'
                   '<metadata name="Application">BambuStudio-02.09.01.70</metadata>'
                   '<metadata name="BambuStudio:3mfVersion">1</metadata>'
                   '<metadata name="Title">%s</metadata>'
                   '<resources>%s</resources><build p:UUID="%s">%s</build></model>'
                   % (make_3mf.NS, escape(titel), ''.join(res), uuid.uuid4(), ''.join(items)))

        cfg = ['<?xml version="1.0" encoding="UTF-8"?>', '<config>']
        for oid, oname, plist, tr, k in objekte:
            cfg.append('  <object id="%d">' % oid)
            cfg.append('    <metadata key="name" value="%s"/>' % escape(oname))
            cfg.append('    <metadata key="extruder" value="%d"/>' % plist[0][2])
            for pid, pn, ex in plist:
                cfg.append('    <part id="%d" subtype="normal_part">' % pid)
                cfg.append('      <metadata key="name" value="%s"/>' % escape(pn))
                cfg.append('      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>')
                cfg.append('      <metadata key="extruder" value="%d"/>' % ex)
                cfg.append('    </part>')
            cfg.append('  </object>')
        ident = 100
        for k, (pname, lage) in enumerate(platten):
            cfg.append('  <plate>')
            cfg.append('    <metadata key="plater_id" value="%d"/>' % (k + 1))
            cfg.append('    <metadata key="plater_name" value="%s"/>' % escape(pname))
            cfg.append('    <metadata key="locked" value="false"/>')
            cfg.append('    <metadata key="filament_map_mode" value="Auto For Flush"/>')
            cfg.append('    <metadata key="filament_maps" value="%s"/>' % ' '.join(['1'] * len(farben)))
            for oid, *_r, pk in objekte:
                if pk != k:
                    continue
                cfg += ['    <model_instance>',
                        '      <metadata key="object_id" value="%d"/>' % oid,
                        '      <metadata key="instance_id" value="0"/>',
                        '      <metadata key="identify_id" value="%d"/>' % ident,
                        '    </model_instance>']
                ident += 1
            cfg.append('  </plate>')
        cfg.append('</config>')
        z.writestr('Metadata/model_settings.config', '\n'.join(cfg) + '\n')
        z.writestr('Metadata/project_settings.config', projekt_einstellungen(farben, einstellungen))

        z.writestr('[Content_Types].xml',
                   '<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
                   '<Default Extension="png" ContentType="image/png"/>'
                   '<Default Extension="config" ContentType="text/xml"/></Types>')
        z.writestr('_rels/.rels',
                   '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
                   '</Relationships>')
        z.writestr('3D/_rels/3dmodel.model.rels',
                   '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Target="%s" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
                   '</Relationships>' % obj_path)

    for k, (pname, lage) in enumerate(platten):
        fs = sorted({f for g, _, _ in lage for f in g[3]}, key=FARBEN.index)
        print('Platte %2d  %-44s %2d Varianten  Filamente %s' % (k + 1, pname, len(lage), ', '.join(str(nr[f]) for f in fs)))
    print('FILAMENTE: ' + ', '.join('%d = %s %s' % (nr[f], KLARNAME[f], HEX[f]) for f in farben))
    print('->', out, '%.1f MB' % (os.path.getsize(out) / 1e6))
    return out, platten, farben


if __name__ == '__main__':
    main()
