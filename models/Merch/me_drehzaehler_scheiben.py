# Drehzaehler "Tage stabiler Betrieb": stehendes Gehaeuse 198,8 x 82,6 x 10,2 mm, 12 Grad nach hinten geneigt in
# einem Fuss 160 x 38 x 14 mm, drei Ziffernraeder (Durchmesser 63,2, 0 bis 9, Daumenraeder) hinter drei Fenstern
# 10,7 x 17 mm, Anzeige 000 bis 999. Ziffern: Impact (fett und schmal), 13 mm hoch, Strich ca. 3 mm.
#
# Druckobjekte (alle flach, ohne Stuetzen, 0,2 mm Schichten, alle Stufenhoehen auf dem 0,2-mm-Raster):
#   front   Frontschale, Sichtseite auf dem Bett (Schrift und Fensterrahmen 1,0 mm tief in den ersten 5 Schichten
#           weiss eingelegt), Radtaschen, Anlaufbunde (0,4 mm), Achsen und Passstifte zeigen nach oben.
#           Progressive Green + Weiss.
#   rueck   Rueckplatte, Aussenseite auf dem Bett, Innenseite oben: Lagerbunde, Stiftloecher mit Einfuehrfase,
#           drei radiale Rastfinger (Federzunge in der Platte, Wurzel unten, Rastnase zeigt nach oben) und
#           Griffmulden in der Oberkante. Experience Green.
#   rad1-3  drei gleiche Ziffernraeder, Ziffern oben (1,0 mm weiss eingelegt), Rastmulden unten. Experience Green
#           + Weiss.
#   fuss    Fuss mit schraegem Schlitz und Passfeder in der Schlitzmitte, steht auf seiner Unterseite;
#           Logo-Variante mit weissem Logo in der Front (0,8 mm). Experience Green (+ Weiss).
# Drucklage: beide Platten uebereinander, die Raeder in einer Reihe darunter, der Fuss quer daneben; alles
# zusammen ca. 240 x 234 mm (Werte im Protokoll). Fuss moeglichst voll (hohe Fuellung) drucken, das Gewicht
# unten macht ihn standfester; fuer die Rastnasen der Rueckplatte eine Mindestschichtzeit einstellen.
#
# Montage: Raeder mit den Ziffern nach unten auf die Achsen der (mit der Sichtseite unten liegenden) Frontschale
# stecken, Rueckplatte auf die fuenf Passstifte und die drei Achszapfen druecken (Stifte 4,0 mm in 4,3-mm-Loechern
# mit Einfuehrfase; sitzt eine Platte zu locker, ein Tropfen Kleber auf die Stifte), Gehaeuse in den Schlitz des
# Fusses stecken, die Kerbe in der Unterkante sitzt auf der Passfeder (kein seitliches Verrutschen).
# Bedienung: Rad oben mit dem Daumen drehen, Oberkante nach rechts = eine Ziffer weiter. Je Ziffer rastet die Nase
# des Fingers in eine von zehn Mulden auf der Radrueckseite; der Finger liegt radial, beide Drehrichtungen fuehlen
# sich gleich an.
#
# Koordinaten des Gehaeuses: u = Breite (vom Betrachter aus nach rechts), v = Hoehe ab Unterkante,
# w = Tiefe ab Vorderseite. Frontschale in Drucklage: x = -u, z = w. Rueckplatte in Drucklage: x = u, z = Dicke - w.
import math
import os

import adsk.core
import adsk.fusion

import me_common as M
from me_common import C

