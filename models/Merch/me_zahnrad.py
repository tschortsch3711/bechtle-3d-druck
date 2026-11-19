# Zahnrad-Trio "Plan Build Run": drei ineinandergreifende Zahnraeder auf einer Grundplatte (Schreibtisch-Spielzeug).
# Dreht man ein Rad, drehen die beiden anderen mit.
#
# Verzahnung: Evolvente, Modul 2, 18 Zaehne, Eingriffswinkel 20 Grad. Achsabstand = m * z + 0,3 mm,
# dazu ist jeder Zahn 0,2 mm duenner als das Nennmass (Flankenspiel fuer den Druck).
# Die Flanken sind in der Skizze Kreisboegen durch Evolventenpunkte (Abweichung unter 0,01 mm).
#
# Druck (alles flach, ohne Stuetzen, 0,2 mm Schichten):
#   platte     Grundplatte 124 x 52 x 3 mm (Zapfen bis 9,8 mm) mit drei Anlaufringen und Achszapfen,
#              Experience Green; Variante "logo" mit weiss eingelegtem Schriftzug (25 mm breit, 1,0 mm tief).
#   rad_plan   Zahnrad D 39,6 x 6 mm, Progressive Green, Wort PLAN weiss eingelegt (1,0 mm tief, Zeichenabstand 8)
#   rad_build  Zahnrad weiss, Wort BUILD dunkelgruen eingelegt (0,6 mm tief)
#   rad_run    Zahnrad Future Green, Wort RUN dunkelgruen eingelegt (0,6 mm tief)
#   kappen     drei Achskappen D 16, Experience Green, auf dem Kopf gedruckt (Sichtseite auf dem Bett, Stift nach oben)
#
# Montage: Raeder auf die Zapfen stecken (aeussere Raeder haben die Zaehne um eine halbe Teilung versetzt,
# die Woerter stehen dann alle oben). Kappen mit dem Stift in die Zapfenbohrung druecken: vier Quetschrippen
# (Huellkreis 6,3 in der Bohrung 6,0, also 0,15 mm je Seite) klemmen; Rippenkoepfe und Bohrungsrand sind
# angefast. Die Bohrung geht durch die Platte: Kappe zum Zerlegen von unten mit einem Stift herausdruecken.
# Vor der Serie eine Kappe und die Platte zur Probe drucken (Pressung haengt vom Drucker ab).
import math
import os

import adsk.core
import adsk.fusion

import me_common as M
from me_common import C

PARAM = dict(
    # Grundplatte (Stadionform)
    laenge=124.0, breite=52.0, dicke=3.0, fase=0.5,
    # Verzahnung
    modul=2.0, zaehne=18, eingriff=20.0,
    kopf=0.9, fuss=1.25,               # Kopf- und Fusshoehe in Modulen (Kopf leicht gekuerzt: breitere Zahnkoepfe)
    achs_zugabe=0.3,                   # Zugabe auf den Achsabstand
    zahn_duenner=0.2,                  # Zahndicke am Teilkreis unter Nennmass
    fuss_r=0.5,                        # Rundung im Zahnfuss
    flanken_boegen=2,                  # Kreisboegen je Flanke
    rad_dicke=6.0, rad_fase_unten=0.4, rad_fase_oben=0.3,
    # Lagerung
    achse_d=10.0, lager_spiel=0.35,    # Spiel Bohrung / Zapfen je Seite
    ring_d=14.0, ring_h=0.4,           # Anlaufring unter dem Rad
    luft_axial=0.4,                    # Luft zwischen Rad und Kappe
    # Kappe
    kappe_d=16.0, kappe_h=1.6, kappe_fase=0.5,
    loch_d=6.0, loch_fase=0.5,         # Bohrung im Zapfen (durchgehend), Einfuehrfase oben
    stift_d=5.5, stift_l=5.0,          # Stift der Kappe
    rippen=4, rippen_d=6.3, rippe_b=1.2, rippe_kurz=0.8,   # Quetschrippen: Huellkreis, Breite, Abstand zum Stiftende
    rippe_fase=0.3,                    # Fase am Rippenkopf (Einfuehrung)
    # Beschriftung
    tiefe=0.6,                         # dunkle Schrift in hellem Rad
    tiefe_hell=1.0,                    # weisse Schrift auf Gruen (deckt besser)
    text_r=12.0, text_cap=5.0, text_winkel=150.0,
    logo=(25.0, -22.2),                # Breite des Schriftzugs, y der Mitte (x = Mitte zwischen BUILD und RUN)
    pruefen=True,                      # Eingriff nach der Montage rechnerisch pruefen (nur Protokoll)
)

