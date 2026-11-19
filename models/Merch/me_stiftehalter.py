# Rack-Stiftehalter mit Wechselblende (84 x 64 x 100 mm): Stiftehalter im Look eines Serverschranks.
# Drei Faecher (ein grosses, zwei kleine), vorn vier angedeutete Einschuebe, an den Seiten Rack-Linien.
# Oben in der Frontwand sitzt eine Schwalbenschwanz-Tasche (z 68 bis 100, Oeffnung 72, hinten 76 mm breit,
# 2,4 tief), in die von oben die Wechselblende (ca. 74,8 x 30 x 2 mm) geschoben wird.
#
# Passung (alles aus 'spiel' abgeleitet, je Seite 0,25 mm; freies Spiel vorn/hinten = spiel * (1 + Wurzel 2)):
#   - Rastrippe (Dreieck 45 Grad, Mitte 4 mm ueber dem Anschlag) = freies Spiel + 'eingriff' (0,4 mm),
#     Nut in der Blende 0,2 mm tiefer als der Eingriff, damit die Rippenspitze nie aufsitzt.
#   - Zwei Fuehrungsleisten auf der Taschenrueckwand (x = +-28, ganze Hoehe, oben 45 Grad angeschraegt)
#     druecken die Blende nach vorn an die Flanken, es bleiben 0,15 mm Luft: die Blende klappert oben nicht.
#   - Oben an der Tasche 0,8 mm Einfuehrschraege (45 Grad), an den unteren Blendenecken hinten 1,2 mm Fase.
#
# Druck (zwei Objekte, keine Stuetzen, jedes Objekt hoechstens vier Farben):
#   halter : 84 x 64 x 100 mm, steht aufrecht auf dem Boden (Fase unten). Anthrazit, die Einschuebe und
#            Rack-Linien sind 0,8 mm tief in die senkrechten Waende eingelegt (schwarz, LEDs in mittel / neon).
#   blende : liegt flach auf der Rueckseite (breite Seite des Schwalbenschwanzes auf dem Bett), Sichtseite oben.
#            Schwarz, Logo / Text / LEDs 1,0 mm tief eingelegt (darunter bleiben 1,0 mm Schwarz, die Nut auf der
#            Rueckseite liegt seitlich daneben), die anthrazitfarbenen Schlitze der neutralen Blende 0,6 mm.
#   Drucklage: Blende 8 mm vor dem Halter, zusammen ca. 84 x 102 mm.
#
# Montage: Blende mit der Schrift nach vorn von oben in die Tasche schieben, bis sie auf dem Anschlag sitzt.
#   Kurz vor dem Anschlag schnappt die Rastrippe der Taschenrueckwand in die Nut auf der Blendenrueckseite,
#   die Blende haelt dann auch ueber Kopf. Zum Wechseln die Blende oben greifen: Daumen vorn auf die Blende,
#   Zeigefinger im grossen Fach durch die Griffkerbe der Taschenrueckwand hinten an die Blende, und nach oben
#   ziehen; oder mit dem Fingernagel in der Griffmulde (20 x 4 mm) unter der Blende nach oben schieben.
#   Die Blenden beider Varianten passen in denselben Halter.
import math

import adsk.core
import adsk.fusion

import me_common as M
from me_common import C