P = dict(
    # Gehaeuse: B = 2 teilung + 2 (rad_d / 2 + tasche_spiel) + 2 x 2,4 mm Seitenwand
    B=198.8, H=82.6, eck_r=8.0,
    front_t=7.2, wand=2.0,             # Frontschale gesamt, Frontwand vor den Raedern
    rueck_t=3.0,
    fase_aussen=0.5, fase_fuge=0.3,    # Fase an den Aussenkanten (Bettseite), kleine Fase an der Fuge
    neigung=12.0,
    # Raeder
    teilung=65.0, achse_v=54.0,        # Abstand der Raeder, Hoehe der Achsen ueber der Unterkante. Oberkante liegt
                                       # 28,6 mm ueber der Achse: ueber den Ziffern (bis 28,2), Rad ragt 3,0 mm heraus
    rad_d=63.2, rad_t=4.0, rad_fase=0.4,
    kerben=20, kerb_r=1.6, kerb_ueber=0.5,   # Griffkerben: Kreise mit kerb_r, Mitte kerb_ueber ausserhalb des Rands
    tasche_spiel=0.4,                  # radial zwischen Rad und Tasche
    bund=0.4,                          # Anlaufbunde vorn (Nabe und Rand) und hinten (Nabe); axiales Spiel = Rest
    nabe_r=8.5, rand_r=28.6,           # vorderer Nabenbund bis nabe_r, vorderer Randbund ab rand_r
    rueck_bund=(4.6, 8.0),             # hinterer Nabenbund, Radius innen / aussen
    achse_d=8.0, lager_spiel=0.35,     # Achse, radiales Spiel der Radbohrung je Seite
    zapfen_d=5.0, zapfen_l=2.2, zapfen_spiel=0.2,    # Achszapfen in der Rueckplatte (Schiebesitz)
    loch_fase=0.3,                     # Einfuehrfase an Zapfen- und Stiftloechern
    oeffnung_tief=3.0,                 # gerade Freistellung der Taschen an der Oberkante (keine spitzen Ecken)
    daumen=(34.0, 5.0),                # Griffmulde in der Oberkante der Rueckplatte hinter jedem Rad: Radius, Tiefe
    # Ziffern und Fenster
    ziffer_h=13.0, ziffer_r=21.6,      # Hoehe der runden Ziffern (Versalhoehe ca. 12,5), Radius der Ziffernmitte
    ziffer_font='Impact', ziffer_bold=False, ziffer_7=0.477,   # Breite / Hoehe der 7 in Impact (Schriftpruefung)
    tiefe=1.0,
    fenster=(10.7, 17.0, 3.0),         # Breite, Hoehe, Eckenradius
    rahmen=1.6, fenster_fase=0.4,      # weisser Rahmen um das Fenster (einschliesslich Fase an der Fensterkante)
    # Rastung
    rast_r=19.0, rast_tiefe=1.2, rast_d=2.0,     # Mulden: Teilkreisradius, Tiefe, Durchmesser am Grund (Flanken 45 Grad)
    finger=(16.0, 5.0, 1.4, 1.0),      # radialer Finger: Laenge Nase bis Wurzel, Breite, Dicke, Spalt ringsum
    nase_luft=0.2,                     # Luft der Nase in der Mulde (keine Vorspannung in der Raststellung)
    # Passstifte Frontschale -> Rueckplatte, (u, v)
    stifte=[(-32.5, 70.5), (32.5, 70.5), (-85.0, 12.0), (0.0, 12.0), (85.0, 12.0)],
    stift_d=4.0, stift_l=2.2, stift_spiel=0.15,  # Presssitz mit 0,15 mm je Seite, notfalls Kleber
    # Beschriftung
    text='TAGE STABILER BETRIEB', text_cap=7.3, text_v=16.2, text_breite=150.0,
    # Fuss
    fuss=(160.0, 38.0, 14.0), fuss_r=4.0, fuss_fase=(0.5, 0.8),
    schlitz_spiel=0.2,                 # je Seite (Schiebesitz)
    schlitz_y=-10.0, sohle_z=5.0,      # Mitte der Gehaeuse-Unterkante: y im Fuss, Hoehe ueber dem Tisch
    kerbe=(10.0, 3.0),                 # Kerbe in der Gehaeuse-Unterkante (Breite, Tiefe); Passfeder 0,2 schmaler je
                                       # Seite und 0,4 niedriger
    logo_breite=46.0, logo_z=7.0, logo_tiefe=0.8,
    # Drucklage
    abstand=3.0, bett=240.0,
    # Vorschau
    anzeige='365',
)


# ---------- kleine Helfer ----------
def _koll(xs):
    col = adsk.core.ObjectCollection.create()
    for x in xs:
        col.add(x)
    return col


def _extr(t, zeichne, z0, z1, name, wahl=None, taper=None):
    """Skizze auf XY (zeichne(sk)), die Profile (alle oder nach wahl) als neue Koerper von z0 bis z1.
    taper: Winkel in Grad, negativ = verjuengt sich."""
    sk = t.root.sketches.add(t.xy)
    sk.name = t._nm(name) + '_Skizze'
    zeichne(sk)
    profs = [sk.profiles.item(i) for i in range(sk.profiles.count)]
    if wahl:
        profs = [pr for pr in profs if wahl(pr)]
    ext = t.root.features.extrudeFeatures
    ei = ext.createInput(_koll(profs), C.NEW)
    ei.startExtent = adsk.fusion.OffsetStartDefinition.create(C.V(z0))
    if taper:
        ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(C.V(z1 - z0)),
                            adsk.fusion.ExtentDirections.PositiveExtentDirection,
                            adsk.core.ValueInput.createByString('%g deg' % taper))
    else:
        ei.setDistanceExtent(False, C.V(z1 - z0))
    e = ext.add(ei)
    bodies = [e.bodies.item(i) for i in range(e.bodies.count)]
    nm = t._nm(name)
    for i, b in enumerate(bodies):
        b.name = '%s_%d' % (nm, i + 1)
    return bodies


def _kreise(sk, pts, d):
    for x, y in pts:
        sk.sketchCurves.sketchCircles.addByCenterRadius(C.P(x, y), C.cm(d / 2.0))


def _zyl(t, pts, d, z0, z1, name):
    return _extr(t, lambda sk: _kreise(sk, pts, d), z0, z1, name)


def _ringe(t, pts, d_innen, d_aussen, z0, z1, name):
    def zeichne(sk):
        _kreise(sk, pts, d_aussen)
        _kreise(sk, pts, d_innen)
    return _extr(t, zeichne, z0, z1, name, wahl=lambda pr: pr.profileLoops.count == 2)


def _quader(t, rects, z0, z1, name):
    def zeichne(sk):
        for x0, y0, x1, y1 in rects:
            sk.sketchCurves.sketchLines.addTwoPointRectangle(C.P(x0, y0), C.P(x1, y1))
    return _extr(t, zeichne, z0, z1, name)


def _kegel(t, pts, d0, z0, z1, name):
    """Kegelstuempfe mit 45-Grad-Flanken: Durchmesser d0 bei z0, nach oben schmaler."""
    bodies = _extr(t, lambda sk: _kreise(sk, pts, d0), z0, z1, name, taper=-45.0)
    h, r0 = z1 - z0, d0 / 2.0
    r1 = r0 - h
    soll = math.pi * h / 3.0 * (r0 * r0 + r0 * r1 + r1 * r1)
    ist = bodies[0].volume * 1000.0
    if abs(ist - soll) > 0.05 * soll:
        t.log('  Hinweis: Kegel %s hat %.2f statt %.2f mm3' % (name, ist, soll))
    return bodies


