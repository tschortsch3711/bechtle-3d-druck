# HE-Lineal: 164 x 36 x 2,4 mm, eine Kante mit Zentimeterskala (0 bis 15 cm), die andere mit Hoeheneinheiten.
#   1 HE = 44,45 mm. Rack-Lochraster je HE: Lochmitten 6,35 / 22,225 / 38,1 mm ab der HE-Grenze
#   (Abstaende 15,875 / 15,875 / 12,7 mm). Der Nullpunkt beider Skalen liegt 7 mm vom linken Rand.
# Alle Skalenstriche laufen bis an die Kante (auch durch die kleine Fase oben), damit man wirklich anlegen kann.
# Druck: flach, Unterseite auf dem Bett, ein Objekt 'lineal'. Grundkoerper weiss, Skala und Schrift
#   Experience Green ('dunkel'), Linie im Mittelband und Logo-Akzent Progressive Green ('mittel').
#   Die Grafik liegt buendig in den obersten drei Schichten (0,6 mm, z 1,8 bis 2,4; dunkle Einlage in weissem
#   Wirt, deshalb nicht tiefer). Erste Schicht 0,2 mm, dann liegt der Taschenboden auf einer Schichtgrenze.
#   Keine Stuetzen, keine Montage. Kein Buegeln (Ironing) der Oberseite, das verschmiert Gruen ins Weiss.
# Schrift: Ziffern 4,5 mm Versalhoehe (bei 4,0 war die Punze der 4 nur rund 0,6 mm weit, jetzt 0,7 mm wie beim A),
#   HE-Beschriftung und Spruch 4,0 mm. Der Spruch ist gesperrt gesetzt (Zeichenabstand wie im Konzept), damit
#   R und A nicht verschmelzen und zwischen allen Buchstaben mindestens eine Bahn Weiss (0,45 mm) Platz hat.
# Genauigkeit: Im Modell sitzen alle Striche exakt. Am gedruckten Teil nach dem ersten Druck Strich 0 bis Strich 15
#   nachmessen (Soll 150,0 mm) und im Slicer die XY-Schrumpfung ausgleichen; PLA schwindet 0,2 bis 0,4 Prozent.
# Varianten: lineal_logo (Bechtle-Logo links im Mittelband), lineal_neutral (ohne Logo, Spruch mittig).
import adsk.core

import me_common as M
from me_common import C

HE = 44.45                         # eine Hoeheneinheit in mm
LOECHER = (6.35, 22.225, 38.1)     # Lochmitten je HE ab der HE-Grenze

P = dict(
    L=164.0, B=36.0, T=2.4, r=3.0,
    fase_unten=0.5, fase_oben=0.3, tiefe=0.6,
    null=7.0,                      # Nullpunkt: Abstand vom linken Rand
    cm=15,                         # Laenge der Zentimeterskala
    strich=(0.8, 5.0, 8.0),        # Breite, Laenge der 5-mm-Striche, Laenge der Zentimeterstriche
    mm_striche=False,              # True: zusaetzlich Millimeterstriche. Standard aus: 0,5 mm Strich und 0,5 mm
    mm=(0.5, 3.0),                 # Luecke sind je nur eine Bahn der 0,4er Duese. (Breite, Laenge der mm-Striche)
    ziffer=(4.5, -6.6, 8.0),       # Versalhoehe, y der Mitte, groesste Breite (Unterkante 1 mm ueber den Strichen)
    he_anzahl=3,
    he_strich=(1.0, 9.4),          # Breite, Laenge der HE-Grenzstriche
    loch=(2.8, 1.8, 0.8),          # Quadrat, Laenge des Stegs von der Kante zum Quadrat, Breite des Stegs
    he_text=(4.0, 10.6, 24.0),     # Versalhoehe, y der Mitte, groesste Breite
    band_y=1.9,                    # Mitte des Mittelbands
    logo=36.0,                     # Breite des Logos (Emblem + Wortmarke), Hoehe rund 7,1
    spruch=('PASST INS RACK', 4.0, 62.0, 18),  # Text, Versalhoehe, groesste Breite, Zeichenabstand (10 = rund
                                               # 0,34 mm je Luecke bei 4 mm Versalhoehe)
    linie=(0.8, 4.0),              # Breite der Linie, Abstand zu Logo und Text
)