PARAM = dict(
    # Halter
    b=84.0, t=64.0, h=100.0, r=3.0, fase=0.5,
    wand=2.4, front=4.0, boden=2.4, steg=1.6, r_fach=1.5,
    fach_gross=48.0,                # Breite des grossen Fachs (links)
    fach_klein=28.0,                # Tiefe der beiden kleinen Faecher (rechts)
    # Schwalbenschwanz-Tasche in der Frontwand
    tasche=2.4,                     # Tiefe (dahinter bleiben 1,6 mm Wand)
    tasche_b=76.0,                  # Breite hinten, Flanken 45 Grad
    nase=0.4,                       # senkrechtes Stueck an der Vorderkante der Haltelippen (keine Messerkante)
    anschlag=68.0,                  # z des Anschlags, darueber ist die Tasche offen
    einfuehrung=0.8,                # 45-Grad-Einfuehrschraege oben an der Tasche
    mulde=(20.0, 4.0),              # Griffmulde unter der Blende: Breite, Hoehe (endet 0,5 ueber dem Einschub)
    griffkerbe=(-2.0, 16.0, 88.0, 4.0),  # Kerbe oben in der Taschenrueckwand zum grossen Fach: x Mitte, Breite,
                                          # z Grund, Eckradius
    rippe=(14.0, 4.0),              # Rastrippe: Laenge, Mitte ueber dem Anschlag (Hoehe aus spiel + eingriff)
    eingriff=0.4,                   # so weit muss die Blende ueber die Rippe ausweichen (Haltekraft)
    fuehrung=(28.0, 1.2, 0.15),     # Fuehrungsleisten: x (+-), Breite, verbleibende Luft vorn/hinten
    # Blende
    blende_h=30.0, blende_d=2.0,
    spiel=0.25,                     # Luft je Seite (hinten und senkrecht zu den Flanken)
    nut=(16.0, 0.2, 0.6),           # Rastnut: Laenge, Tiefe ueber den Eingriff hinaus, Breite am Grund
    blende_fase=(0.4, 0.3),         # Rueckseite (Bett), Sichtseite
    blende_ecke=1.2,                # Fase an den unteren Ecken der Rueckseite (Einfuehrung in die Flanken)
    tiefe_blende=1.0,               # helle Einlagen (weiss, mittel, neon) auf Schwarz
    tiefe_blende_dunkel=0.6,        # anthrazit auf Schwarz (neutrale Schlitze)
    logo=(40.0, -12.0, 6.0),        # Breite, x und y der Mitte
    rack=(6.0, -32.0, -6.5, 38.0),  # "RACK 01": Versalhoehe, x links, y, groesste Breite
    led=(3.0, 23.5, 29.0),          # Status-Punkte: Durchmesser, x1, x2
    neutral_text=(7.0, 5.5, 42.0),  # neutrale Blende: Versalhoehe, y, groesste Breite
    neutral_schlitze=(20, 3.2, 1.6, 6.0, -6.5),   # Anzahl, Raster, Breite, Hoehe, y der Mitte
    # Grafik auf den Waenden
    tiefe_wand=0.8,
    he=14.8,                        # Raster der Einschuebe (1 HE im Massstab 1:3)
    einschub=(72.0, 12.6, 1.2, 57.2),   # Breite, Hoehe, Eckradius, z der Mitte des obersten Einschubs
    einschub_led=(2.4, -31.5, 2.3),     # Durchmesser, x, Abstand von der Mitte
    schlitz=(13, -25.0, 3.0, 1.4, 7.6),     # Lueftung: Anzahl, x links, Raster, Breite, Hoehe
    strich=(18.0, 32.0, 1.2, 2.35),         # zwei Linien: x0, x1, Hoehe, Abstand von der Mitte
    schacht=(4, -24.0, 14.4, 13.0, 8.4, 1.0),   # Laufwerke: Anzahl, x links, Raster, Breite, Hoehe, Rahmen
    griff=(2.2, 5.6, 0.5, 1.2),             # Griff im Schacht: x, Laenge, z ueber der Mitte, Hoehe
    schacht_led=(2.0, 10.0, -1.4),          # Durchmesser, x, z zur Mitte
    rille=(54.0, 1.6, 6),                   # Rack-Linien an den Seiten: Laenge, Hoehe, Anzahl
    abstand=8.0,                    # Luecke zwischen Halter und Blende auf dem Druckbett
)


# ---------- Helfer ----------

