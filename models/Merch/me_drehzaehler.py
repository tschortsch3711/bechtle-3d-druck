# Drehzaehler "Stabiler Betrieb seit 365 Tagen" (Konzept v3, Variante B): drei Ziffernwalzen nebeneinander auf einer
# gemeinsamen waagerechten Achse wie bei einem Kilometerzaehler. Gehaeuse 150 x 58 x 56 mm: dunkler Sockel (11 mm)
# mit Logo, darueber der gruene Koerper mit senkrechter Front (Blende bis 56 mm hoch), flacher Oberseite (50 mm) und
# rundem Ruecken (Radius 22). Die Walzen (D 50 x 16, Teilung 18,5) ragen oben 2,5 mm aus drei Schlitzen hinter der
# Blende und werden mit dem Daumen gedreht; vorn zeigt je ein Fenster 13,5 x 16 die Ziffer (Impact, 12 mm hoch).
#
# Koordinaten (Zusammenbau): x nach rechts, y nach hinten (Front y = -29), z nach oben (Tisch z = 0).
# Walzenachse bei y = -1,5, z = 27,5 (2 mm Frontwand + 0,5 mm Luft vor der Walze).
#
# Druckobjekte (alle ohne Stuetzen, 0,2 mm Schichten, eine Druckplatte ca. 220 x 215 mm, Werte im Protokoll):
#   sockel    Experience Green, steht auf der Unterseite. Drei Walzenmulden, vier Achsstuetzen (Stege, die die Achse
#             von unten in die V-Kerben des Gehaeuses druecken), vier Passstifte D 4 nach oben, Logo-Variante mit
#             weissem Logo (40 mm) in der Front (0,8 mm tief, Farbwechsel je Schicht).
#   gehaeuse  Progressive Green, steht aufrecht (Unterseite auf dem Bett), unten offen. Vollkoerper (Fuellung macht ihn
#             schwer und standfest) mit drei Walzentaschen; die Taschen haben oben ein 45-Grad-Dach (vorn) bzw. eine
#             senkrechte Wand (hinten) und laufen oben als Schlitze aus. Zwischen den Taschen Trennwaende 2,1 mm mit
#             V-Kerbe fuer die Achse und je einer Rastzunge; die linke Endwand hat ebenfalls eine Rastzunge.
#   blende    Progressive Green, liegt mit der Sichtseite auf dem Bett: weisse Schrift (1,0 mm) und dunkles Anzeigefeld
#             (0,6 mm) in den ersten Schichten, drei Fenster, hinten Walzenmulde und vier Passstifte nach oben.
#   walze1-3  Experience Green + Weiss, Achse senkrecht, linke Stirnseite (mit den zehn Rastmulden) auf dem Bett.
#             Ziffern 0,8 mm tief in der Mantelflaeche (Farbwechsel je Schicht), zehn Griffrillen zwischen den Ziffern.
#   achse     Experience Green, liegt (Profil: Kreis D 6 mit 45-Grad-Kiel und Flaeche unten).
#
# Rastung: Jede Walze hat links zehn Kegelmulden (Teilkreis r 16, 36 Grad), in der Wand links daneben haengt eine
# senkrechte Federzunge (1,2 mm dick, Wurzel oben) mit einem 45-Grad-Kegelnoppen. Der Noppen drueckt die Walze gegen
# die rechte Wand und rastet je Ziffer ein; der symmetrische Kegel fuehlt sich in beiden Richtungen gleich an.
#
# Montage: 1. Die drei Walzen (Mulden links, Ziffern aufrecht von vorn gesehen) auf die Achse schieben.
# 2. Gehaeuse auf den Kopf legen, Walzen samt Achse von unten in die Taschen druecken (die Zungen federn aus, die
#    Achsenden liegen in den Sackkerben der Endwaende). 3. Sockel aufsetzen: die Stuetzen fassen unter die Achse, die
#    Passstifte (D 4 in D 4,45, Fase) in die Loecher des Gehaeuses druecken. 4. Blende mit ihren vier Stiften vorn
#    aufstecken. Sitzt ein Stift zu locker: ein Tropfen Kleber. 5. Ziffern mit dem Daumen einstellen.
import math
import os
import tempfile

import adsk.core
import adsk.fusion

import me_common as M
from me_common import C

