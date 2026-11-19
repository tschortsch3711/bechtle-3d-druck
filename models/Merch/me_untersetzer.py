# Uptime-Untersetzer (Ø 95 x 4 mm): flache Scheibe in Experience Green ohne Rand, oben komplett eben.
# Alle Grafik ist buendig in die Oberseite eingelegt, 1,0 mm tief (letzte fuenf Schichten, z = 3,0 .. 4,0;
# darunter bleiben 3,0 mm Scheibe), damit Weiss und Neon ueber dem dunklen Gruen decken. Nichts steht ueber:
#   weisser Randring (Radius 43 .. 44,5), Prompt "PS> Get-Uptime" (weiss, Versalhoehe 4,7 mm, ca. 55,8 mm breit),
#   "99,99 %" (Future Green, Versalhoehe 12 mm), Pulslinie (Progressive Green, Strich 2 mm)
#   und in der Variante "logo" das Bechtle-Logo einfarbig weiss (36 mm breit). Die Variante "neutral" hat kein Logo.
#   Der Text "Bechtle-Uptime" entfaellt (Wunsch).
#   Der i-Punkt im Prompt sitzt 0,1 mm hoeher als im Font, damit der dunkle Steg zum Stamm druckbar bleibt (> 0,5 mm).
# Druck: ein Objekt "untersetzer", Bild nach oben, Unterseite auf dem Bett (Fase unten statt Rundung),
#   ohne Stuetzen. Farben: dunkel (Scheibe), weiss, neon, mittel - Farbwechsel nur in den obersten fuenf Schichten.
#   Feine Schrift: im Slicer den Wandgenerator Arachne verwenden. Fuer heisse Tassen PETG statt PLA nehmen
#   (PLA wird ab etwa 55 Grad weich).
# Montage: keine. Wer mag, klebt unten Filz- oder Korkpunkte auf.
import math

import me_common as M
from me_common import C

PARAM = dict(
    d=95.0, dicke=4.0,
    fase_unten=0.5, fase_oben=0.6,
    tiefe=1.0,                          # Einlegetiefe oben (5 Schichten): hell ueber dunkel braucht 1,0 mm
    ring=(43.0, 44.5),                  # Randring, Radius innen / aussen
    rand_luft=2.0,                      # Mindestabstand der Grafik zum Randring
    prompt='PS> Get-Uptime', prompt_cap=4.7, prompt_breite=56.0,
    i_punkt_hub=0.1,                    # i-Punkt im Prompt um so viel anheben (Steg zum Stamm sonst ca. 0,43 mm)
    zahl=('99,99', '%'), zahl_cap=12.0, zahl_breite=66.0, zahl_luecke=0.3,   # Luecke vor dem % (x Versalhoehe)
    # Pulslinie (EKG-Zacke): x, y relativ zur Grundlinie
    puls=[(-29.0, 0.0), (-10.0, 0.0), (-7.0, -1.6), (-2.5, 7.5), (2.5, -5.5), (6.5, 2.4), (9.5, 0.0), (29.0, 0.0)],
    puls_breite=2.0,
    logo_breite=36.0,                   # Emblem + Schriftzug, Hoehe ca. 7,1 mm
)

# y der Mitte je Element (Pulslinie: Grundlinie). Ohne Logo rueckt alles zur Mitte.
LAGE = {
    'logo': dict(prompt=26.0, zahl=7.0, puls=-13.0, logo=-29.0),
    'neutral': dict(prompt=23.0, zahl=3.0, puls=-19.0, logo=None),
}


def _pruefen(t, p, name, bodies):
    """Schreibt die Box der Grafik ins Log und prueft den Abstand zum Randring."""
    bb = C.bbox_mm(bodies)
    rmax = max(math.hypot(x, y) for x in (bb[0], bb[3]) for y in (bb[1], bb[4]))
    grenze = p['ring'][0] - p['rand_luft']
    t.log('    %-7s x %6.2f .. %6.2f  y %6.2f .. %6.2f  (B %.2f x H %.2f)  Radius max. %.1f'
          % (name, bb[0], bb[3], bb[1], bb[4], bb[3] - bb[0], bb[4] - bb[1], rmax))
    if rmax > grenze:
        t.log('  Hinweis: %s reicht bis Radius %.1f (Grenze %.1f)' % (name, rmax, grenze))