def _passung(p):
    """Abgeleitete Masse der Passung (mm): freies Spiel vorn/hinten, Hoehe der Rastrippe, Tiefe der Nut,
    Hoehe der Fuehrungsleisten."""
    frei = p['spiel'] * (1.0 + math.sqrt(2.0))       # hinten spiel, nach vorn bis zur Flankenanlage spiel * Wurzel 2
    rh = frei + p['eingriff']
    nt = p['eingriff'] + p['nut'][1]
    fh = frei - p['fuehrung'][2]
    return frei, rh, nt, fh


def _taschen_pts(p):
    """Grundriss der Schwalbenschwanz-Tasche (gegen den Uhrzeigersinn), vorn 1 mm ueber die Front hinaus."""
    y0 = -p['t'] / 2.0
    pD, pB = p['tasche'], p['tasche_b'] / 2.0
    pF = pB - (pD - p['nase'])
    return [(-pF, y0 - 1.0), (pF, y0 - 1.0), (pF, y0 + p['nase']), (pB, y0 + pD), (-pB, y0 + pD), (-pF, y0 + p['nase'])]


def _k(x, y, d):
    """Kreis als Form (x0, y0, x1, y1, r)."""
    return (x - d / 2.0, y - d / 2.0, x + d / 2.0, y + d / 2.0, d / 2.0)


def _form(sk, x0, y0, x1, y1, r):
    """Zeichnet ein Rechteck mit runden Ecken (r bis zur halben Seite: Langloch oder Kreis) in die Skizze."""
    w, h = x1 - x0, y1 - y0
    r = min(r, w / 2.0, h / 2.0)
    lines = sk.sketchCurves.sketchLines
    if r < 0.01:
        lines.addTwoPointRectangle(C.P(x0, y0), C.P(x1, y1))
        return
    if abs(w - 2 * r) < 1e-6 and abs(h - 2 * r) < 1e-6:
        sk.sketchCurves.sketchCircles.addByCenterRadius(C.P(x0 + r, y0 + r), C.cm(r))
        return
    arcs = sk.sketchCurves.sketchArcs
    enden = []
    for (cx, cy), a in (((x1 - r, y0 + r), -90), ((x1 - r, y1 - r), 0), ((x0 + r, y1 - r), 90), ((x0 + r, y0 + r), 180)):
        a0, a1 = math.radians(a), math.radians(a + 90)
        s = (cx + r * math.cos(a0), cy + r * math.sin(a0))
        e = (cx + r * math.cos(a1), cy + r * math.sin(a1))
        arcs.addByCenterStartSweep(C.P(cx, cy), C.P(*s), math.pi / 2.0)
        enden.append((s, e))
    for i in range(4):
        a, b = enden[i][1], enden[(i + 1) % 4][0]
        if math.hypot(a[0] - b[0], a[1] - b[1]) > 1e-4:
            lines.addByTwoPoints(C.P(*a), C.P(*b))


def _feld(t, aussen, loecher, tiefe, farbe):
    """Flaches Feld (z = -tiefe .. 0) mit Aussparungen: in den Loechern bleibt spaeter die Wirtfarbe stehen."""
    sk = t.root.sketches.add(t.xy)
    sk.name = t._nm('feld') + '_Skizze'
    sk.isComputeDeferred = True
    _form(sk, *aussen)
    for f in loecher:
        _form(sk, *f)
    sk.isComputeDeferred = False
    prof = C.largest_profile(sk)
    if prof.profileLoops.count != 1 + len(loecher):
        t.log('  Hinweis: Feld hat %d statt %d Konturen' % (prof.profileLoops.count, 1 + len(loecher)))
    e = t.root.features.extrudeFeatures.addSimple(prof, C.V(-tiefe), C.NEW)
    b = e.bodies.item(0)
    b.name = t._nm('feld')
    t.add(b, farbe)
    return b