def _senker(t, pts, d, z_mund, fase, name):
    """Einfuehrfase (45 Grad) an Lochmuendungen auf Hoehe z_mund: Kegel, der nach oben weiter wird."""
    return _extr(t, lambda sk: _kreise(sk, pts, d), z_mund - fase, z_mund + 0.5, name, taper=45.0)


def _kombi(t, ziel, werkzeuge, op, behalten=False):
    ci = t.root.features.combineFeatures.createInput(ziel, _koll(werkzeuge))
    ci.operation = op
    ci.isKeepToolBodies = behalten
    t.root.features.combineFeatures.add(ci)


def _fase(t, kanten, d):
    cf = t.root.features.chamferFeatures
    ci = cf.createInput2()
    ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(_koll(kanten), C.V(d), False)
    cf.add(ci)


def _platte(t, x0, y0, x1, y1, r, dicke, name, fase_unten, fase_oben):
    """Platte mit runden Ecken, Fase an der Bettkante und an der Oberkante."""
    C.rounded_rect_body(t.root, x0, y0, x1, y1, r, '%g mm' % dicke, name)
    M.fase_kanten(t, t.root.bRepBodies.itemByName(name), fase_unten, z=0.0)
    M.fase_kanten(t, t.root.bRepBodies.itemByName(name), fase_oben, z=dicke)
    return t.root.bRepBodies.itemByName(name)


def _stifte(t, pts, d, z0, z1, name, fase=0.4):
    """Stehende Stifte mit Fase an der Spitze."""
    bodies = _zyl(t, pts, d, z0, z1, name)
    namen = [b.name for b in bodies]
    for n in namen:
        C.chamfer_top(t.root, t.root.bRepBodies.itemByName(n), fase, t.log)
    return [t.root.bRepBodies.itemByName(n) for n in namen]


def _kerbe(t, p, X, Y, T, name):
    """Kerbe in der Gehaeuse-Unterkante (u = 0) fuer die Passfeder im Fuss."""
    kb, kt = p['kerbe']
    xa, xb = sorted((X(-kb / 2.0), X(kb / 2.0)))
    return _quader(t, [(xa, Y(-1.0), xb, Y(kt))], -1.0, T + 1.0, name)


# ---------- Lage des Gehaeuses im Fuss ----------
def _plus(a, b, k=1.0):
    return tuple(a[i] + k * b[i] for i in range(3))


def _lage(p):
    """Ursprung (u = 0, v = 0, w = 0) und Achsen U, V, W des geneigten Gehaeuses, Fuss mittig auf dem Ursprung."""
    a = math.radians(p['neigung'])
    s, c = math.sin(a), math.cos(a)
    U, V, W = (1.0, 0.0, 0.0), (0.0, s, c), (0.0, c, -s)
    dick = p['front_t'] + p['rueck_t']
    o = _plus((0.0, p['schlitz_y'], p['sohle_z']), W, -dick / 2.0)
    return o, U, V, W


def _punkt(lage, u, v, w):
    o, U, V, W = lage
    return _plus(_plus(_plus(o, U, u), V, v), W, w)


def _matrix(quelle, ziel, ex, ey, ez):
    """Starre Bewegung: der Punkt quelle (Drucklage) landet auf ziel, die Achsen x, y, z auf ex, ey, ez (mm)."""
    o = ziel
    for q, e in zip(quelle, (ex, ey, ez)):
        o = _plus(o, e, -q)
    m = adsk.core.Matrix3D.create()
    m.setWithCoordinateSystem(C.P(*o), *[adsk.core.Vector3D.create(*e) for e in (ex, ey, ez)])
    return m