PARAM = dict(
    # Gehaeuse (Konzept B)
    B=150.0, D=58.0, H=50.0, Hv=56.0, sockel=11.0,
    blende=6.0, rb=22.0,               # Blendendicke, Radius des Rueckens
    fase=0.8,
    # Walzen
    teilung=18.5, R=25.0, walze_b=16.0, ya=-1.5, za=27.5,
    spiel_r=0.4, spiel_ax=0.2,         # Walze in Tasche / Mulde (radial), Walze zu den Waenden (je Seite)
    rand=2.4, steg=2.4, nabe_d=12.0,   # Mantel, Stirnwand links, Nabe
    walze_fase=0.6,
    rillen=(0.6, 18.0),                # Griffrillen (90 Grad V): Tiefe, Winkel zur Ziffer
    endwand=3.0,                       # Endwaende der Walzenkammer (danach voll)
    # Achse
    achse_d=6.0, achse_flach=2.5,      # Flaeche 2,5 unter der Mitte (Drucklage), Lagerspiel = spiel_lager
    spiel_lager=0.4,                   # Bohrung der Walze D 6,8
    kerbe_b=6.4, sack=2.0,             # Breite der Achskerbe, Tiefe der Sackkerbe in den Endwaenden
    stuetze_spiel=0.2,
    # Rastung
    rast_r=16.0, rast_w=40.0,          # Noppen auf dem Teilkreis r, 40 Grad hinter der Senkrechten unter der Achse
    zunge=(6.0, 1.2, 32.6, 0.6),       # Breite, Dicke, Hoehe der Wurzel (z), Schlitz ringsum
    noppen=(1.2, 0.3),                 # Hoehe ueber der Zungenflaeche, Radius der Spitze (Flanken 45 Grad)
    mulde=(1.1, 1.0),                  # Radius an der Stirnflaeche, Tiefe
    # Ziffern und Fenster
    ziffer_h=12.0, ziffer_font='Impact', ziffer_bold=False, ziffer_7=0.477, tiefe_ziffer=0.8,
    fenster=(13.5, 16.0, 2.0),         # Konzept 17 hoch; 16: Nachbarziffern bleiben bis ca. 20 Grad Blickhoehe verdeckt
                                       # (bei 17 nur bis ca. 10 Grad), die Ziffer ist bis ca. 26 Grad ganz zu sehen
    feld=(60.5, 20.0, 3.0), tiefe_feld=0.6,
    # Schrift
    tiefe_schrift=1.0,
    kopf=('STABILER BETRIEB', 6.0, 46.8, 81.0),       # Text, Versalhoehe, z, Breite (wie im Konzept)
    seit=('SEIT', 6.0, -37.5, 27.5, 17.8),            # Text, Versalhoehe, x (rechtsbuendig), z, Breite
    tagen=('TAGEN', 6.0, 37.5, 27.5, 28.8),           # x linksbuendig
    logo_breite=40.0, logo_tiefe=0.8,
    # Passstifte
    stift_d=4.0, stift_l=5.0, stift_spiel=0.225, stift_fase=0.5,
    stifte_unten=[(-50.0, -10.0), (50.0, -10.0), (-50.0, 15.0), (50.0, 15.0)],   # (x, y) Sockel -> Gehaeuse
    stifte_vorn=[(-50.0, 20.0), (50.0, 20.0), (-50.0, 44.0), (50.0, 44.0)],      # (x, z) Blende -> Gehaeuse
    # Drucklage
    abstand=4.0, bett=240.0,
    # Vorschau
    anzeige='365',
    montage_stl=True,                  # Zusammenbau zusaetzlich als STL ins Temp-Verzeichnis (fuer Pruefskripte)
)


# ---------- kleine Helfer ----------
def _koll(xs):
    col = adsk.core.ObjectCollection.create()
    for x in xs:
        col.add(x)
    return col


# Rahmen fuer Prismen: Skizze in (u, v), Extrusion entlang w. Rahmen = (Ursprung, u-Richtung, v-Richtung).
RX = ((0, 0, 0), (0, 1, 0), (0, 0, 1))        # u = y, v = z, w = x
RY = ((0, 0, 0), (-1, 0, 0), (0, 0, 1))       # u = -x, v = z, w = y
RZ = ((0, 0, 0), (1, 0, 0), (0, 1, 0))        # u = x, v = y, w = z


def _ring(pr):
    return pr.profileLoops.count == 2


def _koerper(t, zeichne, w0, w1, name, rahmen=RZ, taper=None, wahl=None):
    """Skizze in lokalen (u, v) (zeichne(sk, P) mit P(u, v) -> Skizzenpunkt), Extrusion von w0 bis w1, dann in den
    Rahmen gelegt. taper in Grad (negativ = verjuengt sich), wahl filtert die Profile.
    Rueckgabe: Liste der neuen Koerper."""
    sk = t.root.sketches.add(t.xy)
    sk.name = t._nm(name) + '_Skizze'
    sk.isComputeDeferred = True
    zeichne(sk, lambda u, v: C.P(u, v))
    sk.isComputeDeferred = False
    profs = [sk.profiles.item(i) for i in range(sk.profiles.count)]
    if wahl:
        profs = [pr for pr in profs if wahl(pr)]
    ext = t.root.features.extrudeFeatures
    ei = ext.createInput(_koll(profs), C.NEW)
    ei.startExtent = adsk.fusion.OffsetStartDefinition.create(C.V(w0))
    if taper:
        ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(C.V(w1 - w0)),
                            adsk.fusion.ExtentDirections.PositiveExtentDirection,
                            adsk.core.ValueInput.createByString('%g deg' % taper))
    else:
        ei.setDistanceExtent(False, C.V(w1 - w0))
    e = ext.add(ei)
    bodies = [e.bodies.item(i) for i in range(e.bodies.count)]
    nm = t._nm(name)
    for i, b in enumerate(bodies):
        b.name = '%s_%d' % (nm, i + 1)
    if rahmen is not RZ:
        t.auf(M.flaeche(*rahmen), bodies)
    return bodies


def _kreis(sk, P, u, v, r):
    sk.sketchCurves.sketchCircles.addByCenterRadius(P(u, v), C.cm(r))


def _poly(sk, P, pts):
    lines = sk.sketchCurves.sketchLines
    sp = [P(u, v) for u, v in pts]
    first = lines.addByTwoPoints(sp[0], sp[1])
    last = first
    for q in sp[2:]:
        last = lines.addByTwoPoints(last.endSketchPoint, q)
    lines.addByTwoPoints(last.endSketchPoint, first.startSketchPoint)


def _rechteck(sk, P, u0, v0, u1, v1):
    sk.sketchCurves.sketchLines.addTwoPointRectangle(P(u0, v0), P(u1, v1))


def _quader(t, x0, y0, z0, x1, y1, z1, name):
    return _koerper(t, lambda sk, P: _rechteck(sk, P, x0, y0, x1, y1), z0, z1, name)