def _formen(t, formen, tiefe, farbe):
    """Mehrere getrennte Formen in einem Zug als flache Koerper (z = -tiefe .. 0)."""
    sk = t.root.sketches.add(t.xy)
    sk.name = t._nm('formen') + '_Skizze'
    sk.isComputeDeferred = True
    for f in formen:
        _form(sk, *f)
    sk.isComputeDeferred = False
    if sk.profiles.count != len(formen):
        t.log('  Hinweis: %d Profile statt %d Formen' % (sk.profiles.count, len(formen)))
    col = adsk.core.ObjectCollection.create()
    for i in range(sk.profiles.count):
        col.add(sk.profiles.item(i))
    e = t.root.features.extrudeFeatures.addSimple(col, C.V(-tiefe), C.NEW)
    bodies = [e.bodies.item(i) for i in range(e.bodies.count)]
    nm = t._nm('form')
    for i, b in enumerate(bodies):
        b.name = '%s_%d' % (nm, i + 1)
    return t.add(bodies, farbe)


def _verbinden(t, ziel, werkzeuge, op):
    """Schneidet die Werkzeuge aus dem Ziel (C.CUT) oder fuegt sie an (C.JOIN). Die Werkzeuge werden verbraucht."""
    tc = adsk.core.ObjectCollection.create()
    for b in M._liste(werkzeuge):
        tc.add(b)
    ci = t.root.features.combineFeatures.createInput(ziel, tc)
    ci.operation = op
    ci.isKeepToolBodies = False
    t.root.features.combineFeatures.add(ci)


# ---------- Grafik ----------

def _front(t, p):
    """Vier Einschuebe fuer die Frontwand, flach im Ursprung (lokal x = Welt-x, lokal y = Welt-z).
    Rueckgabe: (Koerper, die aus dem Halter geschnitten werden; Liste (Wirt, LEDs) fuer das Einlegen der LEDs)."""
    d = p['tiefe_wand']
    eb, eh, er, z_oben = p['einschub']
    ld, lx, ldz = p['einschub_led']
    felder, leds = [], []
    for i in range(4):
        zc = z_oben - i * p['he']
        loecher = []
        innen = []
        if i < 2:
            # Server: Lueftungsschlitze und zwei Linien (bleiben anthrazit stehen)
            n, sx, raster, sb, sh = p['schlitz']
            for k in range(n):
                loecher.append((sx + k * raster, zc - sh / 2.0, sx + k * raster + sb, zc + sh / 2.0, sb / 2.0))
            lx0, lx1, lh, ldy = p['strich']
            for s in (-1, 1):
                loecher.append((lx0, zc + s * ldy - lh / 2.0, lx1, zc + s * ldy + lh / 2.0, lh / 2.0))
        else:
            # Speicher: vier Laufwerksschaechte (Rahmen anthrazit, Flaeche schwarz, Griff anthrazit, LED)
            n, bx0, raster, bb, bh, rahmen = p['schacht']
            gx, gl, gz, gh = p['griff']
            sd, sx, sz = p['schacht_led']
            for k in range(n):
                bx = bx0 + k * raster
                loecher.append((bx, zc - bh / 2.0, bx + bb, zc + bh / 2.0, 1.0))
                fl = _feld(t, (bx + rahmen, zc - bh / 2.0 + rahmen, bx + bb - rahmen, zc + bh / 2.0 - rahmen, 0.5),
                           [(bx + gx, zc + gz, bx + gx + gl, zc + gz + gh, gh / 2.0)], d, 'schwarz')
                innen.append(fl)
                leds.append((fl, t.kreis(sd, bx + sx, zc + sz, d, 'mittel')))
        feld = _feld(t, (-eb / 2.0, zc - eh / 2.0, eb / 2.0, zc + eh / 2.0, er), loecher, d, 'schwarz')
        felder += [feld] + innen
        led = t.kreis(ld, lx, zc + ldz, d, 'mittel')
        led += t.kreis(ld, lx, zc - ldz, d, 'neon' if i == 0 else 'mittel')
        leds.append((feld, led))
    return felder, leds