def _i_punkt_heben(t, p, bodies, y_mitte, cap):
    """Hebt den i-Punkt der Prompt-Zeile etwas an. Der Punkt ist der einzige Koerper, der erst deutlich
    ueber der Zeilenmitte beginnt (alle anderen stehen auf der Grundlinie oder liegen mittig)."""
    hub = p['i_punkt_hub']
    if hub <= 0:
        return
    punkte = [b for b in bodies if C.bbox_mm([b])[1] > y_mitte + 0.25 * cap]
    if len(punkte) != 1:
        t.log('  Hinweis: i-Punkt nicht eindeutig gefunden (%d Koerper), nicht angehoben' % len(punkte))
        return
    unten = C.bbox_mm(punkte)[1]
    staemme = [C.bbox_mm([b]) for b in bodies if b != punkte[0]]
    xm = (C.bbox_mm(punkte)[0] + C.bbox_mm(punkte)[3]) / 2.0
    oben = max([bb[4] for bb in staemme if bb[0] < xm < bb[3] and bb[4] < unten + 1e-6], default=None)
    t.auf(M.oben(0.0, 0.0, hub), punkte)
    if oben is not None:
        t.log('    i-Punkt um %.2f mm angehoben: Steg zum Stamm %.2f -> %.2f mm'
              % (hub, unten - oben, unten - oben + hub))


def grafik(t, p, lage):
    """Baut das Motiv flach im Ursprung (z = -tiefe .. 0) und gibt die Koerper zurueck."""
    d = p['tiefe']
    k = t.kreis(2 * p['ring'][1], tiefe=d, farbe='weiss', innen_d=2 * p['ring'][0])

    # Prompt-Zeile
    cap = p['prompt_cap'] * min(1.0, p['prompt_breite'] / t.text_breite(p['prompt'], p['prompt_cap'], M.FONT_MONO, True))
    g = t.text(p['prompt'], p['prompt_cap'], 0, lage['prompt'], d, 'weiss', font=M.FONT_MONO, bold=True,
               max_breite=p['prompt_breite'])
    t.log('    Prompt: Versalhoehe %.2f mm' % cap)
    _i_punkt_heben(t, p, g, lage['prompt'], cap)
    _pruefen(t, p, 'Prompt', g)
    k += g

    # grosse Zahl: Ziffern und Prozentzeichen getrennt gesetzt (schmale Luecke statt Leerzeichen), zusammen mittig
    ziffern, prozent = p['zahl']
    cap = p['zahl_cap']
    w1 = t.text_breite(ziffern, cap, M.FONT_BLACK, False)
    w2 = t.text_breite(prozent, cap, M.FONT_BLACK, False)
    f = min(1.0, p['zahl_breite'] / (w1 + p['zahl_luecke'] * cap + w2))
    cap *= f
    total = (w1 + w2) * f + p['zahl_luecke'] * cap
    g = t.text(ziffern, cap, -total / 2.0, lage['zahl'], d, 'neon', font=M.FONT_BLACK, bold=False, align='links')
    g += t.text(prozent, cap, total / 2.0, lage['zahl'], d, 'neon', font=M.FONT_BLACK, bold=False, align='rechts')
    t.log('    Zahl: Versalhoehe %.2f mm' % cap)
    _pruefen(t, p, 'Zahl', g)
    k += g

    # Pulslinie
    y0 = lage['puls']
    g = t.linie([(x, y0 + y) for x, y in p['puls']], p['puls_breite'], d, 'mittel')
    _pruefen(t, p, 'Puls', g)
    k += g

    # Logo einfarbig weiss (das Feld im Emblem bleibt Scheibenfarbe)
    if lage['logo'] is not None:
        g = t.logo('voll', p['logo_breite'], 0, lage['logo'], d, mono='weiss')
        _pruefen(t, p, 'Logo', g)
        k += g
    return k


def untersetzer(app, log, out, p, art, name):
    t = M.Teil(app, log, name)
    t.objekt = 'untersetzer'
    T = p['dicke']
    C.user_param(t.design, 'dicke', T, 'Dicke des Untersetzers')
    sk = t.root.sketches.add(t.xy)
    sk.name = 'Scheibe_Skizze'
    sk.sketchCurves.sketchCircles.addByCenterRadius(C.P(0, 0), C.cm(p['d'] / 2.0))
    body = t.root.features.extrudeFeatures.addSimple(sk.profiles.item(0), C.E('dicke'), C.NEW).bodies.item(0)
    body.name = 'Scheibe'
    M.fase_kanten(t, body, p['fase_unten'], z=0.0)
    M.fase_kanten(t, body, p['fase_oben'], z=T)
    t.add(body, 'dunkel')

    g = t.auf(M.oben(T), grafik(t, p, LAGE[art]))
    t.einlegen(body, g)
    t.fertig(out, ansichten=[('', (0, -100, 173), (0, 0, 1)),
                             ('_oben', (0, 0, 200), (0, 1, 0)),
                             ('_flach', (-70, -150, 80), (0, 0, 1))], rand=1.1)
    return t


def build(app, log, out, nur=None):
    for art in ('logo', 'neutral'):
        name = 'untersetzer_%s' % art
        if nur and not any(n in name for n in nur):
            continue
        untersetzer(app, log, out, PARAM, art, name)