# Objekt, Wort, Radfarbe, Schriftfarbe, Platz (-1, 0, 1), Zaehne um halbe Teilung versetzt, Zeichenabstand
# (PLAN: sonst beruehren sich L und A an der Grundlinie)
RAEDER = [
    ('rad_plan', 'PLAN', 'mittel', 'weiss', -1, True, 8),
    ('rad_build', 'BUILD', 'weiss', 'dunkel', 0, False, 0),
    ('rad_run', 'RUN', 'neon', 'dunkel', 1, True, 0),
]

# Drucklage: Mitte der Raeder und der Kappen neben der Platte
RAD_PLATZ = (46.0, 54.0)       # Abstand in x, y der Reihe
KAPPE_PLATZ = (24.0, -42.0)


def achsabstand():
    return PARAM['modul'] * PARAM['zaehne'] + PARAM['achs_zugabe']


def _schieben(dx, dy, dz):
    m = adsk.core.Matrix3D.create()
    m.translation = adsk.core.Vector3D.create(C.cm(dx), C.cm(dy), C.cm(dz))
    return m


def _zylinder(t, x, y, d, z0, z1, name):
    """Zylinder von z0 bis z1 als neuer Koerper."""
    sk = t.root.sketches.add(t.xy)
    sk.name = name + '_Skizze'
    sk.sketchCurves.sketchCircles.addByCenterRadius(C.P(x, y), C.cm(d / 2.0))
    ext = t.root.features.extrudeFeatures
    ei = ext.createInput(sk.profiles.item(0), C.NEW)
    if z0:
        ei.startExtent = adsk.fusion.OffsetStartDefinition.create(C.V(z0))
    ei.setDistanceExtent(False, C.V(z1 - z0))
    b = ext.add(ei).bodies.item(0)
    b.name = name
    return b


def _vereinen(t, ziel, werkzeuge):
    tc = adsk.core.ObjectCollection.create()
    for w in werkzeuge:
        tc.add(w)
    ci = t.root.features.combineFeatures.createInput(ziel, tc)
    ci.operation = C.JOIN
    t.root.features.combineFeatures.add(ci)


def _fase_kreis(t, body, d, z, radius, x=None, y=None):
    """Fase d an den Kreiskanten auf Hoehe z mit dem Radius radius (optional nur um die Mitte x, y)."""
    edges = adsk.core.ObjectCollection.create()
    for e in body.edges:
        c = adsk.core.Circle3D.cast(e.geometry)
        if c is None or abs(c.center.z - C.cm(z)) > 1e-6 or abs(c.radius - C.cm(radius)) > 1e-6:
            continue
        if x is not None and (abs(c.center.x - C.cm(x)) > 1e-6 or abs(c.center.y - C.cm(y)) > 1e-6):
            continue
        edges.add(e)
    if edges.count == 0:
        t.log('  Hinweis: keine Kreiskante z=%.2f r=%.2f an %s' % (z, radius, body.name))
        return
    cf = t.root.features.chamferFeatures
    ci = cf.createInput2()
    ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges, C.V(d), False)
    cf.add(ci)


# ---------- Zahnrad ----------