def _zyl_x(t, y, z, r, x0, x1, name):
    return _koerper(t, lambda sk, P: _kreis(sk, P, y, z, r), x0, x1, name, RX)


def _kegel_x(t, y, z, r0, x0, laenge, name):
    """Kegelstumpf entlang +x: Radius r0 bei x0, 45 Grad schmaler werdend ueber laenge."""
    return _koerper(t, lambda sk, P: _kreis(sk, P, y, z, r0), x0, x0 + laenge, name, RX, taper=-45.0)


def _kombi(t, ziel, werkzeuge, op, behalten=False):
    werkzeuge = [w for w in werkzeuge if w is not None]
    if not werkzeuge:
        return
    ci = t.root.features.combineFeatures.createInput(ziel, _koll(werkzeuge))
    ci.operation = op
    ci.isKeepToolBodies = behalten
    t.root.features.combineFeatures.add(ci)


def _entfernen(t, body):
    """Hilfskoerper (Werkzeug) aus dem Modell nehmen."""
    try:
        t.root.features.removeFeatures.add(body)
    except Exception:
        body.deleteMe()
    if body.isValid and body.isVisible:
        body.isVisible = False
        t.log('  Hinweis: Hilfskoerper %s nur ausgeblendet' % body.name)


def _fase(t, kanten, d, was):
    if not kanten:
        return
    try:
        cf = t.root.features.chamferFeatures
        ci = cf.createInput2()
        ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(_koll(kanten), C.V(d), False)
        cf.add(ci)
    except Exception as ex:
        t.log('  Hinweis: Fase %s nicht moeglich (%s)' % (was, str(ex).splitlines()[0]))


def _kanten(body, test):
    """Kanten, deren Box (mm) test(x0, y0, z0, x1, y1, z1) erfuellt."""
    out = []
    for e in body.edges:
        a, b = e.boundingBox.minPoint, e.boundingBox.maxPoint
        if test(a.x * 10, a.y * 10, a.z * 10, b.x * 10, b.y * 10, b.z * 10):
            out.append(e)
    return out


def _kreiskanten(body, r, xs):
    """Kreiskanten mit Radius r (mm), Mittelpunkt bei einem der x-Werte (Achse parallel zu x)."""
    out = []
    for e in body.edges:
        c = adsk.core.Circle3D.cast(e.geometry)
        if c is None or abs(c.radius * 10 - r) > 1e-3:
            continue
        if any(abs(c.center.x * 10 - x) < 1e-3 for x in xs):
            out.append(e)
    return out


def _schieben(dx, dy, dz):
    m = adsk.core.Matrix3D.create()
    m.translation = adsk.core.Vector3D.create(C.cm(dx), C.cm(dy), C.cm(dz))
    return m


def _dreh_x(grad, y, z):
    m = adsk.core.Matrix3D.create()
    m.setToRotation(math.radians(grad), adsk.core.Vector3D.create(1, 0, 0), C.P(0, y, z))
    return m


def _rot(spalten):
    """Drehmatrix um den Ursprung; spalten = Bilder der Einheitsvektoren x, y, z."""
    m = adsk.core.Matrix3D.create()
    m.setWithCoordinateSystem(C.P(0, 0, 0), *[adsk.core.Vector3D.create(*s) for s in spalten])
    return m


def _transponiert(spalten):
    return tuple(tuple(spalten[j][i] for j in range(3)) for i in range(3))


def _psi(p, psi, r=None):
    """Punkt (y, z) auf dem Kreis um die Walzenachse; psi = 0 vorn, positiv nach oben."""
    r = p['R'] if r is None else r
    a = math.radians(psi)
    return p['ya'] - r * math.cos(a), p['za'] + r * math.sin(a)


def _mitten(p):
    return [(i - 1) * p['teilung'] for i in range(3)]


# ---------- Walzen ----------
def _ziffern_kal(t, p):
    """Schrift pruefen und Texthoehe so waehlen, dass die Ziffern (Box von 0 bis 9) ziffer_h hoch werden."""
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


def _schneiden(t, ziel, werkzeug):
    """ziel = ziel geschnitten mit werkzeug (Werkzeug bleibt). Neue Teilkoerper erben Farbe und Objekt."""
    vor = [b for b in t.root.bRepBodies]
    _kombi(t, ziel, [werkzeug], adsk.fusion.FeatureOperations.IntersectFeatureOperation, behalten=True)
    out = [ziel]
    if t.root.bRepBodies.count != len(vor):
        it = t._eintrag(ziel)
        for b in t.root.bRepBodies:
            if not any(b == v for v in vor):
                t.items.append([b, it[1], it[2]])
                out.append(b)
    return out