# ---------- Teile ----------
def frontschale(t, p, ox, oy):
    """Sichtseite auf dem Bett (z = 0), x = -u. Rueckgabe: Grundkoerper."""
    t.objekt = 'front'
    B, H, T, wd = p['B'], p['H'], p['front_t'], p['wand']
    zb = wd + p['bund']
    us = [-p['teilung'], 0.0, p['teilung']]

    def X(u):
        return ox - u

    def Y(v):
        return oy + v - H / 2.0

    body = _platte(t, ox - B / 2.0, oy - H / 2.0, ox + B / 2.0, oy + H / 2.0, p['eck_r'], T, 'front',
                   p['fase_aussen'], p['fase_fuge'])
    mitten = [(X(u), Y(p['achse_v'])) for u in us]
    Rp = p['rad_d'] / 2.0 + p['tasche_spiel']

    # Radtaschen bis auf Bundhoehe, dazwischen (Nabenbund .. Randbund) bis auf die Frontwand
    _kombi(t, body, _zyl(t, mitten, 2 * Rp, zb, T + 1.0, 'tasche'), C.CUT)
    _kombi(t, body, _ringe(t, mitten, 2 * p['nabe_r'], 2 * p['rand_r'], wd, zb + 0.5, 'bundnut'), C.CUT)
    # Oeffnung an der Oberkante gerade freistellen (sonst bleiben spitze Keile neben den Raedern stehen)
    tief = p['oeffnung_tief']
    s = math.sqrt(Rp ** 2 - (H - p['achse_v'] - tief) ** 2)
    _kombi(t, body, _quader(t, [(cx - s, Y(H - tief), cx + s, Y(H + 1.0)) for cx, _ in mitten],
                            zb, T + 1.0, 'oeffnung'), C.CUT)
    # Kerbe fuer die Passfeder im Fuss
    _kombi(t, body, _kerbe(t, p, X, Y, T, 'kerbe'), C.CUT)
    # Achsen mit Zapfen und Passstifte
    teile = _zyl(t, mitten, p['achse_d'], wd - 0.5, T, 'achse')
    teile += _stifte(t, mitten, p['zapfen_d'], T - 1.0, T + p['zapfen_l'], 'zapfen')
    teile += _stifte(t, [(X(u), Y(v)) for u, v in p['stifte']], p['stift_d'], T - 1.0, T + p['stift_l'], 'stift')
    _kombi(t, body, teile, C.JOIN)
    t.add(body, 'mittel')

    # Einlagen auf der Sichtseite: Fensterrahmen und Schrift
    fw, fh, fr = p['fenster']
    ra, d = p['rahmen'], p['tiefe']
    vf = p['achse_v'] - p['ziffer_r']
    rahmen = []
    for u in us:
        k = t.rechteck(-fw / 2.0 - ra, -fh / 2.0 - ra, fw / 2.0 + ra, fh / 2.0 + ra, d, 'weiss', r=fr + ra)
        rahmen += t.auf(M.unten(0.0, X(u), Y(vf)), k)
    txt = t.text(p['text'], p['text_cap'], 0, 0, d, 'weiss', max_breite=p['text_breite'])
    bb = C.bbox_mm(txt)
    t.log('    Schrift "%s": %.1f x %.2f mm, %.1f mm tief' % (p['text'], bb[3] - bb[0], bb[4] - bb[1], d))
    t.auf(M.unten(0.0, ox, Y(p['text_v'])), txt)
    t.einlegen(body, rahmen + txt)

    # Fenster durch Frontwand und Rahmen, Fase an der Fensterkante (Bettseite)
    for u, rah in zip(us, rahmen):
        cx, cy = X(u), Y(vf)
        w = C.rounded_rect_body(t.root, cx - fw / 2.0, cy - fh / 2.0, cx + fw / 2.0, cy + fh / 2.0, fr,
                                '4 mm', t._nm('fenster'))
        t.auf(M.oben(-1.0), [w])
        _kombi(t, body, [w], C.CUT, behalten=True)
        _kombi(t, rah, [w], C.CUT)
        kanten = []
        for e in rah.edges:
            a, b = e.boundingBox.minPoint, e.boundingBox.maxPoint
            if abs(a.z) > 1e-6 or abs(b.z) > 1e-6:
                continue
            if all(abs(q.x * 10 - cx) <= fw / 2.0 + 1e-3 and abs(q.y * 10 - cy) <= fh / 2.0 + 1e-3 for q in (a, b)):
                kanten.append(e)
        _fase(t, kanten, p['fenster_fase'])
    return body


def rueckplatte(t, p, ox, oy):
    """Aussenseite auf dem Bett (z = 0), Innenseite oben, x = u."""
    t.objekt = 'rueck'
    B, H, T = p['B'], p['H'], p['rueck_t']
    us = [-p['teilung'], 0.0, p['teilung']]

    def X(u):
        return ox + u

    def Y(v):
        return oy + v - H / 2.0

    body = _platte(t, ox - B / 2.0, oy - H / 2.0, ox + B / 2.0, oy + H / 2.0, p['eck_r'], T, 'rueck',
                   p['fase_aussen'], p['fase_fuge'])
    mitten = [(X(u), Y(p['achse_v'])) for u in us]
    # Griffmulden: von vorn unsichtbar, der Daumen greift das Rad oben und hinten
    rm, tm = p['daumen']
    _kombi(t, body, _zyl(t, [(cx, Y(H + rm - tm)) for cx, _ in mitten], 2 * rm, -1.0, T + 1.0, 'griffmulde'), C.CUT)
    _kombi(t, body, _kerbe(t, p, X, Y, T, 'kerbe'), C.CUT)
    # Nabenbunde, Zapfen- und Stiftloecher (Sackloecher, aussen bleibt die Platte geschlossen), Einfuehrfasen
    ri, ra = p['rueck_bund']
    _kombi(t, body, _ringe(t, mitten, 2 * ri, 2 * ra, T - 0.5, T + p['bund'], 'bund'), C.JOIN)
    dz = p['zapfen_d'] + 2 * p['zapfen_spiel']
    ds = p['stift_d'] + 2 * p['stift_spiel']
    stifte = [(X(u), Y(v)) for u, v in p['stifte']]
    loecher = _zyl(t, mitten, dz, T - p['zapfen_l'] - 0.2, T + 1.0, 'zapfenloch')
    loecher += _zyl(t, stifte, ds, T - p['stift_l'] - 0.2, T + 1.0, 'stiftloch')
    loecher += _senker(t, mitten, dz, T, p['loch_fase'], 'zapfenfase')
    loecher += _senker(t, stifte, ds, T, p['loch_fase'], 'stiftfase')
    _kombi(t, body, loecher, C.CUT)

    # Rastfinger radial (Wurzel unten, freies Ende mit der Nase zur Achse): Zunge in der Platte (auf dem Bett
    # gedruckt), federt nach aussen; Nase mit 45-Grad-Kegel. Die Reibung an der Nase wirkt quer zur Zunge.
    L, fb, ft, spalt = p['finger']
    z_fuss = T + p['bund'] - p['nase_luft']                 # Beginn des Kegels
    z_spitze = z_fuss + p['rast_tiefe']
    nase_d = p['rast_d'] - 0.2                              # Spitze
    fuss_d = nase_d + 2 * p['rast_tiefe']
    kopf = fuss_d / 2.0 + 0.5                               # Zunge reicht so weit ueber die Nasenmitte hinaus
    nasen = [(X(u), Y(p['achse_v'] - p['rast_r'])) for u in us]
    _kombi(t, body, _quader(t, [(nx - fb / 2.0 - spalt, ny - L, nx + fb / 2.0 + spalt, ny + kopf + spalt)
                                for nx, ny in nasen], -1.0, T + 1.0, 'fingerspalt'), C.CUT)
    teile = _quader(t, [(nx - fb / 2.0, ny - L - 1.0, nx + fb / 2.0, ny + kopf) for nx, ny in nasen],
                    0.0, ft, 'finger')
    teile += _zyl(t, nasen, fuss_d, ft - 0.4, z_fuss, 'nasenfuss')
    teile += _kegel(t, nasen, fuss_d, z_fuss, z_spitze, 'nase')
    _kombi(t, body, teile, C.JOIN)
    t.add(body, 'dunkel')
    return body


