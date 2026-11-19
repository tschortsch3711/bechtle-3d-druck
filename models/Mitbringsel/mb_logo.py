# Token (Muenze) mit dem Bechtle-Logo aus logo/Logo_Bechtle.svg (Wikimedia Commons, "Logo Bechtle.svg").
# Weisse Muenze, Logo 0,6 mm erhaben: Wortmarke + dunkler Emblemteil dunkelgruen, oberer Emblemteil hellgruen,
# das weisse Parallelogramm ist die Muenze selbst. Dazu ein dunkelgruener Rand.
import os
import re
import tempfile
import adsk.core
import adsk.fusion
import mb_common as C

NAME = 'bechtle_token'
HERE = os.path.dirname(os.path.abspath(__file__))

PARAM = dict(
    durchmesser=42.0,
    dicke=3.0,
    fase=0.5,
    logo_hoehe=0.6,
    svg='logo/Logo_Bechtle.svg',
    emblem_breite=19.0, emblem_mitte=(0.0, 5.5),
    wortmarke_breite=25.0, wortmarke_mitte=(0.0, -10.0),
    rand_innen=19.2, rand_aussen=20.4,     # Radius des Randrings
    farbe_basis=(245, 245, 245),           # Weiss
    farbe_dunkel=(7, 80, 51),              # #075033
    farbe_hell=(35, 169, 106),             # #23a96a
)


