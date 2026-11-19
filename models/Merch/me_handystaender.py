# Handystaender "On Call": Bodenplatte 78 x 92 mit Lippe vorn, um 20 Grad zurueckgelehnte Lehne (70 Grad zur
# Waagerechten) und Stuetzstrebe hinten. Ein Teil, ein Druckobjekt, drei Farben (dunkel, weiss, neon).
#
# Funktion:
#   - Die Nut zwischen Lippe und Lehne ist 14 mm breit (senkrecht zur Lehne gemessen) und ihr Boden steht
#     rechtwinklig zur Lehne. Das Handy (auch mit Huelle, bis 14 mm) steht mit der Unterkante flach auf dem
#     Nutboden und liegt mit dem Ruecken satt an der Lehne, unabhaengig von seiner Dicke; die Schwerkraft
#     zieht es in die Ecke, die Lippe ist nur der Anschlag nach vorn.
#   - Standsicherheit: mit einem 220-g-Handy (160 mm, hochkant) liegt der gemeinsame Schwerpunkt rund 44 mm
#     hinter der vorderen und 48 mm vor der hinteren Kippkante, also fast mittig ueber der Platte. Nach hinten
#     kippt er erst bei etwa 0,9 N waagerechtem Druck ganz oben am Handy (Tippen auf Displaymitte: ca. 1,7 N).
#     build() schreibt die Werte ins Protokoll.
#   - Keine Kabeloeffnung (das Konzept hat keine): Laden im Hochformat nur kabellos, im Querformat mit Kabel.
#
# Drucklage: stehend wie im Gebrauch, Bodenplatte (78 x 92) auf dem Bett, ohne Stuetzen.
#   Begruendung: Alle Ueberhaenge bleiben unter 45 Grad (Lehnen-Rueckseite 20 Grad, Strebe 35 Grad zur
#   Senkrechten, das Dreieck schliesst oben spitz, also keine Bruecke). Die grosse Platte haftet sicher,
#   beide Seitenflaechen sehen gleich aus, die Schrift auf der Lippe wird aufrecht als senkrechte Wand gedruckt
#   (Einlage 0,8 mm), das Emblem liegt in der 70 Grad steilen Lehne (ebenfalls 0,8 mm). Liegend als Profil
#   gedruckt waeren es 78 mm hohe, 6 mm duenne Waende mit Farbwechsel ueber fast die ganze Hoehe, und die
#   beiden Sichtseiten (Bettseite / Deckflaeche) saehen verschieden aus.
#   Unten umlaufend 0,5 mm Fase, alle Kanten der Seitenflaechen ebenfalls 0,5 mm gefast.
#
# Varianten: handystaender_logo (Schriftzug auf der Lippe, Emblem auf der Lehne) und handystaender_neutral
#   (nur Punkt und ON CALL mittig auf der Lippe, auf der Lehne statt des Emblems der Statuspunkt mit Haken).
# Vorschau: das Bild ohne Zusatz zeigt den Staender mit einem angedeuteten Handy (nur fuer das Bild, wird
#   weder exportiert noch in der F3D gespeichert), "_leer" dieselbe Ansicht ohne Handy.
import math
import os

import adsk.core
import adsk.fusion

import me_common as M
from me_common import C