def _ziffern_kal(t, p):
    """Schrift pruefen und Texthoehe so waehlen, dass die runden Ziffern ziffer_h hoch werden."""
    font, bold = p['ziffer_font'], p['ziffer_bold']
    probe = t.text('0123456789', 10.0, 0, 0, 0.5, 'weiss', font=font, bold=bold)
    bb = C.bbox_mm(probe)
    sieben = t.text('7', 10.0, 0, 0, 0.5, 'weiss', font=font, bold=bold)
    b7 = C.bbox_mm(sieben)
    for b in probe + sieben:
        if b.isValid:
            b.deleteMe()
    t.items = [it for it in t.items if it[0].isValid]
    q7 = (b7[3] - b7[0]) / (b7[4] - b7[1])
    if abs(q7 - p['ziffer_7']) > 0.03:
        raise RuntimeError('Ziffernschrift %s fehlt oder wurde ersetzt (7: Breite/Hoehe %.3f statt %.3f)'
                           % (font, q7, p['ziffer_7']))
    cap = 10.0 * p['ziffer_h'] / (bb[4] - bb[1])
    t.log('    Ziffernschrift %s: Texthoehe %.2f mm fuer %.1f mm hohe Ziffern (7: Breite/Hoehe %.3f)'
          % (font, cap, p['ziffer_h'], q7))
    return cap


def rad(t, p, ox, oy, objekt, cap, messen=False):
    """Ziffernrad in Drucklage: Rueckseite auf dem Bett, Ziffern oben. Ziffer k steht bei -90 + 36 k Grad
    (0 unten, gegen den Uhrzeigersinn steigend), Kopf zur Achse."""
    t.objekt = objekt
    R, T = p['rad_d'] / 2.0, p['rad_t']
    body = C.circle_body(t.root, t.xy, 0, ox, oy, 2 * R, '%g mm' % T, objekt,
                         inner_d=p['achse_d'] + 2 * p['lager_spiel'])
    M.fase_kanten(t, body, p['rad_fase'])
    body = t.root.bRepBodies.itemByName(objekt)
    # Griffkerben, eine genau unten
    n, rk = p['kerben'], R + p['kerb_ueber']
    pts = [(ox + rk * math.cos(math.radians(-90 + i * 360.0 / n)),
            oy + rk * math.sin(math.radians(-90 + i * 360.0 / n))) for i in range(n)]
    _kombi(t, body, _zyl(t, pts, 2 * p['kerb_r'], -1.0, T + 1.0, 'kerbe'), C.CUT)
    # Rastmulden auf der Rueckseite (Bett): Kegel mit 45 Grad, oben flach (2 mm Bruecke)
    rr, rt = p['rast_r'], p['rast_tiefe']
    pts = [(ox + rr * math.sin(math.radians(36 * k)), oy - rr * math.cos(math.radians(36 * k))) for k in range(10)]
    _kombi(t, body, _kegel(t, pts, p['rast_d'] + 2 * (rt + 0.2), -0.2, rt, 'mulde'), C.CUT)
    t.add(body, 'dunkel')
    # Ziffern, jede nach ihrer Box mittig auf den Teilkreis
    g, ziffern = [], []
    rz = p['ziffer_r']
    for k in range(10):
        a = math.radians(36 * k)
        zf = t.text(str(k), cap, 0, 0, p['tiefe'], 'weiss', font=p['ziffer_font'], bold=p['ziffer_bold'])
        bb = C.bbox_mm(zf)
        ex, ey = (math.cos(a), math.sin(a), 0.0), (-math.sin(a), math.cos(a), 0.0)
        mitte = (ox + rz * math.sin(a), oy - rz * math.cos(a), T)
        mitte = _plus(mitte, ex, -(bb[0] + bb[3]) / 2.0)
        mitte = _plus(mitte, ey, -(bb[1] + bb[4]) / 2.0)
        g += t.auf(M.flaeche(mitte, ex, ey), zf)
        ziffern.append(zf)
    t.einlegen(body, g)
    if messen:
        _pruefen(t, p, ox, oy, ziffern)
    return body