def walze(t, p, i, cap):
    """Walze i (0..2) in Ruhelage im Zusammenbau: Ziffer 0 vorn, Ziffer k bei psi = -36 k (k + 1 steht unter k).
    Rastmulde k bei psi_noppen - 36 k: zeigt das Fenster k, sitzt der Noppen in Mulde k."""
    c = _mitten(p)[i]
    t.objekt = 'walze%d' % (i + 1)
    R, b, ya, za = p['R'], p['walze_b'], p['ya'], p['za']
    x0, x1 = c - b / 2.0, c + b / 2.0
    body = _zyl_x(t, ya, za, R, x0, x1, t.objekt)[0]
    nm = body.name
    # Kammer nach rechts offen: Mantel, Stirnwand links, Nabe; Bohrung
    rb_ = R - p['rand']
    kammer = _koerper(t, lambda sk, P: (_kreis(sk, P, ya, za, rb_), _kreis(sk, P, ya, za, p['nabe_d'] / 2.0)),
                      x0 + p['steg'], x1 + 1.0, 'kammer', RX, wahl=_ring)
    bohr = _zyl_x(t, ya, za, p['achse_d'] / 2.0 + p['spiel_lager'], x0 - 1.0, x1 + 1.0, 'bohrung')
    _kombi(t, body, kammer + bohr, C.CUT)
    body = t.root.bRepBodies.itemByName(nm)
    _fase(t, _kreiskanten(body, R, [x0, x1]), p['walze_fase'], 'Walzenrand')
    body = t.root.bRepBodies.itemByName(nm)
    _fase(t, _kreiskanten(body, p['achse_d'] / 2.0 + p['spiel_lager'], [x0, x1]), 0.4, 'Bohrung')
    body = t.root.bRepBodies.itemByName(nm)
    # Griffrillen (90-Grad-V) zwischen den Ziffern
    tief, w = p['rillen']
    rillen = []
    for k in range(10):
        ps = -36.0 * k + w
        a = math.radians(ps)
        ty, tz = math.sin(a), math.cos(a)
        sp = _psi(p, ps, R - tief)
        ay, az = _psi(p, ps, R + 0.5)
        h = tief + 0.5
        pts = [sp, (ay + h * ty, az + h * tz), (ay - h * ty, az - h * tz)]
        rillen += _koerper(t, lambda sk, P, pts=pts: _poly(sk, P, pts), x0 - 1.0, x1 + 1.0, 'rille', RX)
    _kombi(t, body, rillen, C.CUT)
    body = t.root.bRepBodies.itemByName(nm)
    # Rastmulden (Kegel 45 Grad) in der linken Stirnflaeche
    mr, mt = p['mulde']
    ps_n = -(90.0 + p['rast_w'])
    mulden = []
    for k in range(10):
        y, z = _psi(p, ps_n - 36.0 * k, p['rast_r'])
        mulden += _kegel_x(t, y, z, mr + 0.2, x0 - 0.2, mt + 0.2, 'mulde')     # Grund: Radius mr - mt
    _kombi(t, body, mulden, C.CUT)
    body = t.root.bRepBodies.itemByName(nm)
    t.add(body, 'dunkel')

    # Ziffern: flacher Text, gerade durch den Mantel extrudiert und mit der 0,8-mm-Schale geschnitten; von vorn
    # gesehen sieht die Ziffer genau wie der flache Text aus. Dann um die Achse auf ihren Platz gedreht.
    td = p['tiefe_ziffer']
    schale = _koerper(t, lambda sk, P: (_kreis(sk, P, ya, za, R), _kreis(sk, P, ya, za, R - td)),
                      x0, x1, 'schale', RX, wahl=_ring)[0]
    g = []
    for k in range(10):
        zf = t.text(str(k), cap, 0, 0, 3.0, 'weiss', font=p['ziffer_font'], bold=p['ziffer_bold'])
        bb = C.bbox_mm(zf)
        cx, cy = (bb[0] + bb[3]) / 2.0, (bb[1] + bb[4]) / 2.0
        t.auf(M.flaeche((c - cx, ya - R - 0.5, za - cy), (1, 0, 0), (0, 0, 1)), zf)
        teile = []
        for zb in zf:
            teile += _schneiden(t, zb, schale)
        if k:
            t.auf(_dreh_x(36.0 * k, ya, za), teile)
        g += teile
    _entfernen(t, schale)
    t.einlegen(body, g)
    return body


# ---------- Gehaeuse ----------
def _noppen(p):
    """Lage der Rastnoppen (y, z) und die Zungenflaechen x (Wand links neben Walze i)."""
    a = math.radians(p['rast_w'])
    yb, zb = p['ya'] + p['rast_r'] * math.sin(a), p['za'] - p['rast_r'] * math.cos(a)
    xf = [c - p['walze_b'] / 2.0 - p['spiel_ax'] for c in _mitten(p)]
    return yb, zb, xf


def _taschen_x(p):
    """x-Bereiche der Walzentaschen."""
    h = p['walze_b'] / 2.0 + p['spiel_ax']
    return [(c - h, c + h) for c in _mitten(p)]