def _split_svg(path):
    """Zerlegt das Logo in einzelne SVG-Dateien je Pfad (gleiche Leinwand)."""
    src = open(path, encoding='utf-8').read()
    head = re.search(r'<svg[^>]*>', src).group(0)
    paths = re.findall(r'<path[^>]*/>', src)
    tmp = tempfile.mkdtemp(prefix='bechtle_logo_')
    files = []
    for i, pth in enumerate(paths):
        fill = re.search(r'fill="([^"]+)"', pth).group(1).lower()
        # Offene Teilpfade schliessen (SVG fuellt sie implizit geschlossen, Fusion braucht 'z').
        # Die Endpunkte liegen auf den Startpunkten, daher verschiebt 'z' keine relativen Folgebefehle.
        d = re.search(r'd="([^"]+)"', pth).group(1)
        subs = [sp.strip() for sp in re.split(r'(?=[mM])', d) if sp.strip()]
        d2 = ' '.join(sp if sp[-1] in 'zZ' else sp + 'z' for sp in subs)
        pth = pth.replace(d, d2)
        fn = os.path.join(tmp, 'teil_%d.svg' % i)
        with open(fn, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n%s\n%s\n</svg>\n' % (head, pth))
        files.append((fn, fill))
    return files


def _sketch_bb(sk):
    bb = sk.boundingBox
    return (bb.minPoint.x * 10, bb.minPoint.y * 10, bb.maxPoint.x * 10, bb.maxPoint.y * 10)


def _import_fit(comp, plane, svg_files, ref_files, cx, cy, width, name, log):
    """Importiert svg_files in eine Skizze, so dass die gemeinsame Box von ref_files
    die Breite width hat und bei (cx, cy) zentriert ist."""
    # 1. Probe-Import mit Massstab 1 zur Vermessung
    probe = comp.sketches.add(plane)
    for f in ref_files:
        probe.importSVG(f, 0, 0, 1.0)
    x0, y0, x1, y1 = _sketch_bb(probe)
    probe.deleteMe()
    s = width / (x1 - x0)
    px = cx - s * (x0 + x1) / 2.0
    py = cy - s * (y0 + y1) / 2.0
    sk = comp.sketches.add(plane)
    sk.name = name + '_Skizze'
    for f in svg_files:
        sk.importSVG(f, C.cm(px), C.cm(py), s)
    log('  %s: Massstab %.4f, Box %s' % (name, s, ['%.2f' % v for v in _sketch_bb(sk)]))
    return sk


def _filled_profiles(sk):
    """Profile ohne Loecher (z. B. Innenraum von b/e): ein Profil, das komplett in der Box
    eines anderen Profils mit Innenschleife liegt, gilt als Loch."""
    profs = [sk.profiles.item(i) for i in range(sk.profiles.count)]
    boxes = []
    for pr in profs:
        bb = pr.boundingBox
        boxes.append((bb.minPoint.x, bb.minPoint.y, bb.maxPoint.x, bb.maxPoint.y))
    sel = adsk.core.ObjectCollection.create()
    holes = 0
    for i, pr in enumerate(profs):
        a = boxes[i]
        is_hole = False
        for j, other in enumerate(profs):
            if i == j or other.profileLoops.count < 2:
                continue
            b = boxes[j]
            if b[0] <= a[0] + 1e-6 and b[1] <= a[1] + 1e-6 and b[2] >= a[2] - 1e-6 and b[3] >= a[3] - 1e-6:
                is_hole = True
                break
        if is_hole:
            holes += 1
        else:
            sel.add(pr)
    return sel, holes


def build(app, log, out):
    p = PARAM
    doc, design = C.new_design(app)
    root = design.rootComponent
    C.user_param(design, 'dicke', p['dicke'], 'Dicke der Muenze')
    C.user_param(design, 'logo_hoehe', p['logo_hoehe'], 'Hoehe des erhabenen Logos')
    R = p['durchmesser'] / 2.0
    T = p['dicke']

    # Muenze
    occ_b = C.sub_component(root, 'Muenze_weiss')
    cb = occ_b.component
    sk = cb.sketches.add(cb.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(C.spt(sk, 0, 0), C.cm(R))
    ext = cb.features.extrudeFeatures.addSimple(sk.profiles.item(0), C.E('dicke'), C.NEW)
    disc = ext.bodies.item(0)
    disc.name = 'Muenze'
    C.chamfer_top(cb, disc, p['fase'], log)

    files = _split_svg(os.path.join(HERE, p['svg']))
    dark = [f for f, c in files if c == '#075033']
    light = [f for f, c in files if c == '#23a96a']
    wordmark, emblem_dark = dark[0], dark[1]           # Reihenfolge wie im SVG
    emblem_all = [f for f, c in files][1:]              # Pfade 2-4 bilden das Emblem

    occ_d = C.sub_component(root, 'Logo_dunkelgruen')
    cd = occ_d.component
    pld = C.offset_plane(cd, 'dicke')
    occ_l = C.sub_component(root, 'Logo_hellgruen')
    cl = occ_l.component
    pll = C.offset_plane(cl, 'dicke')

    ex, ey = p['emblem_mitte']
    wx, wy = p['wortmarke_mitte']
    sk_w = _import_fit(cd, pld, [wordmark], [wordmark], wx, wy, p['wortmarke_breite'], 'Wortmarke', log)
    sk_ed = _import_fit(cd, pld, [emblem_dark], emblem_all, ex, ey, p['emblem_breite'], 'Emblem_dunkel', log)
    sk_el = _import_fit(cl, pll, light, emblem_all, ex, ey, p['emblem_breite'], 'Emblem_hell', log)

    for skx, comp, nm in ((sk_w, cd, 'Wortmarke'), (sk_ed, cd, 'Emblem_dunkel'), (sk_el, cl, 'Emblem_hell')):
        sel, holes = _filled_profiles(skx)
        e = comp.features.extrudeFeatures.addSimple(sel, C.E('logo_hoehe'), C.NEW)
        for i in range(e.bodies.count):
            e.bodies.item(i).name = '%s_%d' % (nm, i + 1)
        log('  %s: %d Profile extrudiert, %d Loecher ausgelassen, %d Koerper, %s'
            % (nm, sel.count, holes, e.bodies.count, C.fmt_bb(C.bbox_mm([e.bodies.item(i) for i in range(e.bodies.count)]))))

    # Randring
    C.circle_body(cd, pld, T, 0, 0, 2 * p['rand_aussen'], 'logo_hoehe', 'Rand', inner_d=2 * p['rand_innen'])

    C.paint(occ_b, C.color_appearance(app, design, 'MB Weiss', p['farbe_basis']))
    C.paint(occ_d, C.color_appearance(app, design, 'MB Dunkelgruen', p['farbe_dunkel']))
    C.paint(occ_l, C.color_appearance(app, design, 'MB Hellgruen', p['farbe_hell']))

    e = out.get('export')   # None = kein Export (nur Modell und Vorschau)
    if e:
        C.export_stl(design, occ_b, os.path.join(e, NAME + '_1_muenze_weiss.stl'))
        C.export_stl(design, occ_d, os.path.join(e, NAME + '_2_logo_dunkelgruen.stl'))
        C.export_stl(design, occ_l, os.path.join(e, NAME + '_3_logo_hellgruen.stl'))
        C.export_f3d(design, os.path.join(e, NAME + '.f3d'))
        log('  Export ok')

    C.hide_helpers(design)
    C.snapshot(app, os.path.join(out['preview'], NAME + '.png'), (0, 0, 1.5), (-40, -110, 120), margin=1.0)
    C.snapshot(app, os.path.join(out['preview'], NAME + '_oben.png'), (0, 0, 1.5), (0, 0, 200),
               up=(0, 1, 0), margin=1.05)
    log('  Vorschau ok')
    return doc