def _rechteck(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _polys(t, polys, tiefe, farbe, name):
    """Viele geschlossene Polygone in einer Skizze, ein Extrusionsschritt, ein Koerper je Polygon (z = -tiefe .. 0)."""
    sk = t.root.sketches.add(t.xy)
    sk.name = name + '_Skizze'
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines
    for pts in polys:
        sp = [C.P(x, y) for x, y in pts]
        first = lines.addByTwoPoints(sp[0], sp[1])
        last = first
        for q in sp[2:]:
            last = lines.addByTwoPoints(last.endSketchPoint, q)
        lines.addByTwoPoints(last.endSketchPoint, first.startSketchPoint)
    sk.isComputeDeferred = False
    col = adsk.core.ObjectCollection.create()
    for i in range(sk.profiles.count):
        col.add(sk.profiles.item(i))
    e = t.root.features.extrudeFeatures.addSimple(col, C.V(-tiefe), C.NEW)
    bodies = [e.bodies.item(i) for i in range(e.bodies.count)]
    if len(bodies) != len(polys):
        t.log('  Hinweis: %s hat %d Koerper statt %d' % (name, len(bodies), len(polys)))
    for i, b in enumerate(bodies):
        b.name = '%s_%d' % (name, i + 1)
    return t.add(bodies, farbe)


def _fase_schneiden(t, striche, p):
    """Schneidet die Fase oben an den beiden Laengskanten auch in die Striche, die bis an die Kante laufen."""
    L, B, T, c = p['L'], p['B'], p['T'], p['fase_oben']
    if c <= 0:
        return
    # Keil in (y, z) gezeichnet, Laenge in x: lokale x -> Welt-Y, lokale y -> Welt-Z, Extrusion -> Welt-X
    lage = M.flaeche((L / 2.0 + 1.0, 0, 0), (0, 1, 0), (0, 0, 1))
    keile = []
    for s in (-1.0, 1.0):
        y = s * B / 2.0
        pts = [(y + s, T - c - 1.0), (y + s, T + 1.0), (y - s * (c + 1.0), T + 1.0)]
        keile.append(C.poly_body(t.root, t.xy, 0, pts, '%g mm' % -(L + 2.0), 'fasenkeil_%d' % len(keile)))
    t.auf(lage, keile)
    t.einlegen(striche, keile)
    for k in keile:
        t.root.features.removeFeatures.add(k)


def lineal(app, log, out, name, mit_logo):
    p = P
    t = M.Teil(app, log, name)
    t.objekt = 'lineal'
    L, B, T, d = p['L'], p['B'], p['T'], p['tiefe']
    C.user_param(t.design, 'dicke', T, 'Dicke')
    body = C.rounded_rect_body(t.root, -L / 2.0, -B / 2.0, L / 2.0, B / 2.0, p['r'], 'dicke', 'lineal')
    M.fase_kanten(t, body, p['fase_unten'], z=0.0)
    M.fase_kanten(t, body, p['fase_oben'], z=T)
    t.add(body, 'weiss')

    x0 = -L / 2.0 + p['null']
    yu, yo = -B / 2.0, B / 2.0

    # --- Zentimeterkante (unten): Striche alle 5 mm bis an die Kante, Ziffern an den vollen Zentimetern
    polys = []
    w, l5, l10 = p['strich']
    for i in range(p['cm'] * 2 + 1):
        x = x0 + 5.0 * i
        polys.append(_rechteck(x - w / 2.0, yu, x + w / 2.0, yu + (l5 if i % 2 else l10)))
    if p['mm_striche']:
        wm, lm = p['mm']
        for i in range(p['cm'] * 10 + 1):
            if i % 5:
                polys.append(_rechteck(x0 + i - wm / 2.0, yu, x0 + i + wm / 2.0, yu + lm))

    # --- HE-Kante (oben): Grenzstriche und Lochraster (Steg von der Kante zur Lochmitte, darunter ein Quadrat)
    wh, lh = p['he_strich']
    for k in range(p['he_anzahl'] + 1):
        x = x0 + k * HE
        polys.append(_rechteck(x - wh / 2.0, yo - lh, x + wh / 2.0, yo))
    q, a, s = p['loch']
    for k in range(p['he_anzahl']):
        for o in LOECHER:
            x = x0 + k * HE + o
            polys.append([(x - s / 2.0, yo), (x + s / 2.0, yo), (x + s / 2.0, yo - a), (x + q / 2.0, yo - a),
                          (x + q / 2.0, yo - a - q), (x - q / 2.0, yo - a - q), (x - q / 2.0, yo - a),
                          (x - s / 2.0, yo - a)])
    striche = _polys(t, polys, d, 'dunkel', 'skala')
    g = list(striche)

    cap, y, mb = p['ziffer']
    for i in range(p['cm'] + 1):
        g += t.text(str(i), cap, x0 + 10.0 * i, y, d, 'dunkel', max_breite=mb)
    cap, y, mb = p['he_text']
    for k in range(p['he_anzahl']):
        g += t.text('%d HE' % (k + 1), cap, x0 + (k + 0.5) * HE, y, d, 'dunkel', max_breite=mb)

    # --- Mittelband: Logo links, Spruch rechts, Linie dazwischen. Ohne Logo: Spruch mittig, Linie links und rechts.
    ym = p['band_y']
    spruch, cap, mb, sperr = p['spruch']
    wl, luft = p['linie']
    tw = min(mb, t.text_breite(spruch, cap, abstand=sperr))     # gleiche Sperrung wie beim Setzen
    xl, xr = x0 - w / 2.0, x0 + 10.0 * p['cm'] + w / 2.0        # aeussere Kanten des ersten und letzten Strichs
    if mit_logo:
        g += t.logo('voll', p['logo'], xl + p['logo'] / 2.0, ym, d)
        g += t.text(spruch, cap, xr, ym, d, 'dunkel', max_breite=mb, align='rechts', abstand=sperr)
        stuecke = [(xl + p['logo'] + luft, xr - tw - luft)]
    else:
        xm = (xl + xr) / 2.0
        g += t.text(spruch, cap, xm, ym, d, 'dunkel', max_breite=mb, abstand=sperr)
        stuecke = [(xl, xm - tw / 2.0 - luft), (xm + tw / 2.0 + luft, xr)]
    for xa, xb in stuecke:
        if xb > xa + 4.0:
            g += t.rechteck(xa, ym - wl / 2.0, xb, ym + wl / 2.0, d, 'mittel')

    t.auf(M.oben(T), g)
    _fase_schneiden(t, striche, p)
    t.einlegen(body, g)

    t.fertig(out, ansichten=[('', (-15, -105, 170), (0, 0, 1)),
                             ('_oben', (0, 0, 200), (0, 1, 0)),
                             ('_kante', (-60, -160, 60), (0, 0, 1))], rand=1.05)
    return t


def build(app, log, out, nur=None):
    for name, mit_logo in (('lineal_logo', True), ('lineal_neutral', False)):
        if nur and not any(n in name for n in nur):
            continue
        lineal(app, log, out, name, mit_logo)