def gehaeuse(t, p):
    t.objekt = 'gehaeuse'
    B, D, H, S = p['B'], p['D'], p['H'], p['sockel']
    ya, za = p['ya'], p['za']
    yF, yB, rb = -D / 2.0 + p['blende'], D / 2.0, p['rb']
    cy, cz = yB - rb, H - rb
    s45 = math.sqrt(0.5)

    def profil(sk, P):
        lines, arcs = sk.sketchCurves.sketchLines, sk.sketchCurves.sketchArcs
        arc = arcs.addByThreePoints(P(cy, H), P(cy + rb * s45, cz + rb * s45), P(yB, cz))

        def nah(q):
            return min((arc.startSketchPoint, arc.endSketchPoint), key=lambda s: s.geometry.distanceTo(q))
        pa, pb = nah(P(cy, H)), nah(P(yB, cz))
        l1 = lines.addByTwoPoints(pb, P(yB, S))
        l2 = lines.addByTwoPoints(l1.endSketchPoint, P(yF, S))
        l3 = lines.addByTwoPoints(l2.endSketchPoint, P(yF, H))
        lines.addByTwoPoints(l3.endSketchPoint, pa)

    body = _koerper(t, profil, -B / 2.0, B / 2.0, 'gehaeuse', RX)[0]
    nm = body.name
    # Fase an den Seitenflaechen (nicht an der Vorderkante, dort sitzt die Blende)
    _fase(t, _kanten(body, lambda x0, y0, z0, x1, y1, z1: abs(x1 - x0) < 1e-3 and abs(abs(x0) - B / 2.0) < 1e-3
                     and not (abs(y0 - yF) < 1e-3 and abs(y1 - yF) < 1e-3)), p['fase'], 'Gehaeuseseiten')
    body = t.root.bRepBodies.itemByName(nm)

    # Walzentaschen: Kreis (Spiel), darunter offen bis zur Unterseite, oben vorn 45-Grad-Dach, hinten senkrecht
    Rp = p['R'] + p['spiel_r']
    q = Rp * s45
    zt = H - za + 3.0
    weg = []
    for xa, xb in _taschen_x(p):
        weg += _zyl_x(t, ya, za, Rp, xa, xb, 'tasche')
        dach = [(ya - q, za + q), (ya - q + (zt - q), za + zt), (ya + q, za + zt), (ya + q, za + q), (ya, za)]
        weg += _koerper(t, lambda sk, P, d=dach: _poly(sk, P, d), xa, xb, 'dach', RX)
        weg += _koerper(t, lambda sk, P: _rechteck(sk, P, ya - Rp, S - 1.0, ya + Rp, za), xa, xb, 'unten', RX)
    # Achskerben (V oben, Achse liegt auf den 45-Grad-Flanken): durch die Trennwaende, als Sackkerbe in die Endwaende
    k, r = p['kerbe_b'] / 2.0, p['achse_d'] / 2.0
    spitze = r * math.sqrt(2.0)
    kerbe = [(ya - k, S - 1.0), (ya + k, S - 1.0), (ya + k, za + spitze - k), (ya, za + spitze), (ya - k, za + spitze - k)]
    tx = _taschen_x(p)
    for xa, xb in [(tx[0][1] - 0.1, tx[1][0] + 0.1), (tx[1][1] - 0.1, tx[2][0] + 0.1),
                   (tx[0][0] - p['sack'], tx[0][0] + 0.1), (tx[2][1] - 0.1, tx[2][1] + p['sack'])]:
        weg += _koerper(t, lambda sk, P: _poly(sk, P, kerbe), xa, xb, 'kerbe', RX)
    # Federzungen: Fenster durch die Wand (unten offen), Zunge an der Wandflaeche zur Walze, Wurzel oben
    zb_, zd, zw, sl = p['zunge']
    yb, zb, xf = _noppen(p)
    for i, x in enumerate(xf):
        hinten = p['endwand'] + 0.9 if i == 0 else tx[i][0] - tx[i - 1][1] + 0.1
        weg += _quader(t, x - hinten, yb - zb_ / 2.0 - sl, S - 1.0, x + 0.1, yb + zb_ / 2.0 + sl, zw, 'zungenfenster')
    # Stiftloecher unten (mit Einfuehrfase) und vorn (Tropfenform, oben 45 Grad)
    rh = p['stift_d'] / 2.0 + p['stift_spiel']
    tl = p['stift_l'] + 0.4
    for x, y in p['stifte_unten']:
        weg += _koerper(t, lambda sk, P, x=x, y=y: _kreis(sk, P, x, y, rh), S - 1.0, S + tl, 'stiftloch')
        weg += _koerper(t, lambda sk, P, x=x, y=y: _kreis(sk, P, x, y, rh + 0.8), S - 0.4, S + 0.4, 'senker',
                        taper=-45.0)
    for x, z in p['stifte_vorn']:
        tropfen = [(-x + rh * s45, z + rh * s45), (-x, z + rh * math.sqrt(2.0)), (-x - rh * s45, z + rh * s45)]
        weg += _koerper(t, lambda sk, P, x=x, z=z, tr=tropfen: (_kreis(sk, P, -x, z, rh), _poly(sk, P, tr)),
                        yF - 0.5, yF + tl, 'stiftloch', RY)
    _kombi(t, body, weg, C.CUT)
    body = t.root.bRepBodies.itemByName(nm)

    # Zungen mit Kegelnoppen
    nh, nr = p['noppen']
    teile = []
    for x in xf:
        teile += _quader(t, x - zd, yb - zb_ / 2.0, S, x, yb + zb_ / 2.0, zw + 0.4, 'zunge')
        teile += _kegel_x(t, yb, zb, nr + nh + 0.2, x - 0.2, nh + 0.2, 'noppen')
    _kombi(t, body, teile, C.JOIN)
    body = t.root.bRepBodies.itemByName(nm)
    t.add(body, 'mittel')
    return body


