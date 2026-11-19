# Token (Ø 40 x 3, Loch fuer den Schluesselring wahlweise) und Einkaufswagenchip (Ø 23,25 x 2,4; 1 Euro: 23,25 x 2,33).
# Chip 2,4 statt 2,3 mm dick, damit Dicke und Einlagen im 0,2-mm-Schichtraster liegen.
# Vorder- und Rueckseite sind buendig eingelegt (oben die letzten, unten die ersten Schichten).
# Jede Seite ist ein Motiv aus MOTIVE; VARIANTEN legt fest, welche Paare gebaut werden.
import me_common as M
from me_common import C

TOKEN = dict(
    name='token', d=40.0, dicke=3.0, fase=0.5, tiefe=0.6,
    ring=(17.9, 19.0),                 # Randring, Radius innen / aussen (aussen 0,5 mm vor der Fase: 0,6 mm Wand in der 1. Schicht)
    emblem=(20.0, 4.23),               # Breite, y der Mitte (Oberkante 14,2: 1 mm unter dem Loch)
    wort=(22.5, -10.46),               # Breite, y der Mitte (2,2 mm unter dem Emblem, Ecken 0,7 mm vor dem Randring)
    loch=(16.2, 2.0),                  # y der Mitte, Durchmesser: Ring mit 1 mm Draht, ohne Umrandung; 2,8 mm Steg zum Rand
    bogen_aussen=14.0, bogen_r=13.4, bogen_cap=4.0, bogen_total=5.85,   # Bogentexte bleiben 1,2 mm unter dem Loch
    emblem_mitte=(10.0, 2.0),          # groesste Breite, Abstand zum Bogentext
    seit=(5.0, 4.5, 16.0), jahr=(7.5, -4.5, 27.0),       # Versalhoehe, y, groesste Breite
    zus=(3.6, 6.0, 26.0), zuk=(4.0, -0.4, 31.5), strich=(5.0, -6.0, 1.0),
    frage=11.0,
)
CHIP = dict(
    name='chip', d=23.25, dicke=2.4, fase=0.4, tiefe=0.6,
    ring=(9.9, 10.6),
    emblem=(9.0, 2.9),
    wort=(13.6, -5.0),                 # so breit wie moeglich: Strich ca. 0,57 mm
    loch=None,
    bogen_aussen=9.1, bogen_r=7.9, bogen_cap=2.4, bogen_total=5.85,
    emblem_mitte=(7.0, 1.4),
    seit=(2.8, 2.6, 9.6), jahr=(4.2, -2.5, 15.0),
    zus=(2.1, 3.6, 15.5), zuk=(2.4, -0.3, 18.0), strich=(3.0, -3.6, 0.8),
    frage=7.4,
)

# (Vorderseite, Rueckseite). Motive mit Emblem: logo, always, shape. Ohne Logo: seit2004, zusammen, unknown, leer.
# 'leer' = nur der Randring (fuer die 0,4-mm-Duese die sichere Rueckseite des neutralen Chips).
PAARE_LOGO = [('logo', 'seit2004'), ('logo', 'always'), ('logo', 'zusammen'), ('logo', 'shape'), ('logo', 'unknown')]
PAARE_NEUTRAL = [('seit2004', 'zusammen'), ('seit2004', 'unknown'), ('seit2004', 'leer')]


def _bogenpaar(t, p, oben, unten, farbe):
    """Zwei Bogentexte auf einem gemeinsamen Kreis. Rueckgabe: (Koerper, Innenradius).
    Der untere Text bekommt mehr Zeichenabstand (Koepfe laufen zur Mitte zusammen); das zaehlt bei der Breite mit."""
    wt = t.text_breite(oben, 1.0)
    each, total = 3.49, p['bogen_total']          # je Text hoechstens 200 Grad, zusammen z. B. 335 Grad
    s = p['bogen_cap']
    r = min(p['bogen_r'], p['bogen_aussen'] - s / 2.0)
    ab = 0
    for _ in range(12):
        ab = t.bogen_abstand(unten, s, r)
        wb = t.bogen_breite(unten, 1.0, abstand=ab)
        ro, ru = r - s / 2.0, r + s / 2.0         # Grundlinien oben / unten
        s = min(p['bogen_cap'], each * ro / wt, each * ru / wb, total / (wt / ro + wb / ru))
        r = min(p['bogen_r'], p['bogen_aussen'] - s / 2.0)
    k = t.bogentext(oben, s, r, oben=True, tiefe=p['tiefe'], farbe=farbe)
    k += t.bogentext(unten, s, r, oben=False, tiefe=p['tiefe'], farbe=farbe, abstand=ab)
    return k, r - s / 2.0