def verzahnung():
    """Kenngroessen der Verzahnung in mm."""
    p = PARAM
    m, z = p['modul'], p['zaehne']
    al = math.radians(p['eingriff'])
    r = m * z / 2.0
    return dict(m=m, z=z, al=al, r=r, rb=r * math.cos(al), ra=r + p['kopf'] * m, rf=r - p['fuss'] * m,
                s=math.pi * m / 2.0 - p['zahn_duenner'])


def _rad_skizze(t, name, versetzt):
    """Skizze des Zahnrads im Ursprung: Evolventenflanken als Kreisboegen, Kopf- und Fussboegen, Bohrung.
    versetzt=False: ein Zahn zeigt nach +x; versetzt=True: eine Zahnluecke zeigt nach +x."""
    p = PARAM
    g = verzahnung()
    r, rb, ra, rf, al, z = g['r'], g['rb'], g['ra'], g['rf'], g['al'], g['z']
    assert rf < rb < ra, 'Fusskreis muss unter dem Grundkreis liegen'

    def inv(a):
        return math.tan(a) - a

    def halb(rr):
        """Halber Zahnwinkel (Bogenmass) am Radius rr."""
        return g['s'] / (2.0 * r) + inv(al) - inv(math.acos(min(1.0, rb / rr)))

    def pol(rr, a):
        return C.P(rr * math.cos(a), rr * math.sin(a))

    # Stuetzradien der Flanke, gleichmaessig im Waelzwinkel
    n = p['flanken_boegen']
    t1 = math.sqrt(ra * ra - rb * rb) / rb
    rs = [rb * math.sqrt(1.0 + (t1 * k / (2.0 * n)) ** 2) for k in range(2 * n + 1)]
    rs[0], rs[-1] = rb, ra

    sk = t.root.sketches.add(t.xy)
    sk.name = name + '_Skizze'
    sk.isComputeDeferred = True
    arcs = sk.sketchCurves.sketchArcs
    lines = sk.sketchCurves.sketchLines
    teil = 2.0 * math.pi / z
    phase = teil / 2.0 if versetzt else 0.0
    for i in range(z):
        mitte = phase + i * teil
        for sgn in (1.0, -1.0):
            ab = mitte + sgn * halb(rb)
            lines.addByTwoPoints(pol(rf, ab), pol(rb, ab))                 # Zahnfuss: radial bis zum Grundkreis
            for k in range(n):
                q = [pol(rs[2 * k + j], mitte + sgn * halb(rs[2 * k + j])) for j in range(3)]
                arcs.addByThreePoints(q[0], q[1], q[2])                     # Evolvente
        aa = halb(ra)
        arcs.addByThreePoints(pol(ra, mitte - aa), pol(ra, mitte), pol(ra, mitte + aa))        # Zahnkopf
        a0, a1 = mitte + halb(rb), mitte + teil - halb(rb)
        arcs.addByThreePoints(pol(rf, a0), pol(rf, (a0 + a1) / 2.0), pol(rf, a1))              # Zahngrund
    sk.sketchCurves.sketchCircles.addByCenterRadius(C.P(0, 0), C.cm(p['achse_d'] / 2.0 + p['lager_spiel']))
    sk.isComputeDeferred = False
    prof = None
    for i in range(sk.profiles.count):
        if sk.profiles.item(i).profileLoops.count == 2:
            prof = sk.profiles.item(i)
    if prof is None:
        raise RuntimeError('Zahnrad-Umriss ist nicht geschlossen (%d Profile)' % sk.profiles.count)
    return prof