# ---------- Sockel ----------
def sockel(t, p, logo):
    t.objekt = 'sockel'
    B, D, S = p['B'], p['D'], p['sockel']
    ya, za = p['ya'], p['za']
    body = _quader(t, -B / 2.0, -D / 2.0, 0.0, B / 2.0, D / 2.0, S, 'sockel')[0]
    nm = body.name
    _fase(t, list(body.edges), p['fase'], 'Sockel')
    body = t.root.bRepBodies.itemByName(nm)
    # Walzenmulden und Aussparungen unter den Zungenenden
    Rp = p['R'] + p['spiel_r']
    tx = _taschen_x(p)
    weg = []
    for xa, xb in tx:
        weg += _zyl_x(t, ya, za, Rp, xa, xb, 'mulde')
    zb_, zd, _, sl = p['zunge']
    yb, _, xf = _noppen(p)
    for x in xf:
        weg += _quader(t, x - zd - 0.6, yb - zb_ / 2.0 - sl, S - 1.0, x + 0.2, yb + zb_ / 2.0 + sl, S + 0.5, 'frei')
    _kombi(t, body, weg, C.CUT)
    body = t.root.bRepBodies.itemByName(nm)
    # Achsstuetzen (in den Kerben, 0,2 mm Luft je Seite, oben auf der Flaeche der Achse) und Passstifte
    k = p['kerbe_b'] / 2.0 - p['stuetze_spiel']
    zo = za - p['achse_flach']
    sx = [(tx[0][1] + 0.2, tx[1][0] - 0.2), (tx[1][1] + 0.2, tx[2][0] - 0.2),
          (tx[0][0] - p['sack'] + p['spiel_ax'], tx[0][0] - 0.2), (tx[2][1] + 0.2, tx[2][1] + p['sack'] - p['spiel_ax'])]
    teile = []
    for xa, xb in sx:
        teile += _quader(t, xa, ya - k, S - 0.5, xb, ya + k, zo, 'stuetze')
    r, f, L = p['stift_d'] / 2.0, p['stift_fase'], p['stift_l']
    for x, y in p['stifte_unten']:
        teile += _koerper(t, lambda sk, P, x=x, y=y: _kreis(sk, P, x, y, r), S - 0.5, S + L - f, 'stift')
        teile += _koerper(t, lambda sk, P, x=x, y=y: _kreis(sk, P, x, y, r), S + L - f, S + L, 'spitze', taper=-45.0)
    _kombi(t, body, teile, C.JOIN)
    body = t.root.bRepBodies.itemByName(nm)
    t.add(body, 'dunkel')
    if logo:
        g = t.logo('voll', p['logo_breite'], 0, 0, p['logo_tiefe'], mono='weiss')
        bb = C.bbox_mm(g)
        t.log('    Logo: %.1f x %.1f mm, %.1f mm tief' % (bb[3] - bb[0], bb[4] - bb[1], p['logo_tiefe']))
        t.auf(M.vorn(-D / 2.0, 0.0, S / 2.0), g)
        t.einlegen(body, g)
    return body


# ---------- Blende ----------
def _abstand(t, s, cap, breite):
    """Zeichenabstand, mit dem der Text (Segoe UI fett) die Breite aus dem Konzept bekommt."""
    w0 = t.text_breite(s, cap, abstand=0)
    w1 = t.text_breite(s, cap, abstand=20)
    return max(0, int(round(20.0 * (breite - w0) / (w1 - w0))))


def blende(t, p):
    t.objekt = 'blende'
    B, D, S, Hv = p['B'], p['D'], p['sockel'], p['Hv']
    ya, za = p['ya'], p['za']
    y0, y1 = -D / 2.0, -D / 2.0 + p['blende']
    body = _quader(t, -B / 2.0, y0, S, B / 2.0, y1, Hv, 'blende')[0]
    nm = body.name
    _fase(t, _kanten(body, lambda x0, yy0, z0, x1, yy1, z1: (abs(yy0 - y0) < 1e-3 and abs(yy1 - y0) < 1e-3)
                     or (abs(z0 - Hv) < 1e-3 and abs(z1 - Hv) < 1e-3)), p['fase'], 'Blende')
    body = t.root.bRepBodies.itemByName(nm)
    tx = _taschen_x(p)
    _kombi(t, body, _zyl_x(t, ya, za, p['R'] + p['spiel_r'], tx[0][0], tx[2][1], 'mulde'), C.CUT)
    body = t.root.bRepBodies.itemByName(nm)
    r, f, L = p['stift_d'] / 2.0, p['stift_fase'], p['stift_l']
    teile = []
    for x, z in p['stifte_vorn']:
        teile += _koerper(t, lambda sk, P, x=x, z=z: _kreis(sk, P, -x, z, r), y1 - 0.5, y1 + L - f, 'stift', RY)
        teile += _koerper(t, lambda sk, P, x=x, z=z: _kreis(sk, P, -x, z, r), y1 + L - f, y1 + L, 'spitze', RY,
                          taper=-45.0)
    _kombi(t, body, teile, C.JOIN)
    body = t.root.bRepBodies.itemByName(nm)
    t.add(body, 'mittel')

    # Einlagen auf der Sichtseite (liegt auf dem Bett): Anzeigefeld dunkel, Schrift weiss
    fb, fh, fr = p['feld']
    feld = t.rechteck(-fb / 2.0, -fh / 2.0, fb / 2.0, fh / 2.0, p['tiefe_feld'], 'dunkel', r=fr)
    t.auf(M.vorn(y0, 0.0, za), feld)
    td = p['tiefe_schrift']
    texte = []
    s, cap, z, breite = p['kopf']
    a = _abstand(t, s, cap, breite)
    k = t.text(s, cap, 0, 0, td, 'weiss', abstand=a)
    texte.append((s, a, k))
    t.auf(M.vorn(y0, 0.0, z), k)
    for (s, cap, x, z, breite), align in ((p['seit'], 'rechts'), (p['tagen'], 'links')):
        a = _abstand(t, s, cap, breite)
        k = t.text(s, cap, 0, 0, td, 'weiss', align=align, abstand=a)
        texte.append((s, a, k))
        t.auf(M.vorn(y0, x, z), k)
    for s, a, k in texte:
        bb = C.bbox_mm(k)
        t.log('    Schrift "%s": x %.1f .. %.1f, z %.1f .. %.1f (Breite %.1f), Zeichenabstand %d, %.1f mm tief'
              % (s, bb[0], bb[3], bb[2], bb[5], bb[3] - bb[0], a, td))
    t.einlegen(body, feld + [b for _, _, k in texte for b in k])
    body = t.root.bRepBodies.itemByName(nm)
    # Fenster durch Frontwand und Feld
    fw, fh2, frr = p['fenster']
    for c in _mitten(p):
        w = C.rounded_rect_body(t.root, -fw / 2.0, -fh2 / 2.0, fw / 2.0, fh2 / 2.0, frr, '-7 mm', t._nm('fenster'))
        t.auf(M.vorn(y0 - 1.0, c, za), [w])
        for h in [body] + [b for b in feld if b.isValid]:
            _kombi(t, h, [w], C.CUT, behalten=True)
        _entfernen(t, w)
    return body