# ---------- Pruefung der Ziffern am echten Netz ----------
def _umriss(bodies, schritt=0.25):
    """Punkte auf allen Netzkanten (xy in mm), alle schritt mm."""
    out = set()
    for b in bodies:
        calc = b.meshManager.createMeshCalculator()
        calc.surfaceTolerance = 0.002
        m = calc.calculate()
        co, idx = m.nodeCoordinatesAsDouble, m.nodeIndices
        pt = [(co[3 * i] * 10.0, co[3 * i + 1] * 10.0) for i in range(len(co) // 3)]
        for i in range(0, len(idx), 3):
            for a, c in ((idx[i], idx[i + 1]), (idx[i + 1], idx[i + 2]), (idx[i + 2], idx[i])):
                (x0, y0), (x1, y1) = pt[a], pt[c]
                n = max(1, int(math.hypot(x1 - x0, y1 - y0) / schritt))
                for s in range(n + 1):
                    out.add((round(x0 + (x1 - x0) * s / n, 3), round(y0 + (y1 - y0) * s / n, 3)))
    return list(out)


def _sdf(x, y, hw, hh, r):
    """Abstand zum abgerundeten Rechteck (positiv = aussen)."""
    qx, qy = abs(x) - (hw - r), abs(y) - (hh - r)
    return math.hypot(max(qx, 0.0), max(qy, 0.0)) + min(max(qx, qy), 0.0) - r


def _pruefen(t, p, ox, oy, ziffern):
    """Am Netz der eingelegten Ziffern: Luft im Fenster, Nachbarziffern hinter dem Fensterrand (auch mit
    2 Grad Spiel der Rastung), Abstand zwischen den Ziffern, Ziffern unter dem Randbund und unter der Oberkante."""
    fw, fh, fr = p['fenster']
    rz = p['ziffer_r']
    pts = [[(x - ox, y - oy) for x, y in _umriss(zf)] for zf in ziffern]

    def gedreht(k, grad):
        a = math.radians(grad)
        ca, sa = math.cos(a), math.sin(a)
        return [(x * ca - y * sa, x * sa + y * ca) for x, y in pts[k]]

    luft, nachbar, nachbar2 = 1e9, 1e9, 1e9
    for j in range(10):
        for x, y in gedreht(j, -36.0 * j):
            luft = min(luft, -_sdf(x, y + rz, fw / 2.0, fh / 2.0, fr))
        for k in ((j + 1) % 10, (j - 1) % 10):
            for spiel in (0.0, -2.0, 2.0):
                m = min(_sdf(x, y + rz, fw / 2.0, fh / 2.0, fr) for x, y in gedreht(k, -36.0 * j + spiel))
                if spiel == 0.0:
                    nachbar = min(nachbar, m)
                else:
                    nachbar2 = min(nachbar2, m)
    # Luecke zwischen benachbarten Ziffern (Punkte nahe der Winkelhalbierenden)
    luecke = 1e9
    for k in range(10):
        a = math.radians(36 * k + 18)
        nx, ny = math.cos(a), math.sin(a)          # Normale der Halbierenden (Richtung sin a, -cos a)
        A = [q for q in pts[k] if abs(q[0] * nx + q[1] * ny) < 4.0]
        Bq = [q for q in pts[(k + 1) % 10] if abs(q[0] * nx + q[1] * ny) < 4.0]
        for x0, y0 in A:
            for x1, y1 in Bq:
                luecke = min(luecke, math.hypot(x1 - x0, y1 - y0))
    rs = [math.hypot(x, y) for q in pts for x, y in q]
    r_in, r_aus = min(rs), max(rs)
    oben = p['H'] - p['achse_v']
    R = p['rad_d'] / 2.0
    voll = R - (p['kerb_r'] - p['kerb_ueber'])
    fenster_r = math.hypot(fw / 2.0 - fr, rz + fh / 2.0 - fr) + fr
    t.log('    Ziffern: Radius %.2f .. %.2f, Luft im Fenster mind. %.2f mm, Nachbarziffer %.2f mm hinter dem '
          'Fensterrand (mit 2 Grad Spiel %.2f), Luecke zwischen Ziffern %.2f mm' % (r_in, r_aus, luft, nachbar,
                                                                                  nachbar2, luecke))
    t.log('    Oberkante %.2f mm ueber den Ziffern, Randbund %.2f mm ausserhalb, Fensterecke %.2f mm innerhalb '
          'des vollen Rads' % (oben - r_aus, p['rand_r'] - r_aus, voll - fenster_r))
    fehler = []
    if nachbar < 0.5:
        fehler.append('Nachbarziffer nur %.2f mm hinter dem Fensterrand' % nachbar)
    if luft < 1.0:
        fehler.append('Ziffer hat nur %.2f mm Luft im Fenster' % luft)
    if luecke < 0.8:
        fehler.append('Ziffern nur %.2f mm auseinander' % luecke)
    if r_aus > oben - 0.2:
        fehler.append('Ziffern reichen bis %.2f mm unter die Oberkante' % (oben - r_aus))
    if r_aus > p['rand_r'] - 0.2:
        fehler.append('Ziffern reichen unter den Randbund')
    if fenster_r > voll - 0.2:
        fehler.append('Fensterecke reicht in die Griffkerben')
    if fehler:
        raise RuntimeError('Ziffernrad: ' + '; '.join(fehler))


def fuss(t, p, ox, oy, logo):
    """Fuss in Montagelage um (ox, oy): Laenge FW in x, Tiefe FD in y, Schlitz entlang x."""
    t.objekt = 'fuss'
    FW, FD, FH = p['fuss']
    C.rounded_rect_body(t.root, ox - FW / 2.0, oy - FD / 2.0, ox + FW / 2.0, oy + FD / 2.0, p['fuss_r'],
                        '%g mm' % FH, 'fuss')
    M.fase_kanten(t, t.root.bRepBodies.itemByName('fuss'), p['fuss_fase'][0], z=0.0)
    M.fase_kanten(t, t.root.bRepBodies.itemByName('fuss'), p['fuss_fase'][1], z=FH)
    body = t.root.bRepBodies.itemByName('fuss')
    # Schlitz: Gehaeusedicke plus Spiel, 12 Grad geneigt, Boden senkrecht zu den Wangen
    sp = p['schlitz_spiel']
    dick = p['front_t'] + p['rueck_t'] + 2 * sp
    lage = _lage(p)
    ursprung = _plus(_punkt(lage, 0.0, 0.0, -sp), (ox, oy, 0.0))
    w = C.rect_body(t.root, t.xy, 0, -FW / 2.0 - 5.0, 0.0, FW / 2.0 + 5.0, 40.0, '%g mm' % (-dick), 'schlitz')
    t.auf(M.flaeche(ursprung, lage[1], lage[2]), [w])
    _kombi(t, body, [w], C.CUT)
    # Passfeder in der Schlitzmitte: steht auf dem Schlitzboden, reicht von Wange zu Wange
    kb, kt = p['kerbe']
    f = C.rect_body(t.root, t.xy, 0, -kb / 2.0 + sp, 0.0, kb / 2.0 - sp, kt - 0.4, '%g mm' % (-dick), 'feder')
    t.auf(M.flaeche(ursprung, lage[1], lage[2]), [f])
    _kombi(t, body, [f], C.JOIN)
    t.add(body, 'dunkel')
    if logo:
        g = t.logo('voll', p['logo_breite'], 0, 0, p['logo_tiefe'], mono='weiss')
        t.auf(M.vorn(oy - FD / 2.0, ox, p['logo_z']), g)
        t.einlegen(body, g)
    return body


def _standfestigkeit(t, log, p, lage, haupt):
    """Schwerpunkt aller Teile (gleiche Dichte) im Zusammenbau, Kippwinkel und Kippkraefte am Radoberrand."""
    vol, sx, sy, sz = 0.0, 0.0, 0.0, 0.0
    for b in t.koerper():
        pp = b.physicalProperties
        v = pp.volume * 1000.0
        c = pp.centerOfMass
        vol += v
        sx += v * c.x * 10.0
        sy += v * c.y * 10.0
        sz += v * c.z * 10.0
    gx, gy, gz = sx / vol, sy / vol, sz / vol
    FW, FD, _ = p['fuss']
    f0 = p['fuss_fase'][0]
    hinten, vorn, seite = FD / 2.0 - f0, -FD / 2.0 + f0, FW / 2.0 - f0
    R = p['rad_d'] / 2.0
    w_mitte = p['wand'] + p['bund'] + (p['front_t'] - p['wand'] - 2 * p['bund']) / 2.0
    top = _punkt(lage, 0.0, p['achse_v'] + R, w_mitte)
    masse = vol * 1.24e-3 * 0.8                 # PLA, gedruckt ca. 80 % voll (Schaetzung)
    G = masse * 9.81e-3
    log('    Standfestigkeit: Volumen %.0f cm3 (ca. %.0f g gedruckt), Schwerpunkt y %.1f z %.1f mm; '
        'Kippwinkel hinten %.0f, vorn %.0f, seitlich %.0f Grad'
        % (vol / 1000.0, masse, gy, gz, math.degrees(math.atan2(hinten - gy, gz)),
           math.degrees(math.atan2(gy - vorn, gz)), math.degrees(math.atan2(seite - abs(gx), gz))))
    log('    Radoberkante y %.1f z %.1f (Hinterkante Fuss y %.1f): waagerecht nach hinten kippt er ab %.2f N, '
        'seitlich ab %.2f N; Druck nach unten und entlang der Gehaeuseebene stabilisiert'
        % (top[1], top[2], hinten, G * (hinten - gy) / top[2], G * (seite - abs(gx)) / top[2]))


def zaehler(app, log, out, p, name, logo):
    t = M.Teil(app, log, name)
    B, H = p['B'], p['H']
    R = p['rad_d'] / 2.0
    us = [-p['teilung'], 0.0, p['teilung']]
    Rp = R + p['tasche_spiel']
    spiel = p['front_t'] - p['wand'] - 2 * p['bund'] - p['rad_t']
    log('    Gehaeuse %.1f x %.1f x %.1f mm, Seitenwand %.2f, Steg zwischen den Taschen %.2f mm'
        % (B, H, p['front_t'] + p['rueck_t'], B / 2.0 - p['teilung'] - Rp, p['teilung'] - 2 * Rp))
    log('    Rad %.1f mm, ragt oben %.1f mm heraus, axiales Spiel %.2f mm, radial %.2f mm je Seite'
        % (p['rad_d'], p['achse_v'] + R - H, spiel, p['lager_spiel']))
    L, fb, ft, _ = p['finger']
    hub = p['rast_tiefe'] - p['nase_luft'] - spiel               # Auslenkung des Fingers zwischen zwei Rasten
    kraft = 3000.0 * fb * ft ** 3 * hub / (4 * L ** 3)
    log('    Rastfinger radial: Auslenkung %.2f mm, Randdehnung %.2f %%, Kraft ca. %.1f N (PLA, E = 3000 MPa), '
        'am Radrand ca. %.1f .. %.1f N (Reibung 0,25 .. 0,4)'
        % (hub, 150.0 * hub * ft / L ** 2, kraft, kraft * 1.25 / 0.75 * p['rast_r'] / R,
           kraft * 1.4 / 0.6 * p['rast_r'] / R))

    # Drucklage: Frontschale, Rueckplatte darueber, Raeder in einer Reihe darunter, Fuss quer rechts daneben
    g = p['abstand']
    FW, FD, _ = p['fuss']
    o_front = (0.0, 0.0)
    o_rueck = (0.0, H + g)
    y_rad = -(H / 2.0 + g + R)
    o_rad = [(i * (2 * R + g), y_rad) for i in (-1, 0, 1)]
    y0, y1 = y_rad - R, o_rueck[1] + H / 2.0
    o_fuss = (B / 2.0 + g + FD / 2.0, (y0 + y1) / 2.0)
    x0, x1 = -B / 2.0, o_fuss[0] + FD / 2.0
    log('    Drucklage: %.1f x %.1f mm (Fuss %.0f mm lang)' % (x1 - x0, y1 - y0, FW))
    if max(x1 - x0, y1 - y0, FW) > p['bett']:
        raise RuntimeError('Drucklage groesser als %.0f mm' % p['bett'])

    cap = _ziffern_kal(t, p)
    haupt = [frontschale(t, p, *o_front), rueckplatte(t, p, *o_rueck)]
    for i, o in enumerate(o_rad):
        haupt.append(rad(t, p, o[0], o[1], 'rad%d' % (i + 1), cap, messen=(i == 0)))
    haupt.append(fuss(t, p, 0.0, 0.0, logo))
    # Fuss um 90 Grad gedreht neben die Platten legen
    t.auf(_matrix((0.0, 0.0, 0.0), (o_fuss[0], o_fuss[1], 0.0), (0, 1, 0), (-1, 0, 0), (0, 0, 1)),
          t.koerper(objekt='fuss'))

    lage = _lage(p)
    _, U, V, W = lage
    nW = tuple(-x for x in W)
    nU = tuple(-x for x in U)
    dick = p['front_t'] + p['rueck_t']

    def montage():
        # Bild der Drucklage (zeigt alle Ziffern und die Innenseiten), dann zusammensetzen
        C.hide_helpers(t.design)
        bb = C.bbox_mm([it[0] for it in t.items])
        log('    Drucklage gemessen: %.1f x %.1f mm' % (bb[3] - bb[0], bb[4] - bb[1]))
        C.snapshot(app, os.path.join(out['preview'], name + '_drucklage.png'),
                   ((bb[0] + bb[3]) / 2.0, (bb[1] + bb[4]) / 2.0, 0.0), (0, 0, 400), up=(0, 1, 0), margin=1.05)
        t.auf(_matrix((o_fuss[0], o_fuss[1], 0.0), (0.0, 0.0, 0.0), (0, -1, 0), (1, 0, 0), (0, 0, 1)),
              t.koerper(objekt='fuss'))
        t.auf(_matrix((o_front[0], o_front[1], 0.0), _punkt(lage, 0.0, H / 2.0, 0.0), nU, V, W),
              t.koerper(objekt='front'))
        t.auf(_matrix((o_rueck[0], o_rueck[1], 0.0), _punkt(lage, 0.0, H / 2.0, dick), U, V, nW),
              t.koerper(objekt='rueck'))
        w_hinten = p['wand'] + p['bund'] + spiel / 2.0 + p['rad_t']     # Radrueckseite, Rad mittig im Spiel
        for i, (u, o) in enumerate(zip(us, o_rad)):
            th = math.radians(-36.0 * int(p['anzeige'][i]))             # Rad im Uhrzeigersinn bis zur Ziffer
            ex = _plus(tuple(math.cos(th) * x for x in U), V, math.sin(th))
            ey = _plus(tuple(-math.sin(th) * x for x in U), V, math.cos(th))
            t.auf(_matrix((o[0], o[1], 0.0), _punkt(lage, u, p['achse_v'], w_hinten), ex, ey, nW),
                  t.koerper(objekt='rad%d' % (i + 1)))
        # Durchdringen sich die Teile im Zusammenbau?
        try:
            inp = t.design.createInterferenceInput(_koll(haupt))
            inp.areCoincidentFacesIncluded = False
            res = t.design.analyzeInterference(inp)
            treffer = 0
            for i in range(res.count):
                r = res.item(i)
                vol = r.interferenceBody.volume * 1000.0
                if vol > 0.01:
                    treffer += 1
                    log('  Hinweis: Durchdringung %s / %s: %.2f mm3' % (r.entityOne.name, r.entityTwo.name, vol))
            log('    Zusammenbau: %d Durchdringungen zwischen den %d Grundkoerpern' % (treffer, len(haupt)))
        except Exception as ex:
            log('  Hinweis: Durchdringungspruefung nicht moeglich: %s' % ex)
        try:
            _standfestigkeit(t, log, p, lage, haupt)
        except Exception as ex:
            log('  Hinweis: Standfestigkeit nicht berechnet: %s' % ex)

    t.fertig(out, ansichten=[('', (-45, -110, 35), (0, 0, 1)),
                             ('_vorn', (0, -147, 31), (0, 0, 1)),
                             ('_hinten', (60, 120, 50), (0, 0, 1)),
                             ('_oben', (0, -60, 200), (0, 0, 1))],
             montage=montage, rand=0.85)
    return t


def build(app, log, out, nur=None):
    for name, logo in (('drehzaehler_logo', True), ('drehzaehler_neutral', False)):
        if nur and not any(n in name for n in nur):
            continue
        zaehler(app, log, out, P, name, logo)