def zahnrad(t, objekt, wort, farbe, schrift, versetzt, platz, abstand=0):
    """Baut ein Zahnrad mit eingelegtem Wort im Ursprung und schiebt es an seinen Druckplatz (x, y)."""
    p = PARAM
    g = verzahnung()
    H = p['rad_dicke']
    t.objekt = objekt
    name = objekt + '_koerper'
    body = t.root.features.extrudeFeatures.addSimple(_rad_skizze(t, objekt, versetzt), C.V(H), C.NEW).bodies.item(0)
    body.name = name
    # Rundung im Zahnfuss (senkrechte Kanten am Fusskreis)
    if p['fuss_r'] > 0:
        edges = adsk.core.ObjectCollection.create()
        ve = C.vertical_edges(body)
        for i in range(ve.count):
            e = ve.item(i)
            q = e.startVertex.geometry
            if abs(math.hypot(q.x, q.y) - C.cm(g['rf'])) < 1e-5:
                edges.add(e)
        C.fillet(t.root, edges, p['fuss_r'])
        body = t.root.bRepBodies.itemByName(name)
    # unten Fase gegen den Elefantenfuss (sonst klemmen die Zaehne), oben kleine Fase
    M.fase_kanten(t, body, p['rad_fase_unten'], z=0.0)
    body = t.root.bRepBodies.itemByName(name)
    M.fase_kanten(t, body, p['rad_fase_oben'], z=H)
    body = t.root.bRepBodies.itemByName(name)
    t.add(body, farbe)

    tiefe = p['tiefe_hell'] if schrift == 'weiss' else p['tiefe']
    k = t.bogentext(wort, p['text_cap'], p['text_r'], oben=True, tiefe=tiefe, farbe=schrift,
                    max_winkel=p['text_winkel'], abstand=abstand)
    t.auf(M.oben(H), k)
    t.einlegen(body, k)
    t.auf(_schieben(platz[0], platz[1], 0.0), t.koerper(objekt=objekt))
    return body


# ---------- Grundplatte ----------

def platte(t, mit_logo):
    p = PARAM
    T = p['dicke']
    a = achsabstand()
    t.objekt = 'platte'
    name = 'platte_koerper'
    r = p['breite'] / 2.0
    hx = p['laenge'] / 2.0 - r
    sk = t.root.sketches.add(t.xy)
    sk.name = 'platte_Skizze'
    lines = sk.sketchCurves.sketchLines
    arcs = sk.sketchCurves.sketchArcs
    lines.addByTwoPoints(C.P(-hx, -r), C.P(hx, -r))
    arcs.addByThreePoints(C.P(hx, -r), C.P(hx + r, 0), C.P(hx, r))
    lines.addByTwoPoints(C.P(hx, r), C.P(-hx, r))
    arcs.addByThreePoints(C.P(-hx, r), C.P(-hx - r, 0), C.P(-hx, -r))
    body = t.root.features.extrudeFeatures.addSimple(C.largest_profile(sk), C.V(T), C.NEW).bodies.item(0)
    body.name = name
    M.fase_kanten(t, body, p['fase'])
    body = t.root.bRepBodies.itemByName(name)

    # Anlaufringe und Achszapfen
    zA = T + p['ring_h'] + p['rad_dicke'] + p['luft_axial']        # Oberkante Zapfen
    teile = []
    for i in (-1, 0, 1):
        teile.append(_zylinder(t, i * a, 0, p['ring_d'], 0.0, T + p['ring_h'], 'ring%d' % (i + 2)))
        teile.append(_zylinder(t, i * a, 0, p['achse_d'], 0.0, zA, 'achse%d' % (i + 2)))
    _vereinen(t, body, teile)
    body = t.root.bRepBodies.itemByName(name)
    for i in (-1, 0, 1):
        C.cut_circle(t.root, body, i * a, 0, p['loch_d'], zA)
    body = t.root.bRepBodies.itemByName(name)
    _fase_kreis(t, body, 0.4, zA, p['achse_d'] / 2.0)             # Zapfen oben: Rad laesst sich leicht aufstecken
    body = t.root.bRepBodies.itemByName(name)
    _fase_kreis(t, body, p['loch_fase'], zA, p['loch_d'] / 2.0)   # Einfuehrfase fuer Kappenstift und Rippen
    body = t.root.bRepBodies.itemByName(name)
    _fase_kreis(t, body, 0.4, 0.0, p['loch_d'] / 2.0)             # Bohrung am Bett (Elefantenfuss)
    body = t.root.bRepBodies.itemByName(name)
    t.add(body, 'dunkel')

    if mit_logo:
        # Schriftzug weiss in der Luecke vor BUILD und RUN
        k = t.logo('wort', p['logo'][0], 0, 0, p['tiefe_hell'], mono='weiss')
        t.auf(M.oben(T, a / 2.0, p['logo'][1]), k)
        t.einlegen(body, k)
    return body, zA