# ---------- Achse ----------
def achse(t, p):
    t.objekt = 'achse'
    ya, za = p['ya'], p['za']
    r, fl = p['achse_d'] / 2.0, p['achse_flach']
    s = r * math.sqrt(0.5)
    xk = r * math.sqrt(2.0) - fl          # halbe Breite der Flaeche (Kiel mit 45-Grad-Flanken)

    def profil(sk, P):
        lines, arcs = sk.sketchCurves.sketchLines, sk.sketchCurves.sketchArcs
        arc = arcs.addByThreePoints(P(ya + s, za - s), P(ya, za + r), P(ya - s, za - s))

        def nah(q):
            return min((arc.startSketchPoint, arc.endSketchPoint), key=lambda e: e.geometry.distanceTo(q))
        l1 = lines.addByTwoPoints(nah(P(ya - s, za - s)), P(ya - xk, za - fl))
        l2 = lines.addByTwoPoints(l1.endSketchPoint, P(ya + xk, za - fl))
        lines.addByTwoPoints(l2.endSketchPoint, nah(P(ya + s, za - s)))

    xe = _taschen_x(p)[2][1] + p['sack'] - p['spiel_ax']
    body = _koerper(t, profil, -xe, xe, 'achse', RX)[0]
    nm = body.name
    _fase(t, _kanten(body, lambda x0, y0, z0, x1, y1, z1: abs(x1 - x0) < 1e-3 and abs(abs(x0) - xe) < 1e-3), 0.4,
          'Achsenden')
    body = t.root.bRepBodies.itemByName(nm)
    t.add(body, 'dunkel')
    return body, xe


# ---------- Drucklage, Montage, Pruefung ----------
ID = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
R_BLENDE = ((1, 0, 0), (0, 0, 1), (0, -1, 0))     # Sichtseite (y = -29) auf das Bett, oben (z) zeigt nach -y
R_WALZE = ((0, 0, 1), (1, 0, 0), (0, 1, 0))      # Achse senkrecht, linke Stirnseite auf das Bett


def _ablegen(t, objekt, spalten, x0, y0):
    """Dreht das Objekt aus dem Zusammenbau in die Drucklage und schiebt seine Box nach (x0, y0, 0)."""
    bodies = t.koerper(objekt=objekt)
    if spalten != ID:
        t.auf(_rot(spalten), bodies)
    bb = C.bbox_mm(bodies)
    d = (x0 - bb[0], y0 - bb[1], -bb[2])
    t.auf(_schieben(*d), bodies)
    return spalten, d, (bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2])


def _haupt(t, objekt):
    """Groesster Koerper eines Objekts (Grundkoerper ohne Einlagen)."""
    bs = [b for b in t.koerper(objekt=objekt) if b.isValid]
    return max(bs, key=lambda b: b.volume)


def _standfestigkeit(t, log, p):
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
    f = p['fase']
    vorn, hinten, seite = -p['D'] / 2.0 + f, p['D'] / 2.0 - f, p['B'] / 2.0 - f
    masse = vol * 1.24e-3 * 0.45          # PLA, gedruckt mit ca. 15 % Fuellung und 3 Waenden (Schaetzung)
    G = masse * 9.81e-3
    zt = p['za'] + p['R']
    log('    Standfestigkeit: Volumen %.0f cm3 (gedruckt ca. %.0f g), Schwerpunkt x %.1f y %.1f z %.1f mm; '
        'Kippwinkel vorn %.0f, hinten %.0f, seitlich %.0f Grad'
        % (vol / 1000.0, masse, gx, gy, gz, math.degrees(math.atan2(gy - vorn, gz)),
           math.degrees(math.atan2(hinten - gy, gz)), math.degrees(math.atan2(seite - abs(gx), gz))))
    log('    Daumen oben auf der Walze (z %.1f): waagerecht nach hinten kippt er erst ab %.1f N' %
        (zt, G * (hinten - gy) / zt))


def _pruef_text(p):
    """Rechnerische Kennwerte (Spiele, Rastung, Ziffernwinkel)."""
    R = p['R']
    out = []
    out.append('    Walze D %.1f x %.1f, Teilung %.1f, Trennwand %.2f mm; Spiel radial %.2f (Tasche, Mulde, Blende), '
               'axial %.2f je Seite, Lager D %.2f auf D %.2f (%.2f je Seite)'
               % (2 * R, p['walze_b'], p['teilung'], p['teilung'] - p['walze_b'] - 2 * p['spiel_ax'], p['spiel_r'],
                  p['spiel_ax'], p['achse_d'] + 2 * p['spiel_lager'], p['achse_d'], p['spiel_lager']))
    out.append('    Walze ragt %.1f mm ueber die Oberseite, Frontwand vor der Walze %.2f mm, Luft %.2f mm'
               % (p['za'] + R - p['H'], p['ya'] - R - p['spiel_r'] + p['D'] / 2.0,
                  p['ya'] - R + p['D'] / 2.0 - (p['ya'] - R - p['spiel_r'] + p['D'] / 2.0)))
    zb_, zd, zw, _ = p['zunge']
    yb, zb, _ = _noppen(p)
    L = zw - zb
    nh, _ = p['noppen']
    eind = nh - 2 * p['spiel_ax']             # Noppen in der Mulde (Walze an der rechten Wand)
    I = zb_ * zd ** 3 / 12.0
    F = 3 * 3000.0 * I * eind / L ** 3
    out.append('    Rastung: Noppen bei y %.2f z %.2f, Zunge %.1f x %.1f, Hebel %.1f mm, Hub %.2f mm, Kraft ca. %.1f N, '
               'Randdehnung %.2f %% (PLA); am Walzenrand ca. %.1f N (45-Grad-Kegel, Reibung 0,3)'
               % (yb, zb, zb_, zd, L, eind, F, 150.0 * zd * eind / L ** 2,
                  F * (1.0 + 0.3) / (1.0 - 0.3) * p['rast_r'] / R))
    return out