def _rillen(t, p):
    """Rack-Linien fuer eine Seitenwand, flach im Ursprung (lokal y = Welt-z)."""
    rl, rh, n = p['rille']
    return _formen(t, [(-rl / 2.0, k * p['he'] - rh / 2.0, rl / 2.0, k * p['he'] + rh / 2.0, rh / 2.0)
                       for k in range(1, n + 1)], p['tiefe_wand'], 'schwarz')


def _blenden_grafik(t, p, logo):
    """Grafik der Blende, flach im Ursprung (Blendenmitte = 0, 0)."""
    d = p['tiefe_blende']
    ld, x1, x2 = p['led']
    cap, tx, ty, mb = p['rack']
    if logo:
        lb, lx, ly = p['logo']
        g = t.logo('voll', lb, lx, ly, d, mono='weiss')
        g += t.text('RACK 01', cap, tx, ty, d, 'mittel', max_breite=mb, align='links')
        g += _formen(t, [_k(x1, ty, ld), _k(x2, ty, ld)], d, 'neon')
    else:
        # neutral: Beschriftung und Status-Punkte oben, darunter eine Reihe Lueftungsschlitze
        ncap, ny, nmb = p['neutral_text']
        g = t.text('RACK 01', ncap, tx, ny, d, 'mittel', max_breite=nmb, align='links')
        g += _formen(t, [_k(x1, ny, ld), _k(x2, ny, ld)], d, 'neon')
        n, raster, sb, sh, sy = p['neutral_schlitze']
        g += _formen(t, [(tx + k * raster, sy - sh / 2.0, tx + k * raster + sb, sy + sh / 2.0, sb / 2.0)
                         for k in range(n)], p['tiefe_blende_dunkel'], 'anthrazit')
    return g


# ---------- Teile ----------