# ---------- Kappe ----------

def kappe(t, nr, x, y):
    """Achskappe in Drucklage: Sichtseite auf z = 0, Stift mit Quetschrippen nach oben."""
    p = PARAM
    t.objekt = 'kappen'
    name = 'kappe%d_koerper' % nr
    h = p['kappe_h']
    zs = h + p['stift_l']
    body = _zylinder(t, x, y, p['kappe_d'], 0.0, h, name)
    stift = _zylinder(t, x, y, p['stift_d'], 0.0, zs, 'stift%d' % nr)
    _vereinen(t, body, [stift])
    body = t.root.bRepBodies.itemByName(name)
    _fase_kreis(t, body, p['kappe_fase'], 0.0, p['kappe_d'] / 2.0)       # Sichtkante (liegt auf dem Bett)
    body = t.root.bRepBodies.itemByName(name)
    _fase_kreis(t, body, 0.5, zs, p['stift_d'] / 2.0)                    # Einfuehrfase am Stiftende
    body = t.root.bRepBodies.itemByName(name)
    rippen = []
    rm = p['rippen_d'] / 2.0 - p['rippe_b'] / 2.0
    for i in range(p['rippen']):
        w = math.radians(45.0 + i * 360.0 / p['rippen'])
        rx, ry = x + rm * math.cos(w), y + rm * math.sin(w)
        rip = _zylinder(t, rx, ry, p['rippe_b'], h - 0.2, zs - p['rippe_kurz'], 'rippe%d_%d' % (nr, i))
        if p['rippe_fase'] > 0:
            # Fase am Rippenkopf: Rippe laeuft langsam in die Bohrung ein (in Drucklage nach oben, ohne Ueberhang)
            _fase_kreis(t, rip, p['rippe_fase'], zs - p['rippe_kurz'], p['rippe_b'] / 2.0, rx, ry)
            rip = t.root.bRepBodies.itemByName('rippe%d_%d' % (nr, i))
        rippen.append(rip)
    _vereinen(t, body, rippen)
    body = t.root.bRepBodies.itemByName(name)
    t.add(body, 'dunkel')
    return body


# ---------- Pruefung ----------

def _pruefen(t, raeder, platte_body, kappen):
    """Rechnet nach der Montage: Durchdringung der Raeder beim gemeinsamen Drehen (muss 0 sein) und das
    Verdrehflankenspiel. raeder = [(koerper, x)], Achsen bei y = 0."""
    tmp = adsk.fusion.TemporaryBRepManager.get()
    INT = adsk.fusion.BooleanTypes.IntersectionBooleanType

    def gedreht(body, x, grad):
        k = tmp.copy(body)
        if grad:
            m = adsk.core.Matrix3D.create()
            m.setToRotation(math.radians(grad), adsk.core.Vector3D.create(0, 0, 1), C.P(x, 0, 0))
            tmp.transform(k, m)
        return k

    def schnitt(a, b):
        try:
            tmp.booleanOperation(a, b, INT)
        except RuntimeError:
            return 0.0
        return a.volume * 1000.0 if a.faces.count else 0.0

    teil = 360.0 / PARAM['zaehne']
    for (a, xa), (b, xb) in zip(raeder[:-1], raeder[1:]):
        schlimm = 0.0
        for i in range(16):
            w = teil * i / 16.0
            schlimm = max(schlimm, schnitt(gedreht(a, xa, w), gedreht(b, xb, -w)))
        spiel = None
        for i in range(1, 41):
            if schnitt(gedreht(a, xa, 0.0), gedreht(b, xb, 0.1 * i)) > 1e-4:
                spiel = 0.1 * i
                break
        t.log('  Eingriff %s / %s: groesste Durchdringung beim Drehen %.4f mm3, Flankenkontakt nach %s Grad Verdrehung'
              % (a.name, b.name, schlimm, ('%.1f' % spiel) if spiel else '> 4'))
        if schlimm > 1e-3:
            t.log('  Hinweis: Raeder %s und %s durchdringen sich' % (a.name, b.name))
        if spiel is None:
            t.log('  Hinweis: kein Flankenkontakt zwischen %s und %s' % (a.name, b.name))
    for a, xa in raeder:
        v = schnitt(tmp.copy(a), tmp.copy(platte_body))
        for kb in kappen:
            v += schnitt(tmp.copy(a), tmp.copy(kb))
        if v > 1e-3:
            t.log('  Hinweis: %s durchdringt Platte oder Kappe (%.3f mm3)' % (a.name, v))
    v = sum(schnitt(tmp.copy(kb), tmp.copy(platte_body)) for kb in kappen)
    t.log('  Pressung der Quetschrippen (Ueberdeckung Kappen / Platte): %.2f mm3' % v)