PARAM = dict(
    breite=78.0,            # X
    tiefe_y=92.0,           # Y, Bodenplatte
    hoehe=105.0,            # Z, Oberkante der Lehne
    boden=6.0,              # Dicke der Bodenplatte
    lippe=(6.0, 14.0),      # Lippe vorn: Dicke, Hoehe ueber dem Bett
    lippe_fase=(1.0, 1.5),  # Fase oben aussen / innen
    neigung=20.0,           # Lehne, Grad aus der Senkrechten (70 Grad zur Waagerechten)
    lehne=6.0,              # Dicke der Lehne
    lehne_fase=1.2,         # Fase an den beiden oberen Kanten der Lehne
    nut=(14.0, 3.0),        # Nutbreite senkrecht zur Lehne, Restdicke der Platte am Nutgrund
    strebe=(6.0, 55.0),     # Dicke, Winkel zur Waagerechten (Ueberhang 35 Grad)
    ecke_r=3.0,             # Rundung der beiden unteren Ecken des Dreiecks
    fase=0.5,               # Fase unten und an den Seitenflaechen
    tiefe=0.8,              # Einlagetiefe (senkrechte und steile Flaechen)
    # Lippe: Schriftzug, Punkt, ON CALL
    lippe_rand=2.8,         # Rand links und rechts
    lippe_z=6.7,            # Hoehe der Schriftmitte
    wort_b=26.0,            # Breite des Schriftzugs (Hoehe = Breite / 4,47; duennste Striche dann ca. 0,6 mm)
    punkt_d=3.2,
    luecke=3.0,             # Abstand zwischen Schriftzug, Punkt und Text
    text='ON CALL', text_cap=6.0,
    # Lehne: Emblem bzw. Statuspunkt, Mitte auf dieser Hoehe ueber dem Bett
    emblem=(30.0, 79.3),    # Breite, z der Mitte
    status_d=24.0,          # neutrale Variante: Durchmesser des Statuspunkts (0 = Lehne bleibt leer)
    # Annahmen fuer die Standsicherheit und das Vorschau-Handy
    handy=(72.0, 150.0, 9.0, 8.0),      # Breite, Laenge, Dicke, Eckradius (Vorschau)
    handy_masse=(220.0, 160.0, 9.0),    # Gramm, Laenge, Dicke (Rechnung)
    fuellung=0.4,           # geschaetzter Materialanteil des Drucks (Waende + Fuellung), PLA 1,24 g/cm3
)

ANSICHT = (-80, -118, 46)   # wie das Konzeptbild: von vorn links, leicht von oben


def _geo(p):
    """Seitenprofil in (y, z): Aussenkontur, Dreieck und die wichtigsten Punkte."""
    a = math.radians(p['neigung'])
    sn, cs, tn = math.sin(a), math.cos(a), math.tan(a)
    T, H, B = p['tiefe_y'], p['hoehe'], p['boden']
    ld, lh = p['lippe']
    fa, fi = p['lippe_fase']
    nb, nz = p['nut']
    sd, sw = p['strebe']
    b = math.radians(sw)
    y0, y1 = -T / 2.0, T / 2.0
    yl = y0 + ld                          # Innenseite der Lippe
    yF, zF = yl + nb * cs, nz             # Nutgrund = Fuss der Lehnen-Vorderseite
    zA = zF + nb * sn                     # Nutboden an der Lippe
    tH = p['lehne'] / cs                  # waagerechtes Mass der Lehne

    def yf(z):                            # Lehnen-Vorderseite
        return yF + (z - zF) * tn

    def yb(z):                            # Lehnen-Rueckseite
        return yf(z) + tH

    def schnitt(ys):                      # Strebenlinie y = ys - (z - B) / tan(b) mit der Lehnen-Rueckseite
        return (ys + B / math.tan(b) - yF + zF * tn - tH) / (tn + 1.0 / math.tan(b))
    zJ = schnitt(y1)                      # Strebe aussen trifft Lehne
    yi = y1 - sd / math.sin(b)            # Strebe innen auf der Platte
    zK = schnitt(yi)                      # Spitze des Dreiecks
    c = p['lehne_fase']
    aussen = [(y0, 0.0), (y1, 0.0), (y1, B), (yb(zJ), zJ),
              (yb(H - c), H - c), (yb(H) - c, H), (yf(H) + c, H), (yf(H - c), H - c),
              (yF, zF), (yl, zA),
              (yl, lh - fi), (yl - fi, lh), (y0 + fa, lh), (y0, lh - fa)]
    dreieck = [(yb(B), B), (yi, B), (yb(zK), zK)]
    assert zA < lh - fi - 2.0, 'Lippe zu niedrig fuer den Nutboden'
    return dict(sn=sn, cs=cs, tn=tn, yF=yF, zF=zF, zA=zA, yf=yf, yb=yb, zJ=zJ, zK=zK,
                aussen=aussen, dreieck=dreieck, y0=y0, y1=y1)