def motiv(t, p, key, ring_farbe):
    """Baut ein Motiv flach im Ursprung (z = -tiefe .. 0) und gibt die Koerper zurueck."""
    d = p['tiefe']
    k = t.kreis(2 * p['ring'][1], tiefe=d, farbe=ring_farbe, innen_d=2 * p['ring'][0])
    if key == 'logo':
        k += t.logo('emblem', p['emblem'][0], 0, p['emblem'][1], d)
        k += t.logo('wort', p['wort'][0], 0, p['wort'][1], d)
    elif key == 'seit2004':
        cap, y, mb = p['seit']
        k += t.text('seit', cap, 0, y, d, 'mittel', max_breite=mb)
        cap, y, mb = p['jahr']
        k += t.text('2004', cap, 0, y, d, 'dunkel', font=M.FONT_BLACK, bold=False, max_breite=mb)
    elif key == 'zusammen':
        cap, y, mb = p['zus']
        k += t.text('Zusammen', cap, 0, y, d, 'mittel', max_breite=mb)
        cap, y, mb = p['zuk']
        k += t.text('zukunftsstark', cap, 0, y, d, 'dunkel', max_breite=mb)
        hx, y, w = p['strich']
        k += t.linie([(-hx, y), (hx, y)], w, d, 'mittel')
    elif key in ('always', 'shape', 'unknown'):
        oben, unten = {'always': ('ALWAYS PREPARED', 'FOR SUCCESS.'),
                       'shape': ('SHAPE THE FUTURE.', 'WITH BECHTLE.'),
                       'unknown': ('GET TO KNOW', 'THE UNKNOWN!')}[key]
        kk, innen = _bogenpaar(t, p, oben, unten, 'dunkel')
        k += kk
        if key == 'unknown':
            q = min(p['frage'], (innen - 0.8) * 1.4)
            k += t.text('?', q, 0, 0, d, 'mittel', font=M.FONT_BLACK, bold=False)
        else:
            mb, luft = p['emblem_mitte']
            k += t.logo('emblem', min(mb, 2 * (innen - luft)), 0, 0, d)
    elif key != 'leer':
        raise ValueError('unbekanntes Motiv ' + key)
    return k


def muenze(app, log, out, p, vorn, hinten, name, loch=False):
    t = M.Teil(app, log, name)
    t.objekt = p['name']
    T = p['dicke']
    C.user_param(t.design, 'dicke', T, 'Dicke')
    sk = t.root.sketches.add(t.xy)
    sk.sketchCurves.sketchCircles.addByCenterRadius(C.P(0, 0), C.cm(p['d'] / 2.0))
    body = t.root.features.extrudeFeatures.addSimple(sk.profiles.item(0), C.E('dicke'), C.NEW).bodies.item(0)
    M.fase_kanten(t, body, p['fase'])
    t.add(body, 'weiss')

    g = t.auf(M.oben(T), motiv(t, p, vorn, 'dunkel'))
    g += t.auf(M.unten(0), motiv(t, p, hinten, 'mittel'))
    t.einlegen(body, g)
    if loch and p['loch']:
        C.cut_circle(t.root, body, 0, p['loch'][0], p['loch'][1], T)
    t.fertig(out, ansichten=[('', (-30, -80, 150), (0, 0, 1)),
                             ('_rueckseite', (30, -80, -150), (0, 0, -1))], rand=1.1)
    return t


def build(app, log, out, nur=None):
    jobs = []
    for p in (TOKEN, CHIP):
        for art, paare in (('logo', PAARE_LOGO), ('neutral', PAARE_NEUTRAL)):
            for v, h in paare:
                jobs.append((p, v, h, '%s_%s_%s' % (p['name'], art, h), False))
                if p['loch']:
                    jobs.append((p, v, h, '%s_%s_%s_loch' % (p['name'], art, h), True))
    for p, v, h, name, loch in jobs:
        if nur and not any(n in name for n in nur):
            continue
        muenze(app, log, out, p, v, h, name, loch)