def _halter(t, p):
    t.objekt = 'halter'
    B, T, H = p['b'], p['t'], p['h']
    x0, x1, y0, y1 = -B / 2.0, B / 2.0, -T / 2.0, T / 2.0
    body = C.rounded_rect_body(t.root, x0, y0, x1, y1, p['r'], '%g mm' % H, 'halter_roh')
    M.fase_kanten(t, body, p['fase'])               # Fase unten (Bett) und oben aussen
    t.add(body, 'anthrazit')

    # Faecher: grosses Fach links, zwei kleine rechts
    ix0, ix1 = x0 + p['wand'], x1 - p['wand']
    iy0, iy1 = y0 + p['front'], y1 - p['wand']
    xT = ix0 + p['fach_gross']
    yT = iy0 + p['fach_klein']
    faecher = [(ix0, iy0, xT, iy1), (xT + p['steg'], iy0, ix1, yT), (xT + p['steg'], yT + p['steg'], ix1, iy1)]
    tools = []
    for a, b, c, d in faecher:
        t.log('    Fach %.1f x %.1f, %.1f tief' % (c - a, d - b, H - p['boden']))
        tools.append(C.rounded_rect_body(t.root, a, b, c, d, p['r_fach'], '%g mm' % (H - p['boden'] + 1.0),
                                         t._nm('fach')))
    t.auf(M.oben(p['boden']), tools)
    _verbinden(t, body, tools, C.CUT)

    # Schwalbenschwanz-Tasche: oberhalb des Anschlags, nach oben offen
    pD, zS = p['tasche'], p['anschlag']
    pts = _taschen_pts(p)
    tasche = C.poly_body(t.root, t.xy, 0, pts, '%g mm' % (H - zS + 1.0), t._nm('tasche'))
    t.auf(M.oben(zS), tasche)
    _verbinden(t, body, tasche, C.CUT)

    # Einfuehrschraege oben: derselbe Grundriss, nach oben um 45 Grad aufgeweitet (Auszug mit Formschraege)
    c = p['einfuehrung']
    sk = t.root.sketches.add(t.xy)
    sk.name = t._nm('einfuehrung') + '_Skizze'
    lines = sk.sketchCurves.sketchLines
    sp = [C.P(x, y) for x, y in pts]
    for i in range(len(sp)):
        lines.addByTwoPoints(sp[i], sp[(i + 1) % len(sp)])
    ext = t.root.features.extrudeFeatures
    trichter = None
    for winkel in ('45 deg', '-45 deg'):             # Vorzeichen der Formschraege: nach oben weiter werden
        ei = ext.createInput(sk.profiles.item(0), C.NEW)
        ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(C.V(c + 0.5)),
                            adsk.fusion.ExtentDirections.PositiveExtentDirection,
                            adsk.core.ValueInput.createByString(winkel))
        f = ext.add(ei)
        trichter = f.bodies.item(0)
        bb = C.bbox_mm([trichter])
        if bb[3] > p['tasche_b'] / 2.0 + c:
            break
        f.deleteMe()
        trichter = None
    if trichter is None:
        raise RuntimeError('Einfuehrschraege laesst sich nicht bauen')
    trichter.name = t._nm('einfuehrung')
    t.log('    Einfuehrung (%s): Werkzeug x %.2f..%.2f, y %.2f..%.2f, z %.2f..%.2f'
          % (winkel, bb[0], bb[3], bb[1], bb[4], bb[2], bb[5]))
    t.auf(M.oben(H - c), trichter)
    _verbinden(t, body, trichter, C.CUT)

    # Griffmulde unter der Blende (nach oben in die Tasche offen, also ohne Ueberhang)
    mb, mh = p['mulde']
    mulde = C.rect_body(t.root, t.xy, 0, -mb / 2.0, y0 - 1.0, mb / 2.0, y0 + pD, '%g mm' % (mh + 0.5), t._nm('mulde'))
    t.auf(M.oben(zS - mh), mulde)
    _verbinden(t, body, mulde, C.CUT)

    # Griffkerbe oben in der Taschenrueckwand: vom grossen Fach aus liegt die Blendenrueckseite frei
    kx, kb, kz, kr = p['griffkerbe']
    kerbe = C.rounded_rect_body(t.root, kx - kb / 2.0, kz, kx + kb / 2.0, H + kr + 1.0, kr,
                                '%g mm' % (p['front'] - pD + 1.5), t._nm('kerbe'))
    t.auf(M.flaeche((0.0, y0 + p['front'] + 1.0, 0.0), (1, 0, 0), (0, 0, 1)), kerbe)   # Normale -Y
    _verbinden(t, body, kerbe, C.CUT)

    # Rastrippe auf der Taschenrueckwand: Dreieck mit 45-Grad-Flanken, quer liegend
    frei, rh, nt, fh = _passung(p)
    rl, rz = p['rippe']
    e = 0.3                                          # so weit steckt die Rippe in der Wand
    rippe = C.poly_body(t.root, t.xy, 0, [(-(rh + e), -e), (0.0, rh), (rh + e, -e)], '%g mm' % rl, t._nm('rippe'))
    t.auf(M.flaeche((-rl / 2.0, y0 + pD, zS + rz), (0, 0, 1), (0, -1, 0)), rippe)
    _verbinden(t, body, rippe, C.JOIN)

    # Fuehrungsleisten: senkrecht vom Anschlag bis unter die Einfuehrung, oben 45 Grad angeschraegt
    fx, fb, _ = p['fuehrung']
    z1 = H - c                                       # Oberkante an der Wand
    leisten = []
    for sx in (-1, 1):
        lb = C.poly_body(t.root, t.xy, 0, [(zS - 0.5, -e), (z1 + e, -e), (z1 - fh, fh), (zS - 0.5, fh)],
                         '%g mm' % fb, t._nm('leiste'))
        t.auf(M.flaeche((sx * fx - fb / 2.0, y0 + pD, 0.0), (0, 0, 1), (0, -1, 0)), lb)
        leisten.append(lb)
    _verbinden(t, body, leisten, C.JOIN)
    t.log('    Passung: Spiel %.2f je Seite, frei vorn/hinten %.3f, Rastrippe %.3f hoch, Nut %.2f tief, '
          'Fuehrungsleisten %.3f hoch' % (p['spiel'], frei, rh, nt, fh))

    # Grafik: Einschuebe vorn, Rack-Linien links und rechts
    felder, leds = _front(t, p)
    alle = felder + [b for _, ls in leds for b in ls]
    t.auf(M.vorn(y0), alle)
    seiten = t.auf(M.links(x0), _rillen(t, p)) + t.auf(M.rechts(x1), _rillen(t, p))
    t.einlegen(body, felder + seiten)
    for wirt, ls in leds:
        t.einlegen(wirt, ls)
    return body