def _profil_koerper(t, p, g):
    """Extrudiert das Seitenprofil symmetrisch zur YZ-Ebene auf die Breite."""
    sk = t.root.sketches.add(t.root.yZConstructionPlane)
    sk.name = 'profil_Skizze'
    lines = sk.sketchCurves.sketchLines
    for pts in (g['aussen'], g['dreieck']):
        sp = [sk.modelToSketchSpace(C.P(0, y, z)) for y, z in pts]
        first = lines.addByTwoPoints(sp[0], sp[1])
        last = first
        for q in sp[2:]:
            last = lines.addByTwoPoints(last.endSketchPoint, q)
        lines.addByTwoPoints(last.endSketchPoint, first.startSketchPoint)
    prof = None
    for i in range(sk.profiles.count):
        if sk.profiles.item(i).profileLoops.count == 2:
            prof = sk.profiles.item(i)
    ext = t.root.features.extrudeFeatures
    ei = ext.createInput(prof, C.NEW)
    ei.setSymmetricExtent(C.E('breite'), True)
    body = ext.add(ei).bodies.item(0)
    body.name = 'staender'
    return body


def _kanten_x(body, punkte):
    """Kanten parallel zu X, die durch einen der Punkte (y, z) laufen."""
    col = adsk.core.ObjectCollection.create()
    for e in body.edges:
        if e.startVertex is None or e.endVertex is None:
            continue
        a, b = e.startVertex.geometry, e.endVertex.geometry
        if abs(a.y - b.y) > 1e-6 or abs(a.z - b.z) > 1e-6:
            continue
        if any(abs(a.y * 10 - y) < 1e-3 and abs(a.z * 10 - z) < 1e-3 for y, z in punkte):
            col.add(e)
    return col


def _fasen(t, body, p):
    """0,5 mm Fase an allen Kanten der Bodenflaeche und der beiden Seitenflaechen."""
    def sammeln(seiten):
        col, ids = adsk.core.ObjectCollection.create(), set()
        for f in body.faces:
            pl = adsk.core.Plane.cast(f.geometry)
            if pl is None:
                continue
            unten = abs(abs(pl.normal.z) - 1) < 1e-6 and abs(f.pointOnFace.z) < 1e-6
            seite = seiten and abs(abs(pl.normal.x) - 1) < 1e-6
            if not (unten or seite):
                continue
            for e in f.edges:
                if e.tempId not in ids:
                    ids.add(e.tempId)
                    col.add(e)
        return col
    cf = t.root.features.chamferFeatures
    for seiten in (True, False):
        try:
            ci = cf.createInput2()
            ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(sammeln(seiten), C.V(p['fase']), False)
            cf.add(ci)
            return
        except RuntimeError as ex:
            t.log('  Hinweis: Fase %s nicht moeglich (%s)' % ('mit Seitenkanten' if seiten else 'unten',
                                                             str(ex).splitlines()[0]))


def _lippe_grafik(t, p, mit_logo):
    """Schriftzug (nur Logo-Variante), Punkt und ON CALL als eine mittige Zeile, flach im Ursprung."""
    d = p['tiefe']
    cap, s = p['text_cap'], p['text']
    lue, pd = p['luecke'], p['punkt_d']
    wl = p['wort_b'] + lue if mit_logo else 0.0
    frei = p['breite'] - 2 * p['lippe_rand'] - wl - pd - lue
    w = t.text_breite(s, cap, M.FONT_BLACK, False)
    if w > frei:
        cap, w = cap * frei / w, frei
    x = -(wl + pd + lue + w) / 2.0
    k = []
    if mit_logo:
        hw = p['wort_b'] / 4.47
        # Grundlinie des Schriftzugs auf die Grundlinie des Textes
        k += t.logo('wort', p['wort_b'], x + p['wort_b'] / 2.0, -cap / 2.0 + hw / 2.0, d, mono='weiss')
        x += wl
    k += t.kreis(pd, x + pd / 2.0, 0.0, d, 'neon')
    x += pd + lue
    k += t.text(s, cap, x, 0.0, d, 'weiss', font=M.FONT_BLACK, bold=False, align='links')
    t.log('    Lippe: "%s" Versalhoehe %.2f mm, Zeile %.1f mm breit' % (s, cap, wl + pd + lue + w))
    return k