# ---------- Modell ----------

def trio(app, log, out, name, mit_logo):
    p = PARAM
    t = M.Teil(app, log, name)
    a = achsabstand()
    g = verzahnung()
    log('  Verzahnung: m %.1f, z %d, Teilkreis %.1f, Kopfkreis %.1f, Fusskreis %.1f, Achsabstand %.2f'
        % (g['m'], g['z'], 2 * g['r'], 2 * g['ra'], 2 * g['rf'], a))

    platte_body, zA = platte(t, mit_logo)
    raeder = []
    for objekt, wort, farbe, schrift, platz, versetzt, abstand in RAEDER:
        ist = (platz * RAD_PLATZ[0], RAD_PLATZ[1])
        body = zahnrad(t, objekt, wort, farbe, schrift, versetzt, ist, abstand)
        raeder.append((objekt, body, ist, platz * a))
    kappen = []
    for i in (-1, 0, 1):
        ist = (i * KAPPE_PLATZ[0], KAPPE_PLATZ[1])
        kappen.append((kappe(t, i + 2, ist[0], ist[1]), ist, i * a))

    def montage():
        # Bild der Drucklage (alle Objekte nebeneinander, Kappen auf dem Kopf), danach zusammensetzen
        C.hide_helpers(t.design)
        t.doc.activate()
        bb = C.bbox_mm([it[0] for it in t.items])
        ziel = ((bb[0] + bb[3]) / 2.0, (bb[1] + bb[4]) / 2.0, (bb[2] + bb[5]) / 2.0)
        C.snapshot(app, os.path.join(out['preview'], name + '_drucklage.png'), ziel, (-40, -110, 120), margin=1.1)

        z_rad = p['dicke'] + p['ring_h']
        for objekt, body, ist, x in raeder:
            t.auf(_schieben(x - ist[0], -ist[1], z_rad), t.koerper(objekt=objekt))
        for body, ist, x in kappen:
            # erst in den Ursprung, dann umgedreht auf den Zapfen
            t.auf(_schieben(-ist[0], -ist[1], 0.0), [body])
            t.auf(M.flaeche((x, 0.0, zA + p['kappe_h']), (1, 0, 0), (0, -1, 0)), [body])
        if p['pruefen']:
            _pruefen(t, [(body, x) for _, body, _, x in raeder], platte_body, [k[0] for k in kappen])

    t.fertig(out, ansichten=[('', (-31, -125, 153), (0, 0, 1)),
                             ('_oben', (0, 0, 200), (0, 1, 0)),
                             ('_seite', (40, -200, 45), (0, 0, 1)),
                             ('_unten', (30, -80, -150), (0, 0, -1))],
             montage=montage, rand=1.1)
    return t


def build(app, log, out, nur=None):
    for name, mit_logo in (('zahnrad_logo', True), ('zahnrad_neutral', False)):
        if nur and not any(n in name for n in nur):
            continue
        trio(app, log, out, name, mit_logo)