def _blende(t, p, logo, y_mitte):
    """Blende flach liegend, Rueckseite (breit) auf z = 0, Sichtseite oben, Oberkante der Blende in +Y."""
    t.objekt = 'blende'
    d, hB, s = p['blende_d'], p['blende_h'], p['spiel']
    wB = p['tasche_b'] / 2.0 - s - s * math.sqrt(2.0)       # halbe Breite hinten
    wT = wB - d                                             # halbe Breite vorn (Flanken 45 Grad)
    # Querschnitt (x, Tiefe) hochkant bauen und hinlegen: Tiefe 0 = Sichtseite -> z = d
    k = C.poly_body(t.root, t.xy, 0, [(-wT, 0.0), (wT, 0.0), (wB, d), (-wB, d)], '%g mm' % hB, 'blende_roh')
    t.auf(M.flaeche((0.0, -hB / 2.0, d), (1, 0, 0), (0, 0, -1)), k)
    M.fase_kanten(t, k, p['blende_fase'][0], z=0.0)         # Bett: nimmt die Messerkanten und den Elefantenfuss
    M.fase_kanten(t, k, p['blende_fase'][1], z=d)
    t.add(k, 'schwarz')

    # Einfuehrfase an den unteren Ecken: senkrechte 45-Grad-Schnitte, die nur die breite Rueckseite treffen
    # (an der Sichtseite ist die Blende um d schmaler, dort bleibt die Ecke unberuehrt, solange ecke < d)
    ke = p['blende_ecke']
    ecken = []
    for sx in (-1, 1):
        q = [(wB - ke - 1.0, -hB / 2.0 - 1.0), (wB + 1.0, -hB / 2.0 - 1.0), (wB + 1.0, -hB / 2.0 + ke + 1.0)]
        ecken.append(C.poly_body(t.root, t.xy, 0, [(sx * x, y) for x, y in q], '%g mm' % (d + 2.0), t._nm('ecke')))
    t.auf(M.oben(-1.0), ecken)
    _verbinden(t, k, ecken, C.CUT)

    # Rastnut auf der Rueckseite (Trapez, 45-Grad-Flanken, druckt ohne Stuetzen), Tiefe = Eingriff + Reserve
    nl, _, nb = p['nut']
    nt = _passung(p)[2]
    yc = -hB / 2.0 + p['rippe'][1]
    e = 0.2
    nut = C.poly_body(t.root, t.xy, 0, [(yc - nb / 2.0 - nt - e, -e), (yc - nb / 2.0, nt), (yc + nb / 2.0, nt),
                                         (yc + nb / 2.0 + nt + e, -e)], '%g mm' % nl, t._nm('nut'))
    t.auf(M.flaeche((-nl / 2.0, 0.0, 0.0), (0, 1, 0), (0, 0, 1)), nut)
    _verbinden(t, k, nut, C.CUT)

    g = t.auf(M.oben(d), _blenden_grafik(t, p, logo))
    t.einlegen(k, g)
    t.auf(M.oben(0.0, 0.0, y_mitte), t.koerper(objekt='blende'))
    t.log('    Blende: hinten %.3f, vorn %.3f breit, %.1f dick, Nut %.2f tief; Tasche hinten %.1f, Oeffnung %.1f'
          % (2 * wB, 2 * wT, d, nt, p['tasche_b'], 2 * (p['tasche_b'] / 2.0 - p['tasche'] + p['nase'])))
    return k