def _status_grafik(t, p):
    """Statuspunkt mit Haken (aus dem Konzept-Display): Scheibe neon, Haken in der Farbe des Staenders."""
    d, D = p['tiefe'], p['status_d']
    f = D / 20.0
    scheibe = t.kreis(D, 0, 0, d, 'neon')
    haken = t.linie([(-4.6 * f, -0.4 * f), (-1.4 * f, -3.8 * f), (4.8 * f, 3.6 * f)], 2.4 * f, d, 'dunkel')
    return scheibe, haken


def _standsicherheit(t, body, p, g):
    """Grobe Kipprechnung: Schwerpunkt Staender + Handy gegen die vordere und hintere Kante der Bodenplatte."""
    cm_ = body.physicalProperties.centerOfMass
    vol = body.volume                                   # cm3
    ms = vol * 1.24 * p['fuellung']
    mh, lh, dh = p['handy_masse']
    yh = g['yF'] + lh / 2.0 * g['sn'] - dh / 2.0 * g['cs']
    zh = g['zF'] + lh / 2.0 * g['cs'] + dh / 2.0 * g['sn']
    y = (ms * cm_.y * 10 + mh * yh) / (ms + mh)
    z = (ms * cm_.z * 10 + mh * zh) / (ms + mh)
    ztop = g['zF'] + lh * g['cs']
    kraft = (ms + mh) / 1000.0 * 9.81 * (g['y1'] - y) / ztop       # N, waagerecht an der Handy-Oberkante
    t.log('  Standsicherheit: Staender %.1f cm3, ca. %.0f g (voll %.0f g), Schwerpunkt y %.1f z %.1f'
          % (vol, ms, vol * 1.24, cm_.y * 10, cm_.z * 10))
    t.log('    Handy %.0f g: Schwerpunkt y %.1f z %.1f; zusammen y %.1f z %.1f -> %.1f mm hinter der vorderen, '
          '%.1f mm vor der hinteren Kippkante' % (mh, yh, zh, y, z, y - g['y0'], g['y1'] - y))
    t.log('    kippt nach hinten erst ab ca. %.1f N Druck auf die Handy-Oberkante (z %.0f); '
          'leer: Schwerpunkt %.1f mm vor der hinteren Kante' % (kraft, ztop, g['y1'] - cm_.y * 10))


def _vorschau_handy(t, p, g):
    """Angedeutetes Handy an der Lehne, nur fuer das Vorschaubild (nicht angemeldet, also kein Export)."""
    b, l, dk, r = p['handy']
    luft, st = 0.2, 0.3
    root = t.root
    koerper = C.rounded_rect_body(root, -b / 2.0, 0, b / 2.0, l, r, '%g mm' % dk, 'vorschau_handy')
    schirm = C.rounded_rect_body(root, -b / 2.0 + 3, 3, b / 2.0 - 3, l - 3, r - 3, '%g mm' % st, 'vorschau_schirm')
    punkt = C.circle_body(root, t.xy, 0, 0, l / 2.0 + 30, 20, '%g mm' % st, 'vorschau_punkt')
    haken = C.stroke_body(root, t.xy, 0, [(-4.6, l / 2.0 + 29.6), (-1.4, l / 2.0 + 26.2), (4.8, l / 2.0 + 33.6)],
                          2.4, '%g mm' % st, 'vorschau_haken')
    sn, cs = g['sn'], g['cs']
    u, v = (1, 0, 0), (0, sn, cs)

    def lage(n):                          # n mm vor der Lehne, 'luft' ueber dem Nutboden
        return M.flaeche((0, g['yF'] + luft * sn - n * cs, g['zF'] + luft * cs + n * sn), u, v)
    t.auf(lage(luft), [koerper])
    t.auf(lage(luft + dk - st), [schirm, punkt, haken])
    comb = root.features.combineFeatures
    for wirt, werkzeuge in ((koerper, [schirm]), (schirm, [punkt]), (punkt, [haken])):
        tc = adsk.core.ObjectCollection.create()
        for w in werkzeuge:
            tc.add(w)
        ci = comb.createInput(wirt, tc)
        ci.operation = C.CUT
        ci.isKeepToolBodies = True
        comb.add(ci)
    for body, farbe in ((koerper, 'schwarz'), (schirm, 'anthrazit'), (punkt, 'neon'), (haken, 'anthrazit')):
        body.appearance = C.color_appearance(t.app, t.design, 'Merch ' + farbe, M.FARBEN[farbe])
    return [koerper, schirm, punkt, haken]