def zaehler(app, log, out, p, name, logo):
    t = M.Teil(app, log, name)
    for z in _pruef_text(p):
        log(z)
    cap = _ziffern_kal(t, p)
    sockel(t, p, logo)
    gehaeuse(t, p)
    blende(t, p)
    for i in range(3):
        walze(t, p, i, cap)
    _, xe = achse(t, p)

    # Drucklage: unten die Walzen und die Achse, darueber Blende, Gehaeuse, Sockel (alle 150 mm lang)
    g = p['abstand']
    lage = {}
    y = 0.0
    for i in range(3):
        lage['walze%d' % (i + 1)] = _ablegen(t, 'walze%d' % (i + 1), R_WALZE, i * (2 * p['R'] + g), y)
    lage['achse'] = _ablegen(t, 'achse', ID, 3 * (2 * p['R'] + g), y + p['R'] - 3.0)
    y += 2 * p['R'] + g
    for objekt, sp in (('blende', R_BLENDE), ('gehaeuse', ID), ('sockel', ID)):
        lage[objekt] = _ablegen(t, objekt, sp, 0.0, y)
        y += lage[objekt][2][1] + g
    bb = C.bbox_mm([it[0] for it in t.items])
    log('    Drucklage (eine Platte): %.1f x %.1f mm' % (bb[3] - bb[0], bb[4] - bb[1]))
    for objekt, (_, _, gr) in lage.items():
        log('    Druckobjekt %-9s %.1f x %.1f x %.1f mm' % (objekt, gr[0], gr[1], gr[2]))
    if max(bb[3] - bb[0], bb[4] - bb[1]) > p['bett']:
        raise RuntimeError('Drucklage groesser als %.0f mm' % p['bett'])

    def montage():
        C.hide_helpers(t.design)
        t.doc.activate()
        bb = C.bbox_mm([it[0] for it in t.items])
        C.snapshot(app, os.path.join(out['preview'], name + '_drucklage.png'),
                   ((bb[0] + bb[3]) / 2.0, (bb[1] + bb[4]) / 2.0, 0.0), (-60, -160, 220), margin=1.05)
        for objekt, (sp, d, _) in lage.items():
            bodies = t.koerper(objekt=objekt)
            t.auf(_schieben(-d[0], -d[1], -d[2]), bodies)
            if sp != ID:
                t.auf(_rot(_transponiert(sp)), bodies)
        # Walzen an die rechte Wand (der Noppen drueckt sie dorthin) und auf die Anzeige drehen
        for i, ch in enumerate(p['anzeige']):
            bodies = t.koerper(objekt='walze%d' % (i + 1))
            t.auf(_schieben(p['spiel_ax'], 0.0, 0.0), bodies)
            if int(ch):
                t.auf(_dreh_x(-36.0 * int(ch), p['ya'], p['za']), bodies)
        haupt = [_haupt(t, o) for o in lage]
        try:
            inp = t.design.createInterferenceInput(_koll(haupt))
            inp.areCoincidentFacesIncluded = False
            res = t.design.analyzeInterference(inp)
            treffer = 0
            for i in range(res.count):
                r = res.item(i)
                vol = r.interferenceBody.volume * 1000.0
                if vol > 0.001:
                    treffer += 1
                    log('  Hinweis: Durchdringung %s / %s: %.3f mm3' % (r.entityOne.name, r.entityTwo.name, vol))
            log('    Zusammenbau: %d Durchdringungen zwischen den %d Grundkoerpern' % (treffer, len(haupt)))
        except Exception as ex:
            log('  Hinweis: Durchdringungspruefung nicht moeglich: %s' % ex)
        try:
            _standfestigkeit(t, log, p)
        except Exception as ex:
            log('  Hinweis: Standfestigkeit nicht berechnet: %s' % ex)
        if p.get('montage_stl'):
            d = os.path.join(tempfile.gettempdir(), 'drehzaehler_montage')
            os.makedirs(d, exist_ok=True)
            for objekt in lage:
                for f in M.FILAMENT:
                    bs = t.koerper(f, objekt)
                    if bs:
                        t._stl(bs, os.path.join(d, '%s__%s__%s.stl' % (name, objekt, f)))
            log('    Zusammenbau als STL: %s' % d)

    t.fertig(out, ansichten=[('', (-98, -157, 75), (0, 0, 1)),
                             ('_vorn', (0, -200, 21), (0, 0, 1)),
                             ('_hinten', (110, 130, 80), (0, 0, 1)),
                             ('_oben', (0, -60, 200), (0, 0, 1))],
             montage=montage, rand=1.15)
    return t


def build(app, log, out, nur=None):
    for name, logo in (('drehzaehler_logo', True), ('drehzaehler_neutral', False)):
        if nur and not any(n in name for n in nur):
            continue
        zaehler(app, log, out, PARAM, name, logo)