def _kollision(a, b, versatz=(0.0, 0.0, 0.0)):
    """Gemeinsames Volumen zweier Koerper in mm3, b um versatz (mm) verschoben (nur gerechnet, nichts wird veraendert)."""
    tmp = adsk.fusion.TemporaryBRepManager.get()
    ka, kb = tmp.copy(a), tmp.copy(b)
    if any(versatz):
        m = adsk.core.Matrix3D.create()
        m.translation = adsk.core.Vector3D.create(C.cm(versatz[0]), C.cm(versatz[1]), C.cm(versatz[2]))
        tmp.transform(kb, m)
    tmp.booleanOperation(ka, kb, adsk.fusion.BooleanTypes.IntersectionBooleanType)
    return ka.volume * 1000.0 if ka.faces.count else 0.0


def stiftehalter(app, log, out, p, name, logo):
    t = M.Teil(app, log, name)
    y0 = -p['t'] / 2.0
    y_bl = y0 - p['abstand'] - p['blende_h'] / 2.0          # Blende liegt vor dem Halter auf dem Bett
    halter = _halter(t, p)
    blende = _blende(t, p, logo, y_bl)

    def montage():
        # Blende in die Tasche stellen: auf dem Anschlag, Rueckseite 0,02 mm vor den Fuehrungsleisten
        d = p['blende_d']
        frei, rh, nt, fh = _passung(p)
        y_hinten = y0 + p['tasche'] - fh - 0.02
        t.auf(M.vorn(y_hinten, 0.0, p['anschlag'] + p['blende_h'] / 2.0 - y_bl), t.koerper(objekt='blende'))
        rest = frei - fh - 0.02                              # Weg bis zur Anlage an den Flanken
        log('    montiert: Blende steht %.2f mm vor der Front, Weg bis zu den Flanken %.2f mm, Rippe ragt %.2f mm in die '
            '%.2f mm tiefe Nut' % (y0 - (y_hinten - d), rest, rh - fh - 0.02, nt))
        try:
            log('    Kollision Halter / Blende: %.3f mm3 (soll 0: Rippe frei in der Nut)' % _kollision(halter, blende))
            # Gegenproben: nach vorn stoesst sie an die Flanken, nach hinten an die Leisten, nach oben an die Rastrippe
            log('    Probe %.2f mm nach vorn: %.3f, %.2f mm nach vorn: %.2f, 0,1 mm zurueck: %.2f, 1 mm nach oben: %.2f mm3'
                % (rest - 0.01, _kollision(halter, blende, (0, -(rest - 0.01), 0)),
                   rest + 0.1, _kollision(halter, blende, (0, -(rest + 0.1), 0)),
                   _kollision(halter, blende, (0, 0.1, 0)), _kollision(halter, blende, (0, 0, 1.0))))
        except Exception as ex:
            log('  Hinweis: Kollision nicht gerechnet (%s)' % str(ex).splitlines()[0])

    t.fertig(out, montage=montage, rand=1.1,
             ansichten=[('', (-94, -163, 68), (0, 0, 1)),
                        ('_vorn', (0, -200, 0), (0, 0, 1)),
                        ('_rechts', (150, -90, 60), (0, 0, 1)),
                        ('_oben', (0, -40, 200), (0, 0, 1))])
    return t


def build(app, log, out, nur=None):
    for name, logo in (('stiftehalter_logo', True), ('stiftehalter_neutral', False)):
        if nur and not any(n in name for n in nur):
            continue
        stiftehalter(app, log, out, PARAM, name, logo)