def staender(app, log, out, p, name, mit_logo):
    t = M.Teil(app, log, name)
    t.objekt = 'staender'
    g = _geo(p)
    C.user_param(t.design, 'breite', p['breite'], 'Breite des Staenders')
    body = _profil_koerper(t, p, g)
    if p['ecke_r'] > 0:
        try:
            C.fillet(t.root, _kanten_x(body, g['dreieck'][:2]), p['ecke_r'])
        except RuntimeError as ex:
            log('  Hinweis: Rundung im Dreieck nicht moeglich (%s)' % str(ex).splitlines()[0])
    _fasen(t, body, p)
    t.add(body, 'dunkel')
    log('  Nut: %.1f mm senkrecht zur Lehne, Nutgrund y %.2f z %.2f, Nutboden an der Lippe z %.2f; '
        'Strebe trifft die Lehne auf z %.1f' % (p['nut'][0], g['yF'], g['zF'], g['zA'], g['zJ']))
    _standsicherheit(t, body, p, g)

    d = p['tiefe']
    # Lippe vorn
    k = t.auf(M.vorn(g['y0'], 0.0, p['lippe_z']), _lippe_grafik(t, p, mit_logo))
    t.einlegen(body, k)
    # Lehne: Emblem bzw. Statuspunkt auf der schraegen Vorderseite
    ze = p['emblem'][1]
    lehne = M.flaeche((0.0, g['yf'](ze), ze), (1, 0, 0), (0, g['sn'], g['cs']))
    if mit_logo:
        k = t.auf(lehne, t.logo('emblem', p['emblem'][0], 0, 0, d, mono='weiss'))
        t.einlegen(body, k)
    elif p['status_d'] > 0:
        scheibe, haken = _status_grafik(t, p)
        t.auf(lehne, scheibe + haken)
        t.einlegen(body, scheibe)
        t.einlegen(scheibe, haken)

    t.fertig(out, ansichten=[('_leer', ANSICHT, (0, 0, 1)),
                             ('_vorn', (0, -200, 45), (0, 0, 1)),
                             ('_hinten', (110, 130, 70), (0, 0, 1)),
                             ('_seite', (-200, 0, 0), (0, 0, 1))])
    # Hauptbild wie im Konzept mit angelehntem Handy (nach Export und F3D, das Handy bleibt reine Vorschau)
    handy = _vorschau_handy(t, p, g)
    bb = C.bbox_mm([it[0] for it in t.items] + handy)
    ziel = ((bb[0] + bb[3]) / 2.0, (bb[1] + bb[4]) / 2.0, (bb[2] + bb[5]) / 2.0)
    C.snapshot(app, os.path.join(out['preview'], name + '.png'), ziel, ANSICHT, up=(0, 0, 1), margin=1.15)
    return t


def build(app, log, out, nur=None):
    for name, mit_logo in (('handystaender_logo', True), ('handystaender_neutral', False)):
        if nur and not any(n in name for n in nur):
            continue
        staender(app, log, out, PARAM, name, mit_logo)
